import json
import sys
import traceback
from pathlib import Path
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'python': sys.version,
        'file': str(Path(__file__).resolve()),
    })

@app.route('/api/debug-boot')
def debug_boot():
    return jsonify({'boot': 'ok', 'minimal': True})
