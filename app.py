"""
Honda 四輪事業 中長期戦略シミュレーションツール
メインアプリケーション エントリーポイント
"""

import dash
from dash import html, dcc

from layouts.timeline import create_timeline_layout
from layouts.volume_editor import create_volume_editor_layout
from layouts.dashboard import create_dashboard_layout
from layouts.financial_editor import create_financial_editor_layout
from layouts.non_financial_editor import create_non_financial_editor_layout
from layouts.factory_editor import create_factory_editor_layout
from layouts.development_editor import create_development_editor_layout
from layouts.factory_charts import create_factory_charts_layout
from callbacks.simulation_cb import register_callbacks


# ------------------------------------------------------------------
# Dash アプリ初期化
# ------------------------------------------------------------------
app = dash.Dash(
    __name__,
    title="Honda 四輪戦略シミュレーター",
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Honda四輪事業の中長期戦略シミュレーションツール"},
    ],
)
server = app.server


# ------------------------------------------------------------------
# レイアウト
# ------------------------------------------------------------------
app.layout = html.Div([
    # データストア（クライアントサイド）
    dcc.Store(id="sim-data-store"),
    dcc.Store(id="financial-data-store"),
    dcc.Store(id="non-financial-data-store"),
    dcc.Store(id="factory-data-store"),
    dcc.Store(id="development-data-store"),

    # 初期化トリガー
    html.Div(id="app-init-trigger", style={"display": "none"}),

    # ヘッダー
    html.Div([
        html.Div([
            html.Div("HONDA", className="header-logo"),
            html.Div("四輪事業 中長期戦略シミュレーター", className="header-subtitle"),
        ], className="header-left"),
        html.Div([
            html.Span("Strategy Simulation Tool v1.0"),
        ], className="header-right"),
    ], className="app-header"),

    # タブナビゲーション
    dcc.Tabs([
        dcc.Tab(
            label="🚄 タイムライン",
            children=create_timeline_layout(),
            className="custom-tab",
            selected_className="custom-tab--selected",
        ),
        dcc.Tab(
            label="✏️ 台数変更",
            children=create_volume_editor_layout(),
            className="custom-tab",
            selected_className="custom-tab--selected",
        ),
        dcc.Tab(
            label="📈 ダッシュボード",
            children=create_dashboard_layout(),
            className="custom-tab",
            selected_className="custom-tab--selected",
        ),
        dcc.Tab(
            label="💰 財務設定",
            children=create_financial_editor_layout(),
            className="custom-tab",
            selected_className="custom-tab--selected",
        ),
        dcc.Tab(
            label="🧪 開発設定",
            children=create_development_editor_layout(),
            className="custom-tab",
            selected_className="custom-tab--selected",
        ),
        dcc.Tab(
            label="🌱 非財務設定",
            children=create_non_financial_editor_layout(),
            className="custom-tab",
            selected_className="custom-tab--selected",
        ),
        dcc.Tab(
            label="🏭 工場設定",
            children=create_factory_editor_layout(),
            className="custom-tab",
            selected_className="custom-tab--selected",
        ),
        dcc.Tab(
            label="📊 生産可視化",
            children=create_factory_charts_layout(),
            className="custom-tab",
            selected_className="custom-tab--selected",
        ),
    ], className="custom-tabs"),

], id="main-container")


# ------------------------------------------------------------------
# コールバック登録
# ------------------------------------------------------------------
register_callbacks(app)


# ------------------------------------------------------------------
# サーバー起動
# ------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050, use_reloader=False)
