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

async def generate_fixed_preview(answers):
    print("Generating fixed preview...")
    result = []
    html_template = ""
    screen_description = ""

    # 質問1と質問2の回答を取得
    q1_answer = answers.get("1", "")
    q2_answer = answers.get("2", "")
    print(f"Q1: {q1_answer}, Q2: {q2_answer}")

    # HTMLテンプレートと画面説明ファイルの選択
    template_name = ""
    description_file_name = ""

    if q1_answer == "社内業務の効率化":
        if "データ入力・管理" in q2_answer:
            template_name = "pattern1.html"
            description_file_name = "description1.txt"
        elif "レポート作成" in q2_answer:
            template_name = "pattern2.html"
            description_file_name = "description2.txt"
        elif "スケジュール管理" in q2_answer:
            template_name = "pattern3.html"
            description_file_name = "description3.txt"
    elif q1_answer == "顧客サービスの向上":
        if "データ入力・管理" in q2_answer:
            template_name = "pattern4.html"
            description_file_name = "description4.txt"
        elif "レポート作成" in q2_answer:
            template_name = "pattern5.html"
            description_file_name = "description5.txt"
        elif "スケジュール管理" in q2_answer:
            template_name = "pattern6.html"
            description_file_name = "description6.txt"
    elif q1_answer == "売上・利益の増加":
        if "データ入力・管理" in q2_answer:
            template_name = "pattern7.html"
            description_file_name = "description7.txt"
        elif "レポート作成" in q2_answer:
            template_name = "pattern8.html"
            description_file_name = "description8.txt"
        elif "スケジュール管理" in q2_answer:
            template_name = "pattern9.html"
            description_file_name = "description9.txt"

    # テンプレートファイルの読み込み
    print(template_name)

    if template_name:
        template_path = os.path.join("app", "fixed_templates", template_name)
        try:
            with open(template_path, "r", encoding="utf-8") as file:
                html_template = file.read()
        except FileNotFoundError:
            print(f"Template file not found: {template_path}")

    # 画面説明ファイルの読み込み
    print(description_file_name)

    if description_file_name:
        description_path = os.path.join("app", "fixed_descriptions", description_file_name)
        try:
            with open(description_path, "r", encoding="utf-8") as file:
                screen_description = file.read()
        except FileNotFoundError:
            print(f"Description file not found: {description_path}")

    # 質問1の処理
    q1_proposal = ""
    if q1_answer == "社内業務の効率化":
        q1_proposal = "業務プロセスを自動化するワークフローシステムの導入を検討されてみてはいかがでしょうか。"
    elif q1_answer == "顧客サービスの向上":
        q1_proposal = "チャットボットやFAQシステムで迅速な顧客対応を実現を検討されてみてはいかがでしょうか。"
    elif q1_answer == "売上・利益の増加":
        q1_proposal = "データ分析ツールの導入で市場動向を把握検討をされてみてはいかがでしょうか。"
    result.append(f"お客様の回答: {q1_answer}\n提案内容: {q1_proposal}")

    # 質問2の処理
    q2_proposal = "主な機能として、"
    if "データ入力・管理" in q2_answer:
        q2_proposal += "データインポート/エクスポート機能の追加"
    elif "レポート作成" in q2_answer:
        q2_proposal += "レポート自動生成機能で定期的な報告を効率化"
    elif "スケジュール管理" in q2_answer:
        q2_proposal += "カレンダー機能でタスクやイベントを可視化"
    q2_proposal = q2_proposal + "を実装します。"
    result.append(f"お客様の回答: {q2_answer}\n 提案内容: {q2_proposal}")

    # 質問3の処理
    q3_answer = answers.get("3", "")
    q3_proposal = ""
    if q3_answer == "必要":
        q3_proposal = "画面操作機能を実装します。"
    elif q3_answer == "不要":
        q3_proposal = "画面操作機能は実装しません。"
    elif q3_answer == "分からない":
        q3_proposal = "画面操作機能の必要性については要検討です。"
    result.append(f"お客様の回答: {q3_answer}\n提案内容: {q3_proposal}")

    # 質問4の処理
    q4_answer = answers.get("4", "")
    q4_proposal = ""
    if "顧客情報" in q4_answer:
        q4_proposal = "個人情報保護を考慮したデータ管理を目指します。"
    elif "売上データ" in q4_answer:
        q4_proposal = "売上予測機能でビジネス戦略をサポートします。"
    elif "在庫情報" in q4_answer:
        q4_proposal = "在庫分析で需要予測を精緻化します。"
    elif "スケジュール" in q4_answer:
        q4_proposal = "リソース配分を最適化するスケジューリングを目指します。"
    elif "文書ファイル" in q4_answer:
        q4_proposal = "文書管理システムでファイルを一元化します。"
    elif "その他" in q4_answer:
        q4_proposal = "取り扱うデータの具体例を伺い適切なシステム開発を目指します。"
    result.append(f"お客様の回答: {q4_answer}\n提案内容: {q4_proposal}")

    # 質問5の処理
    q5_answer = answers.get("5", "")
    q5_proposal = ""
    if q5_answer == "必要ない":
        q5_proposal = "既存のシステムとの連携は行いません。"
    elif q5_answer == "一部連携が必要":
        q5_proposal = "既存のシステムと一部連携を行います。"
    elif q5_answer == "全的に連携が必要":
        q5_proposal = "既存のシステムと全面的に連携を行います。"
    elif q5_answer == "わからない":
        q5_proposal = "既存のシステムとの連携については要検討です。"
    result.append(f"お客様の回答: {q5_answer}\n提案内容: {q5_proposal}")

    # 質問6の処理
    q6_answer = answers.get("6", "")
    q6_proposal = ""
    if q6_answer == "一般的なレベルで十分":
        q6_proposal = "セキュリティは一般的なレベルで実装します。"
    elif q6_answer == "やや高度なセキュリティが必要":
        q6_proposal = "やや高度なセキュリティ対策を実装します。"
    elif q6_answer == "非常に高度なセキュリティが必須":
        q6_proposal = "非常に高度なセキュリティ対策を実装します。"
    elif q6_answer == "わからない":
        q6_proposal = "セキュリティレベルについては要検討です。"
    result.append(f"お客様の回答: {q6_answer}\n提案内容: {q6_proposal}")

    # 質問7の処理
    q7_answer = answers.get("7", "")
    q7_proposal = ""
    if q7_answer == "必要ない":
        q7_proposal = "システムの引き渡し後は自社での運用をお願いいたします。"
    elif q7_answer == "軽度のサポート（問い合わせ対応程度）":
        q7_proposal = "システム導入後、問い合わせ対応程度の軽度のサポートを提供します。"
    elif q7_answer == "中程度のサポート（定期的なメンテナンス含む）":
        q7_proposal = "システム導入後、定期的なメンテナンスを含む中程度のサポートを提供します。"
    elif q7_answer == "手厚いサポート（運用代行も含む）":
        q7_proposal = "システム導入後、運用代行を含む手厚いサポートを提供します。"
    elif q7_answer == "わからない":
        q7_proposal = "システム導入後のサポート内容については要検討です。"
    result.append(f"お客様の回答: {q7_answer}\n提案内容: {q7_proposal}")

    return {
        "text": "\n\n".join(result),
        "html": html_template,
        "screen_description": screen_description
    }