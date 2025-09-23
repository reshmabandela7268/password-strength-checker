
from flask import Flask, request, jsonify, send_from_directory, abort
from password_strength import PasswordStats
import os
import secrets
import string

app = Flask(__name__, static_folder='.')

# List of common passwords
COMMON = {
    "123456", "password", "123456789", "12345678", "12345", "qwerty",
    "abc123", "111111", "iloveyou", "password1", "admin", "letmein", "welcome"
}

def make_suggestions(pw: str):
    stats = PasswordStats(pw)
    s = []
    if pw.lower() in COMMON:
        s.append("This password is very common — avoid it.")
    if stats.length < 12:
        s.append("Use at least 12 characters.")
    if not stats.has_uppercase():
        s.append("Add uppercase letters.")
    if not stats.has_lowercase():
        s.append("Add lowercase letters.")
    if not stats.has_numbers():
        s.append("Add digits (0-9).")
    if not stats.has_special():
        s.append("Add symbols (e.g. !@#$%).")
    if not s:
        s.append("Looks solid — consider using a password manager.")
    return s

def estimate_crack_times(entropy_bits: float):
    if entropy_bits <= 0:
        return {}
    avg_guesses = 2 ** (entropy_bits - 1)
    rates = {
        "online_throttled": 1e3,        # guesses per second
        "single_gpu": 1e8,
        "high_end_cluster": 1e11
    }
    out = {}
    for label, r in rates.items():
        seconds = avg_guesses / r
        out[label] = {
            "seconds": seconds,
            "readable": format_seconds(seconds),
            "rate": r
        }
    return out

def format_seconds(seconds: float) -> str:
    if seconds == float('inf'):
        return "∞"
    secs = int(round(seconds))
    if secs <= 0:
        return "0 seconds"
    intervals = (
        ('year', 31536000),
        ('day', 86400),
        ('hour', 3600),
        ('minute', 60),
        ('second', 1),
    )
    parts = []
    for name, count in intervals:
        if secs >= count:
            val = secs // count
            secs -= val * count
            parts.append(f"{val} {name}{'s' if val != 1 else ''}")
        if len(parts) >= 2:
            break
    return ', '.join(parts)

def generate_strong_passwords(count=3, length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.<>?"
    return [''.join(secrets.choice(alphabet) for _ in range(length)) for _ in range(count)]

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        return send_from_directory('.', filename)
    abort(404)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json(silent=True)
    if not data or 'password' not in data:
        return jsonify({'error': 'missing password'}), 400

    pw = data['password']
    stats = PasswordStats(pw)
    entropy = stats.entropy_bits
    score = stats.strength() * 100  # convert 0.0-1.0 to 0-100
    label = stats.strength_level

    suggestions = make_suggestions(pw)
    crack_times = estimate_crack_times(entropy)
    generated = generate_strong_passwords(3, max(12, min(20, stats.length + 4)))

    return jsonify({
        "length": stats.length,
        "entropy": entropy,
        "score": score,
        "label": label,
        "suggestions": suggestions,
        "crack_times": crack_times,
        "generated_passwords": generated
    })

if __name__ == '__main__':
    print(">>> Flask starting on http://127.0.0.1:5000")
    app.run(debug=True)
