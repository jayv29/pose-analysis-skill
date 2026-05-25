#!/usr/bin/env python3
"""
Pose Analysis Script - Enhanced
用 MediaPipe 分析训练视频姿态，输出生物力学角度和关键帧
"""

import sys
import json
import os
import math
from pathlib import Path
from typing import Dict, List
from statistics import mean, pstdev

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
MODEL_FILENAME = "pose_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-assets/pose_landmarker.task"
CORE_INDICES = [11, 12, 23, 24]
UPPER_BODY_INDICES = [11, 12, 13, 14, 15, 16]
LOWER_BODY_INDICES = [23, 24, 25, 26, 27, 28]
BODY_BOX_INDICES = [0, 11, 12, 15, 16, 23, 24, 27, 28]


def resolve_model_path() -> str | None:
    """Find the MediaPipe Pose Landmarker model without assuming an OpenClaw path."""
    candidates: list[Path] = []

    env_model = os.environ.get("POSE_LANDMARKER_MODEL")
    if env_model:
        candidates.append(Path(env_model).expanduser())

    candidates.extend([
        SKILL_DIR / "assets" / "models" / MODEL_FILENAME,
        Path.home() / ".cache" / "pose-analysis" / MODEL_FILENAME,
        Path("/tmp") / MODEL_FILENAME,
    ])

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    searched = "\n".join(f"  - {path}" for path in candidates)
    print("错误: 找不到 MediaPipe 姿态模型 pose_landmarker.task。", file=sys.stderr)
    print("请先运行 scripts/download_pose_model.sh，或手动下载模型：", file=sys.stderr)
    print(f"  curl -L -o /tmp/{MODEL_FILENAME} {MODEL_URL}", file=sys.stderr)
    print("已检查路径：", file=sys.stderr)
    print(searched, file=sys.stderr)
    return None


class GeometryUtils:
    @staticmethod
    def calculate_angle(a: Dict, b: Dict, c: Dict) -> float:
        """
        计算三点之间的角度 (0-180度)
        a: 第一个点 (如 Hip)
        b: 中间点 (如 Knee)
        c: 第三个点 (如 Ankle)
        """
        # 转换为向量
        ba = [a['x'] - b['x'], a['y'] - b['y']]
        bc = [c['x'] - b['x'], c['y'] - b['y']]

        # 计算向量长度
        norm_ba = math.sqrt(ba[0]**2 + ba[1]**2)
        norm_bc = math.sqrt(bc[0]**2 + bc[1]**2)

        if norm_ba == 0 or norm_bc == 0:
            return 0.0

        # 计算点积
        dot_product = ba[0] * bc[0] + ba[1] * bc[1]

        # 计算角度 (弧度 -> 角度)
        try:
            cosine = max(-1.0, min(1.0, dot_product / (norm_ba * norm_bc)))
            angle = math.degrees(math.acos(cosine))
        except ValueError:
            return 0.0

        return round(angle, 1)

    @staticmethod
    def calculate_line_angle(a: Dict, b: Dict) -> float:
        """计算两点连线相对水平线的角度，右高左低为正。"""
        dx = b['x'] - a['x']
        dy = b['y'] - a['y']
        if dx == 0 and dy == 0:
            return 0.0
        return round(math.degrees(math.atan2(dy, dx)), 1)

    @staticmethod
    def calculate_vertical_angle(top: Dict, bottom: Dict) -> float:
        """计算躯干相对竖直线的偏移角度，向前/向右偏记为正。"""
        dx = top['x'] - bottom['x']
        dy = bottom['y'] - top['y']
        if dx == 0 and dy == 0:
            return 0.0
        return round(math.degrees(math.atan2(dx, dy)), 1)

    @staticmethod
    def calculate_distance(a: Dict, b: Dict) -> float:
        dx = a['x'] - b['x']
        dy = a['y'] - b['y']
        return round(math.sqrt(dx * dx + dy * dy), 3)

    @staticmethod
    def midpoint(a: Dict, b: Dict) -> Dict:
        return {
            'x': (a['x'] + b['x']) / 2,
            'y': (a['y'] + b['y']) / 2,
            'z': (a.get('z', 0) + b.get('z', 0)) / 2,
            'visibility': min(a.get('visibility', 1), b.get('visibility', 1)),
        }

    @staticmethod
    def get_landmark(landmarks: List[Dict], index: int) -> Dict:
        """安全获取关键点"""
        if index < len(landmarks):
            return landmarks[index]
        return {'x': 0, 'y': 0, 'z': 0, 'visibility': 0}


def analyze_frame_metrics(landmarks: List[Dict]) -> Dict:
    """计算单帧的生物力学指标"""
    utils = GeometryUtils()

    # MediaPipe Pose Landmarks 索引:
    # 0: nose
    # 11: left_shoulder, 12: right_shoulder
    # 13: left_elbow,    14: right_elbow
    # 15: left_wrist,    16: right_wrist
    # 23: left_hip,      24: right_hip
    # 25: left_knee,     26: right_knee
    # 27: left_ankle,    28: right_ankle

    nose = utils.get_landmark(landmarks, 0)
    l_shoulder = utils.get_landmark(landmarks, 11)
    r_shoulder = utils.get_landmark(landmarks, 12)
    l_elbow = utils.get_landmark(landmarks, 13)
    r_elbow = utils.get_landmark(landmarks, 14)
    l_wrist = utils.get_landmark(landmarks, 15)
    r_wrist = utils.get_landmark(landmarks, 16)
    l_hip = utils.get_landmark(landmarks, 23)
    r_hip = utils.get_landmark(landmarks, 24)
    l_knee = utils.get_landmark(landmarks, 25)
    r_knee = utils.get_landmark(landmarks, 26)
    l_ankle = utils.get_landmark(landmarks, 27)
    r_ankle = utils.get_landmark(landmarks, 28)

    shoulder_mid = utils.midpoint(l_shoulder, r_shoulder)
    hip_mid = utils.midpoint(l_hip, r_hip)

    metrics = {
        "knee_angle_left": utils.calculate_angle(l_hip, l_knee, l_ankle),
        "knee_angle_right": utils.calculate_angle(r_hip, r_knee, r_ankle),
        "hip_height": round((l_hip['y'] + r_hip['y']) / 2, 3),  # y 越大越低 (0在上, 1在下)
        "elbow_angle_left": utils.calculate_angle(l_shoulder, l_elbow, l_wrist),
        "elbow_angle_right": utils.calculate_angle(r_shoulder, r_elbow, r_wrist),
        "shoulder_tilt": utils.calculate_line_angle(l_shoulder, r_shoulder),
        "pelvis_tilt": utils.calculate_line_angle(l_hip, r_hip),
        "torso_lean": utils.calculate_vertical_angle(shoulder_mid, hip_mid),
        "head_forward_offset": round(nose['x'] - shoulder_mid['x'], 3),
        "head_height": round(nose['y'], 3),
        "head_tilt_proxy": utils.calculate_vertical_angle(nose, shoulder_mid),
        "hand_height_left": round(l_wrist['y'], 3),
        "hand_height_right": round(r_wrist['y'], 3),
        "hand_reach_left": utils.calculate_distance(l_wrist, shoulder_mid),
        "hand_reach_right": utils.calculate_distance(r_wrist, shoulder_mid),
        "shoulder_hip_separation": round(utils.calculate_line_angle(l_shoulder, r_shoulder) - utils.calculate_line_angle(l_hip, r_hip), 1),
    }

    return metrics


def visibility_mean(landmarks: List[Dict], indices: List[int]) -> float:
    values = []
    for index in indices:
        landmark = GeometryUtils.get_landmark(landmarks, index)
        visibility = landmark.get("visibility", 1)
        if isinstance(visibility, (int, float)):
            values.append(visibility)
    if not values:
        return 0.0
    return round(mean(values), 3)


def analyze_frame_quality(landmarks: List[Dict]) -> Dict:
    keypoints = [GeometryUtils.get_landmark(landmarks, index) for index in BODY_BOX_INDICES]
    usable_points = [
        point for point in keypoints
        if point.get("visibility", 1) >= 0.2 and 0 <= point.get("x", -1) <= 1 and 0 <= point.get("y", -1) <= 1
    ]
    out_of_frame = sum(
        1 for point in keypoints
        if point.get("x", -1) < 0 or point.get("x", 2) > 1 or point.get("y", -1) < 0 or point.get("y", 2) > 1
    )
    if usable_points:
        min_y = min(point["y"] for point in usable_points)
        max_y = max(point["y"] for point in usable_points)
        min_x = min(point["x"] for point in usable_points)
        max_x = max(point["x"] for point in usable_points)
        bbox_height = round(max_y - min_y, 3)
        bbox_width = round(max_x - min_x, 3)
    else:
        bbox_height = 0.0
        bbox_width = 0.0

    return {
        "core_visibility": visibility_mean(landmarks, CORE_INDICES),
        "upper_body_visibility": visibility_mean(landmarks, UPPER_BODY_INDICES),
        "lower_body_visibility": visibility_mean(landmarks, LOWER_BODY_INDICES),
        "body_bbox_height": bbox_height,
        "body_bbox_width": bbox_width,
        "out_of_frame_keypoints": out_of_frame,
    }


def summarize_series(values: List[float], precision: int = 1) -> Dict:
    cleaned = [v for v in values if v is not None]
    if not cleaned:
        return {}
    return {
        "avg": round(mean(cleaned), precision),
        "min": round(min(cleaned), precision),
        "max": round(max(cleaned), precision),
        "std": round(pstdev(cleaned), precision) if len(cleaned) > 1 else 0.0,
    }


def build_metric_summary(frames: List[Dict]) -> Dict:
    if not frames:
        return {}

    keys = [
        "knee_angle_left", "knee_angle_right", "hip_height",
        "elbow_angle_left", "elbow_angle_right",
        "shoulder_tilt", "pelvis_tilt", "torso_lean",
        "head_forward_offset", "head_height", "head_tilt_proxy",
        "hand_height_left", "hand_height_right",
        "hand_reach_left", "hand_reach_right",
        "shoulder_hip_separation",
    ]
    summary = {}
    for key in keys:
        values = [frame.get("metrics", {}).get(key) for frame in frames if key in frame.get("metrics", {})]
        precision = 3 if any(x in key for x in ["height", "offset", "reach"]) else 1
        summary[key] = summarize_series(values, precision)
    return summary


def build_quality_summary(frames: List[Dict], sample_attempts: int, fps: float, width: int, height: int) -> Dict:
    detected = len(frames)
    detection_rate = round(detected / sample_attempts, 3) if sample_attempts else 0.0
    quality_keys = [
        "core_visibility",
        "upper_body_visibility",
        "lower_body_visibility",
        "body_bbox_height",
        "body_bbox_width",
        "out_of_frame_keypoints",
    ]
    result = {
        "fps": round(fps, 3),
        "width": width,
        "height": height,
        "sample_attempts": sample_attempts,
        "detected_pose_frames": detected,
        "detection_rate": detection_rate,
    }
    for key in quality_keys:
        values = [frame.get("quality", {}).get(key) for frame in frames if key in frame.get("quality", {})]
        numeric = [value for value in values if isinstance(value, (int, float))]
        if numeric:
            prefix = "avg_" if key != "out_of_frame_keypoints" else "avg_"
            precision = 3 if key != "out_of_frame_keypoints" else 1
            result[f"{prefix}{key}"] = round(mean(numeric), precision)
    return result


def extract_pose(video_path: str) -> dict:
    """用 MediaPipe 提取姿态关键点并计算指标"""
    # 延迟导入以加快启动速度
    try:
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        import mediapipe as mp
        import cv2
    except ImportError:
        print("错误: 缺少依赖库。请运行 pip install mediapipe opencv-python", file=sys.stderr)
        sys.exit(1)
    
    print(f"正在处理视频: {video_path}", file=sys.stderr)
    
    model_path = resolve_model_path()
    if not model_path:
        return {}
    
    base_options = python.BaseOptions(
        model_asset_path=model_path,
        delegate=python.BaseOptions.Delegate.CPU,
    )
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1
    )
    
    try:
        detector = vision.PoseLandmarker.create_from_options(options)
    except Exception as e:
        print(f"错误: 加载模型失败 - {e}", file=sys.stderr)
        return {}
    
    # 读取视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误: 无法打开视频 {video_path}", file=sys.stderr)
        return {}
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    frame_count = 0
    sample_attempts = 0
    analyzed_frames = []
    
    # 用于关键帧检测的变量
    min_hip_y = 0 # 记录最低重心 (y值最大)
    lowest_cg_frame = None
    
    print(f"视频 FPS: {fps}", file=sys.stderr)
    
    while cap.isOpened() and frame_count < 450:  # 增加限制到 450 帧 (约15秒)
        success, image = cap.read()
        if not success:
            break
        
        # 采样率: 每 5 帧分析一次 (约 6fps)，以捕捉更多细节
        if frame_count % 5 == 0:
            sample_attempts += 1
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            
            # 检测姿态
            timestamp_ms = int(frame_count * 1000 / fps)
            result = detector.detect_for_video(mp_image, timestamp_ms)
            
            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                raw_landmarks = []
                # 转换 landmarks 格式
                for lm in result.pose_landmarks[0]:
                    raw_landmarks.append({
                        "x": lm.x,
                        "y": lm.y,
                        "z": lm.z if hasattr(lm, 'z') else 0,
                        "visibility": getattr(lm, "visibility", 1),
                        "presence": getattr(lm, "presence", 1),
                    })
                
                # 计算生物力学指标
                metrics = analyze_frame_metrics(raw_landmarks)
                quality = analyze_frame_quality(raw_landmarks)
                
                frame_data = {
                    "frame": frame_count,
                    "timestamp": round(timestamp_ms / 1000, 2),
                    "metrics": metrics,
                    "quality": quality,
                    # 仅保留关键的 raw landmarks 以减小 tokens (如需要)
                    # "landmarks": raw_landmarks 
                }
                analyzed_frames.append(frame_data)
                
                # 简单的关键帧检测逻辑: 寻找重心最低点 (Lunge visual)
                if metrics['hip_height'] > min_hip_y:
                    min_hip_y = metrics['hip_height']
                    lowest_cg_frame = frame_data
                
            else:
                pass # 未检测到
        
        frame_count += 1
        if frame_count % 60 == 0:
            print(f"已处理 {frame_count} 帧...", file=sys.stderr)
    
    cap.release()
    print(f"总计分析 {len(analyzed_frames)} 帧", file=sys.stderr)
    
    return {
        "all_frames": analyzed_frames,
        "quality_summary": build_quality_summary(analyzed_frames, sample_attempts, fps, width, height),
        "key_frames": {
            "lowest_center_of_gravity": lowest_cg_frame
        }
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python pose_analyzer.py <视频文件路径>", file=sys.stderr)
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    print(f"正在分析视频: {video_path}", file=sys.stderr)
    print("正在提取姿态关键点并计算生物力学指标...", file=sys.stderr)
    
    result_data = extract_pose(video_path)
    
    if result_data and result_data["all_frames"]:
        print(f"\n成功提取数据", file=sys.stderr)
        print("\n=== POSE_DATA_START ===", file=sys.stderr)
        # 精简输出: 只输出关键帧和少量采样帧给 LLM，防止 token 爆炸
        sampled_frames = result_data["all_frames"][::6]
        final_output = {
            "summary": {
                "total_frames": len(result_data["all_frames"]),
                "duration_sec": result_data["all_frames"][-1]["timestamp"],
                "metric_summary": build_metric_summary(result_data["all_frames"]),
                "quality": result_data["quality_summary"],
            },
            "key_frames": result_data["key_frames"],
            "sampled_frames": sampled_frames
        }
        print(json.dumps(final_output, ensure_ascii=False), file=sys.stderr)
        print("=== POSE_DATA_END ===", file=sys.stderr)
        
        # 标准输出给 Codex 或命令行调用方
        print(json.dumps(final_output, ensure_ascii=False))
    else:
        print("错误: 未能提取到有效姿态数据", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
