from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
# エンドポイントをログに出力
logger.info(f"current database URL: {engine.url}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ロギングの設定を追加
logging.basicConfig(level=logging.INFO, encoding='utf-8')
logger = logging.getLogger(__name__)

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# アプリケーション起動時にこの関数を呼び出す
create_tables()
