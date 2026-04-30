# 日本生命 法人営業AIアシスタント
## Snowflake Intelligence + Streamlit でDatabricksに勝つ

[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white)](https://snowflake.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

> **vs Databricks**: MCP不要のWebSearch・保険業法コンプライアンス検知・説明可能AI商品マッチングでDatabricksを圧倒

---

## 🚀 セットアップ手順

### 1. 前提条件

- Snowflake アカウント（ACCOUNTADMIN ロール）
- Snowflake CLI (`snow`) インストール済み
- Python 3.9+ + `snowflake-connector-python`

### 2. Snowflake 環境構築

```bash
# KMOT_DEMO1 接続でSQLを順に実行
CONN=KMOT_DEMO1

snow sql -f sql/00_setup.sql -c $CONN
snow sql -f sql/01_ddl.sql -c $CONN
snow sql -f sql/02_master_data.sql -c $CONN
```

### 3. デモデータ生成

```bash
# Python スクリプトでリッチなデモデータを生成
SNOWFLAKE_CONNECTION_NAME=KMOT_DEMO1 python3 sql/03_generate_data.py
```

### 4. ビュー・Cortex Search・Semantic View 作成

```bash
snow sql -f sql/08_views.sql -c $CONN
snow sql -f sql/09_cortex_search.sql -c $CONN
snow sql -f sql/10_semantic_view.sql -c $CONN
```

### 5. Streamlit デプロイ

```bash
# Snowflake on Streamlit として CREATE
snow streamlit deploy \
  --app-name NIPPONLIFE_SALES_DEMO \
  --database NIPPONLIFE_DEMO_DB \
  --schema RAW \
  --warehouse NIPPONLIFE_DEMO_WH \
  --main-file streamlit/main.py \
  -c $CONN
```

---

## 📱 アプリ構成（6画面）

| # | 画面 | 機能 | vs Databricks |
|---|------|------|---------------|
| 1 | 🚨 アラート | 事業イベント自動検知・pydeck地図 | ✅ プッシュ型（Databricksはプル型） |
| 2 | 🎙 面談録音 | AI要約・コンプライアンス検知・SF登録 | ✅ 保険業法特化分類は競合になし |
| 3 | 📊 見込み管理 | カンバンボード・C→B昇格チェックリスト | ✅ 昇格チェックリストは競合になし |
| 4 | 🔍 商品マッチング | 4軸説明可能AIスコアリング | ✅✅ 根拠付き（競合は「精度が怪しい」） |
| 5 | 📄 提案書自動生成 | 既存テンプレへの差し込み・PPTX/Word | ✅ カスタムテンプレート対応 |
| 6 | 📈 マーケット | 財務企画部共有の金利・株価 | ✅✅ Snowflake Data Sharing（ゼロコピー） |

---

## 🤖 Snowflake Intelligence（SI）エージェント設定

`si_agent/system_prompt.md` を参照してエージェントを設定してください。

**Tools（10ツール）**:
1. `customer_search` - 顧客・面談情報（Cortex Search）
2. `news_search` - 企業ニュース・イベント（Cortex Search）
3. `product_search` - 保険商品・サービス（Cortex Search）
4. `sales_analytics` - KPI分析（Cortex Analyst）
5. `certified_info` - 優良認定情報（SQL）
6. `event_alert_search` - 事業イベントアラート（SQL）
7. `service_recommendation` - 非保険サービス提案（SQL）
8. `web_search` - リアルタイムWeb検索（**MCP不要・ネイティブ**）
9. `market_context_analysis` - 市場データ×保険提案（SQL）
10. `compliance_check` - 保険業法コンプライアンス検知（AI_CLASSIFY）

---

## 📊 データ構成

- **顧客企業**: 20社（従業員2,000名以上の実在大企業）
- **保険商品**: 14商品（日本生命公式サイト準拠）
- **非保険サービス**: 5サービス（Wellness-Star・Biz-Create・私募債等）
- **ニュース**: 400件（事業イベント分類・保険適合度付き）
- **面談録**: 160件 + 800発言の文字起こし
- **財務データ**: 100件（20社×5年）

---

## 🏆 Databricks との差別化（5ポイント）

1. **MCP不要のWeb Search** - Cortex Agent にネイティブ内蔵。顧客情報が外部に流れない
2. **コンプライアンス検知** - 保険業法特化のAI_CLASSIFY。面談中（SI）+事後（Streamlit）の2モード
3. **説明可能AI商品マッチング** - 4軸スコアリングで根拠を明示（競合は「精度が怪しい」）
4. **Snowflake Data Sharing** - 財務企画部の金利・株価データをゼロコピーで法人営業部に共有
5. **全処理がSnowflakeネットワーク内で完結** - 金融機関として情報漏洩リスクがない

---

*作成: Snowflake SE チーム | 更新: 2026年4月30日*
