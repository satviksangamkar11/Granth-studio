import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict

# Ensure the test file's directory is on sys.path so we can import by plain filename
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from h1_compile_teacher import (
    load_reports,
    video_digest_prompt,
    parse_json_reply,
    cross_video_prompt,
    classify_recipe,
    usage_bucket,
    compile_teacher,
    write_outputs,
    main,
)


class TestLoadReports(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_load_reports_complete_only(self):
        # Create video folder with api_log.json
        vid_dir = Path(self.tmpdir) / "video_001"
        vid_dir.mkdir()
        api_log = {
            "shot_001": {"status": "COMPLETE", "report": {"video_id": "video_001", "inferred_technique": "technique_a"}},
            "shot_002": {"status": "PENDING", "report": {"video_id": "video_001", "inferred_technique": "technique_b"}},
            "event_001": {"status": "COMPLETE", "report": {"video_id": "video_001", "inferred_technique": "technique_c"}},
            "pilot_001": {"status": "COMPLETE", "report": {"video_id": "video_001", "inferred_technique": "technique_d"}},
        }
        with open(vid_dir / "api_log.json", "w") as f:
            json.dump(api_log, f)

        reports = load_reports(self.tmpdir)
        self.assertEqual(len(reports), 3)
        self.assertEqual(reports[0]["group_id"], "shot_001")
        self.assertEqual(reports[0]["kind"], "shot")
        self.assertEqual(reports[1]["group_id"], "event_001")
        self.assertEqual(reports[1]["kind"], "event")
        self.assertEqual(reports[2]["group_id"], "pilot_001")
        self.assertEqual(reports[2]["kind"], "pilot")

    def test_load_reports_order(self):
        # Two video folders, check order
        for i in range(2):
            vid_dir = Path(self.tmpdir) / f"video_{i:03d}"
            vid_dir.mkdir()
            api_log = {
                f"shot_{i}_b": {"status": "COMPLETE", "report": {"video_id": f"video_{i:03d}"}},
                f"shot_{i}_a": {"status": "COMPLETE", "report": {"video_id": f"video_{i:03d}"}},
            }
            with open(vid_dir / "api_log.json", "w") as f:
                json.dump(api_log, f)

        reports = load_reports(self.tmpdir)
        self.assertEqual(len(reports), 4)
        # video_000 first, then video_001; within each, natural sort of group_id
        self.assertEqual(reports[0]["group_id"], "shot_0_a")
        self.assertEqual(reports[1]["group_id"], "shot_0_b")
        self.assertEqual(reports[2]["group_id"], "shot_1_a")
        self.assertEqual(reports[3]["group_id"], "shot_1_b")

    def test_load_reports_corrupt_json_raises(self):
        vid_dir = Path(self.tmpdir) / "video_001"
        vid_dir.mkdir()
        with open(vid_dir / "api_log.json", "w") as f:
            f.write("{ not valid json }")

        with self.assertRaises(ValueError) as cm:
            load_reports(self.tmpdir)
        self.assertIn("Corrupt JSON", str(cm.exception))
        self.assertIn("api_log.json", str(cm.exception))


class TestVideoDigestPrompt(unittest.TestCase):
    def test_drops_low_unknown_lines(self):
        reports = [
            {
                "group_id": "shot_001",
                "start_time": 0.0,
                "end_time": 1.0,
                "evidence_frames": [1, 2, 3],
                "inferred_technique": "UNKNOWN",
                "observed_animation": "nothing visible, black frame",
                "camera_motion": "static",
                "character_motion": "none",
                "visual_effects": "none",
                "required_assets": "none",
                "granthstudio_capability": "UNKNOWN",
                "confidence": "LOW",
            },
            {
                "group_id": "shot_002",
                "start_time": 1.0,
                "end_time": 2.0,
                "evidence_frames": [4, 5],
                "inferred_technique": "technique_x",
                "observed_animation": "character walks",
                "camera_motion": "pan",
                "character_motion": "walk cycle",
                "visual_effects": "none",
                "required_assets": "walk cycle preset",
                "granthstudio_capability": "V2_REUSE",
                "confidence": "HIGH",
            },
        ]
        prompt = video_digest_prompt("video_001", reports)
        self.assertIn("shot_002", prompt)
        self.assertNotIn("shot_001", prompt)  # Dropped due to LOW + black frame
        self.assertIn("technique_x", prompt)
        self.assertIn("V2_REUSE", prompt)

    def test_truncates_at_max_chars(self):
        reports = []
        for i in range(100):
            reports.append({
                "group_id": f"shot_{i:03d}",
                "start_time": float(i),
                "end_time": float(i + 1),
                "evidence_frames": [i * 10],
                "inferred_technique": f"technique_{i}",
                "observed_animation": "observed " + "x" * 200,
                "camera_motion": "static",
                "character_motion": "idle",
                "visual_effects": "none",
                "required_assets": "none",
                "granthstudio_capability": "V2_REUSE",
                "confidence": "HIGH",
            })
        prompt = video_digest_prompt("video_001", reports, max_chars=5000)
        self.assertIn("[truncated:", prompt)
        # Should keep earliest lines
        self.assertIn("shot_000", prompt)
        self.assertIn("shot_001", prompt)

    def test_includes_group_ids_and_frames(self):
        reports = [{
            "group_id": "shot_001",
            "start_time": 0.0,
            "end_time": 1.0,
            "evidence_frames": [10, 20, 30],
            "inferred_technique": "test_tech",
            "observed_animation": "test observed",
            "camera_motion": "static",
            "character_motion": "idle",
            "visual_effects": "none",
            "required_assets": "none",
            "granthstudio_capability": "V2_REUSE",
            "confidence": "HIGH",
        }]
        prompt = video_digest_prompt("video_001", reports)
        self.assertIn("shot_001", prompt)
        self.assertIn("frames=[10,20,30]", prompt)
        self.assertIn("t=0.0-1.0s", prompt)


class TestParseJsonReply(unittest.TestCase):
    def test_valid_json(self):
        text = '{"key": "value", "num": 42}'
        result = parse_json_reply(text)
        self.assertEqual(result, {"key": "value", "num": 42})

    def test_with_code_fences(self):
        text = '```json\n{"a": 1}\n```'
        result = parse_json_reply(text)
        self.assertEqual(result, {"a": 1})

    def test_with_leading_prose(self):
        text = 'Here is the result:\n{"b": 2}\nDone.'
        result = parse_json_reply(text)
        self.assertEqual(result, {"b": 2})

    def test_garbage_returns_none(self):
        text = 'no json here at all'
        result = parse_json_reply(text)
        self.assertIsNone(result)

    def test_not_a_dict_returns_none(self):
        text = '[1, 2, 3]'
        result = parse_json_reply(text)
        self.assertIsNone(result)

    def test_empty_returns_none(self):
        self.assertIsNone(parse_json_reply(""))
        self.assertIsNone(parse_json_reply(None))


class TestClassifyRecipe(unittest.TestCase):
    def test_general_3_videos(self):
        recipe = {"videos": ["v1", "v2", "v3"]}
        self.assertEqual(classify_recipe(recipe), "GENERAL")

    def test_style_specific_2_videos(self):
        recipe = {"videos": ["v1", "v2"]}
        self.assertEqual(classify_recipe(recipe), "STYLE_SPECIFIC")

    def test_experimental_1_video(self):
        recipe = {"videos": ["v1"]}
        self.assertEqual(classify_recipe(recipe), "EXPERIMENTAL")

    def test_experimental_0_videos(self):
        recipe = {"videos": []}
        self.assertEqual(classify_recipe(recipe), "EXPERIMENTAL")

    def test_duplicates_count_once(self):
        recipe = {"videos": ["v1", "v1", "v2", "v2", "v2"]}
        self.assertEqual(classify_recipe(recipe), "STYLE_SPECIFIC")


class TestUsageBucket(unittest.TestCase):
    def test_usable_now_v2_reuse(self):
        recipe = {"videos": ["v1", "v2", "v3"], "capability_class": "V2_REUSE"}
        self.assertEqual(usage_bucket(recipe), "USABLE_NOW")

    def test_usable_now_v2_extension(self):
        recipe = {"videos": ["v1", "v2"], "capability_class": "V2_EXTENSION"}
        self.assertEqual(usage_bucket(recipe), "USABLE_NOW")

    def test_useful_but_blocked_new_artwork(self):
        recipe = {"videos": ["v1", "v2", "v3"], "capability_class": "NEW_ARTWORK"}
        self.assertEqual(usage_bucket(recipe), "USEFUL_BUT_BLOCKED")

    def test_useful_but_blocked_v3_action(self):
        recipe = {"videos": ["v1", "v2"], "capability_class": "V3_ACTION"}
        self.assertEqual(usage_bucket(recipe), "USEFUL_BUT_BLOCKED")

    def test_research_only_experimental(self):
        recipe = {"videos": ["v1"], "capability_class": "V2_REUSE"}
        self.assertEqual(usage_bucket(recipe), "RESEARCH_ONLY")

    def test_research_only_unknown_capability(self):
        recipe = {"videos": ["v1", "v2"], "capability_class": "UNKNOWN"}
        self.assertEqual(usage_bucket(recipe), "RESEARCH_ONLY")


class TestCompileTeacher(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_fake_ask(self, responses: Dict[str, str]):
        """Create a fake ask function that returns predefined responses."""
        call_count = {"count": 0}

        def fake_ask(prompt: str) -> str:
            call_count["count"] += 1
            # Match by video_id in prompt
            for key, resp in responses.items():
                if key in prompt:
                    return resp
            return '{"video_id": "unknown", "techniques": [], "pacing_notes": "", "audio_note": "NOT_ANALYZED"}'

        fake_ask.call_count = lambda: call_count["count"]
        return fake_ask

    def test_compile_teacher_valid_json(self):
        # Create test reports
        vid_dir = Path(self.tmpdir) / "video_001"
        vid_dir.mkdir()
        api_log = {
            "shot_001": {
                "status": "COMPLETE",
                "report": {
                    "video_id": "video_001",
                    "start_time": 0.0,
                    "end_time": 1.0,
                    "evidence_frames": [1, 2],
                    "inferred_technique": "walk_cycle",
                    "observed_animation": "character walks",
                    "camera_motion": "static",
                    "character_motion": "walk cycle",
                    "visual_effects": "none",
                    "required_assets": "walk preset",
                    "granthstudio_capability": "V2_REUSE",
                    "confidence": "HIGH",
                }
            }
        }
        with open(vid_dir / "api_log.json", "w") as f:
            json.dump(api_log, f)

        # Fake ask returns valid digest and cross-video
        digest_reply = json.dumps({
            "video_id": "video_001",
            "techniques": [{
                "name": "walk_cycle",
                "observed": "character walks",
                "evidence": [{"group_id": "shot_001", "frames": [1, 2], "time": "0.0-1.0"}],
                "camera": "static",
                "character_performance": "walk cycle",
                "effects": "none",
                "required_artwork": "walk preset",
                "capability_class": "V2_REUSE",
                "when_it_works": "walking shots",
                "when_not_to_use": "running shots",
                "confidence": "HIGH"
            }],
            "pacing_notes": "steady",
            "audio_note": "NOT_ANALYZED"
        })
        cross_reply = json.dumps({
            "recipes": [{
                "name": "walk_cycle",
                "stage1_lesson": "Use static camera for walk cycles",
                "stage2_lesson": "Apply V2_REUSE walk preset",
                "required_artwork": "walk preset",
                "capability_class": "V2_REUSE",
                "videos": ["video_001"],
                "evidence": [{"video_id": "video_001", "group_id": "shot_001", "frames": [1, 2]}],
                "counterexample": "Running motion",
                "when_not_to_use": "Running shots",
                "confidence": "HIGH"
            }],
            "gaps": ["Need run cycle"]
        })

        ask = self._make_fake_ask({
            "video_001": digest_reply,
            "PER-VIDEO DIGESTS": cross_reply,
        })

        result = compile_teacher(self.tmpdir, ask, workers=2)

        self.assertEqual(result["stats"]["reports"], 1)
        self.assertEqual(result["stats"]["videos"], 1)
        self.assertEqual(result["stats"]["recipes"], 1)
        self.assertEqual(len(result["failed_videos"]), 0)

        # Check playbook has all 6 sections in order
        md = result["playbook_md"]
        sections = [
            "# Kimi animation teacher",
            "## How to use",
            "## Stage 1: direction lessons",
            "## Stage 2: execution lessons",
            "## Research only",
            "## Sound",
            "## Gaps and uncertainties"
        ]
        for i, section in enumerate(sections):
            self.assertIn(section, md, f"Missing section: {section}")
            if i > 0:
                prev_idx = md.index(sections[i-1])
                curr_idx = md.index(section)
                self.assertLess(prev_idx, curr_idx, f"Section order wrong: {section}")

        # Check techniques dict structure
        tech = result["techniques"]
        self.assertEqual(tech["schema"], 1)
        self.assertEqual(len(tech["recipes"]), 1)
        self.assertIn("classification", tech["recipes"][0])
        self.assertIn("usage_bucket", tech["recipes"][0])

    def test_compile_teacher_retry_on_parse_failure(self):
        vid_dir = Path(self.tmpdir) / "video_001"
        vid_dir.mkdir()
        api_log = {
            "shot_001": {
                "status": "COMPLETE",
                "report": {
                    "video_id": "video_001",
                    "start_time": 0.0,
                    "end_time": 1.0,
                    "evidence_frames": [1],
                    "inferred_technique": "test",
                    "observed_animation": "test",
                    "camera_motion": "static",
                    "character_motion": "idle",
                    "visual_effects": "none",
                    "required_assets": "none",
                    "granthstudio_capability": "V2_REUSE",
                    "confidence": "HIGH",
                }
            }
        }
        with open(vid_dir / "api_log.json", "w") as f:
            json.dump(api_log, f)

        # First call returns garbage, second returns valid
        call_count = {"count": 0}

        def fake_ask(prompt: str) -> str:
            call_count["count"] += 1
            if call_count["count"] == 1:
                return "garbage no json here"
            elif call_count["count"] == 2:
                return json.dumps({
                    "video_id": "video_001",
                    "techniques": [{
                        "name": "test",
                        "observed": "test",
                        "evidence": [{"group_id": "shot_001", "frames": [1], "time": "0.0-1.0"}],
                        "camera": "static",
                        "character_performance": "idle",
                        "effects": "none",
                        "required_artwork": "none",
                        "capability_class": "V2_REUSE",
                        "when_it_works": "test",
                        "when_not_to_use": "test",
                        "confidence": "HIGH"
                    }],
                    "pacing_notes": "",
                    "audio_note": "NOT_ANALYZED"
                })
            else:
                return json.dumps({
                    "recipes": [{
                        "name": "test",
                        "stage1_lesson": "test",
                        "stage2_lesson": "test",
                        "required_artwork": "none",
                        "capability_class": "V2_REUSE",
                        "videos": ["video_001"],
                        "evidence": [{"video_id": "video_001", "group_id": "shot_001", "frames": [1]}],
                        "counterexample": "test",
                        "when_not_to_use": "test",
                        "confidence": "HIGH"
                    }],
                    "gaps": []
                })

        result = compile_teacher(self.tmpdir, fake_ask, workers=1)
        self.assertEqual(len(result["failed_videos"]), 0)
        self.assertEqual(result["stats"]["recipes"], 1)

    def test_compile_teacher_failed_video_after_two_failures(self):
        vid_dir = Path(self.tmpdir) / "video_001"
        vid_dir.mkdir()
        api_log = {
            "shot_001": {
                "status": "COMPLETE",
                "report": {
                    "video_id": "video_001",
                    "start_time": 0.0,
                    "end_time": 1.0,
                    "evidence_frames": [1],
                    "inferred_technique": "test",
                    "observed_animation": "test",
                    "camera_motion": "static",
                    "character_motion": "idle",
                    "visual_effects": "none",
                    "required_assets": "none",
                    "granthstudio_capability": "V2_REUSE",
                    "confidence": "HIGH",
                }
            }
        }
        with open(vid_dir / "api_log.json", "w") as f:
            json.dump(api_log, f)

        def fake_ask(prompt: str) -> str:
            return "garbage"

        result = compile_teacher(self.tmpdir, fake_ask, workers=1)
        self.assertIn("video_001", result["failed_videos"])
        self.assertEqual(result["stats"]["recipes"], 0)

    def test_recipe_without_evidence_dropped(self):
        vid_dir = Path(self.tmpdir) / "video_001"
        vid_dir.mkdir()
        api_log = {
            "shot_001": {
                "status": "COMPLETE",
                "report": {
                    "video_id": "video_001",
                    "start_time": 0.0,
                    "end_time": 1.0,
                    "evidence_frames": [1],
                    "inferred_technique": "test",
                    "observed_animation": "test",
                    "camera_motion": "static",
                    "character_motion": "idle",
                    "visual_effects": "none",
                    "required_assets": "none",
                    "granthstudio_capability": "V2_REUSE",
                    "confidence": "HIGH",
                }
            }
        }
        with open(vid_dir / "api_log.json", "w") as f:
            json.dump(api_log, f)

        digest_reply = json.dumps({
            "video_id": "video_001",
            "techniques": [{
                "name": "test",
                "observed": "test",
                "evidence": [{"group_id": "shot_001", "frames": [1], "time": "0.0-1.0"}],
                "camera": "static",
                "character_performance": "idle",
                "effects": "none",
                "required_artwork": "none",
                "capability_class": "V2_REUSE",
                "when_it_works": "test",
                "when_not_to_use": "test",
                "confidence": "HIGH"
            }],
            "pacing_notes": "",
            "audio_note": "NOT_ANALYZED"
        })
        # Cross-video returns recipe with empty evidence
        cross_reply = json.dumps({
            "recipes": [{
                "name": "test",
                "stage1_lesson": "test",
                "stage2_lesson": "test",
                "required_artwork": "none",
                "capability_class": "V2_REUSE",
                "videos": ["video_001"],
                "evidence": [],  # Empty evidence - should be dropped
                "counterexample": "test",
                "when_not_to_use": "test",
                "confidence": "HIGH"
            }],
            "gaps": []
        })

        ask = self._make_fake_ask({
            "video_001": digest_reply,
            "PER-VIDEO DIGESTS": cross_reply,
        })

        result = compile_teacher(self.tmpdir, ask, workers=1)
        self.assertEqual(result["stats"]["recipes"], 0)  # Dropped

    def test_all_video_references_kept(self):
        # Two videos, same technique
        for vid in ["video_001", "video_002"]:
            vid_dir = Path(self.tmpdir) / vid
            vid_dir.mkdir()
            api_log = {
                "shot_001": {
                    "status": "COMPLETE",
                    "report": {
                        "video_id": vid,
                        "start_time": 0.0,
                        "end_time": 1.0,
                        "evidence_frames": [1],
                        "inferred_technique": "shared_tech",
                        "observed_animation": "shared",
                        "camera_motion": "static",
                        "character_motion": "idle",
                        "visual_effects": "none",
                        "required_assets": "none",
                        "granthstudio_capability": "V2_REUSE",
                        "confidence": "HIGH",
                    }
                }
            }
            with open(vid_dir / "api_log.json", "w") as f:
                json.dump(api_log, f)

        digest_reply = json.dumps({
            "video_id": "video_001",
            "techniques": [{
                "name": "shared_tech",
                "observed": "shared",
                "evidence": [{"group_id": "shot_001", "frames": [1], "time": "0.0-1.0"}],
                "camera": "static",
                "character_performance": "idle",
                "effects": "none",
                "required_artwork": "none",
                "capability_class": "V2_REUSE",
                "when_it_works": "test",
                "when_not_to_use": "test",
                "confidence": "HIGH"
            }],
            "pacing_notes": "",
            "audio_note": "NOT_ANALYZED"
        })
        digest_reply2 = json.dumps({
            "video_id": "video_002",
            "techniques": [{
                "name": "shared_tech",
                "observed": "shared",
                "evidence": [{"group_id": "shot_001", "frames": [2], "time": "0.0-1.0"}],
                "camera": "static",
                "character_performance": "idle",
                "effects": "none",
                "required_artwork": "none",
                "capability_class": "V2_REUSE",
                "when_it_works": "test",
                "when_not_to_use": "test",
                "confidence": "HIGH"
            }],
            "pacing_notes": "",
            "audio_note": "NOT_ANALYZED"
        })
        cross_reply = json.dumps({
            "recipes": [{
                "name": "shared_tech",
                "stage1_lesson": "shared lesson",
                "stage2_lesson": "shared preset",
                "required_artwork": "none",
                "capability_class": "V2_REUSE",
                "videos": ["video_001", "video_002"],
                "evidence": [
                    {"video_id": "video_001", "group_id": "shot_001", "frames": [1]},
                    {"video_id": "video_002", "group_id": "shot_001", "frames": [2]}
                ],
                "counterexample": "test",
                "when_not_to_use": "test",
                "confidence": "HIGH"
            }],
            "gaps": []
        })

        ask = self._make_fake_ask({
            "video_001": digest_reply,
            "video_002": digest_reply2,
            "PER-VIDEO DIGESTS": cross_reply,
        })

        result = compile_teacher(self.tmpdir, ask, workers=2)
        recipe = result["techniques"]["recipes"][0]
        self.assertEqual(set(recipe["videos"]), {"video_001", "video_002"})
        self.assertEqual(len(recipe["evidence"]), 2)


class TestWriteOutputs(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_write_outputs_creates_files(self):
        result = {
            "playbook_md": "# Test Playbook\n\nContent here.",
            "techniques": {"schema": 1, "recipes": [], "gaps": [], "failed_videos": []},
            "failed_videos": [],
            "stats": {"reports": 0, "videos": 0, "recipes": 0}
        }
        write_outputs(self.tmpdir, result)

        playbook_path = Path(self.tmpdir) / "KIMI_ANIMATION_PLAYBOOK.md"
        master_path = Path(self.tmpdir) / "MASTER_TECHNIQUES.json"

        self.assertTrue(playbook_path.exists())
        self.assertTrue(master_path.exists())

        with open(playbook_path, "r") as f:
            self.assertEqual(f.read(), "# Test Playbook\n\nContent here.")

        with open(master_path, "r") as f:
            data = json.load(f)
            self.assertEqual(data["_teacher"]["schema"], 1)

    def test_write_outputs_backup_existing(self):
        # Create existing files
        playbook_path = Path(self.tmpdir) / "KIMI_ANIMATION_PLAYBOOK.md"
        master_path = Path(self.tmpdir) / "MASTER_TECHNIQUES.json"
        playbook_path.write_text("OLD PLAYBOOK")
        master_path.write_text(json.dumps({"existing_key": "value"}))

        result = {
            "playbook_md": "NEW PLAYBOOK",
            "techniques": {"schema": 1, "recipes": [], "gaps": [], "failed_videos": []},
            "failed_videos": [],
            "stats": {"reports": 0, "videos": 0, "recipes": 0}
        }
        write_outputs(self.tmpdir, result)

        # Check backups exist
        self.assertTrue((Path(self.tmpdir) / "KIMI_ANIMATION_PLAYBOOK.md.bak_before_teacher").exists())
        self.assertTrue((Path(self.tmpdir) / "MASTER_TECHNIQUES.json.bak_before_teacher").exists())

        # Check new content
        self.assertEqual(playbook_path.read_text(), "NEW PLAYBOOK")
        with open(master_path, "r") as f:
            data = json.load(f)
            self.assertEqual(data["existing_key"], "value")  # Preserved
            self.assertEqual(data["_teacher"]["schema"], 1)

    def test_write_outputs_corrupt_existing_master_raises(self):
        master_path = Path(self.tmpdir) / "MASTER_TECHNIQUES.json"
        master_path.write_text("{ not valid json }")

        result = {
            "playbook_md": "NEW",
            "techniques": {"schema": 1, "recipes": [], "gaps": [], "failed_videos": []},
            "failed_videos": [],
            "stats": {"reports": 0, "videos": 0, "recipes": 0}
        }
        with self.assertRaises(ValueError) as cm:
            write_outputs(self.tmpdir, result)
        self.assertIn("Corrupt JSON", str(cm.exception))


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_fake_ask(self, responses: Dict[str, str]):
        call_count = {"count": 0}

        def fake_ask(prompt: str) -> str:
            call_count["count"] += 1
            for key, resp in responses.items():
                if key in prompt:
                    return resp
            return '{"video_id": "unknown", "techniques": [], "pacing_notes": "", "audio_note": "NOT_ANALYZED"}'

        return fake_ask

    def test_main_dry_run_no_ask_calls(self):
        # Create test reports
        vid_dir = Path(self.tmpdir) / "video_001"
        vid_dir.mkdir()
        api_log = {
            "shot_001": {"status": "COMPLETE", "report": {"video_id": "video_001"}},
            "shot_002": {"status": "COMPLETE", "report": {"video_id": "video_001"}},
        }
        with open(vid_dir / "api_log.json", "w") as f:
            json.dump(api_log, f)

        # Mock ask to fail if called
        def fail_ask(prompt):
            raise AssertionError("ask should not be called in dry-run")

        # Capture stdout
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            exit_code = main(["--output", self.tmpdir, "--dry-run"], ask=fail_ask)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(exit_code, 0)
        stats = json.loads(output)
        self.assertEqual(stats["reports"], 2)
        self.assertEqual(stats["videos"], 1)
        self.assertEqual(stats["per_video"]["video_001"], 2)

    def test_main_sound_section_states_audio_not_analyzed(self):
        vid_dir = Path(self.tmpdir) / "video_001"
        vid_dir.mkdir()
        api_log = {
            "shot_001": {
                "status": "COMPLETE",
                "report": {
                    "video_id": "video_001",
                    "start_time": 0.0,
                    "end_time": 1.0,
                    "evidence_frames": [1],
                    "inferred_technique": "test",
                    "observed_animation": "test",
                    "camera_motion": "static",
                    "character_motion": "idle",
                    "visual_effects": "none",
                    "required_assets": "none",
                    "granthstudio_capability": "V2_REUSE",
                    "confidence": "HIGH",
                }
            }
        }
        with open(vid_dir / "api_log.json", "w") as f:
            json.dump(api_log, f)

        digest_reply = json.dumps({
            "video_id": "video_001",
            "techniques": [{
                "name": "test",
                "observed": "test",
                "evidence": [{"group_id": "shot_001", "frames": [1], "time": "0.0-1.0"}],
                "camera": "static",
                "character_performance": "idle",
                "effects": "none",
                "required_artwork": "none",
                "capability_class": "V2_REUSE",
                "when_it_works": "test",
                "when_not_to_use": "test",
                "confidence": "HIGH"
            }],
            "pacing_notes": "",
            "audio_note": "NOT_ANALYZED"
        })
        cross_reply = json.dumps({
            "recipes": [{
                "name": "test",
                "stage1_lesson": "test",
                "stage2_lesson": "test",
                "required_artwork": "none",
                "capability_class": "V2_REUSE",
                "videos": ["video_001"],
                "evidence": [{"video_id": "video_001", "group_id": "shot_001", "frames": [1]}],
                "counterexample": "test",
                "when_not_to_use": "test",
                "confidence": "HIGH"
            }],
            "gaps": []
        })

        ask = self._make_fake_ask({
            "video_001": digest_reply,
            "PER-VIDEO DIGESTS": cross_reply,
        })

        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            exit_code = main(["--output", self.tmpdir], ask=ask)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        # Check playbook was written with correct sound section
        playbook_path = Path(self.tmpdir) / "KIMI_ANIMATION_PLAYBOOK.md"
        content = playbook_path.read_text()
        self.assertIn("Audio was only checked for silence", content)
        self.assertIn("narration, SFX and music are NOT analyzed", content)
        self.assertIn("no sound lesson is claimed", content)


if __name__ == "__main__":
    unittest.main()
