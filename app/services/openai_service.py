import os
import logging
from openai import AsyncOpenAI
from typing import Dict, Any
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up your OpenAI API client
aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_ai_estimate(data: Dict[Any, Any]) -> Dict[str, Any]:
    # プロンプトの修正
    prompt = f"""
    Given the following project details, provide an estimate for the workload and hourly rate of each component:

    Screens:
    {data['screens']}

    Events:
    {data['events']}

    Entities:
    {data['entities']}

    Relations:
    {data['relations']}

    Please provide the estimate in the following format:
    {{
        "screens": {{
            "画面名1": {{
                "workload": "X 日",
                "hourly_rate": "時給:Y円",
                "tests": ["test1", "test2", ...]
            }},
            "画面名2": {{
                "workload": "X 日",
                "hourly_rate": "時給:Y円",
                "tests": ["test1", "test2", ...]
            }},
            ...
        }},
        "events": {{
            "イベント名1": {{
                "workload": "X 日",
                "hourly_rate": "時給:Y円",
                "tests": ["test1", "test2", ...]
            }},
            "イベント名2": {{
                "workload": "X 日",
                "hourly_rate": "時給:Y円",
                "tests": ["test1", "test2", ...]
            }},
            ...
        }},
        "database": {{
            "workload": "X 日",
            "hourly_rate": "時給:Y円",
            "tests": ["test1", "test2", ...]
        }}
    }}

    workloadは日数で返す 開発者歴が3年程度を想定してください
    hourly_rateは難易度に応じて1000円から10000円の範囲で設定してください。難しいタスクほど高い時給になります。
    testsはテストケースをシンプルに分かりやすく返す 例: ["ログイン成功", "ログイン失敗"]
    画面名やイベント名は、提供された情報から適切な名前を付けてください。
    """

    logger.info(f"Generating AI estimate with prompt: {prompt}")

    # Call OpenAI API
    response = await aclient.chat.completions.create(
        model="gpt-4o-mini",  # Using a more recent model
        messages=[
            {"role": "system", "content": "You are an expert system architect and project estimator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
    )

    logger.info(f"Received response: {response}")

    # Parse the response and return the estimate
    json_match = re.search(r'```json\n(.*?)\n```', response.choices[0].message.content, re.DOTALL)
    if json_match:
        json_data = json_match.group(1)
        try:
            parsed_data = json.loads(json_data)
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from AI response: {str(e)}")
            raise ValueError("Invalid JSON in AI response")
    else:
        logger.error("No JSON found in AI response")
        raise ValueError("No JSON found in AI response")