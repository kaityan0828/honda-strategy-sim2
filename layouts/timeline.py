"""
新幹線タイムラインビュー
横軸に年度、縦軸にモデルを配置し、販売期間を新幹線先頭車両風に表示
"""

import math
from dash import html, dcc
import plotly.graph_objects as go


PT_COLORS = {
    "PET":    "#ADB8CA",
    "FFV":    "#748EB8",
    "HEV":    "#A6DC7B",
    "HEVFFV": "#64B01E",
    "PHEV":   "#A87C13",
    "BEV":    "#21A5C1",
    "FCV":    "#F5B483",
}

# 新幹線ノーズ: 左端の上半分を60度で斜めカット
NOSE_ANGLE_DEG = 60
BAR_HALF_HEIGHT = 0.28  # 棒の半分の高さ (y軸単位)
# ノーズの長さ (x軸=年単位): 上半分の高さ h を 60度でカット
# tan(60°) ≈ 1.732 → nose = h / tan(60°)
NOSE_LENGTH = BAR_HALF_HEIGHT / math.tan(math.radians(NOSE_ANGLE_DEG))


def _hex_to_rgba(hex_color, opacity=0.85):
    """HEXカラーをrgba文字列に変換"""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{opacity})"


def create_timeline_chart(timeline_df):
    """新幹線先頭車両風タイムラインチャートを生成"""
    fig = go.Figure()

    if timeline_df.empty:
        return fig

    # モデル×地域でソート
    timeline_df = timeline_df.sort_values(
        ["powertrain", "model", "region"],
        ascending=[True, True, True]
    ).reset_index(drop=True)

    # 地域名を一定の幅に揃え、「Region | Model」の形式でラベルを生成
    # Plotlyのy軸ラベルでは、HTMLタグ（<code>等）や等幅フォント(Courier等)を使うことで
    # 疑似的に列を分けることが可能
    import unicodedata

    def get_east_asian_width_count(text):
        count = 0
        for c in text:
            if unicodedata.east_asian_width(c) in 'FWA':
                count += 2
            else:
                count += 1
        return count

    # PlotlyのラベルにHTMLを使用する場合、インラインCSSで等幅フォントと固定幅(em)を指定する
    # ことで、より正確に列を揃えるアプローチ
    def format_label(region, model):
        target_width = 16  # 全角換算での目標幅
        current_width = get_east_asian_width_count(region)
        pad_length = max(0, target_width - current_width)
        
        # 全角スペース相当の幅を持つ文字(例: \u3000)や半角スペースで精細に埋める
        # 全角1文字=半角2文字換算
        pad_str = "&nbsp;" * pad_length
        region_html = region + pad_str
        
        # Courier New などの等幅フォントを強制し、見かけ上の幅を揃える
        return f"<span style='font-family: \"Courier New\", Courier, monospace;'>{region_html} | </span>{model}"

    timeline_df["label"] = timeline_df.apply(lambda r: format_label(r["region"], r["model"]), axis=1)

    labels = timeline_df["label"].tolist()
    n = len(labels)

    # 各棒を新幹線型ポリゴンで描画
    for idx, row in timeline_df.iterrows():
        color = PT_COLORS.get(row["powertrain"], "#6B7280")
        avg_vol = row["avg_volume"]

        y_center = idx  # 数値Y位置
        h = BAR_HALF_HEIGHT  # 棒の半分の高さ
        x_start = row["start_year"] - 0.45
        x_end = row["end_year"] + 0.45
        nose = min(NOSE_LENGTH, (x_end - x_start) * 0.25)

        # 新幹線先頭車両型 (左端=先頭, 上半分だけ60度で斜めカット)
        # ※ Y軸反転のため y_center-h が視覚的に上
        #
        #       ___________________
        #      /                   |   ← 上半分: 60度で斜めカット
        #     /                    |
        #    |                     |   ← 下半分: 垂直のまま
        #    |_____________________|
        #
        poly_x = [
            x_start,                # 左中 (斜めカットの始点)
            x_start + nose,         # 左上 (ノーズ斜面の上端)
            x_end,                  # 右上
            x_end,                  # 右下
            x_start,                # 左下
            x_start,                # 閉じる → 左中に戻る
        ]
        poly_y = [
            y_center,               # 左中 (棒の中央 = 斜めカットの始点)
            y_center - h,           # 左上 (視覚的に上)
            y_center - h,           # 右上 (視覚的に上)
            y_center + h,           # 右下 (視覚的に下)
            y_center + h,           # 左下 (視覚的に下)
            y_center,               # 閉じる → 左中に戻る
        ]

        fill_color = _hex_to_rgba(color, 0.85)
        line_color = _hex_to_rgba(color, 1.0)

        fig.add_trace(go.Scatter(
            x=poly_x,
            y=poly_y,
            fill="toself",
            fillcolor=fill_color,
            line=dict(color=line_color, width=1.5),
            mode="lines",
            name=row["powertrain"],
            showlegend=False,
            hoverinfo="text",
            text=(
                f"<b>{row['model']}</b><br>"
                f"地域: {row['region']}<br>"
                f"PT: {row['powertrain']}<br>"
                f"期間: {row['start_year']} - {row['end_year']}<br>"
                f"平均台数: {avg_vol:,.0f} 台/年<br>"
                f"累計台数: {row['total_volume']:,.0f} 台"
            ),
        ))

    # レジェンド用ダミートレース
    for pt, color in PT_COLORS.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            line=dict(color=color, width=10),
            name=pt,
            showlegend=True,
            xaxis="x",
        ))

    # X軸の範囲を動的に決定 (最低でも 最小年-1 から 最大年+1)
    min_year = timeline_df["start_year"].min() - 1 if not timeline_df.empty else 2024
    max_year = timeline_df["end_year"].max() + 1 if not timeline_df.empty else 2036

    # 上部X軸を表示させるための透明なダミートレース
    fig.add_trace(go.Scatter(
        x=[min_year, max_year],
        y=[None, None],
        mode="lines",
        showlegend=False,
        hoverinfo="skip",
        xaxis="x2"
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.7)",
        font=dict(family="Inter, sans-serif", color="#E5E7EB"),
        title=dict(
            text="🚄 モデルタイムライン（新幹線ビュー）",
            font=dict(size=20, color="#F9FAFB"),
            x=0.5,
        ),
        xaxis=dict(
            title="年度",
            dtick=1,
            range=[min_year, max_year],
            gridcolor="rgba(75,85,99,0.3)",
            side="bottom"
        ),
        xaxis2=dict(
            dtick=1,
            range=[min_year, max_year],
            side="top",
            overlaying="x",
            showgrid=False,
            # 上部の余白がないと見切れるため微調整
        ),
        yaxis=dict(
            title="",
            tickvals=list(range(n)),
            ticktext=labels,
            range=[n - 0.5, -0.5],  # 反転
            gridcolor="rgba(75,85,99,0.3)",
            ticklabelposition="outside",
        ),
        height=max(500, n * 34 + 120),
        margin=dict(l=200, r=120, t=90, b=40),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.02,
            font=dict(size=13),
            bgcolor="rgba(17,24,39,0.8)",
            bordercolor="rgba(75,85,99,0.5)",
            borderwidth=1,
        ),
    )

    return fig


def create_timeline_layout():
    """タイムラインタブのレイアウト"""
    return html.Div([
        html.Div([
            html.H3("🚄 モデルライフサイクル タイムライン",
                     className="section-title"),
            html.P("各モデルの販売期間・パワートレイン・生産台数を新幹線ダイヤグラム風に可視化",
                    className="section-desc"),
        ], className="section-header"),

        html.Div([
            html.Div([
                html.Label("地域フィルター", className="filter-label"),
                dcc.Dropdown(
                    id="timeline-region-filter",
                    options=[{"label": "全地域", "value": "ALL"}],
                    value="ALL",
                    className="dropdown-dark",
                    clearable=False,
                ),
            ], className="filter-item"),
            html.Div([
                html.Label("PTフィルター", className="filter-label"),
                dcc.Dropdown(
                    id="timeline-pt-filter",
                    options=[
                        {"label": "全PT", "value": "ALL"},
                        {"label": "ICE", "value": "ICE"},
                        {"label": "HEV", "value": "HEV"},
                        {"label": "PHEV", "value": "PHEV"},
                        {"label": "BEV", "value": "BEV"},
                    ],
                    value="ALL",
                    className="dropdown-dark",
                    clearable=False,
                ),
            ], className="filter-item"),
        ], className="filter-bar"),

        dcc.Graph(id="timeline-chart", className="chart-container"),
    ], className="tab-content")
