# pose-analysis-skill

用 MediaPipe + AI 分析训练视频姿态，生成专业改进建议。

## 功能

- 🎥 **视频姿态检测** - 用 MediaPipe 提取人体 33 个关键点
- 🤖 **AI 智能分析** - 调用 MiniMax M2.1/Gemini 分析动作质量
- 📊 **专业报告** - 生成包含评分、问题分析、改进建议的完整报告
- 💰 **低成本运行** - 本地运行 MediaPipe，仅消耗少量 AI tokens

## 安装

```bash
# 1. 创建虚拟环境
python3 -m venv ~/.venv-pose
source ~/.venv-pose/bin/activate

# 2. 安装依赖
pip install mediapipe opencv-python google-generativeai

# 3. 下载 MediaPipe 模型
curl -L -o /tmp/pose_landmarker.task \
  "https://storage.googleapis.com/mediapipe-assets/pose_landmarker.task"

# 4. 复制 skill 到 OpenClaw
mkdir -p ~/.openclaw/workspace/skills/pose-analysis
cp pose_analyzer.py ~/.openclaw/workspace/skills/pose-analysis/
cp README.md ~/.openclaw/workspace/skills/pose-analysis/
```

## 使用

### 命令行

```bash
source ~/.venv-pose/bin/activate
python3 pose_analyzer.py /path/to/your/video.mp4
```

### OpenClaw 自然语言

直接告诉 Jarvis：
```
"用姿态分析 skill 分析 /path/to/your/训练视频.mp4"
```

## 输出示例

```json
{
  "action": "弓步冲刺",
  "score": "6.5/10",
  "issues": [
    "髋部高度不足",
    "前腿膝关节过度前探",
    "头部稳定性待提升"
  ],
  "suggestions": [
    "加强髋部下降训练",
    "优化膝关节角度控制",
    "核心稳定性练习"
  ]
}
```

## 依赖

- Python 3.11+
- mediapipe
- opencv-python
- google-generativeai（或 MiniMax API）

## 技术栈

| 组件 | 用途 |
|------|------|
| MediaPipe | 姿态估计（本地运行） |
| MiniMax M2.1 / Gemini 2.5 Pro | AI 分析 |
| OpenClaw Skill | 自然语言调用 |

## 目录结构

```
pose-analysis/
├── README.md           # 此文件
├── pose_analyzer.py     # 主脚本
├── requirements.txt     # Python 依赖
└── test.sh            # 测试脚本
```

## License

MIT

## 作者

OpenClaw Community
