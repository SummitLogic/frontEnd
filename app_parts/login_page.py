import streamlit as st
import requests
from .utils import _valid_email, load_users, save_users, hash_password, safe_rerun
from .utils import save_session
import os


def authenticate_remote(login_id, login_pw):
    """Attempt remote authentication using email. Returns (success, user_data, token, error_msg)"""
    login_api = "https://summitlogicapidb-production.up.railway.app/api/auth/login"
    
    try:
        # API requires email and password fields
        payload = {"email": login_id, "password": login_pw}
        
        # Debug: Print what we're sending
        print(f"[DEBUG] Login attempt - API: {login_api}")
        print(f"[DEBUG] Payload: {payload}")
        
        resp = requests.post(login_api, json=payload, timeout=8)
        
        # Debug: Print response
        print(f"[DEBUG] Response Status: {resp.status_code}")
        print(f"[DEBUG] Response Body: {resp.text[:500]}")  # First 500 chars
        
        if 200 <= resp.status_code < 300:
            data = resp.json() if resp.text else {}
            token = data.get('token') or data.get('accessToken') or data.get('access_token')
            user = data.get('user') or data.get('data') or {}
            
            # Debug: Print parsed data
            print(f"[DEBUG] Parsed token: {token}")
            print(f"[DEBUG] Parsed user: {user}")
            
            if user and isinstance(user, dict):
                return (True, user, token, None)
            else:
                return (False, None, None, "Respuesta inválida del servidor")
        else:
            try:
                error_data = resp.json()
                error_msg = error_data.get('message') or error_data.get('error') or resp.text
            except Exception:
                error_msg = f"Error {resp.status_code}: {resp.text[:200]}"
            print(f"[DEBUG] Authentication failed: {error_msg}")
            return (False, None, None, error_msg)
    except requests.exceptions.Timeout:
        return (False, None, None, "Tiempo de espera agotado")
    except requests.exceptions.ConnectionError:
        return (False, None, None, "No se pudo conectar al servidor")
    except Exception as e:
        print(f"[DEBUG] Exception: {str(e)}")
        return (False, None, None, f"Error de conexión: {str(e)}")


def authenticate_local(login_id, login_pw):
    """Attempt local authentication using email. Returns (success, user_data, error_msg)"""
    users = load_users()
    
    if not users:
        return (False, None, "No hay usuarios registrados localmente")
    
    found = None
    for u in users:
        if u.get('email') == login_id:
            found = u
            break
    
    if not found:
        return (False, None, "Email no encontrado")
    
    if found.get('password') != hash_password(login_pw):
        return (False, None, "Contraseña incorrecta")
    
    # Successful local auth
    user_data = {
        'username': found.get('username'),
        'email': found.get('email'),
        'name': found.get('name'),
        'last': found.get('last'),
        'role': found.get('role')
    }
    return (True, user_data, None)


def set_user_session(user_data, token=None):
    """Set all session state variables for a logged-in user"""
    server_role = user_data.get('role', '')
    
    st.session_state['logged_in'] = True
    st.session_state['username'] = user_data.get('username') or user_data.get('email')
    st.session_state['role'] = server_role
    st.session_state['token'] = token
    st.session_state['user'] = user_data
    
    # Persist session
    try:
        save_session({
            'user': user_data,
            'token': token,
            'logged_in': True,
            'username': st.session_state['username'],
            'role': server_role
        })
    except Exception as e:
        print(f"Failed to save session: {e}")
    
    # Determine target page
    if server_role and 'flight' in server_role.lower():
        target_page = 'flightcrew'
    else:
        target_page = 'groundcrew'
    
    # Set navigation
    try:
        st.experimental_set_query_params(page=target_page)
    except Exception:
        st.session_state['goto_page'] = target_page


def render_login(uri1=None, uri2=None, is_standalone=False, public_flight_access=False):
    """Render the access UI (login + register). Designed to be called from the main app."""
    # Center the access block and make it narrow
    lcol, mcol, rcol = st.columns([1, 2, 1])
    with mcol:
        st.markdown("<div style='max-width:520px; margin:0 auto; text-align:center;'><h2 style=\'margin-bottom:6px;\'>Acceso</h2></div>", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["Iniciar sesión", "Registrarse"])

        with tab_login:
            # Form-based login (single click)
            lcol2, mcol2, rcol2 = st.columns([1, 2, 1])
            with mcol2:
                with st.form(key='login_form'):
                    st.text_input("Correo electrónico", key='form_login_id')
                    st.text_input("Contraseña", type='password', key='form_login_pw')
                    submit_login = st.form_submit_button("Iniciar sesión")

                    if submit_login:
                        login_id = st.session_state.get('form_login_id', '').strip()
                        login_pw = st.session_state.get('form_login_pw', '').strip()
                        
                        # Validate input
                        if not login_id or not login_pw:
                            st.error("Por favor ingresa correo electrónico y contraseña.")
                        else:
                            # Try remote authentication first
                            with st.spinner("Autenticando..."):
                                success, user_data, token, error_msg = authenticate_remote(login_id, login_pw)
                            
                            if success:
                                # Remote authentication successful
                                set_user_session(user_data, token)
                                st.success(f"¡Bienvenido, {user_data.get('name', login_id)}!")
                                safe_rerun()
                            else:
                                # Remote failed - try local authentication
                                local_success, local_user, local_error = authenticate_local(login_id, login_pw)
                                
                                if local_success:
                                    # Local authentication successful
                                    set_user_session(local_user)
                                    st.success(f"¡Bienvenido, {local_user.get('name', login_id)}!")
                                    safe_rerun()
                                else:
                                    # Both failed - show error
                                    if error_msg and ("No se pudo conectar" in error_msg or "Tiempo de espera" in error_msg):
                                        # Server unreachable - show local error
                                        st.error(f"Error de conexión al servidor. {local_error}")
                                    else:
                                        # Server reachable but auth failed
                                        st.error(f"Credenciales inválidas. Por favor verifica tu correo electrónico y contraseña.")

        with tab_register:
            lcol2, mcol2, rcol2 = st.columns([1, 2, 1])
            with mcol2:
                reg_name = st.text_input("Nombre", key='reg_name')
                reg_last = st.text_input("Apellidos", key='reg_last')
                reg_email = st.text_input("Correo electrónico", key='reg_email')
                reg_username = st.text_input("Usuario (para inicio de sesión)", key='reg_username')
                reg_role = st.selectbox("Rol", ["FlightCrew", "GroundCrew"], key='reg_role')
                reg_pw = st.text_input("Contraseña", type='password', key='reg_pw')
                
                if st.button("Registrarse", key='register_btn'):
                    # Validate input
                    if not (reg_name.strip() and reg_last.strip() and reg_email.strip() and reg_username.strip() and reg_pw.strip()):
                        st.error("Por favor completa todos los campos.")
                    elif not _valid_email(reg_email.strip()):
                        st.error("Ingresa un correo válido.")
                    else:
                        # Check if user exists locally
                        users = load_users()
                        user_exists = False
                        for u in users:
                            if u.get('username') == reg_username.strip():
                                st.error("El usuario ya existe. Elige otro usuario.")
                                user_exists = True
                                break
                            if u.get('email') == reg_email.strip():
                                st.error("Ya existe una cuenta con ese correo.")
                                user_exists = True
                                break
                        
                        if not user_exists:
                            # Try remote registration
                            api_url = "https://summitlogicapidb-production.up.railway.app/api/auth/register"
                            role_send_map = {"FlightCrew": "Flight Crew", "GroundCrew": "Ground Crew"}
                            payload = {
                                "firstName": reg_name.strip(),
                                "lastName": reg_last.strip(),
                                "email": reg_email.strip(),
                                "username": reg_username.strip(),
                                "role": role_send_map.get(reg_role, reg_role),
                                "password": reg_pw.strip()
                            }
                            
                            try:
                                with st.spinner("Registrando..."):
                                    resp = requests.post(api_url, json=payload, timeout=10)
                                
                                if 200 <= resp.status_code < 300:
                                    # Remote registration successful
                                    user_data = {
                                        'username': reg_username.strip(),
                                        'email': reg_email.strip(),
                                        'name': reg_name.strip(),
                                        'last': reg_last.strip(),
                                        'role': reg_role
                                    }
                                    set_user_session(user_data)
                                    
                                    # Save local backup
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
                                    except Exception as e:
                                        print(f"Failed to save local backup: {e}")
                                    
                                    st.success('¡Registro exitoso!')
                                    safe_rerun()
                                else:
                                    try:
                                        err = resp.json().get('message') or resp.text
                                    except Exception:
                                        err = resp.text
                                    st.error(f"Registro falló: {err}")
                            except Exception as e:
                                # Remote registration failed - save locally
                                st.warning(f"No se pudo conectar al servidor. Guardando localmente...")
                                
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
                                
                                user_data = {
                                    'username': new_user['username'],
                                    'email': new_user.get('email'),
                                    'name': new_user.get('name'),
                                    'last': new_user.get('last'),
                                    'role': new_user.get('role')
                                }
                                set_user_session(user_data)
                                
                                st.success('Registro local exitoso.')
                                safe_rerun()