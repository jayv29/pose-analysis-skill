import importlib.util
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_FORMATTER_PATH = PROJECT_ROOT / "pose-analysis" / "scripts" / "report_formatter.py"


def load_report_formatter():
    spec = importlib.util.spec_from_file_location("report_formatter", REPORT_FORMATTER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def patched_env(**updates):
    original = {key: os.environ.get(key) for key in updates}
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class ReportFormatterTests(unittest.TestCase):
    def setUp(self):
        self.report_formatter = load_report_formatter()

    def test_build_output_paths_avoids_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_root = Path(tmp_dir)
            video_path = output_root / "clip.mov"
            video_path.write_text("not a real video", encoding="utf-8")

            first_report, first_json = self.report_formatter.build_output_paths(
                video_path,
                "unknown",
                output_root,
            )
            first_report.write_text("existing report", encoding="utf-8")
            first_json.write_text("{}", encoding="utf-8")

            next_report, next_json = self.report_formatter.build_output_paths(
                video_path,
                "unknown",
                output_root,
            )

            self.assertNotEqual(first_report, next_report)
            self.assertNotEqual(first_json, next_json)
            self.assertFalse(next_report.exists())
            self.assertFalse(next_json.exists())

    def test_missing_metrics_render_as_na_not_zero(self):
        pose_data = {
            "summary": {"total_frames": 1, "duration_sec": 0.1},
            "key_frames": {"lowest_center_of_gravity": None},
            "sampled_frames": [{"frame": 0, "timestamp": 0.0, "metrics": {}}],
        }

        markdown = self.report_formatter.build_markdown(Path("unknown.mov"), pose_data)

        self.assertIn("N/A", markdown)
        self.assertNotIn("0°（范围 0° ~ 0°）", markdown)

    def test_default_output_root_is_icloud_report(self):
        with patched_env(POSE_ANALYSIS_OUTPUT_DIR=None):
            output_root = self.report_formatter.get_output_root()

        self.assertEqual(
            output_root,
            Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "PoseAnalysis" / "Report",
        )

    def test_resolve_analysis_context_prefers_environment(self):
        with patched_env(
            POSE_ANALYSIS_SPORT="花剑",
            POSE_ANALYSIS_TEMPLATE="弓步冲刺专项",
            POSE_ANALYSIS_ATHLETE_ID="athlete-test",
        ):
            context = self.report_formatter.resolve_analysis_context(Path("random.mov"), {})

        self.assertEqual(context["sport"], "fencing")
        self.assertEqual(context["template"], "lunge_sprint")
        self.assertEqual(context["athlete_id"], "athlete-test")

    def test_resolve_analysis_context_from_filename(self):
        context = self.report_formatter.resolve_analysis_context(
            Path("2026-05-25_攀岩_lead_连续上攀_A01.mov"),
            {},
        )

        self.assertEqual(context["sport"], "climbing")
        self.assertEqual(context["template"], "lead_continuous_climb")

    def test_quality_gate_rejects_empty_pose_data(self):
        gate = self.report_formatter.evaluate_quality_gate(
            {"summary": {"total_frames": 0}, "sampled_frames": []},
            {"sport": "fencing", "template": "lunge_sprint"},
        )

        self.assertEqual(gate["conclusion"], "不可评分")
        self.assertTrue(gate["reasons"])

    def test_quality_gate_accepts_good_pose_data(self):
        frames = [
            {
                "frame": index * 5,
                "timestamp": index / 6,
                "metrics": {
                    "knee_angle_left": 112.0,
                    "knee_angle_right": 168.0,
                    "hip_height": 0.52,
                },
                "quality": {
                    "core_visibility": 0.9,
                    "lower_body_visibility": 0.88,
                    "upper_body_visibility": 0.91,
                    "body_bbox_height": 0.55,
                    "out_of_frame_keypoints": 0,
                },
            }
            for index in range(30)
        ]
        pose_data = {
            "summary": {
                "total_frames": len(frames),
                "duration_sec": 5.0,
                "quality": {
                    "sample_attempts": 30,
                    "detected_pose_frames": 30,
                    "detection_rate": 1.0,
                    "avg_core_visibility": 0.9,
                    "avg_lower_body_visibility": 0.88,
                    "avg_body_bbox_height": 0.55,
                },
            },
            "sampled_frames": frames,
        }

        gate = self.report_formatter.evaluate_quality_gate(
            pose_data,
            {"sport": "fencing", "template": "lunge_sprint"},
        )

        self.assertEqual(gate["conclusion"], "可评分")
        self.assertEqual(gate["confidence"], "高")

    def test_unscorable_report_suppresses_technical_score(self):
        pose_data = {
            "summary": {"total_frames": 0, "duration_sec": 0, "quality": {"detection_rate": 0.0}},
            "key_frames": {"lowest_center_of_gravity": None},
            "sampled_frames": [],
        }

        markdown = self.report_formatter.build_markdown(
            Path("2026-05-25_花剑_弓步冲刺专项_A01.mov"),
            pose_data,
        )

        self.assertIn("结论：不可评分", markdown)
        self.assertIn("重新拍摄建议", markdown)
        self.assertNotIn("综合评分：", markdown)

    def test_update_history_index_groups_by_template(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            history_path = Path(tmp_dir) / "history_index.json"
            context = {
                "athlete_id": "athlete-a",
                "sport": "fencing",
                "template": "lunge_sprint",
                "sport_label": "花剑",
                "template_label": "弓步冲刺专项",
            }
            entry = {"date": "2026-05-25", "quality_conclusion": "可评分"}

            history = self.report_formatter.update_history_index(history_path, context, entry)

        self.assertIn("athlete-a|fencing|lunge_sprint", history)
        self.assertEqual(len(history["athlete-a|fencing|lunge_sprint"]), 1)

    def test_absolute_without_resolving_symlink_preserves_filename(self):
        path = self.report_formatter.absolute_without_resolving_symlink(
            Path("/tmp/2026-05-25_花剑_弓步冲刺专项_A01.MOV")
        )

        self.assertEqual(path.name, "2026-05-25_花剑_弓步冲刺专项_A01.MOV")


if __name__ == "__main__":
    unittest.main()
