# Followerで叩き確認
print("テストヒット開始")

# 軽く叩く
follower.move_delta({
    "shoulder_lift": -60,
    "elbow_flex": +40
}, speed="very_slow")

# すぐ戻す
follower.move_to(angles, speed="slow")
