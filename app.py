"""
app.py
-------
Flask backend for FraudShield AI (AI Public Safety Intelligence Platform).

Routes:
    GET  /            -> chat UI (index.html)
    POST /predict      -> analyze a message, return AI result (JSON)
    GET  /history       -> last N analyzed messages (JSON)
    GET  /stats          -> quick dashboard stats (JSON)
"""

from flask import Flask, request, jsonify, render_template
import predict
import database

app = Flask(__name__)

# Initialize SQLite DB (creates table if not exists)
database.init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict_route():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Message text is required."}), 400

    try:
        result = predict.analyze_message(message)
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

    # Log to SQLite
    database.log_message(
        message=message,
        prediction=result["prediction"],
        fraud_type=result["fraud_type"],
        confidence=result["confidence"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
    )

    return jsonify(
        {
            "message": message,
            "scam_status": result["prediction"],       # "Scam" / "Safe"
            "fraud_type": result["fraud_type"],
            "confidence": result["confidence"],
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "advice": result["advice"],
            "emergency_steps": result["emergency_steps"],
        }
    )


@app.route("/history")
def history_route():
    limit = request.args.get("limit", default=50, type=int)
    return jsonify(database.get_history(limit=limit))


@app.route("/stats")
def stats_route():
    return jsonify(database.get_stats())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)