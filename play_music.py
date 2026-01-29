import json
import time
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

# ==== 設定 ====
SCORE_JSON = "score.json"        # ← 楽譜JSON（今回の形式）
POSE_JSON = "notes_poses.json"  # ← 音名→姿勢対応表
PORT = "/dev/ttyACM0"
ROBOT_ID = "my_awesome_follower_arm"

MOVE_RATIO = 0.4   # 音価のうち「叩きに使う割合」
LIFT_RATIO = 0.2   # 音価のうち「離れる割合」

LIFT_OFFSET = {
    "shoulder_lift.pos": -10.0,
    "elbow_flex.pos": 10.0,
    "wrist_flex.pos": 15.0,
}

JOINT_NAMES = [
    "shoulder_pan.pos",
    "shoulder_lift.pos",
    "elbow_flex.pos",
    "wrist_flex.pos",
    "wrist_roll.pos",
    "gripper.pos",
]


def main():
    # ==== JSON読み込み ====
    with open(SCORE_JSON, "r", encoding="utf-8") as f:
        score = json.load(f)

    with open(POSE_JSON, "r", encoding="utf-8") as f:
        raw_note_poses = json.load(f)

    note_poses = {
        item["note"]: item["motors"]
        for item in raw_note_poses
    }

    bpm = score["bpm"]
    notes = score["notes"]

    beat_sec = 60.0 / bpm

    # ==== ロボット接続 ====
    cfg = SO101FollowerConfig(port=PORT, id=ROBOT_ID)
    robot = SO101Follower(cfg)
    robot.connect(calibrate=False)

    try:
        for n in notes:
            note = n["note"]
            length = n["length"]

            if note not in note_poses:
                raise ValueError(f"姿勢が未定義の音です: {note}")

            base_time = beat_sec * length
            move_time = base_time * MOVE_RATIO
            lift_time = base_time * LIFT_RATIO
            hold_time = base_time - move_time - lift_time

            target_pos = note_poses[note]

            print(f"♪ {note} ({length})")

            # --- 叩く位置へ ---
            robot.send_action({**target_pos, "time_from_start": move_time})
            time.sleep(move_time + 0.02)

            # --- 振り上げ ---
            lift_pos = {}
            for k in JOINT_NAMES:
                base = float(target_pos[k])
                lift_pos[k] = base + LIFT_OFFSET.get(k, 0.0)

            robot.send_action({**lift_pos, "time_from_start": lift_time})
            time.sleep(lift_time + 0.02)

            # --- 音価分保持 ---
            time.sleep(max(0.0, hold_time))

    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()
