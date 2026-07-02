"""
generate_dataset.py
--------------------
Builds data/dataset.csv used to train FraudShield AI's models.

Columns:
    message     -> raw text message
    label       -> "Scam" or "Safe"
    fraud_type  -> category of fraud (or "Not Applicable" for Safe messages)

This is synthetic training data created for the Smart India Hackathon
prototype. For production use, replace/augment with real, consented,
anonymized complaint data (e.g. from cybercrime.gov.in style datasets).
"""

import csv
import random

random.seed(42)

banks = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "PNB", "Bank of Baroda", "Kotak Mahindra Bank", "Canara Bank"]
amounts = ["Rs. 25,000", "Rs. 1,00,000", "Rs. 50,000", "Rs. 10,000", "Rs. 2,50,000", "Rs. 5,000"]
links = ["http://bit.ly/verify-kyc", "http://sbi-secure-login.in", "http://kyc-update24.com",
         "http://hdfc-reward.net", "http://gov-refund.co.in", "http://income-tax-refund.xyz"]
names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohit", "Kavita"]
companies = ["Infosys", "TCS", "Amazon", "Reliance", "Wipro", "Flipkart"]

# ---------------- SCAM TEMPLATES ---------------- #

otp_fraud = [
    "Your {bank} account will be blocked. Share the OTP sent to your number immediately to avoid suspension.",
    "Dear customer, your ATM card is blocked. Share OTP received on your phone to reactivate it now.",
    "URGENT: {bank} KYC update pending. Share the 6 digit OTP now or your account will be frozen today.",
    "We detected suspicious login. Please share the OTP sent to your mobile to secure your {bank} account.",
    "Your account is temporarily locked. Reply with the OTP to verify your identity and unlock it.",
]

lottery_scam = [
    "Congratulations! You have won {amount} in the KBC Lucky Draw. Pay processing fee to claim your prize.",
    "You have been selected as the winner of Rs. 25,00,000 in Airtel Lucky Draw 2026. Contact us to claim.",
    "Dear winner, your mobile number has won a lottery of {amount}. Send your bank details to claim now.",
    "You've won a brand new iPhone in our anniversary lucky draw! Click the link to claim your free gift.",
    "Congrats! Your number won {amount} cash prize from Google Lucky Draw. Pay Rs.500 fee to release amount.",
]

job_scam = [
    "Work from home and earn {amount} per month! No experience needed, just pay Rs. 999 registration fee.",
    "{company} is hiring urgently. Deposit Rs. 2000 refundable security fee to confirm your job offer.",
    "Congratulations {name}, you are selected for a part-time job. Pay registration charges to start earning today.",
    "Earn Rs. 5000 daily by liking YouTube videos. Join now, small joining fee required for training kit.",
    "Get govt job without exam, pay Rs. 3500 processing fee and submit documents within 24 hours.",
]

loan_scam = [
    "Instant personal loan of {amount} approved! No documents required. Pay processing fee to disburse loan.",
    "Pre-approved loan of {amount} for {name}. Transfer Rs. 999 GST fee to release the amount instantly.",
    "Get a loan at 0% interest, {amount} approved for you. Send processing charges via UPI now.",
    "Your loan application is approved. Pay insurance amount of Rs.4999 to get funds credited today.",
]

kyc_scam = [
    "Your {bank} KYC has expired. Click {link} to update immediately or account will be suspended.",
    "Dear customer, complete your e-KYC at {link} within 24 hours to avoid permanent account block.",
    "RBI mandates KYC update. Verify your {bank} account at {link} now to continue banking services.",
    "Your Aadhaar linked bank account needs KYC verification. Visit {link} and enter your details now.",
]

phishing_scam = [
    "Your parcel is on hold due to unpaid customs duty. Pay Rs.199 at {link} to release delivery.",
    "Income tax refund of {amount} is pending. Claim it now at {link} before it expires today.",
    "Your electricity bill is unpaid, disconnection tonight. Pay immediately at {link} to avoid cut-off.",
    "Your PAN card will be deactivated. Update details at {link} within 2 hours to avoid penalty.",
]

investment_scam = [
    "Double your money in 7 days! Invest {amount} in our crypto trading plan, guaranteed high returns.",
    "Join our stock tips group, invest {amount} today and earn 300% guaranteed profit in one week.",
    "Exclusive IPO allotment guaranteed. Deposit {amount} now to secure your shares before it's too late.",
]

# ---------------- SAFE TEMPLATES ---------------- #

safe_msgs = [
    "Your {bank} account has been credited with {amount} on your salary date. Available balance updated.",
    "Dear {name}, your OTP for login is 482913. Do not share this with anyone. -{bank}",
    "Your order from {company} has been shipped and will arrive in 3-4 business days.",
    "Reminder: your electricity bill of Rs. 1200 is due on the 15th. Pay via official app or website.",
    "Hi {name}, your appointment with Dr. Sharma is confirmed for tomorrow at 5 PM.",
    "Your {bank} statement for last month is now available on net banking. Please review at your convenience.",
    "Thank you for shopping with {company}. Your invoice has been emailed to you.",
    "Your monthly mobile recharge of Rs. 299 was successful. Validity extended till next month.",
    "Meeting rescheduled to 3 PM tomorrow in conference room 2. Please confirm your availability.",
    "Your {bank} credit card bill of Rs. 3,450 is generated. Due date is the 20th of this month.",
    "Congratulations {name}, you have successfully completed your {company} certification course.",
    "Your PF balance has been updated. Login to the EPFO portal with your registered credentials to check.",
    "Hi, just checking if we are still on for lunch tomorrow at 1 PM?",
    "Your flight PNR is confirmed. Check-in opens 48 hours before departure. Have a safe journey.",
    "Reminder from school: parent-teacher meeting is scheduled this Saturday at 10 AM.",
]

fraud_categories = {
    "OTP Fraud": otp_fraud,
    "Lottery Scam": lottery_scam,
    "Job Scam": job_scam,
    "Loan Scam": loan_scam,
    "KYC Update Scam": kyc_scam,
    "Phishing Link": phishing_scam,
    "Investment Scam": investment_scam,
}

def fill(template):
    return template.format(
        bank=random.choice(banks),
        amount=random.choice(amounts),
        link=random.choice(links),
        name=random.choice(names),
        company=random.choice(companies),
    )

rows = []

# Generate scam rows (multiple variations per template)
for fraud_type, templates in fraud_categories.items():
    for t in templates:
        for _ in range(6):  # 6 variations each
            rows.append((fill(t), "Scam", fraud_type))

# Generate safe rows
for t in safe_msgs:
    for _ in range(8):
        rows.append((fill(t), "Safe", "Not Applicable"))

random.shuffle(rows)

with open("data/dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["message", "label", "fraud_type"])
    writer.writerows(rows)

print(f"Generated {len(rows)} rows -> data/dataset.csv")