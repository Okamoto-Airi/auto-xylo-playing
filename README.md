# 自動演奏ロボット

このプロジェクトは、ロボットアーム「SO-101」を使用して、卓上木琴を自動演奏させるシステムです。

LeRobotライブラリを使用し、事前に記録したアームの角度データと楽譜データ（JSON）を元に演奏を行います。

## デモ動画

実際の演奏の様子です。

[▶ デモ動画を見る](videos/prototype_demo.mp4)

## プロジェクト概要

単に座標をなぞるだけでなく、**「音を鳴らす位置（ON）」** と **「音を鳴らした後の待機位置（OFF）」** を個別に制御することで、安定した演奏を実現しています。

### 主な機能

* **ティーチングモード**: アームを手で動かして、各鍵盤の正確な座標を記録。
* **JSON楽譜対応**: 音階と音価を記述したJSONファイルを読み込んで演奏。
* **スムーズな演奏制御**: BPM制御、打鍵の強さ（ホールド時間）、音程差が大きい時の予備動作などを実装。

## 技術スタック

* **プログラミング言語**: Python 3.x
* **ハードウェア**: SO-101 Robot Arm
* **ライブラリ**: [Hugging Face LeRobot](https://github.com/huggingface/lerobot)
* **フォーマット**: JSON (アームの姿勢 & 楽譜)

## ディレクトリ構造

```text
.
├── output_json.py        # ティーチング用スクリプト（手動で動かしてアームの各関節の角度データを保存）
├── play_music.py         # 自動演奏のメインスクリプト
├── test_move.py          # 記録した座標の動作確認用スクリプト
├── score.json            # 楽譜データ
├── notes_poses.json      # 打鍵位置のデータ
├── notes_poses_off.json  # 待機位置のデータ
└── .gitignore

```

## セットアップ手順

### 1. 開発環境の構築

Python環境とLeRobotライブラリが必要です。

LeRobot公式リポジトリ：<https://github.com/huggingface/lerobot>

SO-101ドキュメント：<https://huggingface.co/docs/lerobot/so101>

```bash
# 仮想環境の作成
python3 -m venv venv
source venv/bin/activate

# LeRobotのインストール（公式の手順に従ってください）
# 例:
pip install lerobot
```

### 2. 環境変数・設定値

各スクリプト内の定数で設定します。環境に合わせて書き換えてください。

| ファイル | 変数名 | デフォルト値 | 説明 |
| --- | --- | --- | --- |
| `play_music.py` | `PORT` | `/dev/ttyACM0` | ロボットのシリアルポート |
| `play_music.py` | `ROBOT_ID` | `my_awesome_...` | LeRobot設定時のロボットID |
| `score.json` | `bpm` | `60` | 演奏のテンポ |

## 使用方法

### Step 1: 座標のティーチング (Teaching)

卓上木琴の各鍵盤の「打鍵位置」と「離す位置」の2種類を記録します。

**A. 打鍵位置の記録**

```bash
# アームのトルクが切れるので、実行前に手で記録する鍵盤の位置に合わせてEnterを押す
python output_json.py
```

**B. リフト（OFF）位置の記録**

```bash
# 鍵盤から少し浮かせた位置を記録する
python output_json.py
```

**C. 取得したデータを整形する**

A：`notes_poses.json`, B：`notes_poses_off.json`それぞれの構造に合うように取得したアームの角度データを書き換える。

### Step 2: 動作テスト (Test)

記録した座標が正しいか確認します。

```bash
python test_move.py
```

### Step 3: 自動演奏 (Play)

楽譜ファイル (`score.json`) を読み込んで演奏を開始します。

```bash
python play_music.py
```

## トラブルシューティング

**Q. `Permission denied: '/dev/ttyACM0'` と出る**

A. ユーザーにシリアルポートへのアクセス権限がありません。以下のコマンドを実行して再ログインしてください。

```bash
sudo usermod -a -G dialout $USER
```

**Q. アームが予期しない方向に動く**

A. `notes_poses.json` の中身を確認し、異常な数値（例: 他と桁が違う角度など）がないか確認してください。必要であれば `output_json.py` で再記録してください。

**Q. 音が鳴らない（空振りする）**

A. `output_json.py` で記録する際、少し強めに鍵盤に押し当てた位置で記録するか、楽器の位置を微調整してください。
