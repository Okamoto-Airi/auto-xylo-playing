# アーム共通制御ラッパ

class SO101Arm:
    def __init__(self, port, calib_json):
        self.port = port
        self.calib = calib_json
        self.connect()

    def connect(self):
        print(f"Connect to {self.port}")

    def enable_teach_mode(self, enable=True):
        print("Teach mode:", enable)

    def set_torque(self, enable=True):
        print("Torque:", enable)

    def get_joint_positions(self):
        # 実機ではSDKから取得
        return {
            "shoulder_pan": 1520,
            "shoulder_lift": 2100,
            "elbow_flex": 1780,
            "wrist_flex": 1600,
            "wrist_roll": 1400,
            "gripper": 2500
        }

    def move_to(self, joints, speed="slow"):
        print("Move to:", joints, "speed:", speed)

    def move_delta(self, delta, speed="slow"):
        print("Move delta:", delta, "speed:", speed)
