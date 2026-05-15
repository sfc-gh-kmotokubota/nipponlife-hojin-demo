#!/usr/bin/env python3
"""
setup.py - 日本生命 法人営業DXデモ ワンクリックデプロイ
使用方法: SNOWFLAKE_CONNECTION_NAME=<接続名> python3 setup.py
例: SNOWFLAKE_CONNECTION_NAME=UL02714 python3 setup.py
"""
import os
import sys
import json
import subprocess
import snowflake.connector

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR  = os.path.join(REPO_DIR, "sql")
SI_DIR   = os.path.join(REPO_DIR, "si_agent")
ST_DIR   = os.path.join(REPO_DIR, "streamlit")

CONN_NAME = os.getenv("SNOWFLAKE_CONNECTION_NAME")
if not CONN_NAME:
    print("ERROR: SNOWFLAKE_CONNECTION_NAME 環境変数を設定してください")
    print("例: SNOWFLAKE_CONNECTION_NAME=UL02714 python3 setup.py")
    sys.exit(1)

print(f"{'='*60}")
print(f"日本生命 法人営業DXデモ - ワンクリックデプロイ")
print(f"接続名: {CONN_NAME}")
print(f"{'='*60}")

conn = snowflake.connector.connect(connection_name=CONN_NAME)
cur = conn.cursor()
cur.execute("USE ROLE ACCOUNTADMIN")

def run_sql_file(filepath, label=None):
    fname = label or os.path.basename(filepath)
    print(f"\n[{fname}] 実行中...")
    with open(filepath, "r") as f:
        content = f.read()
    statements = [s.strip() for s in content.split(";") if s.strip()]
    ok = err = 0
    for stmt in statements:
        lines = [l for l in stmt.split("\n") if l.strip() and not l.strip().startswith("--")]
        if not lines:
            continue
        try:
            cur.execute(stmt)
            ok += 1
        except Exception as e:
            err += 1
            print(f"  WARN: {str(e)[:120]}")
    print(f"  完了: {ok}成功, {err}エラー")

# ============================================================
# Phase 1: DB / WH / スキーマ / テーブル / マスターデータ
# ============================================================
print("\n" + "="*60)
print("Phase 1: データベース・テーブル・マスターデータ")
print("="*60)

run_sql_file(f"{SQL_DIR}/00_setup.sql", "DB/WH/スキーマ作成")
run_sql_file(f"{SQL_DIR}/01_ddl.sql", "テーブル作成")
run_sql_file(f"{SQL_DIR}/02_master_data.sql", "マスターデータ投入")

# ============================================================
# Phase 2: ダミーデータ生成
# ============================================================
print("\n" + "="*60)
print("Phase 2: ダミーデータ生成 (数分かかります)")
print("="*60)

gen_script = f"{SQL_DIR}/03_generate_data.py"
if os.path.exists(gen_script):
    result = subprocess.run(
        [sys.executable, "-u", gen_script],
        env={**os.environ, "SNOWFLAKE_CONNECTION_NAME": CONN_NAME},
        cwd=SQL_DIR,
        capture_output=False
    )
    if result.returncode != 0:
        print("  WARNING: データ生成でエラーが発生しました")
else:
    print("  SKIP: 03_generate_data.py が見つかりません")

# ============================================================
# Phase 3: ビュー
# ============================================================
print("\n" + "="*60)
print("Phase 3: 分析ビュー作成")
print("="*60)

run_sql_file(f"{SQL_DIR}/08_views.sql", "ビュー作成")

# ============================================================
# Phase 4: Cortex Search
# ============================================================
print("\n" + "="*60)
print("Phase 4: Cortex Search サービス作成")
print("="*60)

run_sql_file(f"{SQL_DIR}/09_cortex_search.sql", "Cortex Search")

# ============================================================
# Phase 5: Semantic View (YAML 経由)
# ============================================================
print("\n" + "="*60)
print("Phase 5: Semantic View 作成")
print("="*60)

sv_yaml_path = f"{SQL_DIR}/sv_sales_analytics.yaml"
if os.path.exists(sv_yaml_path):
    with open(sv_yaml_path, "r") as f:
        yaml_content = f.read()
    try:
        cur.execute("USE DATABASE NIPPONLIFE_DEMO_DB")
        cur.execute(
            "CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(%s, %s)",
            ("NIPPONLIFE_DEMO_DB.ANALYTICS", yaml_content)
        )
        print(f"  Semantic View 作成成功: {cur.fetchone()[0]}")
    except Exception as e:
        print(f"  Semantic View エラー: {str(e)[:150]}")
else:
    print("  SKIP: sv_sales_analytics.yaml が見つかりません")

# ============================================================
# Phase 6: Streamlit デプロイ
# ============================================================
print("\n" + "="*60)
print("Phase 6: Streamlit アプリデプロイ")
print("="*60)

try:
    result = subprocess.run(
        ["snow", "streamlit", "deploy", "--replace",
         "--connection", CONN_NAME,
         "--dbname", "NIPPONLIFE_DEMO_DB",
         "--schemaname", "RAW"],
        cwd=ST_DIR,
        capture_output=True, text=True, timeout=120
    )
    if "successfully deployed" in result.stdout:
        for line in result.stdout.split("\n"):
            if "available under" in line:
                print(f"  {line.strip()}")
                break
        print("  Streamlit デプロイ成功")
    else:
        print(f"  Streamlit 出力: {result.stdout[-200:]}")
        if result.stderr:
            print(f"  stderr: {result.stderr[-200:]}")
except Exception as e:
    print(f"  Streamlit デプロイエラー: {e}")

# ============================================================
# Phase 7: Cortex Agent 作成
# ============================================================
print("\n" + "="*60)
print("Phase 7: Cortex Agent + Skills 作成")
print("="*60)

cur.execute("USE DATABASE NIPPONLIFE_DEMO_DB")
cur.execute("USE SCHEMA RAW")
cur.execute("USE WAREHOUSE NIPPONLIFE_DEMO_WH")

# Skills ステージ + アップロード
cur.execute("CREATE STAGE IF NOT EXISTS NIPPONLIFE_DEMO_DB.RAW.NIPPONLIFE_SKILLS DIRECTORY = (ENABLE = TRUE)")
skill_files = {
    "proposal_generation": "skill_proposal_generation.md",
    "compliance_guidelines": "skill_compliance_guidelines.md",
}
for skill_name, filename in skill_files.items():
    fpath = os.path.join(SI_DIR, filename)
    if os.path.exists(fpath):
        cur.execute(f"PUT file://{fpath} @NIPPONLIFE_DEMO_DB.RAW.NIPPONLIFE_SKILLS/{skill_name}/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
        print(f"  Skill アップロード: {skill_name}")

# Agent 作成
spec_path = os.path.join(SI_DIR, "agent_spec.json")
if os.path.exists(spec_path):
    with open(spec_path, "r") as f:
        spec = json.load(f)
    spec_str = json.dumps(spec, ensure_ascii=False)
    try:
        cur.execute("CREATE OR REPLACE AGENT NIPPONLIFE_DEMO_DB.RAW.NIPPONLIFE_SALES_AGENT FROM SPECIFICATION $$" + spec_str + "$$")
        print("  Agent 作成成功")
        cur.execute("ALTER AGENT NIPPONLIFE_DEMO_DB.RAW.NIPPONLIFE_SALES_AGENT SET COMMENT = '日本生命保険 法人営業AIアシスタント | 担当先企業の事業イベント検知・商品マッチング・DP作成・コンプライアンスチェックを自然言語でサポート'")
        print("  Agent COMMENT 設定完了")
    except Exception as e:
        print(f"  Agent 作成エラー: {str(e)[:150]}")

# ============================================================
# Phase 8: ストアドプロシージャ (PPTX/Word 生成)
# ============================================================
print("\n" + "="*60)
print("Phase 8: PPTX/Word 生成ストアドプロシージャ")
print("="*60)

sp_script = f"{SQL_DIR}/04_stored_procedures.py"
if os.path.exists(sp_script):
    result = subprocess.run(
        [sys.executable, sp_script],
        env={**os.environ, "SNOWFLAKE_CONNECTION_NAME": CONN_NAME},
        capture_output=True, text=True, timeout=300
    )
    print(result.stdout[-300:] if result.stdout else "  (出力なし)")
    if result.returncode != 0 and result.stderr:
        print(f"  stderr: {result.stderr[-200:]}")
else:
    print("  SKIP: 04_stored_procedures.py が見つかりません")

# ============================================================
# 完了サマリー
# ============================================================
print("\n" + "="*60)
print("デプロイ完了サマリー")
print("="*60)

cur.execute("USE DATABASE NIPPONLIFE_DEMO_DB")
cur.execute("USE SCHEMA RAW")

tables = ["T_CUSTOMER_COMPANIES", "T_INSURANCE_PRODUCTS", "T_COMPANY_NEWS",
          "T_EVENT_ALERTS", "T_MEETINGS", "T_MEETING_TRANSCRIPTS",
          "T_PROSPECTS", "T_COMPANY_LOCATIONS", "T_FINANCIAL_DATA"]
print("\nデータ件数:")
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"  {t}: {cur.fetchone()[0]}")
    except:
        print(f"  {t}: ERROR")

print("\nCortex Search:")
try:
    cur.execute("SHOW CORTEX SEARCH SERVICES IN SCHEMA NIPPONLIFE_DEMO_DB.SEARCH")
    for r in cur.fetchall():
        cols = [d[0] for d in cur.description]
        d = dict(zip(cols, r))
        print(f"  {d.get('name')}: {d.get('indexing_state', '?')}")
except:
    print("  (確認できません)")

print("\nSemantic View:")
try:
    cur.execute("SHOW SEMANTIC VIEWS IN SCHEMA NIPPONLIFE_DEMO_DB.ANALYTICS")
    for r in cur.fetchall():
        cols = [d[0] for d in cur.description]
        d = dict(zip(cols, r))
        print(f"  {d.get('name')}")
except:
    print("  (確認できません)")

print("\nAgent:")
try:
    cur.execute("SHOW AGENTS LIKE 'NIPPONLIFE_SALES_AGENT' IN SCHEMA NIPPONLIFE_DEMO_DB.RAW")
    rows = cur.fetchall()
    print(f"  NIPPONLIFE_SALES_AGENT: {'存在' if rows else '未作成'}")
except:
    print("  (確認できません)")

cur.close()
conn.close()

print(f"\n{'='*60}")
print("全てのデプロイが完了しました！")
print(f"{'='*60}")
