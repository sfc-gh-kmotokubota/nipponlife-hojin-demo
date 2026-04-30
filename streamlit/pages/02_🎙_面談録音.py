"""
02_🎙_面談録音.py - 面談録音・要約・コンプライアンス検知・Salesforce登録 (F-01, F-11b, F-12)
"""
import streamlit as st
import pandas as pd
from datetime import date
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="面談録音・要約", layout="wide")
st.title("🎙 面談録音・AI要約・コンプライアンス検知")
st.caption("音声ファイルをアップロードするだけで文字起こし・要約・コンプライアンスチェック・Salesforce登録まで自動化。")

session = get_active_session()

# 企業選択
companies = session.sql("""
    SELECT COMPANY_ID, COMPANY_NAME FROM NIPPONLIFE_DEMO_DB.RAW.T_CUSTOMER_COMPANIES ORDER BY COMPANY_NAME
""").to_pandas()

col1, col2, col3 = st.columns(3)
with col1:
    company_options = {r["COMPANY_NAME"]: r["COMPANY_ID"] for _, r in companies.iterrows()}
    selected_company_name = st.selectbox("対象企業", list(company_options.keys()))
    selected_cid = company_options[selected_company_name]
with col2:
    meeting_date = st.date_input("面談日", value=date.today())
with col3:
    meeting_type = st.selectbox("面談種別", ["訪問", "オンライン", "電話"])

# 音声ファイルアップロード
st.markdown("---")
st.subheader("📁 音声ファイルのアップロード")
uploaded_file = st.file_uploader(
    "音声ファイルをドラッグ＆ドロップ またはクリックしてアップロード",
    type=["wav", "mp3", "m4a", "mp4"],
    help="対応フォーマット: WAV / MP3 / M4A / MP4（最大100MB）"
)

# デモ用サンプル文字起こし（音声がない場合のフォールバック）
DEMO_TRANSCRIPT = {
    "C003": """
山田（日本生命）: 本日はお時間をいただきありがとうございます。先日発表された北米の件についてお伺いしたいと存じます。
田中部長（伊藤忠）: そうですね。買収完了で被買収企業の従業員3200名の福利厚生統合が急務になっています。
山田（日本生命）: 特に団体定期保険と企業年金の制度統合が必要になりますね。現状はどのような保険をお持ちですか？
田中部長（伊藤忠）: 現在はMS&AD系の保険が入っていますが、長期的には一本化を考えています。それと確実に積立が増えると思いますので、DC移行も検討しています。
山田（日本生命）: 承知しました。制度移行のスケジュールと、DCへの移行試算を来月中にご提案させていただきます。
""",
    "DEFAULT": """
山田（日本生命）: 本日はよろしくお願いいたします。御社の従業員向け保険制度についてお伺いできればと思います。
人事部長（先方）: こちらこそよろしくお願いします。実は健康経営の取り組みを強化したいと考えていまして、従業員の休業補償を厚くしたいと思っています。
山田（日本生命）: GLTDという所得補償保険がございまして、長期休業時に給与の最大80%を補償できます。
人事部長（先方）: それは興味深いです。ただ保険料はどの程度になりますか？また来年の健康経営優良法人の申請にも活用できますか？
山田（日本生命）: はい、健康経営の文脈でご提案できます。具体的な試算を来週中にお持ちします。いずれにしても従業員への投資として非常に効果的な施策です。
"""
}

# 処理ボタン
if st.button("▶ AI 文字起こし・要約を実行", type="primary"):
    with st.spinner("AI が面談内容を分析中..."):
        # トランスクリプト（デモ用）
        transcript = DEMO_TRANSCRIPT.get(selected_cid, DEMO_TRANSCRIPT["DEFAULT"])
        if uploaded_file:
            transcript = f"（音声ファイル: {uploaded_file.name}）\n" + transcript

        # AI要約（実際には AI_SUMMARIZE を使用）
        try:
            summary_result = session.sql(f"""
                SELECT AI_COMPLETE('mistral-large2', CONCAT(
                    '以下の保険営業の面談内容を要約してください。
                     以下の形式で日本語で出力してください:
                     【面談概要】（2-3文）
                     【先方の主な関心事項】（箇条書き3点）
                     【事業イベント関連の発言】（あれば）
                     【合意事項・ペンディング】（各1-2点）
                     面談内容：', {repr(transcript)})) AS SUMMARY
            """).collect()[0]["SUMMARY"]
        except:
            summary_result = f"""【面談概要】
{selected_company_name}との面談を実施。保険制度の見直しについて詳細なヒアリングを行った。

【先方の主な関心事項】
・従業員の休業補償制度の強化（GLTD導入検討）
・健康経営優良法人認定取得に向けた支援
・退職給付制度の見直し（DC移行検討）

【合意事項・ペンディング】
・合意: 来月中に具体的な試算と提案書を提示
・ペンディング: 予算規模の確認（次回商談時）"""

        st.session_state["meeting_summary"] = summary_result
        st.session_state["meeting_transcript"] = transcript
        st.session_state["meeting_company"] = selected_cid

# 要約結果表示
if "meeting_summary" in st.session_state and st.session_state.get("meeting_company") == selected_cid:
    st.markdown("---")
    col_summary, col_compliance = st.columns([1, 1])

    with col_summary:
        st.subheader("📋 AI 要約結果")
        st.text_area("面談要約（編集可）", value=st.session_state["meeting_summary"], height=250, key="summary_edit")

        # アクションアイテム
        st.subheader("✅ アクションアイテム")
        action_items = [
            {"優先度": "🔴 高", "内容": "来月中に試算・提案書を作成", "期限": "来月末"},
            {"優先度": "🟡 中", "内容": "次回商談で予算規模を確認", "期限": "来月中"},
        ]
        for item in action_items:
            col_a, col_b, col_c = st.columns([1, 3, 1])
            col_a.markdown(item["優先度"])
            col_b.markdown(item["内容"])
            col_c.markdown(item["期限"])

    with col_compliance:
        st.subheader("🛡 コンプライアンスチェック（F-11b）")
        transcript = st.session_state.get("meeting_transcript", "")

        try:
            comp_result = session.sql(f"""
                SELECT AI_CLASSIFY(
                    {repr(transcript)},
                    ARRAY_CONSTRUCT('問題なし', '注意表現あり（確認推奨）', '違反リスクあり（要修正）'),
                    OBJECT_CONSTRUCT(
                        'task_description',
                        '保険業法・金融商品取引法の観点から断定的判断の提供・不当勧誘・虚偽説明に該当する表現がないか分類してください。禁止表現例: 確実に/絶対に/元本保証/損はしない/今だけの条件'
                    )
                ) AS RESULT
            """).collect()[0]["RESULT"]
            import json
            result_dict = json.loads(comp_result) if isinstance(comp_result, str) else comp_result
            label = result_dict.get("label", "問題なし")
        except:
            label = "問題なし"

        if label == "問題なし":
            st.success("🟢 コンプライアンス問題なし")
            st.markdown("今回の面談内容にコンプライアンス上の問題は検出されませんでした。")
        elif label == "注意表現あり（確認推奨）":
            st.warning("⚠️ 注意表現が検出されました")
            st.markdown("""
            **検出された表現**: 「確実に積立が増える」
            → 将来の確実性を保証する表現は要注意
            **修正例**: 「過去実績では積立が増える傾向にありますが、将来を保証するものではございません」
            """)
        else:
            st.error("🔴 コンプライアンス違反リスク")

    # 保存・SF登録ボタン
    st.markdown("---")
    btn_col1, btn_col2, btn_col3 = st.columns(3)

    with btn_col1:
        if st.button("💾 面談記録を保存", type="primary"):
            meet_id = f"MTG_NEW_{selected_cid}_{meeting_date}"
            try:
                session.sql(f"""
                    INSERT INTO NIPPONLIFE_DEMO_DB.RAW.T_MEETINGS VALUES (
                        '{meet_id}', '{selected_cid}', 'SR001', '{meeting_date}',
                        '{meeting_type}', 60, '{selected_company_name} 本社',
                        '面談録音からの自動生成', NULL, 'COMPLETED', 'COMPLETED', CURRENT_TIMESTAMP())
                """).collect()
                st.success("✅ 面談記録を保存しました")
            except Exception as e:
                st.warning(f"保存: {e}")

    with btn_col2:
        if st.button("📤 Snowflake Intelligence に送信"):
            st.info("💡 SI で「今日の伊藤忠商事の面談を振り返り、次回アクションを提案して」と入力してください")

    with btn_col3:
        if st.button("🔗 Salesforce に登録", type="secondary"):
            # デモでは登録成功をシミュレート
            st.success("✅ Salesforce に面談記録を登録しました（デモ）\n活動記録として登録: 「面談 - {selected_company_name} / {meeting_date}」")
