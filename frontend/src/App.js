import React, { useState } from "react";
import axios from "axios";

const cardStyle = {
  background: "#fff",
  borderRadius: "12px",
  padding: "16px",
  boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
  marginBottom: "14px",
};

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
    } catch (e) {
      setError("Failed to analyze report. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const riskColor = {
    high: "#e53935",
    medium: "#fb8c00",
    low: "#43a047",
  }[(result?.risk || "").toLowerCase()] || "#546e7a";

  return (
    <div style={{ fontFamily: "Inter, Arial", background: "#f4f7fb", minHeight: "100vh", padding: 24 }}>
      <div style={{ maxWidth: 840, margin: "0 auto" }}>
        <h1 style={{ marginBottom: 8 }}>MedMemory AI</h1>
        <p style={{ color: "#546e7a", marginBottom: 20 }}>Upload → AI → Timeline → Insight</p>

        <div style={cardStyle}>
          <h3>1) Upload Medical Report</h3>
          <input type="file" accept=".pdf,image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <br />
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            style={{ marginTop: 12, padding: "10px 18px", borderRadius: 8, border: "none", background: "#1565c0", color: "white", cursor: "pointer" }}
          >
            {loading ? "Analyzing..." : "Analyze Report"}
          </button>
          {error && <p style={{ color: "#e53935" }}>{error}</p>}
        </div>

        {result && (
          <>
            <div style={cardStyle}>
              <h3>2) Patient Summary</h3>
              <p><b>Disease:</b> {result.disease}</p>
              <p><b>Medication:</b> {result.medication}</p>
              <p>
                <b>Risk:</b>{" "}
                <span style={{ color: riskColor, fontWeight: 700 }}>{result.risk}</span>
              </p>
              <p><b>Insight:</b> {result.insight}</p>
            </div>

            <div style={cardStyle}>
              <h3>3) Timeline</h3>
              <div style={{ borderLeft: "3px solid #1976d2", marginLeft: 10, paddingLeft: 14 }}>
                {(result.timeline || []).map((item, idx) => (
                  <div key={idx} style={{ marginBottom: 12 }}>
                    <div style={{ fontWeight: 700 }}>{item.year}</div>
                    <div style={{ color: "#37474f" }}>{item.event}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
