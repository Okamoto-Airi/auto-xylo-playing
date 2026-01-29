import json
import time
import math

from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig  # LeRobotのSO-101 API [web:16]

# ==== 設定 ====
JSON_PATH = "notes_poses.json"   # あなたのJSONファイル名に合わせて変更
PORT = "/dev/ttyACM0"            # 実機のポートに合わせて変更
ROBOT_ID = "my_awesome_follower_arm"  # キャリブレーション時に使ったidに合わせる
MOVE_TIME = 1                  # 1ポーズにかける移動時間（秒）
HOLD_TIME = 2                  # 到達後の待機時間（秒）

def deg_to_rad(d):
    return d * math.pi / 180.0

def main():
    # 1. JSONを読み込む
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. ロボットに接続
    # SO101Follower は config オブジェクトを受け取る
    cfg = SO101FollowerConfig(port=PORT, id=ROBOT_ID)
    robot = SO101Follower(cfg)

    # --- ここで必ず接続する ---
    robot.connect(calibrate=False)

    try:

        # LeRobot側で定義されている関節名（例）[web:16]
        # 実際にrobot.get_observation()["position"]のキーをprintして確認するとより確実
        joint_names = [
            "shoulder_pan.pos",
            "shoulder_lift.pos",
            "elbow_flex.pos",
            "wrist_flex.pos",
            "wrist_roll.pos",
            "gripper.pos",
        ]

        # 3. JSONの各ポーズを順に実行
        for step in data:
            note = step.get("note", "")
            motors = step["motors"]

            # 角度が度数法ならラジアンに変換（キャリブレーション次第なので要検証）
            # まずはそのまま使ってみて、動きが極端ならdeg_to_radを挟んでください。
            target_pos = {}
            for j in joint_names:
                if j not in motors:
                    raise ValueError(f"JSONのmotorsに {j} がありません")
                # そのまま使う場合:
                target_pos[j] = motors[j]
                # 度→ラジアンにしたい場合は
                # target_pos[j] = deg_to_rad(motors[j])

            print(f"Moving to note {note} pose: {target_pos}")

            # 4. 現在姿勢を取得（デバッグ用）
            obs = robot.get_observation()  # 関節角などを含む辞書を返す 返り値は {"shoulder_pan.pos": val, ...}
            current_pos = {k: obs.get(k) for k in joint_names}
            print("Current position:", current_pos)

            # 5. 目標姿勢へ移動
            # LeRobotのAPIでは `send_action` に flatten した joint position を渡す
            # (キーは "shoulder_pan.pos" のように .pos を含む必要あり)
            action = {**target_pos, "time_from_start": MOVE_TIME}
            robot.send_action(action)
            # 移動中待機
            time.sleep(MOVE_TIME + HOLD_TIME)

            # 6. 到達後の誤差を確認（検証用）
            obs_after = robot.get_observation()
            reached_pos = {k: obs_after.get(k) for k in joint_names}
            print("Reached position:", reached_pos)
            print("-" * 40)
    finally:
        # 7. 終了処理（必要に応じて）
        robot.disconnect()

if __name__ == "__main__":
    main()
