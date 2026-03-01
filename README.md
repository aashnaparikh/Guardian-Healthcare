# 🛡 Guardian — Healthcare Diagnostic Suite

**Full-stack AI platform for medical imaging analysis, patient risk scoring, and dosage recommendation.**

Built as a portfolio project to demonstrate end-to-end ML engineering: from model training to REST API to production-ready React dashboard.

---

## What It Does

Upload a chest X-ray and enter patient vitals. Guardian runs three AI pipelines in parallel and returns a unified diagnostic report in real time.

| Pipeline | Input | Output |
|---|---|---|
| Vision | Chest X-ray image | 15-condition classification with confidence scores |
| Risk Engine | Patient vitals (10 features) | Risk score 0–100 + HIGH/LOW label |
| Dosage Advisor | CNN severity + Risk score | Dosage tier recommendation |

---

## Tech Stack

**Machine Learning**
- PyTorch — ResNet-18 CNN (11M parameters, transfer learning, multi-label classification)
- Scikit-Learn — Gradient Boosting Classifier (AUC 0.9853)
- Keras / TensorFlow — MLP fusion model (98.25% validation accuracy)
- OpenCV — CLAHE preprocessing, Gaussian denoising, image normalization

**Backend**
- FastAPI — REST API with auto-generated Swagger docs
- Uvicorn — ASGI server
- Pandas — Patient data pipeline + missing value imputation
- Python 3.11

**Frontend**
- React 19 + TypeScript
- Axios — API communication
- Custom CSS — Medical terminal UI with scan line animations

---

## Model Performance

| Model | Metric | Score |
|---|---|---|
| ResNet-18 CNN | Architecture | 11,184,207 parameters |
| Gradient Boosting | ROC-AUC | 0.9853 |
| Gradient Boosting | Accuracy | 94% |
| Keras MLP | Validation Accuracy | 98.25% |

---

## Project Structure

```
guardian/
├── backend/
│   ├── api.py                    # FastAPI application
│   ├── vision/
│   │   ├── preprocess.py         # OpenCV pipeline
│   │   └── model.py              # PyTorch ResNet-18
│   ├── risk_engine/
│   │   └── risk_model.py         # Scikit-Learn GBM
│   └── dosage_advisor/
│       └── advisor_model.py      # Keras MLP
├── frontend/
│   └── src/
│       └── App.tsx               # React dashboard
├── requirements.txt
└── Procfile
```

---

## Running Locally

**Backend**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.api:app --reload
# API live at http://127.0.0.1:8000
# Swagger docs at http://127.0.0.1:8000/docs
```

**Frontend**
```bash
cd frontend
npm install
npm start
# Dashboard at http://localhost:3000
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | System status |
| GET | `/health` | Health check |
| POST | `/analyze/full` | Full diagnostic (X-ray + vitals) |

---

## Conditions Detected

Atelectasis · Cardiomegaly · Effusion · Infiltration · Mass · Nodule · Pneumonia · Pneumothorax · Consolidation · Edema · Emphysema · Fibrosis · Pleural Thickening · Hernia

Model architecture based on NIH ChestX-ray14 dataset (112K images, 14 pathology labels).

---

*Built by Aashna Parikh*
