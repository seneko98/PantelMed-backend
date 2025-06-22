from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient

app = Flask(__name__)

TRON_WALLET = "TQeHa8VdwfyybxtioW4ggbnDC1rbWe8nFa"
MIN_AMOUNT = 0.5

# підключення до MongoDB
MONGO_URI = "mongodb+srv://Vlad:manreds7@cluster0.d0qnz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["pantelmed"]
tx_collection = db["transactions"]

@app.route("/check-payment", methods=["GET"])
def check_payment():
    url = f"https://api.trongrid.io/v1/accounts/{TRON_WALLET}/transactions/trc20?limit=10"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        recent_time = datetime.utcnow() - timedelta(minutes=30)

        for tx in data.get("data", []):
            tx_id = tx.get("transaction_id")
            value = int(tx.get("value", "0")) / (10 ** 6)
            ts = datetime.fromtimestamp(tx["block_timestamp"] / 1000)

            # Умова: нова, достатня по сумі, свіжа транзакція
            if value >= MIN_AMOUNT and ts > recent_time:
                existing = tx_collection.find_one({"tx_id": tx_id})
                if existing:
                    continue  # транзакція вже використана

                # Нова транзакція — зберігаємо
                tx_collection.insert_one({
                    "tx_id": tx_id,
                    "amount": value,
                    "timestamp": ts,
                    "used": True
                })
                return jsonify({"access": "granted"})

        return jsonify({"access": "denied"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
