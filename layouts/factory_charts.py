"""
工場別生産可視化レイアウト
各工場の生産台数を年度別に積上棒グラフで表示する
"""

from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go

def create_factory_charts_layout():
    """生産可視化タブのレイアウト"""
    return html.Div([
        html.Div([
            html.H3("🏭 工場別生産ブレイクダウン", className="section-title"),
            html.P("各工場の生産台数推移を積上棒グラフで可視化します。積上単位を切り替えて詳細を分析できます。",
                    className="section-desc"),
        ], className="section-header"),

        # コントロールパネル
        html.Div([
            html.Div([
                html.Label("積上単位", className="filter-label"),
                dcc.RadioItems(
                    id="factory-chart-stack-mode",
                    options=[
                        {"label": "パワートレイン別", "value": "powertrain"},
                        {"label": "モデル別", "value": "model"},
                    ],
                    value="powertrain",
                    inline=True,
                    className="radio-dark",
                ),
            ], className="filter-item"),
        ], className="filter-bar", style={"marginBottom": "20px"}),

        # グラフコンテナ（コールバックで動的に生成）
        html.Div(id="factory-charts-container", className="charts-grid"),

    ], className="tab-content")

def create_factory_stacked_bar(df, plant_name, stack_col, capacities):
    """
    特定工場の積上棒グラフを生成
    X軸: year, Y軸: volume, 積上: stack_col, 折れ線: capacities (dict mapping year -> capacity)
    """
    if df.empty:
        # グラフが空でも枠は表示したいので、空のベースを作る
        fig = go.Figure()
        fig.update_layout(title=f"【{plant_name}】データなし", template="plotly_dark")
        return fig

    # 年度を文字列にして離散値として扱う
    df = df.copy()
    df["year"] = df["year"].astype(str)
    
    # 積上カラーマップ
    color_discrete_map = {
        "BEV": "#8B5CF6",
        "HEV": "#10B981",
        "PHEV": "#3B82F6",
        "PET": "#9CA3AF",
        "FFV": "#F59E0B",
        "HEVFFV": "#EC4899",
        "FCV": "#06B6D4",
    }

    # ベースの積上棒グラフ
    fig = px.bar(
        df,
        x="year",
        y="volume",
        color=stack_col,
        title=f"【{plant_name}】生産推移と能力",
        color_discrete_map=color_discrete_map if stack_col == "powertrain" else None,
        template="plotly_dark",
        barmode="stack",
    )

    # 能力線を追加（年度ごとに変動する折れ線）
    years = sorted(df["year"].unique())
    # 文字列年を数値に戻して検索
    cap_values = [capacities.get(int(y), 200000) for y in years]
    
    fig.add_trace(go.Scatter(
        x=years,
        y=cap_values,
        mode="lines+markers",
        name="生産能力",
        line=dict(color="#EF4444", width=3, dash="dash"),
        marker=dict(size=8),
    ))

    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="年度",
        yaxis_title="生産台数 (台)",
        legend_title=None,
        font=dict(color="#D1D5DB"),
        hovermode="x unified",
    )
    
    fig.update_xaxes(gridcolor="#374151")
    fig.update_yaxes(gridcolor="#374151", zerolinecolor="#374151")

    return fig
