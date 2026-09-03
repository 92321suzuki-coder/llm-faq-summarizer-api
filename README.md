# LLM FAQ & Summarizer API

Python (FastAPI) と OpenAI API (`gpt-4o-mini`) を活用した、社内問い合わせ自動応答およびドキュメント要約を行うマイクロサービスAPIです。

## 主な機能
- **社内FAQ自動応答 (`/api/v1/ask`)**: 問い合わせに対して構造化された回答を生成（モック切替機能付き）。
- **ドキュメント要約 (`/api/v1/summarize`)**: 長文テキストを3行で要約。
- **Swagger UI環境**: `/docs` にてWeb上からインタラクティブに動作確認が可能。

## 技術構成
- **バックエンド**: Python 3.11 / FastAPI / Pydantic
- **AIエンジン**: OpenAI API (`gpt-4o-mini`)
- **コンテナ環境**: Docker / Docker Compose

## 起動手順
1. リポジトリのクローン
2. 環境変数の設定 (`.env` ファイルを作成)
env
OPENAI_API_KEY=your_api_key_here
3. Dockerコンテナの起動
bash
docker-compose up --build
4. 動作確認
ブラウザで `http://localhost:8000/docs` にアクセス。