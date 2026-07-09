from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.request
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class Skill:
    """Metadata used by the demo router to decide which skills to load."""

    name: str
    triggers: tuple[str, ...]
    required_for: tuple[str, ...] = ()
    content: str = ""
    skill_id: str | None = None
    path: str | None = None

    @property
    def id(self) -> str:
        return self.skill_id or self.name

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()

    def compact_context(self, max_chars: int = 900) -> str:
        lines = [line.rstrip() for line in self.content.strip().splitlines()]
        compact = "\n".join(line for line in lines if line).strip()
        if len(compact) <= max_chars:
            return compact
        return compact[: max_chars - 3].rstrip() + "..."


class RouteMode(StrEnum):
    AUTO = "auto"
    DETERMINISTIC = "deterministic"
    EXPLICIT = "explicit"
    LLM_FALLBACK = "llm_fallback"
    NO_MATCH = "no_match"


@dataclass(frozen=True)
class RoutedSkill:
    name: str
    required: bool
    confidence: float
    matched_terms: tuple[str, ...]
    source: str
    content_hash: str
    skill_id: str | None = None
    reason: str = ""

    @property
    def id(self) -> str:
        return self.skill_id or self.name

    def to_json(self) -> dict[str, object]:
        return {
            "skill_id": self.id,
            "name": self.name,
            "required": self.required,
            "confidence": self.confidence,
            "matched_terms": list(self.matched_terms),
            "selection_mode": self.source,
            "reason": self.reason,
            "content_hash": self.content_hash,
        }


@dataclass(frozen=True)
class RoutingPlan:
    required: tuple[str, ...]
    optional: tuple[str, ...]
    load_order: tuple[str, ...]
    confidence: dict[str, float]
    mode: RouteMode = RouteMode.DETERMINISTIC
    routed_skills: tuple[RoutedSkill, ...] = ()


@dataclass(frozen=True)
class Subtask:
    id: str
    task: str


@dataclass(frozen=True)
class SubtaskRequest:
    request: str
    subtasks: tuple[Subtask, ...]


@dataclass(frozen=True)
class SubagentAssignment:
    subtask_id: str
    subtask: str
    skill_id: str | None
    skill_name: str | None
    skill_hash: str | None
    confidence: float
    selection_mode: str
    reason: str

    def to_json(self) -> dict[str, object]:
        return {
            "subtask_id": self.subtask_id,
            "subtask": self.subtask,
            "skill_id": self.skill_id,
            "skill": self.skill_name,
            "skill_hash": self.skill_hash,
            "confidence": self.confidence,
            "selection_mode": self.selection_mode,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class AuditEvent:
    event: str
    skill_name: str
    content_hash: str
    message: str


@dataclass(frozen=True)
class MismatchFeedback:
    missing: tuple[str, ...]
    unexpected: tuple[str, ...]
    messages: tuple[str, ...]


@dataclass(frozen=True)
class MismatchSummary(MismatchFeedback):
    observations: int
    repeated_missing: tuple[str, ...]
    repeated_unexpected: tuple[str, ...]
    missing_counts: dict[str, int]
    unexpected_counts: dict[str, int]
    manifest_trigger_suggestions: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class PromotionDecision:
    approved: bool
    blockers: tuple[str, ...]
    reasons: tuple[str, ...]


class PromotionGate:
    def __init__(
        self,
        min_confidence: float = 0.75,
        max_missing_ratio: float = 0.0,
        max_unexpected_ratio: float = 0.0,
        max_repeated_mismatches: int = 0,
    ):
        self.min_confidence = min_confidence
        self.max_missing_ratio = max_missing_ratio
        self.max_unexpected_ratio = max_unexpected_ratio
        self.max_repeated_mismatches = max_repeated_mismatches

    def evaluate(
        self, plan: RoutingPlan, feedback: MismatchFeedback | None = None
    ) -> PromotionDecision:
        blockers: list[str] = []
        if feedback is not None:
            actual_count = len(plan.load_order)
            expected_count = actual_count - len(feedback.unexpected) + len(feedback.missing)
            missing_ratio = _ratio(len(feedback.missing), expected_count)
            unexpected_ratio = _ratio(len(feedback.unexpected), actual_count)

            if missing_ratio > self.max_missing_ratio:
                blockers.append(f"missing expected skills: {', '.join(feedback.missing)}")
                blockers.append(
                    f"missing mismatch ratio {missing_ratio:.2f} "
                    f"above {self.max_missing_ratio:.2f}"
                )
            if unexpected_ratio > self.max_unexpected_ratio:
                blockers.append(f"unexpected routed skills: {', '.join(feedback.unexpected)}")
                blockers.append(
                    f"unexpected mismatch ratio {unexpected_ratio:.2f} "
                    f"above {self.max_unexpected_ratio:.2f}"
                )

            if isinstance(feedback, MismatchSummary):
                repeated_missing = tuple(
                    skill_name
                    for skill_name in feedback.repeated_missing
                    if feedback.missing_counts.get(skill_name, 0)
                    > self.max_repeated_mismatches
                )
                repeated_unexpected = tuple(
                    skill_name
                    for skill_name in feedback.repeated_unexpected
                    if feedback.unexpected_counts.get(skill_name, 0)
                    > self.max_repeated_mismatches
                )
                if repeated_missing:
                    blockers.append(
                        "repeated missing skill mismatches: "
                        + ", ".join(
                            f"{skill_name} ({feedback.missing_counts[skill_name]})"
                            for skill_name in repeated_missing
                        )
                    )
                if repeated_unexpected:
                    blockers.append(
                        "repeated unexpected skill mismatches: "
                        + ", ".join(
                            f"{skill_name} ({feedback.unexpected_counts[skill_name]})"
                            for skill_name in repeated_unexpected
                        )
                    )

        low_confidence = tuple(
            skill_name
            for skill_name in plan.load_order
            if plan.confidence.get(skill_name, 0.0) < self.min_confidence
        )
        if low_confidence:
            blockers.append(
                f"low confidence skills: {', '.join(low_confidence)} "
                f"below {self.min_confidence:.2f}"
            )

        reasons = (
            f"{len(plan.load_order)} skills routed",
            f"minimum confidence {self.min_confidence:.2f}",
            f"missing mismatch threshold {self.max_missing_ratio:.2f}",
            f"unexpected mismatch threshold {self.max_unexpected_ratio:.2f}",
            f"repeated mismatch threshold {self.max_repeated_mismatches}",
        )
        return PromotionDecision(
            approved=not blockers,
            blockers=tuple(blockers),
            reasons=reasons,
        )


class MismatchAggregator:
    def __init__(
        self,
        skills: Iterable[Skill],
        repeated_threshold: int = 2,
        max_suggested_triggers: int = 3,
    ):
        if repeated_threshold < 1:
            raise ValueError("repeated_threshold must be at least 1")
        self.repeated_threshold = repeated_threshold
        self.max_suggested_triggers = max_suggested_triggers
        self._skills_by_name = {skill.name: skill for skill in skills}
        self._missing_counts: dict[str, int] = {}
        self._unexpected_counts: dict[str, int] = {}
        self._observations = 0

    def record(
        self,
        mission: str,
        plan: RoutingPlan,
        expected_skills: Iterable[str],
    ) -> MismatchSummary:
        feedback = _feedback_for_mismatch(plan, expected_skills)
        self._observations += 1

        for skill_name in feedback.missing:
            self._missing_counts[skill_name] = self._missing_counts.get(skill_name, 0) + 1
        for skill_name in feedback.unexpected:
            self._unexpected_counts[skill_name] = (
                self._unexpected_counts.get(skill_name, 0) + 1
            )

        repeated_missing = tuple(
            skill_name
            for skill_name in feedback.missing
            if self._missing_counts[skill_name] >= self.repeated_threshold
        )
        repeated_unexpected = tuple(
            skill_name
            for skill_name in feedback.unexpected
            if self._unexpected_counts[skill_name] >= self.repeated_threshold
        )

        return MismatchSummary(
            missing=feedback.missing,
            unexpected=feedback.unexpected,
            messages=feedback.messages,
            observations=self._observations,
            repeated_missing=repeated_missing,
            repeated_unexpected=repeated_unexpected,
            missing_counts=dict(self._missing_counts),
            unexpected_counts=dict(self._unexpected_counts),
            manifest_trigger_suggestions=self._manifest_trigger_suggestions(
                mission, repeated_missing
            ),
        )

    def _manifest_trigger_suggestions(
        self, mission: str, repeated_missing: tuple[str, ...]
    ) -> tuple[dict[str, object], ...]:
        suggestions: list[dict[str, object]] = []
        for skill_name in repeated_missing:
            skill = self._skills_by_name.get(skill_name)
            if skill is None:
                continue
            add_triggers = _suggested_triggers(
                mission,
                skill,
                max_suggestions=self.max_suggested_triggers,
            )
            if add_triggers:
                suggestion: dict[str, object] = {
                    "skill_id": skill.id,
                    "skill": skill.name,
                    "add_triggers": add_triggers,
                    "reason": (
                        f"{skill.name} was repeatedly expected but not routed for "
                        f"mission terms: {', '.join(add_triggers)}"
                    ),
                }
                if skill.path is not None:
                    suggestion["path"] = skill.path
                suggestions.append(suggestion)
        return tuple(suggestions)


FallbackResult = Sequence[str] | dict[str, object]
LlmFallback = Callable[[str, tuple[Skill, ...]], FallbackResult]
HttpPost = Callable[
    [str, dict[str, object], Mapping[str, str], float],
    Mapping[str, object],
]


class SkillRouter:
    def __init__(
        self,
        skills: Iterable[Skill],
        llm_fallback: LlmFallback | None = None,
        route_log_path: str | Path | None = None,
        ambiguity_margin: float = 0.15,
    ):
        if ambiguity_margin < 0.0:
            raise ValueError("ambiguity_margin must be non-negative")
        self._skills = tuple(skills)
        self._skills_by_name = {skill.name: skill for skill in self._skills}
        self._skills_by_id = {skill.id: skill for skill in self._skills}
        self._llm_fallback = llm_fallback
        self._route_log_path = Path(route_log_path) if route_log_path is not None else None
        self._ambiguity_margin = ambiguity_margin

    def route(self, mission: str, mode: RouteMode | str = RouteMode.AUTO) -> RoutingPlan:
        route_mode = RouteMode(mode)
        tokens = _tokenize(mission)
        explicit_names = _explicit_skill_names(mission, self._skills_by_name)

        if route_mode is RouteMode.LLM_FALLBACK:
            plan = self._route_with_fallback(mission)
        else:
            deterministic_mode = (
                RouteMode.EXPLICIT if explicit_names else RouteMode.DETERMINISTIC
            )
            routed_skills = self._deterministic_route(
                tokens=tokens,
                explicit_names=explicit_names,
                source_mode=deterministic_mode,
            )
            plan = _plan_from_routed_skills(routed_skills, deterministic_mode)

            if (
                route_mode is RouteMode.AUTO
                and not plan.load_order
                and self._llm_fallback is not None
            ):
                plan = self._route_with_fallback(mission)

        self._write_route_log(plan)
        return plan

    def assign_subtasks(self, subtask_request: SubtaskRequest) -> tuple[SubagentAssignment, ...]:
        assignments: list[SubagentAssignment] = []
        for subtask in subtask_request.subtasks:
            plan = self.route(subtask.task)
            if self._llm_fallback is not None and _is_ambiguous_assignment_plan(
                plan, self._ambiguity_margin
            ):
                plan = self._route_with_fallback(subtask.task)
                self._write_route_log(plan)
            assignments.append(_assignment_from_plan(subtask, plan, self._skills_by_name))
        return tuple(assignments)

    def prompts_for_assignments(
        self, assignments: Iterable[SubagentAssignment]
    ) -> dict[str, str]:
        prompts: dict[str, str] = {}
        for assignment in assignments:
            prompts[assignment.subtask_id] = build_subagent_prompt(
                assignment, self._skills_by_id
            )
        return prompts

    def _deterministic_route(
        self,
        tokens: set[str],
        explicit_names: tuple[str, ...],
        source_mode: RouteMode,
    ) -> tuple[RoutedSkill, ...]:
        explicit = set(explicit_names)
        routed: list[RoutedSkill] = []

        for skill in self._skills:
            matched_terms: tuple[str, ...] = ()
            is_required = False
            source = source_mode.value
            confidence = 0.0

            if skill.name in explicit:
                matched_terms = (f"${skill.name}",)
                is_required = True
                confidence = 1.0
            elif _matches(tokens, (skill.name, *skill.required_for)):
                matched_terms = _matched_terms(tokens, (skill.name, *skill.required_for))
                is_required = True
                confidence = 1.0
            elif _matches(tokens, skill.triggers):
                matched_terms = _matched_terms(tokens, skill.triggers)
                confidence = _confidence(tokens, skill.triggers)

            if confidence:
                routed.append(
                    RoutedSkill(
                        skill_id=skill.id,
                        name=skill.name,
                        required=is_required,
                        confidence=confidence,
                        matched_terms=matched_terms,
                        source=source,
                        reason=_route_reason(skill, matched_terms, source),
                        content_hash=skill.content_hash,
                    )
                )

        return tuple(routed)

    def _route_with_fallback(self, mission: str) -> RoutingPlan:
        if self._llm_fallback is None:
            return _plan_from_routed_skills((), RouteMode.LLM_FALLBACK)

        selected_names = _fallback_skill_names(self._llm_fallback(mission, self._skills))
        routed_skills = tuple(
            RoutedSkill(
                skill_id=self._skills_by_name[name].id,
                name=name,
                required=bool(self._skills_by_name[name].required_for),
                confidence=0.75,
                matched_terms=("llm_fallback",),
                source="llm_fallback",
                reason="Selected by deterministic fallback adapter for ambiguous/no-match input.",
                content_hash=self._skills_by_name[name].content_hash,
            )
            for name in selected_names
            if name in self._skills_by_name
        )
        return _plan_from_routed_skills(routed_skills, RouteMode.LLM_FALLBACK)

    def _write_route_log(self, plan: RoutingPlan) -> None:
        if self._route_log_path is None:
            return

        event = {
            "mode": plan.mode.value,
            "required": list(plan.required),
            "optional": list(plan.optional),
            "load_order": list(plan.load_order),
            "confidence": plan.confidence,
            "routed_skills": [skill.to_json() for skill in plan.routed_skills],
        }
        self._route_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self._route_log_path.open("a", encoding="utf-8") as route_log:
            route_log.write(json.dumps(event, sort_keys=True) + "\n")

    def feedback_for_mismatch(
        self, plan: RoutingPlan, expected_skills: Iterable[str]
    ) -> MismatchFeedback:
        return _feedback_for_mismatch(plan, expected_skills)


class SkillLoader:
    def __init__(self, skills: Iterable[Skill]):
        self._skills = {skill.name: skill for skill in skills}
        self._cache: dict[str, dict[str, object]] = {}
        self._load_counts = {name: 0 for name in self._skills}
        self.cache_hits = 0
        self.audit_log: list[AuditEvent] = []

    def load(self, skill_name: str) -> dict[str, object]:
        if skill_name not in self._skills:
            raise KeyError(f"Unknown skill: {skill_name}")

        skill = self._skills[skill_name]
        cache_key = f"{skill.id}:{skill.content_hash}"
        cached = self._cache.get(cache_key)
        if cached:
            self.cache_hits += 1
            self._audit("cache_hit", skill, "Loaded skill context from shared cache")
            return cached

        context = {
            "skill_id": skill.id,
            "name": skill.name,
            "triggers": skill.triggers,
            "required_for": skill.required_for,
            "content": skill.content,
            "content_hash": skill.content_hash,
            "cache_key": cache_key,
        }
        self._cache[cache_key] = context
        self._load_counts[skill.name] += 1
        self._audit("loaded", skill, "Loaded skill context from manifest content")
        return context

    def replace_skill(self, skill: Skill) -> None:
        self._skills[skill.name] = skill
        self._load_counts.setdefault(skill.name, 0)

    @property
    def total_loads(self) -> int:
        return sum(self._load_counts.values())

    def load_count(self, skill_name: str) -> int:
        return self._load_counts.get(skill_name, 0)

    def _audit(self, event: str, skill: Skill, message: str) -> None:
        self.audit_log.append(
            AuditEvent(
                event=event,
                skill_name=skill.name,
                content_hash=skill.content_hash,
                message=message,
            )
        )


def load_skills_from_manifest(path: str | Path) -> tuple[Skill, ...]:
    manifest_path = Path(path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _validate_manifest(manifest, manifest_path.parent)
    skills: list[Skill] = []
    for item in manifest["skills"]:
        skill_path = (manifest_path.parent / item["path"]).resolve()
        skills.append(
            Skill(
                skill_id=item["skill_id"],
                name=item["name"],
                triggers=tuple(item.get("triggers", ())),
                required_for=tuple(item.get("required_for", ())),
                path=str(skill_path),
                content=skill_path.read_text(encoding="utf-8"),
            )
        )
    return tuple(skills)


def load_subtask_request(path: str | Path) -> SubtaskRequest:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("subtask input must be an object")

    request = payload.get("request")
    if not isinstance(request, str) or not request.strip():
        raise ValueError("request must be a non-empty string")

    raw_subtasks = payload.get("subtasks")
    if not isinstance(raw_subtasks, list) or not raw_subtasks:
        raise ValueError("subtasks must be a non-empty list")

    subtasks: list[Subtask] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(raw_subtasks):
        prefix = f"subtasks[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{prefix} must be an object")
        subtask_id = item.get("id")
        task = item.get("task")
        if not isinstance(subtask_id, str) or not subtask_id.strip():
            raise ValueError(f"{prefix}.id must be a non-empty string")
        if subtask_id in seen_ids:
            raise ValueError(f"{prefix}.id duplicates {subtask_id}")
        if not isinstance(task, str) or not task.strip():
            raise ValueError(f"{prefix}.task must be a non-empty string")
        seen_ids.add(subtask_id)
        subtasks.append(Subtask(id=subtask_id, task=task))

    return SubtaskRequest(request=request, subtasks=tuple(subtasks))


def build_assignment_plan(
    subtask_request: SubtaskRequest,
    skills: Iterable[Skill],
    llm_fallback: LlmFallback | None = None,
    ambiguity_margin: float = 0.15,
) -> dict[str, object]:
    router = SkillRouter(
        skills, llm_fallback=llm_fallback, ambiguity_margin=ambiguity_margin
    )
    assignments = router.assign_subtasks(subtask_request)
    return {
        "request": subtask_request.request,
        "subagents": [assignment.to_json() for assignment in assignments],
    }


def build_prompt_plan(
    subtask_request: SubtaskRequest,
    skills: Iterable[Skill],
    llm_fallback: LlmFallback | None = None,
    ambiguity_margin: float = 0.15,
) -> dict[str, object]:
    skill_tuple = tuple(skills)
    router = SkillRouter(
        skill_tuple, llm_fallback=llm_fallback, ambiguity_margin=ambiguity_margin
    )
    assignments = router.assign_subtasks(subtask_request)
    prompts = router.prompts_for_assignments(assignments)
    return {
        "request": subtask_request.request,
        "prompts": [
            {
                "subtask_id": assignment.subtask_id,
                "skill_id": assignment.skill_id,
                "prompt": prompts[assignment.subtask_id],
            }
            for assignment in assignments
        ],
    }


def create_openai_fallback(
    api_key: str | None = None,
    model: str | None = None,
    *,
    endpoint: str = "https://api.openai.com/v1/responses",
    timeout: float = 20.0,
    http_post: HttpPost | None = None,
) -> LlmFallback:
    resolved_api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not resolved_api_key:
        raise ValueError("OPENAI_API_KEY is required for OpenAI fallback routing")

    resolved_model = model or os.environ.get("OPENAI_ROUTER_MODEL", "gpt-5.5")
    post = http_post or _http_post_json

    def fallback(mission: str, skills: tuple[Skill, ...]) -> FallbackResult:
        payload = {
            "model": resolved_model,
            "store": False,
            "instructions": (
                "Select the best skill names for this agent subtask. "
                "Only choose from the provided skills. Return JSON only."
            ),
            "input": _openai_fallback_input(mission, skills),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "skill_routing",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "skills": {
                                "type": "array",
                                "items": {"type": "string"},
                            }
                        },
                        "required": ["skills"],
                    },
                }
            },
        }
        headers = {
            "Authorization": f"Bearer {resolved_api_key}",
            "Content-Type": "application/json",
        }
        response = post(endpoint, payload, headers, timeout)
        return {"skills": list(_fallback_skill_names(_openai_response_json(response)))}

    return fallback


def build_subagent_prompt(
    assignment: SubagentAssignment,
    skills_by_id: dict[str, Skill],
) -> str:
    if assignment.skill_id is None:
        return (
            f"You are assigned this subtask: {assignment.subtask}\n\n"
            "No preloaded skill was selected for this subtask. "
            f"Reason: {assignment.reason}\n"
            "Before proceeding, state what additional context or human routing decision is needed."
        )

    skill = skills_by_id[assignment.skill_id]
    return (
        f"You are assigned this subtask: {assignment.subtask}\n\n"
        f"Preloaded skill: {skill.name} ({skill.id})\n"
        f"Skill hash: {skill.content_hash}\n"
        f"Selection mode: {assignment.selection_mode}\n"
        f"Reason: {assignment.reason}\n\n"
        "Before using it, state why this skill applies.\n\n"
        "Compact skill context:\n"
        f"{skill.compact_context()}"
    )


def run_demo() -> dict[str, int | bool]:
    skills = load_skills_from_manifest(_default_manifest_path())
    subagent_missions = (
        "Planner: read the active mission spec and verification workflow",
        "Builder: implement with tests from the same mission spec",
        "Tester: verify the implementation using the mission spec",
    )

    router = SkillRouter(skills)
    loader = SkillLoader(skills)
    routed_requests = 0

    for mission in subagent_missions:
        for skill_name in router.route(mission).load_order:
            loader.load(skill_name)
            routed_requests += 1

    promotion = PromotionGate(min_confidence=0.5).evaluate(
        router.route("ShipSpec mission with tests and verification")
    )
    return {
        "subagents": len(subagent_missions),
        "naive_loads": routed_requests,
        "routed_loads": loader.total_loads,
        "cache_hits": loader.cache_hits,
        "audit_events": len(loader.audit_log),
        "promotion_approved": promotion.approved,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skill-router")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("demo", "route", "prompts"),
        default="demo",
    )
    parser.add_argument("input", nargs="?")
    parser.add_argument(
        "--manifest",
        default=str(_default_manifest_path()),
        help="Path to skills manifest JSON.",
    )
    parser.add_argument(
        "--openai-fallback",
        action="store_true",
        help="Use OPENAI_API_KEY for ambiguous or no-match subtask routing.",
    )
    parser.add_argument(
        "--openai-model",
        default=os.environ.get("OPENAI_ROUTER_MODEL", "gpt-5.5"),
        help="OpenAI model for fallback routing when --openai-fallback is set.",
    )
    parser.add_argument(
        "--ambiguity-margin",
        type=float,
        default=0.15,
        help=(
            "Confidence gap below which the top two skills are treated as a "
            "near-tie and handed to the LLM fallback (default: 0.15)."
        ),
    )
    args = parser.parse_args(argv)

    if args.command == "demo":
        output: dict[str, object] = run_demo()
    else:
        if not args.input:
            parser.error(f"{args.command} requires a subtask JSON file")
        skills = load_skills_from_manifest(args.manifest)
        subtask_request = load_subtask_request(args.input)
        llm_fallback = (
            create_openai_fallback(model=args.openai_model)
            if args.openai_fallback
            else None
        )
        if args.command == "route":
            output = build_assignment_plan(
                subtask_request, skills, llm_fallback, args.ambiguity_margin
            )
        else:
            output = build_prompt_plan(
                subtask_request, skills, llm_fallback, args.ambiguity_margin
            )

    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


def _default_manifest_path() -> Path:
    return Path(__file__).resolve().parents[2] / "manifests" / "demo-skills.json"


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9-]+", text.lower()))


def _matches(tokens: set[str], needles: Iterable[str]) -> bool:
    return any(
        needle.lower() in tokens or f"{needle.lower()}s" in tokens for needle in needles
    )


def _matched_terms(tokens: set[str], needles: Iterable[str]) -> tuple[str, ...]:
    return tuple(
        needle
        for needle in needles
        if needle.lower() in tokens or f"{needle.lower()}s" in tokens
    )


def _confidence(tokens: set[str], triggers: tuple[str, ...]) -> float:
    if not triggers:
        return 0.0

    matches = sum(1 for trigger in triggers if _matches(tokens, (trigger,)))
    if matches == 0:
        return 0.0
    return round(0.5 + (matches / len(triggers) / 2), 2)


def _explicit_skill_names(
    mission: str, skills_by_name: dict[str, Skill]
) -> tuple[str, ...]:
    names: list[str] = []
    for explicit_name in re.findall(r"\$([a-z0-9][a-z0-9-]*)", mission.lower()):
        if explicit_name in skills_by_name:
            names.append(explicit_name)
    return tuple(dict.fromkeys(names))


def _fallback_skill_names(result: FallbackResult) -> tuple[str, ...]:
    raw_names: object
    if isinstance(result, dict):
        raw_names = result.get("skills", ())
    else:
        raw_names = result

    if isinstance(raw_names, str) or not isinstance(raw_names, Sequence):
        return ()

    names: list[str] = []
    for item in raw_names:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict) and isinstance(item.get("name"), str):
            names.append(item["name"])
    return tuple(dict.fromkeys(names))


def _openai_fallback_input(mission: str, skills: tuple[Skill, ...]) -> str:
    catalog = [
        {
            "name": skill.name,
            "skill_id": skill.id,
            "triggers": list(skill.triggers),
            "required_for": list(skill.required_for),
        }
        for skill in skills
    ]
    return json.dumps(
        {
            "subtask": mission,
            "available_skills": catalog,
            "selection_rules": [
                "Choose at most one best skill for a subtask assignment.",
                "Return an empty skills list if no skill is appropriate.",
            ],
        },
        sort_keys=True,
    )


def _openai_response_json(response: Mapping[str, object]) -> FallbackResult:
    output_text = response.get("output_text")
    if isinstance(output_text, str):
        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError:
            return ()
        if isinstance(parsed, dict):
            return parsed
        return ()

    output = response.get("output")
    if not isinstance(output, Sequence) or isinstance(output, str):
        return ()

    text_chunks: list[str] = []
    for item in output:
        if not isinstance(item, Mapping):
            continue
        content = item.get("content")
        if not isinstance(content, Sequence) or isinstance(content, str):
            continue
        for content_item in content:
            if not isinstance(content_item, Mapping):
                continue
            text = content_item.get("text")
            if isinstance(text, str):
                text_chunks.append(text)

    if not text_chunks:
        return ()

    try:
        parsed = json.loads("".join(text_chunks))
    except json.JSONDecodeError:
        return ()
    if isinstance(parsed, dict):
        return parsed
    return ()


def _http_post_json(
    url: str,
    payload: dict[str, object],
    headers: Mapping[str, str],
    timeout: float,
) -> Mapping[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=dict(headers),
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        parsed = json.loads(response.read().decode("utf-8"))
    if not isinstance(parsed, dict):
        return {}
    return parsed


def _plan_from_routed_skills(
    routed_skills: tuple[RoutedSkill, ...], mode: RouteMode
) -> RoutingPlan:
    required = tuple(skill.name for skill in routed_skills if skill.required)
    optional = tuple(skill.name for skill in routed_skills if not skill.required)
    load_order = tuple(dict.fromkeys([*required, *optional]))
    confidence = {skill.name: skill.confidence for skill in routed_skills}
    return RoutingPlan(
        required=required,
        optional=optional,
        load_order=load_order,
        confidence=confidence,
        mode=mode,
        routed_skills=routed_skills,
    )


def _is_ambiguous_assignment_plan(plan: RoutingPlan, margin: float = 0.0) -> bool:
    """Return True when the top two skills are too close to pick confidently.

    ``margin`` is the confidence gap below which routing is considered
    ambiguous. With ``margin=0`` only exact ties count; a positive margin also
    flags near-ties so the LLM fallback can break them. A required or explicitly
    named top skill is a strong deterministic signal and is never treated as
    ambiguous.
    """
    if len(plan.routed_skills) < 2:
        return False

    ranked = sorted(
        plan.routed_skills, key=lambda skill: skill.confidence, reverse=True
    )
    top, second = ranked[0], ranked[1]
    if top.required:
        return False
    return (top.confidence - second.confidence) <= margin


def _assignment_from_plan(
    subtask: Subtask,
    plan: RoutingPlan,
    skills_by_name: dict[str, Skill],
) -> SubagentAssignment:
    if not plan.routed_skills:
        return SubagentAssignment(
            subtask_id=subtask.id,
            subtask=subtask.task,
            skill_id=None,
            skill_name=None,
            skill_hash=None,
            confidence=0.0,
            selection_mode=RouteMode.NO_MATCH.value,
            reason="No skill matched the subtask text strongly enough.",
        )

    selected = max(plan.routed_skills, key=lambda item: item.confidence)
    skill = skills_by_name[selected.name]
    return SubagentAssignment(
        subtask_id=subtask.id,
        subtask=subtask.task,
        skill_id=skill.id,
        skill_name=skill.name,
        skill_hash=skill.content_hash,
        confidence=selected.confidence,
        selection_mode=selected.source,
        reason=selected.reason,
    )


def _feedback_for_mismatch(
    plan: RoutingPlan, expected_skills: Iterable[str]
) -> MismatchFeedback:
    expected = tuple(expected_skills)
    actual = plan.load_order
    missing = tuple(skill for skill in expected if skill not in actual)
    unexpected = tuple(skill for skill in actual if skill not in expected)
    messages = tuple(
        message
        for message in (
            f"missing expected skills: {', '.join(missing)}" if missing else "",
            f"unexpected routed skills: {', '.join(unexpected)}" if unexpected else "",
        )
        if message
    )
    return MismatchFeedback(
        missing=missing,
        unexpected=unexpected,
        messages=messages,
    )


def _route_reason(skill: Skill, matched_terms: tuple[str, ...], source: str) -> str:
    if not matched_terms:
        return f"Selected {skill.name} by {source}."
    return (
        f"Selected {skill.name} by {source}; matched "
        f"{', '.join(matched_terms)}."
    )


def _ratio(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return count / total


def _suggested_triggers(
    mission: str,
    skill: Skill,
    max_suggestions: int,
) -> tuple[str, ...]:
    existing = {
        *skill.triggers,
        *skill.required_for,
        *skill.name.split("-"),
        skill.name,
    }
    existing = {item.lower() for item in existing}
    ignored = {
        "and",
        "for",
        "the",
        "this",
        "that",
        "with",
        "use",
        "using",
        "write",
        "draft",
        "feature",
    }
    suggestions: list[str] = []
    for token in re.findall(r"[a-z0-9-]+", mission.lower()):
        if len(token) < 3 or token in ignored or token in existing:
            continue
        if token not in suggestions:
            suggestions.append(token)
        if len(suggestions) >= max_suggestions:
            break
    return tuple(suggestions)


def _validate_manifest(manifest: object, manifest_dir: Path) -> None:
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    skills = manifest.get("skills")
    if not isinstance(skills, list):
        raise ValueError("manifest skills must be a list")

    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for index, item in enumerate(skills):
        prefix = f"skills[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{prefix} must be an object")

        skill_id = item.get("skill_id")
        if not isinstance(skill_id, str) or not skill_id:
            raise ValueError(f"{prefix}.skill_id must be a non-empty string")
        if skill_id in seen_ids:
            raise ValueError(f"{prefix}.skill_id duplicates {skill_id}")
        seen_ids.add(skill_id)

        name = item.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{prefix}.name must be a non-empty string")
        if name in seen_names:
            raise ValueError(f"{prefix}.name duplicates {name}")
        seen_names.add(name)

        path = item.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError(f"{prefix}.path must be a non-empty string")
        skill_path = (manifest_dir / path).resolve()
        if not skill_path.is_file():
            raise ValueError(f"{prefix}.path does not exist: {path}")

        for field in ("triggers", "required_for"):
            value = item.get(field, [])
            if not isinstance(value, list) or not all(
                isinstance(entry, str) and entry for entry in value
            ):
                raise ValueError(f"{prefix}.{field} must be a list of non-empty strings")
