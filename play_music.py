import json
import time
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

# ==== 設定 ====
SCORE_JSON = "score.json"        # ← 楽譜JSON（今回の形式）
POSE_JSON = "notes_poses.json"  # ← 音名→姿勢対応表
POSE_OFF_JSON = "notes_poses_off.json"  # ← 音を鳴らした後に戻る姿勢
PORT = "/dev/ttyACM0"
ROBOT_ID = "my_awesome_follower_arm"

MOVE_RATIO = 0.4   # 音価のうち「叩きに使う割合」
LIFT_RATIO = 0.2   # 音価のうち「離れる割合」

LIFT_OFFSET = {
    "shoulder_lift.pos": 20.0,
    "elbow_flex.pos": 20.0
}

JOINT_NAMES = [
    "shoulder_pan.pos",
    "shoulder_lift.pos",
    "elbow_flex.pos",
    "wrist_flex.pos",
    "wrist_roll.pos",
    "gripper.pos",
]

OFF_MOVE_TIME = 0.12  # オフ姿勢へ戻る時間（秒）


def main():
    # ==== JSON読み込み ====
    # 楽譜読み込み
    with open(SCORE_JSON, "r", encoding="utf-8") as f:
        score = json.load(f)

    # 姿勢読み込み
    with open(POSE_JSON, "r", encoding="utf-8") as f:
        raw_note_poses = json.load(f)

    # オフ姿勢読み込み
    with open(POSE_OFF_JSON, "r", encoding="utf-8") as f:
        raw_note_poses_off = json.load(f)

    note_poses = {
        item["note"]: item["motors"]
        for item in raw_note_poses
    }

    note_poses_off = {
        item["note"]: item["motors"]
        for item in raw_note_poses_off
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
            time.sleep(move_time + 1.5)

            # --- オフ姿勢へ戻す ---
            off_pos = note_poses_off.get(note)
            if off_pos is None:
                # 定義がなければリフト姿勢のまま次へ移動
                print(f"警告: オフ姿勢が未定義です: {note}（スキップ）")
                continue

            # --- 音価分保持 ---
            time.sleep(max(0.0, hold_time))

            robot.send_action({**off_pos, "time_from_start": lift_time})
            time.sleep(lift_time + 1.5)

    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()
