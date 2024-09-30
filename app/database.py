import os
import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import DropTable
from sqlalchemy import text

logger = logging.getLogger(__name__)

# 環境変数から接続情報を取得
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# ログに現在の環境を出力
logger.info(f"Current ENVIRONMENT: {ENVIRONMENT}")

# 環境に応じてDATABASE_URLを設定
if ENVIRONMENT == "production":
    db_user = os.getenv("RDS_POSTGRES_USER")
    db_password = os.getenv("RDS_POSTGRES_PASSWORD")
    db_host = os.getenv("RDS_ENDPOINT")
    db_name = "mydatabase"
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
    logger.info(f"Using production database: {db_host}")
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/mydatabase")
    logger.info("Using development database")

logger.info(f"Current database URL: {DATABASE_URL}")

# SQLAlchemyエンジンの作成
engine = create_engine(DATABASE_URL)

# セッションとベースクラスの設定
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ロギングの設定を追加
logging.basicConfig(level=logging.INFO, encoding='utf-8')
logger = logging.getLogger(__name__)

# テーブル作成関数
def create_tables():
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info(f"Existing tables: {existing_tables}")

        Base.metadata.create_all(bind=engine)
        
        new_tables = set(inspector.get_table_names()) - set(existing_tables)
        if new_tables:
            logger.info(f"New tables created: {new_tables}")
        else:
            logger.info("No new tables were created. They may already exist.")

        logger.info("Table creation process completed.")
    except Exception as e:
        logger.error(f"An error occurred while creating tables: {str(e)}")

# 全てのテーブルを削除する関数
def drop_all_tables():
    logger.info("Starting to delete all tables.")
    inspector = inspect(engine)
    
    with engine.begin() as connection:
        # 外部キー制約を無効化
        connection.execute(text("SET session_replication_role = 'replica';"))
        
        # 全てのテーブルを削除
        for table_name in inspector.get_table_names():
            connection.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
        
        # 外部キー制約を再度有効化
        connection.execute(text("SET session_replication_role = 'origin';"))
    
    logger.info("全てのテーブルが削除されました。")

# データベースセッション取得関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# アプリケーション起動時にこの関数を呼び出す
create_tables()
