"""
Dash コールバック定義
テーブル編集・モデル追加/削除 → シミュレーション再計算 → グラフ更新
"""

from dash import Input, Output, State, callback, no_update, ctx, html, dcc
import pandas as pd
import io
import base64
import json

import uuid

from engine.simulator import SimulationEngine
from data.sample_data import generate_sample_data, generate_financial_master, generate_non_financial_master, generate_factory_master, generate_development_master, PLANTS, REGIONS
from layouts.timeline import create_timeline_chart
from layouts.dashboard import (
    create_volume_chart,
    create_pt_ratio_chart,
    create_financial_chart,
    create_non_financial_chart,
    create_plant_cap_chart,
    create_rd_chart,
)
from layouts.factory_charts import create_factory_stacked_bar
from dash import dcc


def register_callbacks(app):
    """全コールバックを登録"""

    # ==============================================================
    # ストアの初期化
    # ==============================================================
    @app.callback(
        [
            Output("sim-data-store", "data"),
            Output("financial-data-store", "data"),
            Output("non-financial-data-store", "data"),
            Output("factory-data-store", "data"),
            Output("development-data-store", "data"),
        ],
        Input("app-init-trigger", "children"),
    )
    def init_data(_):
        df = generate_sample_data()
        fin_df = generate_financial_master()
        non_fin_df = generate_non_financial_master()
        factory_df = generate_factory_master()
        dev_df = generate_development_master()
        
        return (
            df.to_json(date_format="iso", orient="split"), 
            fin_df.to_json(date_format="iso", orient="split"),
            non_fin_df.to_json(date_format="iso", orient="split"),
            factory_df.to_json(date_format="iso", orient="split"),
            dev_df.to_json(date_format="iso", orient="split")
        )

    # ==============================================================
    # フィルタードロップダウンのオプション更新
    # ==============================================================
    @app.callback(
        [
            Output("editor-model-filter", "options"),
            Output("editor-region-filter", "options"),
            Output("editor-year-filter", "options"),
            Output("timeline-region-filter", "options"),
            Output("delete-model-dropdown", "options"),
            Output("add-model-plant", "options"),
            Output("add-model-region", "options"),
            Output("dashboard-factory-filter", "options"),
        ],
        Input("sim-data-store", "data"),
    )
    def update_filter_options(data_json):
        if data_json is None:
            return [[] for _ in range(8)]

        df = pd.read_json(io.StringIO(data_json), orient="split")

        models = sorted(df["model"].unique())
        regions = sorted(df["region"].unique())
        years = sorted(df["year"].unique())

        model_opts = [{"label": "全モデル", "value": "ALL"}] + \
                     [{"label": m, "value": m} for m in models]
        region_opts = [{"label": "全地域", "value": "ALL"}] + \
                      [{"label": r, "value": r} for r in regions]
        year_opts = [{"label": "全年度", "value": "ALL"}] + \
                    [{"label": str(y), "value": y} for y in years]
        timeline_region_opts = [{"label": "全地域", "value": "ALL"}] + \
                               [{"label": r, "value": r} for r in regions]
        delete_opts = [{"label": m, "value": m} for m in models]

        plant_opts = [{"label": p, "value": p} for p in PLANTS.keys()]
        add_region_opts = [{"label": r, "value": r} for r in REGIONS]
        dash_factory_opts = [{"label": "全工場", "value": "ALL"}] + \
                             [{"label": p, "value": p} for p in sorted(PLANTS.keys())]

        return (model_opts, region_opts, year_opts,
                timeline_region_opts, delete_opts,
                plant_opts, add_region_opts, dash_factory_opts)

    # ==============================================================
    # テーブルデータの表示（フィルタリング）
    # ==============================================================
    @app.callback(
        Output("volume-table", "data"),
        [
            Input("sim-data-store", "data"),
            Input("editor-model-filter", "value"),
            Input("editor-region-filter", "value"),
            Input("editor-year-filter", "value"),
            Input("editor-pt-filter", "value"),
        ],
    )
    def update_table(data_json, model_f, region_f, year_f, pt_f):
        if data_json is None:
            return []

        df = pd.read_json(io.StringIO(data_json), orient="split")

        if model_f and model_f != "ALL":
            df = df[df["model"] == model_f]
        if region_f and region_f != "ALL":
            df = df[df["region"] == region_f]
        if year_f and year_f != "ALL":
            df = df[df["year"] == int(year_f)]
        if pt_f and pt_f != "ALL":
            df = df[df["powertrain"] == pt_f]

        df = df.sort_values(["model", "region", "year"]).reset_index(drop=True)
        return df.to_dict("records")

    # ==============================================================
    # テーブル編集 → データストア更新
    # ==============================================================
    @app.callback(
        Output("sim-data-store", "data", allow_duplicate=True),
        Input("volume-table", "data_timestamp"),
        State("volume-table", "data"),
        State("sim-data-store", "data"),
        prevent_initial_call=True,
    )
    def on_table_edit(timestamp, table_data, current_json):
        if timestamp is None or table_data is None or current_json is None:
            return no_update

        current_df = pd.read_json(io.StringIO(current_json), orient="split")
        edited_df = pd.DataFrame(table_data)

        # テーブルに表示されている行を更新
        for _, row in edited_df.iterrows():
            if "id" not in row:
                continue
            mask = current_df["id"] == row["id"]
            if mask.any():
                current_df.loc[mask, "model"] = row["model"]
                current_df.loc[mask, "region"] = row["region"]
                current_df.loc[mask, "powertrain"] = row["powertrain"]
                current_df.loc[mask, "drive"] = row["drive"]
                current_df.loc[mask, "plant"] = row["plant"]
                current_df.loc[mask, "year"] = int(row["year"])
                current_df.loc[mask, "volume"] = int(row["volume"])

        return current_df.to_json(date_format="iso", orient="split")

    # ==============================================================
    # 財務テーブルの表示と編集
    # ==============================================================
    @app.callback(
        Output("financial-table", "data"),
        Input("financial-data-store", "data"),
    )
    def update_financial_table(fin_data_json):
        if fin_data_json is None:
            return []
        fin_df = pd.read_json(io.StringIO(fin_data_json), orient="split")
        return fin_df.to_dict("records")

    @app.callback(
        Output("financial-data-store", "data", allow_duplicate=True),
        Input("financial-table", "data_timestamp"),
        State("financial-table", "data"),
        State("financial-data-store", "data"),
        prevent_initial_call=True,
    )
    def on_financial_table_edit(timestamp, table_data, current_json):
        if timestamp is None or table_data is None or current_json is None:
            return no_update

        current_df = pd.read_json(io.StringIO(current_json), orient="split")
        edited_df = pd.DataFrame(table_data)

        for _, row in edited_df.iterrows():
            if "id" not in row:
                continue
            mask = current_df["id"] == row["id"]
            if mask.any():
                current_df.loc[mask, "price"] = float(row["price"])
                current_df.loc[mask, "fixed_cost"] = float(row["fixed_cost"])
                current_df.loc[mask, "var_cost"] = float(row["var_cost"])

        return current_df.to_json(date_format="iso", orient="split")

    # ==============================================================
    # 非財務テーブルの表示と編集
    # ==============================================================
    @app.callback(
        Output("non-financial-table", "data"),
        Input("non-financial-data-store", "data"),
    )
    def update_non_financial_table(non_fin_data_json):
        if non_fin_data_json is None:
            return []
        non_fin_df = pd.read_json(io.StringIO(non_fin_data_json), orient="split")
        return non_fin_df.to_dict("records")

    @app.callback(
        Output("non-financial-data-store", "data", allow_duplicate=True),
        Input("non-financial-table", "data_timestamp"),
        State("non-financial-table", "data"),
        State("non-financial-data-store", "data"),
        prevent_initial_call=True,
    )
    def on_non_financial_table_edit(timestamp, table_data, current_json):
        if timestamp is None or table_data is None or current_json is None:
            return no_update

        current_df = pd.read_json(io.StringIO(current_json), orient="split")
        edited_df = pd.DataFrame(table_data)

        for _, row in edited_df.iterrows():
            if "id" not in row:
                continue
            mask = current_df["id"] == row["id"]
            if mask.any():
                current_df.loc[mask, "co2"] = float(row["co2"])
                current_df.loc[mask, "fuel_eff"] = float(row["fuel_eff"])
                current_df.loc[mask, "adas"] = str(row["adas"])

        return current_df.to_json(date_format="iso", orient="split")

    # ==============================================================
    # 工場テーブルの表示と編集
    # ==============================================================
    @app.callback(
        [
            Output("factory-matrix-table", "data"),
            Output("factory-matrix-table", "columns"),
        ],
        [
            Input("factory-data-store", "data"),
            Input("sim-data-store", "data"),
        ],
    )
    def update_factory_matrix(factory_json, sim_json):
        if factory_json is None or sim_json is None:
            return [], []
        
        factory_df = pd.read_json(io.StringIO(factory_json), orient="split")
        sim_df = pd.read_json(io.StringIO(sim_json), orient="split")
        
        # 1. 実績(Vol)を年度・工場別で集計
        vol_df = sim_df.groupby(["year", "plant"])["volume"].sum().reset_index()
        vol_df.columns = ["year", "plant", "vol"]
        
        # 2. キャパシティ(Cap)とマージ
        merged_df = factory_df.merge(vol_df, on=["year", "plant"], how="left").fillna(0)
        
        # 3. カラム構成の定義
        cols = [
            {"name": ["基本情報", "工場名"], "id": "plant", "editable": False},
            {"name": ["基本情報", "地域"], "id": "region", "editable": False},
        ]
        
        years = sorted(factory_df["year"].unique())
        for y in years:
            cols.append({"name": [str(y), "実績(台)"], "id": f"{y}_vol", "editable": False, "type": "numeric"})
            cols.append({"name": [str(y), "能力(台)"], "id": f"{y}_cap", "editable": True, "type": "numeric"})
            cols.append({"name": [str(y), "稼働率(%)"], "id": f"{y}_util", "editable": False, "type": "numeric"})
            
        # 4. 横持ちデータ(flat_data)の作成
        # plant別・year別のマトリクスを作るため一度Pivot
        pivot_df = merged_df.pivot(index=["plant", "region"], columns="year", values=["vol", "capacity"])
        
        flat_data = []
        for idx, row in pivot_df.iterrows():
            item = {"plant": idx[0], "region": idx[1]}
            for y in years:
                v = int(row[("vol", y)])
                c = int(row[("capacity", y)])
                u = round(v / c * 100, 1) if c > 0 else 0
                
                item[f"{y}_vol"] = v
                item[f"{y}_cap"] = c
                item[f"{y}_util"] = u
            flat_data.append(item)
            
        return flat_data, cols

    @app.callback(
        Output("factory-data-store", "data", allow_duplicate=True),
        Input("factory-matrix-table", "data_timestamp"),
        State("factory-matrix-table", "data"),
        State("factory-data-store", "data"),
        prevent_initial_call=True,
    )
    def on_factory_matrix_edit(timestamp, table_data, current_json):
        if timestamp is None or table_data is None or current_json is None:
            return no_update

        edited_df = pd.DataFrame(table_data)
        
        # 能力(Cap)列のみを抽出して Melt
        # カラム名が '2025_cap' のような形式になっている
        cap_cols = [c for c in edited_df.columns if "_cap" in c]
        
        melted_df = edited_df.melt(
            id_vars=["plant", "region"], 
            value_vars=cap_cols,
            var_name="year_raw", 
            value_name="capacity"
        )
        # '2025_cap' -> 2025 (int)
        melted_df["year"] = melted_df["year_raw"].apply(lambda x: int(x.split("_")[0]))
        melted_df = melted_df.drop(columns=["year_raw"])
        
        # ID 生成 (plant + year)
        melted_df["id"] = melted_df.apply(lambda x: f"{x['plant']}_{x['year']}", axis=1)
        
        return melted_df.to_json(date_format="iso", orient="split")

    # ==============================================================
    # モデル追加
    # ==============================================================
    @app.callback(
        [
            Output("sim-data-store", "data", allow_duplicate=True),
            Output("financial-data-store", "data", allow_duplicate=True),
            Output("non-financial-data-store", "data", allow_duplicate=True),
            Output("editor-notification", "children", allow_duplicate=True),
        ],
        Input("add-model-btn", "n_clicks"),
        [
            State("add-model-name", "value"),
            State("add-model-pt", "value"),
            State("add-model-drive", "value"),
            State("add-model-plant", "value"),
            State("add-model-region", "value"),
            State("add-model-volume", "value"),
            State("add-model-start", "value"),
            State("add-model-end", "value"),
            State("sim-data-store", "data"),
            State("financial-data-store", "data"),
            State("non-financial-data-store", "data"),
            State("factory-data-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def add_model(n_clicks, name, pt, drive, plant, regions, volume, start, end, data_json, fin_data_json, non_fin_data_json, factory_json):
        if not n_clicks or not name or not plant or not regions:
            return no_update, no_update, no_update, no_update

        df = pd.read_json(io.StringIO(data_json), orient="split")
        fin_df = pd.read_json(io.StringIO(fin_data_json), orient="split")
        non_fin_df = pd.read_json(io.StringIO(non_fin_data_json), orient="split")
        factory_df = pd.read_json(io.StringIO(factory_json), orient="split") if factory_json else None

        # 財務マスターにこのモデルがまだなければ追加する
        if name not in fin_df["model"].values:
            new_fin_row = {
                "id": str(uuid.uuid4()),
                "model": name,
                "price": 300,  # デフォルト値単価（万円）
                "fixed_cost": 500, # デフォルト固定費（億円/年）
                "var_cost": 200,   # デフォルト変動費（万円/台）
            }
            fin_df = pd.concat([fin_df, pd.DataFrame([new_fin_row])], ignore_index=True)

        # 非財務マスターにこの(モデル×PT)がまだなければ追加する
        # 同じモデル名でもPTが違う行を作り得るため複合チェック
        if not ((non_fin_df["model"] == name) & (non_fin_df["powertrain"] == pt)).any():
            # PT別のデフォルトLCA CO2 (data/sample_data.pyのロジックと合わせる)
            lca_defaults = {
                "PET":    {"use": 140, "disp": 5, "prod_in": 15, "prod_out": 25, "logi": 5, "ener": 10},
                "HEV":    {"use": 80,  "disp": 5, "prod_in": 18, "prod_out": 30, "logi": 5, "ener": 10},
                "PHEV":   {"use": 40,  "disp": 6, "prod_in": 20, "prod_out": 45, "logi": 5, "ener": 20},
                "BEV":    {"use": 0,   "disp": 8, "prod_in": 25, "prod_out": 70, "logi": 5, "ener": 40},
                "FCV":    {"use": 0,   "disp": 7, "prod_in": 25, "prod_out": 60, "logi": 5, "ener": 30},
                "FFV":    {"use": 120, "disp": 5, "prod_in": 15, "prod_out": 25, "logi": 5, "ener": 15},
                "HEVFFV": {"use": 75,  "disp": 5, "prod_in": 18, "prod_out": 30, "logi": 5, "ener": 12},
            }
            defaults = lca_defaults.get(pt, lca_defaults["PET"])

            new_non_fin_row = {
                "id": str(uuid.uuid4()),
                "model": name,
                "powertrain": pt,
                "co2_use": defaults["use"],
                "co2_disposal": defaults["disp"],
                "co2_production_in": defaults["prod_in"],
                "co2_production_out": defaults["prod_out"],
                "co2_logistics": defaults["logi"],
                "co2_energy": defaults["ener"],
                "fuel_eff": 20,
                "adas": "P-ADAS Gen1",
            }
            non_fin_df = pd.concat([non_fin_df, pd.DataFrame([new_non_fin_row])], ignore_index=True)

        engine = SimulationEngine(df, financial_df=fin_df, 
                                  non_financial_df=non_fin_df,
                                  factory_df=factory_df)
        
        for region in regions:
            engine.add_model(name, pt, drive, plant, region, int(start), int(end), int(volume))
            
        new_df = engine.get_data()

        notification = html.Div([
            html.Span("✅ ", style={"fontSize": "18px"}),
            html.Span(f"モデル「{name}」を以下の地域に追加しました: {', '.join(regions)} ({start}-{end})",
                       style={"color": "#10B981"}),
        ], className="notification-success")

        return (
            new_df.to_json(date_format="iso", orient="split"), 
            fin_df.to_json(date_format="iso", orient="split"), 
            non_fin_df.to_json(date_format="iso", orient="split"),
            notification
        )

    # ==============================================================
    # モデル削除
    # ==============================================================
    @app.callback(
        [
            Output("sim-data-store", "data", allow_duplicate=True),
            Output("editor-notification", "children", allow_duplicate=True),
        ],
        Input("delete-model-btn", "n_clicks"),
        [
            State("delete-model-dropdown", "value"),
            State("sim-data-store", "data"),
            State("financial-data-store", "data"),
            State("non-financial-data-store", "data"),
            State("factory-data-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def delete_model(n_clicks, model_name, data_json, fin_data_json, non_fin_data_json, factory_json):
        if not n_clicks or not model_name:
            return no_update, no_update

        df = pd.read_json(io.StringIO(data_json), orient="split")
        fin_df = pd.read_json(io.StringIO(fin_data_json), orient="split")
        non_fin_df = pd.read_json(io.StringIO(non_fin_data_json), orient="split")
        factory_df = pd.read_json(io.StringIO(factory_json), orient="split") if factory_json else None

        engine = SimulationEngine(df, financial_df=fin_df, 
                                  non_financial_df=non_fin_df,
                                  factory_df=factory_df)
        engine.delete_model(model_name)
        new_df = engine.get_data()

        notification = html.Div([
            html.Span("🗑️ ", style={"fontSize": "18px"}),
            html.Span(f"モデル「{model_name}」を削除しました",
                       style={"color": "#EF4444"}),
        ], className="notification-danger")

        return new_df.to_json(date_format="iso", orient="split"), notification

    # ==============================================================
    # タイムラインチャート更新
    # ==============================================================
    @app.callback(
        Output("timeline-chart", "figure"),
        [
            Input("sim-data-store", "data"),
            Input("factory-data-store", "data"),
            Input("timeline-region-filter", "value"),
            Input("timeline-pt-filter", "value"),
        ],
    )
    def update_timeline(data_json, factory_json, region_f, pt_f):
        if data_json is None:
            return {}

        df = pd.read_json(io.StringIO(data_json), orient="split")
        factory_df = pd.read_json(io.StringIO(factory_json), orient="split") if factory_json else None
        engine = SimulationEngine(df, factory_df=factory_df)
        timeline = engine.get_timeline_data()

        if region_f and region_f != "ALL":
            timeline = timeline[timeline["region"] == region_f]
        if pt_f and pt_f != "ALL":
            timeline = timeline[timeline["powertrain"] == pt_f]

        return create_timeline_chart(timeline)

    # ==============================================================
    # ダッシュボード グラフ更新
    # ==============================================================
    @app.callback(
        [
            Output("kpi-cards", "children"),
            Output("volume-chart", "figure"),
            Output("pt-ratio-chart", "figure"),
            Output("financial-chart", "figure"),
            Output("non-financial-chart", "figure"),
            Output("rd-chart", "figure"),
        ],
        [
            Input("sim-data-store", "data"),
            Input("financial-data-store", "data"),
            Input("non-financial-data-store", "data"),
            Input("factory-data-store", "data"),
            Input("development-data-store", "data"),
            Input("dashboard-factory-filter", "value"),
        ]
    )
    def update_dashboard(data_json, fin_data_json, non_fin_data_json, factory_json, dev_json, factory_f):
        if data_json is None or fin_data_json is None or non_fin_data_json is None or factory_json is None or dev_json is None:
            return [], {}, {}, {}, {}, {}

        df = pd.read_json(io.StringIO(data_json), orient="split")
        fin_df = pd.read_json(io.StringIO(fin_data_json), orient="split")
        non_fin_df = pd.read_json(io.StringIO(non_fin_data_json), orient="split")
        factory_df = pd.read_json(io.StringIO(factory_json), orient="split")
        
        # 工場フィルターの適用
        if factory_f and factory_f != "ALL":
            df = df[df["plant"] == factory_f]
        
        engine = SimulationEngine(df, financial_df=fin_df, 
                                  non_financial_df=non_fin_df, 
                                  factory_df=factory_df)

        vol_by_model = engine.calc_volume_by_model()
        pt_ratio = engine.calc_pt_ratio()
        financial = engine.calc_financial()
        non_financial = engine.calc_non_financial()
        
        # 開発データの設定
        dev_df = pd.read_json(io.StringIO(dev_json), orient="split")
        engine.set_development_data(dev_df)
        rd_summary = engine.calc_development_effort()

        # KPIカード
        total_vol = df["volume"].sum()
        bev_ratio = df[df["powertrain"] == "BEV"]["volume"].sum() / total_vol * 100 if total_vol > 0 else 0
        latest_year = df["year"].max()
        latest_financial = financial[financial["year"] == latest_year]
        revenue_latest = latest_financial["revenue"].values[0] if len(latest_financial) > 0 else 0
        profit_latest = latest_financial["profit"].values[0] if len(latest_financial) > 0 else 0
        model_count = df["model"].nunique()

        kpi_cards = [
            _create_kpi_card("累計販売台数", f"{total_vol:,.0f} 台", "📦", "#3B82F6"),
            _create_kpi_card("BEV比率", f"{bev_ratio:.1f}%", "⚡", "#8B5CF6"),
            _create_kpi_card(f"売上高 ({latest_year})", f"{revenue_latest:,.0f} 億円", "💰", "#10B981"),
            _create_kpi_card(f"営業利益 ({latest_year})", f"{profit_latest:,.0f} 億円", "📊", "#F59E0B"),
            _create_kpi_card("モデル数", f"{model_count}", "🚗", "#EC4899"),
        ]

        return (
            kpi_cards,
            create_volume_chart(vol_by_model),
            create_pt_ratio_chart(pt_ratio),
            create_financial_chart(financial),
            create_non_financial_chart(non_financial),
            create_rd_chart(rd_summary),
        )

    # ==============================================================
    # Excel エクスポート
    # ==============================================================
    @app.callback(
        Output("export-excel-download", "data"),
        Input("export-excel-btn", "n_clicks"),
        State("sim-data-store", "data"),
        prevent_initial_call=True,
    )
    def export_excel(n_clicks, data_json):
        if not n_clicks or not data_json:
            return no_update
            
        df = pd.read_json(io.StringIO(data_json), orient="split")
        # 並び順を整理
        df = df[["model", "region", "powertrain", "drive", "plant", "year", "volume"]]
        
        return dcc.send_data_frame(df.to_excel, "honda_sim_data.xlsx", index=False)

    # ==============================================================
    # Excel インポート
    # ==============================================================
    @app.callback(
        [
            Output("sim-data-store", "data", allow_duplicate=True),
            Output("editor-notification", "children", allow_duplicate=True),
        ],
        Input("import-excel-upload", "contents"),
        State("import-excel-upload", "filename"),
        prevent_initial_call=True,
    )
    def import_excel(contents, filename):
        if contents is None:
            return no_update, no_update
            
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return no_update, html.Div("❌ 対応していないファイル形式です", style={"color": "#EF4444"})
                
            # 必須カラムのチェック
            required = ["model", "region", "powertrain", "drive", "plant", "year", "volume"]
            if not all(col in df.columns for col in required):
                return no_update, html.Div(f"❌ 必須カラムが不足しています: {required}", style={"color": "#EF4444"})
            
            # IDを付与
            if "id" not in df.columns:
                df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
                
            new_data_json = df.to_json(date_format="iso", orient="split")
            notification = html.Div([
                html.Span("📥 ", style={"fontSize": "18px"}),
                html.Span(f"ファイル「{filename}」から {len(df)} 件のデータをインポートしました",
                           style={"color": "#10B981"}),
            ], className="notification-success")
            
            return new_data_json, notification
            
        except Exception as e:
            return no_update, html.Div(f"❌ インポート中にエラーが発生しました: {str(e)}", style={"color": "#EF4444"})

    # ==============================================================
    # 工場別生産可視化グラフの動的生成
    # ==============================================================
    @app.callback(
        Output("factory-charts-container", "children"),
        [
            Input("sim-data-store", "data"),
            Input("factory-chart-stack-mode", "value"),
            Input("factory-data-store", "data"),
        ]
    )
    def update_factory_charts(data_json, stack_mode, factory_json):
        if data_json is None or factory_json is None:
            return []

        df = pd.read_json(io.StringIO(data_json), orient="split")
        factory_df = pd.read_json(io.StringIO(factory_json), orient="split")
        engine = SimulationEngine(df, factory_df=factory_df)
        
        # 存在する工場リスト（ソート）
        plants = sorted(df["plant"].unique())
        
        charts = []
        for plant in plants:
            plant_data = engine.calc_factory_breakdown(plant)
            # 工場ごとの全年度キャパシティを抽出して辞書化
            plant_caps = factory_df[factory_df["plant"] == plant]
            cap_dict = dict(zip(plant_caps["year"], plant_caps["capacity"]))
            
            fig = create_factory_stacked_bar(plant_data, plant, stack_mode, cap_dict)
            
            charts.append(html.Div([
                dcc.Graph(figure=fig, config={"displayModeBar": False})
            ], className="chart-card"))
            
        return charts

    # ==============================================================
    # 開発設定 (R&D)
    # ==============================================================
    @app.callback(
        Output("development-table", "data"),
        Input("development-data-store", "data"),
    )
    def update_development_table(dev_json):
        if dev_json is None:
            return []
        df = pd.read_json(io.StringIO(dev_json), orient="split")
        return df.to_dict("records")

    @app.callback(
        Output("development-data-store", "data", allow_duplicate=True),
        Input("development-table", "data"),
        prevent_initial_call=True
    )
    def on_development_table_edit(data):
        if not data:
            return no_update
        df = pd.DataFrame(data)
        return df.to_json(date_format="iso", orient="split")


def _create_kpi_card(title, value, icon, color):
    """KPIカードのHTMLを生成"""
    return html.Div([
        html.Div(icon, className="kpi-icon", style={"color": color}),
        html.Div([
            html.Div(value, className="kpi-value", style={"color": color}),
            html.Div(title, className="kpi-title"),
        ], className="kpi-text"),
    ], className="kpi-card", style={"borderColor": color})
