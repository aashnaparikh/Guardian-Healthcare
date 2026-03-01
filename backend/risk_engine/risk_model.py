import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, classification_report
import joblib
import os

# ── 1. Generate synthetic patient data ──────────────────────────────────────

def generate_patient_data(n_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Creates a realistic synthetic patient dataset.
    In production this would be replaced with real EHR data.
    """
    np.random.seed(seed)

    df = pd.DataFrame({
        "age":             np.random.randint(18, 90, n_samples),
        "bmi":             np.round(np.random.normal(27, 6, n_samples), 1),
        "systolic_bp":     np.random.randint(90, 200, n_samples),
        "diastolic_bp":    np.random.randint(60, 120, n_samples),
        "heart_rate":      np.random.randint(50, 120, n_samples),
        "oxygen_sat":      np.round(np.random.normal(97, 2, n_samples), 1),
        "glucose":         np.random.randint(70, 300, n_samples),
        "smoker":          np.random.randint(0, 2, n_samples),
        "diabetic":        np.random.randint(0, 2, n_samples),
        "family_history":  np.random.randint(0, 2, n_samples),
    })

    # Clip to realistic ranges
    df["bmi"]         = df["bmi"].clip(15, 50)
    df["oxygen_sat"]  = df["oxygen_sat"].clip(85, 100)

    # Risk label: high-risk if multiple danger signs present
    df["high_risk"] = (
        (df["age"] > 60).astype(int) +
        (df["systolic_bp"] > 140).astype(int) +
        (df["bmi"] > 30).astype(int) +
        (df["smoker"] == 1).astype(int) +
        (df["glucose"] > 200).astype(int) +
        (df["oxygen_sat"] < 95).astype(int)
    ) >= 3

    df["high_risk"] = df["high_risk"].astype(int)
    return df


# ── 2. Clean the data ────────────────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pandas cleaning pipeline:
    - Clip outliers to valid medical ranges
    - Fill any missing values with column medians
    - Report what was cleaned
    """
    print(f"  Input shape: {df.shape}")
    print(f"  Missing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")

    # Introduce some missing values to simulate real data, then fill them
    df = df.copy()
    mask = np.random.random(df.shape) < 0.02  # 2% missing
    df[mask] = np.nan

    before_nulls = df.isnull().sum().sum()
    df = df.fillna(df.median(numeric_only=True))
    print(f"  Filled {before_nulls} missing values with column medians")

    # Clip to valid ranges
    df["oxygen_sat"] = df["oxygen_sat"].clip(85, 100)
    df["bmi"]        = df["bmi"].clip(15, 50)
    df["heart_rate"] = df["heart_rate"].clip(30, 200)

    print(f"  Output shape: {df.shape}")
    return df


# ── 3. Train the Risk Score model ────────────────────────────────────────────

def train_risk_model(df: pd.DataFrame):
    """
    Train a Gradient Boosting classifier to predict high-risk patients.
    Returns the trained model, scaler, and evaluation metrics.
    """
    feature_cols = [
        "age", "bmi", "systolic_bp", "diastolic_bp",
        "heart_rate", "oxygen_sat", "glucose",
        "smoker", "diabetic", "family_history"
    ]
    X = df[feature_cols]
    y = df["high_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        random_state=42
    )
    model.fit(X_train_scaled, y_train)

    y_pred  = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    auc     = roc_auc_score(y_test, y_proba)

    print(f"\n  ROC-AUC Score: {auc:.4f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Low Risk', 'High Risk'])}")

    return model, scaler, auc


# ── 4. Score a single patient ─────────────────────────────────────────────────

def get_risk_score(model, scaler, patient: dict) -> dict:
    """
    Takes a patient dict and returns a 0-100 risk score + label.
    """
    feature_cols = [
        "age", "bmi", "systolic_bp", "diastolic_bp",
        "heart_rate", "oxygen_sat", "glucose",
        "smoker", "diabetic", "family_history"
    ]
    df_patient = pd.DataFrame([patient])[feature_cols]
    scaled     = scaler.transform(df_patient)
    proba      = model.predict_proba(scaled)[0][1]
    score      = int(proba * 100)

    if score >= 70:
        label = "HIGH RISK"
    elif score >= 40:
        label = "MODERATE RISK"
    else:
        label = "LOW RISK"

    return {"score": score, "label": label, "probability": round(proba, 4)}


# ── Smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n--- Guardian Risk Engine ---\n")

    print("Generating patient data...")
    df = generate_patient_data(n_samples=1000)
    print(f"✓ Generated {len(df)} patients | High-risk rate: {df['high_risk'].mean():.1%}")

    print("\nCleaning data...")
    df = clean_data(df)
    print("✓ Data cleaning complete")

    print("\nTraining Gradient Boosting model...")
    model, scaler, auc = train_risk_model(df)
    print(f"✓ Model trained | AUC: {auc:.4f}")

    # Score a sample high-risk patient
    test_patient = {
        "age": 68, "bmi": 34.2, "systolic_bp": 155,
        "diastolic_bp": 95, "heart_rate": 88, "oxygen_sat": 93.5,
        "glucose": 210, "smoker": 1, "diabetic": 1, "family_history": 1
    }
    result = get_risk_score(model, scaler, test_patient)
    print(f"\n--- Sample Patient Risk Score ---")
    print(f"  Score:  {result['score']}/100")
    print(f"  Label:  {result['label']}")
    print(f"  P(risk): {result['probability']}")

    print("\n📊 Guardian Risk Engine: SMOKE TEST PASSED")