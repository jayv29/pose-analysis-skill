#!/usr/bin/env python3
"""
Pose Analysis Report Formatter

This script turns pose_analyzer.py JSON into local report artifacts:
1. pose JSON copied into the configured report folder
2. a Chinese coach-grade Markdown report skeleton
3. a lightweight same-template history index

It does not call an external model. The final expert narrative is completed by
the current Codex session using the generated JSON, report skeleton, and skill
knowledge base.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any


ICLOUD_POSE_ANALYSIS_ROOT = (
    Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "PoseAnalysis"
)
DEFAULT_INBOX_ROOT = ICLOUD_POSE_ANALYSIS_ROOT / "Inbox"
DEFAULT_OUTPUT_ROOT = ICLOUD_POSE_ANALYSIS_ROOT / "Report"
HISTORY_FILENAME = "history_index.json"
CODEX_MODEL_LABEL = "Codex 当前模型（本地模板预生成）"

SPORT_KEYWORDS = {
    "fencing": ["花剑", "击剑", "foil", "fencing"],
    "climbing": ["攀岩", "climbing", "top-rope", "top rope", "lead", "先锋", "顶绳"],
    "fitness": ["体能", "基础体能", "深蹲", "俯卧撑", "fitness", "squat", "push-up", "pushup"],
}

SPORT_ALIASES = {
    "花剑": "fencing",
    "击剑": "fencing",
    "foil": "fencing",
    "fencing": "fencing",
    "攀岩": "climbing",
    "climbing": "climbing",
    "top-rope": "climbing",
    "top rope": "climbing",
    "lead": "climbing",
    "先锋": "climbing",
    "顶绳": "climbing",
    "体能": "fitness",
    "基础体能": "fitness",
    "fitness": "fitness",
    "squat": "fitness",
}

SPORT_META = {
    "fencing": {
        "label": "花剑",
        "title": "花剑技术分析报告",
        "expert": "花剑专项教练",
        "filename": "花剑技术分析报告_{date}.md",
    },
    "fitness": {
        "label": "基础体能",
        "title": "基础体能技术分析报告",
        "expert": "儿童基础体能教练",
        "filename": "基础体能分析报告_{date}.md",
    },
    "climbing": {
        "label": "攀岩",
        "title": "攀岩技术分析报告",
        "expert": "攀岩技术分析教练",
        "filename": "攀岩技术分析报告_{date}.md",
    },
    "unknown": {
        "label": "未指定项目",
        "title": "动作姿态分析报告",
        "expert": "运动技术分析师",
        "filename": "动作姿态分析报告_{date}.md",
    },
}

TEMPLATE_SPECS = {
    "fencing": {
        "lunge_sprint": {
            "label": "弓步冲刺专项",
            "aliases": ["弓步冲刺", "弓步", "lunge", "lunge sprint", "lunge_sprint"],
            "dimensions": [
                ("准备姿势与重心预备", 15),
                ("启动顺序与节奏", 15),
                ("后腿蹬伸与推进效率", 20),
                ("前脚落地与前膝控制", 20),
                ("躯干、髋部和头部稳定", 15),
                ("持剑臂协调与完成姿势", 10),
                ("回收与再准备", 5),
            ],
            "tracking": ["启动到落地时长", "前膝落地角度", "后腿蹬伸完成度", "躯干前倾", "回收时间"],
            "reshoot": "横屏固定机位，从侧面垂直于弓步前进方向拍摄，保留启动前和结束后各 1-2 秒。",
        },
        "lesson": {
            "label": "一对一教练课片段",
            "aliases": ["一对一", "教练课", "lesson"],
            "dimensions": [
                ("距离控制", 20),
                ("节奏响应", 20),
                ("技术动作完成度", 25),
                ("持剑线与身体协调", 15),
                ("教练指令执行稳定性", 10),
                ("回合间调整能力", 10),
            ],
            "tracking": ["指令响应时机", "距离调整质量", "动作完成稳定性", "回合间恢复姿势"],
            "reshoot": "固定机位拍到孩子、教练和双方距离变化，避免教练长期遮挡孩子关键动作。",
        },
        "bout": {
            "label": "实战比赛片段",
            "aliases": ["实战", "比赛", "bout", "match"],
            "dimensions": [
                ("距离判断", 25),
                ("启动时机", 20),
                ("技术选择", 20),
                ("脚步与剑手协调", 15),
                ("防守后转换", 10),
                ("节奏稳定性", 10),
            ],
            "tracking": ["得失分前距离", "启动时机", "准备动作质量", "攻防转换速度"],
            "reshoot": "横屏固定机位拍到双方和交锋线，明确要分析的运动员。",
        },
    },
    "climbing": {
        "top_rope_continuous_climb": {
            "label": "top-rope-连续上攀",
            "aliases": ["top-rope", "top rope", "top_rope", "顶绳", "连续上攀"],
            "dimensions": [
                ("脚法准确性与踩点稳定", 20),
                ("髋部和重心控制", 20),
                ("手臂使用效率", 20),
                ("动作顺序与路线阅读", 20),
                ("节奏和停顿管理", 10),
                ("身体张力与摆动控制", 10),
            ],
            "tracking": ["脚点一次成功率", "高屈肘停留时间", "停顿位置", "髋部移动是否先行"],
            "reshoot": "拍到全身、手点、脚点和当前路线区域，镜头稳定，少跟拍。",
        },
        "lead_continuous_climb": {
            "label": "lead-连续上攀",
            "aliases": ["lead", "先锋", "连续上攀"],
            "dimensions": [
                ("脚法准确性与踩点稳定", 20),
                ("髋部和重心控制", 20),
                ("手臂使用效率", 15),
                ("动作顺序与路线阅读", 15),
                ("节奏和停顿管理", 10),
                ("身体张力与摆动控制", 10),
                ("lead clipping 管理", 10),
            ],
            "tracking": ["clip 前站位", "clip 后恢复节奏", "脚点稳定性", "高耗能停顿次数"],
            "reshoot": "如果要分析 clipping，必须拍到绳、快挂、手部和 clip 前后身体位置。",
        },
        "crux_move": {
            "label": "单个难点动作",
            "aliases": ["难点", "crux", "单个"],
            "dimensions": [
                ("起始站位和重心准备", 20),
                ("发力方向", 20),
                ("手脚顺序", 20),
                ("髋部旋转/贴墙策略", 15),
                ("完成后的稳定", 15),
                ("尝试间调整", 10),
            ],
            "tracking": ["起始站位", "髋部先行", "完成后稳定时间", "尝试间调整"],
            "reshoot": "保留难点动作前后至少各 2 秒，并拍到相关手点、脚点和髋部。",
        },
        "footwork_center_of_mass": {
            "label": "脚法与重心控制",
            "aliases": ["脚法", "重心", "center", "mass"],
            "dimensions": [
                ("脚点准确性", 25),
                ("换脚稳定性", 20),
                ("髋部随脚点移动", 20),
                ("手臂放松与承重分配", 15),
                ("身体摆动控制", 20),
            ],
            "tracking": ["脚点一次到位", "换脚晃动", "髋部靠近支撑脚", "手臂屈肘时间"],
            "reshoot": "机位要能看清脚点和髋部，不要只拍上半身或背部近景。",
        },
    },
    "fitness": {
        "squat": {
            "label": "深蹲",
            "aliases": ["深蹲", "squat"],
            "dimensions": [
                ("动作范围", 15),
                ("关节轨迹", 20),
                ("躯干和骨盆控制", 20),
                ("左右对称", 15),
                ("节奏与离心控制", 15),
                ("稳定性和重复一致性", 15),
            ],
            "tracking": ["深度", "膝轨迹", "躯干角度", "左右偏移", "底部稳定"],
            "reshoot": "侧面固定机位拍 3-5 次；如重点看膝内扣，补充正面。",
        },
        "split_squat_lunge": {
            "label": "弓步/分腿蹲",
            "aliases": ["分腿蹲", "体能弓步", "split squat", "lunge"],
            "dimensions": [
                ("前膝控制", 20),
                ("髋稳定", 20),
                ("后脚支撑", 15),
                ("下沉和起身控制", 20),
                ("左右差异", 25),
            ],
            "tracking": ["前膝轨迹", "骨盆水平", "左右差异", "起身稳定"],
            "reshoot": "侧面和正面都重要，至少每侧 3 次。",
        },
        "push_up": {
            "label": "俯卧撑",
            "aliases": ["俯卧撑", "push-up", "pushup"],
            "dimensions": [
                ("肩肘路径", 20),
                ("躯干直线", 25),
                ("骨盆控制", 20),
                ("动作幅度", 20),
                ("左右对称", 15),
            ],
            "tracking": ["躯干塌陷", "肘角", "肩胛稳定", "动作幅度"],
            "reshoot": "侧面固定机位拍完整身体，保留 3-5 次。",
        },
        "plank_hollow": {
            "label": "平板支撑/hollow hold",
            "aliases": ["平板", "hollow", "plank"],
            "dimensions": [
                ("肋骨-骨盆位置", 30),
                ("腰椎代偿控制", 25),
                ("肩部稳定", 20),
                ("呼吸和持续性", 10),
                ("疲劳后姿势保持", 15),
            ],
            "tracking": ["骨盆下沉", "肋骨外翻", "肩部耸起", "保持时间"],
            "reshoot": "侧面固定机位拍完整身体，避免从头脚方向拍摄。",
        },
        "jump_landing": {
            "label": "跳跃落地",
            "aliases": ["跳跃", "落地", "jump", "landing"],
            "dimensions": [
                ("落地缓冲", 25),
                ("膝踝对齐", 25),
                ("左右受力", 20),
                ("躯干控制", 15),
                ("二次弹跳控制", 15),
            ],
            "tracking": ["膝内扣", "落地静音", "髋膝踝缓冲", "左右脚同步"],
            "reshoot": "正面看膝踝对齐，侧面看髋膝缓冲；保留起跳和落地后 2 秒。",
        },
        "single_leg_control": {
            "label": "单腿平衡/单腿下蹲准备",
            "aliases": ["单腿", "平衡", "single leg"],
            "dimensions": [
                ("骨盆水平", 25),
                ("膝轨迹", 25),
                ("足踝控制", 20),
                ("躯干补偿", 15),
                ("保持稳定时间", 15),
            ],
            "tracking": ["骨盆水平", "膝轨迹", "足踝晃动", "稳定 3-5 秒"],
            "reshoot": "正面和侧面都重要；如果只拍一个角度，需要降低未覆盖维度的置信度。",
        },
    },
    "unknown": {},
}


def get_output_root() -> Path:
    override = os.environ.get("POSE_ANALYSIS_OUTPUT_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_OUTPUT_ROOT


def get_inbox_root() -> Path:
    override = os.environ.get("POSE_ANALYSIS_INBOX_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_INBOX_ROOT


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def absolute_without_resolving_symlink(path: Path) -> Path:
    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded
    return Path.cwd() / expanded


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def collect_metric_values(frames: list[dict], metric_key: str) -> list[float]:
    values = []
    for frame in frames:
        value = frame.get("metrics", {}).get(metric_key)
        if is_number(value):
            values.append(value)
    return values


def add_if_number(result: dict, key: str, value: Any) -> None:
    if is_number(value):
        result[key] = value


def add_stats(result: dict, values: list[float], prefix: str, precision: int) -> None:
    if not values:
        return
    result[f"{prefix}_avg"] = round(mean(values), precision)
    result[f"{prefix}_min"] = round(min(values), precision)
    result[f"{prefix}_max"] = round(max(values), precision)


def summarize_metrics(data: dict) -> dict:
    summary = data.get("summary", {}).get("metric_summary")
    if summary:
        result = {}
        metric_map = {
            "knee_angle_left": {"avg": "left_knee_avg", "min": "left_knee_min", "max": "left_knee_max"},
            "knee_angle_right": {"avg": "right_knee_avg", "min": "right_knee_min", "max": "right_knee_max"},
            "hip_height": {"avg": "hip_height_avg", "min": "hip_height_min", "max": "hip_height_max"},
            "elbow_angle_left": {"avg": "elbow_left_avg"},
            "elbow_angle_right": {"avg": "elbow_right_avg"},
            "shoulder_tilt": {"avg": "shoulder_tilt_avg"},
            "pelvis_tilt": {"avg": "pelvis_tilt_avg"},
            "torso_lean": {"avg": "torso_lean_avg"},
            "head_forward_offset": {"avg": "head_forward_avg"},
            "hand_reach_left": {"avg": "hand_reach_left_avg"},
            "hand_reach_right": {"avg": "hand_reach_right_avg"},
            "shoulder_hip_separation": {"avg": "shoulder_hip_separation_avg"},
        }
        for metric_key, output_keys in metric_map.items():
            metric_stats = summary.get(metric_key, {})
            for stat_key, output_key in output_keys.items():
                add_if_number(result, output_key, metric_stats.get(stat_key))
        return result

    frames = data.get("sampled_frames", [])
    if not frames:
        return {}

    result = {}
    add_stats(result, collect_metric_values(frames, "knee_angle_left"), "left_knee", 1)
    add_stats(result, collect_metric_values(frames, "knee_angle_right"), "right_knee", 1)
    add_stats(result, collect_metric_values(frames, "hip_height"), "hip_height", 3)
    return result


def normalize_text(value: str) -> str:
    return value.lower().replace("_", " ").replace("-", " ").strip()


def normalize_sport(value: str | None) -> str | None:
    if not value:
        return None
    value_norm = normalize_text(value)
    for alias, sport in SPORT_ALIASES.items():
        if normalize_text(alias) in value_norm:
            return sport
    return None


def detect_sport(video_name: str, pose_data: dict | None = None) -> str:
    lower = normalize_text(video_name)
    for sport, keywords in SPORT_KEYWORDS.items():
        if any(normalize_text(keyword) in lower for keyword in keywords):
            return sport

    if lower == "img 1392.mov":
        return "fencing"

    if pose_data:
        frames = pose_data.get("sampled_frames", [])
        if frames:
            left = collect_metric_values(frames, "knee_angle_left")
            right = collect_metric_values(frames, "knee_angle_right")
            hip = collect_metric_values(frames, "hip_height")
            if left and right and hip:
                left_avg = mean(left)
                right_avg = mean(right)
                hip_avg = mean(hip)
                if left_avg > 155 and right_avg > 150 and 0.43 <= hip_avg <= 0.56:
                    return "fencing"

    return "unknown"


def normalize_template(value: str | None, sport: str) -> str:
    specs = TEMPLATE_SPECS.get(sport, {})
    if not value or not specs:
        return "unspecified"
    value_norm = normalize_text(value)
    if sport == "climbing":
        if "lead" in value_norm or "先锋" in value_norm:
            return "lead_continuous_climb"
        if "top rope" in value_norm or "toprope" in value_norm or "顶绳" in value_norm:
            return "top_rope_continuous_climb"
    best_match = "unspecified"
    best_score = 0
    for template_key, spec in specs.items():
        for alias in spec.get("aliases", []):
            alias_norm = normalize_text(alias)
            if alias_norm and alias_norm in value_norm and len(alias_norm) > best_score:
                best_match = template_key
                best_score = len(alias_norm)
    return best_match


def detect_template(video_name: str, sport: str) -> str:
    return normalize_template(video_name, sport)


def get_template_spec(sport: str, template: str) -> dict:
    specs = TEMPLATE_SPECS.get(sport, {})
    if template in specs:
        return specs[template]
    return {
        "label": "未指定动作模板",
        "aliases": [],
        "dimensions": [],
        "tracking": ["拍摄质量", "动作关键阶段", "可量化姿态指标"],
        "reshoot": "请在文件名或指令中明确项目和动作模板，并按对应拍摄规范重新提交。",
    }


def resolve_analysis_context(video_path: Path, pose_data: dict | None = None) -> dict:
    env_sport = normalize_sport(os.environ.get("POSE_ANALYSIS_SPORT"))
    sport = env_sport or detect_sport(video_path.name, pose_data)
    env_template = os.environ.get("POSE_ANALYSIS_TEMPLATE")
    template = normalize_template(env_template, sport) if env_template else detect_template(video_path.name, sport)
    template_spec = get_template_spec(sport, template)
    sport_meta = SPORT_META.get(sport, SPORT_META["unknown"])
    athlete_id = os.environ.get("POSE_ANALYSIS_ATHLETE_ID", "athlete-a").strip() or "athlete-a"

    return {
        "sport": sport,
        "sport_label": sport_meta["label"],
        "template": template,
        "template_label": template_spec["label"],
        "athlete_id": athlete_id,
        "athlete_label": "运动员A",
        "expert": sport_meta["expert"],
        "template_spec": template_spec,
        "context_source": "environment" if env_sport or env_template else "filename",
    }


def evaluate_quality_gate(pose_data: dict, context: dict) -> dict:
    summary = pose_data.get("summary", {})
    quality = summary.get("quality", {}) or {}
    has_quality_metadata = bool(quality)
    frames = pose_data.get("sampled_frames", [])
    detected_frames = int(quality.get("detected_pose_frames") or summary.get("total_frames") or len(frames) or 0)
    sample_attempts = int(quality.get("sample_attempts") or detected_frames or 0)
    detection_rate = quality.get("detection_rate")
    if not is_number(detection_rate):
        detection_rate = 1.0 if detected_frames > 0 and sample_attempts == detected_frames else 0.0

    avg_core_visibility = quality.get("avg_core_visibility")
    avg_lower_visibility = quality.get("avg_lower_body_visibility")
    avg_upper_visibility = quality.get("avg_upper_body_visibility")
    avg_bbox_height = quality.get("avg_body_bbox_height")

    reasons: list[str] = []
    limitations: list[str] = []
    reshoot: list[str] = []
    conclusion = "可评分"
    confidence = "高"

    if detected_frames == 0:
        reasons.append("未提取到有效人体姿态关键点。")
        reshoot.append("重新拍摄时让运动员全身进入画面，并避免遮挡。")
        return {
            "conclusion": "不可评分",
            "confidence": "低",
            "reasons": reasons,
            "limitations": ["无法判断动作阶段、关节角度和技术完成度。"],
            "reshoot": reshoot + [context.get("template_spec", {}).get("reshoot", "")],
        }

    if not has_quality_metadata:
        conclusion = "部分可评分"
        confidence = "中"
        limitations.append("姿态 JSON 缺少检测率、关键点可见度和主体画面占比摘要；只能按已有姿态指标做有限判断。")

    if detected_frames < 8:
        conclusion = "不可评分"
        confidence = "低"
        reasons.append(f"有效姿态帧只有 {detected_frames} 帧，不足以支撑动作评分。")
        reshoot.append("保留完整动作周期，重复训练动作建议至少 3 次。")
    elif detected_frames < 20:
        conclusion = "部分可评分"
        confidence = "低"
        limitations.append(f"有效姿态帧只有 {detected_frames} 帧，只能做有限观察。")

    if detection_rate < 0.35:
        conclusion = "不可评分"
        confidence = "低"
        reasons.append(f"姿态检测成功率约 {detection_rate:.0%}，关键点追踪不稳定。")
        reshoot.append("提高光线、稳定机位，并让主体占据画面主要区域。")
    elif detection_rate < 0.65 and conclusion != "不可评分":
        conclusion = "部分可评分"
        confidence = "低"
        limitations.append(f"姿态检测成功率约 {detection_rate:.0%}，时间序列指标置信度较低。")

    if is_number(avg_core_visibility) and avg_core_visibility < 0.45:
        conclusion = "不可评分"
        confidence = "低"
        reasons.append(f"核心躯干关键点平均可见度约 {avg_core_visibility:.2f}，遮挡或识别不稳定。")
    elif is_number(avg_core_visibility) and avg_core_visibility < 0.65 and conclusion != "不可评分":
        conclusion = "部分可评分"
        confidence = "中" if confidence == "高" else confidence
        limitations.append(f"核心躯干关键点平均可见度约 {avg_core_visibility:.2f}，部分姿态判断需降级。")

    lower_body_required = context.get("sport") in {"fencing", "fitness"}
    if lower_body_required and is_number(avg_lower_visibility) and avg_lower_visibility < 0.5:
        conclusion = "不可评分"
        confidence = "低"
        reasons.append(f"下肢关键点平均可见度约 {avg_lower_visibility:.2f}，无法可靠判断步法或下肢控制。")
    elif lower_body_required and is_number(avg_lower_visibility) and avg_lower_visibility < 0.7 and conclusion != "不可评分":
        conclusion = "部分可评分"
        confidence = "中" if confidence == "高" else confidence
        limitations.append(f"下肢关键点平均可见度约 {avg_lower_visibility:.2f}，下肢评分置信度下降。")

    if is_number(avg_bbox_height):
        if avg_bbox_height < 0.25:
            conclusion = "部分可评分" if conclusion != "不可评分" else conclusion
            confidence = "中" if confidence == "高" else confidence
            limitations.append(f"运动员画面占比偏小，身体高度约占画面 {avg_bbox_height:.0%}。")
            reshoot.append("下次让运动员身体高度约占画面 35%-80%。")
        elif avg_bbox_height > 0.9:
            conclusion = "部分可评分" if conclusion != "不可评分" else conclusion
            confidence = "中" if confidence == "高" else confidence
            limitations.append(f"运动员画面占比过大，身体高度约占画面 {avg_bbox_height:.0%}，容易出画。")
            reshoot.append("下次稍微拉远镜头，确保手脚和完整动作阶段都在画面内。")

    if context.get("template") == "unspecified" and conclusion != "不可评分":
        conclusion = "部分可评分"
        confidence = "中" if confidence == "高" else confidence
        limitations.append("动作模板未明确，只能生成通用观察，不能做严格专项评分。")

    if conclusion == "可评分":
        reasons.append("有效姿态帧、检测稳定性和关键身体部位可见度满足当前模板的基础分析要求。")
    elif conclusion == "部分可评分" and not reasons:
        reasons.append("视频可支持部分技术观察，但存在影响综合评分的拍摄或识别限制。")

    template_reshoot = context.get("template_spec", {}).get("reshoot")
    if template_reshoot and template_reshoot not in reshoot:
        reshoot.append(template_reshoot)

    return {
        "conclusion": conclusion,
        "confidence": confidence,
        "reasons": reasons,
        "limitations": limitations,
        "reshoot": [item for item in reshoot if item],
    }


def format_list(items: list[str], fallback: str) -> str:
    values = [item for item in items if item]
    if not values:
        values = [fallback]
    return "\n".join(f"- {item}" for item in values)


def format_metric(value: Any, suffix: str = "") -> str:
    if is_number(value):
        return f"{value}{suffix}"
    return "N/A"


def dimensions_table(dimensions: list[tuple[str, int]]) -> str:
    if not dimensions:
        return "| 维度 | 权重 | 本地证据 |\n| --- | ---: | --- |\n| 待明确动作模板 | N/A | 请先指定项目和动作模板 |"
    lines = ["| 维度 | 权重 | 本地证据 |", "| --- | ---: | --- |"]
    for name, weight in dimensions:
        lines.append(f"| {name} | {weight} | 待 Codex 结合视频、姿态 JSON 和知识库补全 |")
    return "\n".join(lines)


def history_key(context: dict) -> str:
    return f"{context.get('athlete_id', 'athlete-a')}|{context.get('sport', 'unknown')}|{context.get('template', 'unspecified')}"


def load_history_index(history_path: Path) -> dict:
    if not history_path.exists():
        return {}
    try:
        data = json.loads(history_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def update_history_index(history_path: Path, context: dict, entry: dict, limit: int = 50) -> dict:
    history = load_history_index(history_path)
    key = history_key(context)
    entries = history.get(key, [])
    if not isinstance(entries, list):
        entries = []
    entries.append(entry)
    history[key] = entries[-limit:]
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    return history


def build_history_section(context: dict, history_entries: list[dict] | None) -> str:
    entries = history_entries or []
    if not entries:
        return (
            "### 相对上一次\n"
            "- 暂无同一动作模板历史记录。\n\n"
            "### 最近三次趋势\n"
            "- 暂无足够历史数据。\n\n"
            "### 下次复测重点\n"
            f"{format_list(context['template_spec'].get('tracking', []), '保持同一机位和同一动作模板。')}"
        )

    last = entries[-1]
    recent = entries[-3:]
    return (
        "### 相对上一次\n"
        f"- 上一次报告：{last.get('report_output', 'N/A')}\n"
        f"- 上一次质量结论：{last.get('quality_conclusion', 'N/A')}\n"
        "- 本次和上次的具体技术进退步，需要 Codex 对照两次 JSON 与视频证据补全。\n\n"
        "### 最近三次趋势\n"
        f"- 当前同模板历史记录数：{len(entries)}\n"
        f"- 最近三次质量结论：{', '.join(item.get('quality_conclusion', 'N/A') for item in recent)}\n\n"
        "### 下次复测重点\n"
        f"{format_list(context['template_spec'].get('tracking', []), '保持同一机位和同一动作模板。')}"
    )


def build_unscorable_markdown(
    video_path: Path,
    pose_data: dict,
    context: dict,
    quality_gate: dict,
    metrics: dict,
    date_cn: str,
    date_time: str,
) -> str:
    summary = pose_data.get("summary", {})
    return f"""# {context['sport_label']}-{context['template_label']} 拍摄质量报告

**分析日期**：{date_cn}
**视频来源**：{video_path.name}
**匿名身份**：{context['athlete_label']}
**分析工具**：MediaPipe + {CODEX_MODEL_LABEL}

## 一、拍摄质量与可评分结论

- 结论：{quality_gate['conclusion']}
- 置信度：{quality_gate['confidence']}
- 有效姿态帧：{summary.get('total_frames', 'N/A')}
- 姿态检测成功率：{format_metric(summary.get('quality', {}).get('detection_rate'))}

## 二、为什么不能评分

{format_list(quality_gate['reasons'], '当前视频不足以支撑动作评分。')}

## 三、仍可保留的观察

- 左膝角度：{format_metric(metrics.get('left_knee_avg'), '°')}
- 右膝角度：{format_metric(metrics.get('right_knee_avg'), '°')}
- 髋部高度：{format_metric(metrics.get('hip_height_avg'))}
- 以上观察只作为低置信度参考，不作为技术评分依据。

## 四、重新拍摄建议

{format_list(quality_gate['reshoot'], '按当前动作模板重新拍摄，确保全身和关键动作阶段入画。')}

## 五、下次提交文件名建议

```text
YYYY-MM-DD_{context['sport_label']}_{context['template_label']}_A01.mov
```

## 六、隐私说明

本报告默认使用匿名身份，不记录儿童真实姓名。

---

*报告生成时间：{date_time}*
"""


def build_markdown(video_path: Path, pose_data: dict, history_entries: list[dict] | None = None) -> str:
    today = datetime.now()
    date_cn = today.strftime("%Y-%m-%d")
    date_time = today.strftime("%Y-%m-%d %H:%M")
    context = resolve_analysis_context(video_path, pose_data)
    quality_gate = evaluate_quality_gate(pose_data, context)
    metrics = summarize_metrics(pose_data)
    summary = pose_data.get("summary", {})
    key_frame = pose_data.get("key_frames", {}).get("lowest_center_of_gravity")

    if quality_gate["conclusion"] == "不可评分":
        return build_unscorable_markdown(video_path, pose_data, context, quality_gate, metrics, date_cn, date_time)

    scoring_section = ""
    if quality_gate["conclusion"] == "可评分":
        scoring_section = f"""## 三、技术评分

综合评分：待 Codex 按知识库补全 / 100
评分置信度：{quality_gate['confidence']}

{dimensions_table(context['template_spec'].get('dimensions', []))}
"""
    else:
        scoring_section = f"""## 三、可评分维度

本次结论为部分可评分，不给综合总分。以下只列出可由 Codex 结合视频和姿态 JSON 复核的维度。

{dimensions_table(context['template_spec'].get('dimensions', []))}
"""

    return f"""# {context['sport_label']}-{context['template_label']} 技术分析报告

**分析日期**：{date_cn}
**视频来源**：{video_path.name}
**匿名身份**：{context['athlete_label']}
**分析模型**：{CODEX_MODEL_LABEL}
**专家角色**：{context['expert']}
**姿态检测**：MediaPipe（{summary.get('total_frames', 'N/A')} 帧人体姿态数据）

## 一、拍摄质量与可评分结论

- 结论：{quality_gate['conclusion']}
- 置信度：{quality_gate['confidence']}
- 主要依据：
{format_list(quality_gate['reasons'], '视频满足基础分析要求。')}
- 本次不能可靠判断：
{format_list(quality_gate['limitations'], '暂无明确限制。')}

## 二、本次核心结论

- 本地脚本已完成姿态提取、质量门槛判断和报告骨架生成。
- 最终技术结论必须由 Codex 结合原视频、姿态 JSON、报告模板和专项知识库补全。
- 报告应优先回答：本次主要技术问题、下一周训练建议、下次追踪指标，以及同模板历史变化。

{scoring_section}
## 四、关键证据

| 指标 | 本地摘要 |
| --- | --- |
| 左膝角度 | {format_metric(metrics.get('left_knee_avg'), '°')}（范围 {format_metric(metrics.get('left_knee_min'), '°')} ~ {format_metric(metrics.get('left_knee_max'), '°')}） |
| 右膝角度 | {format_metric(metrics.get('right_knee_avg'), '°')}（范围 {format_metric(metrics.get('right_knee_min'), '°')} ~ {format_metric(metrics.get('right_knee_max'), '°')}） |
| 髋部高度 | {format_metric(metrics.get('hip_height_avg'))}（范围 {format_metric(metrics.get('hip_height_min'))} ~ {format_metric(metrics.get('hip_height_max'))}） |
| 左/右肘角 | {format_metric(metrics.get('elbow_left_avg'), '°')} / {format_metric(metrics.get('elbow_right_avg'), '°')} |
| 躯干前倾 | {format_metric(metrics.get('torso_lean_avg'), '°')} |
| 肩线/骨盆倾斜 | {format_metric(metrics.get('shoulder_tilt_avg'), '°')} / {format_metric(metrics.get('pelvis_tilt_avg'), '°')} |
| 头部前探 | {format_metric(metrics.get('head_forward_avg'))} |
| 左/右手前伸距离 | {format_metric(metrics.get('hand_reach_left_avg'))} / {format_metric(metrics.get('hand_reach_right_avg'))} |
| 最低重心关键帧 | {json.dumps(key_frame, ensure_ascii=False) if key_frame else 'N/A'} |

## 五、主要技术问题排序

### 1. 待 Codex 补全的专项问题
表现：结合视频关键时间点、姿态 JSON 和 `{context['sport_label']}-{context['template_label']}` 知识库补全。

影响：说明该问题对技术表现、节奏、效率或稳定性的影响。

证据：必须引用时间点、角度、趋势或可见动作阶段。

### 2. 证据不足或需复拍的维度
{format_list(quality_gate['limitations'], '当前视频没有明显证据不足维度。')}

## 六、训练建议

### 下次训练重点
{format_list(context['template_spec'].get('tracking', []), '围绕当前动作模板复测关键指标。')}

### 一周内练习建议
- 由 Codex 根据最终技术问题补全 2-4 个可执行练习。
- 每个练习应包含目的、执行方式和教练观察口令。

### 教练可观察口令
- 用一句话提示动作关键点。
- 避免使用羞辱式标签或不可验证判断。

## 七、下次追踪指标

| 指标 | 目标 | 拍摄要求 |
| --- | --- | --- |
| 拍摄质量 | 保持可评分 | {context['template_spec'].get('reshoot', '保持固定机位和完整动作周期。')} |
| 动作模板 | 与本次一致 | 文件名或指令继续使用 `{context['template_label']}` |
| 专项指标 | 待 Codex 补全 | 使用同一角度，便于历史对比 |

## 八、历史对比

{build_history_section(context, history_entries)}

## 九、隐私说明

本报告默认使用匿名身份，不记录儿童真实姓名。报告面向教练和家长复盘，不用于医疗诊断。

---

*报告生成时间：{date_time}*
*分析工具：MediaPipe + 本地标准报告生成器*
"""


def safe_filename_part(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value).strip()
    return value or "未指定"


def build_output_paths(video_path: Path, sport: str, output_root: Path, context: dict | None = None):
    now = datetime.now()
    date_compact = now.strftime("%Y%m%d")
    date_dash = now.strftime("%Y-%m-%d")
    meta = SPORT_META.get(sport, SPORT_META["unknown"])
    if context:
        report_name = (
            f"{safe_filename_part(context.get('sport_label', meta['label']))}_"
            f"{safe_filename_part(context.get('template_label', '未指定动作模板'))}_"
            f"{date_compact}.md"
        )
    else:
        report_name = meta["filename"].format(date=date_compact, date_dash=date_dash)
    json_name = f"{video_path.stem}.pose.{date_compact}.json"
    report_path = output_root / report_name
    json_path = output_root / json_name
    if not report_path.exists() and not json_path.exists():
        return report_path, json_path

    time_suffix = now.strftime("%H%M%S")
    for counter in range(1000):
        suffix = f"-{time_suffix}" if counter == 0 else f"-{time_suffix}-{counter}"
        candidate_report = report_path.with_name(f"{report_path.stem}{suffix}{report_path.suffix}")
        candidate_json = json_path.with_name(f"{json_path.stem}{suffix}{json_path.suffix}")
        if not candidate_report.exists() and not candidate_json.exists():
            return candidate_report, candidate_json

    raise RuntimeError("无法生成不覆盖现有文件的输出路径")


def main() -> int:
    if len(sys.argv) < 3:
        print("用法: python report_formatter.py <视频路径> <pose_json_path>", file=sys.stderr)
        return 1

    video_path = absolute_without_resolving_symlink(Path(sys.argv[1]))
    pose_json_path = Path(sys.argv[2]).expanduser().resolve()
    pose_data = load_json(pose_json_path)
    context = resolve_analysis_context(video_path, pose_data)
    quality_gate = evaluate_quality_gate(pose_data, context)
    output_root = get_output_root()

    output_root.mkdir(parents=True, exist_ok=True)
    history_path = output_root / HISTORY_FILENAME
    existing_history = load_history_index(history_path)
    existing_entries = existing_history.get(history_key(context), [])

    md_out, json_out = build_output_paths(video_path, context["sport"], output_root, context=context)
    json_out.write_text(json.dumps(pose_data, ensure_ascii=False, indent=2), encoding="utf-8")
    md_out.write_text(build_markdown(video_path, pose_data, history_entries=existing_entries), encoding="utf-8")

    metrics = summarize_metrics(pose_data)
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "video": str(video_path),
        "json_output": str(json_out),
        "report_output": str(md_out),
        "sport": context["sport"],
        "sport_label": context["sport_label"],
        "template": context["template"],
        "template_label": context["template_label"],
        "quality_conclusion": quality_gate["conclusion"],
        "quality_confidence": quality_gate["confidence"],
        "metrics": metrics,
    }
    history = update_history_index(history_path, context, entry)

    result = {
        "status": "ok",
        "video": str(video_path),
        "json_output": str(json_out),
        "report_output": str(md_out),
        "history_output": str(history_path),
        "history_key": history_key(context),
        "history_entries": len(history.get(history_key(context), [])),
        "sport": context["sport"],
        "template": context["template"],
        "quality_conclusion": quality_gate["conclusion"],
        "message": "已完成本地报告骨架、姿态 JSON 与历史索引落盘。请由 Codex 基于报告和知识库补全最终教练分析。",
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
