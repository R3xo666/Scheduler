"""
ADI TRACKER — Render.com Backend Server
Flask server for uptime tracking + event logging
Deploy this on Render.com (free tier)
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json, os
from pathlib import Path

app = Flask(__name__)
LOG_FILE = Path("events.log")

def log_event(data):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

@app.route("/")
def home():
    return jsonify({"status": "Adi Tracker running!", "time": datetime.now().isoformat()})

@app.route("/ping", methods=["POST"])
def ping():
    data = request.json or {}
    data["received_at"] = datetime.now().isoformat()
    log_event(data)
    return jsonify({"ok": True})

@app.route("/events", methods=["GET"])
def events():
    """Get today's events"""
    date = request.args.get("date", datetime.now().date().isoformat())
    out = []
    if LOG_FILE.exists():
        for line in LOG_FILE.read_text().splitlines():
            try:
                e = json.loads(line)
                if e.get("date") == date:
                    out.append(e)
            except: pass
    return jsonify({"date": date, "events": out, "count": len(out)})

@app.route("/status", methods=["GET"])
def status():
    """Quick status check — last heartbeat"""
    if not LOG_FILE.exists():
        return jsonify({"status": "no_data"})
    hbs = []
    for line in LOG_FILE.read_text().splitlines():
        try:
            e = json.loads(line)
            if e.get("event") in ("heartbeat", "boot"):
                hbs.append(e)
        except: pass
    last = hbs[-1] if hbs else None
    return jsonify({"last_event": last, "total_events": len(hbs)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
