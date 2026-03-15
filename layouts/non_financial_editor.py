"""
非財務設定画面
マスターデータ（CO2・燃費・安全評価）を編集するためのタブレイアウト
"""

from dash import html, dcc, dash_table


def create_non_financial_editor_layout():
    """非財務設定タブのレイアウト"""
    return html.Div([
        # ── セクション: 非財務マスターデータ ──
        html.Div([
            html.H3("🌱 環境・安全（非財務）パラメーター", className="section-title"),
            html.P("各モデル・PT別のCO2排出量や燃費、安全機能レベルを編集し、LCAやCAFEのシミュレーションを行います。",
                    className="section-desc"),
        ], className="section-header"),

        # 編集可能データテーブル
        html.Div([
            dash_table.DataTable(
                id="non-financial-table",
                columns=[
                    {"name": "モデル",           "id": "model",              "editable": False},
                    {"name": "PT",               "id": "powertrain",         "editable": False},
                    {"name": "製品使用 (g/km)",   "id": "co2_use",            "editable": True, "type": "numeric"},
                    {"name": "廃棄 (g/km)",       "id": "co2_disposal",       "editable": True, "type": "numeric"},
                    {"name": "生産-内作 (g/km)",  "id": "co2_production_in",  "editable": True, "type": "numeric"},
                    {"name": "生産-外作 (g/km)",  "id": "co2_production_out", "editable": True, "type": "numeric"},
                    {"name": "物流 (g/km)",       "id": "co2_logistics",      "editable": True, "type": "numeric"},
                    {"name": "エネ製造 (g/km)",   "id": "co2_energy",         "editable": True, "type": "numeric"},
                    {"name": "燃費 (km/L)",      "id": "fuel_eff",           "editable": True, "type": "numeric"},
                    {"name": "ADAS適用名称",     "id": "adas",               "editable": True, "presentation": "dropdown"},
                ],
                dropdown={
                    "adas": {
                        "options": [
                            {"label": "ADAS適用なし", "value": "ADAS適用なし"},
                            {"label": "E-ADAS", "value": "E-ADAS"},
                            {"label": "P-ADAS Gen1", "value": "P-ADAS Gen1"},
                            {"label": "P-ADAS Gen2", "value": "P-ADAS Gen2"},
                            {"label": "Elite", "value": "Elite"},
                        ],
                        "clearable": False
                    }
                },
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
                        "if": {"column_id": ["co2_use", "co2_disposal", "co2_production_in", "co2_production_out", "co2_logistics", "co2_energy", "fuel_eff", "adas"]},
                        "backgroundColor": "#1a1a2e",
                        "color": "#10B981", # Greenish to distinct from financial
                        "fontWeight": "bold",
                        "cursor": "pointer",
                        "border": "1px solid #34D399",
                    },
                    {
                        "if": {"state": "active"},
                        "backgroundColor": "#2563EB",
                        "color": "#FFFFFF",
                        "border": "1px solid #60A5FA",
                    },
                ],
                css=[
                    # ドロップダウン全体の文字色を緑色に統一
                    {"selector": ".dash-spreadsheet .Select-value-label", "rule": "color: #10B981 !important;"},
                    {"selector": ".dash-spreadsheet .Select-value", "rule": "color: #10B981 !important;"},
                    # ドロップダウンの矢印の色
                    {"selector": ".dash-spreadsheet .Select-arrow", "rule": "border-color: #10B981 transparent transparent !important;"},
                    {"selector": ".dash-spreadsheet .is-open .Select-arrow", "rule": "border-color: transparent transparent #10B981 !important;"},
                    # ドロップダウンのメニュー（選択肢リスト）の背景と文字色
                    {"selector": ".dash-spreadsheet .Select-menu-outer", "rule": "background-color: #111827 !important; color: #10B981 !important; border: 1px solid #34D399 !important;"},
                    # ホバー時・選択時の色
                    {"selector": ".dash-spreadsheet .VirtualizedSelectOption:hover", "rule": "background-color: #1F2937 !important; color: #10B981 !important;"},
                    {"selector": ".dash-spreadsheet .VirtualizedSelectFocusedOption", "rule": "background-color: #2563EB !important; color: #FFFFFF !important;"},
                ]
            ),
        ], className="table-container", style={"maxWidth": "800px"}),

        html.Hr(className="section-divider"),

        # 注意書きサマリー
        html.Div([
            html.H3("💡 非財務計算ロジックについて", className="section-title", style={"fontSize": "16px"}),
            html.Ul([
                html.Li("LCA: ライフサイクル全体での加重平均CO2排出量 (g/km)。製品使用、廃棄、生産、輸送、発電の内訳で構成されます。"),
                html.Li("CAFE: 内燃機関・ハイブリッド車を対象とした加重平均燃費 (km/L)。BEVは除外されます。"),
                html.Li("事故死亡率指数: 適用されているADASに応じて、改善係数(1.0〜0.40)を台数で加重平均して算出されます。"),
                html.Li("ADASは『Elite (係数0.40)』が最も安全とみなされ、『ADAS適用なし(係数1.0)』が基準となります。"),
            ], style={"color": "#9CA3AF", "fontSize": "14px", "lineHeight": "1.6"})
        ], className="info-block", style={"padding": "20px", "backgroundColor": "#1F2937", "borderRadius": "8px", "marginTop": "20px"}),

    ], className="tab-content")
