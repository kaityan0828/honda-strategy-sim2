"""
開発工数・費用設定画面
モデルごとの機種生涯工数（人月）と単価を編集するためのタブレイアウト
"""

from dash import html, dcc, dash_table


def create_development_editor_layout():
    """開発設定タブのレイアウト"""
    return html.Div([
        # ── セクション: 開発マスターデータ ──
        html.Div([
            html.H3("🧪 開発工数・単価設定", className="section-title"),
            html.P("各モデルの開発に必要な総工数（機種生涯工数）と人月単価を編集します。費用は販売開始の3年前から発生します。",
                    className="section-desc"),
        ], className="section-header"),

        # 編集可能データテーブル
        html.Div([
            dash_table.DataTable(
                id="development-table",
                columns=[
                    {"name": "モデル",       "id": "model",      "editable": False},
                    {"name": "機種生涯工数 (人月)", "id": "lifespan_man_months", "editable": True, "type": "numeric"},
                    {"name": "人月単価 (万円/月)",  "id": "unit_cost",           "editable": True, "type": "numeric"},
                ],
                data=[],
                page_size=20,
                sort_action="native",
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": "#1F2937",
                    "color": "#F9FAFB",
                    "fontWeight": "bold",
                    "border": "1px solid #374151",
                    "textAlign": "center",
                    "padding": "12px 8px",
                },
                style_cell={
                    "backgroundColor": "#111827",
                    "color": "#D1D5DB",
                    "border": "1px solid #1F2937",
                    "textAlign": "center",
                    "padding": "10px 8px",
                    "fontFamily": "Inter, sans-serif",
                    "fontSize": "14px",
                    "minWidth": "150px",
                },
                style_data_conditional=[
                    {
                        "if": {"column_id": ["lifespan_man_months", "unit_cost"]},
                        "backgroundColor": "#1a1a2e",
                        "color": "#60A5FA",
                        "fontWeight": "bold",
                        "cursor": "pointer",
                        "border": "1px solid #3B82F6",
                    },
                    {
                        "if": {"state": "active"},
                        "backgroundColor": "#2563EB",
                        "color": "#FFFFFF",
                        "border": "1px solid #60A5FA",
                    },
                ],
            ),
        ], className="table-container", style={"maxWidth": "800px"}),

        html.Hr(className="section-divider"),

        # 注意書きサマリー
        html.Div([
            html.H3("💡 開発費算出ロジックについて", className="section-title", style={"fontSize": "16px"}),
            html.Ul([
                html.Li("開発期間：各モデルの販売開始年度（Start Year）の3年前から1年前までの3年間と定義します。"),
                html.Li("工数配布：機種生涯工数を開発期間の3年間に均等に割り当てます（例：15,000人月 → 5,000人月/年）。"),
                html.Li("年度別開発費 = 年度別工数 × 人月単価。"),
                html.Li("算出された費用は「ダッシュボード」の推移グラフおよび損益計算に反映されます。")
            ], style={"color": "#9CA3AF", "fontSize": "14px", "lineHeight": "1.6"})
        ], className="info-block", style={"padding": "20px", "backgroundColor": "#1F2937", "borderRadius": "8px", "marginTop": "20px"}),

    ], className="tab-content")
