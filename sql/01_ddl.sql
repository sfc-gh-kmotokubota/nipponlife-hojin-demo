-- ============================================================
-- 01_ddl.sql: 全テーブル定義 (16 テーブル)
-- ============================================================
USE DATABASE NIPPONLIFE_DEMO_DB;
USE SCHEMA RAW;
USE WAREHOUSE NIPPONLIFE_DEMO_WH;

-- ────────────────────────────────────────
-- 1. 顧客企業マスタ（20社）
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_CUSTOMER_COMPANIES (
    COMPANY_ID              VARCHAR(10)   NOT NULL PRIMARY KEY,
    COMPANY_NAME            VARCHAR(100)  NOT NULL,
    COMPANY_NAME_KANA       VARCHAR(100),
    INDUSTRY_LARGE          VARCHAR(50),
    INDUSTRY_DETAIL         VARCHAR(50),
    EMPLOYEE_COUNT          INTEGER,
    EMPLOYEE_COUNT_JAPAN    INTEGER,
    EMPLOYEE_COUNT_OVERSEAS INTEGER,
    HEADQUARTERS            VARCHAR(200),
    PREFECTURE              VARCHAR(20),
    FOUNDED_YEAR            INTEGER,
    ANNUAL_REVENUE_JPY      FLOAT,
    STOCK_MARKET            VARCHAR(30),
    CREDIT_RATING           VARCHAR(10),
    EMPLOYEE_RETENTION_RATE FLOAT,
    AVERAGE_AGE             FLOAT,
    AVERAGE_SALARY_JPY      INTEGER,
    WELFARE_EXPENSE_RATIO   FLOAT,
    TURNOVER_RATE           FLOAT,
    IS_LISTED               BOOLEAN,
    HAS_OVERSEAS_SUBSIDIARY BOOLEAN,
    PENSION_TYPE            VARCHAR(20),
    HEALTH_CERT_STATUS      VARCHAR(100),
    SALES_REP_ID            VARCHAR(10),
    STOCK_TICKER            VARCHAR(20),
    PROSPECT_RANK           CHAR(1),
    YEARS_IN_CHARGE         INTEGER,
    CREATED_AT              TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT              TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 2. 先方担当者マスタ（60名）
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_CONTACTS (
    CONTACT_ID      VARCHAR(15) NOT NULL PRIMARY KEY,
    COMPANY_ID      VARCHAR(10) NOT NULL,
    FULL_NAME       VARCHAR(100) NOT NULL,
    DEPARTMENT      VARCHAR(100),
    TITLE           VARCHAR(100),
    CONTACT_ROLE    VARCHAR(30),  -- 'DECISION_MAKER' / 'INFLUENCER' / 'WINDOW'
    EMAIL           VARCHAR(200),
    PHONE           VARCHAR(30),
    IS_PRIMARY      BOOLEAN DEFAULT FALSE,
    CREATED_AT      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 3. 日本生命 営業担当者マスタ
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_SALES_REPS (
    SALES_REP_ID    VARCHAR(10) NOT NULL PRIMARY KEY,
    FULL_NAME       VARCHAR(100) NOT NULL,
    DEPARTMENT      VARCHAR(100),
    TITLE           VARCHAR(100),
    EMAIL           VARCHAR(200),
    EXPERIENCE_YEARS INTEGER,
    CREATED_AT      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 4. 面談ヘッダ
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_MEETINGS (
    MEETING_ID          VARCHAR(20) NOT NULL PRIMARY KEY,
    COMPANY_ID          VARCHAR(10) NOT NULL,
    SALES_REP_ID        VARCHAR(10) NOT NULL,
    MEETING_DATE        DATE        NOT NULL,
    MEETING_TYPE        VARCHAR(20),  -- '訪問' / 'オンライン' / '電話'
    DURATION_MINUTES    INTEGER,
    LOCATION            VARCHAR(500),
    AGENDA              TEXT,
    AUDIO_FILE_PATH     VARCHAR(500),
    TRANSCRIPT_STATUS   VARCHAR(20) DEFAULT 'COMPLETED',
    SUMMARY_STATUS      VARCHAR(20) DEFAULT 'COMPLETED',
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 5. 面談文字起こし
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_MEETING_TRANSCRIPTS (
    TRANSCRIPT_ID       VARCHAR(20) NOT NULL PRIMARY KEY,
    MEETING_ID          VARCHAR(20) NOT NULL,
    SPEAKER_LABEL       VARCHAR(100),
    START_TIME_SEC      FLOAT,
    END_TIME_SEC        FLOAT,
    TRANSCRIPT_TEXT     TEXT NOT NULL,
    CONFIDENCE_SCORE    FLOAT,
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 6. AI生成済み面談要約
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_MEETING_SUMMARIES (
    SUMMARY_ID          VARCHAR(20) NOT NULL PRIMARY KEY,
    MEETING_ID          VARCHAR(20) NOT NULL,
    SUMMARY_TEXT        TEXT,
    KEY_ISSUES          ARRAY,       -- 先方の主な関心事項
    ACTION_ITEMS        VARIANT,     -- アクションアイテム（JSON）
    EVENT_MENTIONS      ARRAY,       -- 事業イベント関連発言
    COMPLIANCE_ISSUES   ARRAY,       -- コンプライアンス注意事項
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 7. 見込み管理
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_PROSPECTS (
    PROSPECT_ID         VARCHAR(20) NOT NULL PRIMARY KEY,
    COMPANY_ID          VARCHAR(10) NOT NULL,
    PRODUCT_ID          VARCHAR(10),
    CURRENT_RANK        CHAR(1)     NOT NULL,  -- S / A / B / C
    PREVIOUS_RANK       CHAR(1),
    PROSPECT_AMOUNT     FLOAT,
    PROBABILITY         FLOAT,
    AI_SCORE            FLOAT,
    AI_SCORE_REASON     TEXT,
    RANKUP_ACTIONS      TEXT,
    LAST_EVENT_TRIGGER  VARCHAR(100),
    LAST_EVENT_DATE     DATE,
    EXPECTED_CLOSE_DATE DATE,
    LAST_CONTACT_DATE   DATE,
    DAYS_SINCE_CONTACT  INTEGER,
    SALES_REP_ID        VARCHAR(10),
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 8. 見込みランク昇格チェックリストマスタ
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_PROSPECT_CHECKLIST_MASTER (
    CHECKLIST_ID        VARCHAR(10) NOT NULL PRIMARY KEY,
    FROM_RANK           CHAR(1),
    TO_RANK             CHAR(1),
    CHECK_ITEM          VARCHAR(500),
    CHECK_CATEGORY      VARCHAR(50),
    DISPLAY_ORDER       INTEGER,
    IS_REQUIRED         BOOLEAN DEFAULT TRUE
);

-- ────────────────────────────────────────
-- 9. 保険商品マスタ（14商品）
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_INSURANCE_PRODUCTS (
    PRODUCT_ID          VARCHAR(10) NOT NULL PRIMARY KEY,
    PRODUCT_NAME        VARCHAR(200) NOT NULL,
    PRODUCT_CATEGORY    VARCHAR(50),
    PRODUCT_TYPE        VARCHAR(30),  -- '経営者向け' / '福利厚生'
    EXPENSE_TYPE        VARCHAR(30),  -- '企業保障型' / '自助努力型' / '混合'
    TARGET_AUDIENCE     VARCHAR(200),
    MIN_EMPLOYEES       INTEGER,
    DESCRIPTION         TEXT,
    KEY_BENEFITS        ARRAY,
    TRIGGER_EVENTS      ARRAY,
    RENEWAL_CYCLE       VARCHAR(30),
    INDUSTRY_FIT_SCORE  VARIANT,      -- 業種別適合スコア（JSON）
    SOURCE_URL          VARCHAR(500),
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 10. 非保険サービスマスタ（5サービス）
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_NISSAY_SERVICES (
    SERVICE_ID          VARCHAR(10) NOT NULL PRIMARY KEY,
    SERVICE_NAME        VARCHAR(200) NOT NULL,
    SERVICE_CATEGORY    VARCHAR(50),
    DESCRIPTION         TEXT NOT NULL,
    KEY_FEATURES        ARRAY,
    TARGET_AUDIENCE     VARCHAR(200),
    TRIGGER_EVENTS      ARRAY,
    CROSS_SELL_PRODUCTS ARRAY,
    EXTERNAL_URL        VARCHAR(500),
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 11. 既存契約
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_CONTRACTS (
    CONTRACT_ID         VARCHAR(20) NOT NULL PRIMARY KEY,
    COMPANY_ID          VARCHAR(10) NOT NULL,
    PRODUCT_ID          VARCHAR(10) NOT NULL,
    CONTRACT_DATE       DATE,
    EXPIRY_DATE         DATE,
    ANNUAL_PREMIUM      FLOAT,
    INSURED_COUNT       INTEGER,
    STATUS              VARCHAR(20) DEFAULT 'ACTIVE',
    SALES_REP_ID        VARCHAR(10),
    NOTES               TEXT,
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 12. 次回アクション管理
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_NEXT_ACTIONS (
    ACTION_ID           VARCHAR(20) NOT NULL PRIMARY KEY,
    COMPANY_ID          VARCHAR(10) NOT NULL,
    MEETING_ID          VARCHAR(20),
    ACTION_TITLE        VARCHAR(500) NOT NULL,
    ACTION_DETAIL       TEXT,
    PRIORITY            VARCHAR(10),  -- '高' / '中' / '低'
    DUE_DATE            DATE,
    STATUS              VARCHAR(20) DEFAULT 'OPEN',  -- 'OPEN' / 'DONE' / 'CANCELLED'
    SALES_REP_ID        VARCHAR(10),
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 13. 企業ニュース（400件）
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_COMPANY_NEWS (
    NEWS_ID             VARCHAR(20) NOT NULL PRIMARY KEY,
    COMPANY_ID          VARCHAR(10) NOT NULL,
    NEWS_DATE           DATE        NOT NULL,
    NEWS_SOURCE         VARCHAR(100),
    HEADLINE            VARCHAR(1000) NOT NULL,
    BODY_TEXT           TEXT,
    EVENT_TYPE          VARCHAR(100),
    NEWS_CATEGORY       VARCHAR(50),
    SENTIMENT           VARCHAR(20),  -- 'POSITIVE' / 'NEUTRAL' / 'NEGATIVE'
    INSURANCE_RELEVANCE VARCHAR(10),  -- '最高' / '高' / '中' / '低'
    ALERT_GENERATED     BOOLEAN DEFAULT FALSE,
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 14. 事業イベントアラート
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_EVENT_ALERTS (
    ALERT_ID            VARCHAR(20) NOT NULL PRIMARY KEY,
    COMPANY_ID          VARCHAR(10) NOT NULL,
    DETECTED_AT         TIMESTAMP_NTZ NOT NULL,
    NEWS_ID             VARCHAR(20),
    EVENT_TYPE          VARCHAR(100) NOT NULL,
    EVENT_SUMMARY       TEXT         NOT NULL,
    INSURANCE_RELEVANCE VARCHAR(10),
    ALERT_REASON        TEXT,
    RECOMMENDED_PRODUCTS ARRAY,
    RECOMMENDED_ACTION  TEXT,
    URGENCY_DAYS        INTEGER,
    STATUS              VARCHAR(20) DEFAULT 'UNREAD',
    SALES_REP_ID        VARCHAR(10),
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 15. 企業財務情報（100件：20社×5年）
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_FINANCIAL_DATA (
    FINANCIAL_ID        VARCHAR(20) NOT NULL PRIMARY KEY,
    COMPANY_ID          VARCHAR(10) NOT NULL,
    FISCAL_YEAR         INTEGER     NOT NULL,
    REVENUE_JPY         FLOAT,
    OPERATING_PROFIT    FLOAT,
    NET_PROFIT          FLOAT,
    TOTAL_ASSETS        FLOAT,
    EMPLOYEE_COUNT      INTEGER,
    EMPLOYEE_COUNT_YOY  FLOAT,
    AVERAGE_SALARY      INTEGER,
    WELFARE_EXPENSE_RATIO FLOAT,
    TURNOVER_RATE       FLOAT,
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ────────────────────────────────────────
-- 16. 企業拠点情報（地図用）
-- ────────────────────────────────────────
CREATE OR REPLACE TABLE T_COMPANY_LOCATIONS (
    LOCATION_ID         VARCHAR(20) NOT NULL PRIMARY KEY,
    COMPANY_ID          VARCHAR(10) NOT NULL,
    LOCATION_TYPE       VARCHAR(30),
    LOCATION_NAME       VARCHAR(200),
    ADDRESS             VARCHAR(500),
    PREFECTURE          VARCHAR(30),
    CITY                VARCHAR(100),
    LATITUDE            FLOAT        NOT NULL,
    LONGITUDE           FLOAT        NOT NULL,
    EMPLOYEE_COUNT      INTEGER,
    IS_HEADQUARTERS     BOOLEAN DEFAULT FALSE,
    CREATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

SELECT 'DDL completed: 16 tables created' AS STATUS;
