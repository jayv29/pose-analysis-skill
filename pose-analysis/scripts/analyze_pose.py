#!/usr/bin/env python3
"""
Pose Analysis Helper

兼容旧入口：不再在 skill 内直连固定大模型 API。
这个脚本现在只负责调用本地姿态提取，并输出结构化 JSON。
真正的专业分析应由当前 Codex 会话基于 JSON 和报告完成。
"""

import json
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent
POSE_ANALYZER = SKILL_DIR / "pose_analyzer.py"


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python analyze_with_ai.py <视频路径>", file=sys.stderr)
        return 1

    video_path = sys.argv[1]

    proc = subprocess.run(
        [sys.executable, str(POSE_ANALYZER), video_path],
        capture_output=True,
        text=True,
    )

    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")

    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end="")
        return proc.returncode

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print(json.dumps({
            "status": "error",
            "error": "pose_analyzer 输出不是有效 JSON",
            "raw_stdout": proc.stdout,
        }, ensure_ascii=False))
        return 1

    result = {
        "status": "pose_only",
        "video_path": video_path,
        "message": "姿态数据提取完成。请让当前 Codex 会话基于该 JSON 生成最终专业报告。",
        "pose_data": payload,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
