# Professional Reference Sources

PoseAnalysis uses these sources to shape its rubrics, confidence rules, report language, and safety boundaries. They are references, not official endorsement by any federation or publisher.

## Computer Vision And Pose Estimation

| Source | Why it matters |
| --- | --- |
| [Google AI Edge MediaPipe Pose Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker) | Defines the landmark task used by the local extraction script, including video input, normalized coordinates, world coordinates, confidence thresholds, and 33 landmark output. |
| [BlazePose: On-device Real-time Body Pose Tracking](https://arxiv.org/abs/2006.10204) | Describes the 33-keypoint real-time pose-tracking approach behind MediaPipe-style fitness and movement applications. |
| [A comprehensive analysis of machine-learning pose-estimation models used in human movement and posture analyses](https://doi.org/10.1016/j.heliyon.2024.e39977) | Supports the project's conservative stance on single-camera pose estimation, occlusion, posture analysis limits, and confidence labeling. |

## Foil Fencing

| Source | Why it matters |
| --- | --- |
| [FIE Rules](https://fie.org/fie/documents/rules) | Official competition-rule context for foil conventions, offensive actions, piste constraints, equipment responsibilities, and terminology. |
| [FIE Technical Rules](https://static.fie.org/uploads/38/190673-technical%20rules%20ang.pdf) | Detailed technical rulebook used as a terminology anchor for fencing actions and competition boundaries. |

## Climbing

| Source | Why it matters |
| --- | --- |
| [World Climbing Competition Resources](https://www.worldclimbing.com/resources/competitions) | Official rules, event regulations, ranking resources, equipment code, and safeguarding resources for competition climbing. |
| [World Climbing Competition Rules](https://images.ifsc-climbing.org/ifsc/image/private/t_q_good/prd/jaq7awz9jmqwpddwnbpr.pdf) | Competition rules reference for lead, boulder, and speed contexts. PoseAnalysis currently uses this for domain language and route-context constraints, not official judging. |

## Youth Fitness And Long-Term Development

| Source | Why it matters |
| --- | --- |
| [NSCA Youth Resistance Training Position Statement](https://doi.org/10.1519/JSC.0b013e31819df407) | Supports conservative youth-strength recommendations: supervision, technique first, age-appropriate load, and long-term development. |
| [WHO Guidelines on Physical Activity and Sedentary Behaviour](https://www.who.int/publications/b/55518) | Establishes broad public-health context for children and adolescents, while PoseAnalysis stays focused on technique rather than medical claims. |

## How Sources Are Used

- Federation rules shape terminology and event context.
- Sport-science and coaching references shape rubrics and training suggestions.
- Pose-estimation references define what can and cannot be inferred from a single video.
- When video evidence is weak, the report must downgrade confidence instead of filling gaps from ideal technique models.
