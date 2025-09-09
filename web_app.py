#!/usr/bin/env python3
"""
Azure AD Token Utility - Web UI Version
Provides a clean web interface for device code flow authentication.
"""

from flask import Flask, render_template, request, jsonify, session
import requests
import time
import os
import csv
import json
from typing import Dict, List, Optional
import threading
import uuid
import pickle

app = Flask(__name__)
app.secret_key = os.urandom(24)

DEVICE_CODE_URL = "https://login.microsoftonline.com/organizations/oauth2/v2.0/devicecode"
TOKEN_URL = "https://login.microsoftonline.com/organizations/oauth2/v2.0/token"

# Top 4 Microsoft applications
TOP_APPS = [
    {
        "name": "Microsoft Azure CLI",
        "client_id": "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
        "scope": "https://graph.microsoft.com/.default offline_access openid"
    },
    {
        "name": "Microsoft Teams",
        "client_id": "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
        "scope": "https://graph.microsoft.com/.default offline_access openid"
    },
    {
        "name": "Microsoft Outlook",
        "client_id": "5d661950-3475-41cd-a2c3-d671a3162bc1",
        "scope": "https://graph.microsoft.com/.default offline_access openid"
    },
    {
        "name": "Azure Active Directory PowerShell",
        "client_id": "1b730954-1685-4b74-9bfd-dac224a7b894",
        "scope": "https://graph.microsoft.com/.default offline_access openid"
    }
]

SESSION_FILE = os.path.join(os.path.dirname(__file__), 'active_sessions.pkl')

def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_sessions(sessions):
    with open(SESSION_FILE, 'wb') as f:
        pickle.dump(sessions, f)

def load_microsoft_apps() -> List[Dict]:
    """Load Microsoft applications from CSV file."""
    apps = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'MicrosoftApps.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('AppId') and row.get('AppDisplayName'):
                    apps.append({
                        'name': row['AppDisplayName'],
                        'client_id': row['AppId'],
                        'scope': "https://graph.microsoft.com/.default offline_access openid"
                    })
    except FileNotFoundError:
        print(f"Warning: MicrosoftApps.csv not found. Using only top 4 apps.")
    except Exception as e:
        print(f"Error loading apps: {e}")
    
    return apps

def get_device_code(client_id: str, scope: str) -> Dict:
    """Get device code from Azure AD."""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": client_id,
        "scope": scope
    }
    resp = requests.post(DEVICE_CODE_URL, data=data, headers=headers)
    resp.raise_for_status()
    return resp.json()

def poll_for_token(client_id: str, device_code: str, interval: int) -> Optional[Dict]:
    """Poll for access token."""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "client_id": client_id,
        "device_code": device_code
    }
    
    resp = requests.post(TOKEN_URL, data=data, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    elif resp.status_code == 400:
        error = resp.json().get("error")
        if error in ("authorization_pending", "slow_down"):
            return None  # Still waiting
        else:
            raise Exception(f"OAuth error: {resp.json()}")
    else:
        raise Exception(f"Unexpected error: {resp.text}")

def search_apps(apps: List[Dict], query: str) -> List[Dict]:
    """Search applications by name."""
    query = query.lower()
    return [app for app in apps if query in app['name'].lower()]

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html', top_apps=TOP_APPS)

@app.route('/api/search')
def api_search():
    """Search API endpoint."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    all_apps = load_microsoft_apps()
    results = search_apps(all_apps, query)
    
    # Limit results to first 50 for performance
    return jsonify(results[:50])

@app.route('/api/device-code', methods=['POST'])
def api_device_code():
    """Get device code endpoint."""
    data = request.get_json()
    client_id = data.get('client_id')
    scope = data.get('scope', 'https://graph.microsoft.com/.default offline_access openid')
    
    if not client_id:
        return jsonify({'error': 'Client ID is required'}), 400
    
    try:
        device = get_device_code(client_id, scope)
        
        # Generate session ID and store device info
        session_id = str(uuid.uuid4())
        active_sessions = load_sessions()
        active_sessions[session_id] = {
            'client_id': client_id,
            'device_code': device['device_code'],
            'interval': device.get('interval', 5),
            'expires_at': time.time() + device.get('expires_in', 900)
        }
        save_sessions(active_sessions)
        
        return jsonify({
            'session_id': session_id,
            'verification_uri': device['verification_uri'],
            'user_code': device['user_code'],
            'message': device['message']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/poll-token/<session_id>')
def api_poll_token(session_id):
    """Poll for token endpoint."""
    active_sessions = load_sessions()
    if session_id not in active_sessions:
        return jsonify({'error': 'Invalid session ID'}), 404
    
    session_data = active_sessions[session_id]
    
    # Check if session expired
    if time.time() > session_data['expires_at']:
        del active_sessions[session_id]
        save_sessions(active_sessions)
        return jsonify({'error': 'Session expired'}), 408
    
    try:
        token = poll_for_token(
            session_data['client_id'],
            session_data['device_code'],
            session_data['interval']
        )
        
        if token:
            # Clean up session
            del active_sessions[session_id]
            save_sessions(active_sessions)
            return jsonify({
                'access_token': token['access_token'],
                'refresh_token': token.get('refresh_token'),
                'id_token': token.get('id_token'),
                'expires_in': token.get('expires_in')
            })
        else:
            return jsonify({'status': 'pending'})
            
    except Exception as e:
        # Clean up session on error
        del active_sessions[session_id]
        save_sessions(active_sessions)
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-apps')
def api_top_apps():
    """Get top apps endpoint."""
    return jsonify(TOP_APPS)

@app.route('/api/scopes/<client_id>')
def api_scopes(client_id):
    """Return all scopes for a given client_id from the scope-map.txt file."""
    scope_map_path = os.path.join(os.path.dirname(__file__), 'data', 'scope-map.txt')
    scopes = set()
    try:
        with open(scope_map_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    scope, resource, client = parts[0], parts[1], parts[2]
                    if client.lower() == client_id.lower():
                        scopes.add(scope if scope.startswith('http') or scope.startswith('.') else resource)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(sorted(scopes))

if __name__ == '__main__':
    print("Starting Azure AD Token Utility Web Server...")
    print("Access the application at: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001) 