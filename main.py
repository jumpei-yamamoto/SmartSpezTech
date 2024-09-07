import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
import uuid
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from textblob import TextBlob
import re
import debugpy
import asyncio

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from textblob import TextBlob
import re
import debugpy

# .envファイルを読み込む
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)



app = FastAPI() 

# ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# @app.middleware("http")
# async def validate_host(request, call_next):
#     host = request.headers.get("host")
#     if host not in ALLOWED_HOSTS:
#         raise HTTPException(status_code=400, detail="Invalid host")
#     response = await call_next(request)
#     return response

# CORSミドルウェアを追加
origins = [
    "https://dov1dxiwhcjvd.cloudfront.net",
    "https://smartspeztech.s3-website-ap-northeast-3.amazonaws.com",
    "http://smartspeztech.s3-website-ap-northeast-3.amazonaws.com",
    "https://smartspeztech.eba-kam3e43r.ap-northeast-3.elasticbeanstalk.com"  # この行を追加

]

if os.environ.get("ENVIRONMENT") == "development":
    origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI APIキーを.envファイルから読み込む

# インメモリデータストア（本番環境では適切なデータベースを使用してください）
forms = {}

class Form(BaseModel):
    id: str = None
    answers: List[str]

@app.post("/save")
async def save_form(form: Form):
    if form.id and form.id in forms:
        forms[form.id] = form.answers
    else:
        new_id = str(uuid.uuid4())
        forms[new_id] = form.answers
        form.id = new_id
    return {"id": form.id}

@app.get("/load/{form_id}")
async def load_form(form_id: str):
    if form_id in forms:
        return {"answers": forms[form_id]}
    else:
        raise HTTPException(status_code=404, detail="Form not found")

class AnalyzeRequest(BaseModel):
    answers: List[str]

# @app.post("/analyze")
# async def analyze_form(request: AnalyzeRequest):
#     logger.info(f"Received analysis request with {len(request.answers)} answers")
#     try:
#         # Your analysis logic here
#         # For example:
#         analysis = "This is a placeholder analysis"
#         logger.info("Analysis completed successfully")
#         return {"analysis": analysis}
#     except Exception as e:
#         logger.error(f"An error occurred during analysis: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_form(form: Form, background_tasks: BackgroundTasks):
    # タスクIDを生成
    task_id = str(uuid.uuid4())
    
    # バックグラウンドタスクとして分析を実行
    background_tasks.add_task(perform_analysis, task_id, form.answers)
    
    # 即座にタスクIDを返す
    return {"task_id": task_id, "status": "processing"}

@app.get("/analysis_result/{task_id}")
async def get_analysis_result(task_id: str):
    # 結果を取得する処理（この例では単純化のため、グローバル変数を使用）
    if task_id in analysis_results:
        return {"status": "complete", "result": analysis_results[task_id]}
    else:
        return {"status": "processing"}

# グローバル変数で結果を保持（実際の実装では、データベースなどを使用すべき）
analysis_results = {}

async def perform_analysis(task_id: str, answers: List[str]):
    # 既存の分析ロジック
    gpt_analysis = await analyze_with_gpt(answers)
    sentiment_scores = [analyze_sentiment(answer) for answer in answers]
    keywords = extract_keywords(answers)

    combined_analysis = f"""
    GPTによる分析:
    {gpt_analysis}
    
    感情分析スコア:
    {', '.join([f'{score:.2f}' for score in sentiment_scores])}
    
    抽出されたキーワード:
    {', '.join(keywords)}
    """

    # 結果を保存
    analysis_results[task_id] = combined_analysis

@app.get("/")
async def root():
    return {"message": "Hello World"}

async def analyze_with_gpt(answers: List[str]):
    prompt = f"以下のプロジェクト評価フォームの回答を分析し、プロジェクトの強みと弱み、改善点を指摘してください:\n\n"
    for i, answer in enumerate(answers):
        prompt += f"質問{i+1}: {answer}\n\n"

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # GPT-4o-miniモデルを使用
        messages=[
            {"role": "system", "content": "あなたはプロジェクト評価の専門家です。"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def analyze_sentiment(text: str):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def extract_keywords(answers: List[str]):
    text = ' '.join(answers)
    words = re.findall(r'\w+', text.lower())
    word_freq = {}
    for word in words:
        if len(word) > 1:
            word_freq[word] = word_freq.get(word, 0) + 1
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:10]]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 80))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)