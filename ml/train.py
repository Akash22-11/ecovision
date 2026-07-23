import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

ML_DIR = Path(__file__).parent
DATASET_PATH = ML_DIR / "dataset.csv"
MODEL_PATH = ML_DIR / "model.pkl"

FEATURE_COLUMNS = ["aqi", "pm25", "pm10", "temperature", "humidity", "wind_speed"]
TARGET_COLUMN = "aqi_next_24h"

RANDOM_SEED = 42

def generate_synthetic_dataset(n_rows: int = 2000) -> pd.DataFrame:
    """
    Generate a synthetic dataset with a realistic relationship between
    current conditions and next-24h AQI: particulates push AQI up, wind
    disperses it, with noise to keep the model honest.
    """
    rng = np.random.default_rng(RANDOM_SEED)

    aqi = rng.uniform(30, 400, n_rows)
    pm25 = aqi * rng.uniform(0.35, 0.55, n_rows) + rng.normal(0, 5, n_rows)
    pm10 = pm25 * rng.uniform(1.3, 1.8, n_rows) + rng.normal(0, 8, n_rows)
    temperature = rng.uniform(10, 42, n_rows)
    humidity = rng.uniform(15, 95, n_rows)
    wind_speed = rng.uniform(0.2, 9.0, n_rows)

    
    particulate_pressure = pm25 * 0.5 + pm10 * 0.3
    dispersion_relief = wind_speed * 6.0
    humidity_trap = np.where(humidity > 70, 8.0, 0.0)  # stagnant humid air traps pollution
    persistence = aqi * 0.55

    
    noise = rng.normal(0, 10, n_rows)
    aqi_next_24h = np.clip(
        persistence + particulate_pressure * 0.3 - dispersion_relief + humidity_trap + noise, 0, 500
    )

    df = pd.DataFrame(
        {
            "aqi": aqi,
            "pm25": pm25.clip(0),
            "pm10": pm10.clip(0),
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "aqi_next_24h": aqi_next_24h,
        }
    )
    return df.round(2)


def load_or_create_dataset() -> pd.DataFrame:
    if DATASET_PATH.exists():
        print(f"Loading existing dataset from {DATASET_PATH}")
        return pd.read_csv(DATASET_PATH)

    print(f"No dataset found at {DATASET_PATH}; generating a synthetic one for bootstrapping.")
    df = generate_synthetic_dataset()
    df.to_csv(DATASET_PATH, index=False)
    print(f"Synthetic dataset written to {DATASET_PATH} ({len(df)} rows).")
    return df


def train() -> None:
    df = load_or_create_dataset()

    missing = set(FEATURE_COLUMNS + [TARGET_COLUMN]) - set(df.columns)
    if missing:
        print(f"ERROR: dataset is missing required columns: {missing}", file=sys.stderr)
        sys.exit(1)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=3,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print("\n--- Training complete ---")
    print(f"Test MAE : {mae:.2f} AQI points")
    print(f"Test R^2 : {r2:.3f}")
    print("Feature importances:")
    for feature, importance in sorted(
        zip(FEATURE_COLUMNS, model.feature_importances_), key=lambda x: -x[1]
    ):
        print(f"  {feature:<12} {importance:.3f}")

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
