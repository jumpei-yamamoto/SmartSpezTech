from openai import AsyncOpenAI
import os

aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def create_system_requirements_specification(answers):
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

    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはシステム要求仕様書の専門家です。簡潔に要点をまとめてください。"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()

async def create_requirements_definition(answers):
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

    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは要件定義の専門家です。簡潔に要点をまとめてください。"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()