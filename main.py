import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

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

# CORSミドルウェアを追加
origins = [
    "https://dov1dxiwhcjvd.cloudfront.net/.cloudfront.net",
    "https://smartspeztech.s3-website-ap-northeast-3.amazonaws.com",
    "http://smartspeztech.s3-website-ap-northeast-3.amazonaws.com"
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
async def analyze_form(form: Form):

    # OpenAI GPT-3を使用した分析
    gpt_analysis = await analyze_with_gpt(form.answers)

    # テキスト分析（感情分析とキーワード抽出）
    sentiment_scores = [analyze_sentiment(answer) for answer in form.answers]
    keywords = extract_keywords(form.answers)

    # 分析結果の組み合わせ
    combined_analysis = f"""
    GPTによる分析:
    {gpt_analysis}
    
    感情分析スコア:
    {', '.join([f'{score:.2f}' for score in sentiment_scores])}
    
    抽出されたキーワード:
    {', '.join(keywords)}
    """

    return {"analysis": combined_analysis}

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)