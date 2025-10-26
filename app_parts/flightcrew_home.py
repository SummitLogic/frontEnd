import streamlit as st
import os
import json
from datetime import datetime
from .flight_alcohol import render as render_alcohol
from .flight_inventory import render as render_inventory
from .flight_training import render as render_training
from .utils import safe_rerun


def render_flightcrew(uri1=None, uri2=None, standalone=True):
    role_label = 'Flight Crew'

    # Attempt to restore session_state from the persisted session file.
    try:
        from .utils import restore_session_state
        restore_session_state()
    except Exception:
        pass

# Only show logos if in standalone mode (when accessed via ?page=groundcrew)
    # When rendering inline (standalone=False), the main dashboard already shows logos
    if standalone and (uri1 or uri2):
        top_margin = '-110px'
        imgs = f"<div class='logo-center' style='display:flex; justify-content:center; gap:28px; align-items:center; margin-top:{top_margin};'>"
        if uri1:
            imgs += f"<img src='{uri1}' width='220' alt='logo' style='max-height:80px; object-fit:contain;'/>"
        if uri2:
            imgs += f"<img src='{uri2}' width='620' alt='logo2' style='max-height:190px; object-fit:contain; margin-top:28px;'/>"
        imgs += "</div>"
        st.markdown(imgs, unsafe_allow_html=True)
    elif standalone:
        # Fallback placeholder only in standalone mode
        st.markdown("<div class='logo-center'><img src='https://via.placeholder.com/400x80/1f77b4/ffffff?text=SummitLogic' width='400' alt='logo' /></div>", unsafe_allow_html=True)

    # Resolve full name from users.json if possible
    full_name = None
    # Prefer the stored user object from session_state (populated at login)
    sess_user = st.session_state.get('user')
    username_key = st.session_state.get('username')
    users_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'users.json')
    # If we have a session user from the API, use that first. Accept multiple key names
    if sess_user:
        # possible first name keys returned by different backends
        first = (sess_user.get('name') or sess_user.get('firstName') or sess_user.get('first') or sess_user.get('givenName') or '').strip()
        last = (sess_user.get('last') or sess_user.get('lastName') or sess_user.get('surname') or sess_user.get('familyName') or '').strip()
        if first or last:
            full_name = f"{first} {last}".strip()
        else:
            # fallback to displayName, fullName, username or email
            full_name = (sess_user.get('displayName') or sess_user.get('fullName') or sess_user.get('username') or sess_user.get('email'))
            if full_name:
                full_name = str(full_name).strip()
    elif username_key and os.path.exists(users_path):
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
        full_name = st.session_state.get('username') or '---'

    now = datetime.now()
    local_dt = now.strftime('%A, %d %B %Y — %H:%M')

    header_html = f"""
    <div style='position:relative; display:flex; justify-content:space-between; align-items:center; gap:12px; margin-top:12px;'>
      <div style='background:rgba(255,255,255,0.02); padding:18px; border-radius:10px;'>
        <h2 style='margin:0; color:var(--gold);'>Bienvenido de vuelta, {full_name}</h2>
        <div style='margin-top:6px; font-size:14px; color:var(--gold);'>
          <strong>Rol:</strong> {role_label}
        </div>
      </div>
      <div style='background:rgba(255,255,255,0.02); padding:12px 16px; border-radius:8px; text-align:right;'>
        <div style='font-weight:600; color:var(--gold);'>{local_dt}</div>
      </div>
          <!-- Top-right logout anchor -->
          <a href='?logout=1' style='position:absolute; top:8px; right:14px; display:inline-block; padding:8px 12px; background:rgba(255,255,255,0.03); border-radius:8px; color:var(--gold); text-decoration:none;'>Cerrar sesión</a>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown("---")

    if standalone:
        # Show links that navigate to standalone pages for each subpage
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <a href='?page=flightcrew&sub=alcohol' style='display:inline-block;padding:12px 18px;background:rgba(255,255,255,0.03);border-radius:8px;color:var(--gold);text-decoration:none;'>Alcohol</a>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <a href='?page=flightcrew&sub=inventario' style='display:inline-block;padding:12px 18px;background:rgba(255,255,255,0.03);border-radius:8px;color:var(--gold);text-decoration:none;'>Inventario</a>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <a href='?page=flightcrew&sub=entrenamiento' style='display:inline-block;padding:12px 18px;background:rgba(255,255,255,0.03);border-radius:8px;color:var(--gold);text-decoration:none;'>Entrenamiento</a>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("[Volver a la app principal](./)")
    else:
        # Render three tab-like links that navigate to standalone pages in the same tab.
        st.markdown("""
        <div style='display:flex; gap:8px;'>
          <a href='?page=flightcrew&sub=alcohol' role='tab' style='padding:10px 16px; background:rgba(255,255,255,0.03); border-radius:8px; color:var(--gold); text-decoration:none; font-weight:600;'>Alcohol</a>
          <a href='?page=flightcrew&sub=inventario' role='tab' style='padding:10px 16px; background:rgba(255,255,255,0.03); border-radius:8px; color:var(--gold); text-decoration:none; font-weight:600;'>Inventario</a>
          <a href='?page=flightcrew&sub=entrenamiento' role='tab' style='padding:10px 16px; background:rgba(255,255,255,0.03); border-radius:8px; color:var(--gold); text-decoration:none; font-weight:600;'>Entrenamiento</a>
        </div>
        <hr />
        <p style='color:var(--gold); margin-top:12px;'>Haz click en cualquiera de las pestañas para abrir la vista completa de esa sección.</p>
        """, unsafe_allow_html=True)
