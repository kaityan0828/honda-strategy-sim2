"""
財務設定画面
マスターデータ（単価・固定費・変動費）を編集するためのタブレイアウト
"""

from dash import html, dcc, dash_table


def create_financial_editor_layout():
    """財務設定タブのレイアウト"""
    return html.Div([
        # ── セクション: 財務マスターデータ ──
        html.Div([
            html.H3("💰 財務・損益パラメーター", className="section-title"),
            html.P("各モデルの単価（万円）、固定費（億円/年）、変動費（万円/台）を編集してシミュレーションを行います。",
                    className="section-desc"),
        ], className="section-header"),

        # 編集可能データテーブル
        html.Div([
            dash_table.DataTable(
                id="financial-table",
                columns=[
                    {"name": "モデル",       "id": "model",      "editable": False},
                    {"name": "単価 (万円)",  "id": "price",      "editable": True, "type": "numeric"},
                    {"name": "固定費 (億円/年)", "id": "fixed_cost", "editable": True, "type": "numeric"},
                    {"name": "変動費 (万円/台)", "id": "var_cost",   "editable": True, "type": "numeric"},
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
                    "minWidth": "100px",
                },
                style_data_conditional=[
                    {
                        "if": {"column_id": ["price", "fixed_cost", "var_cost"]},
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
            html.H3("💡 利益計算ロジックについて", className="section-title", style={"fontSize": "16px"}),
            html.Ul([
                html.Li("当期のモデル別売上高 = 累計販売台数 × 単価"),
                html.Li("当期のモデル別営業利益 = 当期のモデル別売上高 - (固定費 + (変動費 × 累計販売台数))"),
                html.Li("総額および利益率は、これらの合算としてダッシュボード（KPI）に反映されます。")
            ], style={"color": "#9CA3AF", "fontSize": "14px", "lineHeight": "1.6"})
        ], className="info-block", style={"padding": "20px", "backgroundColor": "#1F2937", "borderRadius": "8px", "marginTop": "20px"}),

    ], className="tab-content")
