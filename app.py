
from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

TRON_WALLET = "TQeHa8VdwfyybxtioW4ggbnDC1rbWe8nFa"
MIN_AMOUNT = 0.5

@app.route("/check-payment", methods=["GET"])
def check_payment():
    url = f"https://api.trongrid.io/v1/accounts/{TRON_WALLET}/transactions/trc20?limit=10"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        recent_time = datetime.utcnow() - timedelta(minutes=30)
        for tx in data.get("data", []):
            value = int(tx.get("value", "0")) / (10 ** 6)  # USDT decimals = 6
            ts = datetime.fromtimestamp(tx["block_timestamp"] / 1000)
            if value >= MIN_AMOUNT and ts > recent_time:
                return jsonify({"access": "granted"})
        return jsonify({"access": "denied"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
