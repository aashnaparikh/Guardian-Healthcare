from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.vision.preprocess import preprocess_xray
from backend.vision.model import build_model, preprocess_for_model, run_inference
from backend.risk_engine.risk_model import generate_patient_data, clean_data, train_risk_model, get_risk_score
from backend.dosage_advisor.advisor_model import build_advisor_model, generate_training_data, train_advisor, recommend_dosage

app = FastAPI(
    title="Guardian Healthcare Diagnostic Suite",
    description="AI-powered medical imaging + patient risk analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("\n🩺 Guardian API starting up — loading models...\n")

cnn_model = build_model(pretrained=True)
print("✓ CNN loaded")

df = generate_patient_data(1000)
df = clean_data(df)
risk_model, risk_scaler, _ = train_risk_model(df)
print("✓ Risk Engine loaded")

X, y = generate_training_data(2000)
dosage_model = build_advisor_model()
train_advisor(dosage_model, X, y)
print("✓ Dosage Advisor loaded")

print("\n✅ All models ready. Guardian is online.\n")


@app.get("/")
def root():
    return {
        "name": "Guardian Healthcare Diagnostic Suite",
        "status": "online",
        "pipelines": ["vision", "risk_engine", "dosage_advisor"],
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy", "models_loaded": 3}


@app.post("/analyze/full")
async def full_analysis(
    file: UploadFile = File(...),
    age: float = Form(...),
    bmi: float = Form(...),
    systolic_bp: float = Form(...),
    diastolic_bp: float = Form(...),
    heart_rate: float = Form(...),
    oxygen_sat: float = Form(...),
    glucose: float = Form(...),
    smoker: int = Form(...),
    diabetic: int = Form(...),
    family_history: int = Form(...),
):
    patient_dict = {
        "age": age, "bmi": bmi, "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp, "heart_rate": heart_rate,
        "oxygen_sat": oxygen_sat, "glucose": glucose,
        "smoker": smoker, "diabetic": diabetic, "family_history": family_history
    }

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        img = preprocess_xray(tmp_path)
        tensor = preprocess_for_model(img)
        vision_results = run_inference(cnn_model, tensor)
    finally:
        os.unlink(tmp_path)

    top_condition = max(vision_results, key=vision_results.get)
    cnn_severity = vision_results[top_condition]

    risk_result = get_risk_score(risk_model, risk_scaler, patient_dict)
    dosage_result = recommend_dosage(dosage_model, cnn_severity, risk_result["score"])

    summary = (
        f"Patient flagged as {risk_result['label']} (score {risk_result['score']}/100). "
        f"Top imaging finding: {top_condition} ({cnn_severity:.1%} confidence). "
        f"Recommendation: {dosage_result['label']} — {dosage_result['description']}"
    )

    return {
        "vision": {
            "top_condition": top_condition,
            "confidence": round(cnn_severity, 4),
            "all_scores": {k: round(v, 4) for k, v in vision_results.items()}
        },
        "risk":    risk_result,
        "dosage":  dosage_result,
        "summary": summary
    }