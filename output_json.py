#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

def load_notes(path: Path) -> List[str]:
    if not path.exists():
        return []
    j = json.loads(path.read_text(encoding="utf-8"))
    # expect list of {"note": "...", ...} or plain list
    if isinstance(j, list) and j and isinstance(j[0], dict) and "note" in j[0]:
        return [rec["note"] for rec in j]
    if isinstance(j, list):
        return [str(x) for x in j]
    return []

def extract_motors(obs: Dict[str, Any]) -> Dict[str, float]:
    return {k: float(v) for k, v in obs.items() if k.endswith(".pos")}

def apply_loaded_calibration(robot) -> None:
    calib = getattr(robot, "calibration", None)
    if calib:
        try:
            if hasattr(robot, "bus") and hasattr(robot.bus, "write_calibration"):
                robot.bus.write_calibration(calib)
                print("Loaded calibration applied to bus.")
            else:
                print("bus.write_calibration not available; calibration loaded into robot object.")
        except Exception as e:
            print("Warning: failed to apply calibration to bus:", e)
    else:
        print("No calibration found for this robot id; run calibrate first if needed.")

def torque_off_for_teaching(robot) -> None:
    # try common API names to disable torque so user can move arm by hand
    try:
        if hasattr(robot, "set_torque_enable"):
            robot.set_torque_enable(False)
        elif hasattr(robot, "set_torque"):
            robot.set_torque(False)
        elif hasattr(robot, "enable_motors"):
            robot.enable_motors(False)
        else:
            print("トルク制御APIが見つかりません。手で動かす場合は注意してください。")
    except Exception as e:
        print("トルクオフに失敗:", e)

def torque_on_after(robot) -> None:
    try:
        if hasattr(robot, "set_torque_enable"):
            robot.set_torque_enable(True)
        elif hasattr(robot, "set_torque"):
            robot.set_torque(True)
        elif hasattr(robot, "enable_motors"):
            robot.enable_motors(True)
    except Exception:
        pass

def main():
    p = argparse.ArgumentParser(description="手動でアームを動かしてEnterで現在の観測(.pos)を保存する")
    p.add_argument("--port", default="/dev/ttyACM0")
    p.add_argument("--id", default="my_awesome_follower_arm")
    p.add_argument("--notes", default="notes_poses.json", help="既存ノート一覧(JSON) または省略可")
    p.add_argument("--out", default="outputs/manual_poses18.json")
    p.add_argument("--use-degrees", action="store_true")
    args = p.parse_args()

    notes = load_notes(Path(args.notes))
    cfg = SO101FollowerConfig(port=args.port, id=args.id, use_degrees=bool(args.use_degrees))
    robot = SO101Follower(cfg)
    robot.connect(calibrate=False)  # use existing calibration saved by test.py

    try:
        apply_loaded_calibration(robot)
        print("トルクをオフにします。手でアームを目的位置に合わせてください。")
        torque_off_for_teaching(robot)

        out_path = Path(args.out)
        out: List[Dict[str, Any]] = []
        if out_path.exists():
            try:
                out = json.loads(out_path.read_text(encoding="utf-8"))
            except Exception:
                out = []

        idx = 0
        while True:
            idx += 1
            label = notes[idx-1] if idx-1 < len(notes) else f"pose_{idx:02d}"
            print(f"\n[{idx}] '{label}' にアームを手で合わせて Enter を押してください ('s' スキップ, 'q' 終了)")
            cmd = input("> ").strip().lower()
            if cmd == "q":
                print("終了します。")
                break
            if cmd == "s":
                print("スキップ")
                continue

            try:
                obs = robot.get_observation()
            except Exception as e:
                print("観測取得失敗:", e)
                obs = {}

            motors = extract_motors(obs)
            rec = {"i": idx, "note": label, "timestamp": time.time(), "motors": motors}
            out.append(rec)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
            print(f"保存: {out_path} (最新: {label})")
    finally:
        print("記録終了。トルクを戻して切断します。")
        torque_on_after(robot)
        try:
            robot.disconnect()
        except Exception:
            pass

if __name__ == "__main__":
    main()