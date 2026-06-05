import os
import re
import time
import subprocess
import threading
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import psutil
import serial
import requests  

app = Flask(__name__)
app.secret_key = "aegis_super_secret_key_2026" 

# --- Core Configuration ---
LOG_FILE = "/var/log/secure"
MAX_ATTEMPTS = 5
BLOCKED_IPS = {}
STATUS = {
    "total_attacks": 0, 
    "blocked_count": 0, 
    "last_ip": "NONE", 
    "nmap_data": "Waiting...",
    "recent_logs": [], 
    "honeypot_alert": "SAFE (No Intrusion)",
    "attacker_mac": "UNKNOWN",
    "attacker_vendor": "UNKNOWN"
}

# --- Telegram Configuration ---
TELEGRAM_TOKEN = "8611882081:AAEBYR36GWfi8UbnvLiWZExgVITorlKtkC8"
TELEGRAM_CHAT_ID = "-1003561602080"

# --- Arduino Setup ---
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
except Exception as e:
    ser = None
    print(f"Warning: Arduino not connected or wrong port. Details: {e}")

# --- Telegram Alert Functions ---
def send_telegram_alert(ip):
    mac = STATUS.get("attacker_mac", "UNKNOWN")
    
    message = (
        f"🛡 *SECURITY ALERT* 🛡\n\n"
        f"🚨 *Status:* BLOCKED\n"
        f"🌐 *IP Address:* `{ip}`\n"
        f"🆔 *MAC Address:* `{mac}`\n"
        f"🔐 *Failed Login Attempts:* {MAX_ATTEMPTS}\n\n"
        f"⚠️ *Action Taken:*\n"
        f"The device has been temporarily blocked due to multiple failed authentication attempts.\n\n"
        f"🔎 Please verify if this activity is legitimate."
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        pass

# الدالة الخاصة بتقرير الاستخبارات على التليجرام
def send_telegram_intel_report(ip, nmap_data):
    message = (
        f"📊 *TARGET INTELLIGENCE REPORT* 📊\n\n"
        f"🎯 *Target Lock:* `{ip}`\n\n"
        f"{nmap_data}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        pass

def send_telegram_resolved_alert():
    message = (
        f"✅ *A.E.G.I.S SYSTEM UPDATE* ✅\n\n"
        f"🛡️ *Action:* System Disarmed Manually.\n"
        f"🟢 *Status:* Threat neutralized. System returned to Safe Mode."
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        pass

def send_telegram_honeypot_alert():
    message = (
        f"⚠️ *CRITICAL ALERT: HONEYPOT ACCESSED* ⚠️\n\n"
        f"🕵️ *Intruder Detected!*\n"
        f"📂 *Target:* `server_passwrds.txt` (Fake Passwords)\n\n"
        f"🚨 The attacker is exploring the system and reading files!"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        pass

# --- Active Defense Sequence (Tactical Delay & Clean Profiling) ---
def active_defense_sequence(ip):
    STATUS["last_ip"] = ip
    STATUS["nmap_data"] = f"Profiling target {ip}...\n"
    
    # --- المرحلة 1: سحب الماك أدريس أولاً ---
    try:
        arp_result = subprocess.check_output(['arp', '-n', ip]).decode('utf-8')
        mac_search = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", arp_result)
        if mac_search:
            mac_address = mac_search.group(0).upper()
            STATUS["attacker_mac"] = mac_address
            oui_map = {
                "00:0C:29": "VMware, Inc.",
                "08:00:27": "Oracle VirtualBox",
                "00:50:56": "VMware, Inc.",
                "52:54:00": "QEMU/KVM Virtual Machine",
                "DC:71:96": "Intel Corporate (HP)", 
                "88:B1:11": "Intel Corporate",
                "18:66:DA": "Dell Inc.",
                "3C:D9:2B": "Hewlett Packard",
                "A8:86:DD": "Apple, Inc.",
                "00:E0:4C": "Realtek (Asus/Acer/Lenovo)",
                "6C:C3:74": "Samsung Electronics",
                "B8:27:EB": "Raspberry Pi Foundation"
            }
            STATUS["attacker_vendor"] = oui_map.get(mac_address[:8], "LOCAL NETWORK DEVICE")
    except:
        pass

    # --- المرحلة 2: الإنذار الفوري ---
    if ser:
        ser.write(b'R') 
    STATUS["blocked_count"] += 1
    threading.Thread(target=send_telegram_alert, args=(ip,)).start()

    # --- المرحلة 3: سحب البورتات والـ OS مع تنظيف كامل للبيانات ---
    try:
        nmap_process = subprocess.run(
            ['sudo', 'nmap', '-O', '--osscan-guess', '-Pn', '-F', ip], 
            capture_output=True, text=True, timeout=30
        )
        raw_output = nmap_process.stdout
        
        ports_found = re.findall(r"(\d+/tcp\s+open\s+\S+)", raw_output)
        clean_data = "🔍 *OPEN PORTS FOUND:*\n"
        clean_data += ("\n".join(ports_found) if ports_found else "No accessible ports detected.")
        
        detected_os = None
        
        for line in raw_output.split('\n'):
            if line.startswith("OS details:"):
                detected_os = line.replace("OS details:", "").strip()
                break
            elif line.startswith("Aggressive OS guesses:"):
                full_guess = line.replace("Aggressive OS guesses:", "").strip()
                detected_os = full_guess.split(',')[0].strip()
                break
            elif line.startswith("Running:"):
                detected_os = line.replace("Running:", "").strip()
                break
                
        if detected_os:
            clean_data += f"\n\n🖥️ *DETECTED OS:*\n`{detected_os}`"
        else:
            if "445/tcp" in raw_output or "135/tcp" in raw_output:
                clean_data += "\n\n🖥️ *DETECTED OS:*\n`Microsoft Windows (Heuristic Match)`"
            elif "22/tcp" in raw_output:
                clean_data += "\n\n🖥️ *DETECTED OS:*\n`Linux / Unix-based (Heuristic Match)`"
            else:
                clean_data += "\n\n🖥️ *DETECTED OS:*\n`Unknown System (Stealthy)`"
        
        STATUS["nmap_data"] = clean_data
        # إرسال رسالة التليجرام التانية (التقرير الاستخباراتي) فوراً بعد تنظيف البيانات
        threading.Thread(target=send_telegram_intel_report, args=(ip, clean_data)).start()

    except Exception as e:
        STATUS["nmap_data"] = "Target profiling completed with limited OS data."

    # --- المرحلة 4: الحظر الفعلي (Firewall Rule) ---
    try:
        subprocess.run(['sudo', 'firewall-cmd', '--add-rich-rule', f'rule family="ipv4" source address="{ip}" reject'], check=True)
        subprocess.run(['sudo', 'firewall-cmd', '--runtime-to-permanent'], check=True)
        STATUS["nmap_data"] += "\n\n🛡️ [SYSTEM ACTION]: Firewall rule applied. Attacker isolated."
    except Exception as e:
        print(f"Error blocking IP: {e}")

# --- Honeypot Monitor (Threaded) ---
def monitor_honeypot():
    log_file = "/var/log/audit/audit.log"
    try:
        with open(log_file, "r") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                
                if "HONEYPOT_TRIPPED" in line and "success=yes" in line:
                    STATUS["honeypot_alert"] = "⚠️ BREACHED! (File Read by Attacker)"
                    threading.Thread(target=send_telegram_honeypot_alert).start()
                    if ser:
                        ser.write(b'R') 
                    time.sleep(10)
    except Exception as e:
        print(f"Audit Log Error: {e}")

# --- Log Monitor (Threaded) ---
def monitor_logs():
    print("A.E.G.I.S Security Monitor Started...")
    try:
        initial_logs = subprocess.check_output(['tail', '-n', '5', LOG_FILE]).decode('utf-8')
        STATUS["recent_logs"] = [line for line in initial_logs.split('\n') if line.strip()]
    except:
        STATUS["recent_logs"] = ["System initializing... waiting for logs."]

    with open(LOG_FILE, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            clean_line = line.strip()
            if clean_line:
                STATUS["recent_logs"].append(clean_line)
                if len(STATUS["recent_logs"]) > 10:
                    STATUS["recent_logs"].pop(0)

                if "Failed password" in clean_line:
                    ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', clean_line)
                    if ip_match:
                        ip = ip_match.group(1)
                        STATUS["total_attacks"] += 1
                        BLOCKED_IPS[ip] = BLOCKED_IPS.get(ip, 0) + 1
                        
                        if BLOCKED_IPS[ip] == MAX_ATTEMPTS:
                            threading.Thread(target=active_defense_sequence, args=(ip,)).start()

# --- Flask API & Routing ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'aegis_soc' and password == 'Aeg!s@Soc#':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid ID or Passcode. Access Denied.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
    except:
        cpu = 0
        ram = 0

    return jsonify({
        "cpu": cpu,
        "ram": ram,
        "total_attacks": STATUS["total_attacks"],
        "blocked_count": STATUS["blocked_count"],
        "last_ip": STATUS["last_ip"],
        "nmap_data": STATUS["nmap_data"],
        "logs": STATUS["recent_logs"],
        "honeypot_alert": STATUS["honeypot_alert"],
        "attacker_mac": STATUS["attacker_mac"],
        "attacker_vendor": STATUS["attacker_vendor"]
    })

@app.route('/api/disarm', methods=['POST'])
def disarm_system():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    if ser:
        ser.write(b'S') 
        
    STATUS["blocked_count"] = 0 
    STATUS["honeypot_alert"] = "SAFE (No Intrusion)"
    
    STATUS["attacker_mac"] = "UNKNOWN"
    STATUS["attacker_vendor"] = "UNKNOWN"
    
    threading.Thread(target=send_telegram_resolved_alert).start()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    threading.Thread(target=monitor_logs, daemon=True).start()
    threading.Thread(target=monitor_honeypot, daemon=True).start() 
    app.run(host='0.0.0.0', port=5000, debug=False)