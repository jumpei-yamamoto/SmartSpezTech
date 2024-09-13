import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from fastapi.middleware.cors import CORSMiddleware
import re
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
from openai import AsyncOpenAI

aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from textblob import TextBlob

# .envファイルを読み込む
load_dotenv()

# OpenAI APIキーの設定

# ロギングの設定
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORSミドルウェアの設定
origins = [
    "https://dov1dxiwhcjvd.cloudfront.net",  # CloudFrontのドメイン
    "https://d3uk2ucdyrom6m.cloudfront.net",  # Elastic BeanstalkのCloudFrontドメイン
    "http://localhost:3000",  # ローカル開発用
    "http://smartspeztech.eba-kam3e43r.ap-northeast-3.elasticbeanstalk.com",  # Elastic Beanstalkのドメイン
    "https://smartspeztech.com",  # 新しいカスタムドメイン
    "https://www.smartspeztech.com"  # www付きのカスタムドメイン（必要な場合）
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Content-Security-Policy ヘッダーを追加するカスタムミドルウェア
class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' https://smartspeztech.com https://*.cloudfront.net http: https:;"
        return response

# ミドルウェアを追加
app.add_middleware(ContentSecurityPolicyMiddleware)

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

class EstimateRequest(BaseModel):
    answers: Dict[str, Any]

@app.post("/estimate")
async def estimate(request: EstimateRequest):
    try:
        answers = request.answers

        # 非同期で並行して処理を実行
        tasks = [
            create_system_requirements_specification(answers),
            create_requirements_definition(answers),
            create_screen_list(answers),
            estimate_total_workload(answers),
            analyze_with_gpt(answers),  # 分析を追加
        ]
        results = await asyncio.gather(*tasks)

        requirements_specification = results[0]
        requirements_definition = results[1]
        screens = results[2]
        estimate_develop = results[3]
        gpt_analysis = results[4]

        # 感情分析とキーワード抽出
        sentiment_scores = [analyze_sentiment(str(answer)) for answer in answers.values() if isinstance(answer, str)]
        keywords = extract_keywords(answers)

        combined_analysis = f"""
GPTによる分析:
{gpt_analysis}

感情分析スコア:
{', '.join([f'{score:.2f}' for score in sentiment_scores])}

抽出されたキーワード:
{', '.join(keywords)}
"""

        return {
            "requirements_specification": requirements_specification,
            "requirements_definition": requirements_definition,
            "screens": screens,
            "estimate_develop": estimate_develop,
            "analysis": combined_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hello World"}

async def analyze_with_gpt(answers: Dict[str, Any]):
    prompt = "以下のプロジェクト評価フォームの回答を分析し、プロジェクトの強みと弱み、改善点を指摘してください:\n\n"
    for key, answer in answers.items():
        prompt += f"質問{key}: {answer}\n\n"

    response = await aclient.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "あなたはプロジェクト評価の専門家です。"},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content.strip()

def analyze_sentiment(text: str):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def extract_keywords(answers: Dict[str, Any]):
    texts = []
    for answer in answers.values():
        if isinstance(answer, str):
            texts.append(answer)
        elif isinstance(answer, list):
            texts.extend([str(a) for a in answer])
        else:
            texts.append(str(answer))
    text = ' '.join(texts)
    words = re.findall(r'\w+', text.lower())
    word_freq = {}
    for word in words:
        if len(word) > 1:
            word_freq[word] = word_freq.get(word, 0) + 1
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:10]]

async def create_system_requirements_specification(answers: Dict[str, Any]) -> str:
    with open("template/System_Requirements_Specification.md", "r", encoding='utf-8') as f:
        template = f.read()
    prompt = f"""
以下のプロジェクト要件に基づいて、システム要求仕様書の概要を作成してください。
詳細は省略し、主要なポイントのみを簡潔に記述してください。

プロジェクト要件:
{answers}

テンプレート:
{template}
"""

    response = await aclient.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "あなたはシステム要求仕様書の専門家です。簡潔に要点をまとめてください。"},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content.strip()

async def create_requirements_definition(answers: Dict[str, Any]) -> str:
    with open("template/Requirements_Definition.md", "r", encoding='utf-8') as f:
        template = f.read()
    prompt = f"""
以下のプロジェクト要件に基づいて、要件定義書の概要を作成してください。
詳細は省略し、主要なポイントのみを簡潔に記述してください。

プロジェクト要件:
{answers}

テンプレート:
{template}
"""

    response = await aclient.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "あなたは要件定義の専門家です。簡潔に要点をまとめてください。"},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content.strip()

async def create_screen_list(answers: Dict[str, Any]) -> List[str]:
    prompt = f"""
以下のプロジェクト要件に基づいて、想定される主要な画面の一覧を作成してください。
各画面名を簡潔に記述し、最大10個までのリストとして返してください。

プロジェクト要件:
{answers}
"""

    response = await aclient.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "あなたはUIデザインの専門家です。主要な画面のみをリストアップしてください。"},
        {"role": "user", "content": prompt}
    ])

    screen_list = response.choices[0].message.content.strip().split("\n")
    return [screen.strip("- ").strip() for screen in screen_list if screen]

async def estimate_total_workload(answers: Dict[str, Any]) -> str:
    prompt = f"""
以下のプロジェクト要件に基づいて、全体の工数見積もりの概要を作成してください。
各フェーズ（要件定義、設計、開発、テスト）の大まかな工数と合計を人日で表してください。

プロジェクト要件:
{answers}
"""

    response = await aclient.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "あなたはプロジェクトマネージャーです。大まかな工数見積もりを提供してください。"},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content.strip()

class ScreenDetailsRequest(BaseModel):
    screen: str
    answers: Dict[str, Any]

@app.post("/screen_details")
async def get_screen_details(request: ScreenDetailsRequest):
    try:
        workload = await estimate_screen_workload(request.screen, request.answers)
        basic_design = await create_basic_design(request.screen, request.answers)
        screen_sample = await create_screen_sample(request.screen, request.answers)

        return {
            "workload": workload,
            "basic_design": basic_design,
            "screen_sample": screen_sample
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def estimate_screen_workload(screen: str, answers: Dict[str, Any]) -> str:
    prompt = f"""
以下の画面と全体のプロジェクト要件に基づいて、この画面の開発工数を見積もってください。
工数は人日で表してください。

画面名: {screen}
プロジェクト要件:
{answers}
"""

    response = await aclient.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "あなたはプロジェクトマネージャーです。"},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content.strip()

async def create_basic_design(screen: str, answers: Dict[str, Any]) -> str:
    with open("template/Basic_Design_Specification.md", "r", encoding='utf-8') as f:
        template = f.read()
    prompt = f"""
以下の画面と全体のプロジェクト要件に基づいて、この画面の基本設計を作成してください。
テンプレートに従って、各セクションを適切に埋めてください。

画面名: {screen}
プロジェクト要件:
{answers}

テンプレート:
{template}
"""

    response = await aclient.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "あなたはシステム設計の専門家です。"},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content.strip()

async def create_screen_sample(screen: str, answers: Dict[str, Any]) -> str:
    prompt = f"""
    以下の画面と全体のプロジェクト要件に基づいて、この画面のサンプルデザインをHTMLとTailwind CSSで作成してください。
    必要に応じてJavaScriptも含めてください。
    コードは一つのコードブロックで提供してください。

    画面名: {screen}
    プロジェクト要件:
    {answers}
    """

    response = await aclient.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "あなたはUIデザイナーです。"},
        {"role": "user", "content": prompt}
    ])

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
