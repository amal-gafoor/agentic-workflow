import os
import json
from config import SESSION_DIR, MAX_HISTORY

os.makedirs(SESSION_DIR,exist_ok=True)

def get_path(user_id):
    return os.path.join(SESSION_DIR, f"{user_id}.json")

def default_session():
    return {
        'history': [],
        'order': {
            'state': 'idle',
            'data': {}
        }
    }

def load_memory(user_id):
    path = get_path(user_id)

    if not os.path.exists(path):
        return default_session()
                
    try:
        with open(path,'r') as f:
            session= json.load(f)

        if 'history' not in session:
            session['history'] = []
        if 'order' not in session:
            session ['order'] = {'state': 'idle','data': {}}

        return session
        
            
    except Exception as e:
        print(f"[MEMORY LOAD ERROR] {e}")
        return session

def save_memory(user_id,session):
    path = get_path(user_id)

    try:
        # Keep only the last MAX_HISTORY items
        if 'history' in session and len(session['history']) > MAX_HISTORY:
            session['history'] = session['history'][-MAX_HISTORY:]

        with open(path,'w') as f:
            json.dump(session,f,indent=2)

    except Exception as e:
        print(f"[MEMORY ERROR] {e}")