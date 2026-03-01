import numpy as np
import tensorflow as tf
from tensorflow import keras

DOSAGE_TIERS = {
    0: {"label": "Monitoring Only",    "description": "No medication required. Schedule follow-up in 3 months."},
    1: {"label": "Low Dose",           "description": "Standard prophylactic dose. Monitor every 6 weeks."},
    2: {"label": "Moderate Dose",      "description": "Therapeutic dose indicated. Monitor every 2 weeks."},
    3: {"label": "High Dose",          "description": "Aggressive intervention required. Immediate specialist referral."},
}


# ── 1. Generate synthetic training data ──────────────────────────────────────

def generate_training_data(n_samples: int = 2000, seed: int = 42):
    """
    Features: [cnn_severity (0-1), risk_score (0-100)]
    Label: dosage tier (0-3)
    """
    np.random.seed(seed)
    cnn_severity = np.random.beta(2, 5, n_samples)           # skewed low (most scans normal)
    risk_score   = np.random.randint(0, 101, n_samples) / 100.0

    # Dosage logic based on combined severity
    combined = (cnn_severity * 0.6) + (risk_score * 0.4)
    labels = np.digitize(combined, bins=[0.25, 0.50, 0.75]) # 0,1,2,3

    X = np.column_stack([cnn_severity, risk_score]).astype(np.float32)
    y = keras.utils.to_categorical(labels, num_classes=4)
    return X, y


# ── 2. Build the Keras MLP ────────────────────────────────────────────────────

def build_advisor_model() -> keras.Model:
    """
    A small but effective MLP:
    2 inputs → 64 → 32 → 4 outputs (dosage tiers)
    """
    model = keras.Sequential([
        keras.layers.Input(shape=(2,)),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(32, activation="relu"),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(4, activation="softmax")
    ], name="DosageAdvisor")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


# ── 3. Train ──────────────────────────────────────────────────────────────────

def train_advisor(model: keras.Model, X, y) -> keras.callbacks.History:
    split = int(len(X) * 0.8)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=40,
        batch_size=32,
        verbose=0,
        callbacks=[
            keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)
        ]
    )

    val_acc = max(history.history["val_accuracy"])
    print(f"  Best validation accuracy: {val_acc:.4f}")
    return history


# ── 4. Recommend dosage ───────────────────────────────────────────────────────

def recommend_dosage(model: keras.Model, cnn_severity: float, risk_score: int) -> dict:
    """
    cnn_severity: float 0-1 (top confidence from CNN)
    risk_score:   int 0-100 (from Risk Engine)
    """
    X = np.array([[cnn_severity, risk_score / 100.0]], dtype=np.float32)
    proba = model.predict(X, verbose=0)[0]
    tier  = int(np.argmax(proba))

    return {
        "tier":        tier,
        "label":       DOSAGE_TIERS[tier]["label"],
        "description": DOSAGE_TIERS[tier]["description"],
        "confidence":  round(float(proba[tier]), 4),
        "all_proba":   {DOSAGE_TIERS[i]["label"]: round(float(p), 4) for i, p in enumerate(proba)}
    }


# ── Smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n--- Guardian Dosage Advisor ---\n")

    print("Generating training data...")
    X, y = generate_training_data(2000)
    print(f"✓ {len(X)} samples | Features: {X.shape} | Labels: {y.shape}")

    print("\nBuilding Keras model...")
    model = build_advisor_model()
    model.summary()

    print("\nTraining...")
    train_advisor(model, X, y)
    print("✓ Training complete")

    # Test three patient scenarios
    scenarios = [
        {"name": "Healthy Patient",      "cnn": 0.10, "risk": 15},
        {"name": "Moderate Risk Patient","cnn": 0.45, "risk": 55},
        {"name": "Critical Patient",     "cnn": 0.85, "risk": 99},
    ]

    print("\n--- Dosage Recommendations ---")
    for s in scenarios:
        result = recommend_dosage(model, s["cnn"], s["risk"])
        print(f"\n  {s['name']} (CNN: {s['cnn']}, Risk: {s['risk']}/100)")
        print(f"  → {result['label']} | {result['description']}")
        print(f"  → Confidence: {result['confidence']:.1%}")

    print("\n💊 Guardian Dosage Advisor: SMOKE TEST PASSED")