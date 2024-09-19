from textblob import TextBlob
import re
from openai import AsyncOpenAI
import os

aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analyze_with_gpt(answers):
    prompt = "以下のプロジェクト評価フォームの回答を分析し、プロジェクトの強みと弱み、改善点を指摘してください:\n\n"
    for key, answer in answers.items():
        prompt += f"質問{key}: {answer}\n\n"

    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはプロジェクト評価の専門家です。"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()

def analyze_sentiment(text: str):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def extract_keywords(answers):
    texts = []
    for answer in answers.values():
        if isinstance(answer, str):
            texts.append(answer)
        elif isinstance(answer, list):
            texts.extend([str(a) for a in answer])
        else:
            texts.append(str(answer))
    text = ' '.join(texts)
    words = re.findall(r'\w+', text.lower())
    word_freq = {}
    for word in words:
        if len(word) > 1:
            word_freq[word] = word_freq.get(word, 0) + 1
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:10]]