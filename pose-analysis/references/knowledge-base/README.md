# 运动知识库使用说明

## 目标

本知识库用于约束 PoseAnalysis 的专业判断。报告必须把视频证据、姿态数据和专项知识结合起来，而不是自由发挥。

## 来源分级

优先级从高到低：

1. 官方协会、国家/地区教练体系、规则或教学资料。
2. 同行评审运动科学、运动生物力学和训练研究。
3. 受认可的教练教育、训练机构和专业课程资料。
4. 用户、教练和本项目历史报告中形成的本地经验。

## 使用规则

- 先读 `video-quality-gate.md`，判断是否可评分。
- 再读 `professional-analysis-standard.md`，确认证据等级、置信度和单机位分析边界。
- 按项目读取基础知识库和高级 rubric。
- 完成最终报告前读取 `final-report-quality.md` 和 `phase-recognition.md`。
- 如果视频证据不足，不能把知识库中的理想技术动作直接套到孩子身上。
- 对儿童训练建议必须保守，优先动作质量、长期发展和可持续训练。
- 专项建议必须能被教练在下一次训练中观察或复测。

## 当前知识库文件

- `foil.md`：花剑，包括弓步冲刺、教练课片段和实战片段。
- `foil-advanced.md`：花剑 100 分 rubric、阶段诊断、错误分型、训练处方和历史指标。
- `climbing.md`：top rope/lead 攀岩，包括连续上攀、单个难点和脚法重心。
- `climbing-advanced.md`：攀岩 100 分 rubric、lead clipping、脚法/重心分型和历史指标。
- `fitness.md`：儿童基础体能，包括深蹲、弓步、俯卧撑、核心、跳跃落地和单腿稳定。
- `fitness-advanced.md`：儿童基础体能 100 分 rubric、红黄绿分级、训练处方和历史指标。
- `professional-analysis-standard.md`：证据等级、置信度、单机位分析边界和评分原则。

相关通用文件：

- `../phase-recognition.md`：三项目动作阶段识别。
- `../final-report-quality.md`：最终报告质量标准。
- `../history-comparison.md`：历史对比准确性规则。

## 来源记录

详细来源记录见 [`../../../docs/references/professional-sources.md`](../../../docs/references/professional-sources.md)。

初始知识库参考了以下来源类型：

- MediaPipe Pose Landmarker 官方文档和 BlazePose 论文：用于理解身体关键点、视频输入和 landmark 输出边界。
- FIE 官方规则和技术规则：用于花剑攻击、弓步、剑手威胁逻辑和比赛语境。
- World Climbing / IFSC 竞赛资源：用于 lead/top-rope 项目语境、规则和术语边界。
- 姿态估计与人体动作分析综述：用于单机位、遮挡、置信度和视频证据限制。
- NSCA 青少年抗阻训练立场声明和 WHO 体力活动指南：用于儿童基础体能训练的长期发展、监督、动作质量和训练负荷边界。

## 维护规则

新增知识点时必须写入：

- 来源链接或书目信息
- 适用项目
- 可观察证据
- 不适用场景
- 是否适合 10 岁儿童
