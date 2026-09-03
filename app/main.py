import os
import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
# 動作モード切替フラグ
# True : パターンB（OpenAI APIを呼ばず、ローカルでテスト用ダミー応答を返す）
# False: パターンA（実際のOpenAI APIを呼び出す。APIクレジット残高が必要）
# ==============================================================================
USE_MOCK = True

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(
    title="LLM FAQ & Summarizer API",
    description="社内FAQ自動応答およびテキスト要約API",
    version="1.0.0"
)

# パターンA（本番通信）用のOpenAIクライアント初期化
client = None
if not USE_MOCK:
    http_client = httpx.Client()
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        http_client=http_client
    )


class AskRequest(BaseModel):
    question: str = Field(..., example="有給休暇の申請手順を教えてください。")


class SummarizeRequest(BaseModel):
    text: str = Field(
        ...,
        example="当社では年次有給休暇を取得する際、原則として取得日の3日前までに申請を出さなければなりません..."
    )


class AIResponse(BaseModel):
    result: str
    model_used: str


@app.get("/")
def read_root():
    mode_text = "MOCK Mode" if USE_MOCK else "OpenAI API Mode"
    return {"status": "ok", "message": f"API Service is running ({mode_text})"}


@app.post("/api/v1/ask", response_model=AIResponse, summary="社内FAQ回答生成")
def ask_faq(payload: AskRequest):
    # パターンB: モック応答（API残高がない場合・開発テスト用）
    if USE_MOCK:
        mock_result = (
            f"【自動回答（モック）】「{payload.question}」について：\n"
            "1. 社内ポータルサイト（ワークフローシステム）へログインしてください。\n"
            "2. 「各種申請」メニューから「有給休暇申請」を選択します。\n"
            "3. 取得希望日と理由を入力し、直属の上司へ提出してください。"
        )
        return AIResponse(
            result=mock_result,
            model_used="gpt-4o-mini (mock)"
        )

    # パターンA: OpenAI API 呼び出し
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは優秀な社内ヘルプデスクアシスタントです。質問に対して簡潔かつ分かりやすく箇条書きを交えて回答してください。"
                },
                {"role": "user", "content": payload.question}
            ],
            temperature=0.3,
        )
        return AIResponse(
            result=response.choices[0].message.content,
            model_used="gpt-4o-mini"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/summarize", response_model=AIResponse, summary="ドキュメント要約")
def summarize_text(payload: SummarizeRequest):
    # パターンB: モック応答（API残高がない場合・開発テスト用）
    if USE_MOCK:
        mock_result = (
            "【要約結果（モック）】\n"
            "・有給休暇は取得日の3日前までに事前申請が必要\n"
            "・社内ワークフローシステムから申請を行うこと\n"
            "・緊急時を除き事後申請は認められない"
        )
        return AIResponse(
            result=mock_result,
            model_used="gpt-4o-mini (mock)"
        )

    # パターンA: OpenAI API 呼び出し
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "与えられたテキストの要点を3行の箇条書きで要約してください。"
                },
                {"role": "user", "content": payload.text}
            ],
            temperature=0.2,
        )
        return AIResponse(
            result=response.choices[0].message.content,
            model_used="gpt-4o-mini"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))