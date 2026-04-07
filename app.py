from flask import Flask, request, jsonify
import datetime, json, os

app = Flask(__name__)

STORE_FILE = "/tmp/hb_state.json"

def load_state():
    if os.path.exists(STORE_FILE):
        try:
            return json.loads(open(STORE_FILE).read())
        except: pass
    return {"last_ping": None, "offline_periods": []}

def save_state(state):
    try:
        with open(STORE_FILE, "w") as f:
            json.dump(state, f)
    except: pass

@app.route('/ping', methods=['POST'])
def ping():
    state = load_state()
    now = datetime.datetime.utcnow()
    now_iso = now.isoformat()

    if state["last_ping"]:
        try:
            last = datetime.datetime.fromisoformat(state["last_ping"])
            diff = (now - last).total_seconds() / 60.0
            # If more than 15 mins gap → offline period
            if diff > 15:
                state["offline_periods"].append({
                    "start": state["last_ping"],
                    "end": now_iso,
                    "duration_mins": round(diff)
                })
        except: pass

    state["last_ping"] = now_iso
    save_state(state)
    return jsonify({"status": "ok", "time": now_iso})

@app.route('/report', methods=['GET'])
def report():
    state = load_state()
    periods = list(state.get("offline_periods", []))
    state["offline_periods"] = []   # Clear after reading
    save_state(state)
    return jsonify({"offline_periods": periods})

@app.route('/health', methods=['GET'])
def health():
    state = load_state()
    return jsonify({"last_ping": state.get("last_ping"), "pending_offline": len(state.get("offline_periods",[]))})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
