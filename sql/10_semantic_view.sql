-- ============================================================
-- 10_semantic_view.sql: Cortex Analyst 用 Semantic View
-- ============================================================
USE DATABASE NIPPONLIFE_DEMO_DB;
USE SCHEMA ANALYTICS;
USE WAREHOUSE NIPPONLIFE_DEMO_WH;

CREATE OR REPLACE SEMANTIC VIEW SV_SALES_ANALYTICS
  COMMENT = '日本生命 法人営業 KPI・見込み・アラート分析用セマンティックビュー'
TABLES (
    RAW.T_PROSPECTS AS prospects
        PRIMARY KEY (PROSPECT_ID)
        COMMENT = '見込み管理テーブル。各顧客企業×商品の見込みスコア・ランク・推奨アクション',
    RAW.T_CUSTOMER_COMPANIES AS companies
        PRIMARY KEY (COMPANY_ID)
        COMMENT = '顧客企業マスタ。20社の大企業情報（従業員数・業種・財務・見込みランク等）',
    RAW.T_MEETINGS AS meetings
        PRIMARY KEY (MEETING_ID)
        COMMENT = '面談履歴テーブル。各顧客との接触記録',
    RAW.T_EVENT_ALERTS AS alerts
        PRIMARY KEY (ALERT_ID)
        COMMENT = '事業イベントアラート。M&A・経営陣交代・大規模採用等の保険提案機会',
    RAW.T_INSURANCE_PRODUCTS AS products
        PRIMARY KEY (PRODUCT_ID)
        COMMENT = '保険商品マスタ（14商品）',
    RAW.T_NISSAY_SERVICES AS services
        PRIMARY KEY (SERVICE_ID)
        COMMENT = '非保険サービスマスタ（5サービス）'
)
RELATIONSHIPS (
    prospects (COMPANY_ID) REFERENCES companies (COMPANY_ID),
    meetings  (COMPANY_ID) REFERENCES companies (COMPANY_ID),
    alerts    (COMPANY_ID) REFERENCES companies (COMPANY_ID),
    prospects (PRODUCT_ID) REFERENCES products (PRODUCT_ID)
)
DIMENSIONS (
    companies.COMPANY_NAME
        COMMENT = '顧客企業名',
    companies.INDUSTRY_LARGE
        COMMENT = '業種（大分類）: 製造業・商社・IT・金融・エネルギー等',
    companies.PREFECTURE
        COMMENT = '本社所在都道府県',
    prospects.CURRENT_RANK
        SYNONYMS = ('見込みランク', 'ランク', 'rank')
        COMMENT = '見込みランク: S（最高）/ A / B / C（最低）',
    alerts.EVENT_TYPE
        SYNONYMS = ('事業イベント種別', 'イベント種別')
        COMMENT = 'M&A・経営陣交代・大規模採用・健康経営・退職給付制度改定等',
    alerts.INSURANCE_RELEVANCE
        SYNONYMS = ('アラート優先度', '重要度')
        COMMENT = '最高・高・中・低',
    products.PRODUCT_CATEGORY
        COMMENT = '商品カテゴリ: 経営者向け・福利厚生（死亡保障）・医療保障・休業補償・年金',
    meetings.MEETING_TYPE
        COMMENT = '面談種別: 訪問・オンライン・電話'
)
METRICS (
    -- 見込み保険料
    prospect_amount_total
        AS SUM(prospects.PROSPECT_AMOUNT)
        SYNONYMS = ('見込み保険料合計', '見込み金額合計', '見込み総額')
        COMMENT = '見込み保険料の合計金額（年額、円）',
    -- 件数
    prospect_count
        AS COUNT(prospects.PROSPECT_ID)
        SYNONYMS = ('見込み件数', '案件数')
        COMMENT = '見込み管理の件数',
    -- 平均AIスコア
    avg_ai_score
        AS AVG(prospects.AI_SCORE)
        SYNONYMS = ('平均AIスコア', 'AIスコア平均')
        COMMENT = '見込みAIスコアの平均値（0-100）',
    -- 平均接触間隔
    avg_days_since_contact
        AS AVG(prospects.DAYS_SINCE_CONTACT)
        SYNONYMS = ('平均接触間隔', '接触日数平均')
        COMMENT = '最終接触からの平均経過日数',
    -- 未対応アラート件数
    unread_alert_count
        AS COUNT(alerts.ALERT_ID)
        WHERE alerts.STATUS = 'UNREAD'
        SYNONYMS = ('未対応アラート件数', '未読アラート数')
        COMMENT = '未対応（未読）の事業イベントアラート件数',
    -- 面談件数
    meeting_count
        AS COUNT(meetings.MEETING_ID)
        SYNONYMS = ('面談件数', '接触回数')
        COMMENT = '面談・接触の総件数'
)
VERIFIED_QUERIES (
    '現在のAランク・Bランクの見込み件数と金額を教えてください'
    VERIFIED_QUERY AS
        SELECT CURRENT_RANK, COUNT(*) AS PROSPECT_COUNT, SUM(PROSPECT_AMOUNT)/1e8 AS AMOUNT_HUNDRED_MILLION
        FROM RAW.T_PROSPECTS
        WHERE CURRENT_RANK IN ('A','B')
        GROUP BY CURRENT_RANK
        ORDER BY CURRENT_RANK,

    '未対応アラートが最も多い企業を教えてください'
    VERIFIED_QUERY AS
        SELECT c.COMPANY_NAME, COUNT(ea.ALERT_ID) AS ALERT_COUNT
        FROM RAW.T_EVENT_ALERTS ea
        JOIN RAW.T_CUSTOMER_COMPANIES c ON ea.COMPANY_ID = c.COMPANY_ID
        WHERE ea.STATUS = 'UNREAD'
        GROUP BY c.COMPANY_NAME
        ORDER BY ALERT_COUNT DESC
        LIMIT 5,

    '業種別の見込み保険料合計を教えてください'
    VERIFIED_QUERY AS
        SELECT c.INDUSTRY_LARGE, SUM(p.PROSPECT_AMOUNT)/1e8 AS TOTAL_AMOUNT_HUNDRED_MILLION
        FROM RAW.T_PROSPECTS p
        JOIN RAW.T_CUSTOMER_COMPANIES c ON p.COMPANY_ID = c.COMPANY_ID
        GROUP BY c.INDUSTRY_LARGE
        ORDER BY TOTAL_AMOUNT_HUNDRED_MILLION DESC
);

SELECT 'Semantic View SV_SALES_ANALYTICS created' AS STATUS;
