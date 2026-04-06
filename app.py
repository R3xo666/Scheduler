from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# Very simple in-memory storage for 1 user (Adi).
# If restarting Render, the data resets, but for daily tracking it's fine.
last_ping = None
offline_periods = []

@app.route('/ping', methods=['POST'])
def ping():
    global last_ping, offline_periods
    now = datetime.datetime.now()
    
    if last_ping:
        diff = (now - last_ping).total_seconds() / 60.0
        # If the script was OFF for more than 15 minutes, log it.
        if diff > 15:
            offline_periods.append({
                "start": last_ping.isoformat(),
                "end": now.isoformat(),
                "duration_mins": round(diff)
            })
            
    last_ping = now
    return jsonify({"status": "ok", "time": now.isoformat()})

@app.route('/report', methods=['GET'])
def report():
    global offline_periods
    res = list(offline_periods)
    offline_periods.clear()  # Clear after reading
    return jsonify({"offline_periods": res})

if __name__ == '__main__':
    # Used for local testing, Render uses gunicorn
    app.run(host='0.0.0.0', port=5000)