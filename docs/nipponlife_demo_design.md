# 日本生命 法人営業企画部向け Snowflake デモ 設計書

**作成日**: 2026年4月30日  
**バージョン**: v3.0（Databricks完全対抗・コンプライアンス検知・Salesforce連携・Web Search追加）  
**対象**: 日本生命保険相互会社 法人部 営業企画部  
**用途**: 社内デモ検討・実装設計

---

## 目次

1. [プロジェクト概要](#1-プロジェクト概要)
2. [競合分析（vs Databricks）](#2-競合分析vs-databricks)
3. [想定ユーザー・デモシナリオ概要](#3-想定ユーザーデモシナリオ概要)
4. [機能一覧 & ツール割り当て](#4-機能一覧--ツール割り当て)
5. [アーキテクチャ設計](#5-アーキテクチャ設計)
6. [ダミーデータ設計](#6-ダミーデータ設計)
7. [Snowflake Intelligence（SI）設計](#7-snowflake-intelligencesi設計)
8. [Streamlit アプリ設計](#8-streamlit-アプリ設計)
9. [60分デモシナリオ（タイムライン）](#9-60分デモシナリオタイムライン)
10. [競合差別化ポイント（vs Databricks 詳細）](#10-競合差別化ポイントvs-databricks-詳細)
11. [実装ロードマップ](#11-実装ロードマップ)
12. [技術スタック一覧](#12-技術スタック一覧)
13. [UI/UX デザイン設計（hokan / SFA 参考）](#13-uiux-デザイン設計hokan--sfa-参考)
14. [地図データ設計（pydeck）](#14-地図データ設計pydeck)
15. [★ データシェアリング設計（財務企画部 × 法人営業部）](#15--データシェアリング設計財務企画部--法人営業部)

---

## 1. プロジェクト概要

### 1.1 目的

日本生命保険相互会社（以下「日本生命」）の法人営業企画部が主導する、大企業向け法人営業の高度化・DX推進を支援するデモを構築する。具体的には以下の 2 点を目的とする。

1. **日本生命の営業生産性向上**: 大企業顧客担当の営業が、AI・データ活用によりより質の高い提案を効率的に実施できる環境を示す
2. **Snowflake Platform の優位性訴求**: Databricks（Databricks Apps + Genie）との競合状況において、Snowflake Intelligence・Streamlit・Cortex Code の組み合わせが生命保険営業DXにとって最適であることを証明する

### 1.2 背景・競合状況

法人営業企画部は現在 Databricks のアプローチを受けており、特に以下の 2 つのプロダクトに興味を示している：

- **Databricks Apps**: 業務アプリケーションの迅速な構築
- **Databricks Genie**: 自然言語によるデータ分析・AI エージェント機能

Snowflake としては、以下のプロダクト群でこれを上回るユーザー体験・ガバナンス・業務適合性を示す必要がある：

- **Snowflake Intelligence**: AI エージェント・会話型分析
- **Streamlit on Snowflake**: ノーコードデプロイ可能なビジネスアプリ
- **Cortex AI Functions**: AI_COMPLETE / AI_SUMMARIZE / AI_EXTRACT 等
- **Cortex Search**: 全文検索・RAG
- **Cortex Analyst**: テキスト to SQL の自然言語分析

### 1.3 訴求ポイント（3本柱）

| 柱 | メッセージ |
|---|----------|
| **All-in-One** | データ管理・AI・アプリが 1 プラットフォームに統合。MCP サーバー等の外部サービス不要 |
| **金融機関のセキュリティ完結** | Web 検索・AI 処理・顧客データが全て Snowflake ネットワーク内で完結。顧客の会話が外部に漏れない |
| **営業担当者ファースト** | エンジニア不要・4〜5時間でデモ実装。Cortex Code がコード生成を支援 |

> **v3.0 追加訴求**: 白倉さんからのメール（2026/4/30）で、競合他社（Databricks と推測）が ①面談前②面談中③面談後の業務フローに沿ったデモを見せたことが判明。本設計書は同等機能を全てカバーした上で、**コンプライアンス検知・Salesforce連携・Web Search のネイティブ対応**で上回る。

---

## 2. 競合分析（vs Databricks）

### 2.0 競合デモの実態把握（2026年4月 情報）

> 日本生命 法人情報センター 白倉氏のメールにより、競合他社（Databricks と推測）が見せたデモの内容が判明した。以下に **各機能の Snowflake による完全対応マトリクス**を示す。

| # | 競合が見せた機能 | Snowflake 対応 | 優位性 |
|---|--------------|--------------|-------|
| 1 | 顧客リストと優先順位（A〜D）表示 | Streamlit 見込みカンバン（App3） | ✅ 既存対応 |
| 2 | **情報収集ボタン → MCP サーバーで Web 検索** | **Cortex Agent Web Search（MCP 不要・ネイティブ）** | ✅✅ **MCP 不要かつセキュリティ完結** |
| 3 | 財務ダッシュボード（売上・利益） | Streamlit + Cortex Analyst | ✅ 既存対応 |
| 4 | 商品マッチング AI スコア（降順） | Cortex AI スコアリング + Streamlit | ✅ 既存対応 |
| 5 | 提案書（既存 PPTX テンプレに情報反映） | **Streamlit + python-pptx（PPTX 生成に強化）** | ✅ v3.0 強化 |
| 6 | 想定 QA（約款対応） | Cortex Search（約款 PDF）+ SI | ✅ 既存対応 |
| 7 | 見込み顧客管理（C→B） | Streamlit 見込みカンバン | ✅ 既存対応 |
| 8 | シンプル UI（ボタン式） | Streamlit on Snowflake | ✅ 既存対応 |
| 9 | **面談中コンプライアンス懸念の会話を検出・表示** | **AI_CLASSIFY + Cortex Agent（F-11）** | ✅✅ **v3.0 新規追加** |
| 10 | 面談中推奨アクション（リアルタイム） | Cortex Agent リアルタイムサジェスト（F-04） | ✅ 既存対応 |
| 11 | 面談後 PPTX・Word 生成（ボタン 1 つ） | Streamlit + python-pptx / python-docx | ✅ v3.0 強化 |
| 12 | AIが次回宿題・タスク表示 | Cortex Agent + T_NEXT_ACTIONS（F-02） | ✅ 既存対応 |
| 13 | **Salesforce 登録ボタン** | **Salesforce REST API 連携（F-12）** | ✅✅ **v3.0 新規追加** |
| 14 | 壁打ちチャットボット | Snowflake Intelligence（F-09） | ✅ 既存対応 |

**結論**: 競合が見せた 14 機能を **全て Snowflake でカバー**。さらに以下 3 点で上回る：
1. **Web Search**: MCP サーバー不要・Snowflake ネイティブ → 金融機関として情報漏洩リスクがない
2. **コンプライアンス検知**: 保険業法対応の禁止表現をリアルタイム検出 → 競合にはない機能
3. **セキュリティ一気通貫**: 全処理が Snowflake 内で完結 → 顧客の会話データが外部サービスに流れない

### 2.1 機能比較表

| 比較軸 | Databricks | Snowflake | 判定 |
|-------|-----------|-----------|------|
| 自然言語 AI エージェント | Genie（汎用） | Snowflake Intelligence（業務特化） | **SF優位** |
| ビジネスアプリ構築 | Databricks Apps | Streamlit on Snowflake（ノーデプロイ） | **SF優位** |
| データガバナンス | Unity Catalog | Snowflake Horizon（成熟度高） | **SF優位** |
| ML/モデル管理 | MLflow | Snowflake Model Registry + Cortex ML | 互角 |
| ドキュメント AI | Delta Lake + LLM | Document AI + Cortex Functions | **SF優位** |
| リアルタイム処理 | Delta Live Tables | Dynamic Tables + Streams | 互角 |
| セキュリティ・規制対応 | 要設定 | ネイティブ対応（金融業界実績） | **SF優位** |
| 日本語 LLM 対応 | 限定的 | Mistral / Llama / Arctic 選択可 | **SF優位** |
| 営業担当者の自走利用 | エンジニア依存 | SI / Streamlit でノーコード | **SF優位** |
| エコシステム | Databricks Marketplace | Snowflake Marketplace（1,500+） | **SF優位** |

### 2.2 日本生命案件における Snowflake の強み

1. **保険業界特有のデータガバナンス要件** に対し Snowflake の Column-level Security・Row Access Policy・Data Masking が即対応
2. **監査ログの完全性**: Snowflake の ACCESS HISTORY・QUERY HISTORY は金融機関の内部監査要件を満たす
3. **個人情報保護**: Cortex Functions の AI 処理は Snowflake ネットワーク内で完結（外部 LLM に個人データを送信しない設計が可能）
4. **既存 Salesforce/基幹システムとの連携**: Snowflake Native Connectors による即時接続

---

## 3. 想定ユーザー・デモシナリオ概要

### 3.1 ペルソナ設定

| 属性 | 詳細 |
|-----|------|
| **氏名** | 山田 太郎（仮） |
| **所属** | 日本生命保険相互会社 法人部 第三営業課 シニア営業担当 |
| **担当企業数** | 大手企業 **20 社**（従業員 2,000 名以上・製造・商社・IT通信・金融・エネルギー・小売・建設・物流・製薬・航空・不動産・鉄鋼・食品・鉄道・化学） |
| **経験年数** | 12 年 |
| **課題** | 担当先の事業イベント（M&A・役員交代・大規模採用）を見逃して提案機会を逃すことがある。商談件数が多く準備時間も不足 |
| **スキル** | PC 操作は標準的。専門ツールへの抵抗感あり |

### 3.2 企業向け保険営業における「勝ちパターン」

法人保険営業において、**提案が成功するタイミングはほぼ決まっている**。その「トリガーイベント」をいち早く察知し、最速でアプローチできるかが勝負の分かれ目。

```
《保険ニーズが急増する事業イベント》

  M&A・合併 ──────────────────── 従業員保険・年金制度の統合再設計
  新規上場（IPO）────────────── 役員退職慰労金・D&O保険・内部統制整備
  経営陣交代（CEO/CFO/CHRO）── 新任者との関係構築・既存契約見直し
  大規模採用計画発表 ─────────── 団体保険の適用対象拡大・保険料増額
  海外展開・現地法人設立 ────── 海外勤務者保険・グローバル保険設計
  大型設備投資・新工場建設 ──── 従業員増・事故リスク増 → 保険拡大
  退職給付制度改定発表 ───────── DB→DC 移行支援・積立不足解消提案
  健康経営認定申請・取得 ────── GLTD・団体医療保険への投資意欲が高い
  中期経営計画発表 ────────────── 人材投資方針から保険ニーズを先読み
  業績悪化・リストラ発表 ────── コスト最適化提案 or 経営安定化保険
```

### 3.3 主要デモシーン

**デモのメインシーン**: 日本生命の山田担当が、担当先 **20 社**のニュースを AI が自動検知・アラートし、最優先でアプローチすべき企業と提案内容をその場で生成するシナリオ

**デモ全体のストーリーライン**:
```
[朝] 事業イベントアラート確認（新機能）
  → AI が昨夜の全担当先ニュースをスキャン
  → トヨタが海外 EV 合弁会社設立を発表 → 「海外勤務者保険の提案機会」とアラート
  
[商談前準備]
  → 企業情報収集（SI）+ 事前 QA 生成（SI）
  
[当日 商談中] 
  → 面談リアルタイムサジェスト（SI）
  
[当日 商談後]
  → 音声録音・要約（Streamlit）
  → 次回アクション提案（SI）
  
[翌週 フォロー準備]
  → 見込みランク分析（Streamlit）
  → 企業ニーズ分析・商品提案（Streamlit + SI）
  → 提案書自動生成（Streamlit）
  
[随時]
  → 壁打ちチャットボット（SI）
```

---

## 4. 機能一覧 & ツール割り当て

### 4.1 機能マッピング表

| # | 機能名 | 主ツール | 補助ツール | デモ優先度 | 想定デモ時間 |
|---|--------|---------|-----------|-----------|------------|
| F-01 | 面談音声録音・要約 | Streamlit | Cortex AI (AI_SUMMARIZE) | ★★★ | 6分 |
| F-02 | 面談後次回アクション提案・振り返り | Snowflake Intelligence | Cortex Search | ★★★ | 5分 |
| F-03 | 見込み管理高度化（C→B昇格支援） | Streamlit | Cortex Analyst | ★★★ | 6分 |
| F-04 | 面談リアルタイムサジェスト | Snowflake Intelligence | Cortex Search | ★★ | 4分 |
| F-05 | 提案書自動作成（**Word + PPTX 両対応**） | Streamlit | AI_COMPLETE | ★★★ | 7分 |
| F-06 | 企業情報収集・資料作成 | Snowflake Intelligence | Cortex Search + Document AI | ★★★ | 7分 |
| F-07 | 企業ニーズ分析（商品マッチング） | Streamlit + SI | Cortex Analyst | ★★★ | 6分 |
| F-08 | 商談前事前QA提示 | Snowflake Intelligence | Cortex Search | ★★ | 4分 |
| F-09 | 壁打ちチャットボット | Snowflake Intelligence | 全ツール | ★★ | 4分 |
| **F-10** | **事業イベント検知・アラート** | **Streamlit + SI** | **Cortex Search / Streams** | **★★★** | **7分** |
| **F-11a** | **面談中コンプライアンス検知（リアルタイム）** | **Snowflake Intelligence** | **compliance_check Tool + AI_CLASSIFY** | **★★★** | **（SI 内で都度チェック）** |
| **F-11b** | **面談後コンプライアンス一括分析** | **Streamlit（App1）** | **AI_CLASSIFY バッチ** | **★★** | **（面談録音の事後分析）** |
| **F-12** | **Salesforce 自動登録** | **Streamlit + REST API** | **Snowflake Secret** | **★★★** | **（F-01に統合）** |
| **F-13** | **マーケットデータ連携・金利株価ダッシュボード** | **Streamlit App6 + SI** | **Snowflake Data Sharing / plotly** | **★★★** | **（S-00に統合）** |

**合計**: 約 56 分（イントロ・まとめ 4 分追加で 60 分）。F-11・F-12 は App1（面談録音・要約）画面内に統合して実装。

### 4.2 ツール別機能分類

**Snowflake Intelligence (SI) が主担当する機能**:
- F-02: 面談後振り返り・次回アクション提案
- F-04: 面談中リアルタイムサジェスト
- F-06: 企業情報収集・資料作成（ワークフロー出力）
- F-08: 商談前事前QA生成
- F-09: 壁打ちチャットボット

**Streamlit on Snowflake が主担当する機能**:
- F-01: 音声録音アップロード・要約表示
- F-03: 見込み管理ダッシュボード（AIスコアリング可視化）
- F-05: 提案書自動生成（Word/PDF ダウンロード）
- F-07: 企業ニーズ分析・商品レコメンド表示
- F-10: 事業イベントアラートダッシュボード（★新機能）

---

## 5. アーキテクチャ設計

### 5.1 全体アーキテクチャ図

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         Snowflake Platform                                    ║
║                                                                                ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │                        Data Layer (Snowflake Storage)                   │  ║
║  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────────┐  │  ║
║  │  │顧客企業マスタ │ │面談録・要約  │ │見込み管理DB │ │保険商品マスタ │  │  ║
║  │  └──────────────┘ └──────────────┘ └──────────────┘ └───────────────┘  │  ║
║  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────────┐  │  ║
║  │  │企業ニュース  │ │財務データ   │ │統合報告書   │ │★事業イベント │  │  ║
║  │  │(リアルタイム)│ │(公開IR)     │ │(PDFチャンク)│ │  アラートDB  │  │  ║
║  │  └──────────────┘ └──────────────┘ └──────────────┘ └───────────────┘  │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
║                                       │                                        ║
║  ┌─────────────────────┐              │          ┌─────────────────────────┐  ║
║  │  Cortex AI Layer    │◄─────────────┤          │  Search & Analytics     │  ║
║  │  AI_COMPLETE        │              │          │  Cortex Search ×3       │  ║
║  │  AI_SUMMARIZE       │              │          │  Cortex Analyst         │  ║
║  │  AI_EXTRACT         │              │          │  (Semantic View)        │  ║
║  │  Document AI (PDF)  │              │          └─────────────────────────┘  ║
║  └─────────────────────┘              │                    │                   ║
║           │                           │                    │                   ║
║  ┌────────┴──────────────────────────┴────────────────────┴────────────────┐  ║
║  │                    Application Layer                                      │  ║
║  │  ┌──────────────────────────────┐    ┌──────────────────────────────┐   │  ║
║  │  │   Snowflake Intelligence     │    │   Streamlit on Snowflake     │   │  ║
║  │  │   (Cortex Agent)             │    │                              │   │  ║
║  │  │  - 企業情報収集ツール        │    │  App1: 面談録音・要約        │   │  ║
║  │  │  - ニュース検索ツール        │    │  App2: 事業イベントアラート  │   │  ║
║  │  │  - 統合報告書検索ツール      │    │  App3: 見込み管理            │   │  ║
║  │  │  - 面談要約ツール            │    │  App4: 企業ニーズ分析        │   │  ║
║  │  │  - KPI分析ツール             │    │  App5: 提案書自動生成        │   │  ║
║  │  │  - イベント検知ツール(新)    │    │                              │   │  ║
║  │  └──────────────────────────────┘    └──────────────────────────────┘   │  ║
║  └────────────────────────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════════════╝

外部データ入力（全て公開情報）:
  ┌─────────────────────────────────────────────────────────┐
  │  日経新聞/Bloomberg/Reuters RSS → Snowpipe/Streams      │
  │  東証適時開示情報（EDINET API）→ Snowpipe              │
  │  統合報告書 PDF → Document AI + Cortex Search          │
  │  有価証券報告書 → Snowpipe → 財務テーブル              │
  │  音声ファイル (.wav/.mp3) → Whisper API / Cortex       │
  └─────────────────────────────────────────────────────────┘
```

### 5.2 Snowflake オブジェクト構成

```
DATABASE: NIPPONLIFE_DEMO_DB
├── SCHEMA: RAW
│   ├── T_CUSTOMER_COMPANIES       -- 顧客企業マスタ（実在企業 20 社）
│   ├── T_CONTACTS                 -- 先方担当者マスタ
│   ├── T_SALES_REPS               -- 日本生命 営業担当者マスタ
│   ├── T_MEETINGS                 -- 面談ヘッダ
│   ├── T_MEETING_TRANSCRIPTS      -- 面談文字起こし
│   ├── T_MEETING_SUMMARIES        -- AI生成済み要約
│   ├── T_PROSPECTS                -- 見込み管理
│   ├── T_INSURANCE_PRODUCTS       -- 保険商品マスタ（14商品・実サイト準拠）
│   ├── T_NISSAY_SERVICES          -- ★非保険サービスマスタ（5サービス）
│   ├── T_CONTRACTS                -- 既存契約
│   ├── T_NEXT_ACTIONS             -- 次回アクション管理
│   ├── T_COMPANY_NEWS             -- 企業ニュース（定期取込）
│   ├── T_FINANCIAL_DATA           -- 企業財務情報（5年分）
│   ├── T_INTEGRATED_REPORTS       -- 統合報告書テキストチャンク
│   ├── T_CERTIFIED_INFO           -- 優良認定情報
│   ├── T_PROPOSALS                -- 提案書メタデータ
│   └── T_EVENT_ALERTS             -- ★事業イベントアラート
│   └── T_COMPANY_LOCATIONS        -- ★企業拠点情報（地図用）
│
├── SCHEMA: ANALYTICS
│   ├── V_PROSPECT_DASHBOARD        -- 見込み管理ビュー
│   ├── V_CUSTOMER_360              -- 顧客360度ビュー
│   ├── V_EVENT_ALERT_PRIORITY      -- ★アラート優先度ビュー（新）
│   └── SV_SALES_ANALYTICS          -- Semantic View (Cortex Analyst用)
│
├── SCHEMA: SEARCH
│   ├── CUSTOMER_INFO_SEARCH        -- Cortex Search（顧客・面談情報）
│   ├── NEWS_SEARCH                 -- Cortex Search（ニュース・開示情報）
│   └── INTEGRATED_REPORT_SEARCH   -- Cortex Search（統合報告書）
│
└── SCHEMA: AI
    ├── UDF_SUMMARIZE_MEETING()     -- 面談要約UDF
    ├── UDF_SCORE_PROSPECT()        -- 見込みスコアリングUDF
    ├── UDF_GENERATE_PROPOSAL()     -- 提案書ドラフト生成UDF
    └── UDF_DETECT_EVENTS()         -- ★イベント検知・分類UDF（新）
```

### 5.3 実行環境（v3.0 推奨: デモアカウント SFSEAPAC-KMOT_AWS1）

> **v3.0 重要変更**: 競合（Databricks）への対抗上、**Cortex Agent Web Search・Skills・External Network Access（Salesforce API）**が必須となった。これらはトライアルアカウントでは制限されるため、**デモアカウント（SFSEAPAC-KMOT_AWS1）の使用を強く推奨**する。SPCS は引き続き不使用（Warehouse ベースで統一）。

| コンポーネント | トライアル | デモアカウント | 用途 |
|-------------|-----------|-------------|------|
| **Cortex Agent Web Search** | ⚠ 制限あり | ✅ フル機能 | 企業情報リアルタイム収集（MCP不要） |
| **Cortex Agent Skills** | ⚠ 制限あり | ✅ フル機能 | ツール呼び出し・外部連携 |
| **External Network Access** | ❌ 不可 | ✅ | Salesforce REST API 連携（F-12） |
| LLM モデル（mistral-large2等） | ⚠ 一部 | ✅ 全モデル | 日本語精度の高いモデルを選択 |
| Snowflake Intelligence（SI） | ⚠ 基本のみ | ✅ フル機能 | エージェント全機能 |
| Streamlit on Snowflake | ✅ | ✅ | Warehouse ベースで動作 |
| Cortex Search | ✅ | ✅ | 全文検索・RAG |
| pydeck 地図 | ✅ | ✅ | API キー不要 |
| python-docx / python-pptx | ✅ | ✅ | Word・PPTX 提案書生成 |
| AI_CLASSIFY（コンプライアンス） | ✅ | ✅ | Warehouse 上で実行 |
| Snowpark Container Services | ❌ 不使用 | — | 引き続き不使用（Warehouse 統一） |

---

## 6. ダミーデータ設計

> **設計方針**: ニュース・財務・統合報告書は全て公開情報を元にしたデモデータのため、**実在の日本の大手企業名を使用**する。具体的なニュース内容はデモ用のサンプルテキスト（架空の日付・金額を含む）とするが、企業の特性・業種・従業員規模は実態に即した値を設定する。

### 6.1 対象企業 20 社（実在企業名・従業員 2,000 名以上）

> **日本生命の大企業定義**: 従業員 2,000 名以上。本デモでは山田担当者が 20 社を担当するシナリオ。実在企業の公開情報（従業員数・業種）に基づくが、契約内容・見込み金額はデモ用の想定値。

| # | 企業名 | 業種 | 従業員数 | 主要保険ニーズ | 見込みランク | 担当年数 | ティッカー |
|---|--------|------|---------|--------------|------------|---------|---------|
| 1 | トヨタ自動車(株) | 製造（自動車） | 72,700 | DC・海外勤務者保険・GLTD | **B** | 8年 | 7203.T |
| 2 | パナソニック ホールディングス(株) | 製造（電機） | 63,400 | グループ再編後の保険統合・年金再設計 | **A** | 5年 | 6752.T |
| 3 | 伊藤忠商事(株) | 総合商社 | 44,500 | M&A後保険統合・海外勤務者・役員退職慰労金 | **A** | 10年 | 8001.T |
| 4 | NTTデータグループ(株) | IT・デジタル | 190,000 | 大規模採用に伴う団体保険拡大・健康経営 | **B** | 3年 | 9613.T |
| 5 | 野村ホールディングス(株) | 金融・証券 | 26,000 | 役員退職慰労金・事業保障・D&O保険連携 | **B** | 7年 | 8604.T |
| 6 | JERA(株) | エネルギー | 5,100 | 大型設備投資後の従業員増・リスク拡大対応 | **C** | 2年 | — |
| 7 | イオン(株) | 小売・流通 | 306,000 | 大規模パート→正社員転換・福利厚生整備 | **B** | 6年 | 8267.T |
| 8 | 住友商事(株) | 総合商社 | 48,200 | 海外子会社拡張・中計発表後の人材投資 | **C** | 1年 | 8053.T |
| 9 | 鹿島建設(株) | インフラ・建設 | 21,800 | 海外大型プロジェクト受注・労災補完保険 | **C** | 4年 | 1812.T |
| 10 | 日本郵船(株) | 物流・海運 | 36,000 | 脱炭素投資に伴う大型設備・雇用変化対応 | **B** | 5年 | 9101.T |
| 11 | 武田薬品工業(株) | 製薬・ライフサイエンス | 14,000 | グローバル高スキル人材のGLTD・海外勤務者保険・DC強化 | **B** | 2年 | 4502.T |
| 12 | ANAホールディングス(株) | 航空・旅行 | 44,000 | コロナ後の大規模採用再開・団体保険拡大・健康経営 | **C** | 新規 | 9202.T |
| 13 | セブン＆アイ・ホールディングス(株) | 流通・コンビニ | 130,000 | 北米法人（7-Eleven）海外勤務者保険・パート正社員化 | **B** | 3年 | 3382.T |
| 14 | KDDI(株) | 通信・IT | 48,000 | IT人材採用強化・GLTD・健康経営優良法人申請 | **A** | 6年 | 9433.T |
| 15 | 三菱地所(株) | 不動産・開発 | 10,000 | 大丸有再開発プロジェクト・役員退職慰労金 | **C** | 1年 | 8802.T |
| 16 | 日本製鉄(株) | 鉄鋼・素材 | 51,000 | USスチール買収後の海外勤務者保険統合・大型設備投資 | **B** | 4年 | 5401.T |
| 17 | 三井住友フィナンシャルグループ(株) | 銀行・金融 | 40,000 | 金融規制強化・役員保護・グループ再編保険統合 | **B** | 8年 | 8316.T |
| 18 | サントリーホールディングス(株) | 飲料・食品 | 40,000 | ★IPO準備中（役員退職慰労金保険・D&O緊急提案）・海外M&A統合 | **C** | 新規 | 非上場 |
| 19 | 東日本旅客鉄道(株) | 鉄道・インフラ | 70,000 | DX/MaaS人材大規模採用・大型設備投資・健康経営 | **B** | 5年 | 9020.T |
| 20 | 旭化成(株) | 化学・素材・電子 | 45,000 | EV車載材料・半導体設備投資拡大・海外展開保険 | **B** | 3年 | 3407.T |

**ランク分布**: S: 0社 / A: 3社（パナHD・伊藤忠・KDDI）/ B: 11社 / C: 6社（うち新規2社）  
**業種カバレッジ**: 製造・商社・IT通信・金融・エネルギー・小売・建設・物流・製薬・航空・不動産・鉄鋼・食品・鉄道・化学  
**★デモの目玉**: サントリーHD（IPO準備中・最高優先アラート）・日本製鉄（USスチール買収）・ANA（大規模採用再開）

### 6.2 事業イベント × 保険ニーズ マッピング（核心的な設計）

企業営業において最も重要な「今アプローチすべき理由」を AI が自動検知するための事業イベントカテゴリと、それに対応する保険商品のマッピング。

| イベントカテゴリ | 代表的な事例 | 主な保険ニーズ | アラート優先度 |
|---------------|-----------|-------------|-------------|
| **M&A・経営統合** | 子会社設立、他社買収、JV設立 | 被買収企業の福利厚生統合、年金制度再設計、従業員間の保険格差解消 | **最高** |
| **新規上場（IPO）** | 上場申請、上場承認 | 役員退職慰労金保険、D&O補完保険、内部統制強化に伴う役員保護 | **最高** |
| **経営陣交代** | CEO/CFO/CHRO/CHO 交代 | 新任者との関係再構築、既存契約見直し提案、新経営方針に合わせた保険設計 | **高** |
| **大規模採用計画** | 中途採用1000人超、新卒採用増、正社員化 | 団体定期保険の被保険者数増加対応、保険料見直し、GLTD適用拡大 | **高** |
| **海外展開・現地法人設立** | 海外子会社設立、海外工場建設 | 海外勤務者保険、ビジネストラベル保険、グローバル年金設計 | **高** |
| **大型設備投資・新工場建設** | 工場新設、データセンター建設 | 従業員増加に伴う保険拡大、労働災害補完保険、重機・プラント事故リスク | **中** |
| **退職給付制度改定** | DB年金の見直し、DC移行計画 | DC移行支援、積立不足解消提案、年金資産運用見直し | **高** |
| **健康経営認定取得・申請** | 優良法人ホワイト500申請、くるみん取得 | GLTD（就労不能保険）、団体医療保険、メンタルヘルス対応 | **中** |
| **中期経営計画発表** | 新中計公表、人材投資方針発表 | 計画内の人材投資・福利厚生強化から保険ニーズを先読み | **中** |
| **業績変化・リストラ** | 大幅黒字化、赤字転落、人員削減 | コスト最適化提案（黒字時）or 経営安定化保険強化（赤字時） | **中** |
| **グループ再編・分社化** | 持株会社化、子会社独立 | グループ保険の再設計、保険移行手続き支援 | **最高** |

### 6.3 ニュースデータサンプル（各社 20 件、計 200 件）

デモ用ニュースは以下の構造で作成し、**EVENT_TYPE** と **INSURANCE_RELEVANCE** を必ず付与する：

```
【トヨタ自動車】サンプルニュース（5件）
─────────────────────────────────────────────────────────────
① 2025/10/15 | EVENT_TYPE: M&A | INSURANCE_RELEVANCE: 最高
  「トヨタ自動車、北米EV合弁会社を設立 従業員3,200名」
  → アラートコメント: 海外勤務者保険（新会社従業員対象）の提案機会。
    合弁会社の福利厚生制度整備を急ぐ見込み。

② 2025/10/08 | EVENT_TYPE: 経営陣交代 | INSURANCE_RELEVANCE: 高
  「トヨタ自動車、来春より新CHROに鈴木氏が就任予定と発表」
  → アラートコメント: 新CHRO着任前にアポを設定し、福利厚生見直し提案の打ち合わせを。

③ 2025/09/20 | EVENT_TYPE: 大規模採用 | INSURANCE_RELEVANCE: 高
  「トヨタ、ソフトウェア人材2,000人の追加採用計画を発表」
  → アラートコメント: 採用完了後、団体定期保険の被保険者拡大手続きが必要。

④ 2025/09/05 | EVENT_TYPE: 健康経営 | INSURANCE_RELEVANCE: 中
  「トヨタ自動車、4年連続 健康経営優良法人ホワイト500 認定」
  → アラートコメント: 健康経営強化の文脈でGLTD・団体医療の拡充提案を検討。

⑤ 2025/08/10 | EVENT_TYPE: 中期経営計画 | INSURANCE_RELEVANCE: 中
  「トヨタ、新中期経営計画で人的資本投資1兆円・全従業員研修義務化」
  → アラートコメント: 従業員保護意識の高まりを踏まえ、総合福祉団体定期の見直しを提案。
```

### 6.4 テーブル定義詳細

#### T_CUSTOMER_COMPANIES（顧客企業マスタ）
```sql
CREATE TABLE T_CUSTOMER_COMPANIES (
    COMPANY_ID              VARCHAR(10)   NOT NULL PRIMARY KEY,
    COMPANY_NAME            VARCHAR(100)  NOT NULL,
    COMPANY_NAME_KANA       VARCHAR(100),
    INDUSTRY_LARGE          VARCHAR(50),   -- 大分類
    INDUSTRY_DETAIL         VARCHAR(50),   -- 詳細
    EMPLOYEE_COUNT          INTEGER,
    EMPLOYEE_COUNT_JAPAN    INTEGER,       -- 国内従業員数
    EMPLOYEE_COUNT_OVERSEAS INTEGER,       -- 海外従業員数
    HEADQUARTERS            VARCHAR(100),
    FOUNDED_YEAR            INTEGER,
    ANNUAL_REVENUE_JPY      FLOAT,
    STOCK_MARKET            VARCHAR(20),   -- 東証プライム等
    CREDIT_RATING           VARCHAR(5),
    EMPLOYEE_RETENTION_RATE FLOAT,
    AVERAGE_AGE             FLOAT,
    AVERAGE_SALARY_JPY      INTEGER,
    WELFARE_EXPENSE_RATIO   FLOAT,
    TURNOVER_RATE           FLOAT,
    IS_LISTED               BOOLEAN,
    HAS_OVERSEAS_SUBSIDIARY BOOLEAN,       -- 海外子会社あり
    PENSION_TYPE            VARCHAR(20),   -- DB / DC / 混合
    HEALTH_CERT_STATUS      VARCHAR(50),   -- 健康経営優良法人等
    SALES_REP_ID            VARCHAR(10),
    STOCK_TICKER            VARCHAR(20),   -- 株式ティッカー（'7203.T'等。非上場はNULL）
    CREATED_AT              TIMESTAMP_NTZ,
    UPDATED_AT              TIMESTAMP_NTZ
);
```

#### T_EVENT_ALERTS（事業イベントアラート ★新テーブル）
```sql
CREATE TABLE T_EVENT_ALERTS (
    ALERT_ID               VARCHAR(15)   NOT NULL PRIMARY KEY,
    COMPANY_ID             VARCHAR(10)   NOT NULL,
    DETECTED_AT            TIMESTAMP_NTZ NOT NULL,   -- 検知日時
    NEWS_ID                VARCHAR(15),               -- 元ニュースへの参照
    EVENT_TYPE             VARCHAR(50)   NOT NULL,    -- M&A / IPO / 経営陣交代 / 大規模採用 等
    EVENT_SUMMARY          TEXT          NOT NULL,    -- イベント概要
    INSURANCE_RELEVANCE    VARCHAR(10),               -- 最高 / 高 / 中 / 低
    ALERT_REASON           TEXT,                      -- AI生成「なぜ保険提案機会なのか」
    RECOMMENDED_PRODUCTS   ARRAY,                     -- 推奨商品リスト
    RECOMMENDED_ACTION     TEXT,                      -- AI生成「次にとるべき行動」
    URGENCY_DAYS           INTEGER,                   -- 何日以内にアプローチすべきか
    STATUS                 VARCHAR(20),               -- UNREAD / READ / ACTION_TAKEN / DISMISSED
    SALES_REP_ID           VARCHAR(10),
    CREATED_AT             TIMESTAMP_NTZ,
    UPDATED_AT             TIMESTAMP_NTZ
);
```

#### T_COMPANY_NEWS（企業ニュース）
```sql
CREATE TABLE T_COMPANY_NEWS (
    NEWS_ID                VARCHAR(15)   NOT NULL PRIMARY KEY,
    COMPANY_ID             VARCHAR(10)   NOT NULL,
    NEWS_DATE              DATE          NOT NULL,
    NEWS_SOURCE            VARCHAR(50),   -- '日経新聞' / '東証適時開示' / 'Bloomberg' 等
    HEADLINE               VARCHAR(500)  NOT NULL,
    BODY_TEXT              TEXT,
    EVENT_TYPE             VARCHAR(50),   -- ★事業イベント分類（新フィールド）
    NEWS_CATEGORY          VARCHAR(50),   -- 経営 / M&A / 人事 / 業績 / 社会貢献
    SENTIMENT              VARCHAR(10),   -- POSITIVE / NEUTRAL / NEGATIVE
    INSURANCE_RELEVANCE    VARCHAR(10),   -- 最高 / 高 / 中 / 低
    ALERT_GENERATED        BOOLEAN,       -- アラートを生成済みか
    URL                    VARCHAR(500),
    CREATED_AT             TIMESTAMP_NTZ
);
```

#### T_PROSPECTS（見込み管理）
```sql
CREATE TABLE T_PROSPECTS (
    PROSPECT_ID            VARCHAR(15)   NOT NULL PRIMARY KEY,
    COMPANY_ID             VARCHAR(10)   NOT NULL,
    PRODUCT_ID             VARCHAR(10),
    CURRENT_RANK           CHAR(1)       NOT NULL,   -- S / A / B / C
    PREVIOUS_RANK          CHAR(1),
    PROSPECT_AMOUNT        FLOAT,
    PROBABILITY            FLOAT,
    AI_SCORE               FLOAT,
    AI_SCORE_REASON        TEXT,
    RANKUP_ACTIONS         TEXT,
    LAST_EVENT_TRIGGER     VARCHAR(50),  -- ★最後の見込み変化のトリガーイベント（新）
    LAST_EVENT_DATE        DATE,         -- ★そのイベント発生日
    EXPECTED_CLOSE_DATE    DATE,
    LAST_CONTACT_DATE      DATE,
    DAYS_SINCE_CONTACT     INTEGER,
    SALES_REP_ID           VARCHAR(10),
    CREATED_AT             TIMESTAMP_NTZ,
    UPDATED_AT             TIMESTAMP_NTZ
);
```

#### T_INSURANCE_PRODUCTS（保険商品マスタ）
```sql
CREATE TABLE T_INSURANCE_PRODUCTS (
    PRODUCT_ID             VARCHAR(10)   NOT NULL PRIMARY KEY,
    PRODUCT_NAME           VARCHAR(100)  NOT NULL,
    PRODUCT_CATEGORY       VARCHAR(50),
    TARGET_AUDIENCE        VARCHAR(100),
    MIN_EMPLOYEES          INTEGER,
    DESCRIPTION            TEXT,
    KEY_BENEFITS           ARRAY,
    TRIGGER_EVENTS         ARRAY,        -- ★この商品が刺さるイベント種別リスト（新）
    RENEWAL_CYCLE          VARCHAR(20),
    INDUSTRY_FIT_SCORE     VARIANT,      -- 業種別適合スコア（JSON）
    PRODUCT_BROCHURE_URL   VARCHAR(500),
    CREATED_AT             TIMESTAMP_NTZ
);
```

### 6.5 保険商品マスタ（14商品・日本生命公式サイト準拠）

> **出典**: https://www.nissay.co.jp/hojin/shohin/ の全カテゴリページから収集。商品名・説明・対象・種別は公開情報に基づく。

#### カテゴリ A: 経営者のための保障（4商品）

| # | 商品ID | 商品名（正式） | 主な対象 | 商品の目的・特徴 | 刺さるイベントトリガー |
|---|--------|-------------|---------|----------------|-------------------|
| 1 | P001 | 長期定期保険 | 役員・経営者 | 長期保険期間の死亡保障。役員退職慰労金・事業保障の財源として活用 | 経営陣交代、IPO、業績好調、後継者問題 |
| 2 | P002 | 傷害保障重点期間設定型長期定期保険 | 役員・経営者 | 傷害死亡を重点保障する経営者向け長期定期保険。退職慰労金財源 | 経営陣交代、IPO |
| 3 | P003 | 傷害死亡重点期間設定型介護保障保険 | 役員・経営者 | 傷害死亡保障＋要介護保障。経営者の長期的なリスクを一本化 | 経営陣交代、経営者の高齢化 |
| 4 | P004 | 逓増定期保険 | 役員・経営者 | 保険料一定・保険金額が段階的に増加。事業成長に合わせた保障 | 業績拡大、新規上場、設備投資 |

#### カテゴリ B: 従業員の死亡保障（3商品）

| # | 商品ID | 商品名（正式） | 主な対象 | 商品の目的・特徴 | 刺さるイベントトリガー |
|---|--------|-------------|---------|----------------|-------------------|
| 5 | P005 | 総合福祉団体定期保険 | 全従業員 | 企業保障型。死亡退職金規程の財源準備。高度障がい保障も付帯可 | M&A後統合、グループ再編、中計発表（人材投資） |
| 6 | P006 | みんなの団体定期保険（新無配当扱特約付団体定期保険） | 全従業員（100名〜） | 企業負担＋従業員任意加入のハイブリッド。デジタル完結で導入ハードル低い | 大規模採用、100名超の中堅企業 |
| 7 | P007 | 希望者グループ保険（団体定期保険） | 全従業員（任意加入） | 自助努力型。従業員がライフステージに応じ保険金額を選択 | 採用強化（福利厚生充実のアピール）、健康経営認定 |

#### カテゴリ C: 従業員の医療保障（3商品）

| # | 商品ID | 商品名（正式） | 主な対象 | 商品の目的・特徴 | 刺さるイベントトリガー |
|---|--------|-------------|---------|----------------|-------------------|
| 8 | P008 | 総合医療保険（団体型） | 全従業員 | 入院・手術・介護を保障。女性特定疾病の倍額設定も可。企業/自助どちらも可 | 健康経営申請、採用競争激化、CHRO交代 |
| 9 | P009 | 3大疾病保障保険（団体型） | 全従業員 | がん・急性心筋梗塞・脳卒中に対する一時金給付。就労不能補完にも活用 | 健康経営強化、平均年齢高い企業、メンタルヘルス対策 |
| 10 | P010 | 無配当扱特約付介護保障保険（団体型） | 全従業員 | 要介護状態になった場合に介護保険金を給付 | 高齢化対策、介護離職防止の経営課題 |

#### カテゴリ D: 従業員の休業補償（2商品）

| # | 商品ID | 商品名（正式） | 主な対象 | 商品の目的・特徴 | 刺さるイベントトリガー |
|---|--------|-------------|---------|----------------|-------------------|
| 11 | P011 | 新団体就業不能保障保険 | 全従業員 | 企業保障型。就業不能時の休業補償給付財源を確保。健康保険の傷病手当金を補完 | 健康経営強化、離職防止、メンタルヘルス対策 |
| 12 | P012 | 団体長期障害所得補償保険（GLTD） | 全従業員（任意加入） | 長期就業不能時に所得の一定額/率を補償。親介護一時金特約付加可能 | 健康経営申請（優良法人ホワイト500）、採用強化、CHRO交代 |

#### カテゴリ E: 従業員の退職後保障・年金（2商品）

| # | 商品ID | 商品名（正式） | 主な対象 | 商品の目的・特徴 | 刺さるイベントトリガー |
|---|--------|-------------|---------|----------------|-------------------|
| 13 | P013 | 確定給付企業年金（DB） | 全従業員 | 確定給付企業年金法に基づく年金制度。積立不足時は追加拠出義務あり | 退職給付制度改定、積立不足、M&A後統合 |
| 14 | P014 | 確定拠出年金（企業型・DC） | 全従業員 | 確定拠出年金法に基づく。掛金確定、従業員が自ら運用。60歳以降に受取 | DB→DC移行、新規DC導入、中計発表（人材投資） |

---

### 6.6 非保険サービスマスタ（T_NISSAY_SERVICES）★新設

日本生命は保険商品に加え、大企業顧客に対して以下の**非保険サービス**を提供している。これらを `T_NISSAY_SERVICES` テーブルで管理し、SI の提案生成・商品マッチングに活用する。

> **ポイント**: 保険単独ではなく「経営課題の総合解決」として提案できることが、競合（他生保・Databricks）への最大の差別化要因となる。

#### T_NISSAY_SERVICES テーブル定義

```sql
CREATE TABLE T_NISSAY_SERVICES (
    SERVICE_ID          VARCHAR(10)   NOT NULL PRIMARY KEY,
    SERVICE_NAME        VARCHAR(100)  NOT NULL,
    SERVICE_CATEGORY    VARCHAR(50),  -- 'ヘルスケア' / 'ビジネス支援' / '資金調達' / '資産運用' / '損害保険'
    DESCRIPTION         TEXT          NOT NULL,
    KEY_FEATURES        ARRAY,        -- 主な特長・提供価値
    TARGET_AUDIENCE     VARCHAR(100), -- 想定する担当者（人事部長・CFO・経営者等）
    TRIGGER_EVENTS      ARRAY,        -- 提案に最適な事業イベント
    CROSS_SELL_PRODUCTS ARRAY,        -- 組み合わせる保険商品IDリスト
    EXTERNAL_URL        VARCHAR(500),
    CREATED_AT          TIMESTAMP_NTZ
);
```

#### 5サービスのデータ定義

```sql
INSERT INTO T_NISSAY_SERVICES VALUES

-- S001: Wellness-Star☆（健康増進支援サービス）
('S001',
 'Wellness-Star☆（ニッセイ健康増進コンサルティングサービス）',
 'ヘルスケア',
 '従業員の健診・医療データを活用したデータヘルス計画の策定支援。保険だけでなく「リスクを軽減する」ヘルスケアサービスを提供し、健康経営優良法人の認定取得を支援する。',
 ['健康診断データの分析・可視化', 'データヘルス計画策定支援', '保健事業PDCA支援', '健康経営優良法人申請サポート', '労働生産性向上施策提案'],
 '人事部長・健康保険組合担当者・CHRO',
 ['健康経営認定取得・申請', '大規模採用（健康管理の重要性増大）', 'CHRO交代（新任者への訴求）'],
 ['P008', 'P011', 'P012'],  -- 団体医療・就業不能・GLTD
 'https://www.nissay.co.jp/hojin/wellness_star/',
 CURRENT_TIMESTAMP),

-- S002: Biz-Create® by NISSAY（ビジネスマッチング）
('S002',
 'Biz-Create® by NISSAY（ビジネスマッチングサービス）',
 'ビジネス支援',
 '全国約1,500の営業網・約27.9万社ネットワークを活かしたビジネスマッチング。Web上でビジネスパートナーを探し、日本生命の営業担当者がサポートして商談実現まで支援する。',
 ['27.9万社ネットワークへのアクセス', 'Web上でのニーズ登録・商談申込', '営業担当者によるマッチングサポート', '定期的な企業交流会・商談会への参加'],
 '経営企画部長・事業開発部長・経営者',
 ['M&A後統合（新たなビジネスパートナー探し）', '海外展開（国内販路の再構築）', '新規事業立上げ', '中計発表（新規事業・販路拡大）'],
 ['P001', 'P004'],  -- 役員向け長期保険とのセット
 'https://www.nissay.co.jp/hojin/businessmatching/',
 CURRENT_TIMESTAMP),

-- S003: 私募債（資金調達サービス）
('S003',
 '私募債（特定投資家向け直接金融）',
 '資金調達',
 '株式会社が比較的長期の資金調達を目的として、特定の投資家（日本生命）に対して発行する債券。直接金融への足がかりとなり、金融機関からの借入に依存しない資金調達多様化を実現する。',
 ['直接金融比率の向上', '借入依存からの脱却', '取締役会決議で発行可能', '長期安定資金の確保'],
 'CFO・財務部長',
 ['IPO準備', 'M&A・買収資金調達', '大型設備投資・新工場建設', '海外展開資金'],
 ['P001', 'P002'],  -- 役員退職慰労金・事業保障とのセット
 'https://www.nissay.co.jp/hojin/shikin/shibosai/',
 CURRENT_TIMESTAMP),

-- S004: 資産運用サービス（ニッセイアセットマネジメント）
('S004',
 '資産運用サービス（ニッセイアセットマネジメント）',
 '資産運用',
 'ニッセイアセットマネジメントが提供する投資一任・投資信託商品。企業年金（DB・DC）の年金資産運用に最適化されたサービス。退職給付債務の安定化に貢献する。',
 ['DB年金の積立不足解消支援', 'DC年金の運用商品選定アドバイス', '投資一任契約による専門運用', '年金ポートフォリオの最適化'],
 '財務部長・CFO・年金委員会',
 ['退職給付制度改定', 'DB→DC移行', '積立不足の深刻化', '金利変動リスク対応'],
 ['P013', 'P014'],  -- DB・DC年金とセット
 'https://www.nam.co.jp/',
 CURRENT_TIMESTAMP),

-- S005: 損害保険（あいおいニッセイ同和損保との連携）
('S005',
 '損害保険（あいおいニッセイ同和損害保険との業務提携）',
 '損害保険',
 'あいおいニッセイ同和損害保険との業務提携により、生命保険と損害保険を組み合わせた総合的なリスクマネジメントサービスを提供。法人の多様なリスクをワンストップでカバーする。',
 ['生保+損保のワンストップ提案', '海外勤務者の総合保護（生保+損保）', '事業用財産の損害保険', '企業向け賠償責任保険'],
 '総務部長・リスク管理部長・CFO',
 ['海外展開・現地法人設立', '大型設備投資・新工場建設', 'M&A後リスク統合管理'],
 ['P005', 'P006'],  -- 団体定期・役員退職慰労金とのセット
 'https://www.aioinissaydowa.co.jp/',
 CURRENT_TIMESTAMP);
```

#### 6サービスのイベント × サービス提案マッピング

| 事業イベント | 保険商品 | 非保険サービス | 総合提案メッセージ |
|-----------|--------|-------------|-----------------|
| **M&A・経営統合** | P005総合福祉団体定期 / P013DB年金 | S002 Biz-Create（パートナー探し） / S003 私募債 | 「従業員保護の統合 + 事業拡大のビジネス支援 + 資金調達」 |
| **IPO準備** | P001長期定期 / P002傷害重点型 | S003 私募債 / S004 資産運用 | 「役員保護 + 直接金融への移行 + 年金運用最適化」 |
| **健康経営認定申請** | P008団体医療 / P011就業不能 / P012 GLTD | S001 Wellness-Star☆ | 「保険による保障準備 + データヘルスによるリスク低減で認定取得を支援」 |
| **海外展開・法人設立** | P007希望者グループ保険（海外） | S005 損害保険連携 | 「海外勤務者の生命保険 + 損害保険でトータル保護」 |
| **大型設備投資** | P005総合福祉団体定期（従業員増） | S003 私募債（設備資金） / S005 損保 | 「従業員増加に伴う保険拡大 + 設備投資の資金調達 + 財物損害保険」 |
| **退職給付制度改定** | P013 DB / P014 DC | S004 資産運用（ニッセイAM） | 「DC移行設計 + 年金資産の専門運用で積立不足を解消」 |

---

| テーブル | レコード数 | 備考 |
|---------|-----------|------|
| T_CUSTOMER_COMPANIES | **20 社** | 実在企業名（従業員2,000名以上） |
| T_CONTACTS | **60 名**（各社 3 名） | 決裁者・担当者・窓口 |
| T_SALES_REPS | 5 名 | チーム担当分け |
| T_MEETINGS | **160 件** | 1社平均8回・過去2年分 |
| T_MEETING_TRANSCRIPTS | **1,600 行** | 1面談10発言ターン |
| T_MEETING_SUMMARIES | **160 件** | AI生成済みサンプル |
| T_PROSPECTS | 25 件 | 1社複数商品見込みあり |
| T_INSURANCE_PRODUCTS | **14 商品** | 日本生命公式サイト準拠（経営者向け4 + 死亡保障3 + 医療3 + 休業2 + 年金2） |
| **T_NISSAY_SERVICES** | **5 サービス** | **Wellness-Star / Biz-Create / 私募債 / 資産運用 / 損保連携** |
| T_CONTRACTS | 35 件 | 既存契約 |
| T_NEXT_ACTIONS | 60 件 | 直近3ヶ月分 |
| T_COMPANY_NEWS | **400 件** | 各社20件・事業イベント分類付き |
| **T_EVENT_ALERTS** | **50 件** | **未対応アラート含む・新テーブル** |
| T_FINANCIAL_DATA | **100 件** | 20社×5年 |
| T_INTEGRATED_REPORTS | **1,000 チャンク** | 各社50チャンク |
| T_CERTIFIED_INFO | **60 件** | 各社2〜4認定 |

---

## 7. Snowflake Intelligence（SI）設計

### 7.1 エージェント設定

| 項目 | 設定値 |
|-----|--------|
| **エージェント名** | 法人営業アシスタント（Hojin_Sales_Assistant） |
| **説明** | 日本生命 法人営業担当向け AI アシスタント。企業の事業イベントを検知し、最適なタイミングで最適な保険提案を支援します |
| **使用 LLM** | mistral-large2（日本語精度重視） |
| **言語** | 日本語メイン |

### 7.2 Tools 設計（Tool 10 追加・計10ツール）

> Tool 1〜8: 本セクション定義。**Tool 9（market_context_analysis）は Section 15.6** で定義。**Tool 10（compliance_check）は下記**。

#### Tool 1: customer_search（顧客・面談情報検索）
```yaml
tool_type: cortex_search
search_service: NIPPONLIFE_DEMO_DB.SEARCH.CUSTOMER_INFO_SEARCH
description: 顧客企業の基本情報、過去の面談内容・要約、既存契約を検索
columns_to_search: [TRANSCRIPT_TEXT, SUMMARY_TEXT, AGENDA]
filter_columns: [COMPANY_ID, MEETING_DATE, SALES_REP_ID]
max_results: 5
```

#### Tool 2: news_search（企業ニュース・開示情報検索）
```yaml
tool_type: cortex_search
search_service: NIPPONLIFE_DEMO_DB.SEARCH.NEWS_SEARCH
description: 顧客企業の最新ニュース・プレスリリース・適時開示・IR情報を検索。
             M&A・IPO・経営陣変更・採用計画等の事業イベントの詳細を調査する際に使用。
columns_to_search: [HEADLINE, BODY_TEXT]
filter_columns: [COMPANY_ID, NEWS_DATE, EVENT_TYPE, INSURANCE_RELEVANCE]
max_results: 8
```

#### Tool 3: integrated_report_search（統合報告書検索）
```yaml
tool_type: cortex_search
search_service: NIPPONLIFE_DEMO_DB.SEARCH.INTEGRATED_REPORT_SEARCH
description: 統合報告書・アニュアルレポートから人材戦略・中計・ESG方針を検索
columns_to_search: [CHUNK_TEXT]
filter_columns: [COMPANY_ID, REPORT_YEAR, CHAPTER]
max_results: 5
```

#### Tool 4: sales_analytics（営業 KPI・見込み分析）
```yaml
tool_type: cortex_analyst
semantic_view: NIPPONLIFE_DEMO_DB.ANALYTICS.SV_SALES_ANALYTICS
description: 見込みランク別件数・金額分析、KPI トレンド、担当先業績比較を自然言語で分析
```

#### Tool 5: certified_info（優良認定情報取得）
```yaml
tool_type: sql_execution
description: 健康経営優良法人・くるみん・えるぼし等の認定取得状況を取得
```

#### Tool 6: event_alert_search（事業イベントアラート検索 ★新）
```yaml
tool_type: sql_execution
description: >
  担当先企業の未対応アラート・最新事業イベントを取得します。
  「今週アプローチすべき企業は？」「M&A関連のアラートは？」等の質問に使用。
  T_EVENT_ALERTS テーブルから STATUS='UNREAD' の優先度順に返却。
query_template: >
  SELECT c.COMPANY_NAME, ea.EVENT_TYPE, ea.EVENT_SUMMARY,
         ea.INSURANCE_RELEVANCE, ea.ALERT_REASON,
         ea.RECOMMENDED_PRODUCTS, ea.RECOMMENDED_ACTION,
         ea.URGENCY_DAYS, ea.DETECTED_AT
  FROM T_EVENT_ALERTS ea
  JOIN T_CUSTOMER_COMPANIES c ON ea.COMPANY_ID = c.COMPANY_ID
  WHERE ea.SALES_REP_ID = :sales_rep_id
    AND ea.STATUS = 'UNREAD'
  ORDER BY
    CASE ea.INSURANCE_RELEVANCE WHEN '最高' THEN 1 WHEN '高' THEN 2 WHEN '中' THEN 3 ELSE 4 END,
    ea.URGENCY_DAYS ASC
  LIMIT 10
```

#### Tool 7: service_recommendation（非保険サービス提案 ★新）
```yaml
tool_type: sql_execution
tool_name: service_recommendation
description: >
  事業イベントや企業の課題に応じて、保険商品だけでなく
  Wellness-Star☆・Biz-Create・私募債・資産運用・損保連携サービスも含めた
  「総合提案パッケージ」を生成します。
  「このM&Aに対して何を提案すべきか（保険以外も含めて）？」等の質問に使用。
query_template: >
  SELECT s.SERVICE_ID, s.SERVICE_NAME, s.SERVICE_CATEGORY,
         s.DESCRIPTION, s.KEY_FEATURES, s.TARGET_AUDIENCE,
         s.TRIGGER_EVENTS, s.CROSS_SELL_PRODUCTS
  FROM T_NISSAY_SERVICES s
  WHERE ARRAY_CONTAINS(:event_type::VARIANT, s.TRIGGER_EVENTS)
     OR s.SERVICE_CATEGORY = :category
  ORDER BY s.SERVICE_CATEGORY
```

#### Tool 8: web_search（リアルタイム Web 検索 ★v3.0 追加・MCP 不要）
```yaml
tool_type: cortex_web_search
tool_name: web_search
description: >
  Snowflake ネイティブのリアルタイム Web 検索。
  「今日発表されたニュース」「最新の株価・IR情報」「最新プレスリリース」等
  Snowflake 内部データにない情報の取得に使用。
  ※ 競合（Databricks）の「MCP サーバー経由 Web 検索」と同等機能だが、
     Snowflake ネイティブのため外部サービス不要。
     全処理が Snowflake ネットワーク境界内で完結し、
     顧客の会話データが外部 MCP サーバーに送信されない。
max_results: 5
safe_search: true
```

#### Tool 10: compliance_check（保険業法コンプライアンスチェック ★F-11a）
```yaml
tool_type: sql_execution
tool_name: compliance_check
description: >
  入力されたテキスト（発言・会話）が保険業法・金融商品取引法上の
  コンプライアンスリスクに該当しないかチェックします。
  面談中に「この発言は問題ないか確認して」「さっきこう言ったが大丈夫か」
  等の質問に使用。SI が自動的に呼び出します。
  ※ このツールは「面談中のリアルタイムチェック」(F-11a) を担当。
     面談後の録音全体の一括分析 (F-11b) は Streamlit App1 で AI_CLASSIFY を直接使用。
query_template: >
  SELECT
    AI_CLASSIFY(
        :input_text,
        ['問題なし', '注意表現あり（確認推奨）', '違反リスクあり（要修正）'],
        OBJECT_CONSTRUCT(
            'task_description',
            '保険業法・金融商品取引法の観点から以下の禁止事項に該当するか分類してください:
             ①断定的判断の提供（確実に/絶対に/必ず儲かる）
             ②元本保証に関する虚偽説明（元本保証/損はしない）
             ③不当勧誘（今だけの特別条件/急がないと損）
             ④比較広告規制違反（他社より確実に有利）
             ⑤重要事項の不告知'
        )
    ) AS risk_level,
    AI_EXTRACT(
        :input_text,
        OBJECT_CONSTRUCT(
            'risk_expressions', 'ARRAY',
            'violation_categories', 'ARRAY',
            'recommended_corrections', 'ARRAY'
        )
    ) AS risk_detail
```

**SI のシステムプロンプト追加（応答手順）**:
```
compliance_check ツールの使用ルール:
  - ユーザーが発言・会話のコンプライアンスチェックを求めた場合は必ず compliance_check ツールを呼び出す
  - ツール結果に基づき、以下の形式で回答すること:
    ① リスクレベル（絵文字付きで分かりやすく）
    ② 問題となる具体的な表現（あれば引用）
    ③ なぜ問題なのか（法律・規制の観点から簡潔に）
    ④ その場で使える代替表現の例
    ⑤ 万一言ってしまった場合の対処法（必要な場合）
  - 「問題なし」の場合は安心させる言葉を添えて簡潔に回答
```

### 7.3 主要プロンプトシナリオ（デモ用）

#### シナリオ A: 事業イベントアラート確認（★最重要シナリオ）
```
プロンプト例:
「今朝のアラートを確認してください。
今週アプローチすべき企業と、その理由、すぐ使えるアクションを教えてください」

期待する出力:
① 🔴 最優先: 伊藤忠商事 → 北米食品会社買収完了を発表
   保険ニーズ: 被買収企業3,200名の福利厚生を日本生命の団体保険に統合する提案機会
   推奨アクション: 今週中に人事部長へアポ。制度移行スケジュールを確認

② 🔴 最優先: パナソニック HD → 電池事業子会社が来季上場検討と報道
   保険ニーズ: 上場準備に伴う役員退職慰労金保険・D&O保険の整備
   推奨アクション: 2週間以内にCFOへアプローチ。上場準備支援の文脈で提案

③ 🟡 高優先: トヨタ自動車 → 新CHRO着任予定を発表
   保険ニーズ: 新任CHRO就任前のアポ設定。既存契約の包括的見直し提案
   推奨アクション: 来週中に就任挨拶を兼ねてアポを依頼
```

#### シナリオ B: 商談前 企業情報収集
```
プロンプト例:
「来週、伊藤忠商事の人事部長との北米子会社の保険制度統合について
商談があります。以下を整理してください：
1. 今回の買収の概要と被買収企業の規模
2. 伊藤忠商事の現在の従業員保険・年金の構成
3. 過去の面談で出ていた懸念点
4. 今回の提案で想定される先方の質問と回答」
```

#### シナリオ C: C ランク→B ランク昇格戦略
```
プロンプト例:
「JERAは現在Cランクですが、最近アラートが出ていたと思います。
最新の事業イベントを踏まえた上で、Bランクに昇格させるための
最も効果的な戦略と、今すぐ使えるアプローチトークを教えてください」
```

#### シナリオ D: 業界横断ニーズ分析
```
プロンプト例:
「担当先のうち、M&A関連の事業イベントが起きている企業はどこですか？
それぞれどの保険商品が最も関連しますか？まとめてください」
```

#### シナリオ E: 総合提案パッケージ生成（★非保険サービス活用）
```
プロンプト例:
「伊藤忠商事の北米M&Aに対して、保険だけでなく
日本生命として提供できる全てのサービスを使った
総合的な提案パッケージを作ってください。
担当者別（CFO・人事部長・経営企画部長）に分けて提案内容を整理してください」

期待する出力:
■ CFO向け
  - 私募債（M&A資金調達の直接金融化）
  - 確定給付企業年金（被買収企業との年金制度統合）
  - 資産運用サービス（統合後の年金資産運用見直し）

■ 人事部長向け
  - 総合福祉団体定期保険（被買収企業3,200名の死亡保障統合）
  - 企業型DC（退職給付制度の統一）
  - Wellness-Star☆（統合後の健康経営推進・認定取得支援）

■ 経営企画部長向け
  - Biz-Create®（統合後の新規ビジネスパートナー探索）
  - 損害保険連携（北米法人の財物・賠償リスクカバー）
```

#### シナリオ F: リアルタイム Web 検索（★Databricks MCP 対抗・最大の見せ場）
```
プロンプト例:
「今日のトヨタ自動車の最新ニュースをリアルタイムで調べて、
 保険提案に関連しそうな情報をまとめてください」

SI の動作（画面上で見せる）:
  🔍 Web Search ツールを使用中...
  → 「トヨタ、北米EV合弁会社を本日正式設立と発表（AP通信）」
  → 「従業員3,200名、福利厚生制度の整備が急務と現地メディアが報道」

期待する出力:
「Web 検索で本日の最新情報を取得しました。
 北米合弁会社設立により、新規3,200名に対する
 海外勤務者保険・団体定期保険の提案機会が発生しています。
 今週中に人事部長へのアポを推奨します。」

デモ時の説明ポイント:
  ※ 競合（Databricks）は外部の「MCP サーバー」を経由して Web 検索します。
  ※ Snowflake Intelligence は MCP サーバー不要でネイティブに Web 検索可能。
  ※ 全処理が Snowflake のセキュリティ境界内で完結し、
     顧客の情報が外部に送信されないため、金融機関として安全に利用可能です。
```

#### シナリオ G: 面談中コンプライアンスリスク検知（★F-11a・SI で完結）
```
【F-11a: 面談中リアルタイムチェック（SI）】

面談中、営業担当者は Snowflake Intelligence しか触れないため、
SI の compliance_check ツールを使ってその場でチェックする。

プロンプト例①（都度チェック）:
「さっきこう言ってしまいました：
 『この商品は絶対に損しません、元本は保証されます』
 コンプライアンス上問題ありますか？今どう対処すれば？」

SI の動作:
  → compliance_check ツールを自動呼び出し
  → AI_CLASSIFY でリスクレベルを判定
  → 以下の形式で回答:

SI の出力例:
「🔴 違反リスクあり（要修正）

 問題となる表現:
  ①「絶対に損しません」→ 断定的判断の提供（保険業法 300 条違反のリスク）
  ②「元本は保証されます」→ 虚偽の事項の告知（同 300 条 1 号）

 今すぐできる対処:
  「先ほどの説明が不正確でした。正確には、過去の実績上では〇〇でしたが
   将来を保証するものではございません。大変失礼いたしました」
   と訂正することを強くお勧めします。

 代替表現:
  「過去実績では〇〇%のケースで運用プラスでしたが、
   将来の確実性はお約束できません」」

プロンプト例②（会話スニペットの一括チェック）:
「今日の面談でこのやり取りがありました。問題ないか確認して：
 先方:「損することはないですよね？」
 自分:「長期保有であれば基本的には大丈夫です」」

---

【F-11b: 面談後一括分析（Streamlit App1 統合）】

面談録音の文字起こし全体を AI_CLASSIFY でバッチ分析。
違反箇所をハイライト + 修正例一覧で表示。
管理職への監査レポート生成にも活用。

Streamlit 画面例:
  [コンプライアンス分析結果]
  🟢 全体判定: 軽微な注意が 1 件
  ⚠ [14分23秒]「基本的には大丈夫」→ 断定的表現の可能性（要確認）
  ✅ その他 47 発言は問題なし
  [修正例を表示] [監査レポートをダウンロード]

デモ時の説明ポイント:
  ※ 面談中の都度チェックは SI（Snowflake Intelligence）で完結
  ※ 面談後の全件バッチ分析は Streamlit で実施
  ※ どちらも Snowflake ネットワーク内で処理 → 顧客会話が外部に出ない
  ※ 競合（Databricks）にはこの保険業法特化の分類機能は存在しない
```

### 7.4 Semantic View 設計（Cortex Analyst 用）

```yaml
name: SV_SALES_ANALYTICS
tables:
  - prospects / companies / meetings / event_alerts

dimensions:
  - rank: 見込みランク
  - industry: 業種
  - event_type: 事業イベント種別 ★新
  - insurance_relevance: アラート重要度 ★新

metrics:
  - prospect_amount_total: 見込み保険料合計
  - prospect_count: 見込み件数
  - avg_ai_score: 平均AIスコア
  - unread_alert_count: 未対応アラート件数 ★新
  - avg_days_since_alert: アラートからの平均経過日数 ★新
```

---

## 8. Streamlit アプリ設計

### 8.1 アプリ全体設計方針

- **デザイン**: 日本生命のコーポレートカラー（赤：#E60012）を基調とした UI
- **ナビゲーション**: サイドバーで 6 画面を切り替え
- **認証**: Snowflake の認証を利用（追加ログイン不要）

### 8.1b SI vs Streamlit 使い分けガイドライン

> **背景**: 白倉さんのメール（2026/4/30）で「フロントが全てを自然言語で呼び出し、AI エージェントを動かすのは大変なので、簡単なインターフェイスがあった方がよさそう」という指摘があった。**SI はパワフルだが毎回文章を入力するのは手間**。定型作業は Streamlit のボタン 1 つで完結させ、SI は複雑な判断や深掘り分析に特化させる設計とする。

| 操作 | 推奨ツール | 理由 |
|-----|-----------|------|
| 顧客リスト・アラートの確認 | **Streamlit** | 毎朝の定型作業→ボタン不要で自動表示 |
| 企業情報の収集（最新Web情報含む） | **SI** | 複雑な横断検索→自然言語が最適 |
| 事前QAの生成 | **SI** | 企業固有の内容→自然言語で指示 |
| 面談録音のアップロード・要約 | **Streamlit** | ファイル操作→ボタン1つで処理 |
| 面談中コンプライアンスチェック | **SI** | 判断+アドバイスが必要→会話が自然 |
| Salesforce 登録 | **Streamlit** | ボタン1つ→定型作業 |
| 見込みランクの確認・チェックリスト | **Streamlit** | 日常的な進捗管理→ダッシュボードが最適 |
| 商品マッチングスコアの確認 | **Streamlit** | 可視化が重要→グラフ・表が最適 |
| 商品マッチングの深掘り分析 | **SI** | 「なぜこのスコアか」→自然言語で説明 |
| 提案書の生成 | **Streamlit** | ボタン1つでPPTX/Word生成 |
| 次回戦略の壁打ち | **SI** | 創造的な議論→会話が最適 |
| 金利・株価確認 | **Streamlit（App6）** | ダッシュボード表示が最適 |
| 市場×保険提案の分析 | **SI** | 複合的な分析→自然言語が最適 |


### 8.2 App 1: 面談録音・要約ダッシュボード（F-01）

**目的**: 面談の音声ファイルを Streamlit 経由でアップロードし、AI による自動文字起こし・要約・アクションアイテム抽出を行う。**v3.0 で F-11（コンプライアンス検知）と F-12（Salesforce 登録）をこの画面に統合。**

**画面構成（v3.0 強化版）**:
```
┌──────────────────────────────────────────────────────────────┐
│ 🎙 面談録音・AI要約                                          │
│                                                               │
│ [企業選択 ▼] [面談日付 📅] [面談種別 ▼]                     │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 音声ファイルをここにドロップまたはクリックしてアップロード│  │
│ └─────────────────────────────────────────────────────────┘  │
│ [▶ AI文字起こし・要約を実行]                                 │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ ■ 面談概要                                              │  │
│ │ ■ 先方の主な関心事項 / 課題                             │  │
│ │ ■ 事業イベント関連の発言 ★                             │  │
│ │   「来月、北米子会社の従業員が正式に統合される予定」     │  │
│ │   → AI: M&A後統合の進捗確認。保険制度移行の好機。       │  │
│ │ ■ 合意事項・ペンディング                                │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ 🛡 コンプライアンスチェック（F-11）     ★ v3.0 追加      │  │
│ │─────────────────────────────────────────────────────────│  │
│ │ 🟢 全体判定: 問題なし                                   │  │
│ │                                                         │  │
│ │ ⚠ [14分23秒] 注意:「確実に損しません」                  │  │
│ │   → 断定的判断の提供に該当する可能性                    │  │
│ │   → 修正例: 「過去実績では〇〇%のケースで...」           │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ アクションアイテム                                       │  │
│ │ 🔴 優先 | M&A後統合スケジュール確認 | 11/14まで         │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ [💾 保存] [📤 SI に送信] [📊 提案書生成] [🔗 Salesforce登録 ★]│
└──────────────────────────────────────────────────────────────┘
```

**F-11 コンプライアンス検知の実装コード**:
```python
# AI_CLASSIFY で禁止・注意表現を検知
compliance_result = session.sql("""
    SELECT
        AI_CLASSIFY(
            :transcript_text,
            ['問題なし', '注意表現あり（確認推奨）', '違反リスクあり（要修正）'],
            OBJECT_CONSTRUCT(
                'task_description',
                '保険業法・金融商品取引法の観点から断定的判断の提供・不当勧誘・
                 事実と異なる説明に該当する表現がないか分類してください。
                 禁止表現例: 確実に/絶対に/元本保証/損はしない/今だけの条件'
            )
        ) AS compliance_class,
        AI_EXTRACT(
            :transcript_text,
            OBJECT_CONSTRUCT(
                'risk_expressions', 'ARRAY',
                'timestamps', 'ARRAY',
                'suggested_alternatives', 'ARRAY'
            )
        ) AS risk_detail
""", transcript_text=transcript_text).collect()[0]

# 結果を Streamlit で表示
if compliance_result['COMPLIANCE_CLASS']['label'] != '問題なし':
    st.warning("⚠ コンプライアンス注意事項が検出されました")
    for risk in risk_detail['risk_expressions']:
        st.error(f"[{risk['timestamp']}] {risk['expression']}")
        st.info(f"修正例: {risk['alternative']}")
```

**F-12 Salesforce 自動登録の実装コード**:
```python
def register_to_salesforce(meeting_summary, next_actions, company_sf_id):
    # Snowflake Secret で認証情報を管理（コード内に書かない）
    sf_token = session.sql(
        "SELECT SYSTEM$GET_SECRET('salesforce_access_token')"
    ).collect()[0][0]
    
    payload = {
        "Subject": f"面談記録: {company_name} / {meeting_date}",
        "Description": meeting_summary,
        "ActivityDate": meeting_date,
        "WhatId": company_sf_id,
        "Type": "Call",
        "Status": "Completed",
        "NextActions__c": next_actions
    }
    resp = requests.post(
        f"{SF_INSTANCE}/services/data/v58.0/sobjects/Task/",
        headers={"Authorization": f"Bearer {sf_token}",
                 "Content-Type": "application/json"},
        json=payload
    )
    return resp.status_code == 201

# Streamlit ボタン
if st.button("🔗 Salesforce に登録", type="primary"):
    success = register_to_salesforce(summary, actions, sf_id)
    if success:
        st.success("✅ Salesforce に面談記録を登録しました")
```

**強化ポイント（v3.0）**:
- `AI_CLASSIFY()` によるコンプライアンス検知はリアルタイムで動作
- Salesforce 認証情報は `SYSTEM$GET_SECRET()` で管理 → コードに秘密情報が残らない
- Databricks でも同様の機能は実装可能だが、認証情報の管理・ガバナンスが煩雑

### 8.3 App 2: 事業イベント・アラートダッシュボード（F-10 ★新規）

**目的**: 担当先全企業の事業イベントアラートを一覧管理。「今すぐアプローチすべき企業」を AI が優先度付きで提示する。

**画面構成**:
```
┌──────────────────────────────────────────────────────────────┐
│ 🚨 事業イベント・アラートダッシュボード       山田 太郎 担当  │
│                                                               │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│ │ 未対応アラート│ │ 最高優先度   │ │ 今週期限     │          │
│ │     7 件      │ │     3 件     │ │     2 件     │          │
│ └──────────────┘ └──────────────┘ └──────────────┘          │
│                                                               │
│ ▼ 最優先アラート（今すぐアクション必要）                      │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 🔴 伊藤忠商事  |  M&A・経営統合  |  3日以内              │ │
│ │ 北米食品会社の買収完了を発表。被買収企業3,200名の         │ │
│ │ 福利厚生統合が喫緊の課題に。                             │ │
│ │ 推奨商品: 団体定期保険 / 企業年金(DC)                    │ │
│ │ AI推奨アクション: 今週中に人事部長へ連絡。統合スケジュール│ │
│ │ を確認し、制度設計提案の機会を設定する。                  │ │
│ │ [✅ 対応済み] [💬 SIで詳細分析] [📄 提案書を作成]       │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 🔴 パナソニック HD  |  グループ再編・分社化  |  5日以内  │ │
│ │ 電池事業子会社の上場を来季に計画と報道。役員陣の         │ │
│ │ 退職金・保護スキームの整備が必要になる見込み。           │ │
│ │ 推奨商品: 役員退職慰労金保険 / 事業保障保険             │ │
│ │ AI推奨アクション: 2週間以内にCFOにコンタクト。          │ │
│ │ [✅ 対応済み] [💬 SIで詳細分析] [📄 提案書を作成]       │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                               │
│ ▼ 高優先アラート                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 🟡 トヨタ自動車  |  経営陣交代  |  2週間以内             │ │
│ │ 🟡 NTTデータグループ  |  大規模採用  |  1ヶ月以内        │ │
│ │ 🟡 イオン  |  退職給付制度改定  |  2週間以内             │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                               │
│ ▼ 中優先アラート（今月中に対応）                              │
│ [JERA | 設備投資] [住友商事 | 中計発表] ...                  │
│                                                               │
│ [フィルター: イベント種別 ▼] [優先度 ▼] [対応済みを除く ☑]  │
└──────────────────────────────────────────────────────────────┘
```

**バックエンド処理**:
1. `T_EVENT_ALERTS` × `T_COMPANY_NEWS` × `T_CUSTOMER_COMPANIES` の JOIN
2. AI スコアリングで INSURANCE_RELEVANCE と URGENCY_DAYS を算出
3. `AI_COMPLETE()` で「推奨アクション」テキストを生成・DB に保存
4. Snowflake Streams + Tasks で新規ニュース取込時に自動アラート生成

### 8.4 App 3: 見込み管理ダッシュボード（F-03）

**目的**: 担当先 **20 社**の見込み管理を一元可視化。Pipedrive スタイルのカンバンで直感的なランク管理と、**「C→B に昇格するために何が必要か」のチェックリスト**を表示する（Databricks メールで指摘された「ステージをC⇒Bに進めるためにはこの確認が必要」という要件に対応）。

**画面構成**:
```
┌──────────────────────────────────────────────────────────────┐
│ 📊 見込み管理ダッシュボード                                  │
│  S | A: 2件 | B: 5件 | C: 3件                               │
│                                                               │
│ ★ ランクアップ候補（最新イベントトリガー付き）               │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ JERA     C → B  AIスコア74  最新トリガー: 設備投資拡大   │ │
│ │ 住友商事 C → B  AIスコア68  最新トリガー: 中計発表       │ │
│ │ 鹿島建設 C → B  AIスコア61  最新トリガー: 海外受注       │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌──────────────────┐ ┌────────────────────────────────────┐  │
│ │ 見込み一覧       │ │ JERA C→B 昇格チェックリスト 🆕   │  │
│ │                  │ │                                    │  │
│ │ トヨタ  B 12.3億 │ │ 進捗: ████░░░░ 50%               │  │
│ │ 伊藤忠  A  8.2億 │ │                                    │  │
│ │ パナHD  A  6.5億 │ │ ✅ 担当者（人事部長）との面談済   │  │
│ │ ...              │ │ ✅ 企業課題（設備投資）確認済      │  │
│ │                  │ │ ✅ 大まかな保険ニーズの確認済      │  │
│ │                  │ │ ❌ 予算規模・決裁者の確認 ← 要対応│  │
│ │                  │ │ ❌ 競合状況の確認 ← 要対応        │  │
│ │                  │ │ ❌ 具体的な提案書の提示            │  │
│ │                  │ │                                    │  │
│ │                  │ │ AI アドバイス:                     │  │
│ │                  │ │ 「次回商談で予算規模と CFO への    │  │
│ │                  │ │  アクセスを確認することが最優先。  │  │
│ │                  │ │  競合（MS&AD？）の動きも要確認。」 │  │
│ └──────────────────┘ └────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

**C→B 昇格チェックリスト 設計（T_PROSPECT_CHECKLIST）**:
```sql
-- 見込みランク昇格に必要な確認項目マスタ
CREATE TABLE T_PROSPECT_CHECKLIST_MASTER (
    CHECKLIST_ID      VARCHAR(10)  NOT NULL PRIMARY KEY,
    FROM_RANK         CHAR(1),     -- 'C'
    TO_RANK           CHAR(1),     -- 'B'
    CHECK_ITEM        VARCHAR(200), -- チェック項目名
    CHECK_CATEGORY    VARCHAR(50), -- '関係構築' / '課題把握' / '予算確認' / '競合確認' / '提案'
    DISPLAY_ORDER     INTEGER,
    IS_REQUIRED       BOOLEAN      -- 必須 or 推奨
);

-- サンプルデータ（C→B昇格の必要条件）
INSERT INTO T_PROSPECT_CHECKLIST_MASTER VALUES
('CK001', 'C', 'B', 'キーパーソン（人事部長/CHRO）との面談実施', '関係構築', 1, TRUE),
('CK002', 'C', 'B', '企業の主要課題（退職給付・健康経営等）の確認', '課題把握', 2, TRUE),
('CK003', 'C', 'B', '現在の保険契約状況・競合会社の把握', '競合確認', 3, TRUE),
('CK004', 'C', 'B', '予算規模（年間保険料の概算）の確認', '予算確認', 4, TRUE),
('CK005', 'C', 'B', '決裁者（CFO/取締役）へのアクセス確認', '予算確認', 5, TRUE),
('CK006', 'C', 'B', '少なくとも1商品の具体的な提案書を提示', '提案', 6, FALSE),
('CK007', 'C', 'B', '次回商談日時の合意', '関係構築', 7, FALSE);
```



**目的**: 企業情報・事業イベント・市場データ・面談履歴を統合し、**なぜその商品が推奨されるのか根拠付きで**スコアリングを表示する。Databricks のマッチングは「精度が怪しい」という評価を受けたが、Snowflake は **説明可能 AI（Explainable AI）**でスコアの根拠を 3 点以上明示することで上回る。

**画面構成（詳細設計）**:
```
┌──────────────────────────────────────────────────────────────┐
│ 🔍 企業ニーズ分析・商品マッチング                            │
│ 分析対象企業: [伊藤忠商事(株) ▼]     [最終更新: たった今 🔄]│
│                                                               │
│ ──── 企業プロファイル サマリー ────                          │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│ │ 従業員数     │ │ 財務健全性   │ │ 最新トリガーイベント  │  │
│ │  44,500名   │ │ AA / 堅調    │ │ 🔴 M&A (3日前)       │  │
│ │  平均43.1歳 │ │ ROE 15.8%   │ │ 北米食品会社買収完了  │  │
│ └──────────────┘ └──────────────┘ └──────────────────────┘  │
│                                                               │
│ ──── AI 商品マッチング（スコア降順・根拠付き）────           │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ # │ 商品名           │ スコア │ 推奨根拠（上位3理由）  │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 1 │ 総合福祉団体定期 │ ██ 97  │ ①M&A後3200名統合      │ │
│ │   │                 │        │ ②現契約が過小評価状態  │ │
│ │   │                 │        │ ③グループ再編で期限迫  │ │
│ │   │                 │        │               [詳細▼] │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 2 │ 企業年金 (DC)    │ ██ 94  │ ①10年金利1.45%→DB余剰 │ │
│ │   │                 │        │ ②M&A統合でDB統一必要   │ │
│ │   │                 │        │ ③CFOが費用削減に注目   │ │
│ │   │                 │        │               [詳細▼] │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 3 │ Wellness-Star☆  │ ██ 88  │ ①健康経営ホワイト500   │ │
│ │   │（非保険サービス）│        │ ②CHRO新任（3ヶ月前）   │ │
│ │   │                 │        │ ③採用2000名計画中      │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                               │
│ ──── Databricks との差別化ポイント（デモ時に強調）────       │
│  ※ 競合のマッチングは単純スコアのみ（根拠なし・精度不明）    │
│  ※ Snowflake は以下の4データソースを統合してスコア算出:      │
│     ①事業イベント（M&A・経営陣交代・採用計画）               │
│     ②市場データ（長期金利・株価・信用スプレッド）            │
│     ③面談履歴（過去の発言・課題・関心度）                    │
│     ④企業財務・認定情報                                      │
│                                                               │
│ [💬 SI でさらに詳しく分析] [📄 提案書アプリを開く →]        │
└──────────────────────────────────────────────────────────────┘
```

**スコアリングロジック（Snowflake の優位性の核心）**:

Databricks は汎用 LLM でスコアを出すため精度が不安定。Snowflake は以下の **4 軸の重み付きスコア**で構造化し、根拠を明示する：

```python
def calculate_product_score(company_id, product_id, session):
    # 4軸スコアリング（各25点満点 → 合計100点）

    # 軸1: 事業イベント適合度（動的・最大25点）
    # 直近のアラートイベントと商品のTRIGGER_EVENTSが一致するか
    event_score = session.sql("""
        SELECT SUM(
            CASE WHEN ARRAY_CONTAINS(n.EVENT_TYPE::VARIANT, p.TRIGGER_EVENTS)
            THEN (CASE ea.INSURANCE_RELEVANCE
                  WHEN '最高' THEN 25 WHEN '高' THEN 18
                  WHEN '中' THEN 10 ELSE 5 END)
            ELSE 0 END
        ) / COUNT(*) AS event_score
        FROM T_EVENT_ALERTS ea
        JOIN T_COMPANY_NEWS n ON ea.NEWS_ID = n.NEWS_ID
        CROSS JOIN T_INSURANCE_PRODUCTS p
        WHERE ea.COMPANY_ID = :company_id
          AND p.PRODUCT_ID = :product_id
          AND ea.STATUS IN ('UNREAD','READ')
          AND ea.DETECTED_AT >= DATEADD(DAY, -90, CURRENT_DATE)
    """, company_id=company_id, product_id=product_id).collect()[0][0] or 0

    # 軸2: 市場環境適合度（金利・株価連動・最大25点）
    # 市場データ（Section 15）から保険商品への影響を試算
    market_score = session.sql("""
        SELECT
            CASE p.PRODUCT_ID
                WHEN 'P013' THEN  -- DB年金: 金利上昇で好機
                    LEAST(25, GREATEST(0, (mi.CURRENT_10Y_RATE - 0.5) * 25))
                WHEN 'P014' THEN  -- DC: 金利上昇でDB移行好機
                    LEAST(25, GREATEST(0, (mi.CURRENT_10Y_RATE - 0.8) * 30))
                WHEN 'P001' THEN  -- 長期定期: 株価下落時に役員保険訴求
                    CASE WHEN mi.STOCK_1M_CHANGE_PCT < -5 THEN 20 ELSE 10 END
                ELSE 12  -- その他商品は中立スコア
            END AS market_score
        FROM NIPPONLIFE_DEMO_DB.ANALYTICS.V_MARKET_INSIGHT mi
        CROSS JOIN T_INSURANCE_PRODUCTS p
        WHERE mi.COMPANY_ID = :company_id AND p.PRODUCT_ID = :product_id
    """, company_id=company_id, product_id=product_id).collect()[0][0] or 12

    # 軸3: 企業属性適合度（従業員構成・業種・最大25点）
    attribute_score = session.sql("""
        SELECT
            GET(p.INDUSTRY_FIT_SCORE, c.INDUSTRY_LARGE)::FLOAT AS ind_score
        FROM T_CUSTOMER_COMPANIES c
        CROSS JOIN T_INSURANCE_PRODUCTS p
        WHERE c.COMPANY_ID = :company_id AND p.PRODUCT_ID = :product_id
    """, company_id=company_id, product_id=product_id).collect()[0][0] or 12

    # 軸4: 面談・接触履歴の関心度（最大25点）
    # 過去の面談テキストから商品への関心ワードの出現頻度
    interest_score = session.sql("""
        SELECT LEAST(25, COUNT(*) * 5) AS interest_score
        FROM T_MEETING_TRANSCRIPTS mt
        JOIN T_MEETINGS m ON mt.MEETING_ID = m.MEETING_ID
        JOIN T_INSURANCE_PRODUCTS p ON p.PRODUCT_ID = :product_id
        WHERE m.COMPANY_ID = :company_id
          AND CONTAINS(LOWER(mt.TRANSCRIPT_TEXT),
                       LOWER(ARRAY_TO_STRING(p.KEY_BENEFITS, ' ')))
    """, company_id=company_id, product_id=product_id).collect()[0][0] or 0

    total = event_score + market_score + attribute_score + interest_score

    # AI_COMPLETE で根拠テキストを生成（最大3理由）
    reason = session.sql("""
        SELECT AI_COMPLETE('mistral-large2', CONCAT(
            'この会社に', :product_name, 'を推奨する根拠を3点で簡潔に述べてください。
             事業イベント: ', :event_context, '
             市場環境: 10年金利', :rate, '%
             企業属性: ', :company_profile,
            ' 各理由は10文字以内で。'))
    """, ...).collect()[0][0]

    return {"score": total, "reasons": reason, "breakdown": {
        "event": event_score, "market": market_score,
        "attribute": attribute_score, "interest": interest_score
    }}
```


### 8.6 App 5: 提案書自動生成（F-05 v3.0 強化：PPTX + Word 両対応）

**目的**: 企業情報・商品選択をインプットとして、**既存のPowerPoint テンプレートに最新情報を差し込む**形で提案書を自動生成。Word・PPTX の両フォーマットでダウンロード可能。（Databricks デモで見せた「既存テンプレへの情報反映」と同等機能）

**画面構成**:
```
┌──────────────────────────────────────────────────────────────┐
│ 📊 提案書自動生成（Word / PowerPoint）                       │
│                                                               │
│ STEP 1: 基本情報設定                                         │
│  対象企業: [伊藤忠商事(株) ▼]                               │
│  対象商品: [✅総合福祉団体定期] [✅企業年金DC] [企業年金DB]  │
│  提案日  : [2025-11-20 📅]                                   │
│  提出先  : 人事部長 田中 誠 様                               │
│                                                               │
│ STEP 2: テンプレート選択                                     │
│  ○ 標準提案書（12 ページ）  ● 簡易版（5 ページ）            │
│  [📁 カスタムテンプレートをアップロード]   ← ★ v3.0 追加   │
│                                                               │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ 自動差し込み情報（AI が企業データから生成）            │    │
│ │ ✅ 最新ニュース（M&A発表：3日前）を「提案背景」に反映  │    │
│ │ ✅ 財務データ（2024年度）を「企業現状」に反映          │    │
│ │ ✅ 健康経営ホワイト500認定を「信頼関係」に反映        │    │
│ └──────────────────────────────────────────────────────┘    │
│                                                               │
│ [▶ AI 提案書生成（約 30 秒）]                               │
│                                                               │
│ [📊 PowerPoint ⬇] [📄 Word ⬇]    ← 両フォーマットで即DL  │
└──────────────────────────────────────────────────────────────┘
```

**PPTX 生成コード**:
```python
from pptx import Presentation
from pptx.util import Inches, Pt
import io

def generate_pptx_proposal(company_data, products, ai_analysis, template_path):
    prs = Presentation(template_path)  # 既存テンプレートを使用

    # スライド1: 表紙（企業名・日付を自動差し込み）
    title_slide = prs.slides[0]
    for shape in title_slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    run.text = run.text\
                        .replace("{{会社名}}", company_data['name'])\
                        .replace("{{日付}}", today)\
                        .replace("{{担当者}}", sales_rep_name)

    # スライド2: 御社の現状（財務データ・最新ニュースを自動反映）
    news_slide = prs.slides[1]
    # AI_COMPLETE で生成した「提案背景テキスト」を差し込み
    news_slide.placeholders[1].text = ai_analysis['proposal_background']

    # スライド3〜: 商品提案（マッチングスコア順に自動配置）
    # ...

    output = io.BytesIO()
    prs.save(output)
    return output.getvalue()

# Streamlit ダウンロードボタン
col1, col2 = st.columns(2)
with col1:
    st.download_button(
        "📊 PowerPoint ⬇",
        data=generate_pptx_proposal(...),
        file_name=f"proposal_{company_name}_{today}.pptx",
        mime="application/vnd.openxmlformats-officedocument"
              ".presentationml.presentation"
    )
with col2:
    st.download_button(
        "📄 Word ⬇",
        data=generate_docx_proposal(...),
        file_name=f"proposal_{company_name}_{today}.docx",
        mime="application/vnd.openxmlformats-officedocument"
              ".wordprocessingml.document"
    )
```

---

## 9. 60分デモシナリオ（タイムライン）

### 9.1 デモ全体の流れ（v3.0 更新版）

| 時間 | シーン# | シーン名 | 使用ツール | Databricks 対抗ポイント |
|------|---------|---------|-----------|----------------------|
| 0:00-3:00 | - | イントロ・全体像説明 | スライド | 競合デモの14機能を全て上回ることを宣言 |
| 3:00-10:00 | S-00 | ★朝のアラート確認 | Streamlit App2 | 夜間自動スキャン（競合はクリック起動） |
| **10:00-15:00** | **S-01a** | **★Web Search で最新情報収集** | **SI + Web Search** | **「MCPサーバー不要・セキュリティ完結」を訴求** |
| 15:00-19:00 | S-01b | 社内データ×Web情報の統合分析 | SI + Cortex Search | 社内+外部情報の横断分析 |
| 19:00-23:00 | S-02 | 商談前：事前 QA 生成 | SI | 約款対応の回答生成 |
| 23:00-30:00 | S-03 | 面談音声録音・要約 + **コンプライアンス検知** | Streamlit App1 | **コンプライアンス検知は競合にない機能** |
| 30:00-33:00 | S-03b | **Salesforce 自動登録** | Streamlit App1 | ボタン 1 つで登録完了 |
| 33:00-38:00 | S-04 | 面談後振り返り・次回アクション | SI | 次回戦略の自動立案 |
| 38:00-44:00 | S-05 | 見込み管理（C→B昇格） | Streamlit App3 | Pipedrive スタイルのカンバン |
| 44:00-49:00 | S-06 | 企業ニーズ分析・商品提案 | Streamlit App4 + SI | 担当者別（CFO/人事/経企）総合提案 |
| 49:00-55:00 | S-07 | **提案書自動生成（PPTX + Word）** | Streamlit App5 | 既存テンプレへの差し込み生成 |
| 55:00-57:00 | S-08 | **★市場データ × 保険提案（Data Sharing）** | Streamlit App6 + SI | 「財務企画部共有データ」を金利・株価で参照しDC移行提案根拠を示す |
| 57:00-60:00 | - | まとめ・Snowflake の優位性 | スライド | 「競合の14機能を全てカバーし3点で上回る」 |

### 9.2 S-01a: Web Search デモ（★MCP 対抗・最大の見せ場）

**ナレーション**:
> 「競合他社のデモでは、企業情報の収集に『MCP サーバー』を使っていたと聞いています。
> Snowflake Intelligence では MCP サーバーは不要です。
> ここをクリックするだけで、今日のリアルタイム情報を安全に収集できます。」

**強調ポイント**:
1. **「MCP サーバー不要」**を明言する — 競合は外部サービスが必要
2. SI の思考プロセス（どのツールを使っているか）を画面に表示して見せる
3. 「全処理が Snowflake ネットワーク内で完結 = 顧客の情報が外部に流れない」
4. 金融機関として「情報管理の安全性」が最重要であることを訴求

**入力プロンプト（SI）**:
```
今日の伊藤忠商事の最新ニュースをリアルタイムで調べてください。
特に保険提案に関連しそうな情報（M&A・採用・経営者変更等）に
フォーカスして、今週とるべきアクションを提案してください
```

### 9.3 S-03: コンプライアンス検知デモ（★競合にない機能）

**ナレーション**:
> 「競合のデモでもコンプライアンス検知機能がありましたが、
> Snowflake では AI_CLASSIFY という関数で保険業法に特化した分類が可能です。
> そして重要なのは、面談の音声データが Snowflake の外に一切出ない点です。」

**強調ポイント**:
1. `AI_CLASSIFY` の精度が保険業法の禁止表現に特化していることを説明
2. 「注意表現」だけでなく「修正例」まで自動生成することを見せる
3. 内部統制・コンプライアンス部門への提案材料にもなることを訴求


## 10. 競合差別化ポイント（vs Databricks 詳細）

### 10.1 Databricks が競合デモで見せた主な機能

白倉氏のメール（2026/4/30）で判明した競合デモの特徴:
- 面談前→面談中→面談後の流れに沿ったシナリオ設計
- MCP サーバーを使った Web 情報収集ボタン
- ベテラン開発者なら**コンセプト決定後 4〜5 時間で実装**できるとアピール

### 10.2 Snowflake の逆転ポイント（5つ） 「MCP 不要の Web Search vs 外部サービス依存」（★最重要差別化）
- Databricks は**外部 MCP サーバーを経由**して Web 検索 → 顧客情報・会話内容が外部サービスに送信されるリスク
- Snowflake Intelligence は**Web Search がプラットフォーム内蔵** → MCP サーバー不要
- 全処理が Snowflake のセキュリティ境界内で完結 → 金融機関の情報管理要件を満たす
- **デモで見せ方**: SI の思考プロセスで「Web Search ツールを使用中...」が表示される = 外部に出ていないことが画面で分かる

#### ポイント 2: 「コンプライアンス検知（業界唯一）の 2 モード設計」
- **面談中（F-11a）**: 営業担当者は面談中 SI しか触れないため、SI の `compliance_check` Tool で都度チェック。「この発言は大丈夫？」と SI に聞けば即座に保険業法の観点から判定＋修正例が返ってくる
- **面談後（F-11b）**: Streamlit（App1）で面談録音全文字起こしをバッチ分析。違反箇所ハイライト＋監査レポート生成
- どちらも全処理が Snowflake ネットワーク内で完結 → **顧客の会話が外部に流れない**
- 将来的に「違反傾向の営業担当者別統計」「月次コンプライアンスレポート」も生成可能

#### ポイント 3: 「業務特化 AI エージェント vs 汎用 BI ツール」
- Databricks Genie は**「データに質問する」プル型**ツール
- Snowflake Intelligence は**「今何をすべきかを提案する」プッシュ型エージェント**
- 事業イベント検知 → 保険ニーズ特定 → 推奨アクション → 提案書生成の**保険営業ワークフローが AI に組み込まれている**
- **競合のデモは4〜5時間で作れたと聞いている → Snowflake は Cortex Code でさらに高速に実装可能**

#### ポイント 4: 「Salesforce 連携のセキュリティ」
- Databricks でも Salesforce 連携は可能だが、認証情報の管理が複雑
- Snowflake は `SYSTEM$GET_SECRET()` + External Network Access で**認証情報がコードに残らない**
- ガバナンス・監査証跡が Snowflake の QUERY HISTORY で一元管理

#### ポイント 5: 「音声→提案書の一気通貫・全処理がネットワーク内」
- 音声 → 文字起こし → コンプライアンス検知 → 要約 → Salesforce 登録 → 提案書生成（PPTX/Word）
- **全工程が Snowflake 1 プラットフォーム内**で完結 → 情報漏洩リスクがゼロ
- Databricks では各処理に MCP・外部 API・別サービスを組み合わせる必要がある


---

## 11. 実装ロードマップ

### 11.1 フェーズ別実装計画

| フェーズ | 内容 | 主要タスク | 想定期間 |
|---------|------|-----------|---------|
| **Phase 1** | 基盤構築 | DB・スキーマ・テーブル作成 + ダミーデータ生成（STOCK_TICKER列含む） | 2日 |
| **Phase 2** | 検索・分析基盤 | Cortex Search × 3 + Semantic View + Event Alert 自動化 | 2.5日 |
| **Phase 3** | Streamlit 開発 | App1〜6 の 6 画面実装（App1 コンプライアンス検知・Salesforce統合を最優先） | 5日 |
| **Phase 4** | SI エージェント設定 | Tool 1〜9 設定 + プロンプトチューニング | 2.5日 |
| **Phase 5** | **データシェアリング構築** | **財務企画部アカウントのダミー SHARE 作成 + V_MARKET_INSIGHT ビュー + App6 連携** | **1.5日** |
| **Phase 6** | 統合テスト・リハーサル | 60分シナリオ通し + バックアップ準備 | 1日 |
| **合計** | | | **約 14.5 日（約 3 週間）** |

### 11.2 Phase 1 優先データ作成順

1. `T_COMPANY_NEWS`（200件）: EVENT_TYPE・INSURANCE_RELEVANCE 分類付き
2. `T_EVENT_ALERTS`（50件）: 未対応アラートを含む、デモ映えするデータ
3. `T_CUSTOMER_COMPANIES`（**20社**）: 実在企業の実態に即した値
4. その他テーブル: 面談録・財務・統合報告書

### 11.3 デモ環境

| 項目 | 設定値 |
|-----|--------|
| **Snowflake DB** | NIPPONLIFE_DEMO_DB |
| **ウェアハウス** | NIPPONLIFE_DEMO_WH（M サイズ） |
| **SI エージェント名** | 法人営業アシスタント |
| **デモ用ログイン** | demo_yamada_taro（山田担当者として操作） |

---

## 12. 技術スタック一覧

| カテゴリ | Snowflake コンポーネント | 用途 |
|---------|------------------------|------|
| **AI エージェント** | Snowflake Intelligence (Cortex Agent) + 9 Tools | 事業イベント分析・Web Search・業務支援会話 |
| **ビジネスアプリ** | Streamlit on Snowflake | **6 アプリ**（App1〜App5 営業支援 + App6 マーケット） |
| **全文検索** | Cortex Search × 3 | 面談録・ニュース・統合報告書 RAG |
| **自然言語分析** | Cortex Analyst + Semantic View | KPI・見込み・アラート・市場データ分析 |
| **テキスト生成** | AI_COMPLETE (Mistral Large 2) | 提案書・QA・アクション生成 |
| **要約** | AI_SUMMARIZE | 面談要約・ニュース要約 |
| **抽出** | AI_EXTRACT | 事業イベント抽出・アクションアイテム抽出 |
| **コンプライアンス検知** | **AI_CLASSIFY** | **保険業法禁止表現をリアルタイム検出（F-11）** |
| **ドキュメント解析** | Document AI | 統合報告書 PDF 解析 |
| **リアルタイム処理** | Streams + Tasks | ニュース取込 → 自動アラート生成 |
| **セキュリティ** | Column-level Security + Row Access Policy | 個人情報・顧客契約情報の保護 |
| **Word生成** | python-docx（Streamlit内） | 提案書 Word ファイル出力 |
| **PowerPoint生成** | **python-pptx（Streamlit内）** | **既存テンプレートへの情報差し込み（F-05強化）** |
| **Salesforce連携** | **Salesforce REST API + Snowflake Secret** | **面談後 Salesforce 自動登録（F-12）** |
| **データシェアリング** | **Snowflake Secure Data Sharing** | **財務企画部から金利・株価データをゼロコピー共有** |
| **グラフ可視化** | **plotly（Streamlit内）** | **金利トレンド・株価チャート（App6）** |
| **地図可視化** | pydeck (st.pydeck_chart) + Snowflake Geospatial | アラートマップ・見込み分布・拠点ヒートマップ |
| **実行環境** | Snowflake Warehouse（SPCS 不使用） | **デモアカウント SFSEAPAC-KMOT_AWS1 推奨** |
| **開発支援** | Cortex Code | デモ開発・デバッグ（今まさに使用中） |

---

*本設計書は v3.0 です。Databricks 完全対抗版：コンプライアンス検知（F-11）・Salesforce 自動登録（F-12）・Web Search（MCP不要）・PPTX生成・デモアカウント推奨を追加。*  
*作成: Snowflake SE チーム | 最終更新: 2026年4月30日*

---

## 13. UI/UX デザイン設計（hokan / SFA 参考）

### 13.1 参考プロダクト一覧

| プロダクト | 特徴 | 本デモへの活用ポイント |
|----------|------|---------------------|
| **hokan®** | 保険代理店向け CRM。保険業法対応・意向把握・アフターフォロー可視化 | 保険業務特化のUI設計・アクティビティタイムライン・意向把握シート |
| **Pipedrive** | ビジュアルパイプライン（カンバン式）。シンプルで直感的 | 見込み管理の案件カンバンボード・ドラッグ&ドロップ操作 |
| **Mazrica Sales** | 日本語 SFA・AIインサイト・カード型案件管理 | AI推奨アクションカード・ファネル分析・予実比較 |
| **HubSpot CRM** | クリーンな企業詳細ページ・アクティビティフィード | 顧客360度ビュー・接触履歴の統合タイムライン |
| **Salesforce** | 業界標準 SFA。エンタープライズ向け豊富な機能 | 商談フェーズ管理・活動記録テンプレート |

### 13.2 hokan® から採用する UI/UX 要素

#### 左サイドバーナビゲーション（hokan スタイル）
```
サイドバー（常時表示）:
  🏠 ホーム（今日のアラートと ToDo）
  🚨 アラート（事業イベント）    ← バッジ表示（未読件数）
  🏢 顧客企業                    ← 担当 20 社一覧
  📊 見込み管理
  🎙 面談録
  📄 提案書
  ⚙️ 設定
```

#### 企業詳細ページ（hokan × HubSpot スタイル）
```
企業名: トヨタ自動車(株)                      [見込み: B] [AI スコア: 68]
────────────────────────────────────────────────────────────────────
タブ: [基本情報] [担当者] [面談履歴] [契約情報] [アラート] [提案書]

[基本情報タブ]
  本社: 愛知県豊田市    │ 従業員: 72,700名   │ 年商: 29.3兆円
  業種: 製造（自動車）  │ 平均年齢: 41.8歳   │ 格付け: AA
  担当: 山田太郎       │ 関係年数: 8年      │ 最終接触: 3日前

  [現在のアクティブアラート]
  🔴 新CHRO就任予定（3日以内にアポ必要）
  🟡 ソフトウェア人材2,000人採用計画

[アクティビティタイムライン]  ← hokan のアクティビティ機能
  📞 2025/10/28  電話  「M&A後の統合スケジュール確認」
  📧 2025/10/22  メール 「企業年金見直しに関する資料を送付」
  🤝 2025/10/15  訪問  「人事部長・田中様 / DC移行ヒアリング」
  🤝 2025/09/30  訪問  「CHROへの挨拶・今後の方針ヒアリング」
```

#### 意向把握・商品比較シート（hokan スタイル）
```
意向確認チェックリスト               推奨商品（AIマッチング）
────────────────────────             ─────────────────────────────
☑ 退職給付制度の見直し意向           1位 企業年金(DC)   ████████ 94
☑ 健康経営への投資意欲あり           2位 総合福祉団体定期 ███████ 87  
☐ 海外従業員の保護ニーズ             3位 団体医療保険    ██████  81
☐ 役員退職慰労金の整備               4位 GLTD          █████   72
```

### 13.3 Pipedrive から採用する UI/UX 要素

#### 見込み管理カンバンボード（Pipedrive スタイル）
```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  C ランク   │ │  B ランク   │ │  A ランク   │ │  S ランク   │ │  成約 ✅   │
│   3件       │ │   5件       │ │   2件       │ │   0件       │ │   8件       │
│  8.1億      │ │  34.0億     │ │  15.9億     │ │             │ │  31.2億     │
│─────────────│ │─────────────│ │─────────────│ │─────────────│ │─────────────│
│ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │ │             │ │ ┌─────────┐ │
│ │ JERA    │ │ │ │トヨタ   │ │ │ │パナHD   │ │ │             │ │ │ ...     │ │
│ │ 2.8億   │ │ │ │12.3億   │ │ │ │ 6.5億   │ │ │             │ │ └─────────┘ │
│ │ AI:74   │ │ │ │ AI:68   │ │ │ │ AI:85   │ │ │             │ │             │
│ │🔴 アラート│ │ │ │🟡 アラート│ │ │ │⚡ 要フォロー│ │ │             │ │             │
│ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │ │             │ │             │
│ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │ │             │ │             │
│ │住友商事 │ │ │ │伊藤忠   │ │ │ │         │ │ │             │ │             │
│ │ 3.8億   │ │ │ │ 8.2億   │ │ │ └─────────┘ │ │  [+ 追加]   │ │             │
│ └─────────┘ │ │ └─────────┘ │ │             │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
                    ↑ ドラッグ&ドロップでランク変更（デモ映え）
```

**実装**: `st.columns()` で 5 カラム構成、カード は `st.container()` + CSS で実装

### 13.4 Mazrica Sales から採用する UI/UX 要素

#### AI インサイトカード（Mazrica スタイル）
```
┌─────────────────────────────────────────────────────────────────┐
│ 💡 AI インサイト                              [詳細を見る →]    │
│─────────────────────────────────────────────────────────────────│
│ 「伊藤忠商事は過去30日でアラート2件、接触0回。                    │
│  競合他社が既にアプローチを開始した可能性があります。             │
│  今週中のコンタクトを強く推奨します。」                          │
│                                                                   │
│ 推奨アクション:  📞 今週中に電話  📧 制度移行資料を送付          │
└─────────────────────────────────────────────────────────────────┘
```

### 13.5 全体デザイン仕様

| 要素 | 設定値 |
|-----|--------|
| **プライマリカラー** | `#E60012`（日本生命レッド） |
| **セカンダリカラー** | `#1A1A2E`（ダークネイビー） |
| **アクセントカラー** | `#F5A623`（アンバー・アラート表示用） |
| **背景** | `#F7F8FA`（ライトグレー） |
| **カードスタイル** | 白背景・`border-radius: 8px`・subtle shadow |
| **フォント** | `Noto Sans JP`（日本語）/ `Inter`（英数） |
| **アイコン** | emoji（🔴🟡🟢✅📊🎙📄🚨）主体でシンプルに |
| **レイアウト** | `st.set_page_config(layout="wide")` |
| **ナビゲーション** | `st.sidebar` + `st.radio()` で画面切替 |

### 13.6 CSS カスタマイズ（Streamlit inject_css）

```python
st.markdown("""
<style>
/* プライマリカラー */
.stButton > button {
    background-color: #E60012;
    color: white;
    border-radius: 6px;
    font-weight: bold;
}
/* アラートカード */
.alert-card-critical {
    background: #FFF0F0;
    border-left: 4px solid #E60012;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 8px 0;
}
.alert-card-high {
    background: #FFFBF0;
    border-left: 4px solid #F5A623;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 8px 0;
}
/* 見込みカード（Pipedrive スタイル） */
.prospect-card {
    background: white;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12);
    margin: 6px 0;
    cursor: pointer;
    transition: box-shadow 0.2s;
}
.prospect-card:hover {
    box-shadow: 0 3px 12px rgba(0,0,0,0.2);
}
/* タブスタイル */
.stTabs [data-baseweb="tab"] {
    font-size: 14px;
    font-weight: 500;
}
/* サイドバー */
section[data-testid="stSidebar"] {
    background: #1A1A2E;
    color: white;
}
</style>
""", unsafe_allow_html=True)
```

---

## 14. 地図データ設計（pydeck）

### 14.1 使用ライブラリ

| ライブラリ | 用途 | Warehouse 対応 |
|-----------|------|--------------|
| `pydeck` (st.pydeck_chart) | メインの地図ライブラリ。リッチなインタラクション | ✅ Streamlit 標準 |
| Snowflake Geospatial 関数 | `ST_MAKEPOINT()`, `H3_LATLNG_TO_CELL()` | ✅ ウェアハウス上で実行 |

> `pydeck` は Mapbox のレンダリングエンジン（deck.gl）を使用。API キー不要でベースマップを表示可能（`pdk.map_styles.CARTO_POSITRON` 等を使用）。

### 14.2 地図データ用テーブル

#### T_COMPANY_LOCATIONS（企業拠点情報）
```sql
CREATE TABLE T_COMPANY_LOCATIONS (
    LOCATION_ID       VARCHAR(15)  NOT NULL PRIMARY KEY,
    COMPANY_ID        VARCHAR(10)  NOT NULL,
    LOCATION_TYPE     VARCHAR(20), -- '本社' / '支社' / '工場' / '物流センター' / 'データセンター'
    LOCATION_NAME     VARCHAR(100),
    ADDRESS           VARCHAR(200),
    PREFECTURE        VARCHAR(20), -- 都道府県
    CITY              VARCHAR(50),
    LATITUDE          FLOAT        NOT NULL,
    LONGITUDE         FLOAT        NOT NULL,
    EMPLOYEE_COUNT    INTEGER,     -- その拠点の従業員数
    IS_HEADQUARTERS   BOOLEAN      DEFAULT FALSE,
    CREATED_AT        TIMESTAMP_NTZ
);
```

#### 10 社の本社座標データ
```sql
-- デモ用 INSERT サンプル（実際の本社所在地）
INSERT INTO T_COMPANY_LOCATIONS VALUES
-- トヨタ自動車（愛知県豊田市）
('LOC001', 'C001', '本社', 'トヨタ自動車 本社', '愛知県豊田市', '愛知県', '豊田市', 35.0835, 137.1562, 72700, TRUE, CURRENT_TIMESTAMP),
-- パナソニック HD（大阪府門真市）
('LOC002', 'C002', '本社', 'パナソニック HD 本社', '大阪府門真市', '大阪府', '門真市', 34.7460, 135.5831, 63400, TRUE, CURRENT_TIMESTAMP),
-- 伊藤忠商事（東京都港区）
('LOC003', 'C003', '本社', '伊藤忠商事 本社', '東京都港区青山', '東京都', '港区', 35.6608, 139.7322, 44500, TRUE, CURRENT_TIMESTAMP),
-- NTTデータグループ（東京都江東区）
('LOC004', 'C004', '本社', 'NTTデータグループ 本社', '東京都江東区豊洲', '東京都', '江東区', 35.6674, 139.7775, 190000, TRUE, CURRENT_TIMESTAMP),
-- 野村HD（東京都中央区）
('LOC005', 'C005', '本社', '野村ホールディングス 本社', '東京都中央区日本橋', '東京都', '中央区', 35.6812, 139.7671, 26000, TRUE, CURRENT_TIMESTAMP),
-- JERA（東京都中央区）
('LOC006', 'C006', '本社', 'JERA 本社', '東京都中央区', '東京都', '中央区', 35.6812, 139.7741, 5100, TRUE, CURRENT_TIMESTAMP),
-- イオン（千葉県千葉市）
('LOC007', 'C007', '本社', 'イオン 本社', '千葉県千葉市美浜区', '千葉県', '千葉市', 35.6073, 140.1063, 306000, TRUE, CURRENT_TIMESTAMP),
-- 住友商事（東京都千代田区）
('LOC008', 'C008', '本社', '住友商事 本社', '東京都千代田区大手町', '東京都', '千代田区', 35.6897, 139.7630, 48200, TRUE, CURRENT_TIMESTAMP),
-- 鹿島建設（東京都港区）
('LOC009', 'C009', '本社', '鹿島建設 本社', '東京都港区元赤坂', '東京都', '港区', 35.6782, 139.7252, 21800, TRUE, CURRENT_TIMESTAMP),
-- 日本郵船（東京都千代田区）
('LOC010', 'C010', '本社', '日本郵船 本社', '東京都千代田区丸の内', '東京都', '千代田区', 35.6845, 139.7614, 36000, TRUE, CURRENT_TIMESTAMP),
-- ★新規10社（C011〜C020）
-- 武田薬品工業（東京都中央区）
('LOC011', 'C011', '本社', '武田薬品工業 本社', '東京都中央区日本橋本町', '東京都', '中央区', 35.6812, 139.7732, 14000, TRUE, CURRENT_TIMESTAMP),
-- ANAホールディングス（東京都港区）
('LOC012', 'C012', '本社', 'ANAホールディングス 本社', '東京都港区東新橋', '東京都', '港区', 35.6550, 139.7530, 44000, TRUE, CURRENT_TIMESTAMP),
-- セブン＆アイ・ホールディングス（東京都千代田区）
('LOC013', 'C013', '本社', 'セブン＆アイ HD 本社', '東京都千代田区二番町', '東京都', '千代田区', 35.6923, 139.7508, 130000, TRUE, CURRENT_TIMESTAMP),
-- KDDI（東京都千代田区）
('LOC014', 'C014', '本社', 'KDDI 本社', '東京都千代田区飯田橋', '東京都', '千代田区', 35.6897, 139.7527, 48000, TRUE, CURRENT_TIMESTAMP),
-- 三菱地所（東京都千代田区）
('LOC015', 'C015', '本社', '三菱地所 本社', '東京都千代田区大手町', '東京都', '千代田区', 35.6852, 139.7631, 10000, TRUE, CURRENT_TIMESTAMP),
-- 日本製鉄（東京都千代田区）
('LOC016', 'C016', '本社', '日本製鉄 本社', '東京都千代田区丸の内', '東京都', '千代田区', 35.6891, 139.7644, 51000, TRUE, CURRENT_TIMESTAMP),
-- 三井住友フィナンシャルグループ（東京都千代田区）
('LOC017', 'C017', '本社', '三井住友FG 本社', '東京都千代田区丸の内', '東京都', '千代田区', 35.6908, 139.7572, 40000, TRUE, CURRENT_TIMESTAMP),
-- サントリーホールディングス（東京都港区）
('LOC018', 'C018', '本社', 'サントリーHD 本社', '東京都港区台場', '東京都', '港区', 35.6272, 139.7748, 40000, TRUE, CURRENT_TIMESTAMP),
-- 東日本旅客鉄道（東京都渋谷区）
('LOC019', 'C019', '本社', 'JR東日本 本社', '東京都渋谷区代々木', '東京都', '渋谷区', 35.6850, 139.7013, 70000, TRUE, CURRENT_TIMESTAMP),
-- 旭化成（東京都千代田区）
('LOC020', 'C020', '本社', '旭化成 本社', '東京都千代田区有楽町', '東京都', '千代田区', 35.6835, 139.7528, 45000, TRUE, CURRENT_TIMESTAMP);
```

### 14.3 地図機能の画面別設計

#### App2（事業イベントアラートマップ）

**目的**: アラート発生企業を地図上にプロット。優先度を色で表現。

```python
import pydeck as pdk
import streamlit as st

# アラートデータ（Snowflake から取得）
df_alerts = session.sql("""
    SELECT c.COMPANY_NAME, l.LATITUDE, l.LONGITUDE,
           ea.INSURANCE_RELEVANCE, ea.EVENT_TYPE, ea.EVENT_SUMMARY,
           ea.URGENCY_DAYS, ea.RECOMMENDED_ACTION
    FROM T_EVENT_ALERTS ea
    JOIN T_CUSTOMER_COMPANIES c ON ea.COMPANY_ID = c.COMPANY_ID
    JOIN T_COMPANY_LOCATIONS l ON ea.COMPANY_ID = l.COMPANY_ID
    WHERE l.IS_HEADQUARTERS = TRUE AND ea.STATUS = 'UNREAD'
""").to_pandas()

# 優先度で色分け
def get_color(relevance):
    return {
        '最高': [230, 0, 18, 230],   # 日本生命レッド（最高優先）
        '高':   [245, 166, 35, 210], # アンバー
        '中':   [100, 149, 237, 180] # コーンフラワーブルー
    }.get(relevance, [150, 150, 150, 150])

df_alerts['color'] = df_alerts['insurance_relevance'].apply(get_color)
df_alerts['radius'] = df_alerts['urgency_days'].apply(lambda x: max(20000, 60000 - x * 1000))

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_alerts,
    get_position=["longitude", "latitude"],
    get_color="color",
    get_radius="radius",
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=35.6762, longitude=137.0, zoom=5.5, pitch=0
)

tooltip = {
    "html": """
        <b>{company_name}</b><br/>
        🚨 {event_type}<br/>
        {event_summary}<br/>
        ⏰ {urgency_days}日以内に対応<br/>
        💡 {recommended_action}
    """,
    "style": {"backgroundColor": "#1A1A2E", "color": "white", "fontSize": "13px"}
}

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip,
    map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
))
```

#### App3（見込み管理マップ）

**目的**: 担当先企業の本社を地図上に表示。バブルサイズ = 見込み保険料額、色 = 見込みランク。

```python
# バブルマップ: 見込み金額 × ランクを可視化
layer_prospects = pdk.Layer(
    "ScatterplotLayer",
    data=df_prospects_with_loc,
    get_position=["longitude", "latitude"],
    get_color="""
        current_rank == 'S' ? [255, 215, 0, 255] :
        current_rank == 'A' ? [0, 200, 100, 230] :
        current_rank == 'B' ? [0, 100, 230, 200] :
        [180, 180, 180, 160]
    """,
    get_radius="prospect_amount / 50",  # 見込み金額（万円）に比例
    pickable=True,
)

# テキストレイヤー（企業名ラベル）
layer_text = pdk.Layer(
    "TextLayer",
    data=df_prospects_with_loc,
    get_position=["longitude", "latitude"],
    get_text="company_name_short",
    get_size=14,
    get_color=[30, 30, 30],
    get_alignment_baseline="'bottom'",
)
```

#### App3（都道府県別 H3 ヘクサゴンマップ）

**目的**: 担当先の従業員が多い都道府県をヒートマップで表示。保険料の潜在的な規模感を把握。

```python
# Snowflake の H3 関数で拠点データを集計
df_h3 = session.sql("""
    SELECT
        H3_LATLNG_TO_CELL(LATITUDE, LONGITUDE, 4) AS h3_cell,
        SUM(EMPLOYEE_COUNT) AS total_employees,
        COUNT(DISTINCT COMPANY_ID) AS company_count
    FROM T_COMPANY_LOCATIONS
    WHERE EMPLOYEE_COUNT IS NOT NULL
    GROUP BY 1
""").to_pandas()

layer_h3 = pdk.Layer(
    "H3HexagonLayer",
    data=df_h3,
    get_hexagon="h3_cell",
    get_elevation="total_employees / 1000",
    get_fill_color="[230, 0, 18, 180]",  # 日本生命レッド
    elevation_scale=100,
    extruded=True,  # 3D 表示
    pickable=True,
    auto_highlight=True,
)
```

### 14.4 地図機能の優先実装順

| 優先度 | 地図機能 | 対応アプリ | 実装難易度 |
|--------|---------|-----------|-----------|
| ★★★ | 事業イベントアラートマップ（バブル） | App2 | 低 |
| ★★★ | 見込み管理バブルマップ（ランク色分け） | App3 | 低 |
| ★★ | 企業拠点詳細マップ（本社+支社+工場） | App3 企業詳細 | 中 |
| ★ | H3 従業員密度ヒートマップ（3D） | App3 | 中 |




---

## 15. ★ データシェアリング設計（財務企画部 × 法人営業部）

### 15.1 シナリオの背景・意義

日本生命では、**財務企画部**が金融市場データ（長期金利・株価指数・信用スプレッド等）を Snowflake で管理している想定とする。このデータを **Snowflake Secure Data Sharing** により法人営業部のデモ環境に共有することで：

1. **保険提案の精度が向上**: 足元の金利環境・顧客企業の株価動向を踏まえた根拠ある提案
2. **Snowflake の差別化訴求**: データコピー不要・リアルタイム共有という Snowflake の核心価値を示す
3. **Databricks Delta Sharing との対比**: Delta Sharing はオープンフォーマット共有だが、Snowflake はネイティブ共有でセットアップが格段にシンプル

```
長期金利が保険営業に与える影響:
  金利上昇 → DB年金の積立不足が縮小 → DC移行提案の最適タイミング
  金利低下 → 積立不足拡大リスク → 追加掛金発生 → 制度見直し訴求

株価（担当先企業）が保険営業に与える影響:
  株価下落 → 財務体力低下 → 事業保障・役員退職慰労金保険の訴求
  株価上昇 → 業績好調 → 福利厚生投資予算が取りやすい → 拡充提案好機

信用スプレッド:
  スプレッド拡大 → 信用力低下懸念 → 経営者保険・事業保障を強く訴求
```

### 15.2 アーキテクチャ設計

```
  財務企画部 Snowflake アカウント
  DATABASE: MARKET_DATA_DB
  ├── INTEREST_RATES    (日次長期金利)
  ├── STOCK_PRICES      (個別株価・指数)
  ├── CREDIT_SPREADS    (信用スプレッド)
  └── ECONOMIC_INDICATORS (CPI・GDP等)

  CREATE SHARE MARKET_DATA_SHARE;
  ALTER SHARE MARKET_DATA_SHARE
    ADD ACCOUNT = NISSAY_SALES_DEPT;

         ↓ ゼロコピー・リアルタイム共有

  法人営業部 Snowflake アカウント (SFSEAPAC-KMOT_AWS1)

  CREATE DATABASE MARKET_DATA_SHARED
    FROM SHARE NISSAY_FINANCE.MARKET_DATA_SHARE;

  V_MARKET_INSIGHT: 市場データ × 顧客 × 見込み を JOIN したビュー

  [Streamlit App6]               [SI + Tool 9]
  金利・株価ダッシュボード        市場コンテキスト参照
```

### 15.3 共有テーブル定義

#### INTEREST_RATES（長期金利）
```sql
CREATE TABLE MARKET_DATA_DB.PUBLIC.INTEREST_RATES (
    RATE_DATE           DATE          NOT NULL,
    INSTRUMENT          VARCHAR(50),  -- '日本国債10年', '日本国債30年', '米国債10年'
    RATE_PERCENT        FLOAT,        -- 金利（%）例: 1.45
    CHANGE_FROM_PREV    FLOAT,        -- 前日差（%ポイント）
    CHANGE_FROM_MONTH   FLOAT,
    CHANGE_FROM_YEAR    FLOAT,
    DATA_SOURCE         VARCHAR(50),  -- '日本銀行' / 'Bloomberg'
    CREATED_AT          TIMESTAMP_NTZ
);
```

デモ用金利推移サンプル（2024〜2025年）:
- 2024/01: 0.62%  上昇局面開始 → DC移行好機の兆し
- 2024/06: 0.95%  日銀利上げ → DB積立余剰に転換
- 2025/01: 1.10%  上昇継続 → 積立不足解消
- 2025/10: 1.45%  高金利定着 → 確定給付見直し機会

#### STOCK_PRICES（個別株価・指数）
```sql
CREATE TABLE MARKET_DATA_DB.PUBLIC.STOCK_PRICES (
    PRICE_DATE      DATE         NOT NULL,
    TICKER          VARCHAR(20),  -- '7203.T'(トヨタ), 'TOPIX', 'N225'
    COMPANY_NAME    VARCHAR(100),
    CLOSING_PRICE   FLOAT,
    MARKET_CAP_JPY  FLOAT,
    PBR             FLOAT,
    PER             FLOAT,
    CHANGE_1D_PCT   FLOAT,
    CHANGE_1M_PCT   FLOAT,
    CHANGE_1Y_PCT   FLOAT,
    DATA_SOURCE     VARCHAR(50),
    CREATED_AT      TIMESTAMP_NTZ
);
```

デモ対象銘柄（担当先20社のうち上場19社 + 指数）:

| 企業名 | ティッカー |
|--------|----------|
| トヨタ自動車 | 7203.T |
| パナソニック HD | 6752.T |
| 伊藤忠商事 | 8001.T |
| NTTデータグループ | 9613.T |
| 野村ホールディングス | 8604.T |
| イオン | 8267.T |
| 住友商事 | 8053.T |
| 鹿島建設 | 1812.T |
| 日本郵船 | 9101.T |
| TOPIX 指数 | TOPIX |
| 日経225 指数 | N225 |

#### CREDIT_SPREADS（信用スプレッド）
```sql
CREATE TABLE MARKET_DATA_DB.PUBLIC.CREDIT_SPREADS (
    SPREAD_DATE         DATE          NOT NULL,
    COMPANY_NAME        VARCHAR(100),
    CREDIT_RATING       VARCHAR(10),  -- 'AA' / 'A' / 'BBB'
    BOND_MATURITY_YEAR  INTEGER,
    YIELD_PERCENT       FLOAT,
    SPREAD_BPS          FLOAT,        -- 対国債スプレッド（bps）
    CHANGE_FROM_MONTH   FLOAT,
    DATA_SOURCE         VARCHAR(50),
    CREATED_AT          TIMESTAMP_NTZ
);
```

### 15.4 法人営業部側の統合ビュー

```sql
CREATE OR REPLACE VIEW NIPPONLIFE_DEMO_DB.ANALYTICS.V_MARKET_INSIGHT AS
SELECT
    c.COMPANY_ID,
    c.COMPANY_NAME,
    c.INDUSTRY_LARGE,
    c.PENSION_TYPE,
    c.STOCK_TICKER,
    -- 最新株価（共有データから直接 JOIN）
    sp.CLOSING_PRICE                AS LATEST_STOCK_PRICE,
    sp.CHANGE_1M_PCT                AS STOCK_1M_CHANGE_PCT,
    sp.CHANGE_1Y_PCT                AS STOCK_1Y_CHANGE_PCT,
    sp.MARKET_CAP_JPY               AS MARKET_CAP,
    CASE
        WHEN sp.CHANGE_1M_PCT < -10 THEN '要注意（株価急落）'
        WHEN sp.CHANGE_1M_PCT < -5  THEN '注意（株価下落）'
        WHEN sp.CHANGE_1M_PCT > 10  THEN '好調（株価急騰）'
        ELSE '安定'
    END                             AS STOCK_SIGNAL,
    -- 最新金利（DB年金への影響）
    ir.RATE_PERCENT                 AS CURRENT_10Y_RATE,
    ir.CHANGE_FROM_YEAR             AS RATE_CHANGE_1Y,
    CASE
        WHEN ir.RATE_PERCENT > 1.0 AND ir.CHANGE_FROM_YEAR > 0
            THEN 'DB積立改善傾向 → DC移行の好機'
        WHEN ir.RATE_PERCENT < 0.5
            THEN 'DB積立不足拡大リスク → 追加掛金警戒'
        ELSE 'DB積立影響軽微'
    END                             AS PENSION_RATE_SIGNAL,
    -- 信用スプレッド
    cs.SPREAD_BPS                   AS CREDIT_SPREAD_BPS,
    cs.CREDIT_RATING,
    -- 見込み情報
    p.CURRENT_RANK                  AS PROSPECT_RANK,
    p.AI_SCORE                      AS PROSPECT_AI_SCORE,
    p.PROSPECT_AMOUNT
FROM NIPPONLIFE_DEMO_DB.RAW.T_CUSTOMER_COMPANIES c
LEFT JOIN MARKET_DATA_SHARED.PUBLIC.STOCK_PRICES sp
    ON sp.TICKER = c.STOCK_TICKER
    AND sp.PRICE_DATE = (
        SELECT MAX(PRICE_DATE) FROM MARKET_DATA_SHARED.PUBLIC.STOCK_PRICES)
LEFT JOIN MARKET_DATA_SHARED.PUBLIC.INTEREST_RATES ir
    ON ir.INSTRUMENT = '日本国債10年'
    AND ir.RATE_DATE = (
        SELECT MAX(RATE_DATE) FROM MARKET_DATA_SHARED.PUBLIC.INTEREST_RATES)
LEFT JOIN MARKET_DATA_SHARED.PUBLIC.CREDIT_SPREADS cs
    ON cs.COMPANY_NAME = c.COMPANY_NAME
    AND cs.SPREAD_DATE = (
        SELECT MAX(SPREAD_DATE) FROM MARKET_DATA_SHARED.PUBLIC.CREDIT_SPREADS)
LEFT JOIN NIPPONLIFE_DEMO_DB.RAW.T_PROSPECTS p
    ON p.COMPANY_ID = c.COMPANY_ID;
```

### 15.5 App 6: マーケット・インサイトダッシュボード（新設）

目的: 担当先企業の株価動向 × 金利環境を一画面で確認し、提案のタイミングと論点を把握する。

```
  [マーケット・インサイト]  データ提供: 財務企画部 Snowflake（リアルタイム共有）

  長期金利（10年国債）            市場サマリー
  現在: 1.45%  +0.35%(1年)       金利環境: 上昇局面
  [2年間の折れ線グラフ]           DB年金: 積立改善中
  DB計算基準金利（点線）          提案機会: DC移行 ★★★

  担当先企業の株価シグナル   [1M / 3M / 1Y 切替]
  伊藤忠商事   A  +8.2%  AA   [緑] 福利厚生強化の好機
  パナソニックHD B -4.1%  A    [黄] 株価下落→事業保障訴求
  トヨタ自動車 B  +2.3%  AA+  [緑] 安定→DC移行提案適期
  野村HD       B  -7.5%  A    [赤] 急落→役員保険緊急訴求
  JERA         C  —       BBB  [青] 金利上昇で設備投資加速

  金利×保険提案タイミング分析（AI生成）
  ① DC移行提案: ★★★ 最適タイミング
     金利上昇→DB積立余剰発生→移行コストが低い
     対象: トヨタ・パナソニック・伊藤忠
  ② 役員退職慰労金保険: ★★
     高金利→保険予定利率改善→積立効率UP
     対象: 野村HD（株価下落+金利上昇）

  [SI で詳細分析] [提案書に金利分析を追加]
```

**Streamlit 実装コード**:
```python
import streamlit as st
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session

session = get_active_session()

# 財務企画部共有データを参照（ゼロコピー・リアルタイム）
df_rates = session.sql("""
    SELECT RATE_DATE, RATE_PERCENT, CHANGE_FROM_YEAR
    FROM MARKET_DATA_SHARED.PUBLIC.INTEREST_RATES
    WHERE INSTRUMENT = '日本国債10年'
      AND RATE_DATE >= DATEADD(YEAR, -2, CURRENT_DATE)
    ORDER BY RATE_DATE
""").to_pandas()

df_market = session.sql(
    "SELECT * FROM NIPPONLIFE_DEMO_DB.ANALYTICS.V_MARKET_INSIGHT"
    " ORDER BY PROSPECT_AI_SCORE DESC NULLS LAST"
).to_pandas()

st.caption("データ提供: 日本生命 財務企画部 Snowflake（Secure Data Sharing・ゼロコピー）")

# 金利チャート
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_rates['RATE_DATE'], y=df_rates['RATE_PERCENT'],
    mode='lines', line=dict(color='#E60012', width=2),
    name='10年国債利回り'
))
fig.add_hline(y=1.0, line_dash="dash", line_color="#888",
              annotation_text="DB年金計算基準金利（目安）")
fig.update_layout(title='長期金利推移',  yaxis_title='利回り（%）')
st.plotly_chart(fig, use_container_width=True)

# 株価シグナル一覧
for _, row in df_market.iterrows():
    chg = row.get('STOCK_1M_CHANGE_PCT') or 0
    icon = "🟢" if chg > 5 else "🔴" if chg < -5 else "✅"
    with st.expander(
        f"{icon} {row['COMPANY_NAME']} | ランク {row['PROSPECT_RANK']} "
        f"| 株価 {chg:+.1f}% (1M)"
    ):
        c1, c2 = st.columns(2)
        with c1:
            price = row.get('LATEST_STOCK_PRICE')
            st.metric("現在株価",
                      f"¥{price:,.0f}" if price else "非上場",
                      f"{chg:+.1f}% (1M)")
        with c2:
            st.info(f"**金利シグナル**: {row.get('PENSION_RATE_SIGNAL', '—')}")
            st.info(f"**株価シグナル**: {row.get('STOCK_SIGNAL', '—')}")
```

### 15.6 SI Tool 9: market_context_analysis（市場コンテキスト分析）

```yaml
tool_type: sql_execution
tool_name: market_context_analysis
description: >
  金利・株価・信用スプレッド等の市場データと顧客の見込み情報を統合し、
  「今の市場環境で最も刺さる提案」を特定します。
  「金利が上がっているが DC 移行を提案すべき顧客は？」
  「株価急落している担当先で急いでアプローチすべき企業は？」に使用。
  財務企画部の Snowflake から共有された最新市場データを参照。
query_template: >
  SELECT COMPANY_NAME, PROSPECT_RANK, STOCK_SIGNAL,
         PENSION_RATE_SIGNAL, CREDIT_RATING,
         STOCK_1M_CHANGE_PCT, CURRENT_10Y_RATE, PROSPECT_AMOUNT
  FROM NIPPONLIFE_DEMO_DB.ANALYTICS.V_MARKET_INSIGHT
  WHERE PROSPECT_RANK IN ('A','B','C')
  ORDER BY
    CASE PROSPECT_RANK WHEN 'A' THEN 1 WHEN 'B' THEN 2 ELSE 3 END,
    ABS(STOCK_1M_CHANGE_PCT) DESC NULLS LAST
```

**SI デモプロンプト例**:
```
「足元の金利環境と担当先の株価動向を踏まえて、
 今月中にアプローチすべき企業と具体的な提案内容を教えてください」

SI の出力例:
  10年金利が1.45%（1年前比+0.35%ポイント）に上昇しており、
  DB年金の積立余剰が改善しています。最適タイミングは以下の2社です:

  ① トヨタ自動車（Bランク）: DC移行の移行コストが今最小。
    85,000名規模での移行は年間掛金削減効果が最大。
    来週の商談で提案書を提出推奨。

  ② 野村HD（Bランク）: 株価が-7.5%(1M)と下落中。
    財務プレッシャーが高まる今、役員退職慰労金保険の
    積立強化を事業継続の観点で訴求できる。
```

### 15.7 Snowflake Data Sharing vs Databricks Delta Sharing

| 観点 | Databricks Delta Sharing | Snowflake Secure Data Sharing |
|-----|------------------------|-----------------------------|
| 共有の仕組み | Delta Lake + REST API | ネイティブメタデータ共有 |
| データコピー | あり（一部ゼロコピー可） | **完全ゼロコピー** |
| セットアップ | Recipient トークン発行が必要 | `ALTER SHARE ADD ACCOUNT` 1行 |
| リアルタイム性 | バッチ更新が基本 | **即時反映** |
| セキュリティ | 共有先アクセス制御 | 行・列レベルセキュリティそのまま適用 |
| クロスリージョン | 追加設定が必要 | **Global Data Sharing で自動** |
| コスト（受信側） | コンピュート費用発生 | **Snowflake アカウントがあれば無料** |

**デモでの訴求文**:
「財務企画部のリアルタイム金利・株価データを法人営業部が使う。
設定は SQL 3行。データはコピーされないので常に最新。
これが Snowflake のデータクラウドです。
Databricks Delta Sharing は受信側にもコンピュートが必要ですが、
Snowflake はゼロコピーで即時共有できます。」

### 15.8 デモシナリオへの組み込み

**朝のアラートダッシュボード（App2）に市場シグナルを追加**:
```
  [市場シグナル]  データ提供: 財務企画部 Snowflake（リアルタイム共有）
  10年金利: 1.45%  +0.35%(1年) → DC移行提案の好機
  野村HD株価: -7.5%(1M) → 役員保険の緊急訴求
  伊藤忠商事株価: +8.2%(1M) → 福利厚生強化提案好機
```

**SI への統合プロンプト例（商談前企業情報収集に追加）**:
```
「現在の金利環境（10年金利1.45%）と伊藤忠商事の直近株価動向を踏まえて、
 今回のM&A案件に対する最適な提案書の構成を考えてください。
 特にDC移行のタイミング的な優位性を数字で示せますか？」
```
