import json
import hashlib
import os

AUTH_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'auth.json')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def admin_exists():
    if not os.path.exists(AUTH_PATH):
        return False
    with open(AUTH_PATH, 'r') as f:
        data = json.load(f)
    return len(data.get('users', [])) > 0

def create_admin(username, password, nama_penuh):
    users = []
    if os.path.exists(AUTH_PATH):
        with open(AUTH_PATH, 'r') as f:
            data = json.load(f)
            users = data.get('users', [])
    users.append({
        'username': username.lower().strip(),
        'password': hash_password(password),
        'nama_penuh': nama_penuh,
        'role': 'admin'
    })
    os.makedirs(os.path.dirname(AUTH_PATH), exist_ok=True)
    with open(AUTH_PATH, 'w') as f:
        json.dump({'users': users}, f, indent=2)
    return True

def tambah_user(username, password, nama_penuh, role='staff'):
    if not os.path.exists(AUTH_PATH):
        return False, "Tiada admin lagi"
    with open(AUTH_PATH, 'r') as f:
        data = json.load(f)
    users = data.get('users', [])
    for u in users:
        if u['username'] == username.lower().strip():
            return False, "Username sudah wujud"
    users.append({
        'username': username.lower().strip(),
        'password': hash_password(password),
        'nama_penuh': nama_penuh,
        'role': role
    })
    with open(AUTH_PATH, 'w') as f:
        json.dump({'users': users}, f, indent=2)
    return True, "User berjaya ditambah"

def semua_users():
    if not os.path.exists(AUTH_PATH):
        return []
    with open(AUTH_PATH, 'r') as f:
        data = json.load(f)
    return [{'username': u['username'], 'nama_penuh': u['nama_penuh'], 'role': u['role']}
            for u in data.get('users', [])]

def padam_user(username):
    if not os.path.exists(AUTH_PATH):
        return False
    with open(AUTH_PATH, 'r') as f:
        data = json.load(f)
    users = [u for u in data.get('users', []) if u['username'] != username.lower().strip()]
    with open(AUTH_PATH, 'w') as f:
        json.dump({'users': users}, f, indent=2)
    return True

def login(username, password):
    if not os.path.exists(AUTH_PATH):
        return False, None
    with open(AUTH_PATH, 'r') as f:
        data = json.load(f)
    for user in data.get('users', []):
        if (user['username'] == username.lower().strip() and
                user['password'] == hash_password(password)):
            return True, user
    return False, None
