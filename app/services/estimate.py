import asyncio
from app.services.analysis import analyze_with_gpt, analyze_sentiment, extract_keywords
from app.services.requirements import create_system_requirements_specification, create_requirements_definition
from app.services.preview import generate_title, generate_catchphrase, generate_description, generate_preview_screen
from app.services.screen import create_screen_list, estimate_total_workload, preview_screen_list
from app.schemas.estimate import InquiryRequest
from app.database import get_db
from app.models.estimate import Estimate
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
    new_estimate = Estimate(
        name=request.name,
        email=request.email,
        inquiry=request.message,
        requirements_specification=request.simulationResult.requirements_specification,
        requirements_definition=request.simulationResult.requirements_definition,
        screens=json.dumps(request.simulationResult.screens),
        estimate_develop=request.simulationResult.estimate_develop,
        analysis=json.dumps(request.simulationResult.answers)
    )
    
    db: Session = next(get_db())
    try:
        db.add(new_estimate)
        db.commit()
        db.refresh(new_estimate)
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
        preview = await generate_preview_screen(screen)
        results.append({
            "title": title,
            "catchphrase": catchphrase,
            "description": description,
            "preview": preview
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
