import { useState, useEffect, useRef } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

const riskColor = (s: number) => s >= 70 ? "#ff4444" : s >= 40 ? "#ffaa00" : "#00ff88";
const riskGlow = (s: number) => s >= 70 ? "0 0 20px #ff444466" : s >= 40 ? "0 0 20px #ffaa0066" : "0 0 20px #00ff8866";

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: #020408; }
  ::-webkit-scrollbar-thumb { background: #00ff8833; border-radius: 2px; }

  body { background: #020408; }

  .guardian-app {
    min-height: 100vh;
    background: #020408;
    background-image:
      radial-gradient(ellipse 80% 50% at 20% 10%, #001a0d22 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 80% 80%, #001220 0%, transparent 60%),
      linear-gradient(180deg, #020408 0%, #030810 100%);
    color: #e8f4f0;
    font-family: 'Space Mono', monospace;
    padding: 0;
    overflow-x: hidden;
  }

  .scan-overlay {
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background: repeating-linear-gradient(
      0deg, transparent, transparent 2px, #00ff0803 2px, #00ff0803 4px
    );
    opacity: 0.4;
  }

  .header {
    position: relative;
    padding: 32px 40px 24px;
    border-bottom: 1px solid #00ff8818;
    background: linear-gradient(180deg, #020c06 0%, transparent 100%);
    z-index: 10;
  }

  .header-top { display: flex; align-items: center; justify-content: space-between; }

  .logo-area { display: flex; align-items: center; gap: 16px; }

  .logo-icon {
    width: 44px; height: 44px;
    border: 1px solid #00ff8840;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    background: #00ff8808;
    box-shadow: 0 0 20px #00ff8820, inset 0 0 20px #00ff8808;
    animation: pulse-icon 3s ease-in-out infinite;
  }

  @keyframes pulse-icon {
    0%, 100% { box-shadow: 0 0 20px #00ff8820, inset 0 0 20px #00ff8808; }
    50% { box-shadow: 0 0 40px #00ff8840, inset 0 0 30px #00ff8815; }
  }

  .logo-text {
    font-family: 'Syne', sans-serif;
    font-size: 26px; font-weight: 800;
    color: #fff;
    letter-spacing: -0.5px;
  }

  .logo-text span { color: #00ff88; }

  .logo-sub {
    font-size: 10px; color: #00ff8866; letter-spacing: 3px;
    text-transform: uppercase; margin-top: 2px;
  }

  .status-badge {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 14px; border-radius: 99px;
    border: 1px solid #00ff8830;
    background: #00ff8808;
    font-size: 11px; color: #00ff88; letter-spacing: 2px;
  }

  .status-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #00ff88;
    box-shadow: 0 0 8px #00ff88;
    animation: blink 2s ease-in-out infinite;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; } 50% { opacity: 0.3; }
  }

  .main-grid {
    display: grid;
    grid-template-columns: 420px 1fr;
    gap: 0;
    min-height: calc(100vh - 100px);
    position: relative; z-index: 10;
  }

  .left-panel {
    border-right: 1px solid #00ff8815;
    padding: 28px 32px;
    background: linear-gradient(180deg, #020c0608 0%, transparent 100%);
    overflow-y: auto;
  }

  .right-panel {
    padding: 28px 32px;
    overflow-y: auto;
  }

  .section {
    margin-bottom: 20px;
    border: 1px solid #0d2018;
    border-radius: 12px;
    overflow: hidden;
    background: #050d0a;
    transition: border-color 0.3s;
  }

  .section:hover { border-color: #00ff8820; }

  .section-header {
    padding: 12px 16px;
    border-bottom: 1px solid #0d2018;
    background: #020c06;
    display: flex; align-items: center; gap: 10px;
  }

  .section-icon {
    width: 24px; height: 24px; border-radius: 6px;
    background: #00ff8812; border: 1px solid #00ff8825;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px;
  }

  .section-title {
    font-size: 10px; letter-spacing: 3px; color: #00ff8899;
    text-transform: uppercase; font-weight: 700;
  }

  .section-body { padding: 16px; }

  .upload-zone {
    border: 1px dashed #00ff8830;
    border-radius: 10px;
    padding: 28px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    background: #020c0650;
    position: relative;
    overflow: hidden;
  }

  .upload-zone:hover {
    border-color: #00ff8860;
    background: #00ff8808;
  }

  .upload-zone.has-file {
    border-color: #00ff8850;
    background: #00ff8808;
  }

  .upload-icon { font-size: 28px; margin-bottom: 10px; opacity: 0.7; }
  .upload-text { font-size: 12px; color: #00ff8888; letter-spacing: 1px; }
  .upload-sub { font-size: 10px; color: #00ff8844; margin-top: 4px; }
  .upload-filename { font-size: 13px; color: #00ff88; font-weight: 700; }

  .vitals-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .vital-field label {
    display: block;
    font-size: 9px; letter-spacing: 2px; color: #00ff8855;
    text-transform: uppercase; margin-bottom: 5px;
  }

  .vital-field input {
    width: 100%;
    background: #020c06;
    border: 1px solid #0d2018;
    border-radius: 6px;
    padding: 8px 10px;
    color: #00ff88cc;
    font-size: 13px;
    font-family: 'Space Mono', monospace;
    outline: none;
    transition: border-color 0.2s;
  }

  .vital-field input:focus {
    border-color: #00ff8840;
    background: #00ff8805;
  }

  .run-btn {
    width: 100%;
    padding: 16px;
    border: none;
    border-radius: 10px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
  }

  .run-btn.active {
    background: linear-gradient(135deg, #00ff88, #00cc6a);
    color: #020c06;
    box-shadow: 0 0 30px #00ff8840;
  }

  .run-btn.active:hover {
    box-shadow: 0 0 50px #00ff8870;
    transform: translateY(-1px);
  }

  .run-btn.active::after {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(90deg, transparent, #ffffff20, transparent);
    transform: translateX(-100%);
    animation: shimmer 2.5s ease-in-out infinite;
  }

  @keyframes shimmer {
    100% { transform: translateX(100%); }
  }

  .run-btn.disabled {
    background: #0d2018;
    color: #00ff8830;
    cursor: not-allowed;
  }

  .run-btn.loading {
    background: #0d2018;
    color: #00ff88;
  }

  .error-box {
    margin-top: 12px;
    padding: 12px 16px;
    border: 1px solid #ff444430;
    border-radius: 8px;
    background: #ff444408;
    color: #ff6666;
    font-size: 11px;
    letter-spacing: 0.5px;
  }

  /* RIGHT PANEL */

  .empty-state {
    height: 100%;
    min-height: 500px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    opacity: 0.4;
  }

  .empty-icon {
    font-size: 48px;
    filter: grayscale(1);
  }

  .empty-text {
    font-size: 11px; letter-spacing: 2px; color: #00ff88;
    text-transform: uppercase; text-align: center; line-height: 1.8;
  }

  .loader {
    height: 100%;
    min-height: 500px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 20px;
  }

  .loader-ring {
    width: 60px; height: 60px;
    border: 2px solid #00ff8820;
    border-top-color: #00ff88;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .loader-text {
    font-size: 10px; letter-spacing: 3px; color: #00ff8888;
    text-transform: uppercase;
    animation: fade 1.5s ease-in-out infinite;
  }

  @keyframes fade { 0%,100% { opacity: 0.4; } 50% { opacity: 1; } }

  .results-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
  }

  .result-card {
    border: 1px solid #0d2018;
    border-radius: 12px;
    padding: 18px;
    background: #050d0a;
    transition: all 0.3s;
    animation: fadeUp 0.5s ease both;
  }

  .result-card:hover { border-color: #00ff8820; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .result-card.delay-1 { animation-delay: 0.1s; }
  .result-card.delay-2 { animation-delay: 0.2s; }
  .result-card.delay-3 { animation-delay: 0.3s; }
  .result-card.delay-4 { animation-delay: 0.4s; }
  .result-card.full-width { grid-column: 1 / -1; }

  .card-label {
    font-size: 9px; letter-spacing: 3px; color: #00ff8855;
    text-transform: uppercase; margin-bottom: 14px;
    display: flex; align-items: center; gap: 8px;
  }

  .card-label::after {
    content: '';
    flex: 1; height: 1px;
    background: linear-gradient(90deg, #00ff8820, transparent);
  }

  .summary-text {
    font-size: 12px; line-height: 1.8; color: #a8c4b8;
    letter-spacing: 0.3px;
  }

  .summary-text strong { color: #00ff88; }

  .risk-display {
    display: flex; align-items: center; gap: 16px;
  }

  .risk-number {
    font-family: 'Syne', sans-serif;
    font-size: 64px; font-weight: 800;
    line-height: 1;
    transition: color 0.3s;
  }

  .risk-info { flex: 1; }

  .risk-label {
    font-size: 11px; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; margin-bottom: 8px;
  }

  .risk-bar-track {
    height: 4px; border-radius: 99px;
    background: #0d2018; overflow: hidden;
  }

  .risk-bar-fill {
    height: 100%; border-radius: 99px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .risk-prob {
    font-size: 10px; color: #00ff8844; margin-top: 6px; letter-spacing: 1px;
  }

  .top-finding {
    margin-bottom: 8px;
  }

  .finding-name {
    font-family: 'Syne', sans-serif;
    font-size: 20px; font-weight: 700;
    color: #fff; margin-bottom: 4px;
  }

  .finding-conf {
    font-size: 11px; color: #00ff88; letter-spacing: 1px;
  }

  .dosage-tier {
    font-family: 'Syne', sans-serif;
    font-size: 22px; font-weight: 700;
    color: #00ff88; margin-bottom: 8px;
  }

  .dosage-desc {
    font-size: 11px; color: #7a9e8a; line-height: 1.7; letter-spacing: 0.3px;
  }

  .dosage-conf {
    margin-top: 10px;
    font-size: 10px; color: #00ff8844; letter-spacing: 1px;
  }

  .bars-list { display: flex; flex-direction: column; gap: 10px; }

  .bar-row {}

  .bar-meta {
    display: flex; justify-content: space-between;
    font-size: 11px; margin-bottom: 5px;
  }

  .bar-name { color: #7a9e8a; }

  .bar-val { font-weight: 700; letter-spacing: 1px; }

  .bar-track {
    height: 3px; border-radius: 99px;
    background: #0d2018; overflow: hidden;
  }

  .bar-fill {
    height: 100%; border-radius: 99px;
    transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
  }
`;

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState("");
  const [animated, setAnimated] = useState(false);

  const [patient, setPatient] = useState({
    age: 55, bmi: 28.5, systolic_bp: 145, diastolic_bp: 90,
    heart_rate: 82, oxygen_sat: 95.5, glucose: 180,
    smoker: 1, diabetic: 1, family_history: 1,
  });

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true); setError(""); setResults(null); setAnimated(false);
    try {
      const form = new FormData();
      form.append("file", file);
      Object.entries(patient).forEach(([k, v]) => form.append(k, String(v)));
      const { data } = await axios.post(`${API}/analyze/full`, form);
      setResults(data);
      setTimeout(() => setAnimated(true), 100);
    } catch {
      setError("ANALYSIS FAILED — VERIFY API CONNECTION ON PORT 8000");
    } finally { setLoading(false); }
  };

  const barData = results
    ? Object.entries(results.vision?.all_scores || {})
        .filter(([k]) => k !== "No Finding")
        .sort((a: any, b: any) => (b[1] as number) - (a[1] as number))
        .slice(0, 8)
        .map(([name, value]: any) => ({ name, value: Math.round(value * 100) }))
    : [];

  const formatSummary = (text: string) => {
    if (!text) return text;
    return text.replace(/(HIGH RISK|MODERATE RISK|LOW RISK|High Dose|Moderate Dose|Low Dose|Monitoring Only)/g,
      '<strong>$1</strong>');
  };

  return (
    <>
      <style>{css}</style>
      <div className="guardian-app">
        <div className="scan-overlay" />

        {/* Header */}
        <div className="header">
          <div className="header-top">
            <div className="logo-area">
              <div className="logo-icon">🛡</div>
              <div>
                <div className="logo-text">GUARD<span>IAN</span></div>
                <div className="logo-sub">Healthcare Diagnostic Suite</div>
              </div>
            </div>
            <div className="status-badge">
              <div className="status-dot" />
              SYSTEM ONLINE
            </div>
          </div>
        </div>

        {/* Main */}
        <div className="main-grid">

          {/* LEFT */}
          <div className="left-panel">

            {/* Upload */}
            <div className="section">
              <div className="section-header">
                <div className="section-icon">📡</div>
                <div className="section-title">Imaging Input</div>
              </div>
              <div className="section-body">
                <label className={`upload-zone ${file ? "has-file" : ""}`}>
                  <input type="file" accept="image/*" style={{ display: "none" }}
                    onChange={e => setFile(e.target.files?.[0] || null)} />
                  {file ? (
                    <>
                      <div className="upload-icon">✅</div>
                      <div className="upload-filename">{file.name}</div>
                      <div className="upload-sub">IMAGE LOADED — READY FOR ANALYSIS</div>
                    </>
                  ) : (
                    <>
                      <div className="upload-icon">⬆</div>
                      <div className="upload-text">DROP X-RAY IMAGE</div>
                      <div className="upload-sub">JPG · PNG · DICOM COMPATIBLE</div>
                    </>
                  )}
                </label>
              </div>
            </div>

            {/* Vitals */}
            <div className="section">
              <div className="section-header">
                <div className="section-icon">📊</div>
                <div className="section-title">Patient Vitals</div>
              </div>
              <div className="section-body">
                <div className="vitals-grid">
                  {Object.entries(patient).map(([key, val]) => (
                    <div className="vital-field" key={key}>
                      <label>{key.replace(/_/g, " ")}</label>
                      <input type="number" value={val}
                        onChange={e => setPatient(p => ({ ...p, [key]: parseFloat(e.target.value) }))} />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Button */}
            <button
              className={`run-btn ${!file ? "disabled" : loading ? "loading" : "active"}`}
              onClick={handleAnalyze}
              disabled={!file || loading}
            >
              {loading ? "[ PROCESSING... ]" : "[ RUN FULL DIAGNOSTIC ]"}
            </button>

            {error && <div className="error-box">⚠ {error}</div>}
          </div>

          {/* RIGHT */}
          <div className="right-panel">

            {!results && !loading && (
              <div className="empty-state">
                <div className="empty-icon">🩻</div>
                <div className="empty-text">
                  AWAITING INPUT<br />
                  UPLOAD X-RAY + PATIENT DATA<br />
                  TO INITIALIZE DIAGNOSTIC
                </div>
              </div>
            )}

            {loading && (
              <div className="loader">
                <div className="loader-ring" />
                <div className="loader-text">RUNNING AI ANALYSIS...</div>
              </div>
            )}

            {results && (
              <>
                {/* Summary - full width */}
                <div className="result-card full-width" style={{ marginBottom: 16, animationDelay: "0s" }}>
                  <div className="card-label">diagnostic summary</div>
                  <p className="summary-text"
                    dangerouslySetInnerHTML={{ __html: formatSummary(results.summary) }} />
                </div>

                <div className="results-grid">
                  {/* Risk Score */}
                  <div className="result-card delay-1">
                    <div className="card-label">risk score</div>
                    <div className="risk-display">
                      <div className="risk-number" style={{ color: riskColor(results.risk.score), textShadow: riskGlow(results.risk.score) }}>
                        {results.risk.score}
                      </div>
                      <div className="risk-info">
                        <div className="risk-label" style={{ color: riskColor(results.risk.score) }}>
                          {results.risk.label}
                        </div>
                        <div className="risk-bar-track">
                          <div className="risk-bar-fill" style={{
                            width: animated ? `${results.risk.score}%` : "0%",
                            background: riskColor(results.risk.score),
                            boxShadow: riskGlow(results.risk.score)
                          }} />
                        </div>
                        <div className="risk-prob">P(RISK) = {results.risk.probability}</div>
                      </div>
                    </div>
                  </div>

                  {/* Top Finding */}
                  <div className="result-card delay-2">
                    <div className="card-label">primary finding</div>
                    <div className="top-finding">
                      <div className="finding-name">{results.vision.top_condition}</div>
                      <div className="finding-conf">
                        {Math.round(results.vision.confidence * 100)}% CONFIDENCE
                      </div>
                    </div>
                    <div style={{ marginTop: 12 }}>
                      <div className="risk-bar-track">
                        <div className="risk-bar-fill" style={{
                          width: animated ? `${Math.round(results.vision.confidence * 100)}%` : "0%",
                          background: "linear-gradient(90deg, #00aaff, #0066ff)"
                        }} />
                      </div>
                    </div>
                  </div>

                  {/* Dosage */}
                  <div className="result-card delay-3">
                    <div className="card-label">dosage recommendation</div>
                    <div className="dosage-tier">{results.dosage.label}</div>
                    <div className="dosage-desc">{results.dosage.description}</div>
                    <div className="dosage-conf">
                      CONFIDENCE: {(results.dosage.confidence * 100).toFixed(1)}%
                    </div>
                  </div>

                  {/* Imaging Findings */}
                  <div className="result-card delay-4">
                    <div className="card-label">imaging findings</div>
                    <div className="bars-list">
                      {barData.map((item: any, i: number) => (
                        <div className="bar-row" key={item.name}>
                          <div className="bar-meta">
                            <span className="bar-name">{item.name}</span>
                            <span className="bar-val" style={{
                              color: item.value > 60 ? "#ff4444" : item.value > 40 ? "#ffaa00" : "#00ff88"
                            }}>{item.value}%</span>
                          </div>
                          <div className="bar-track">
                            <div className="bar-fill" style={{
                              width: animated ? `${item.value}%` : "0%",
                              background: item.value > 60
                                ? "linear-gradient(90deg, #ff4444, #ff6666)"
                                : item.value > 40
                                ? "linear-gradient(90deg, #ffaa00, #ffcc44)"
                                : "linear-gradient(90deg, #00ff88, #00cc6a)",
                              transitionDelay: `${i * 0.08}s`
                            }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}