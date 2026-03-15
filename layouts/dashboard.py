"""
リアルタイムダッシュボード
台数・財務・非財務・工場CAPの4象限グラフパネル
"""

from dash import html, dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots


PT_COLORS = {
    "PET":    "#ADB8CA",
    "FFV":    "#748EB8",
    "HEV":    "#A6DC7B",
    "HEVFFV": "#64B01E",
    "PHEV":   "#A87C13",
    "BEV":    "#21A5C1",
    "FCV":    "#F5B483",
}

MODEL_COLORS = [
    "#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#8B5CF6",
    "#EC4899", "#14B8A6", "#F97316", "#6366F1", "#84CC16",
    "#06B6D4", "#E11D48", "#A855F7", "#22D3EE", "#FB923C",
    "#4ADE80",
]


def create_volume_chart(vol_by_model):
    """年度×モデル別 積み上げ棒グラフ"""
    fig = go.Figure()

    if vol_by_model.empty:
        return fig

    models = sorted(vol_by_model["model"].unique())
    years = sorted(vol_by_model["year"].unique())

    for i, model in enumerate(models):
        model_data = vol_by_model[vol_by_model["model"] == model]
        color = MODEL_COLORS[i % len(MODEL_COLORS)]

        fig.add_trace(go.Bar(
            x=model_data["year"],
            y=model_data["volume"],
            name=model,
            marker=dict(color=color, opacity=0.85),
            hovertemplate=f"<b>{model}</b><br>年度: %{{x}}<br>台数: %{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.5)",
        font=dict(family="Inter, sans-serif", color="#E5E7EB"),
        title=dict(text="📦 年度別販売台数（モデル別）", font=dict(size=16, color="#F9FAFB")),
        xaxis=dict(title="年度", dtick=1, gridcolor="rgba(75,85,99,0.3)"),
        yaxis=dict(title="台数", gridcolor="rgba(75,85,99,0.3)",
                   tickformat=","),
        legend=dict(font=dict(size=10), orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center"),
        margin=dict(l=60, r=20, t=80, b=40),
        height=380,
    )
    return fig


def create_pt_ratio_chart(pt_ratio_df):
    """年度別PT比率 積み上げエリアチャート"""
    fig = go.Figure()

    if pt_ratio_df.empty:
        return fig

    for pt in ["PET", "FFV", "HEV", "HEVFFV", "PHEV", "BEV", "FCV"]:
        pt_data = pt_ratio_df[pt_ratio_df["powertrain"] == pt]
        if not pt_data.empty:
            fig.add_trace(go.Scatter(
                x=pt_data["year"],
                y=pt_data["ratio"],
                name=pt,
                mode="lines",
                stackgroup="one",
                line=dict(width=0.5, color=PT_COLORS[pt]),
                fillcolor=PT_COLORS[pt],
                hovertemplate=f"<b>{pt}</b><br>年度: %{{x}}<br>比率: %{{y:.1f}}%<extra></extra>",
            ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.5)",
        font=dict(family="Inter, sans-serif", color="#E5E7EB"),
        title=dict(text="⚡ パワートレイン構成比推移", font=dict(size=16, color="#F9FAFB")),
        xaxis=dict(title="年度", dtick=1, gridcolor="rgba(75,85,99,0.3)"),
        yaxis=dict(title="比率 (%)", range=[0, 100], gridcolor="rgba(75,85,99,0.3)"),
        legend=dict(font=dict(size=11)),
        margin=dict(l=60, r=20, t=60, b=40),
        height=380,
    )
    return fig


def create_financial_chart(financial_df):
    """財務指標チャート（売上高・営業利益）"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if financial_df.empty:
        return fig

    fig.add_trace(
        go.Bar(
            x=financial_df["year"],
            y=financial_df["revenue"],
            name="売上高",
            marker=dict(color="#3B82F6", opacity=0.7),
            hovertemplate="売上高: %{y:,.0f} 億円<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=financial_df["year"],
            y=financial_df["profit"],
            name="営業利益",
            mode="lines+markers",
            line=dict(color="#F59E0B", width=3),
            marker=dict(size=8, symbol="diamond"),
            hovertemplate="営業利益: %{y:,.0f} 億円<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.5)",
        font=dict(family="Inter, sans-serif", color="#E5E7EB"),
        title=dict(text="💰 財務目標推移", font=dict(size=16, color="#F9FAFB")),
        xaxis=dict(title="年度", dtick=1, gridcolor="rgba(75,85,99,0.3)"),
        legend=dict(font=dict(size=11), orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center"),
        margin=dict(l=60, r=60, t=80, b=40),
        height=380,
    )
    fig.update_yaxes(title_text="売上高 (億円)", gridcolor="rgba(75,85,99,0.3)", secondary_y=False,
                     tickformat=",")
    fig.update_yaxes(title_text="営業利益 (億円)", gridcolor="rgba(75,85,99,0.3)", secondary_y=True,
                     tickformat=",")

    return fig


def create_non_financial_chart(nf_df):
    """非財務指標チャート（LCA, CAFE, 事故死亡率、リサイクル率）"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("🌿 LCA CO2排出量 (g/km)", "⛽ CAFE 平均燃費 (km/L)",
                        "🛡️ 事故死亡率指数", "♻️ リサイクル率 (%)"),
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
    )

    if nf_df.empty:
        return fig

    # LCA CO2 Breakdown (Stacked Bar)
    co2_colors = {
        "co2_use": "#10B981",            # Green
        "co2_disposal": "#9CA3AF",      # Gray
        "co2_production_in": "#3B82F6", # Blue
        "co2_production_out": "#1E40AF",# Dark Blue
        "co2_logistics": "#F59E0B",     # Orange
        "co2_energy": "#8B5CF6"         # Purple
    }
    co2_labels = {
        "co2_use": "製品使用",
        "co2_disposal": "廃棄",
        "co2_production_in": "生産(内)",
        "co2_production_out": "生産(外)",
        "co2_logistics": "輸送",
        "co2_energy": "エネルギー製造"
    }

    for col, color in co2_colors.items():
        fig.add_trace(go.Bar(
            x=nf_df["year"], y=nf_df[col],
            name=co2_labels[col],
            marker_color=color,
            hovertemplate="%{y:.1f} g/km<extra></extra>",
            showlegend=True, # Show legend only for CO2 breakdown to keep it clean
        ), row=1, col=1)

    # CAFE
    fig.add_trace(go.Scatter(
        x=nf_df["year"], y=nf_df["cafe_fuel_eff"],
        mode="lines+markers",
        line=dict(color="#3B82F6", width=2.5),
        marker=dict(size=6),
        name="CAFE",
        showlegend=False,
        hovertemplate="%{y:.1f} km/L<extra></extra>",
    ), row=1, col=2)

    # 事故死亡率
    fig.add_trace(go.Scatter(
        x=nf_df["year"], y=nf_df["accident_rate_index"],
        mode="lines+markers",
        line=dict(color="#F59E0B", width=2.5),
        marker=dict(size=6),
        name="事故死亡率",
        showlegend=False,
        hovertemplate="%{y:.3f}<extra></extra>",
    ), row=2, col=1)

    # リサイクル率
    fig.add_trace(go.Scatter(
        x=nf_df["year"], y=nf_df["recycle_rate"],
        mode="lines+markers",
        line=dict(color="#EC4899", width=2.5),
        marker=dict(size=6),
        name="リサイクル率",
        showlegend=False,
        hovertemplate="%{y:.1f}%<extra></extra>",
    ), row=2, col=2)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.5)",
        font=dict(family="Inter, sans-serif", color="#E5E7EB", size=11),
        title=dict(text="🌍 非財務目標推移", font=dict(size=16, color="#F9FAFB")),
        margin=dict(l=50, r=20, t=80, b=40),
        height=600, # Increased height for better visibility of 2x2 with legend
        barmode="stack",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        )
    )

    # 各サブプロットのグリッド設定
    for i in range(1, 3):
        for j in range(1, 3):
            fig.update_xaxes(dtick=2, gridcolor="rgba(75,85,99,0.3)", row=i, col=j)
            fig.update_yaxes(gridcolor="rgba(75,85,99,0.3)", row=i, col=j)

    return fig


def create_plant_cap_chart(plant_util_df):
    """工場稼働率チャート"""
    fig = go.Figure()

    if plant_util_df.empty:
        return fig

    plant_util_df = plant_util_df.sort_values("utilization", ascending=True)

    colors = [
        "#EF4444" if u > 100 else "#F59E0B" if u > 85 else "#10B981"
        for u in plant_util_df["utilization"]
    ]

    fig.add_trace(go.Bar(
        y=plant_util_df["plant"],
        x=plant_util_df["utilization"],
        orientation="h",
        marker=dict(color=colors, opacity=0.85,
                    line=dict(color="rgba(255,255,255,0.2)", width=1)),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "稼働率: %{x:.1f}%<br>"
            "<extra></extra>"
        ),
    ))

    # 100%ライン
    fig.add_vline(x=100, line=dict(color="#EF4444", width=2, dash="dash"),
                  annotation_text="100%", annotation_position="top right")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.5)",
        font=dict(family="Inter, sans-serif", color="#E5E7EB"),
        title=dict(text="🏭 工場稼働率", font=dict(size=16, color="#F9FAFB")),
        xaxis=dict(title="稼働率 (%)", gridcolor="rgba(75,85,99,0.3)", range=[0, max(130, plant_util_df["utilization"].max() + 10)]),
        yaxis=dict(title=""),
        margin=dict(l=140, r=20, t=60, b=40),
        height=380,
        showlegend=False,
    )
    return fig


    return fig


def create_rd_chart(rd_df):
    """開発工数・費用チャート"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if rd_df.empty:
        return fig

    # 開発工数 (棒グラフ)
    fig.add_trace(
        go.Bar(
            x=rd_df["year"],
            y=rd_df["man_months"],
            name="開発工数 (人月)",
            marker=dict(color="#A855F7", opacity=0.7),
            hovertemplate="開発工数: %{y:,.0f} 人月<extra></extra>",
        ),
        secondary_y=False,
    )

    # 開発費 (折れ線グラフ)
    fig.add_trace(
        go.Scatter(
            x=rd_df["year"],
            y=rd_df["cost_oku"],
            name="開発費 (億円)",
            mode="lines+markers",
            line=dict(color="#22D3EE", width=3),
            marker=dict(size=8, symbol="circle"),
            hovertemplate="開発費: %{y:,.1f} 億円<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.5)",
        font=dict(family="Inter, sans-serif", color="#E5E7EB"),
        title=dict(text="🧪 開発工数・開発費推移", font=dict(size=16, color="#F9FAFB")),
        xaxis=dict(title="年度", dtick=1, gridcolor="rgba(75,85,99,0.3)"),
        legend=dict(font=dict(size=11), orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center"),
        margin=dict(l=60, r=60, t=80, b=40),
        height=380,
    )
    fig.update_yaxes(title_text="開発工数 (人月)", gridcolor="rgba(75,85,99,0.3)", secondary_y=False,
                     tickformat=",")
    fig.update_yaxes(title_text="開発費 (億円)", gridcolor="rgba(75,85,99,0.3)", secondary_y=True,
                     tickformat=",")

    return fig


def create_dashboard_layout():
    """ダッシュボードタブのレイアウト"""
    return html.Div([
        html.Div([
            html.H3("📈 リアルタイムダッシュボード", className="section-title"),
            html.P("台数・財務・非財務指標・工場CAP・開発状況がシミュレーション変更に連動してリアルタイム更新",
                    className="section-desc"),
        ], className="section-header"),

        # サマリーKPIカード
        html.Div(id="kpi-cards", className="kpi-grid"),

        # フィルターエリア
        html.Div([
            html.Div([
                html.Label("工場フィルター", className="filter-label"),
                dcc.Dropdown(
                    id="dashboard-factory-filter",
                    options=[{"label": "全工場", "value": "ALL"}],
                    value="ALL",
                    className="custom-dropdown",
                    clearable=False,
                ),
            ], className="filter-item", style={"width": "300px"}),
        ], className="filter-row", style={"marginBottom": "20px"}),

        # グラフグリッド (2x2)
        html.Div([
            html.Div([
                dcc.Graph(id="volume-chart", className="chart-card"),
            ], className="grid-item"),
            html.Div([
                dcc.Graph(id="pt-ratio-chart", className="chart-card"),
            ], className="grid-item"),
        ], className="chart-grid"),

        html.Div([
            html.Div([
                dcc.Graph(id="financial-chart", className="chart-card"),
            ], className="grid-item"),
            html.Div([
                dcc.Graph(id="rd-chart", className="chart-card"),
            ], className="grid-item"),
        ], className="chart-grid"),

        html.Div([
            html.Div([
                dcc.Graph(id="non-financial-chart", className="chart-card"),
            ], className="grid-item", style={"flex": 1}),
        ], className="chart-grid"),

    ], className="tab-content")
