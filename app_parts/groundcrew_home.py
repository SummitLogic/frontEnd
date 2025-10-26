import streamlit as st
import os
import json
import requests
from datetime import datetime
from .ground_alcohol import render as render_alcohol
from .ground_inventory import render as render_inventory
from .ground_training import render as render_training
from .utils import safe_rerun


def render_groundcrew(uri1=None, uri2=None, standalone=True):
    role_label = 'Ground Crew'

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
    sess_user = st.session_state.get('user')
    username_key = st.session_state.get('username')
    users_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'users.json')
    
    # Prefer session user object populated at login. Accept multiple key names
    if sess_user:
        first = (sess_user.get('name') or sess_user.get('firstName') or sess_user.get('first') or sess_user.get('givenName') or '').strip()
        last = (sess_user.get('last') or sess_user.get('lastName') or sess_user.get('surname') or sess_user.get('familyName') or '').strip()
        if first or last:
            full_name = f"{first} {last}".strip()
        else:
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

    # Header with welcome message and date/time - with logout button
    header_html = f"""
    <div style='position:relative; display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:24px;'>
      <div style='background:rgba(255,255,255,0.02); padding:18px 24px; border-radius:10px; flex:1;'>
        <h2 style='margin:0; color:var(--gold); font-size:24px;'>Bienvenido de vuelta, {full_name}</h2>
      </div>
      <div style='background:rgba(255,255,255,0.02); padding:18px 24px; border-radius:10px;'>
        <div style='font-weight:600; color:var(--gold); font-size:16px;'>{local_dt}</div>
      </div>
      <!-- Top-right logout anchor -->
      <a href='?logout=1' style='position:absolute; top:-40px; right:0; display:inline-block; padding:8px 16px; background:rgba(255,255,255,0.03); border-radius:8px; color:var(--gold); text-decoration:none; font-size:14px;'>Cerrar sesión</a>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # Create two-column layout: sidebar (left) and main content (right)
    col_sidebar, col_main = st.columns([1, 3])

    with col_sidebar:
        # Sidebar with upcoming flights
        st.markdown("""
        <div style='background:rgba(255,255,255,0.02); padding:20px; border-radius:10px; height:100%;'>
            <h3 style='color:var(--gold); margin-top:0; margin-bottom:20px;'>Próximos Vuelos</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Fetch upcoming flights from API
        token = st.session_state.get('token')
        upcoming_flights = get_upcoming_flights(token)
        
        if upcoming_flights:
            for flight in upcoming_flights:
                flight_html = f"""
                <div style='background:rgba(255,255,255,0.03); padding:12px; border-radius:8px; margin-bottom:12px;'>
                    <div style='color:var(--gold); font-weight:600; margin-bottom:4px;'>{flight.get('time', 'N/A')}</div>
                    <div style='color:var(--gold); font-size:14px;'>{flight.get('departure_city', 'N/A')} → {flight.get('destination_city', 'N/A')}</div>
                    <div style='color:var(--gold); font-size:12px; margin-top:4px;'>Tiempo de vuelo: {flight.get('flight_time', 'N/A')}</div>
                    <div style='color:var(--gold); font-size:12px;'>Vuelo: {flight.get('status', 'N/A')}</div>
                </div>
                """
                st.markdown(flight_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:rgba(255,255,255,0.03); padding:16px; border-radius:8px; margin-bottom:12px;'>
                <p style='color:var(--gold); margin:0; font-size:14px;'>No hay vuelos próximos</p>
            </div>
            """, unsafe_allow_html=True)

    with col_main:
        # Tab navigation
        st.markdown("""
        <div style='display:flex; gap:8px; margin-bottom:20px;'>
          <a href='?page=groundcrew&sub=alcohol' role='tab' style='padding:12px 20px; background:rgba(255,255,255,0.03); border-radius:8px; color:var(--gold); text-decoration:none; font-weight:600; text-align:center; flex:1;'>Alcohol</a>
          <a href='?page=groundcrew&sub=inventario' role='tab' style='padding:12px 20px; background:rgba(255,255,255,0.03); border-radius:8px; color:var(--gold); text-decoration:none; font-weight:600; text-align:center; flex:1;'>Inventario</a>
          <a href='?page=groundcrew&sub=entrenamiento' role='tab' style='padding:12px 20px; background:rgba(255,255,255,0.03); border-radius:8px; color:var(--gold); text-decoration:none; font-weight:600; text-align:center; flex:1;'>Entrenamiento</a>
        </div>
        """, unsafe_allow_html=True)
        
        # Main content area with weather and time info
        # Weather section
        st.markdown("""
        <div style='background:rgba(255,255,255,0.02); padding:20px; border-radius:10px; margin-bottom:16px;'>
            <h3 style='color:var(--gold); margin-top:0; margin-bottom:16px;'>Clima de ciudades destino</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Fetch weather data from API (placeholder for now)
        # TODO: Replace with actual API call to fetch weather
        weather_data = get_destination_weather()
        
        if weather_data:
            # Display weather in a grid
            weather_cols = st.columns(min(len(weather_data), 3))
            for idx, weather in enumerate(weather_data):
                with weather_cols[idx % 3]:
                    weather_html = f"""
                    <div style='background:rgba(255,255,255,0.03); padding:16px; border-radius:8px; text-align:center;'>
                        <div style='color:var(--gold); font-weight:600; font-size:16px; margin-bottom:8px;'>{weather.get('city', 'N/A')}</div>
                        <div style='color:var(--gold); font-size:24px; font-weight:bold; margin-bottom:4px;'>{weather.get('temp', 'N/A')}°C</div>
                        <div style='color:var(--gold); font-size:14px;'>{weather.get('condition', 'N/A')}</div>
                    </div>
                    """
                    st.markdown(weather_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:rgba(255,255,255,0.03); padding:16px; border-radius:8px;'>
                <p style='color:var(--gold); margin:0;'>No hay información de clima disponible</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Time section
        st.markdown("""
        <div style='background:rgba(255,255,255,0.02); padding:20px; border-radius:10px; margin-top:16px;'>
            <h3 style='color:var(--gold); margin-top:0; margin-bottom:16px;'>Hora de ciudades destino</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Fetch time data from API (placeholder for now)
        # TODO: Replace with actual API call to fetch city times
        time_data = get_destination_times()
        
        if time_data:
            # Display times in a grid
            time_cols = st.columns(min(len(time_data), 3))
            for idx, time_info in enumerate(time_data):
                with time_cols[idx % 3]:
                    time_html = f"""
                    <div style='background:rgba(255,255,255,0.03); padding:16px; border-radius:8px; text-align:center;'>
                        <div style='color:var(--gold); font-weight:600; font-size:16px; margin-bottom:8px;'>{time_info.get('city', 'N/A')}</div>
                        <div style='color:var(--gold); font-size:20px; font-weight:bold;'>{time_info.get('time', 'N/A')}</div>
                        <div style='color:var(--gold); font-size:12px; margin-top:4px;'>{time_info.get('timezone', 'N/A')}</div>
                    </div>
                    """
                    st.markdown(time_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:rgba(255,255,255,0.03); padding:16px; border-radius:8px;'>
                <p style='color:var(--gold); margin:0;'>No hay información de hora disponible</p>
            </div>
            """, unsafe_allow_html=True)

    # Link back to main app (only in standalone mode)
    if standalone:
        st.markdown("<hr style='margin-top:40px; margin-bottom:20px;' />", unsafe_allow_html=True)
        st.markdown("<a href='./' style='color:var(--gold); text-decoration:none;'>Volver a la app principal</a>", unsafe_allow_html=True)


def get_upcoming_flights(token=None):
    """
    Fetch upcoming flights from API/Database
    Returns list of flight dictionaries with real data from the flights table
    """
    api_url = "https://summitlogicapidb-production.up.railway.app/api/flights"
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        print(f"[DEBUG] Fetching flights from: {api_url}")
        print(f"[DEBUG] Headers: {headers}")
        
        # Fetch flights from API
        response = requests.get(api_url, headers=headers, timeout=10)
        
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Try to parse JSON
            try:
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    print(f"[WARNING] Unexpected content type: {content_type}")
                
                flights_data = response.json()
                print(f"[DEBUG] Parsed JSON successfully")
                print(f"[DEBUG] Data type: {type(flights_data)}")
                
                # Handle different response structures
                if isinstance(flights_data, dict):
                    # Check for common wrapper keys
                    flights_list = (
                        flights_data.get('flights') or 
                        flights_data.get('data') or 
                        flights_data.get('results') or
                        []
                    )
                    if not flights_list:
                        # If no wrapper key found, maybe the dict IS a single flight
                        if 'id' in flights_data or 'flight_number' in flights_data:
                            flights_list = [flights_data]
                        else:
                            print(f"[WARNING] Could not find flights in response. Keys: {flights_data.keys()}")
                            flights_list = []
                elif isinstance(flights_data, list):
                    flights_list = flights_data
                else:
                    print(f"[ERROR] Unexpected data type: {type(flights_data)}")
                    return []
                
                print(f"[DEBUG] Found {len(flights_list)} flights")
                if flights_list:
                    print(f"[DEBUG] First flight sample: {flights_list[0]}")
                
                # Parse and format the flight data
                formatted_flights = []
                for idx, flight in enumerate(flights_list):
                    if not isinstance(flight, dict):
                        print(f"[WARNING] Flight #{idx} is not a dict: {type(flight)}")
                        continue
                    
                    print(f"[DEBUG] Processing flight #{idx}: {flight.keys()}")
                    
                    # Parse scheduled_departure datetime
                    scheduled_departure = (
                        flight.get('scheduled_departure') or 
                        flight.get('scheduledDeparture') or
                        flight.get('departure_time')
                    )
                    departure_time = 'N/A'
                    flight_time_calc = 'N/A'
                    
                    if scheduled_departure:
                        try:
                            # Handle both datetime and date strings
                            if 'T' in str(scheduled_departure):
                                dt = datetime.fromisoformat(str(scheduled_departure).replace('Z', '+00:00'))
                            else:
                                # If it's just a date, assume midnight
                                dt = datetime.strptime(str(scheduled_departure), '%Y-%m-%d')
                            departure_time = dt.strftime('%H:%M')
                            
                            # Calculate flight time if arrival time exists
                            scheduled_arrival = (
                                flight.get('scheduled_arrival') or 
                                flight.get('scheduledArrival') or
                                flight.get('arrival_time')
                            )
                            if scheduled_arrival:
                                try:
                                    if 'T' in str(scheduled_arrival):
                                        arrival_dt = datetime.fromisoformat(str(scheduled_arrival).replace('Z', '+00:00'))
                                    else:
                                        arrival_dt = datetime.strptime(str(scheduled_arrival), '%Y-%m-%d')
                                    duration = arrival_dt - dt
                                    hours = duration.seconds // 3600
                                    minutes = (duration.seconds % 3600) // 60
                                    flight_time_calc = f'{hours}h {minutes}m'
                                except Exception as e:
                                    print(f"[WARNING] Error calculating flight time: {e}")
                        except Exception as e:
                            print(f"[WARNING] Error parsing departure time '{scheduled_departure}': {e}")
                    
                    # Try multiple possible field names for each value
                    departure_city = (
                        flight.get('departure_city') or 
                        flight.get('departureCity') or
                        flight.get('departure_airport') or
                        flight.get('origin') or
                        'N/A'
                    )
                    
                    arrival_city = (
                        flight.get('arrival_city') or 
                        flight.get('arrivalCity') or
                        flight.get('arrival_airport') or
                        flight.get('destination') or
                        'N/A'
                    )
                    
                    flight_number = (
                        flight.get('flight_number') or 
                        flight.get('flightNumber') or
                        flight.get('number') or
                        'N/A'
                    )
                    
                    formatted_flight = {
                        'time': departure_time,
                        'departure_city': departure_city,
                        'destination_city': arrival_city,
                        'flight_time': flight_time_calc,
                        'status': flight_number
                    }
                    formatted_flights.append(formatted_flight)
                    print(f"[DEBUG] Formatted flight #{idx}: {formatted_flight}")
                
                print(f"[DEBUG] Successfully formatted {len(formatted_flights)} flights")
                # Return only upcoming flights (limit to 5 most recent)
                return formatted_flights[:5]
                
            except ValueError as json_error:
                print(f"[ERROR] Failed to parse JSON: {json_error}")
                print(f"[ERROR] Response text (first 1000 chars): {response.text[:1000]}")
                return []
                
        elif response.status_code == 401:
            print(f"[ERROR] Unauthorized (401) - Token might be invalid or expired")
            return []
        elif response.status_code == 403:
            print(f"[ERROR] Forbidden (403) - You don't have permission to access this endpoint")
            return []
        elif response.status_code == 404:
            print(f"[ERROR] Not Found (404) - The endpoint /api/flights doesn't exist or returned no data")
            print(f"[ERROR] Response: {response.text[:500]}")
            return []
        else:
            print(f"[ERROR] Failed to fetch flights: HTTP {response.status_code}")
            print(f"[ERROR] Response: {response.text[:500]}")
            return []
            
    except requests.exceptions.Timeout:
        print(f"[ERROR] Request timeout when fetching flights")
        return []
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection error when fetching flights: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error fetching flights from API: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_destination_weather():
    """
    Fetch weather data for destination cities from API
    TODO: Replace with actual API call
    Returns list of weather dictionaries
    """
    # Placeholder data - replace with actual API call
    return [
        {'city': 'Cancún', 'temp': 28, 'condition': 'Soleado'},
        {'city': 'Guadalajara', 'temp': 24, 'condition': 'Parcialmente nublado'},
        {'city': 'Monterrey', 'temp': 22, 'condition': 'Despejado'}
    ]


def get_destination_times():
    """
    Fetch current times for destination cities from API
    TODO: Replace with actual API call
    Returns list of time dictionaries
    """
    # Placeholder data - replace with actual API call
    return [
        {'city': 'Cancún', 'time': '15:30', 'timezone': 'CST (UTC-6)'},
        {'city': 'Guadalajara', 'time': '14:30', 'timezone': 'CST (UTC-6)'},
        {'city': 'Monterrey', 'time': '15:30', 'timezone': 'CST (UTC-6)'}
    ]