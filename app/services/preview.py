import asyncio  # Add this import statement
from openai import AsyncOpenAI
import os
import logging  # Add this import statement
import random  # テンプレート選択のためにrandomをインポート
import re  # 正規表現を使用するためにインポート

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# テンプレートを読み込む関数
def load_templates():
    templates = {}
    template_dir = "app/templates"  # テンプレートファイルのディレクトリ
    for filename in os.listdir(template_dir):
        if filename.endswith(".html"):
            with open(os.path.join(template_dir, filename), "r") as file:
                templates[filename] = file.read()
    return templates

# テンプレートを選択する関数を改善
async def select_template(templates, screen_info):
    return templates.get("default.html", "")
    keyword = await extract_keywords(screen_info)
    
    for filename, content in templates.items():
        if keyword in filename.lower():
            return content
    
    # キーワードに完全一致するテンプレートがない場合はデフォルトのテンプレートを返す
    return templates.get("default.html", "")

# キーワード抽出関数を更新
async def extract_keywords(text):
    important_keywords = [
        "login", "signup", "dashboard",  "settings", "list", "detail",
        "form", "search", "report", "user", "admin", "default"
    ]
    
    prompt = f"""
    以下の画面情報から、最も適切なキーワードを1つ選択してください。
    選択肢: {', '.join(important_keywords)}

    画面情報:
    {text}

    回答は選択肢の中から1つのキーワードのみを返してください。 もし該当するキーワードがない場合は、"default"を返してください。
    """
    
    logger.info(f"Extracting keyword with prompt: {prompt}")
    response = await aclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは画面情報からキーワードを抽出する専門家です。与えられた選択肢から最も適切なキーワードを1つだけ選んでください。"},
            {"role": "user", "content": prompt}
        ]
    )
    logger.info(f"Received response: {response}")
    return response.choices[0].message.content.strip().lower()

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
    templates = load_templates()
    selected_template = await select_template(templates, screen)
    
    prompt = f"""
    以下の画面情報とHTMLテンプレートに基づいて、この画面のサンプルデザインをHTMLとTailwind CSSで作成してください。
    必要に応じてJavaScriptも含めてください。
    コードは一つのコードブロックで提供してください。
    ボタンやリンク・リストボックスなどのインタラクティブな要素は実装してください。またidをつけてください。
    全てのイベントとリンクは、JavaScriptの標準アラート(ラップはせずHTMLで直接指定)で何が実行されるかを簡潔に表示するようにしてください。
    scriptタグ内でalertを使用するとエラーになってしまいます。そのため、onclick属性を使用してください。
    例: 
    - ボタン: onclick="alert('ログイン処理が実行されます')"
    - リンク: onclick="event.preventDefault(); alert('ホームページへ遷移が実行されます')"
    説明や追加のコメントは含めず、実装のコードのみを返してください。

    画面情報: {screen}

    HTMLテンプレート:
    {selected_template}
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

