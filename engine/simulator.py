"""
Honda 四輪事業 シミュレーションエンジン
台数変更・工場変更・モデル追加削除・時期変更を処理し、KPIを算出する
"""

import pandas as pd
import numpy as np
import uuid
from data.sample_data import get_model_master, get_plant_capacity, PLANTS


# ------------------------------------------------------------------
# モデル別の財務パラメータ（万円）
# ------------------------------------------------------------------
FINANCIAL_PARAMS = {
    "N-BOX":          {"price": 165,  "cost_ratio": 0.82},
    "Fit":            {"price": 195,  "cost_ratio": 0.80},
    "Civic":          {"price": 345,  "cost_ratio": 0.78},
    "Accord":         {"price": 450,  "cost_ratio": 0.76},
    "CR-V":           {"price": 440,  "cost_ratio": 0.77},
    "HR-V":           {"price": 300,  "cost_ratio": 0.79},
    "ZR-V":           {"price": 350,  "cost_ratio": 0.78},
    "e:NY1":          {"price": 480,  "cost_ratio": 0.85},
    "e:NP1":          {"price": 550,  "cost_ratio": 0.84},
    "Prologue":       {"price": 600,  "cost_ratio": 0.83},
    "0 Series Sedan": {"price": 700,  "cost_ratio": 0.82},
    "0 Series SUV":   {"price": 750,  "cost_ratio": 0.82},
}

# PT別のCO2排出係数 (g/km)
PT_CO2 = {
    "PET":    140,
    "FFV":    120,
    "HEV":    80,
    "HEVFFV": 75,
    "PHEV":   40,
    "BEV":    0,
    "FCV":    0,
}

# PT別の燃費 (km/L相当)
PT_FUEL_EFFICIENCY = {
    "PET":    15,
    "FFV":    13,
    "HEV":    25,
    "HEVFFV": 22,
    "PHEV":   40,
    "BEV":    999,  # 燃費基準ではBEVは特殊扱い
    "FCV":    999,  # FCVも特殊扱い
}

# 安全装備(ADAS)レベル別の事故死亡率改善係数
SAFETY_FACTOR = {
    "ADAS適用なし": 1.0, 
    "E-ADAS": 0.85, 
    "P-ADAS Gen1": 0.70, 
    "P-ADAS Gen2": 0.55, 
    "Elite": 0.40
}


class SimulationEngine:
    """シミュレーションエンジン"""

    def __init__(self, df: pd.DataFrame, financial_df: pd.DataFrame = None, 
                 non_financial_df: pd.DataFrame = None, factory_df: pd.DataFrame = None):
        self.df = df.copy()
        self.model_master = get_model_master()
        self.plant_capacity = get_plant_capacity()
        
        # 財務データが提供されていない場合はデフォルトを生成
        if financial_df is not None:
            self.financial_df = financial_df.copy()
        else:
            from data.sample_data import generate_financial_master
            self.financial_df = generate_financial_master()
            
        # 非財務データが提供されていない場合はデフォルトを生成
        if non_financial_df is not None:
            self.non_financial_df = non_financial_df.copy()
        else:
            from data.sample_data import generate_non_financial_master
            self.non_financial_df = generate_non_financial_master()

        # 工場データが提供されていない場合はデフォルトを生成
        if factory_df is not None:
            self.factory_df = factory_df.copy()
        else:
            from data.sample_data import generate_factory_master
            self.factory_df = generate_factory_master()

        # 開発データ
        from data.sample_data import generate_development_master
        self.development_df = generate_development_master()

    def get_data(self) -> pd.DataFrame:
        return self.df.copy()

    def set_data(self, df: pd.DataFrame):
        self.df = df.copy()

    def set_development_data(self, df: pd.DataFrame):
        self.development_df = df.copy()

    # ----------------------------------------------------------
    # 操作メソッド
    # ----------------------------------------------------------

    def update_volume(self, model: str, region: str, year: int, new_volume: int):
        """特定のモデル×地域×年の台数を更新"""
        mask = (
            (self.df["model"] == model) &
            (self.df["region"] == region) &
            (self.df["year"] == year)
        )
        self.df.loc[mask, "volume"] = new_volume

    def change_plant(self, model: str, region: str, old_plant: str, new_plant: str):
        """モデルの生産工場を変更"""
        mask = (
            (self.df["model"] == model) &
            (self.df["region"] == region) &
            (self.df["plant"] == old_plant)
        )
        self.df.loc[mask, "plant"] = new_plant

    def add_model(self, model: str, powertrain: str, drive: str,
                  plant: str, region: str, start_year: int, end_year: int,
                  volume: int):
        """新モデルを追加"""
        new_rows = []
        for year in range(start_year, end_year + 1):
            new_rows.append({
                "id": str(uuid.uuid4()),
                "region": region,
                "model": model,
                "drive": drive,
                "powertrain": powertrain,
                "plant": plant,
                "year": year,
                "volume": volume,
            })
        self.df = pd.concat([self.df, pd.DataFrame(new_rows)], ignore_index=True)

    def delete_model(self, model: str):
        """モデルを削除"""
        self.df = self.df[self.df["model"] != model].reset_index(drop=True)

    def shift_timeline(self, model: str, region: str, shift_years: int):
        """モデルの販売年を前倒し(負)・後ろ倒し(正)"""
        mask = (self.df["model"] == model) & (self.df["region"] == region)
        self.df.loc[mask, "year"] = self.df.loc[mask, "year"] + shift_years

    # ----------------------------------------------------------
    # KPI算出メソッド
    # ----------------------------------------------------------

    def calc_development_effort(self) -> pd.DataFrame:
        """
        年度別の開発工数・費用を算出
        開発期間は販売開始年(start_year)の3年前から1年前までの3年間（均等割り）
        """
        # 1. 各モデルの販売開始年（グローバル最小値）を取得
        launch_years = self.df.groupby("model")["year"].min().reset_index()
        launch_years.columns = ["model", "launch_year"]
        
        # 2. 開発マスターをマージ
        dev_df = self.development_df.merge(launch_years, on="model", how="left").fillna(2030)
        
        results = []
        for _, row in dev_df.iterrows():
            model = row["model"]
            total_mm = row["lifespan_man_months"]
            unit_cost = row["unit_cost"]
            launch_y = int(row["launch_year"])
            
            # 3年間に均等割り
            mm_per_year = total_mm / 3
            cost_per_year = mm_per_year * unit_cost
            
            for offset in range(1, 4):
                dev_year = launch_y - offset
                results.append({
                    "year": dev_year,
                    "model": model,
                    "man_months": mm_per_year,
                    "cost": cost_per_year
                })
        
        res_df = pd.DataFrame(results)
        # 年度別に集計
        summary = res_df.groupby("year").agg({
            "man_months": "sum",
            "cost": "sum"
        }).reset_index()
        
        # 費用は億円単位に
        summary["cost_oku"] = (summary["cost"] / 10000).round(1)
        
        return summary

    def calc_total_volume(self) -> pd.DataFrame:
        """年度×地域別の合計台数"""
        return self.df.groupby(["year", "region"])["volume"].sum().reset_index()

    def calc_volume_by_model(self) -> pd.DataFrame:
        """年度×モデル別の合計台数"""
        return self.df.groupby(["year", "model"])["volume"].sum().reset_index()

    def calc_pt_ratio(self) -> pd.DataFrame:
        """年度別PTタイプ構成比"""
        pt_vol = self.df.groupby(["year", "powertrain"])["volume"].sum().reset_index()
        total = self.df.groupby("year")["volume"].sum().reset_index()
        total.columns = ["year", "total_volume"]
        merged = pt_vol.merge(total, on="year")
        merged["ratio"] = merged["volume"] / merged["total_volume"] * 100
        return merged

    def calc_financial(self) -> pd.DataFrame:
        """年度別の財務指標（売上高・営業利益）を算出"""
        df = self.df.copy()
        fin_df = self.financial_df

        # マスターデータから各モデルのパラメータを取得する辞書を作成
        price_dict = dict(zip(fin_df["model"], fin_df["price"]))
        fixed_cost_dict = dict(zip(fin_df["model"], fin_df["fixed_cost"]))
        var_cost_dict = dict(zip(fin_df["model"], fin_df["var_cost"]))

        def _get_price(model):
            return price_dict.get(model, 300)

        def _get_var_cost(model):
            return var_cost_dict.get(model, 200)
            
        def _get_fixed_cost(model):
            return fixed_cost_dict.get(model, 500)

        # 売上高（単価×台数） ※単価は万円
        df["revenue"] = df.apply(lambda r: r["volume"] * _get_price(r["model"]), axis=1)
        
        # 変動費総額（変動費単価×台数） ※変動費は万円
        df["total_var_cost"] = df.apply(lambda r: r["volume"] * _get_var_cost(r["model"]), axis=1)

        # 年度別に基礎データを集計 (売上万円, 変動費万円)
        result = df.groupby("year")[["revenue", "total_var_cost"]].sum().reset_index()
        
        # 年度別に稼働しているモデルを特定して固定費を計上
        # (その年に生産/販売実績があるモデルの固定費だけを合計する)
        yearly_fixed_costs = []
        for year in result["year"]:
            models_in_year = df[df["year"] == year]["model"].unique()
            # 該当年の全モデルの固定費(億円)を合算
            # 万円計算と単位を合わせるため後で処理するが、一旦億円のまま取得
            fixed_cost_sum_oku = sum([_get_fixed_cost(m) for m in models_in_year])
            yearly_fixed_costs.append(fixed_cost_sum_oku)
            
        result["fixed_cost_oku"] = yearly_fixed_costs

        # 万円 → 億円 に変換してまとめる
        result["revenue_oku"] = (result["revenue"] / 10000).round(0)
        result["var_cost_oku"] = (result["total_var_cost"] / 10000).round(0)
        
        # 利益 = 売上 - (固定費 + 変動費)  [全て億円]
        result["profit_oku"] = result["revenue_oku"] - (result["fixed_cost_oku"] + result["var_cost_oku"])
        
        # ダッシュボード用に元と同じカラム名を返す
        return pd.DataFrame({
            "year": result["year"],
            "revenue": result["revenue_oku"],
            "profit": result["profit_oku"]
        })

    def calc_non_financial(self) -> pd.DataFrame:
        """
        年度別の非財務指標を算出
        - LCA: 加重平均CO2排出量 (g/km) の内訳
        - CAFE: 加重平均燃費 (km/L)
        - accident_rate: 加重平均事故死亡率指数 (基準=1.0)
        - recycle_rate: リサイクル率 (%)
        """
        df = self.df.copy()
        non_fin_df = self.non_financial_df

        # マスターから環境/安全データを取得
        # キーは "model_powertrain" 単位で組み合わせる
        co2_cols = ["co2_use", "co2_disposal", "co2_production_in", "co2_production_out", "co2_logistics", "co2_energy"]
        
        # 各CO2項目の辞書を作成
        co2_dicts = {col: dict(zip(non_fin_df["model"] + "_" + non_fin_df["powertrain"], non_fin_df[col]))
                    for col in co2_cols}
        
        fuel_eff_dict = dict(zip(non_fin_df["model"] + "_" + non_fin_df["powertrain"], non_fin_df["fuel_eff"]))
        adas_dict = dict(zip(non_fin_df["model"] + "_" + non_fin_df["powertrain"], non_fin_df["adas"]))

        # 各行にCO2内訳を割り当て
        for col in co2_cols:
            df[col] = df.apply(
                lambda r: co2_dicts[col].get(f"{r['model']}_{r['powertrain']}", 0),
                axis=1
            )
            
        df["fuel_eff"] = df.apply(
            lambda r: fuel_eff_dict.get(f"{r['model']}_{r['powertrain']}", 20),
            axis=1
        )
        df["adas"] = df.apply(
            lambda r: adas_dict.get(f"{r['model']}_{r['powertrain']}", "P-ADAS Gen1"),
            axis=1
        )
        df["accident_factor"] = df["adas"].map(SAFETY_FACTOR).fillna(0.7)

        results = []
        for year, grp in df.groupby("year"):
            total_vol = grp["volume"].sum()
            if total_vol == 0:
                continue

            # 加重平均CO2内訳
            lca_data = {col: (grp[col] * grp["volume"]).sum() / total_vol for col in co2_cols}
            lca_total = sum(lca_data.values())

            # CAFE: 非BEVのみで計算
            non_bev = grp[~grp["powertrain"].isin(["BEV", "FCV"])]
            if len(non_bev) > 0:
                cafe = (non_bev["fuel_eff"] * non_bev["volume"]).sum() / non_bev["volume"].sum()
            else:
                cafe = 999

            # 事故死亡率指数
            accident = (grp["accident_factor"] * grp["volume"]).sum() / total_vol

            # リサイクル率
            bev_phev_ratio = grp[grp["powertrain"].isin(["BEV", "PHEV", "FCV"])]["volume"].sum() / total_vol
            recycle = 95 - bev_phev_ratio * 5

            res_row = {
                "year": year,
                "lca_co2": round(lca_total, 1),
                "cafe_fuel_eff": round(cafe, 1),
                "accident_rate_index": round(accident, 3),
                "recycle_rate": round(recycle, 1),
            }
            # 内訳も追加
            for col in co2_cols:
                res_row[col] = round(lca_data[col], 1)
                
            results.append(res_row)

        return pd.DataFrame(results)

    def calc_plant_utilization(self) -> pd.DataFrame:
        """工場別の生産台数 vs キャパシティ (年度別)"""
        prod = self.df.groupby(["year", "plant"])["volume"].sum().reset_index()
        prod.columns = ["year", "plant", "production"]

        # 工場マスターからキャパシティを結合（年度 + 工場名）
        cap_df = self.factory_df
        prod = prod.merge(cap_df[["year", "plant", "capacity"]], on=["year", "plant"], how="left")
        
        # マッチしない場合はデフォルト（旧互換用）
        prod["capacity"] = prod["capacity"].fillna(200000)
        prod["utilization"] = (prod["production"] / prod["capacity"] * 100).round(1)
        prod["over_capacity"] = prod["utilization"] > 100

        return prod

    def calc_plant_utilization_by_year(self, year: int) -> pd.DataFrame:
        """特定年度の工場別稼働率"""
        all_util = self.calc_plant_utilization()
        return all_util[all_util["year"] == year].reset_index(drop=True)

    def get_timeline_data(self) -> pd.DataFrame:
        """タイムラインビュー用のデータ（モデル×地域の販売期間）"""
        grouped = self.df.groupby(["model", "powertrain", "region"]).agg(
            start_year=("year", "min"),
            end_year=("year", "max"),
            total_volume=("volume", "sum"),
            avg_volume=("volume", "mean"),
        ).reset_index()
        return grouped

    def calc_factory_breakdown(self, plant: str) -> pd.DataFrame:
        """特定工場の生産ブレイクダウンデータ（年度別）"""
        plant_df = self.df[self.df["plant"] == plant].copy()
        if plant_df.empty:
            return pd.DataFrame(columns=["year", "powertrain", "model", "volume"])
        
        return plant_df.groupby(["year", "powertrain", "model"])["volume"].sum().reset_index()
