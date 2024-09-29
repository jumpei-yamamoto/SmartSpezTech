import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import form, screen, estimate as estimate_router, inquiry, joblist, order_check
from app.middleware.content_security_policy import ContentSecurityPolicyMiddleware
from app.database import engine, get_db, create_tables, drop_all_tables
from app.models import estimate as estimate_model
from sqlalchemy import text

# .envファイルを読み込む
load_dotenv()

# ロギングの設定を修正
logging.basicConfig(level=logging.INFO, encoding='utf-8')
logger = logging.getLogger(__name__)

logger.info("Application imports completed")

app = FastAPI()

logger.info("FastAPI application created")

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
app.include_router(inquiry.router)  
app.include_router(joblist.router) 
app.include_router(order_check.router)  # 新しいルーターを追加

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    # 全てのテーブルを削除
    drop_all_tables()

    # テーブル作成
    create_tables()

    # データベース名を取得してログに出力
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        result = session.execute(text("SELECT current_database();"))
        database_name = result.scalar()
        logger.info(f"現在接続しているデータベース: {database_name}")

if __name__ == "__main__":
    logger.info("Main block executed")
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
