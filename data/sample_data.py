"""
Honda 四輪事業 サンプルデータ生成モジュール
リアルなHondaモデルラインナップに基づいたシミュレーション用データを生成する
"""

import pandas as pd
import numpy as np
import uuid


# ------------------------------------------------------------------
# マスターデータ定義
# ------------------------------------------------------------------

MODELS = [
    # model, powertrain, drive, base_price_万円, co2_g_per_km, safety_level(1-5)
    {"model": "N-BOX",     "powertrain": "PET",    "drive": "FF",  "price": 165,  "co2": 130, "safety": 3},
    {"model": "N-BOX",     "powertrain": "HEV",    "drive": "FF",  "price": 195,  "co2": 85,  "safety": 3},
    {"model": "Fit",       "powertrain": "PET",    "drive": "FF",  "price": 175,  "co2": 120, "safety": 3},
    {"model": "Fit",       "powertrain": "HEV",    "drive": "FF",  "price": 220,  "co2": 75,  "safety": 4},
    {"model": "Civic",     "powertrain": "PET",    "drive": "FF",  "price": 320,  "co2": 140, "safety": 4},
    {"model": "Civic",     "powertrain": "HEV",    "drive": "FF",  "price": 370,  "co2": 80,  "safety": 4},
    {"model": "Accord",    "powertrain": "HEV",    "drive": "FF",  "price": 450,  "co2": 70,  "safety": 5},
    {"model": "CR-V",      "powertrain": "HEV",    "drive": "4WD", "price": 420,  "co2": 90,  "safety": 4},
    {"model": "CR-V",      "powertrain": "PHEV",   "drive": "4WD", "price": 490,  "co2": 40,  "safety": 4},
    {"model": "HR-V",      "powertrain": "HEV",    "drive": "FF",  "price": 300,  "co2": 85,  "safety": 4},
    {"model": "HR-V",      "powertrain": "FFV",    "drive": "FF",  "price": 280,  "co2": 110, "safety": 3},
    {"model": "ZR-V",      "powertrain": "HEVFFV", "drive": "4WD", "price": 360,  "co2": 78,  "safety": 4},
    {"model": "ZR-V",      "powertrain": "HEV",    "drive": "4WD", "price": 350,  "co2": 82,  "safety": 4},
    {"model": "e:NY1",     "powertrain": "BEV",    "drive": "FF",  "price": 480,  "co2": 0,   "safety": 4},
    {"model": "e:NP1",     "powertrain": "BEV",    "drive": "4WD", "price": 550,  "co2": 0,   "safety": 5},
    {"model": "Prologue",  "powertrain": "BEV",    "drive": "4WD", "price": 600,  "co2": 0,   "safety": 5},
    {"model": "0 Series Sedan",  "powertrain": "BEV", "drive": "4WD", "price": 700, "co2": 0, "safety": 5},
    {"model": "0 Series SUV",    "powertrain": "BEV", "drive": "4WD", "price": 750, "co2": 0, "safety": 5},
    {"model": "CR-V FCEV", "powertrain": "FCV",    "drive": "4WD", "price": 700,  "co2": 0,   "safety": 5},
]

REGIONS = ["Japan", "North America", "Europe", "China", "Asia/Oceania"]

PLANTS = {
    "鈴鹿":       {"region": "Japan",          "capacity": 250000},
    "埼玉(寄居)":  {"region": "Japan",          "capacity": 250000},
    "アラバマ":     {"region": "North America",  "capacity": 340000},
    "オハイオ(MEP)": {"region": "North America", "capacity": 440000},
    "武漢(第一)":   {"region": "China",          "capacity": 240000},
    "武漢(第二)":   {"region": "China",          "capacity": 240000},
    "広州":        {"region": "China",           "capacity": 200000},
    "スウィンドン": {"region": "Europe",          "capacity": 150000},
    "タイ(プラチンブリ)": {"region": "Asia/Oceania", "capacity": 200000},
    "インド(タプカラ)":   {"region": "Asia/Oceania", "capacity": 180000},
}

# モデル → 販売期間・工場・地域 のマッピング (年度ベース 2025-2035)
MODEL_PLAN = [
    # (model, powertrain, drive, plant, region, start_year, end_year, base_volume)
    ("N-BOX",   "PET", "FF",  "鈴鹿",       "Japan",          2025, 2030, 180000),
    ("N-BOX",   "HEV", "FF",  "鈴鹿",       "Japan",          2028, 2035, 120000),
    ("Fit",     "PET", "FF",  "鈴鹿",       "Japan",          2025, 2029, 80000),
    ("Fit",     "HEV", "FF",  "鈴鹿",       "Japan",          2025, 2035, 60000),
    ("Fit",     "HEV", "FF",  "タイ(プラチンブリ)", "Asia/Oceania", 2025, 2035, 45000),
    ("Civic",   "PET", "FF",  "埼玉(寄居)",  "Japan",          2025, 2028, 35000),
    ("Civic",   "HEV", "FF",  "埼玉(寄居)",  "Japan",          2025, 2035, 45000),
    ("Civic",   "HEV", "FF",  "オハイオ(MEP)", "North America", 2025, 2035, 90000),
    ("Accord",  "HEV", "FF",  "オハイオ(MEP)", "North America", 2025, 2035, 110000),
    ("Accord",  "HEV", "FF",  "埼玉(寄居)",  "Japan",          2025, 2035, 25000),
    ("CR-V",    "HEV", "4WD", "オハイオ(MEP)", "North America", 2025, 2035, 200000),
    ("CR-V",    "PHEV","4WD", "オハイオ(MEP)", "North America", 2027, 2035, 80000),
    ("CR-V",    "HEV", "4WD", "武漢(第一)",   "China",          2025, 2035, 95000),
    ("HR-V",    "HEV", "FF",  "タイ(プラチンブリ)", "Asia/Oceania", 2025, 2035, 70000),
    ("HR-V",    "FFV", "FF",  "タイ(プラチンブリ)", "Asia/Oceania", 2025, 2032, 40000),
    ("HR-V",    "HEV", "FF",  "武漢(第二)",   "China",          2025, 2033, 60000),
    ("ZR-V",    "HEVFFV", "4WD", "埼玉(寄居)",  "Japan",       2025, 2035, 40000),
    ("ZR-V",    "HEV", "4WD", "スウィンドン", "Europe",         2025, 2035, 55000),
    ("e:NY1",   "BEV", "FF",  "武漢(第二)",   "China",          2025, 2035, 50000),
    ("e:NY1",   "BEV", "FF",  "スウィンドン", "Europe",         2026, 2035, 35000),
    ("e:NP1",   "BEV", "4WD", "武漢(第一)",   "China",          2027, 2035, 40000),
    ("Prologue","BEV", "4WD", "アラバマ",     "North America",  2025, 2035, 70000),
    ("0 Series Sedan", "BEV", "4WD", "埼玉(寄居)", "Japan",     2026, 2035, 30000),
    ("0 Series Sedan", "BEV", "4WD", "オハイオ(MEP)", "North America", 2026, 2035, 60000),
    ("0 Series SUV",   "BEV", "4WD", "アラバマ",    "North America",  2027, 2035, 55000),
    ("0 Series SUV",   "BEV", "4WD", "スウィンドン", "Europe",        2027, 2035, 40000),
    ("Fit",     "HEV", "FF",  "インド(タプカラ)", "Asia/Oceania", 2026, 2035, 55000),
    ("CR-V",    "HEV", "4WD", "インド(タプカラ)", "Asia/Oceania", 2027, 2035, 35000),
    ("CR-V FCEV", "FCV", "4WD", "埼玉(寄居)", "Japan",          2028, 2035, 15000),
]


def generate_sample_data() -> pd.DataFrame:
    """サンプルデータを生成して DataFrame を返す"""
    np.random.seed(42)
    rows = []

    for (model, pt, dr, plant, region, start, end, base_vol) in MODEL_PLAN:
        for year in range(start, end + 1):
            # 年度ごとにリアルな変動を付与
            progress = (year - start) / max(end - start, 1)

            # BEV: 成長カーブ、ICE: 減少カーブ、HEV/PHEV: 緩やかな成長後安定
            if pt == "BEV" or pt == "FCV":
                growth = 1.0 + progress * 1.2  # 最大2.2倍
            elif pt in ("PET", "FFV"):
                growth = 1.0 - progress * 0.4  # 最大0.6倍
            elif pt == "PHEV":
                growth = 1.0 + progress * 0.5  # 最大1.5倍
            elif pt == "HEVFFV":
                growth = 1.0 + progress * 0.2  # 最大1.2倍
            else:  # HEV
                growth = 1.0 + progress * 0.3  # 最大1.3倍

            # ランダム変動 ±10%
            noise = np.random.uniform(0.9, 1.1)
            volume = int(base_vol * growth * noise)

            rows.append({
                "id": str(uuid.uuid4()),
                "region": region,
                "model": model,
                "drive": dr,
                "powertrain": pt,
                "plant": plant,
                "year": year,
                "volume": volume,
            })

    df = pd.DataFrame(rows)
    return df


def get_plant_capacity() -> pd.DataFrame:
    """工場キャパシティのDataFrameを返す"""
    rows = [{"plant": name, **info} for name, info in PLANTS.items()]
    return pd.DataFrame(rows)


def get_model_master() -> pd.DataFrame:
    """モデルマスターデータを返す"""
    return pd.DataFrame(MODELS)


def generate_financial_master() -> pd.DataFrame:
    """財務マスターデータの初期状態を生成して DataFrame を返す"""
    # 既存のFINANCIAL_PARAMSをベースに、固定費(億円)と変動費(万円)へと分解した初期データを作成する
    # ※原価率(cost_ratio)から逆算しつつ、適当なそれらしい数値を初期値とする
    
    financial_data = [
        {"id": str(uuid.uuid4()), "model": "N-BOX",          "price": 165, "fixed_cost": 500,  "var_cost": 130},
        {"id": str(uuid.uuid4()), "model": "Fit",            "price": 195, "fixed_cost": 600,  "var_cost": 150},
        {"id": str(uuid.uuid4()), "model": "Civic",          "price": 345, "fixed_cost": 1000, "var_cost": 260},
        {"id": str(uuid.uuid4()), "model": "Accord",         "price": 450, "fixed_cost": 1200, "var_cost": 330},
        {"id": str(uuid.uuid4()), "model": "CR-V",           "price": 440, "fixed_cost": 1500, "var_cost": 320},
        {"id": str(uuid.uuid4()), "model": "HR-V",           "price": 300, "fixed_cost": 900,  "var_cost": 220},
        {"id": str(uuid.uuid4()), "model": "ZR-V",           "price": 350, "fixed_cost": 1100, "var_cost": 260},
        {"id": str(uuid.uuid4()), "model": "e:NY1",          "price": 480, "fixed_cost": 2000, "var_cost": 380},
        {"id": str(uuid.uuid4()), "model": "e:NP1",          "price": 550, "fixed_cost": 2200, "var_cost": 440},
        {"id": str(uuid.uuid4()), "model": "Prologue",       "price": 600, "fixed_cost": 3000, "var_cost": 480},
        {"id": str(uuid.uuid4()), "model": "0 Series Sedan", "price": 700, "fixed_cost": 4000, "var_cost": 550},
        {"id": str(uuid.uuid4()), "model": "0 Series SUV",   "price": 750, "fixed_cost": 4500, "var_cost": 590},
        {"id": str(uuid.uuid4()), "model": "CR-V FCEV",      "price": 700, "fixed_cost": 1500, "var_cost": 580},
    ]
    return pd.DataFrame(financial_data)


def generate_non_financial_master() -> pd.DataFrame:
    """非財務マスターデータの初期状態を生成して DataFrame を返す"""
    non_fin_data = []
    
    # PT別のデフォルト燃費
    pt_fuel_eff_def = {
        "PET": 15, "FFV": 13, "HEV": 25, "HEVFFV": 22, 
        "PHEV": 40, "BEV": 999, "FCV": 999
    }
    
    # PT別のLCA CO2初期値 (g/km) の内訳
    # 概算値: 
    #   製品使用: ICE/HEVは高い、BEVは0
    #   廃棄: ほぼ一定
    #   生産(内作・外作): 固定要素 + バッテリー容量分(BEVが高い)
    #   輸送: ほぼ一定
    #   エネルギー製造: ICEは燃料精製分(小)、BEVは発電分(中)
    lca_defaults = {
        "PET":    {"use": 140, "disp": 5, "prod_in": 15, "prod_out": 25, "logi": 5, "ener": 10},
        "HEV":    {"use": 80,  "disp": 5, "prod_in": 18, "prod_out": 30, "logi": 5, "ener": 10},
        "PHEV":   {"use": 40,  "disp": 6, "prod_in": 20, "prod_out": 45, "logi": 5, "ener": 20},
        "BEV":    {"use": 0,   "disp": 8, "prod_in": 25, "prod_out": 70, "logi": 5, "ener": 40},
        "FCV":    {"use": 0,   "disp": 7, "prod_in": 25, "prod_out": 60, "logi": 5, "ener": 30},
        "FFV":    {"use": 120, "disp": 5, "prod_in": 15, "prod_out": 25, "logi": 5, "ener": 15},
        "HEVFFV": {"use": 75,  "disp": 5, "prod_in": 18, "prod_out": 30, "logi": 5, "ener": 12},
    }
    
    # ADASレベルと名称のマッピング
    adas_map = {
        1: "ADAS適用なし", 2: "E-ADAS", 3: "P-ADAS Gen1", 4: "P-ADAS Gen2", 5: "Elite"
    }
    
    for m in MODELS:
        pt = m["powertrain"]
        defaults = lca_defaults.get(pt, lca_defaults["PET"])
        non_fin_data.append({
            "id": str(uuid.uuid4()),
            "model": m["model"],
            "powertrain": pt,
            "co2_use": defaults["use"],
            "co2_disposal": defaults["disp"],
            "co2_production_in": defaults["prod_in"],
            "co2_production_out": defaults["prod_out"],
            "co2_logistics": defaults["logi"],
            "co2_energy": defaults["ener"],
            "fuel_eff": pt_fuel_eff_def.get(pt, 20),
            "adas": adas_map.get(m.get("safety", 3), "P-ADAS Gen1"),
        })
        
    return pd.DataFrame(non_fin_data)



def generate_factory_master() -> pd.DataFrame:
    """工場マスターデータの初期状態を生成して DataFrame を返す（年度別）"""
    rows = []
    for year in range(2025, 2036):
        for name, info in PLANTS.items():
            rows.append({
                "id": str(uuid.uuid4()),
                "year": year,
                "plant": name,
                "region": info["region"],
                "capacity": info["capacity"]
            })
    return pd.DataFrame(rows)


def generate_development_master() -> pd.DataFrame:
    """開発マスター（工数・単価）を生成して DataFrame を返す"""
    # リアルなHondaモデルに基づいた機種生涯工数（人月）と人月単価（万円/月）の初期値
    # 一般的に新型車開発には数千〜数万人月かかるとされる
    models = [
        "N-BOX", "Fit", "Civic", "Accord", "CR-V", "HR-V", "ZR-V", 
        "e:NY1", "e:NP1", "Prologue", "0 Series Sedan", "0 Series SUV", "CR-V FCEV"
    ]
    
    dev_data = []
    for m in models:
        # BEVや新型プラットフォーム(0 Series)は工数が高く設定
        if "0 Series" in m:
            lifespan_mm = 30000
        elif m in ("Prologue", "e:NY1", "e:NP1"):
            lifespan_mm = 20000
        else:
            lifespan_mm = 15000
            
        dev_data.append({
            "id": str(uuid.uuid4()),
            "model": m,
            "lifespan_man_months": lifespan_mm,  # 機種生涯工数(人月)
            "unit_cost": 150,                   # 人月単価(万円)
        })
        
    return pd.DataFrame(dev_data)


if __name__ == "__main__":
    df = generate_sample_data()
    print(f"生成されたレコード数: {len(df)}")
    print(df.head(20))
    print(f"\nモデル数: {df['model'].nunique()}")
    print(f"年度範囲: {df['year'].min()} - {df['year'].max()}")
    print(f"合計台数: {df['volume'].sum():,}")
