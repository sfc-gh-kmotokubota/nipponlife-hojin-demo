-- ============================================================
-- 09_cortex_search.sql: Cortex Search サービス × 3
-- ============================================================
USE DATABASE NIPPONLIFE_DEMO_DB;
USE SCHEMA SEARCH;
USE WAREHOUSE NIPPONLIFE_DEMO_WH;

-- ────────────────────────────────────────
-- 1. 顧客情報・面談内容 Cortex Search
-- ────────────────────────────────────────
CREATE OR REPLACE CORTEX SEARCH SERVICE CUSTOMER_INFO_SEARCH
  ON TRANSCRIPT_TEXT
  ATTRIBUTES COMPANY_ID, MEETING_DATE, MEETING_TYPE, SPEAKER_LABEL
  WAREHOUSE = NIPPONLIFE_DEMO_WH
  TARGET_LAG = '1 hour'
AS (
    SELECT
        mt.TRANSCRIPT_TEXT,
        mt.SPEAKER_LABEL,
        m.COMPANY_ID,
        m.MEETING_DATE::VARCHAR AS MEETING_DATE,
        m.MEETING_TYPE,
        c.COMPANY_NAME,
        m.MEETING_ID
    FROM RAW.T_MEETING_TRANSCRIPTS mt
    JOIN RAW.T_MEETINGS m ON mt.MEETING_ID = m.MEETING_ID
    JOIN RAW.T_CUSTOMER_COMPANIES c ON m.COMPANY_ID = c.COMPANY_ID
);

-- ────────────────────────────────────────
-- 2. 企業ニュース・イベント Cortex Search
-- ────────────────────────────────────────
CREATE OR REPLACE CORTEX SEARCH SERVICE NEWS_SEARCH
  ON SEARCH_TEXT
  ATTRIBUTES COMPANY_ID, NEWS_DATE, EVENT_TYPE, INSURANCE_RELEVANCE
  WAREHOUSE = NIPPONLIFE_DEMO_WH
  TARGET_LAG = '1 hour'
AS (
    SELECT
        n.HEADLINE || ' ' || COALESCE(n.BODY_TEXT, '') AS SEARCH_TEXT,
        n.HEADLINE,
        n.BODY_TEXT,
        n.COMPANY_ID,
        n.NEWS_DATE::VARCHAR AS NEWS_DATE,
        n.EVENT_TYPE,
        n.INSURANCE_RELEVANCE,
        n.NEWS_SOURCE,
        c.COMPANY_NAME
    FROM RAW.T_COMPANY_NEWS n
    JOIN RAW.T_CUSTOMER_COMPANIES c ON n.COMPANY_ID = c.COMPANY_ID
);

-- ────────────────────────────────────────
-- 3. 保険商品・サービス Cortex Search
-- ────────────────────────────────────────
CREATE OR REPLACE CORTEX SEARCH SERVICE PRODUCT_SEARCH
  ON SEARCH_TEXT
  ATTRIBUTES PRODUCT_ID, PRODUCT_CATEGORY, PRODUCT_TYPE
  WAREHOUSE = NIPPONLIFE_DEMO_WH
  TARGET_LAG = '24 hours'
AS (
    -- 保険商品
    SELECT
        ip.PRODUCT_NAME || ' ' || COALESCE(ip.DESCRIPTION, '') AS SEARCH_TEXT,
        ip.PRODUCT_ID,
        ip.PRODUCT_NAME,
        ip.DESCRIPTION,
        ip.PRODUCT_CATEGORY,
        ip.PRODUCT_TYPE,
        ip.TARGET_AUDIENCE,
        '保険商品' AS CONTENT_TYPE
    FROM RAW.T_INSURANCE_PRODUCTS ip

    UNION ALL

    -- 非保険サービス
    SELECT
        ns.SERVICE_NAME || ' ' || COALESCE(ns.DESCRIPTION, '') AS SEARCH_TEXT,
        ns.SERVICE_ID AS PRODUCT_ID,
        ns.SERVICE_NAME AS PRODUCT_NAME,
        ns.DESCRIPTION,
        ns.SERVICE_CATEGORY AS PRODUCT_CATEGORY,
        '非保険サービス' AS PRODUCT_TYPE,
        ns.TARGET_AUDIENCE,
        '非保険サービス' AS CONTENT_TYPE
    FROM RAW.T_NISSAY_SERVICES ns
);

SELECT 'Cortex Search services created: CUSTOMER_INFO_SEARCH, NEWS_SEARCH, PRODUCT_SEARCH' AS STATUS;
