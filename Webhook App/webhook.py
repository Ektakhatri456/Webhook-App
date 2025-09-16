import os
from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage
import random
import string

webhook_app = Flask(__name__)

# Read email config from environment variables
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_SUBJECT = os.environ.get("EMAIL_SUBJECT")

def send_license_email(to_email: str, license_key: str):
    msg = EmailMessage()
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(f"Thank you for your purchase!\n\nYour license key is:\n\n{license_key}\n\nKeep it safe.")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"License email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

@webhook_app.route("/gumroad-webhook", methods=["POST"])
def gumroad_webhook():
    data = request.form or request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    buyer_email = data.get("email")
    if not buyer_email:
        return jsonify({"error": "No buyer email found"}), 400
    
    ok, license_key = add_license()
    if not ok:
        return jsonify({"error": "Failed to generate license key"}), 500

    send_license_email(buyer_email, license_key)

    return jsonify({"message": "License generated and emailed", "license_key": license_key}), 200

def add_license():
    try:
        # Generate a random 16-character license key (alphanumeric)
        license_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        
        # TODO: Save license_key to your database or file here if needed
        
        return True, license_key
    except Exception as e:
        print(f"Error generating license key: {e}")
        return False, None
    

if __name__ == "__main__":
    webhook_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    