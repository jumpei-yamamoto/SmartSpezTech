import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import form, screen
from app.routers import estimate as estimate_router
from app.middleware.content_security_policy import ContentSecurityPolicyMiddleware
from app.database import engine, get_db, create_tables
from app.models import estimate as estimate_model

# .envファイルを読み込む
load_dotenv()

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# モデルに基づいてテーブルを作成
# estimate_model.Base.metadata.create_all(bind=engine)

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

# Content-Security-Policy ミドルウェアを追加
app.add_middleware(ContentSecurityPolicyMiddleware)

# ルーターを追加
app.include_router(form.router)
app.include_router(estimate_router.router)
app.include_router(screen.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    logger.info("アプリケーションの起動を開始します。")
    create_tables()
    logger.info("アプリケーションの起動が完了しました。")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
