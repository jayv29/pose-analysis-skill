# PoseAnalysis

Current version: `3.0.0`

PoseAnalysis is a Codex skill for coach-grade Chinese sports technique analysis from local training videos.

Current product scope:

- Input: iPhone videos saved to iCloud Drive `PoseAnalysis/Inbox`.
- Sports: foil fencing, top-rope/lead climbing, and basic youth fitness.
- Output: video-quality gate, technical scoring when valid, training advice, next tracking metrics, and same-template history comparison.
- Privacy: child identity is anonymized by default.

This repository is the Codex upgrade of the previous OpenClaw `pose-analysis-skill` project. It keeps deterministic local MediaPipe pose extraction, and moves the expert reasoning layer into Codex skill references and current-session analysis.

Start with:

- `docs/product/PRODUCT_REQUIREMENTS.md`
- `docs/skill-design/POSE_ANALYSIS_SKILL_REDESIGN.md`
- `pose-analysis/SKILL.md`
- `pose-analysis/references/input-spec.md`
- `pose-analysis/references/video-quality-gate.md`
- `pose-analysis/references/report-templates.md`
- `pose-analysis/references/knowledge-base/README.md`

Installed Codex skill copy:

`~/.codex/skills/pose-analysis`

iCloud Inbox:

`~/Library/Mobile Documents/com~apple~CloudDocs/PoseAnalysis/Inbox`

iCloud Report:

`~/Library/Mobile Documents/com~apple~CloudDocs/PoseAnalysis/Report`

## Usage

Analyze the newest Inbox video:

```bash
bash pose-analysis/scripts/run_skill.sh --latest
```

Analyze a specific video:

```bash
POSE_ANALYSIS_SPORT=花剑 \
POSE_ANALYSIS_TEMPLATE=弓步冲刺专项 \
bash pose-analysis/scripts/run_skill.sh "/path/to/video.mov"
```

The runner writes generated pose JSON, report skeletons, and history indexes to the report folder. Final coach-grade reports should be produced by Codex from the generated artifacts and the bundled knowledge base.

## Validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
PYTHONPYCACHEPREFIX=/tmp/pose-analysis-pycache python3 -m py_compile \
  pose-analysis/scripts/pose_analyzer.py \
  pose-analysis/scripts/report_formatter.py \
  pose-analysis/scripts/analyze_pose.py
bash -n pose-analysis/scripts/run_skill.sh
bash -n pose-analysis/scripts/download_pose_model.sh
```
