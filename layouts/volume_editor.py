"""
台数変更画面
データテーブルの編集・モデル追加/削除・工場変更・タイムライン変更のUI
"""

from dash import html, dcc, dash_table


def create_volume_editor_layout():
    """台数変更タブのレイアウト"""
    return html.Div([
        # ── セクション: データテーブル ──
        html.Div([
            html.H3("📊 台数シミュレーション", className="section-title"),
            html.P("テーブル内の台数（Volume）セルを直接編集すると、ダッシュボードにリアルタイム反映されます",
                    className="section-desc"),
        ], className="section-header"),

        # フィルターバー
        html.Div([
            html.Div([
                html.Label("モデル", className="filter-label"),
                dcc.Dropdown(
                    id="editor-model-filter",
                    options=[{"label": "全モデル", "value": "ALL"}],
                    value="ALL",
                    className="dropdown-dark",
                    clearable=False,
                ),
            ], className="filter-item"),
            html.Div([
                html.Label("地域", className="filter-label"),
                dcc.Dropdown(
                    id="editor-region-filter",
                    options=[{"label": "全地域", "value": "ALL"}],
                    value="ALL",
                    className="dropdown-dark",
                    clearable=False,
                ),
            ], className="filter-item"),
            html.Div([
                html.Label("年度", className="filter-label"),
                dcc.Dropdown(
                    id="editor-year-filter",
                    options=[{"label": "全年度", "value": "ALL"}],
                    value="ALL",
                    className="dropdown-dark",
                    clearable=False,
                ),
            ], className="filter-item"),
            html.Div([
                html.Label("PT", className="filter-label"),
                dcc.Dropdown(
                    id="editor-pt-filter",
                    options=[
                        {"label": "全PT", "value": "ALL"},
                        {"label": "PET", "value": "PET"},
                        {"label": "FFV", "value": "FFV"},
                        {"label": "HEV", "value": "HEV"},
                        {"label": "HEVFFV", "value": "HEVFFV"},
                        {"label": "PHEV", "value": "PHEV"},
                        {"label": "BEV", "value": "BEV"},
                        {"label": "FCV", "value": "FCV"},
                    ],
                    value="ALL",
                    className="dropdown-dark",
                    clearable=False,
                ),
            ], className="filter-item"),
            
            # Excel連携ボタン
            html.Div([
                html.Label("エクセル連動", className="filter-label"),
                html.Div([
                    html.Button("📥 Export", id="export-excel-btn", className="btn-secondary", style={"marginRight": "10px"}),
                    dcc.Upload(
                        id="import-excel-upload",
                        children=html.Button("📤 Import", className="btn-secondary"),
                        multiple=False
                    ),
                ], style={"display": "flex"}),
                dcc.Download(id="export-excel-download"),
            ], className="filter-item", style={"flexGrow": 1, "justifyContent": "flex-end"}),
        ], className="filter-bar"),

        # 編集可能データテーブル
        html.Div([
            dash_table.DataTable(
                id="volume-table",
                columns=[
                    {"name": "モデル",   "id": "model",      "editable": True},
                    {"name": "地域",     "id": "region",     "editable": True},
                    {"name": "PT",       "id": "powertrain", "editable": True},
                    {"name": "Dr",       "id": "drive",      "editable": True},
                    {"name": "工場",     "id": "plant",      "editable": True},
                    {"name": "年度",     "id": "year",       "editable": True, "type": "numeric"},
                    {"name": "台数",     "id": "volume",     "editable": True, "type": "numeric",
                     "format": {"specifier": ","}},
                ],
                data=[],
                page_size=15,
                sort_action="native",
                sort_mode="multi",
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
                    "fontSize": "13px",
                    "minWidth": "80px",
                },
                style_data_conditional=[
                    {
                        "if": {"state": "active"},
                        "backgroundColor": "#2563EB",
                        "color": "#FFFFFF",
                        "border": "1px solid #60A5FA",
                    },
                    {
                        "if": {"state": "active"},
                        "backgroundColor": "#2563EB",
                        "color": "#FFFFFF",
                        "border": "1px solid #60A5FA",
                    },
                ],
            ),
        ], className="table-container"),

        html.Hr(className="section-divider"),

        # ── セクション: モデル追加 ──
        html.Div([
            html.H3("➕ モデル追加", className="section-title"),
            html.P("新しいモデルを計画に追加します", className="section-desc"),
        ], className="section-header"),

        html.Div([
            html.Div([
                html.Div([
                    html.Label("モデル名", className="input-label"),
                    dcc.Input(id="add-model-name", type="text",
                              placeholder="例: New EV SUV", className="text-input"),
                ], className="form-field"),
                html.Div([
                    html.Label("パワートレイン", className="input-label"),
                    dcc.Dropdown(
                        id="add-model-pt",
                        options=[
                            {"label": "PET", "value": "PET"},
                            {"label": "FFV", "value": "FFV"},
                            {"label": "HEV", "value": "HEV"},
                            {"label": "HEVFFV", "value": "HEVFFV"},
                            {"label": "PHEV", "value": "PHEV"},
                            {"label": "BEV", "value": "BEV"},
                            {"label": "FCV", "value": "FCV"},
                        ],
                        value="BEV",
                        className="dropdown-dark",
                        clearable=False,
                    ),
                ], className="form-field"),
                html.Div([
                    html.Label("駆動方式", className="input-label"),
                    dcc.Dropdown(
                        id="add-model-drive",
                        options=[
                            {"label": "FF", "value": "FF"},
                            {"label": "4WD", "value": "4WD"},
                        ],
                        value="FF",
                        className="dropdown-dark",
                        clearable=False,
                    ),
                ], className="form-field"),
            ], className="form-row"),

            html.Div([
                html.Div([
                    html.Label("工場", className="input-label"),
                    dcc.Dropdown(id="add-model-plant", options=[], value=None,
                                 className="dropdown-dark", clearable=False),
                ], className="form-field"),
                html.Div([
                    html.Label("地域", className="input-label"),
                    dcc.Dropdown(
                        id="add-model-region", 
                        options=[], 
                        value=[],
                        multi=True,
                        className="dropdown-dark", 
                        clearable=False
                    ),
                ], className="form-field"),
                html.Div([
                    html.Label("台数 (台/年)", className="input-label"),
                    dcc.Input(id="add-model-volume", type="number",
                              value=50000, className="text-input"),
                ], className="form-field"),
            ], className="form-row"),

            html.Div([
                html.Div([
                    html.Label("開始年度", className="input-label"),
                    dcc.Input(id="add-model-start", type="number",
                              value=2026, min=2025, max=2035, className="text-input"),
                ], className="form-field"),
                html.Div([
                    html.Label("終了年度", className="input-label"),
                    dcc.Input(id="add-model-end", type="number",
                              value=2035, min=2025, max=2035, className="text-input"),
                ], className="form-field"),
                html.Div([
                    html.Button("モデルを追加", id="add-model-btn",
                                className="btn-primary"),
                ], className="form-field btn-field"),
            ], className="form-row"),
        ], className="form-container"),

        html.Hr(className="section-divider"),

        # ── セクション: モデル削除 ──
        html.Div([
            html.H3("🗑️ モデル削除", className="section-title"),
        ], className="section-header"),

        html.Div([
            html.Div([
                html.Label("削除するモデル", className="input-label"),
                dcc.Dropdown(id="delete-model-dropdown", options=[], value=None,
                             className="dropdown-dark"),
            ], className="form-field"),
            html.Div([
                html.Button("モデルを削除", id="delete-model-btn",
                            className="btn-danger"),
            ], className="form-field btn-field"),
        ], className="form-row-inline"),

        # 通知エリア
        html.Div(id="editor-notification", className="notification-area"),

    ], className="tab-content")
