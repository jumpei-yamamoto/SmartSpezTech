import asyncio
from app.services.analysis import analyze_with_gpt, analyze_sentiment, extract_keywords
from app.services.requirements import create_system_requirements_specification, create_requirements_definition
from app.services.preview import generate_title, generate_catchphrase, generate_description, generate_preview_screen
from app.services.screen import create_screen_list, estimate_total_workload, preview_screen_list
from app.schemas.estimate import InquiryRequest
from app.database import get_db
from app.models.estimate import Estimate, Screen
import json
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
import os
import logging

aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_estimate(answers):
    tasks = [
        create_system_requirements_specification(answers),
        create_requirements_definition(answers),
        create_screen_list(answers),
        estimate_total_workload(answers),
        analyze_with_gpt(answers),
    ]
    results = await asyncio.gather(*tasks)

    requirements_specification, requirements_definition, screens, estimate_develop, gpt_analysis = results

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

async def save_inquiry_data(request: InquiryRequest):
    db: Session = next(get_db())
    try:
        new_estimate = Estimate(
            name=request.name,
            email=request.email,
            inquiry=request.message,
            answers=json.dumps(request.simulationData[0].answers)  # JSON文字列に変換
        )
        db.add(new_estimate)
        db.flush()  # IDを生成するためにflushする

        # Screenモデルを生成して保存
        for screen_data in request.simulationData:
            new_screen = Screen(
                estimate_id=new_estimate.id,
                title=screen_data.title,
                catchphrase=screen_data.catchphrase,
                description=screen_data.description,
                preview=screen_data.preview
            )
            db.add(new_screen)

        db.commit()
        db.refresh(new_estimate)
        
        logging.info("database saved check")
        # データベースから保存されたデータを再取得して確認
        saved_estimate = db.query(Estimate).filter(Estimate.id == new_estimate.id).first()
        
        if saved_estimate:
            logging.info(f"新しい見積もりがデータベースに正常に保存されました。ID: {saved_estimate.id}")
            logging.info(f"名前: {saved_estimate.name}, メール: {saved_estimate.email}")
            logging.info(f"問い合わせ内容: {saved_estimate.inquiry[:100]}...")  # 最初の100文字のみログ出力
            
            # 関連する画面情報も確認
            for screen in saved_estimate.screens:
                logging.info(f"画面情報 - タイトル: {screen.title}, キャッチフレーズ: {screen.catchphrase}")
        else:
            logging.error(f"見積もり（ID: {new_estimate.id}）のデータベースへの保存が確認できませんでした。")
        
        return new_estimate
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

async def generate_preview(answers):

    # まずはユーザーの回答から3つの主要画面を生成する
    screens = await preview_screen_list(answers)  # ここでawaitを追加
    # 生成された画面のプレビューを生成する
    results = []
    for screen in screens:
        title = await generate_title(screen)
        catchphrase = await generate_catchphrase(screen)
        description = await generate_description(screen)
        previews = await generate_preview_screen(screen)  # This should now return a list of strings
        results.append({
            "title": title,
            "catchphrase": catchphrase,
            "description": description,
            "preview": previews,  # This is now a list
            "answers": answers
        })
    

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Log the results before returning
    logger.info("Generated preview results:")
    for i, result in enumerate(results):
        logger.info(f"Screen {i + 1}:")
        logger.info(f"  Title: {result['title']}")
        logger.info(f"  Catchphrase: {result['catchphrase']}")
        logger.info(f"  Description: {result['description']}")
        logger.info(f"  Preview: {result['preview'][:100]}...")  # Log first 100 characters of preview

    return results  # Changed to return the entire results list
