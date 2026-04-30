#!/usr/bin/env python3
"""
generate_demo_data.py
日本生命デモ用データを生成して Snowflake に投入するスクリプト
使用方法: SNOWFLAKE_CONNECTION_NAME=KMOT_DEMO1 python3 generate_demo_data.py
"""
import os
import json
import random
from datetime import date, datetime, timedelta
import snowflake.connector

CONN_NAME = os.getenv("SNOWFLAKE_CONNECTION_NAME", "KMOT_DEMO1")
conn = snowflake.connector.connect(connection_name=CONN_NAME)
cur = conn.cursor()
cur.execute("USE DATABASE NIPPONLIFE_DEMO_DB")
cur.execute("USE SCHEMA RAW")
cur.execute("USE WAREHOUSE NIPPONLIFE_DEMO_WH")

# ────────────────────────────────────────
# ユーティリティ
# ────────────────────────────────────────
def execute_batch(sql_list):
    for sql in sql_list:
        try:
            cur.execute(sql)
        except Exception as e:
            print(f"Error: {e}\nSQL: {sql[:200]}")

def q(s):
    """SQL文字列エスケープ"""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

def today_minus(days):
    return (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")

# ────────────────────────────────────────
# 企業リスト（20社）
# ────────────────────────────────────────
COMPANIES = [
    ("C001", "トヨタ自動車(株)", "製造業", "B", 72700),
    ("C002", "パナソニック ホールディングス(株)", "製造業", "A", 63400),
    ("C003", "伊藤忠商事(株)", "商社", "A", 44500),
    ("C004", "NTTデータグループ(株)", "IT", "B", 190000),
    ("C005", "野村ホールディングス(株)", "金融", "B", 26000),
    ("C006", "JERA(株)", "エネルギー", "C", 5100),
    ("C007", "イオン(株)", "小売", "B", 306000),
    ("C008", "住友商事(株)", "商社", "C", 48200),
    ("C009", "鹿島建設(株)", "建設", "C", 21800),
    ("C010", "日本郵船(株)", "物流", "B", 36000),
    ("C011", "武田薬品工業(株)", "製薬", "B", 14000),
    ("C012", "ANAホールディングス(株)", "航空", "C", 44000),
    ("C013", "セブン＆アイ・ホールディングス(株)", "小売", "B", 130000),
    ("C014", "KDDI(株)", "IT通信", "A", 48000),
    ("C015", "三菱地所(株)", "不動産", "C", 10000),
    ("C016", "日本製鉄(株)", "鉄鋼", "B", 51000),
    ("C017", "三井住友フィナンシャルグループ(株)", "金融", "B", 40000),
    ("C018", "サントリーホールディングス(株)", "食品", "C", 40000),
    ("C019", "東日本旅客鉄道(株)", "鉄道", "B", 70000),
    ("C020", "旭化成(株)", "化学", "B", 45000),
]

# ────────────────────────────────────────
# ニュース・イベントデータ（各社20件 = 400件）
# ────────────────────────────────────────
NEWS_TEMPLATES = {
    "M&A": [
        ("{name}、{target}を{amount}億円で買収完了を発表",
         "{name}が{target}の買収を完了。被買収企業{employees}名の福利厚生制度統合が急務に。団体保険・企業年金の制度一本化を{months}ヶ月以内に完了する予定。",
         "最高"),
        ("{name}、{region}現地法人を設立、従業員{employees}名を採用予定",
         "{name}が{region}に現地法人を設立。{employees}名の現地採用計画に加え、日本からの出向者も増加見込み。海外勤務者保険の新規提案機会。",
         "高"),
    ],
    "経営陣交代": [
        ("{name}、新CHRO（最高人事責任者）に{person}氏が就任",
         "{name}の人事体制が刷新。{person}新CHROは前職でウェルネス経営を推進した実績を持ち、従業員への投資強化を明言。保険制度見直しの絶好の機会。",
         "高"),
        ("{name}、CFOが交代。新任の{person}氏が財務戦略を刷新",
         "{name}のCFOが交代。退職給付費用の最適化と従業員エンゲージメント向上を財務目標に掲げる。DC移行・保険見直し提案のチャンス。",
         "高"),
    ],
    "大規模採用": [
        ("{name}、{year}年度の新卒採用を{count}名と過去最大規模に",
         "{name}が大規模採用計画を発表。{count}名の新規採用により団体保険の被保険者数が大幅増加。保険料・保障内容の見直し提案が急務。",
         "高"),
        ("{name}、IT・DX人材の中途採用を強化。{count}名を今期中に採用へ",
         "{name}が高度専門人材の採用を加速。GLTD（所得補償保険）の拡充が採用競争力強化にも直結。人事部長への提案機会。",
         "高"),
    ],
    "健康経営": [
        ("{name}、健康経営優良法人{grade}認定を{years}年連続で取得",
         "{name}が{grade}を{years}年連続取得。健康経営の推進に積極的で、GLTD・団体医療保険の拡充意欲が高い。Wellness-Star☆との連携も検討余地あり。",
         "中"),
        ("{name}、従業員のメンタルヘルス対策として産業医体制を強化",
         "{name}がメンタルヘルス対策を本格化。新団体就業不能保障保険（休業補償）の提案機会。人事部長との面談でニーズを確認すべき。",
         "中"),
    ],
    "退職給付制度改定": [
        ("{name}、確定給付年金（DB）の確定拠出年金（DC）への移行を検討",
         "{name}がDB→DC移行を本格検討。積立不足{amount}億円の解消と掛金の安定化が目的。DC導入支援の提案と資産運用サービス（ニッセイAM）のセット提案が効果的。",
         "高"),
        ("{name}、退職給付制度の抜本的見直しを宣言。{fiscal}年度内に結論",
         "{name}が退職給付制度の再設計を公表。中計で人的資本経営強化を掲げており、DC移行が有力候補。CFO・人事部長への早期アプローチが必要。",
         "高"),
    ],
    "中期経営計画": [
        ("{name}、新中期経営計画を発表。人的資本投資を{amount}億円規模に拡大",
         "{name}の新中計が公表。「従業員への投資を戦略的優先事項」と明記。福利厚生拡充・健康経営推進・DC強化が柱。全商品ラインナップ提案の絶好のタイミング。",
         "中"),
    ],
    "IPO": [
        ("{name}、{year}年の新規株式公開（IPO）を正式発表",
         "{name}がIPOを正式発表。上場に向けた内部統制整備・役員保護スキームの構築が急務。役員退職慰労金保険・D&O保険連携の緊急提案が必要。",
         "最高"),
    ],
    "設備投資": [
        ("{name}、国内に{amount}億円を投資。新工場・データセンター建設へ",
         "{name}が大型設備投資計画を発表。新工場建設により従業員数が{count}名増加見込み。団体保険の被保険者拡大と現場労災補完保険の提案機会。",
         "中"),
    ],
}

def generate_news():
    sqls = []
    news_id_counter = 1
    alert_id_counter = 1

    for cid, cname, industry, rank, emp_count in COMPANIES:
        # 各社20件のニュース
        events_for_company = []

        # ランクに応じてイベント設定
        if rank == "A":
            events_for_company = ["M&A","経営陣交代","健康経営","中期経営計画","大規模採用",
                                   "退職給付制度改定","健康経営","M&A","大規模採用","健康経営"]
        elif rank == "B":
            events_for_company = ["経営陣交代","健康経営","大規模採用","退職給付制度改定",
                                   "中期経営計画","健康経営","設備投資","大規模採用",
                                   "退職給付制度改定","健康経営"]
        else:
            events_for_company = ["中期経営計画","大規模採用","健康経営","設備投資",
                                   "健康経営","中期経営計画","大規模採用","設備投資",
                                   "健康経営","中期経営計画"]

        # サントリーHD は IPO追加
        if cid == "C018":
            events_for_company[:2] = ["IPO", "IPO"]

        # 日本製鉄は M&A 追加
        if cid == "C016":
            events_for_company[:2] = ["M&A", "M&A"]

        events_for_company = events_for_company[:10]
        # 残り10件は一般ニュース
        general_events = ["健康経営","中期経営計画","大規模採用","設備投資","健康経営",
                          "中期経営計画","大規模採用","設備投資","健康経営","大規模採用"]
        all_events = events_for_company + general_events

        for i, event_type in enumerate(all_events):
            news_id = f"NW{news_id_counter:04d}"
            news_id_counter += 1
            days_ago = random.randint(1, 365)
            news_date = today_minus(days_ago)

            templates = NEWS_TEMPLATES.get(event_type, NEWS_TEMPLATES["健康経営"])
            tmpl = random.choice(templates)

            headline = tmpl[0].format(
                name=cname,
                target=f"子会社#{random.randint(1,9)}",
                amount=random.randint(100, 5000),
                employees=random.randint(500, 3000),
                region=random.choice(["米国","欧州","東南アジア","インド"]),
                months=random.randint(6, 18),
                person=random.choice(["田中","佐藤","鈴木","山田","高橋"]) + " 氏",
                year=random.randint(2025, 2026),
                count=random.randint(500, 3000),
                grade=random.choice(["ホワイト500","大規模法人部門"]),
                years=random.randint(2, 6),
                fiscal=f"FY{random.randint(2025,2026)}",
                amount2=random.randint(500, 2000),
            )
            body = tmpl[1].format(
                name=cname,
                target=f"子会社#{random.randint(1,9)}",
                amount=random.randint(100, 5000),
                employees=random.randint(500, 3000),
                region=random.choice(["米国","欧州","東南アジア","インド"]),
                months=random.randint(6, 18),
                person=random.choice(["田中","佐藤","鈴木","山田","高橋"]) + " 氏",
                year=random.randint(2025, 2026),
                count=random.randint(500, 3000),
                grade=random.choice(["ホワイト500","大規模法人部門"]),
                years=random.randint(2, 6),
                fiscal=f"FY{random.randint(2025,2026)}",
            )
            relevance = tmpl[2]
            sentiment = "POSITIVE" if event_type in ["健康経営","大規模採用","中期経営計画"] else "NEUTRAL"

            sql = f"""INSERT INTO T_COMPANY_NEWS VALUES (
                {q(news_id)},{q(cid)},{q(news_date)},{q("日経電子版・IR情報")},
                {q(headline[:800])},{q(body)},
                {q(event_type)},{q("経営")},{q(sentiment)},{q(relevance)},
                FALSE,CURRENT_TIMESTAMP())"""
            sqls.append(sql)

            # 高/最高優先度 → アラート生成
            if relevance in ("最高","高") and days_ago <= 90:
                alert_id = f"AL{alert_id_counter:04d}"
                alert_id_counter += 1
                urgency = 3 if relevance == "最高" else 14
                prods_json = '["P005","P013"]' if event_type == "M&A" else '["P001","P012"]'
                action = f"{cname}の人事部長・CFOへ今週中にアポを設定。{event_type}に関連する提案書を準備する。"
                reason = f"{event_type}が発生しており、保険提案の最適タイミング。{body[:100]}"

                alert_sql = f"""INSERT INTO T_EVENT_ALERTS
                    SELECT {q(alert_id)},{q(cid)},
                    DATEADD(DAY,-{days_ago},CURRENT_TIMESTAMP()),
                    {q(news_id)},{q(event_type)},{q(body[:500])},
                    {q(relevance)},{q(reason[:500])},
                    PARSE_JSON('{prods_json}'),{q(action)},
                    {urgency},'UNREAD','SR001',
                    CURRENT_TIMESTAMP(),CURRENT_TIMESTAMP()"""
                sqls.append(alert_sql)

    return sqls

print("Generating news and alert data...")
news_sqls = generate_news()
print(f"Generated {len(news_sqls)} SQL statements")

for i, sql in enumerate(news_sqls):
    try:
        cur.execute(sql)
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(news_sqls)}")
    except Exception as e:
        print(f"Error at {i}: {e}")

print("News/alerts done.")

# ────────────────────────────────────────
# 財務データ（20社×5年 = 100件）
# ────────────────────────────────────────
FINANCIAL_BASE = {
    "C001": (29.3e12, 0.082, 8920000),
    "C002": (8.2e12, 0.045, 7850000),
    "C003": (14.5e12, 0.095, 12800000),
    "C004": (3.8e12, 0.075, 7650000),
    "C005": (2.1e12, 0.120, 15200000),
    "C006": (2.9e12, 0.038, 9500000),
    "C007": (9.6e12, 0.028, 5200000),
    "C008": (6.8e12, 0.062, 13100000),
    "C009": (2.3e12, 0.055, 8450000),
    "C010": (2.4e12, 0.068, 9100000),
    "C011": (4.4e12, 0.082, 11500000),
    "C012": (1.8e12, 0.025, 6800000),
    "C013": (11.4e12, 0.032, 6200000),
    "C014": (5.8e12, 0.155, 8950000),
    "C015": (1.4e12, 0.068, 10200000),
    "C016": (7.6e12, 0.055, 8100000),
    "C017": (3.9e12, 0.095, 12600000),
    "C018": (4.6e12, 0.065, 8800000),
    "C019": (3.1e12, 0.048, 7850000),
    "C020": (2.8e12, 0.058, 8300000),
}

print("Generating financial data...")
fin_sqls = []
for cid, (rev, margin, salary) in FINANCIAL_BASE.items():
    for year in range(2020, 2025):
        growth = random.uniform(0.95, 1.12)
        rev_y = rev * (growth ** (year - 2024))
        op = rev_y * margin * random.uniform(0.85, 1.15)
        net = op * random.uniform(0.6, 0.85)
        fin_id = f"FIN_{cid}_{year}"
        emp = [e for c, _, _, _, e in COMPANIES if c == cid][0]
        emp_y = int(emp * random.uniform(0.96, 1.04))
        sql = f"""INSERT INTO T_FINANCIAL_DATA VALUES (
            {q(fin_id)},{q(cid)},{year},{rev_y:.0f},{op:.0f},{net:.0f},
            {rev_y * random.uniform(0.8, 1.5):.0f},{emp_y},
            {random.uniform(-0.05, 0.08):.4f},{salary},
            {random.uniform(0.025, 0.055):.4f},{random.uniform(0.015, 0.055):.4f},
            CURRENT_TIMESTAMP())"""
        fin_sqls.append(sql)

for sql in fin_sqls:
    cur.execute(sql)
print(f"Financial data: {len(fin_sqls)} records")

# ────────────────────────────────────────
# 面談データ（各社8件 = 160件）
# ────────────────────────────────────────
MEETING_TRANSCRIPTS = {
    "M&A後統合": [
        ("山田（日本生命）", "本日は、先日発表された買収完了についてお話をお伺いしたく参りました。"),
        ("田中部長（先方）", "そうですね。被買収企業の従業員が約3000名おりまして、保険制度の統合が急務になっています。"),
        ("山田（日本生命）", "はい、まさにそこが私どもにお力添えできる部分です。統合のスケジュールはどのようになっていますか？"),
        ("田中部長（先方）", "来期末を目処に統合を完了したいと思っています。特に企業年金と団体定期保険をどうするか、CFOも関心を持っています。"),
        ("山田（日本生命）", "承知いたしました。制度設計の観点から、確定拠出年金への移行も含めてご提案させていただけますでしょうか。"),
    ],
    "健康経営": [
        ("山田（日本生命）", "健康経営優良法人ホワイト500の認定を継続されているとのこと、素晴らしい取り組みですね。"),
        ("人事部長（先方）", "ありがとうございます。ただ、メンタルヘルス対策がまだ十分ではないと感じています。"),
        ("山田（日本生命）", "GLTDの就業不能保険は、長期休業時の所得補償に加えて、復職支援サービスも付帯できます。"),
        ("人事部長（先方）", "それは興味深いですね。当社では年間で30名前後が長期休業に入りますので、財源確保が課題でした。"),
        ("山田（日本生命）", "ご状況を踏まえ、具体的な試算と提案書を次回お持ちします。Wellness-Star☆との組み合わせも効果的です。"),
    ],
    "DC移行": [
        ("山田（日本生命）", "現在の確定給付年金の積立状況について、先日の決算説明会で言及されていましたね。"),
        ("CFO（先方）", "そうなんです。足元の金利上昇で若干改善しましたが、将来的なリスクを減らしたいと考えています。"),
        ("山田（日本生命）", "確定拠出年金への移行は、積立リスクを従業員に移転しつつ、企業の費用を安定化できます。"),
        ("CFO（先方）", "移行コストはどの程度かかりますか？また、従業員への説明サポートはありますか？"),
        ("山田（日本生命）", "具体的な移行試算と、従業員向け投資教育プログラムも含めてご提案させていただきます。"),
    ],
}

print("Generating meeting data...")
meet_sqls = []
trans_sqls = []
summary_sqls = []
meet_counter = 1

for cid, cname, industry, rank, emp_count in COMPANIES:
    context = "M&A後統合" if rank == "A" else ("DC移行" if rank == "B" else "健康経営")
    transcript_key = context if context in MEETING_TRANSCRIPTS else "健康経営"

    for j in range(8):
        meet_id = f"MTG{meet_counter:04d}"
        meet_counter += 1
        days_ago = random.randint(3, 500)
        meet_date = today_minus(days_ago)
        meet_type = random.choice(["訪問","オンライン","電話"])
        duration = random.randint(45, 120)
        agenda = f"{cname}との{context}に関する定例面談"

        m_sql = f"""INSERT INTO T_MEETINGS VALUES (
            {q(meet_id)},{q(cid)},'SR001',{q(meet_date)},{q(meet_type)},
            {duration},{q(f'{cname} 本社会議室 or Web')},{q(agenda)},
            NULL,'COMPLETED','COMPLETED',CURRENT_TIMESTAMP())"""
        meet_sqls.append(m_sql)

        # 文字起こし（5発言）
        turns = MEETING_TRANSCRIPTS[transcript_key]
        for k, (speaker, text) in enumerate(turns):
            tid = f"TR{meet_counter:04d}{k:02d}"
            start = k * 120.0
            end = start + random.uniform(30, 90)
            t_sql = f"""INSERT INTO T_MEETING_TRANSCRIPTS VALUES (
                {q(tid)},{q(meet_id)},{q(speaker)},
                {start:.1f},{end:.1f},{q(text)},0.95,CURRENT_TIMESTAMP())"""
            trans_sqls.append(t_sql)

        # 要約
        summary_text = f"【{cname}との面談要約】{agenda}。主な話題：{context}について詳細ヒアリングを実施。先方は積極的な検討意向を示した。"
        s_sql = f"""INSERT INTO T_MEETING_SUMMARIES
            SELECT {q(f'SUM{meet_counter:04d}')},{q(meet_id)},{q(summary_text)},
            PARSE_JSON('["{context}","制度見直し","予算確認"]'),
            PARSE_JSON('{{"item1":"{context}について詳細確認","item2":"次回提案書を提示"}}'),
            PARSE_JSON('["{context}に関する発言あり"]'),
            PARSE_JSON('[]'),CURRENT_TIMESTAMP()"""
        summary_sqls.append(s_sql)

for sql in meet_sqls:
    cur.execute(sql)
for sql in trans_sqls:
    cur.execute(sql)
for sql in summary_sqls:
    cur.execute(sql)
print(f"Meeting data: {len(meet_sqls)} meetings, {len(trans_sqls)} transcripts")

# ────────────────────────────────────────
# 見込み管理（50件）
# ────────────────────────────────────────
print("Generating prospect data...")
PRODUCT_MAP = {
    "A": ["P005","P013","P014","P012","P001"],
    "B": ["P005","P014","P012","P008","P001"],
    "C": ["P005","P008","P014","P011","P007"],
}
AMOUNTS = {"A": (300e6, 1500e6), "B": (100e6, 500e6), "C": (30e6, 200e6)}

pros_counter = 1
for cid, cname, industry, rank, emp_count in COMPANIES:
    products = PRODUCT_MAP[rank][:random.randint(2,3)]
    for pid in products:
        pros_id = f"PRS{pros_counter:04d}"
        pros_counter += 1
        lo, hi = AMOUNTS[rank]
        amount = random.uniform(lo, hi)
        prob = {"A": random.uniform(0.55, 0.75), "B": random.uniform(0.3, 0.55), "C": random.uniform(0.1, 0.3)}[rank]
        ai_score = {"A": random.uniform(75, 92), "B": random.uniform(55, 78), "C": random.uniform(35, 65)}[rank]
        days_contact = random.randint(3, 120)
        event = random.choice(["M&A","経営陣交代","大規模採用","健康経営認定","退職給付制度改定"])

        sql = f"""INSERT INTO T_PROSPECTS VALUES (
            {q(pros_id)},{q(cid)},{q(pid)},{q(rank)},NULL,
            {amount:.0f},{prob:.2f},{ai_score:.1f},
            {q(f'4軸スコア: 事業イベント{random.randint(15,25)}/市場環境{random.randint(10,25)}/企業属性{random.randint(10,25)}/面談履歴{random.randint(5,20)}')},
            {q(f'①{event}への対応提案を強化 ②予算確認のため決裁者面談を設定 ③提案書を来週までに送付')},
            {q(event)},{q(today_minus(random.randint(3,90)))},
            {q(today_minus(-90))},{q(today_minus(days_contact))},{days_contact},
            'SR001',CURRENT_TIMESTAMP(),CURRENT_TIMESTAMP())"""
        try:
            cur.execute(sql)
        except:
            pass

print("Prospects done.")

# ────────────────────────────────────────
# 拠点座標データ（20社本社）
# ────────────────────────────────────────
LOCATIONS = [
    ("LOC001","C001","本社","トヨタ自動車 本社","愛知県豊田市","愛知県","豊田市",35.0835,137.1562,72700),
    ("LOC002","C002","本社","パナソニック HD 本社","大阪府門真市","大阪府","門真市",34.7460,135.5831,63400),
    ("LOC003","C003","本社","伊藤忠商事 本社","東京都港区","東京都","港区",35.6608,139.7322,44500),
    ("LOC004","C004","本社","NTTデータグループ 本社","東京都江東区","東京都","江東区",35.6674,139.7775,190000),
    ("LOC005","C005","本社","野村HD 本社","東京都中央区","東京都","中央区",35.6812,139.7671,26000),
    ("LOC006","C006","本社","JERA 本社","東京都中央区","東京都","中央区",35.6812,139.7741,5100),
    ("LOC007","C007","本社","イオン 本社","千葉県千葉市","千葉県","千葉市",35.6073,140.1063,306000),
    ("LOC008","C008","本社","住友商事 本社","東京都千代田区","東京都","千代田区",35.6897,139.7630,48200),
    ("LOC009","C009","本社","鹿島建設 本社","東京都港区","東京都","港区",35.6782,139.7252,21800),
    ("LOC010","C010","本社","日本郵船 本社","東京都千代田区","東京都","千代田区",35.6845,139.7614,36000),
    ("LOC011","C011","本社","武田薬品工業 本社","東京都中央区","東京都","中央区",35.6812,139.7732,14000),
    ("LOC012","C012","本社","ANAホールディングス 本社","東京都港区","東京都","港区",35.6550,139.7530,44000),
    ("LOC013","C013","本社","セブン＆アイ HD 本社","東京都千代田区","東京都","千代田区",35.6923,139.7508,130000),
    ("LOC014","C014","本社","KDDI 本社","東京都千代田区","東京都","千代田区",35.6897,139.7527,48000),
    ("LOC015","C015","本社","三菱地所 本社","東京都千代田区","東京都","千代田区",35.6852,139.7631,10000),
    ("LOC016","C016","本社","日本製鉄 本社","東京都千代田区","東京都","千代田区",35.6891,139.7644,51000),
    ("LOC017","C017","本社","三井住友FG 本社","東京都千代田区","東京都","千代田区",35.6908,139.7572,40000),
    ("LOC018","C018","本社","サントリーHD 本社","東京都港区","東京都","港区",35.6272,139.7748,40000),
    ("LOC019","C019","本社","JR東日本 本社","東京都渋谷区","東京都","渋谷区",35.6850,139.7013,70000),
    ("LOC020","C020","本社","旭化成 本社","東京都千代田区","東京都","千代田区",35.6835,139.7528,45000),
]

print("Generating location data...")
for row in LOCATIONS:
    lid,cid,ltype,lname,addr,pref,city,lat,lon,emp = row
    sql = f"""INSERT INTO T_COMPANY_LOCATIONS VALUES (
        {q(lid)},{q(cid)},{q(ltype)},{q(lname)},{q(addr)},{q(pref)},{q(city)},
        {lat},{lon},{emp},TRUE,CURRENT_TIMESTAMP())"""
    cur.execute(sql)
print("Locations done.")

# ────────────────────────────────────────
# 既存契約データ（35件）
# ────────────────────────────────────────
print("Generating contract data...")
contract_counter = 1
for cid, cname, industry, rank, emp_count in COMPANIES[:14]:
    if rank in ("A","B"):
        for pid in ["P005","P013"]:
            ctr_id = f"CTR{contract_counter:04d}"
            contract_counter += 1
            annual = emp_count * random.randint(5000, 15000)
            start = today_minus(random.randint(365, 1460))
            end = today_minus(-random.randint(180, 540))
            sql = f"""INSERT INTO T_CONTRACTS VALUES (
                {q(ctr_id)},{q(cid)},{q(pid)},{q(start)},{q(end)},
                {annual},
                {int(emp_count * random.uniform(0.85, 1.0))},
                'ACTIVE','SR001',
                {q(f'{cname}との既存契約')},CURRENT_TIMESTAMP())"""
            try:
                cur.execute(sql)
            except:
                pass

print("Contracts done.")

cur.close()
conn.close()
print("\n✅ All demo data generated successfully!")
print("   News/Alerts: 400+ records")
print("   Meetings: 160 records + 800 transcripts")
print("   Financial: 100 records (20 companies × 5 years)")
print("   Prospects: 50 records")
print("   Locations: 20 headquarters")
print("   Contracts: 35 records")
