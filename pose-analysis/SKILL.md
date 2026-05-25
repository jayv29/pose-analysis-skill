---
name: pose-analysis
description: Use when a user asks Codex to analyze sports, training, posture, or movement videos; extract MediaPipe pose landmarks; judge whether a video is suitable for technical scoring; or produce Chinese coach-grade reports for foil fencing, top-rope/lead climbing, or youth fitness videos.
---

# Pose Analysis

## Overview

This skill analyzes local training videos as a Codex skill. It runs local MediaPipe pose extraction when needed, judges video quality before scoring, and uses project references to produce Chinese coach-grade reports.

Primary supported scenarios:

- Foil fencing: lunge sprint drills, one-on-one lesson clips, and bout clips.
- Climbing: top-rope/lead continuous climbing, single crux moves, footwork and center-of-mass control.
- Youth fitness: squat, split squat/lunge, push-up, plank/hollow hold, jump landing, and single-leg balance.

Default reader is the coach. The parent is secondary. Reports must be Chinese, professional, evidence-based, and anonymized for a child athlete.

## Workflow

1. Resolve the video path. The default inbox is:

```text
~/Library/Mobile Documents/com~apple~CloudDocs/PoseAnalysis/Inbox
```

2. Confirm the sport and action template from the filename or user instruction. Do not auto-guess when the user has not provided enough context.
3. Read `references/input-spec.md` for accepted naming and instruction patterns.
4. If the MediaPipe model is missing, run `scripts/download_pose_model.sh` or download `pose_landmarker.task` to `/tmp/pose_landmarker.task`.
5. Run with an explicit path or the newest video from the Inbox:

```bash
bash scripts/run_skill.sh /path/to/video.mp4
bash scripts/run_skill.sh --latest
```

6. Read the generated JSON and Markdown paths printed by the command.
7. Before scoring, read `references/video-quality-gate.md` and decide:
   - `可评分`
   - `部分可评分`
   - `不可评分`
8. If the video is `不可评分`, do not produce technical scores. Output only the quality failure reasons and reshooting advice.
9. If scoring is allowed, read `references/report-templates.md`, `references/history-comparison.md`, and the sport-specific knowledge-base file:
   - `references/knowledge-base/foil.md`
   - `references/knowledge-base/foil-advanced.md`
   - `references/knowledge-base/climbing.md`
   - `references/knowledge-base/climbing-advanced.md`
   - `references/knowledge-base/fitness.md`
   - `references/knowledge-base/fitness-advanced.md`
   - `references/knowledge-base/professional-analysis-standard.md`
   - `references/phase-recognition.md`
   - `references/final-report-quality.md`
10. Use the Markdown report plus JSON metrics to produce the final coaching report in Chinese.

## Configuration

- Python defaults to `~/.venv-pose/bin/python`, then falls back to `python3`.
- Override Python with `POSE_ANALYSIS_PYTHON=/path/to/python`.
- Override the MediaPipe model path with `POSE_LANDMARKER_MODEL=/path/to/pose_landmarker.task`.
- Override the Inbox with `POSE_ANALYSIS_INBOX_DIR=/path/to/inbox`.
- Override output location with `POSE_ANALYSIS_OUTPUT_DIR=/path/to/report`.
- Default output location is `~/Library/Mobile Documents/com~apple~CloudDocs/PoseAnalysis/Report`.
- Default Inbox is `~/Library/Mobile Documents/com~apple~CloudDocs/PoseAnalysis/Inbox`.
- Optionally set `POSE_ANALYSIS_SPORT`, `POSE_ANALYSIS_TEMPLATE`, and `POSE_ANALYSIS_ATHLETE_ID` to avoid relying on filename parsing.

## References

- Input workflow: `references/input-spec.md`
- Video quality gate: `references/video-quality-gate.md`
- Report templates: `references/report-templates.md`
- Final report quality: `references/final-report-quality.md`
- Action phase recognition: `references/phase-recognition.md`
- History comparison: `references/history-comparison.md`
- Child privacy: `references/privacy.md`
- Knowledge-base index: `references/knowledge-base/README.md`
- Professional analysis standard: `references/knowledge-base/professional-analysis-standard.md`
- Advanced foil rubric: `references/knowledge-base/foil-advanced.md`
- Advanced climbing rubric: `references/knowledge-base/climbing-advanced.md`
- Advanced youth fitness rubric: `references/knowledge-base/fitness-advanced.md`
- Legacy concise guide: `references/analysis-guide.md`

## Output

The runner writes:

- `*.pose.YYYYMMDD.json`: structured pose metrics, summaries, key frames, and sampled frames.
- `*.md`: a local report skeleton with calculated values and coaching prompts.
- `history_index.json`: same-athlete, same-sport, same-template history index used for later comparison.

Final reports must include video-quality assessment, confidence, evidence, technical scoring only when valid, training advice, next tracking metrics, same-template history comparison, and privacy-safe wording.

Do not call OpenClaw or an `analysis-expert` agent. This is the Codex version: Codex should inspect the generated artifacts directly and complete the expert analysis in the current conversation.
