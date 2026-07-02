"""
predict.py
-----------
Core AI inference module for FraudShield AI.

Loads the trained TF-IDF vectorizer + Logistic Regression models and
exposes analyze_message(text) which returns a full structured result:

    {
        "prediction": "Scam" | "Safe",
        "fraud_type": str,
        "confidence": float (0-100),
        "risk_score": int (0-100),
        "risk_level": "Low" | "Medium" | "High" | "Critical",
        "advice": str,          # persona-driven explanation, <=150 words
        "emergency_steps": [str, ...]
    }

Persona rules implemented here (Cyber Crime Assistant for India):
  - Never hallucinate: every explanation is derived directly from the
    model's prediction/fraud_type, not invented facts.
  - If Scam: explain Why, Risk, Safety Tips, Government Advice.
  - If Safe: explain why it appears safe.
  - Professional tone, max 150 words.
  - Always ends with the fixed safety reminder line.
"""

import os
import joblib

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")

_vectorizer = joblib.load(os.path.join(MODEL_DIR, "vectorizer.pkl"))
_label_model = joblib.load(os.path.join(MODEL_DIR, "label_model.pkl"))
_type_model = joblib.load(os.path.join(MODEL_DIR, "type_model.pkl"))

SAFETY_LINE = "Stay alert. Never share OTP, PIN, passwords or transfer money under pressure."

# ---------------------------------------------------------------- #
# Fraud-type specific knowledge base (used for "Why", tips, advice)
# ---------------------------------------------------------------- #
FRAUD_INFO = {
    "OTP Fraud": {
        "why": "the message pressures you to share a one-time password (OTP), a tactic scammers use to hijack bank accounts or cards.",
        "tips": "Banks and RBI never ask for OTP over call, SMS or chat. Never share your OTP with anyone, even someone claiming to be bank staff.",
        "gov_advice": "Report immediately on the National Cyber Crime Portal (cybercrime.gov.in) or call the Cyber Crime Helpline 1930.",
        "severity": 0.95,
    },
    "Lottery Scam": {
        "why": "it claims you won a prize you never entered for, and asks for an upfront fee — a classic advance-fee lottery fraud pattern.",
        "tips": "Genuine lotteries never ask winners to pay a fee to release winnings. Do not share bank or personal details.",
        "gov_advice": "Do not respond or pay. Report the number/link at cybercrime.gov.in or call 1930.",
        "severity": 0.85,
    },
    "Job Scam": {
        "why": "it offers unrealistic income for minimal work and demands a registration or security fee before hiring, a common fake-job tactic.",
        "tips": "Legitimate employers never charge job seekers a fee. Verify company details independently before paying anything.",
        "gov_advice": "Report the offer on cybercrime.gov.in and verify company legitimacy via its official website.",
        "severity": 0.8,
    },
    "Loan Scam": {
        "why": "it promises an instant, no-document loan and asks for an upfront 'processing fee' — a hallmark of fraudulent loan apps/agents.",
        "tips": "RBI-registered lenders deduct processing fees from the loan amount, never ask for it upfront via UPI.",
        "gov_advice": "Verify lender registration on the RBI website and report suspicious apps at cybercrime.gov.in.",
        "severity": 0.85,
    },
    "KYC Update Scam": {
        "why": "it creates urgency around KYC/account suspension and pushes you to click a link and enter banking credentials.",
        "tips": "Never update KYC via SMS/WhatsApp links. Visit your bank's official app, website, or branch only.",
        "gov_advice": "Report phishing links to your bank's official fraud helpline and cybercrime.gov.in.",
        "severity": 0.9,
    },
    "Phishing Link": {
        "why": "it uses urgency (unpaid dues, refunds, deactivation) to make you click a suspicious link and enter sensitive information.",
        "tips": "Do not click unknown links. Verify by visiting the official website directly by typing the URL yourself.",
        "gov_advice": "Report the URL to cybercrime.gov.in; you may also flag it to Google Safe Browsing.",
        "severity": 0.85,
    },
    "Investment Scam": {
        "why": "it guarantees unrealistically high returns in a short time, a key indicator of Ponzi-style investment fraud.",
        "tips": "No legitimate investment guarantees fixed high returns. Verify SEBI registration before investing.",
        "gov_advice": "Verify the entity on the SEBI website and report at cybercrime.gov.in if suspicious.",
        "severity": 0.9,
    },
    "Not Applicable": {
        "why": "the message does not show pressure tactics, requests for OTP/PIN, suspicious links, or unrealistic offers.",
        "tips": "Continue standard precautions: never share OTP/PIN with anyone and verify unfamiliar senders.",
        "gov_advice": "No action needed. If in doubt, verify directly with the concerned bank/organisation via official channels.",
        "severity": 0.1,
    },
}

EMERGENCY_STEPS_SCAM = [
    "Do NOT click any link, share OTP/PIN, or make any payment.",
    "Block and report the sender's number immediately.",
    "If money was already transferred, call the Cyber Crime Helpline 1930 within the golden hour.",
    "File a complaint at the National Cyber Crime Reporting Portal: cybercrime.gov.in.",
    "Inform your bank's official fraud helpline to freeze suspicious transactions.",
]

EMERGENCY_STEPS_SAFE = [
    "No immediate action required.",
    "Still verify the sender if anything feels unusual.",
    "Never share OTP/PIN even for messages that look genuine.",
]


def _risk_level(risk_score: int) -> str:
    if risk_score >= 80:
        return "Critical"
    if risk_score >= 55:
        return "High"
    if risk_score >= 30:
        return "Medium"
    return "Low"


def _build_advice(prediction: str, fraud_type: str) -> str:
    """Builds a persona-compliant, <=150 word advisory string."""
    info = FRAUD_INFO.get(fraud_type, FRAUD_INFO["Not Applicable"])

    if prediction == "Scam":
        advice = (
            f"This message has been classified as a likely SCAM ({fraud_type}). "
            f"Why: {info['why']} "
            f"Risk: Engaging with this message may lead to financial loss or identity theft. "
            f"Safety Tips: {info['tips']} "
            f"Government Advice: {info['gov_advice']}"
        )
    else:
        advice = (
            f"This message appears SAFE. It does not match known fraud patterns "
            f"because {info['why']} No urgent action or payment is being demanded, "
            f"and no OTP/PIN is requested. {info['tips']}"
        )

    # Enforce 150-word cap
    words = advice.split()
    if len(words) > 150:
        advice = " ".join(words[:150]).rstrip(",.") + "..."

    return f"{advice}\n\n{SAFETY_LINE}"


def analyze_message(message: str) -> dict:
    if not message or not message.strip():
        raise ValueError("Message text is empty.")

    X = _vectorizer.transform([message])

    # --- Scam / Safe prediction --- #
    label_pred = _label_model.predict(X)[0]
    label_proba = _label_model.predict_proba(X)[0]
    label_classes = list(_label_model.classes_)
    confidence = float(max(label_proba)) * 100

    # --- Fraud type prediction (only meaningful if Scam) --- #
    if label_pred == "Scam":
        type_pred = _type_model.predict(X)[0]
        type_proba = _type_model.predict_proba(X)[0]
        type_confidence = float(max(type_proba)) * 100
    else:
        type_pred = "Not Applicable"
        type_confidence = 100.0

    info = FRAUD_INFO.get(type_pred, FRAUD_INFO["Not Applicable"])

    # --- Risk score: blends model confidence with category severity --- #
    if label_pred == "Scam":
        risk_score = int(round(confidence * info["severity"]))
        risk_score = max(risk_score, 40)  # any confirmed scam is at least Medium-High
    else:
        risk_score = int(round((100 - confidence) * 0.3))

    risk_score = min(max(risk_score, 0), 100)
    risk_level = _risk_level(risk_score)

    advice = _build_advice(label_pred, type_pred)
    emergency_steps = EMERGENCY_STEPS_SCAM if label_pred == "Scam" else EMERGENCY_STEPS_SAFE

    return {
        "prediction": label_pred,
        "fraud_type": type_pred,
        "confidence": round(confidence, 2),
        "type_confidence": round(type_confidence, 2),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "advice": advice,
        "emergency_steps": emergency_steps,
    }


if __name__ == "__main__":
    # Quick manual test
    samples = [
        "Your SBI account will be blocked. Share the OTP sent to your number immediately.",
        "Your order from Amazon has been shipped and will arrive in 3-4 business days.",
    ]
    for s in samples:
        print(s)
        print(analyze_message(s))
        print("-" * 60)