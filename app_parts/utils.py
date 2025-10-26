
import os
import base64
import json
import hashlib
import re
import time
import streamlit as st


def _img_data_uri(path, mime='png'):
    try:
        with open(path, 'rb') as f:
            data = f.read()
            b64 = base64.b64encode(data).decode('utf-8')
            return f"data:image/{mime};base64,{b64}"
    except Exception:
        return None


def _users_file_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'users.json')


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def load_users():
    path = _users_file_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_users(users_list):
    path = _users_file_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(users_list, f, ensure_ascii=False, indent=2)


def _valid_email(email: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def safe_rerun():
    try:
        if hasattr(st, 'experimental_rerun') and callable(st.experimental_rerun):
            st.experimental_rerun()
            return
    except Exception:
        pass

    try:
        if hasattr(st, 'experimental_get_query_params') and hasattr(st, 'experimental_set_query_params'):
            params = st.experimental_get_query_params() or {}
            params['_r'] = int(time.time())
            st.experimental_set_query_params(**params)
            st.stop()
            return
    except Exception:
        pass

    try:
        st.stop()
    except Exception:
        pass


def _session_file_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'session.json')


def save_session(session_obj: dict):
    """Save a small session blob to disk (local development fallback).

    session_obj should be JSON-serializable. This is used to persist the
    logged-in user/token across full page reloads during development.
    """
    # Don't write an empty/null session blob. Use clear_session() to remove the
    # on-disk session when logging out. This prevents accidental overwrites
    # where a None/empty user would replace a valid persisted session.
    if not session_obj or not isinstance(session_obj, dict):
        return
    user = session_obj.get('user')
    # Only persist when we have a non-empty user object
    if not user:
        return
    path = _session_file_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(session_obj, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_session():
    path = _session_file_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None


def clear_session():
    path = _session_file_path()
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def restore_session_state():
    """Ensure st.session_state contains user/token/logged_in by loading the
    persisted session file if present. Safe to call repeatedly.
    """
    try:
        # Only attempt if session not already populated
        if not st.session_state.get('logged_in') or not st.session_state.get('user'):
            sess = load_session()
            if sess and isinstance(sess, dict):
                user = sess.get('user')
                token = sess.get('token')
                if user:
                    st.session_state['user'] = user
                    st.session_state['username'] = user.get('username') or user.get('email') or st.session_state.get('username')
                    st.session_state['role'] = user.get('role') or st.session_state.get('role')
                    if token:
                        st.session_state['token'] = token
                    st.session_state['logged_in'] = True
    except Exception:
        pass
