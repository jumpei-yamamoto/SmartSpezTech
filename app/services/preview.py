import asyncio  # Add this import statement
from openai import AsyncOpenAI
import os
import logging  # Add this import statement

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_title(answer):
    prompt = f"""
    以下のプロジェクト要件に基づいて、システム開発のパンフレットのタイトルを作成してください。
    タイトルは10文字以内で簡潔に機能が分かる表現にしてください。

    プロジェクト要件:
    {answer}
    """
    logger.info(f"Generating title with prompt: {prompt}")
    response = await aclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはシステム開発の専門家で、システム発注が初めての方にも分かりやすい用語で説明することに自信を持っています。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info(f"Received response: {response}")
    return response.choices[0].message.content.strip()

async def generate_catchphrase(answer):
    prompt = f"""
    以下のプロジェクト要件に基づいて、システム開発のパンフレットのキャッチコピーを作成してください。
    キャッチコピーは20文字以内で簡潔に機能が分かる表現にしてください。

    プロジェクト要件:
    {answer}
    """
    logger.info(f"Generating catchphrase with prompt: {prompt}")
    response = await aclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはシステム開発の専門家で、システム発注が初めての方にも分かりやすい用語で説明することに自信を持っています。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info(f"Received response: {response}")
    return response.choices[0].message.content.strip()

async def generate_description(answer):
    prompt = f"""
    以下のプロジェクト要件に基づいて、システム開発のパンフレットの説明書きを作成してください。
    説明書きは100文字以内で簡潔に機能が分かる表現にしてください。

    プロジェクト要件:
    {answer}
    """
    logger.info(f"Generating description with prompt: {prompt}")
    response = await aclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはシステム開発の専門家で、システム発注が初めての方にも分かりやすい用語で説明することに自信を持っています。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info(f"Received response: {response}")
    return response.choices[0].message.content.strip()

async def generate_preview_screen(screen):
    prompt = f"""
    以下の画面情報に基づいて、この画面のサンプルデザインをHTMLとTailwind CSSで作成してください。
    必要に応じてJavaScriptも含めてください。
    コードは一つのコードブロックで提供してください。
    ボタンやリンク・リストボックスなどのインタラクティブな要素は実装してください。またidをつけてください。
    全てのイベントとリンクは、JavaScriptのアラートで何が実行されるかを簡潔に表示するようにしてください。
    例: 
    - ボタン: onclick="alert('ログイン処理が実行されます')"
    - リンク: onclick="event.preventDefault(); alert('ホームページへ遷移が実行されます')"
    説明や追加のコメントは含めず、実装のコードのみを返してください。

    画面情報: {screen}
    """
    logger.info(f"Generating preview screen with prompt: {prompt}")
    response = await aclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはフロントエンド開発の専門家かつUIデザイナーです。コードのみを提供し、説明は含めません。全てのイベントとリンクはJavaScriptのアラートで表示し、'〇〇が実行されます'という形式で記述します。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info(f"Received response: {response}")
    return response.choices[0].message.content.strip()

