# 日本生命 法人営業AIアシスタント
## Snowflake Intelligence + Streamlit で実現する営業DX

[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white)](https://snowflake.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

日本生命保険相互会社 法人営業部向けのAIアシスタントデモ。  
Snowflake Intelligence（Cortex Agent）と Streamlit on Snowflake を組み合わせ、**面談前 → 面談中 → 面談後** の営業活動を全面サポートします。

---

## 📱 アプリ構成（7画面）

| # | ファイル | 画面 | 主な機能 |
|---|---------|------|---------|
| – | `main.py` | 🏠 ホーム | KPI ダッシュボード・各機能への導線 |
| 1 | `01_alert.py` | 🚨 事業イベントアラート | M&A・IPO・経営陣交代等をAIが自動検知。pydeck地図で可視化 |
| 2 | `02_meeting.py` | 🎙 面談録音・要約 | 音声/会話ログ対応・AI要約・コンプライアンス検知・SF登録 |
| 3 | `03_prospect.py` | 📊 見込み管理 | カンバンボード・昇格チェックリスト・1クリック昇格 |
| 4 | `04_matching.py` | 🔍 商品マッチング | 4軸説明可能AIスコアリング（根拠付き） |
| 5 | `05_proposal.py` | 📄 提案書自動生成 | 既存テンプレへの情報差し込み・PPTX/Word対応 |
| 6 | `06_market.py` | 📈 マーケット・インサイト | 金利・株価データで提案タイミングを分析 |
| 7 | `07_prepare.py` | 🎯 面談前準備 | 企業ブリーフィング1クリック生成・想定Q&A自動作成 |

---

## 🤖 Snowflake Intelligence（Cortex Agent）

**エージェント**: `NIPPONLIFE_DEMO_DB.RAW.NIPPONLIFE_SALES_AGENT`

面談①前・②中・③後のすべてのフェーズをカバーする4ツール構成：

| ツール | タイプ | 用途 |
|-------|--------|------|
| `customer_search` | Cortex Search | 顧客・面談記録の全文検索 |
| `news_search` | Cortex Search | 企業ニュース・事業イベント検索 |
| `product_search` | Cortex Search | 保険商品・非保険サービス検索 |
| `sales_analytics` | Cortex Analyst | KPI・見込み・アラートのSQL分析 |

デモシナリオ集: `si_agent/demo_scenarios.md`（7つのマルチターン会話シナリオ）

---

## 🚀 セットアップ手順

### 前提条件

- Snowflake アカウント（ACCOUNTADMIN ロール）
- Snowflake CLI (`snow`) v3.14+
- Python 3.9+ + `snowflake-connector-python`

### 1. Snowflake 環境構築

```bash
CONN=KMOT_DEMO1

# DB / ウェアハウス / スキーマ / ロール
snow sql -f sql/00_setup.sql -c $CONN

# 全 16 テーブル DDL
snow sql -f sql/01_ddl.sql -c $CONN

# マスタデータ（20社・14商品・5サービス・チェックリスト）
# ※ snow sql の {} テンプレート変数問題を回避するため Python を使用
SNOWFLAKE_CONNECTION_NAME=$CONN python3 -c "
import os, snowflake.connector, pathlib
conn = snowflake.connector.connect(connection_name=os.environ['SNOWFLAKE_CONNECTION_NAME'])
cur = conn.cursor()
for stmt in pathlib.Path('sql/02_master_data.sql').read_text().split(';'):
    stmt = stmt.strip()
    if stmt and not stmt.startswith('--'):
        cur.execute(stmt)
conn.close()
print('Master data loaded.')
"
```

### 2. デモデータ生成

```bash
# ニュース（400件）・面談（160件）・財務・見込み・座標データ
SNOWFLAKE_CONNECTION_NAME=$CONN python3 sql/03_generate_data.py
```

### 3. ビュー・Cortex Search・Semantic View

```bash
# Analytics Views（V_PROSPECT_DASHBOARD / V_EVENT_ALERT_PRIORITY / V_MARKET_INSIGHT）
SNOWFLAKE_CONNECTION_NAME=$CONN python3 -c "
import os, snowflake.connector
conn = snowflake.connector.connect(connection_name=os.environ['SNOWFLAKE_CONNECTION_NAME'])
cur = conn.cursor()
cur.execute('USE DATABASE NIPPONLIFE_DEMO_DB'); cur.execute('USE WAREHOUSE NIPPONLIFE_DEMO_WH')
for f in ['sql/08_views.sql', 'sql/09_cortex_search.sql', 'sql/10_semantic_view.sql']:
    import pathlib
    for stmt in pathlib.Path(f).read_text().split(';'):
        s = stmt.strip()
        if s and not s.startswith('--') and not s.startswith('USE'):
            try: cur.execute(s)
            except Exception as e: print(f'  Warning: {e}')
conn.close()
"
```

> **Note**: `09_cortex_search.sql` と `10_semantic_view.sql` は snow CLI でも直接実行できますが、`{}` を含む場合は Python 経由を推奨。

### 4. Streamlit デプロイ

```bash
cd streamlit
snow streamlit deploy --replace \
  --connection $CONN \
  --dbname NIPPONLIFE_DEMO_DB \
  --schemaname RAW
```

**アプリ URL**:  
`https://app.snowflake.com/SFSEAPAC/kmot_demo1/#/streamlit-apps/NIPPONLIFE_DEMO_DB.RAW.NIPPONLIFE_SALES_DEMO`

### 5. Cortex Agent 作成

```bash
SKILL_DIR="/Applications/Cortex Code.app/Contents/Resources/app/resources/snowflake/skills/cortex-code-skills/cortex-agent"

uv run --project "$SKILL_DIR" python "$SKILL_DIR/scripts/create_or_alter_agent.py" create \
  --agent-name NIPPONLIFE_SALES_AGENT \
  --config-file si_agent/agent_spec.json \
  --database NIPPONLIFE_DEMO_DB \
  --schema RAW \
  --role ACCOUNTADMIN \
  --connection $CONN
```

---

## 📊 データ構成

| テーブル | 件数 | 内容 |
|---------|------|------|
| `T_CUSTOMER_COMPANIES` | 20社 | 従業員2,000名以上の実在大企業 |
| `T_INSURANCE_PRODUCTS` | 14商品 | 日本生命公式サイト準拠 |
| `T_NISSAY_SERVICES` | 5サービス | Wellness-Star・Biz-Create・私募債等 |
| `T_COMPANY_NEWS` | 401件 | 事業イベント分類・保険適合度付き |
| `T_EVENT_ALERTS` | 34件 | 未読アラート（M&A・IPO・経営陣交代等） |
| `T_MEETINGS` | 223件 | 面談記録＋文字起こし |
| `T_FINANCIAL_DATA` | 200件 | 20社×5年分の財務データ |
| `T_PROSPECTS` | 54件 | 見込み管理（AIスコア・ランク付き） |
| `T_COMPANY_LOCATIONS` | 20件 | 本社座標（pydeck地図用） |

---

## 🗂 リポジトリ構造

```
nipponlife-hojin-demo/
├── README.md
├── sql/
│   ├── 00_setup.sql          # DB / WH / スキーマ / ロール
│   ├── 01_ddl.sql            # 全 16 テーブル定義
│   ├── 02_master_data.sql    # 20社・14商品・5サービス・チェックリスト
│   ├── 03_generate_data.py   # ニュース・面談・財務・見込みデータ生成
│   ├── 08_views.sql          # 分析ビュー × 3
│   ├── 09_cortex_search.sql  # Cortex Search × 3
│   └── 10_semantic_view.sql  # SV_SALES_ANALYTICS
├── streamlit/
│   ├── snowflake.yml
│   ├── environment.yml
│   ├── main.py
│   └── pages/
│       ├── 01_alert.py       # 事業イベントアラート
│       ├── 02_meeting.py     # 面談録音・要約・会話ログ分析
│       ├── 03_prospect.py    # 見込み管理
│       ├── 04_matching.py    # 商品マッチング
│       ├── 05_proposal.py    # 提案書自動生成
│       ├── 06_market.py      # マーケット・インサイト
│       └── 07_prepare.py     # 面談前準備
├── si_agent/
│   ├── agent_spec.json       # Cortex Agent 設定
│   ├── demo_scenarios.md     # デモシナリオ集（7シナリオ）
│   └── README.md             # エージェント設定ガイド
└── docs/
    └── nipponlife_demo_design.md  # 設計書 v3.0
```

---

## ⚙️ Snowflake オブジェクト一覧

| オブジェクト | 場所 | 説明 |
|-------------|------|------|
| `NIPPONLIFE_DEMO_WH` | – | デモ用ウェアハウス（Medium） |
| `NIPPONLIFE_DEMO_DB.RAW` | スキーマ | テーブル・Streamlit |
| `NIPPONLIFE_DEMO_DB.ANALYTICS` | スキーマ | ビュー・Semantic View |
| `NIPPONLIFE_DEMO_DB.SEARCH` | スキーマ | Cortex Search |
| `V_PROSPECT_DASHBOARD` | ANALYTICS | 見込みダッシュボードビュー |
| `V_EVENT_ALERT_PRIORITY` | ANALYTICS | アラート優先度ビュー |
| `V_MARKET_INSIGHT` | ANALYTICS | 市場シグナルビュー |
| `CUSTOMER_INFO_SEARCH` | SEARCH | 面談記録の全文検索 |
| `NEWS_SEARCH` | SEARCH | 企業ニュースの全文検索 |
| `PRODUCT_SEARCH` | SEARCH | 保険商品・サービスの全文検索 |
| `SV_SALES_ANALYTICS` | ANALYTICS | Cortex Analyst 用 Semantic View |
| `NIPPONLIFE_SALES_AGENT` | RAW | Cortex Agent（4ツール） |
| `NIPPONLIFE_SALES_DEMO` | RAW | Streamlit on Snowflake |

---

*作成: Snowflake SE チーム | 最終更新: 2026年5月4日*
