# soundpack-generator

## 概要

このリポジトリは、AI 語りを活用して「森林」をテーマにした効果音パックを生成し、そのプレビュー動画を自動生成するツール群をまとめたものです。生成したデモ動画は YouTube にアップロード済みです。

## デモ動画

* YouTube デモ: [FOREST SOUNDS](https://www.youtube.com/watch?v=qlhQRn4cVPc)
* YouTube デモ 日本語版: [FOREST SOUNDS](https://www.youtube.com/watch?v=msS2McuqIUo)

## ディレクトリ構成

```
├── config/
│   └── config_forest.py       ← タイトル・プロンプト定義
├── assets/
│   ├── forest_bg.png          ← 背景画像
│   └── fonts/
│       └── meiryo.ttc         ← 日本語フォント
├── outputs/                   ← 生成成果物保存先（通常は .gitignore 対象）
├── generate_audio.py         ← SFX WAV 生成スクリプト
├── generate_preview_video.py ← プレビュー動画生成スクリプト
├── README.md                 ← このファイル
└── LICENSE                   ← MIT License
```

## 必要環境

* Python 3.8+
* CUDA 対応 GPU（`generate_audio.py` 実行時）
* 以下の主な依存ライブラリ

  * `torch`
  * `diffusers`
  * `moviepy`
  * `Pillow`
  * `soundfile`
  * `pydub`

## セットアップ

1. リポジトリをクローン

   ```bash
   git clone https://github.com/YourUsername/forest-soundpack-generator.git
   cd forest-soundpack-generator
   ```
2. 仮想環境の作成・有効化

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
   ```
3. 必要パッケージをインストール

   ```bash
   pip install -r requirements.txt
   ```

## 使い方

### 1. 効果音（WAV）を生成する

```bash
python generate_audio.py \
  --output-root outputs \
  --hf-token YOUR_HUGGINGFACE_TOKEN
```

* `--output-root`：成果物のルートディレクトリ（デフォルト: `./outputs`）
* `--hf-token`：Hugging Face トークン（`HUGGINGFACE_TOKEN` 環境変数でも可）

### 2. プレビュー動画を作成する

```bash
python generate_preview_video.py \
  --assets-dir assets \
  --output-dir outputs
```

* `--assets-dir`：背景画像やフォントがあるフォルダ（デフォルト: `./assets`）
* `--output-dir`：動画出力先ディレクトリ（デフォルト: `./outputs`）

## .gitignore

* `outputs/`
* `*.wav`
* `*.mp4`
* `__pycache__/`
* `.venv/`

## ライセンス

本リポジトリのコードは **MIT License** の下で公開しています。詳細は `LICENSE` ファイルをご覧ください。
