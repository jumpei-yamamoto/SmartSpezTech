import logging
from openai import AsyncOpenAI
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def create_screen_list(answers):
    prompt = f"""
以下のプロジェクト要件に基づいて、想定される主要な画面の一覧を作成してください。
各画面名を簡潔に記述し、最大10個までのリストとして返してください。

プロジェクト要件:
{answers}
"""

    logger.info("Sending request to OpenAI for create_screen_list with prompt: %s", prompt)
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはUIデザインの専門家です。主要な画面のみをリストアップしてください。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info("Received response from OpenAI for create_screen_list: %s", response)

    screen_list = response.choices[0].message.content.strip().split("\n")
    return [screen.strip("- ").strip() for screen in screen_list if screen]

async def estimate_total_workload(answers):
    prompt = f"""
以下のプロジェクト要件に基づいて、全体の工数見積もりの概要を作成してください。
各フェーズ（要件定義、設計、開発、テスト）の大まかな工数と合計を人日で表してください。

プロジェクト要件:
{answers}
"""

    logger.info("Sending request to OpenAI for estimate_total_workload with prompt: %s", prompt)
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはプロジェクトマネージャーです。大まかな工数見積もりを提供してください。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info("Received response from OpenAI for estimate_total_workload: %s", response)

    return response.choices[0].message.content.strip()

async def get_screen_details(screen, answers):
    workload = await estimate_screen_workload(screen, answers)
    basic_design = await create_basic_design(screen, answers)
    screen_sample = await create_screen_sample(screen, answers)

    return {
        "workload": workload,
        "basic_design": basic_design,
        "screen_sample": screen_sample
    }

async def estimate_screen_workload(screen, answers):
    prompt = f"""
以下の画面と全体のプロジェクト要件に基づいて、この画面の開発工数を見積もってください。
工数は人日で表してください。

画面名: {screen}
プロジェクト要件:
{answers}
"""

    logger.info("Sending request to OpenAI for estimate_screen_workload with prompt: %s", prompt)
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはプロジェクトマネージャーです。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info("Received response from OpenAI for estimate_screen_workload: %s", response)

    return response.choices[0].message.content.strip()

async def create_basic_design(screen, answers):
    template_path = os.path.join(os.path.dirname(__file__), "..", "..", "template", "Basic_Design_Specification.md")
    with open(template_path, "r", encoding='utf-8') as f:
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

    logger.info("Sending request to OpenAI for create_basic_design with prompt: %s", prompt)
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはシステム設計の専門家です。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info("Received response from OpenAI for create_basic_design: %s", response)

    return response.choices[0].message.content.strip()

async def create_screen_sample(screen, answers):
    prompt = f"""
    以下の画面と全体のプロジェクト要件に基づいて、この画面のサンプルデザインをHTMLとTailwind CSSで作成してください。
    必要に応じてJavaScriptも含めてください。
    コードは一つのコードブロックで提供してください。

    画面名: {screen}
    プロジェクト要件:
    {answers}
    """

    logger.info("Sending request to OpenAI for create_screen_sample with prompt: %s", prompt)
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはUIデザイナーです。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info("Received response from OpenAI for create_screen_sample: %s", response)

    return response.choices[0].message.content.strip()

async def preview_screen_list(answers):
    prompt = f"""
以下のプロジェクト要件に基づいて、想定される主要な画面の一覧とその機能を提示してください。
各画面名を簡潔に記述し、必ず3つのリストとして返してください。

プロジェクト要件:
{answers}
"""

    logger.info("Sending request to OpenAI for preview_screen_list with prompt: %s", prompt)
    response = await aclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはWebサイトのUI/UXデザイン専門家です。必ず3つの主要な画面を提案してください。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info("Received response from OpenAI for preview_screen_list: %s", response)

    screen_list = response.choices[0].message.content.strip().split("\n")
    screen_list = [screen.strip("- ").strip() for screen in screen_list if screen]
    
    # 2つ目から4つ目の画面を取得
    screen_list = screen_list[1:4]
    
    # 必ず3つの画面を返すように調整
    if len(screen_list) > 3:
        screen_list = screen_list[:3]
    elif len(screen_list) < 3:
        screen_list.extend(["追加画面"] * (3 - len(screen_list)))
    
    return screen_list