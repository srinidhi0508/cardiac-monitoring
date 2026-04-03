from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
import random
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cardiacai_secret'

socketio = SocketIO(app)


# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return render_template("home.html")  # Your original homepage

@app.route("/select-login")
def select_login():
    return render_template("select_login.html")

@app.route("/patient_login", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        return redirect(url_for("patient_dashboard"))
    return render_template("patient_login.html")


@app.route("/doctor_login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        return redirect(url_for("doctor_dashboard"))
    return render_template("doctor_login.html")


@app.route("/patient_dashboard")
def patient_dashboard():
    return render_template("patient_dashboard.html")


@app.route("/doctor_dashboard")
def doctor_dashboard():
    return render_template("doctor_dashboard.html")


# -----------------------------
# REAL-TIME HEART SYSTEM
# -----------------------------

def heart_monitor():
    while True:
        heart_rate = random.randint(50, 140)

        if heart_rate > 120:
            diagnosis = "Tachycardia"
            recommendation = "High heart rate detected. Please relax, drink water, and avoid stress."
        elif heart_rate < 60:
            diagnosis = "Bradycardia"
            recommendation = "Low heart rate. Sit down and monitor condition carefully."
        else:
            diagnosis = "Normal"
            recommendation = "Heart rate normal. Continue regular activities."

        socketio.emit("heart_update", {
            "value": heart_rate,
            "diagnosis": diagnosis,
            "recommendation": recommendation
        })

        time.sleep(3)


thread = threading.Thread(target=heart_monitor)
thread.daemon = True
thread.start()


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    socketio.run(app, debug=True)