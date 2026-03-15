"""
工場設定画面
各工場のキャパシティ（生産能力）を編集するためのタブレイアウト
"""

from dash import html, dcc, dash_table


def create_factory_editor_layout():
    """工場設定タブのレイアウト"""
    return html.Div([
        # ── セクション: 工場キャパシティマスター ──
        html.Div([
            html.H3("🏭 工場キャパシティ設定", className="section-title"),
            html.P("各工場の年間生産能力（キャパシティ）を調整します。現在の合計生産台数と比較し、稼働状況をシミュレーションします。",
                    className="section-desc"),
        ], className="section-header"),

        # 編集可能データテーブル (マトリクス形式)
        html.Div([
            dash_table.DataTable(
                id="factory-matrix-table",
                columns=[],  # コールバックで動的に生成
                data=[],
                editable=True,
                merge_duplicate_headers=True,  # マルチヘッダー用
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
                    "padding": "4px 2px",
                    "fontFamily": "Inter, sans-serif",
                    "fontSize": "11px",
                    "minWidth": "60px",
                },
                style_data_conditional=[
                    # 編集可能列（能力値）の強調
                    {
                        "if": {"column_editable": True},
                        "backgroundColor": "#1a1a2e",
                        "color": "#60A5FA", 
                        "fontWeight": "bold",
                        "cursor": "pointer",
                        "border": "1px solid #3B82F6",
                    },
                ] + [
                    # 稼働率による警告表示 (全年度分生成)
                    {
                        "if": {
                            "column_id": f"{year}_util",
                            "filter_query": f"{{{year}_util}} > 100"
                        },
                        "color": "#EF4444",
                        "fontWeight": "bold",
                    } for year in range(2025, 2036)
                ] + [
                    {
                        "if": {
                            "column_id": f"{year}_util",
                            "filter_query": f"{{{year}_util}} <= 100"
                        },
                        "color": "#10B981",
                    } for year in range(2025, 2036)
                ] + [
                    {
                        "if": {"state": "active"},
                        "backgroundColor": "#2563EB",
                        "color": "#FFFFFF",
                        "border": "1px solid #60A5FA",
                    },
                ],
            ),
        ], className="table-container", style={"maxWidth": "1200px"}),

        html.Hr(className="section-divider"),

        # 注意書きサマリー
        html.Div([
            html.H3("💡 工場稼働率の計算について", className="section-title", style={"fontSize": "16px"}),
            html.Ul([
                html.Li("能力マトリクス: 各行が工場、各列が2025年から2035年までの各年度の生産能力（台）を表しています。"),
                html.Li("編集: セルを直接編集することで、その年度・その工場の能力値を変更できます。"),
                html.Li("反映: 編集した内容は「生産可視化」タブの能力線や、ダッシュボードの稼働率計算に即座に反映されます。"),
            ], style={"color": "#9CA3AF", "fontSize": "14px", "lineHeight": "1.6"})
        ], className="info-block", style={"padding": "20px", "backgroundColor": "#1F2937", "borderRadius": "8px", "marginTop": "20px"}),

    ], className="tab-content")
