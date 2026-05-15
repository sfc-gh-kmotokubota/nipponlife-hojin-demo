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
| 2 | `02_prepare.py` | 🎯 面談前準備 | 企業ブリーフィング1クリック生成・想定Q&A自動作成 |
| 3 | `03_meeting.py` | 🎙 面談録音・要約 | 音声/会話ログ対応・AI要約・コンプライアンス検知・SF登録 |
| 4 | `04_prospect.py` | 📊 見込み管理 | カンバンボード・昇格チェックリスト・1クリック昇格 |
| 5 | `05_matching.py` | 🔍 商品マッチング | 4軸説明可能AIスコアリング + AI深掘り分析 |
| 6 | `06_proposal.py` | 📄 DP自動生成 | ディスカッションペーパー・PPTX/Word対応 |
| 7 | `07_market.py` | 📈 マーケット・インサイト | 金利・株価データで提案タイミングを分析 |

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
| `generate_proposal_pptx` | Generic (SP) | PowerPoint 提案書生成 → presigned URL |
| `generate_proposal_docx` | Generic (SP) | Word 提案書生成 → presigned URL |

デモシナリオ集: `si_agent/demo_scenarios.md`（7つのマルチターン会話シナリオ）

---

## 🚀 セットアップ手順（ワンクリック）

### 前提条件

- Snowflake アカウント（ACCOUNTADMIN ロール）
- Snowflake CLI (`snow`) v3.14+
- Python 3.9+ + `snowflake-connector-python`
- `~/.snowflake/connections.toml` に接続設定済み

### デプロイ（1コマンド）

```bash
SNOWFLAKE_CONNECTION_NAME=<接続名> python3 setup.py
```

これで以下が全て自動で実行されます：
1. DB / WH / スキーマ / ロール作成
2. 16 テーブル DDL 作成
3. マスターデータ投入（20社・14商品・5サービス）
4. ダミーデータ生成（ニュース400件・面談160件・見込み50件 等）
5. 分析ビュー 3 件作成
6. Cortex Search サービス 3 件作成
7. Semantic View 作成（YAML 経由）
8. Streamlit アプリ（7ページ）デプロイ
9. Cortex Agent（6ツール + 2スキル）作成
10. PPTX/Word 生成ストアドプロシージャ作成

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
