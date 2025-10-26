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

# Page configuration
st.set_page_config(
    page_title="GateFlow Dashboard - SummitLogic",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    </style>
    """, unsafe_allow_html=True)

# Login / Logo area
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# Temporary toggle to allow public access to FlightCrew Home without login
PUBLIC_FLIGHTCREW_ACCESS = True

# Determine if this request should render the standalone FlightCrew page
try:
    _params = st.query_params
except Exception:
    _params = {}
_page = None
if _params:
    v = _params.get('page')
    if isinstance(v, list):
        _page = v[0] if v else None
    else:
        _page = v
IS_STANDALONE_FLIGHTCREW = (_page == 'flightcrew')



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
        imgs = "<div class='logo-center' style='display:flex; justify-content:center; gap:18px; align-items:center;'>"
        if uri1:
            imgs += f"<img src='{uri1}' width='320' alt='logo' style='max-height:120px; object-fit:contain;'/>"
        if uri2:
            imgs += f"<img src='{uri2}' width='320' alt='logo2' style='max-height:120px; object-fit:contain;'/>"
        imgs += "</div>"
        # Only show top logos if we are NOT rendering the standalone FlightCrew page
        if not IS_STANDALONE_FLIGHTCREW:
            st.markdown(imgs, unsafe_allow_html=True)
    else:
        if not IS_STANDALONE_FLIGHTCREW:
            st.markdown("<div class='logo-center'><img src='https://via.placeholder.com/400x80/1f77b4/ffffff?text=SummitLogic' width='400' alt='logo' /></div>", unsafe_allow_html=True)

# If the request is for the standalone FlightCrew page, render it here (using uri1/uri2) and stop further rendering
if IS_STANDALONE_FLIGHTCREW:
    # Build logo block for standalone page
    if uri1 or uri2:
        # Use a slightly different top margin depending on whether this is the standalone page
        if not IS_STANDALONE_FLIGHTCREW:
            top_margin = '-240px'  # pull logos slightly more up in the main app/tab
        else:
            top_margin = '-110px'   # lift logos slightly more in standalone view
        imgs = f"<div class='logo-center' style='display:flex; justify-content:center; gap:12px; align-items:center; margin-top:{top_margin};'>"
        if uri1:
            imgs += f"<img src='{uri1}' width='220' alt='logo' style='max-height:80px; object-fit:contain;'/>"
        if uri2:
            imgs += f"<img src='{uri2}' width='220' alt='logo2' style='max-height:80px; object-fit:contain;'/>"
        imgs += "</div>"
        # In standalone page we want to show the logos here as well
        st.markdown(imgs, unsafe_allow_html=True)
    else:
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
    st.markdown("## Acceso")
    tab_login, tab_register = st.tabs(["Iniciar sesión", "Registrarse"])

    with tab_login:
        login_id = st.text_input("Usuario o correo", value=st.session_state.get('username', ''), key='login_id')
        login_pw = st.text_input("Contraseña", type='password', key='login_pw')
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("Iniciar sesión", key='login_btn'):
                users = load_users()
                if users:
                    found = None
                    for u in users:
                        if u.get('username') == login_id or u.get('email') == login_id:
                            found = u
                            break
                    if not found:
                        st.error("Usuario no registrado. Por favor regístrate.")
                    else:
                        if found.get('password') == hash_password(login_pw):
                            st.session_state['logged_in'] = True
                            st.session_state['username'] = found.get('username')
                            st.session_state['role'] = found.get('role')
                            st.success(f"Bienvenido, {st.session_state['username']}!")
                            st.experimental_rerun()
                        else:
                            st.error("Credenciales inválidas.")
                else:
                    # no users registered yet - allow any non-empty for demo
                    if login_id.strip() and login_pw.strip():
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = login_id.strip()
                        st.success(f"Bienvenido, {st.session_state['username']}!")
                        st.experimental_rerun()
                    else:
                        st.error("Por favor ingresa usuario y contraseña.")

    with tab_register:
        reg_name = st.text_input("Nombre", key='reg_name')
        reg_last = st.text_input("Apellidos", key='reg_last')
        reg_email = st.text_input("Correo electrónico", key='reg_email')
        reg_username = st.text_input("Usuario (para inicio de sesión)", key='reg_username')
        # Use role labels without spaces as requested
        reg_role = st.selectbox("Rol", ["FlightCrew", "GroundCrew"], key='reg_role')
        reg_pw = st.text_input("Contraseña", type='password', key='reg_pw')
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("Registrarse", key='register_btn'):
                # basic validation
                if not (reg_name.strip() and reg_last.strip() and reg_email.strip() and reg_username.strip() and reg_pw.strip()):
                    st.error("Por favor completa todos los campos.")
                elif not _valid_email(reg_email.strip()):
                    st.error("Ingresa un correo válido.")
                else:
                    users = load_users()
                    # check duplicates
                    for u in users:
                        if u.get('username') == reg_username.strip():
                            st.error("El usuario ya existe. Elige otro usuario.")
                            break
                        if u.get('email') == reg_email.strip():
                            st.error("Ya existe una cuenta con ese correo.")
                            break
                    else:
                                    # Try to register via remote API first
                                    api_url = "https://summitlogicapidb-production.up.railway.app/api/auth/register"
                                    # The UI shows roles without spaces (FlightCrew/GroundCrew).
                                    # The server expects the human-readable values with a space.
                                    role_send_map = {
                                        "FlightCrew": "Flight Crew",
                                        "GroundCrew": "Ground Crew"
                                    }
                                    payload = {
                                        "firstName": reg_name.strip(),
                                        "lastName": reg_last.strip(),
                                        "email": reg_email.strip(),
                                        "username": reg_username.strip(),
                                        # translate to the server-expected form
                                        "role": role_send_map.get(reg_role, reg_role),
                                        "password": reg_pw.strip()
                                    }
                                    try:
                                        resp = requests.post(api_url, json=payload, timeout=10)
                                        if 200 <= resp.status_code < 300:
                                            st.success('Registro exitoso en el servidor. Ahora estás logueado.')
                                            st.session_state['logged_in'] = True
                                            st.session_state['username'] = reg_username.strip()
                                            st.session_state['role'] = reg_role
                                            # Optionally persist locally for offline fallback
                                            try:
                                                new_user = {
                                                    'username': reg_username.strip(),
                                                    'name': reg_name.strip(),
                                                    'last': reg_last.strip(),
                                                    'email': reg_email.strip(),
                                                    'role': reg_role,
                                                    'password': hash_password(reg_pw.strip())
                                                }
                                                users.append(new_user)
                                                save_users(users)
                                            except Exception:
                                                pass
                                            st.experimental_rerun()
                                        else:
                                            # try to extract message from server
                                            try:
                                                err = resp.json().get('message') or resp.text
                                            except Exception:
                                                err = resp.text
                                            st.error(f"Registro falló en el servidor: {err}")
                                    except Exception as e:
                                        st.warning(f"No se pudo conectar con el servidor de registro: {e}. Intentando guardado local...")
                                        # fallback to local registration
                                        new_user = {
                                            'username': reg_username.strip(),
                                            'name': reg_name.strip(),
                                            'last': reg_last.strip(),
                                            'email': reg_email.strip(),
                                            'role': reg_role,
                                            'password': hash_password(reg_pw.strip())
                                        }
                                        users.append(new_user)
                                        save_users(users)
                                        st.success('Registro local exitoso. Ahora estás logueado.')
                                        st.session_state['logged_in'] = True
                                        st.session_state['username'] = new_user['username']
                                        st.session_state['role'] = new_user['role']
                                        st.experimental_rerun()

    # stop further rendering until logged in (allow public FlightCrew if configured)
    if not st.session_state['logged_in'] and not PUBLIC_FLIGHTCREW_ACCESS:
        st.stop()

# The main app shows only the access UI (Iniciar sesión / Registrarse). The standalone FlightCrew
# page is still available at ?page=flightcrew but we remove the in-app FlightCrew tab and card.

# Sidebar
with st.sidebar:
    # Logout button
    if st.session_state.get('logged_in'):
        if st.button("Cerrar sesión"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ''
            st.experimental_rerun()

    st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=SummitLogic", use_column_width=True)
    st.markdown("---")
    
    st.subheader("About GateFlow")
    st.markdown("""
        GateFlow is SummitLogic's all-in-one application for galley operations, unifying:
        
        - 🍾 Alcohol bottle handling
        - ⚠️ Real-time error detection
        - 👥 Employee training & engagement
        
        Into a single role-aware experience.
    """)
    
    st.markdown("---")
    
    st.subheader("Key Benefits")
    st.success("✅ 20-30% waste reduction")
    st.success("✅ 50% fewer packing errors")
    st.success("✅ 30% faster employee ramp-up")
    st.success("✅ 20% throughput gain")
    
    st.markdown("---")
    
    st.subheader("Contact")
    st.info("📧 info@summitlogic.com")
    
    st.markdown("---")
    st.caption("© 2024 SummitLogic. All rights reserved.")