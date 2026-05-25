# Pose Analysis Guide

This is the concise navigation guide. Load the detailed references before producing a final report.

## Required Sequence

1. Identify video, sport, and action template.
2. Read `input-spec.md` when the input source or filename is unclear.
3. Run or inspect pose extraction outputs.
4. Read `video-quality-gate.md` and decide `可评分`, `部分可评分`, or `不可评分`.
5. If `不可评分`, stop technical scoring and provide reshooting advice.
6. If scoring is allowed, read `report-templates.md`, `history-comparison.md`, `privacy.md`, and the relevant knowledge-base file.

## Supported Sport Files

- Foil fencing: `knowledge-base/foil.md`
- Top-rope/lead climbing: `knowledge-base/climbing.md`
- Youth fitness: `knowledge-base/fitness.md`

## Evidence Rules

- Use numeric evidence from pose JSON when available.
- Cite specific angles, averages, ranges, key-frame timestamps, or visible events.
- Mark missing or unreliable dimensions as `证据不足`.
- Do not infer exact 3D distance, foot pressure, true velocity, or tactical intent from a single poor-angle video.

## Report Rules

- Output Chinese only.
- Default to coach-grade professional wording.
- Use anonymized child identity.
- Give a 100-point score only when the quality gate is `可评分`.
- For `部分可评分`, score only reliable dimensions or provide qualitative ratings.
- For `不可评分`, output no technical score.

## Medical Boundary

Do not diagnose medical conditions or prescribe rehabilitation. If a movement looks concerning, recommend coach review or professional assessment without naming a diagnosis.
