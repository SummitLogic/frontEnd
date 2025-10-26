import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import json
import hashlib
import re
from datetime import datetime
import requests
import time
from app_parts.login_page import render_login
from app_parts.flightcrew_home import render_flightcrew
from app_parts.groundcrew_home import render_groundcrew

# Subpage modules (standalone)
from app_parts.flight_alcohol import render as render_flight_alcohol
from app_parts.flight_inventory import render as render_flight_inventory
from app_parts.flight_training import render as render_flight_training
from app_parts.ground_alcohol import render as render_ground_alcohol
from app_parts.ground_inventory import render as render_ground_inventory
from app_parts.ground_training import render as render_ground_training

# Page configuration
st.set_page_config(
    page_title="GateFlow Dashboard - SummitLogic",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state defaults to avoid KeyError when accessed later
for _k, _v in {
    'logged_in': False,
    'username': '',
    'role': '',
    'token': None,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Try to restore persisted session (local fallback) if available and session not already logged in
try:
    from app_parts.utils import load_session
    if not st.session_state.get('logged_in'):
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


def safe_rerun():
    """Attempt to rerun the Streamlit script in a way that's compatible across
    Streamlit versions. Prefer `st.experimental_rerun()` when available. As a
    fallback, toggle a query parameter and call `st.stop()` to trigger a reload.
    """
    try:
        if hasattr(st, 'experimental_rerun') and callable(st.experimental_rerun):
            st.experimental_rerun()
            return
    except Exception:
        pass

    # Fallback: toggle a timestamp query param to force a rerun
    try:
        if hasattr(st, 'experimental_get_query_params') and hasattr(st, 'experimental_set_query_params'):
            params = st.experimental_get_query_params() or {}
            params['_r'] = int(time.time())
            st.experimental_set_query_params(**params)
            # Stop execution so Streamlit will reload the script with new params
            st.stop()
            return
    except Exception:
        pass

    # Last-resort: attempt to stop the script
    try:
        st.stop()
    except Exception:
        pass

# Custom CSS: force pure black background and golden text across the app
# Gold color: rgb(166,151,109)
# Custom CSS: force pure black background and golden text across the app
# Gold color: rgb(166,151,109)
st.markdown("""
    <style>
    :root { --gold: rgb(166,151,109); }

    /* Primary containers */
    html, body, .stApp, .stApp>div, .block-container, .main, .reportview-container {
        background: #000000 !important;
        color: var(--gold) !important;
    }

    /* Sidebar and header/footer */
    .stSidebar, .css-1d391kg, .css-1v3fvcr, header, footer {
        background: #000000 !important;
        color: var(--gold) !important;
    }

    /* Ensure any Streamlit generated containers use dark background */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .css-18e3th9, .css-1d391kg {
        background: #000000 !important;
        color: var(--gold) !important;
    }

    /* Logo container centered */
    .logo-center { text-align: center; padding: 10px 0; }
    .logo-center img { display:block; margin: 0 auto; }

    /* Metric card styling to match dark theme */
    .metric-card {
        background-color: rgba(255,255,255,0.02) !important;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid var(--gold) !important;
        color: var(--gold) !important;
    }

    /* Tabs and headers */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 50px; padding-left: 20px; padding-right: 20px; color: var(--gold) !important; }
    h1, h2, h3, h4, h5, h6, p, span, label, div, a {
        color: var(--gold) !important;
    }

    /* Buttons and inputs: make text gold on dark */
    .stButton>button, .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        color: var(--gold) !important;
        background-color: rgba(255,255,255,0.03) !important;
        border-color: rgba(255,255,255,0.08) !important;
    }

    /* Prevent placeholder images from adding bright backgrounds */
    img[alt="logo"] { background-color: transparent !important; }
    /* Hide the Streamlit left sidebar entirely (app-wide) */
    [data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# Determine if this request should render the standalone FlightCrew/GroundCrew page
try:
    _params = st.query_params
except Exception:
    _params = {}
# If the user clicked the logout anchor (?logout=1), perform a full reset:
# - remove persisted session file
# - clear all session_state entries
# - clear query params and rerun so the app returns to the initial access screen
try:
    if _params and ('logout' in _params or _params.get('logout')):
        try:
            from app_parts.utils import clear_session
            clear_session()
        except Exception:
            pass

        # Safely remove all session_state keys to fully reset the app state
        try:
            keys = list(st.session_state.keys())
            for k in keys:
                del st.session_state[k]
        except Exception:
            # Best-effort: clear common keys if full clear fails
            for _k in ('logged_in', 'username', 'role', 'token', 'user', 'goto_page'):
                if _k in st.session_state:
                    del st.session_state[_k]

        try:
            # clear URL params
            st.experimental_set_query_params()
        except Exception:
            pass

        # Force a rerun so the app initializes as if freshly started
        try:
            if hasattr(st, 'experimental_rerun'):
                st.experimental_rerun()
        except Exception:
            try:
                st.stop()
            except Exception:
                pass
        try:
            st.stop()
        except Exception:
            pass
except Exception:
    pass
_page = None
if _params:
    v = _params.get('page')
    if isinstance(v, list):
        _page = v[0] if v else None
    else:
        _page = v
_sub = None
if _params:
    s = _params.get('sub')
    if isinstance(s, list):
        _sub = s[0] if s else None
    else:
        _sub = s
# Support programmatic navigation set via session_state['goto_page'] as a fallback
if not _page and st.session_state.get('goto_page'):
    _page = st.session_state.pop('goto_page', None)
IS_STANDALONE_FLIGHTCREW = (_page == 'flightcrew')
IS_STANDALONE_GROUNDCREW = (_page == 'groundcrew')
IS_STANDALONE = IS_STANDALONE_FLIGHTCREW or IS_STANDALONE_GROUNDCREW
# Configuration toggles
# When True, FlightCrew UI is publicly accessible without logging in
PUBLIC_FLIGHTCREW_ACCESS = False
# Logo display (centered). The app will use `assets/logo.png` or `assets/logo.jpg` if present.
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    assets_logo_path = os.path.join(assets_dir, 'logo.png')
    assets_logo_jpg = os.path.join(assets_dir, 'logo.jpg')

    def _img_data_uri(path, mime='png'):
        try:
            with open(path, 'rb') as f:
                data = f.read()
                b64 = base64.b64encode(data).decode('utf-8')
                return f"data:image/{mime};base64,{b64}"
        except Exception:
            return None

    # Support two persistent logos: logo.png (primary) and logo2.png (secondary)
    uri1 = None
    uri2 = None
    if os.path.exists(assets_logo_path):
        uri1 = _img_data_uri(assets_logo_path, 'png')
    elif os.path.exists(assets_logo_jpg):
        uri1 = _img_data_uri(assets_logo_jpg, 'jpeg')

    assets_logo2_path = os.path.join(assets_dir, 'logo2.png')
    assets_logo2_jpg = os.path.join(assets_dir, 'logo2.jpg')
    if os.path.exists(assets_logo2_path):
        uri2 = _img_data_uri(assets_logo2_path, 'png')
    elif os.path.exists(assets_logo2_jpg):
        uri2 = _img_data_uri(assets_logo2_jpg, 'jpeg')

    if uri1 or uri2:
        # show both logos side-by-side when available
        imgs = "<div class='logo-center' style='display:flex; justify-content:center; gap:40px; align-items:center;'>"
        if uri1:
            imgs += f"<img src='{uri1}' width='320' alt='logo' style='max-height:120px; object-fit:contain;'/>"
        if uri2:
            # Make logo2 larger than the primary logo on the access screen and nudge it down
            # Increased margin-top by 20px as requested
            imgs += f"<img src='{uri2}' width='770' alt='logo2' style='max-height:230px; object-fit:contain; margin-top:32px;'/>"
        imgs += "</div>"
        # Only show top logos if we are NOT rendering any standalone page
        if not IS_STANDALONE:
            st.markdown(imgs, unsafe_allow_html=True)
    else:
        if not IS_STANDALONE_FLIGHTCREW:
            st.markdown("<div class='logo-center'><img src='https://via.placeholder.com/400x80/1f77b4/ffffff?text=SummitLogic' width='400' alt='logo' /></div>", unsafe_allow_html=True)

# If request is for a standalone crew page, delegate to the appropriate renderer
if IS_STANDALONE_FLIGHTCREW or IS_STANDALONE_GROUNDCREW:
    # If a subpage is requested (e.g. ?page=flightcrew&sub=alcohol), render that standalone subpage
    if _sub:
        sub = (_sub or '').lower()
        if IS_STANDALONE_FLIGHTCREW:
            if sub == 'alcohol':
                render_flight_alcohol()
            elif sub in ('inventario', 'inventory', 'inv'):
                render_flight_inventory()
            elif sub in ('entrenamiento', 'training', 'trn'):
                render_flight_training()
            else:
                # Unknown subpage: fall back to flightcrew home
                render_flightcrew(uri1, uri2)
        else:
            # groundcrew subpages
            if sub == 'alcohol':
                render_ground_alcohol()
            elif sub in ('inventario', 'inventory', 'inv'):
                render_ground_inventory()
            elif sub in ('entrenamiento', 'training', 'trn'):
                render_ground_training()
            else:
                render_groundcrew(uri1, uri2)
    else:
<<<<<<< HEAD
        # No sub requested: render the crew home
        if IS_STANDALONE_FLIGHTCREW:
            render_flightcrew(uri1, uri2)
        else:
            render_groundcrew(uri1, uri2)
    # When rendering a standalone crew page (home or a subpage) we must stop
    # further execution so the login/access UI below does not render under it.
    try:
        st.stop()
    except Exception:
        # If st.stop() is not available for some Streamlit version, just return
        pass
=======
        st.markdown("<div class='logo-center'><img src='https://via.placeholder.com/400x80/1f77b4/ffffff?text=SummitLogic' width='400' alt='logo' /></div>", unsafe_allow_html=True)

    # Top header: left = welcome box, right = local date/time
    # Resolve full name from users.json if possible
    full_name = None
    username_key = st.session_state.get('username')
    users_path = os.path.join(os.path.dirname(__file__), 'data', 'users.json')
    if username_key and os.path.exists(users_path):
        try:
            with open(users_path, 'r', encoding='utf-8') as uf:
                all_users = json.load(uf)
                for u in all_users:
                    if u.get('username') == username_key or u.get('email') == username_key:
                        first = u.get('name', '').strip()
                        last = u.get('last', '').strip()
                        if first or last:
                            full_name = f"{first} {last}".strip()
                        break
        except Exception:
            full_name = None

    if not full_name:
        # fallback to username or placeholder
        full_name = st.session_state.get('username') or '---'

    # local date/time
    now = datetime.now()
    local_dt = now.strftime('%A, %d %B %Y — %H:%M')

    # render header with welcome and clock
    header_html = f"""
    <div style='display:flex; justify-content:space-between; align-items:center; gap:12px; margin-top:12px;'>
      <div style='background:rgba(255,255,255,0.02); padding:18px; border-radius:10px;'>
        <h2 style='margin:0; color:var(--gold);'>Bienvenido de vuelta, {full_name}</h2>
      </div>
      <div style='background:rgba(255,255,255,0.02); padding:12px 16px; border-radius:8px; text-align:right;'>
        <div style='font-weight:600; color:var(--gold);'>{local_dt}</div>
      </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.button("Ver manifiesto de vuelo")
    with c2:
        st.button("Reporte rápido de galley")
    st.markdown("---")
    st.markdown("[Volver a la app principal](./)")
    st.stop()
>>>>>>> 822a55df5934cef6daa169ff82b1385e6cfa0b3a

# Note: removed experimental_get_query_params usage per deprecation; FlightCrew UI is provided as an inline tab below.

# Login form
def _users_file_path():
    return os.path.join(os.path.dirname(__file__), 'data', 'users.json')

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


if not st.session_state['logged_in']:
    # Delegate the login/register UI to the modular page
    render_login(uri1=uri1, uri2=uri2, is_standalone=IS_STANDALONE, public_flight_access=PUBLIC_FLIGHTCREW_ACCESS)

    # Registration UI moved to `app_parts.login_page.render_login`

    # stop further rendering until logged in (allow public FlightCrew if configured)
    if not st.session_state['logged_in'] and not PUBLIC_FLIGHTCREW_ACCESS:
        st.stop()

# The main app shows only the access UI (Iniciar sesión / Registrarse). The standalone FlightCrew
# page is still available at ?page=flightcrew but we remove the in-app FlightCrew tab and card.

# Sidebar
# Sidebar removed: UI simplified to a single main column. Sidebar content intentionally omitted.


def main():
    """Entry point for running this module as a script.

    Preferred usage is via Streamlit:
        streamlit run gategroupDashboard.py

    If the module is executed directly with plain `python`, this function
    will print a short instruction and exit. When executed by Streamlit the
    app runs as normal (Streamlit imports and executes the module contents).
    """
    import sys

    # If the process looks like Streamlit, do nothing (Streamlit already ran the script)
    argv0 = sys.argv[0].lower() if sys.argv else ''
    if 'streamlit' in argv0 or any('streamlit' in a.lower() for a in sys.argv):
        return

    print("This script is intended to be run with Streamlit.")
    print("Run with:")
    print("  streamlit run gategroupDashboard.py")
    print("or from the project root:")
    print("  streamlit run /Users/rigo/Desktop/frontEnd/gategroupDashboard.py")


if __name__ == '__main__':
    main()