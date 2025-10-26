import streamlit as st
import requests
from .utils import _valid_email, load_users, save_users, hash_password, safe_rerun
from .utils import save_session
import os


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
                    st.text_input("Usuario o correo", key='form_login_id')
                    st.text_input("Contraseña", type='password', key='form_login_pw')
                    submit_login = st.form_submit_button("Iniciar sesión")

                    if submit_login:
                        login_id = st.session_state.get('form_login_id', '').strip()
                        login_pw = st.session_state.get('form_login_pw', '').strip()
                        
                        if not login_id or not login_pw:
                            st.error("Por favor ingresa usuario y contraseña.")
                            st.stop()
                        
                        # Try remote login first
                        login_api = "https://summitlogicapidb-production.up.railway.app/api/auth/login"
                        remote_succeeded = False
                        
                        try:
                            payload = {"email": login_id, "password": login_pw}
                            resp = requests.post(login_api, json=payload, timeout=8)
                            
                            if 200 <= resp.status_code < 300:
                                data = resp.json() if resp.text else {}
                                token = data.get('token') or data.get('accessToken')
                                user = data.get('user') or data.get('data') or {}
                                server_role = user.get('role') if isinstance(user, dict) else None
                                target_page = 'groundcrew'
                                if server_role and 'flight' in server_role.lower():
                                    target_page = 'flightcrew'

                                # Set ALL session_state values
                                st.session_state['logged_in'] = True
                                st.session_state['username'] = user.get('username') or user.get('email') or login_id
                                st.session_state['role'] = server_role or ''
                                st.session_state['token'] = token
                                st.session_state['user'] = user
                                
                                # Persist session
                                try:
                                    save_session({
                                        'user': st.session_state['user'],
                                        'token': st.session_state['token'],
                                        'logged_in': True,
                                        'username': st.session_state['username'],
                                        'role': st.session_state['role']
                                    })
                                except Exception as e:
                                    print(f"Failed to save session: {e}")
                                
                                # Set query params and rerun
                                try:
                                    st.experimental_set_query_params(page=target_page)
                                except Exception:
                                    st.session_state['goto_page'] = target_page
                                
                                # Mark success and exit
                                remote_succeeded = True
                                safe_rerun()
                                st.stop()  # Prevent further execution
                            else:
                                # Remote auth failed - will try local
                                remote_succeeded = False
                        except Exception as e:
                            # Connection failed - will try local
                            print(f"Remote auth connection error: {e}")
                            remote_succeeded = False
                        
                        # Only try local auth if remote didn't succeed
                        if not remote_succeeded:
                            users = load_users()
                            if users:
                                found = None
                                for u in users:
                                    if u.get('username') == login_id or u.get('email') == login_id:
                                        found = u
                                        break
                                
                                if not found:
                                    st.error("Usuario no registrado. Por favor regístrate.")
                                elif found.get('password') == hash_password(login_pw):
                                    # Local auth successful
                                    st.session_state['logged_in'] = True
                                    st.session_state['username'] = found.get('username')
                                    st.session_state['role'] = found.get('role')
                                    st.session_state['user'] = {
                                        'username': found.get('username'),
                                        'email': found.get('email'),
                                        'name': found.get('name'),
                                        'last': found.get('last'),
                                        'role': found.get('role')
                                    }
                                    
                                    # Persist the session
                                    try:
                                        save_session({
                                            'user': st.session_state['user'],
                                            'token': st.session_state.get('token'),
                                            'logged_in': True,
                                            'username': st.session_state['username'],
                                            'role': st.session_state['role']
                                        })
                                    except Exception as e:
                                        print(f"Failed to save session: {e}")
                                    
                                    if found.get('role') and 'flight' in found.get('role').lower():
                                        try:
                                            st.experimental_set_query_params(page='flightcrew')
                                        except Exception:
                                            st.session_state['goto_page'] = 'flightcrew'
                                    else:
                                        try:
                                            st.experimental_set_query_params(page='groundcrew')
                                        except Exception:
                                            st.session_state['goto_page'] = 'groundcrew'
                                    safe_rerun()
                                    st.stop()
                                else:
                                    st.error("Credenciales inválidas.")
                            else:
                                # No users in local DB - demo mode
                                st.session_state['logged_in'] = True
                                st.session_state['username'] = login_id
                                st.session_state['user'] = {
                                    'username': login_id,
                                    'email': login_id,
                                    'name': login_id,
                                    'last': '',
                                    'role': 'GroundCrew'
                                }
                                try:
                                    save_session({
                                        'user': st.session_state['user'],
                                        'token': None,
                                        'logged_in': True,
                                        'username': st.session_state['username'],
                                        'role': st.session_state.get('role', 'GroundCrew')
                                    })
                                except Exception as e:
                                    print(f"Failed to save session: {e}")
                                safe_rerun()
                                st.stop()

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
                    if not (reg_name.strip() and reg_last.strip() and reg_email.strip() and reg_username.strip() and reg_pw.strip()):
                        st.error("Por favor completa todos los campos.")
                    elif not _valid_email(reg_email.strip()):
                        st.error("Ingresa un correo válido.")
                    else:
                        users = load_users()
                        for u in users:
                            if u.get('username') == reg_username.strip():
                                st.error("El usuario ya existe. Elige otro usuario.")
                                break
                            if u.get('email') == reg_email.strip():
                                st.error("Ya existe una cuenta con ese correo.")
                                break
                        else:
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
                                resp = requests.post(api_url, json=payload, timeout=10)
                                if 200 <= resp.status_code < 300:
                                    # Set ALL session_state values
                                    st.session_state['logged_in'] = True
                                    st.session_state['username'] = reg_username.strip()
                                    st.session_state['role'] = reg_role
                                    st.session_state['user'] = {
                                        'username': reg_username.strip(),
                                        'email': reg_email.strip(),
                                        'name': reg_name.strip(),
                                        'last': reg_last.strip(),
                                        'role': reg_role
                                    }
                                    
                                    # Persist the session
                                    try:
                                        save_session({
                                            'user': st.session_state['user'],
                                            'token': st.session_state.get('token'),
                                            'logged_in': True,
                                            'username': st.session_state['username'],
                                            'role': st.session_state['role']
                                        })
                                    except Exception as e:
                                        print(f"Failed to save session: {e}")
                                    
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
                                    except Exception:
                                        pass
                                    
                                    st.success('Registro exitoso en el servidor.')
                                    safe_rerun()
                                else:
                                    try:
                                        err = resp.json().get('message') or resp.text
                                    except Exception:
                                        err = resp.text
                                    st.error(f"Registro falló en el servidor: {err}")
                            except Exception as e:
                                st.warning(f"No se pudo conectar con el servidor de registro: {e}. Intentando guardado local...")
                                
                                # Set ALL session_state values
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
                                
                                st.session_state['logged_in'] = True
                                st.session_state['username'] = new_user['username']
                                st.session_state['role'] = new_user['role']
                                st.session_state['user'] = {
                                    'username': new_user['username'],
                                    'email': new_user.get('email'),
                                    'name': new_user.get('name'),
                                    'last': new_user.get('last'),
                                    'role': new_user.get('role')
                                }
                                
                                # Persist the session
                                try:
                                    save_session({
                                        'user': st.session_state['user'],
                                        'token': st.session_state.get('token'),
                                        'logged_in': True,
                                        'username': st.session_state['username'],
                                        'role': st.session_state['role']
                                    })
                                except Exception as e:
                                    print(f"Failed to save session: {e}")
                                
                                st.success('Registro local exitoso.')
                                safe_rerun()