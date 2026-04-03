from fastapi import FastAPI
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

# ✅ CORS (for Next.js frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ MongoDB connection
client = MongoClient("your connect string")  # 🔴 Replace with your Atlas URL
db = client["cardiac_db"]
collection = db["patients"]


# ✅ ROOT PAGE (for testing in browser)
@app.get("/")
def home():
    return """
    <html>
    <body style="font-family: Arial; padding:20px;">

        <h2>Cardiac Patient Monitor</h2>
        <div id="output">Loading...</div>

        <script>
        fetch("http://127.0.0.1:8000/patient/P001")
          .then(res => res.json())
          .then(data => {
            document.getElementById("output").innerHTML = `
              <h3>Patient: ${data.name}</h3>
              <p>Age: ${data.age}</p>

              <h4>Heart Rate Readings:</h4>
              <ul>
                ${data.heart_readings_display.map(r => `<li>${r}</li>`).join("")}
              </ul>

              <p><b>Average:</b> ${data.analysis.avg_bpm} bpm</p>
              <p><b>Min:</b> ${data.analysis.min_bpm} bpm</p>
              <p><b>Max:</b> ${data.analysis.max_bpm} bpm</p>
              <p><b>Variability:</b> ${data.analysis.variability}</p>
              <p><b>Risk:</b> ${data.analysis.risk_level}</p>
            `;
          });
        </script>

    </body>
    </html>
    """


# ✅ MAIN API ENDPOINT
@app.get("/patient/{patient_id}")
def get_patient(patient_id: str):

    patient = collection.find_one({"patient_id": patient_id}, {"_id": 0})

    if not patient:
        return {"error": "Patient not found"}

    heart_data = patient.get("heart_data", [])

    if not heart_data:
        return {**patient, "analysis": {}, "heart_readings_display": []}

    values = [d["value"] for d in heart_data]

    # ✅ ANALYSIS
    avg_bpm = round(np.mean(values), 2)
    max_bpm = max(values)
    min_bpm = min(values)
    variability = round(np.std(values), 2)

    # ✅ RISK LOGIC
    if avg_bpm > 100:
        risk = "High"
    elif avg_bpm > 85:
        risk = "Medium"
    else:
        risk = "Low"

    # ✅ FORMAT FOR DISPLAY
    heart_readings_display = [
        f"{d['timestamp']} → {d['value']} bpm"
        for d in heart_data
    ]

    return {
        **patient,
        "analysis": {
            "avg_bpm": avg_bpm,
            "max_bpm": max_bpm,
            "min_bpm": min_bpm,
            "variability": variability,
            "risk_level": risk
        },
        "heart_readings_display": heart_readings_display
    }
