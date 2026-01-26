import json
from so101 import SO101Arm

LEADER_PORT = "/dev/ttyUSB1"
FOLLOWER_PORT = "/dev/ttyUSB0"
NOTES_FILE = "notes.json"


def load_notes():
    try:
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"notes": {}}


def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)


def teach_one_note(note_name):
    leader = SO101Arm(LEADER_PORT, "my_awesome_leader_arm.json")
    follower = SO101Arm(FOLLOWER_PORT, "my_awesome_follower_arm.json")

    # ① Leader 脱力
    leader.set_torque(False)
    leader.enable_teach_mode(True)

    print(f"👉 Leaderを動かして【{note_name}】に合わせてください")
    input("位置が決まったら Enter")

    # ③ Leader角度取得
    angles = leader.get_joint_positions()

    print("取得角度:")
    for k, v in angles.items():
        print(f" {k}: {v}")

    # ④ Followerで再現
    print("Followerで再現します")
    follower.set_torque(True)
    follower.move_to(angles, speed="slow")

    ok = input("Followerで正しく叩けそうですか？ (y/n): ")
    if ok.lower() != "y":
        print("❌ 保存せず終了")
        return

    # ⑥ JSONに保存
    notes = load_notes()
    notes["notes"][note_name] = {
        "pre_hit": angles
    }
    save_notes(notes)

    print(f"✅ {note_name} を保存しました")


if __name__ == "__main__":
    note = input("教示する音名（例: G3）: ")
    teach_one_note(note)
