import json
import tomllib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import skill_router_demo
from skill_router_demo.router import (
    MismatchAggregator,
    PromotionGate,
    RouteMode,
    Skill,
    SkillLoader,
    SkillRouter,
    Subtask,
    SubtaskRequest,
    build_assignment_plan,
    create_openai_fallback,
    build_prompt_plan,
    load_skills_from_manifest,
    load_subtask_request,
    run_demo,
)


class SkillRouterTests(unittest.TestCase):
    def setUp(self):
        self.skills = [
            Skill(
                skill_id="shipspec",
                name="shipspec",
                triggers=("mission", "spec", "verification"),
                required_for=("ship",),
                content="ShipSpec instructions v1",
            ),
            Skill(
                skill_id="test-driven-development",
                name="test-driven-development",
                triggers=("test", "implementation", "bugfix"),
                content="TDD instructions v1",
            ),
            Skill(
                skill_id="frontend-testing-debugging",
                name="frontend-testing-debugging",
                triggers=("browser", "ui", "playwright"),
                content="Frontend testing instructions v1",
            ),
        ]

    def test_loads_skills_from_manifest_file_paths(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            skill_file = root / "skills" / "shipspec" / "SKILL.md"
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text("ShipSpec manifest file content", encoding="utf-8")
            manifest_path = root / "manifests" / "skills.json"
            manifest_path.parent.mkdir()
            manifest_path.write_text(
                json.dumps(
                    {
                        "skills": [
                            {
                                "skill_id": "shipspec",
                                "name": "shipspec",
                                "triggers": ["mission", "spec"],
                                "required_for": ["ship"],
                                "path": "../skills/shipspec/SKILL.md",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            skills = load_skills_from_manifest(manifest_path)

        self.assertEqual(len(skills), 1)
        self.assertEqual(skills[0].id, "shipspec")
        self.assertEqual(skills[0].content, "ShipSpec manifest file content")
        self.assertEqual(skills[0].content_hash[:8], "316db73b")

    def test_package_metadata_exposes_local_library_and_cli(self):
        pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(pyproject["project"]["readme"], "README.md")
        self.assertEqual(
            pyproject["project"]["scripts"]["skill-router"],
            "skill_router_demo.router:main",
        )
        self.assertEqual(
            pyproject["project"]["scripts"]["skill-router-demo"],
            "skill_router_demo.router:main",
        )

    def test_package_root_exports_reusable_library_api(self):
        expected_exports = {
            "Subtask",
            "SubtaskRequest",
            "SubagentAssignment",
            "build_assignment_plan",
            "build_prompt_plan",
            "load_subtask_request",
        }

        self.assertTrue(expected_exports.issubset(set(skill_router_demo.__all__)))
        self.assertIs(skill_router_demo.Subtask, Subtask)
        self.assertIs(skill_router_demo.SubtaskRequest, SubtaskRequest)
        self.assertIs(skill_router_demo.build_assignment_plan, build_assignment_plan)

    def test_manifest_validation_rejects_missing_skill_file(self):
        with TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "skills.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "skills": [
                            {
                                "skill_id": "shipspec",
                                "name": "shipspec",
                                "triggers": ["mission"],
                                "path": "missing/SKILL.md",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "path does not exist"):
                load_skills_from_manifest(manifest_path)

    def test_manifest_validation_rejects_duplicate_skill_id(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            skill_file = root / "SKILL.md"
            skill_file.write_text("content", encoding="utf-8")
            manifest_path = root / "skills.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "skills": [
                            {
                                "skill_id": "same",
                                "name": "one",
                                "triggers": [],
                                "path": "SKILL.md",
                            },
                            {
                                "skill_id": "same",
                                "name": "two",
                                "triggers": [],
                                "path": "SKILL.md",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "skill_id duplicates same"):
                load_skills_from_manifest(manifest_path)

    def test_load_subtask_request_validates_shape(self):
        with TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "subtasks.json"
            path.write_text(
                json.dumps(
                    {
                        "request": "Ship feature",
                        "subtasks": [{"id": "docs", "task": "Read the PDF"}],
                    }
                ),
                encoding="utf-8",
            )

            request = load_subtask_request(path)

        self.assertEqual(request.request, "Ship feature")
        self.assertEqual(request.subtasks[0].id, "docs")
        self.assertEqual(request.subtasks[0].task, "Read the PDF")

    def test_load_subtask_request_rejects_malformed_input(self):
        with TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "subtasks.json"
            path.write_text(
                json.dumps({"request": "Ship feature", "subtasks": [{"id": "docs"}]}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, r"subtasks\[0\].task"):
                load_subtask_request(path)

    def test_routes_required_and_optional_skills_from_mission_text(self):
        router = SkillRouter(self.skills)

        plan = router.route(
            "Implement the active ShipSpec mission with focused tests and verification evidence"
        )

        self.assertEqual(plan.required, ("shipspec",))
        self.assertEqual(plan.optional, ("test-driven-development",))
        self.assertEqual(plan.load_order, ("shipspec", "test-driven-development"))
        self.assertEqual(plan.confidence["shipspec"], 1.0)
        self.assertGreaterEqual(plan.confidence["test-driven-development"], 0.5)

    def test_routes_named_skill_as_explicit_selection_without_extra_matches(self):
        router = SkillRouter(self.skills)

        plan = router.route("Use $shipspec only for this mission")

        self.assertEqual(plan.mode, RouteMode.EXPLICIT)
        self.assertEqual(tuple(item.name for item in plan.routed_skills), ("shipspec",))
        self.assertEqual(plan.routed_skills[0].required, True)
        self.assertEqual(plan.routed_skills[0].matched_terms, ("$shipspec",))
        self.assertEqual(plan.required, ("shipspec",))
        self.assertEqual(plan.optional, ())

    def test_llm_fallback_routes_when_deterministic_mode_finds_no_skills(self):
        def fallback(mission, skills):
            self.assertIn("launch readiness", mission)
            self.assertEqual(
                tuple(skill.name for skill in skills),
                tuple(skill.name for skill in self.skills),
            )
            return {"skills": ["shipspec", "test-driven-development"]}

        router = SkillRouter(self.skills, llm_fallback=fallback)

        plan = router.route("Coordinate launch readiness", mode=RouteMode.AUTO)

        self.assertEqual(plan.mode, RouteMode.LLM_FALLBACK)
        self.assertEqual(plan.required, ("shipspec",))
        self.assertEqual(plan.optional, ("test-driven-development",))
        self.assertEqual(plan.load_order, ("shipspec", "test-driven-development"))
        self.assertEqual(plan.routed_skills[0].source, "llm_fallback")
        self.assertGreaterEqual(plan.confidence["shipspec"], 0.75)

    def test_modes_can_disable_fallback_or_force_it(self):
        fallback_calls = []

        def fallback(mission, skills):
            fallback_calls.append(mission)
            return ("frontend-testing-debugging",)

        router = SkillRouter(self.skills, llm_fallback=fallback)

        deterministic = router.route(
            "Coordinate launch readiness", mode=RouteMode.DETERMINISTIC
        )
        forced = router.route("Coordinate launch readiness", mode=RouteMode.LLM_FALLBACK)

        self.assertEqual(deterministic.load_order, ())
        self.assertEqual(forced.load_order, ("frontend-testing-debugging",))
        self.assertEqual(forced.mode, RouteMode.LLM_FALLBACK)
        self.assertEqual(fallback_calls, ["Coordinate launch readiness"])

    def test_route_log_writes_jsonl_with_routed_skills(self):
        with TemporaryDirectory() as tmp_dir:
            route_log_path = Path(tmp_dir) / "routes.jsonl"
            router = SkillRouter(self.skills, route_log_path=route_log_path)

            plan = router.route("Use $shipspec and tests")

            lines = route_log_path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(len(lines), 1)
        event = json.loads(lines[0])
        self.assertEqual(event["mode"], "explicit")
        self.assertEqual(event["load_order"], ["shipspec", "test-driven-development"])
        self.assertEqual(event["routed_skills"][0]["skill_id"], "shipspec")
        self.assertEqual(
            event["routed_skills"][0]["content_hash"],
            self.skills[0].content_hash,
        )
        self.assertEqual(
            tuple(item.name for item in plan.routed_skills),
            ("shipspec", "test-driven-development"),
        )

    def test_shared_loader_loads_repeated_skills_once_for_multiple_subagents(self):
        router = SkillRouter(self.skills)
        loader = SkillLoader(self.skills)

        missions = [
            "Planner: read the active mission spec and verification workflow",
            "Builder: implement with tests from the same mission spec",
            "Tester: verify the implementation using the mission spec",
        ]

        for mission in missions:
            for skill_name in router.route(mission).load_order:
                loader.load(skill_name)

        self.assertEqual(loader.load_count("shipspec"), 1)
        self.assertEqual(loader.total_loads, 2)
        self.assertEqual(loader.cache_hits, 3)
        self.assertEqual(loader.audit_log[0].event, "loaded")
        self.assertEqual(loader.audit_log[-1].event, "cache_hit")

    def test_content_hash_cache_reloads_changed_skill_content(self):
        original = Skill(
            skill_id="shipspec",
            name="shipspec",
            triggers=("mission",),
            content="ShipSpec instructions v1",
        )
        updated = Skill(
            skill_id="shipspec",
            name="shipspec",
            triggers=("mission",),
            content="ShipSpec instructions v2",
        )
        loader = SkillLoader([original])

        first = loader.load("shipspec")
        loader.replace_skill(updated)
        second = loader.load("shipspec")

        self.assertNotEqual(first["content_hash"], second["content_hash"])
        self.assertNotEqual(first["cache_key"], second["cache_key"])
        self.assertEqual(loader.load_count("shipspec"), 2)
        self.assertEqual(loader.audit_log[-1].event, "loaded")

    def test_assignment_plan_outputs_one_assignment_per_subtask(self):
        request = _fixture_subtask_request()

        plan = build_assignment_plan(request, self.skills)

        self.assertEqual(plan["request"], "Ship feature")
        self.assertEqual(len(plan["subagents"]), 3)
        assignments = {item["subtask_id"]: item for item in plan["subagents"]}
        self.assertEqual(assignments["spec"]["skill_id"], "shipspec")
        self.assertEqual(assignments["ui"]["skill_id"], "frontend-testing-debugging")
        self.assertEqual(assignments["unknown"]["selection_mode"], "no_match")
        self.assertIn("No skill matched", assignments["unknown"]["reason"])

    def test_assignment_plan_uses_fallback_for_no_match_subtask(self):
        def fallback(mission, skills):
            self.assertEqual(mission, "Coordinate launch calendar")
            return {"skills": ["shipspec"]}

        plan = build_assignment_plan(
            _fixture_subtask_request(),
            self.skills,
            llm_fallback=fallback,
        )

        assignments = {item["subtask_id"]: item for item in plan["subagents"]}
        self.assertEqual(assignments["unknown"]["skill_id"], "shipspec")
        self.assertEqual(assignments["unknown"]["selection_mode"], "llm_fallback")
        self.assertIn("ambiguous/no-match", assignments["unknown"]["reason"])

    def test_assignment_plan_uses_fallback_for_ambiguous_subtask(self):
        request = SubtaskRequest(
            request="Ship feature",
            subtasks=(
                Subtask(
                    id="ambiguous",
                    task="Coordinate mission browser handoff",
                ),
            ),
        )

        def fallback(mission, skills):
            self.assertIn("mission browser", mission)
            return {"skills": ["frontend-testing-debugging"]}

        plan = build_assignment_plan(request, self.skills, llm_fallback=fallback)

        assignment = plan["subagents"][0]
        self.assertEqual(assignment["skill_id"], "frontend-testing-debugging")
        self.assertEqual(assignment["selection_mode"], "llm_fallback")

    def test_openai_fallback_posts_structured_skill_selection_request(self):
        calls = []

        def fake_post(url, payload, headers, timeout):
            calls.append((url, payload, headers, timeout))
            return {"output_text": json.dumps({"skills": ["shipspec"]})}

        fallback = create_openai_fallback(
            api_key="test-key",
            model="gpt-test",
            http_post=fake_post,
        )

        result = fallback("Coordinate launch readiness", tuple(self.skills))

        self.assertEqual(result, {"skills": ["shipspec"]})
        url, payload, headers, timeout = calls[0]
        self.assertEqual(url, "https://api.openai.com/v1/responses")
        self.assertEqual(headers["Authorization"], "Bearer test-key")
        self.assertEqual(payload["model"], "gpt-test")
        self.assertEqual(payload["store"], False)
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertIn("shipspec", payload["input"])
        self.assertEqual(timeout, 20.0)

    def test_prompt_plan_contains_only_selected_skill_context(self):
        request = _fixture_subtask_request()

        plan = build_prompt_plan(request, self.skills)

        prompts = {item["subtask_id"]: item["prompt"] for item in plan["prompts"]}
        self.assertIn("Preloaded skill: shipspec", prompts["spec"])
        self.assertIn("Before using it, state why this skill applies.", prompts["spec"])
        self.assertIn("ShipSpec instructions v1", prompts["spec"])
        self.assertNotIn("Frontend testing instructions v1", prompts["spec"])
        self.assertIn("No preloaded skill was selected", prompts["unknown"])

    def test_mismatch_feedback_and_promotion_gate_block_low_confidence_routes(self):
        router = SkillRouter(self.skills)
        plan = router.route("Investigate vague browser evidence")

        feedback = router.feedback_for_mismatch(
            plan,
            expected_skills=("shipspec", "frontend-testing-debugging"),
        )
        decision = PromotionGate(min_confidence=0.8).evaluate(plan, feedback)

        self.assertEqual(feedback.missing, ("shipspec",))
        self.assertEqual(feedback.unexpected, ())
        self.assertFalse(decision.approved)
        self.assertIn("missing expected skills: shipspec", decision.blockers)

    def test_promotion_gate_can_use_mismatch_ratio_thresholds(self):
        router = SkillRouter(self.skills)
        plan = router.route("Use $shipspec and browser")
        feedback = router.feedback_for_mismatch(
            plan,
            expected_skills=("shipspec", "test-driven-development"),
        )

        strict = PromotionGate(
            min_confidence=0.5,
            max_missing_ratio=0.0,
            max_unexpected_ratio=0.0,
        ).evaluate(plan, feedback)
        tolerant = PromotionGate(
            min_confidence=0.5,
            max_missing_ratio=0.5,
            max_unexpected_ratio=0.5,
        ).evaluate(plan, feedback)

        self.assertFalse(strict.approved)
        self.assertIn("missing mismatch ratio 0.50 above 0.00", strict.blockers)
        self.assertIn("unexpected mismatch ratio 0.50 above 0.00", strict.blockers)
        self.assertTrue(tolerant.approved)

    def test_mismatch_aggregation_blocks_repeated_missing_skill_routes(self):
        router = SkillRouter(self.skills)
        aggregator = MismatchAggregator(self.skills, repeated_threshold=2)
        plan = router.route("Write acceptance criteria for the feature")

        first = aggregator.record(
            "Write acceptance criteria for the feature",
            plan,
            expected_skills=("test-driven-development",),
        )
        second = aggregator.record(
            "Write acceptance criteria for the feature",
            plan,
            expected_skills=("test-driven-development",),
        )

        self.assertEqual(first.repeated_missing, ())
        self.assertEqual(second.repeated_missing, ("test-driven-development",))
        decision = PromotionGate(
            min_confidence=0.5,
            max_missing_ratio=1.0,
            max_unexpected_ratio=1.0,
        ).evaluate(plan, second)

        self.assertFalse(decision.approved)
        self.assertIn(
            "repeated missing skill mismatches: test-driven-development (2)",
            decision.blockers,
        )

    def test_mismatch_aggregation_suggests_manifest_trigger_updates(self):
        router = SkillRouter(self.skills)
        aggregator = MismatchAggregator(self.skills, repeated_threshold=2)
        plan = router.route("Draft acceptance criteria")

        aggregator.record(
            "Draft acceptance criteria",
            plan,
            expected_skills=("test-driven-development",),
        )
        summary = aggregator.record(
            "Draft acceptance criteria",
            plan,
            expected_skills=("test-driven-development",),
        )

        self.assertEqual(len(summary.manifest_trigger_suggestions), 1)
        suggestion = summary.manifest_trigger_suggestions[0]
        self.assertEqual(suggestion["skill_id"], "test-driven-development")
        self.assertEqual(suggestion["skill"], "test-driven-development")
        self.assertIn("acceptance", suggestion["add_triggers"])

    def test_demo_reports_fewer_routed_loads_than_naive_loading(self):
        result = run_demo()

        self.assertEqual(result["subagents"], 3)
        self.assertGreater(result["naive_loads"], result["routed_loads"])
        self.assertEqual(result["routed_loads"], 2)
        self.assertEqual(result["promotion_approved"], True)
        self.assertEqual(result["audit_events"], 5)


def _fixture_subtask_request():
    return SubtaskRequest(
        request="Ship feature",
        subtasks=(
            Subtask(id="spec", task="Prepare the mission spec"),
            Subtask(id="ui", task="Use browser to verify the UI"),
            Subtask(id="unknown", task="Coordinate launch calendar"),
        ),
    )


if __name__ == "__main__":
    unittest.main()
