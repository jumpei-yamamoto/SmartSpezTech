import asyncio
from app.services.analysis import analyze_with_gpt, analyze_sentiment, extract_keywords
from app.services.requirements import create_system_requirements_specification, create_requirements_definition
from app.services.screen import create_screen_list, estimate_total_workload

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