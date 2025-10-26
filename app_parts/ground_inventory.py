import streamlit as st
from .utils import safe_rerun
import cv2
import numpy as np
from pyzbar import pyzbar
import time
from datetime import datetime
import pandas as pd
import os
import requests


class QRInventoryScanner:
    """QR Code Scanner for inventory management using local CSV and API"""
    
    def __init__(self, csv_path, api_base_url, cooldown_seconds=2):
        self.csv_path = csv_path
        self.api_base_url = api_base_url
        self.cooldown_seconds = cooldown_seconds
        self.last_scan_time = {}
        self.inventory_data = None
        self.load_inventory_data()
        
    def load_inventory_data(self):
        """Load inventory data from CSV file"""
        try:
            if os.path.exists(self.csv_path):
                self.inventory_data = pd.read_csv(self.csv_path)
                print(f"[SUCCESS] Loaded {len(self.inventory_data)} items from CSV")
                print(f"[DEBUG] CSV columns: {self.inventory_data.columns.tolist()}")
                
                # Verify required columns
                if 'name' not in self.inventory_data.columns or 'url' not in self.inventory_data.columns:
                    print("[WARNING] CSV should have 'name' and 'url' columns")
            else:
                print(f"[ERROR] CSV file not found at: {self.csv_path}")
                self.inventory_data = pd.DataFrame(columns=['name', 'url'])
        except Exception as e:
            print(f"[ERROR] Failed to load CSV: {str(e)}")
            self.inventory_data = pd.DataFrame(columns=['name', 'url'])
    
    def get_item_from_qr(self, qr_data):
        """Get item information from QR code data using CSV"""
        try:
            if self.inventory_data is None or self.inventory_data.empty:
                return None, "CSV no cargado"
            
            qr_data_clean = qr_data.strip()
            
            # Try exact URL match
            match = self.inventory_data[self.inventory_data['url'] == qr_data_clean]
            if not match.empty:
                item = match.iloc[0]
                item_id = qr_data_clean.split('/')[-1]  # Extract ID from URL
                return {
                    'name': item['name'],
                    'url': item['url'],
                    'id': item_id
                }, None
            
            # Try partial match (in case QR has extra parameters)
            for idx, row in self.inventory_data.iterrows():
                if pd.notna(row['url']) and row['url'] in qr_data_clean:
                    item_id = row['url'].split('/')[-1]
                    return {
                        'name': row['name'],
                        'url': row['url'],
                        'id': item_id
                    }, None
            
            # Try matching by ID extracted from QR
            qr_id = qr_data_clean.split('/')[-1]
            for idx, row in self.inventory_data.iterrows():
                if pd.notna(row['url']) and row['url'].endswith(qr_id):
                    return {
                        'name': row['name'],
                        'url': row['url'],
                        'id': qr_id
                    }, None
            
            return None, f"Item no encontrado: {qr_data_clean}"
            
        except Exception as e:
            print(f"[ERROR] Error searching item: {str(e)}")
            return None, str(e)
    
    def decode_qr_codes(self, frame):
        """Decode QR codes from frame"""
        decoded_objects = pyzbar.decode(frame)
        return decoded_objects
    
    def annotate_frame(self, frame, decoded_objects):
        """Draw rectangles and text on frame for detected QR codes"""
        for obj in decoded_objects:
            # Get bounding box
            points = obj.polygon
            if len(points) == 4:
                # Draw polygon around QR code
                pts = np.array([[p.x, p.y] for p in points], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
            
            # Draw data text
            data = obj.data.decode('utf-8')
            x, y = obj.rect.left, obj.rect.top
            
            # Try to get item name from CSV
            item_data, error = self.get_item_from_qr(data)
            if item_data:
                item_name = str(item_data['name'])[:30]
            else:
                item_name = data.split('/')[-1][:30]
            
            cv2.putText(frame, item_name, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def should_send(self, qr_data):
        """Check if enough time has passed since last scan of this QR code"""
        current_time = time.time()
        last_time = self.last_scan_time.get(qr_data, 0)
        
        if current_time - last_time >= self.cooldown_seconds:
            self.last_scan_time[qr_data] = current_time
            return True
        return False
    
    def send_to_api(self, qr_data, item_data, token=None):
        """Send scan data to API endpoint /api/scanner"""
        try:
            # Prepare payload
            payload = {
                "qr_code": qr_data,
                "item_url": item_data.get('url', qr_data),
                "item_name": item_data.get('name', 'Unknown Item'),
                "item_id": item_data.get('id', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "scanned_by": st.session_state.get('username', 'unknown'),
                "user_id": st.session_state.get('user', {}).get('id', 'unknown'),
                "role": st.session_state.get('role', 'Ground Crew'),
                "action": "inventory_scan"
            }
            
            # Add authorization header if token is provided
            headers = {
                "Content-Type": "application/json"
            }
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            # API endpoint
            endpoint = f"{self.api_base_url}/scanner"
            
            print(f"[DEBUG] Sending to API: {endpoint}")
            print(f"[DEBUG] Payload: {payload}")
            
            try:
                response = requests.post(endpoint, json=payload, headers=headers, timeout=5)
                
                if response.status_code in [200, 201]:
                    print(f"[SUCCESS] Data sent to API: {item_data.get('name')}")
                    result = response.json() if response.text else {}
                    return True, result
                else:
                    print(f"[WARNING] API returned {response.status_code}: {response.text}")
                    # Return success anyway since we have local data
                    return True, {"api_status": response.status_code, "api_message": "API responded with error"}
            except requests.exceptions.ConnectionError:
                print("[WARNING] Could not connect to API, storing locally only")
                return True, {"api_error": "API offline - stored locally"}
            except requests.exceptions.Timeout:
                print("[WARNING] API request timed out")
                return True, {"api_error": "API timeout - stored locally"}
            
        except Exception as e:
            print(f"[ERROR] Failed to send to API: {str(e)}")
            return True, {"api_error": str(e)}
    
    def process_qr(self, qr_data, token=None):
        """Process QR code data: get item from CSV and send to API"""
        try:
            # Get item from CSV
            item_data, error = self.get_item_from_qr(qr_data)
            
            if error:
                print(f"[ERROR] {error}")
                return False, error, None
            
            if not item_data:
                return False, "Item no encontrado", None
            
            item_name = item_data['name']
            item_id = item_data['id']
            
            # Send to API (non-blocking - we proceed even if it fails)
            api_success, api_result = self.send_to_api(qr_data, item_data, token)
            
            # Build result
            result = {
                "qr_code": qr_data,
                "item_name": item_name,
                "item_id": item_id,
                "item_url": item_data['url'],
                "timestamp": datetime.now().isoformat(),
                "scanned_by": st.session_state.get('username', 'unknown'),
                "user_id": st.session_state.get('user', {}).get('id', 'unknown'),
                "role": st.session_state.get('role', 'Ground Crew'),
                "action": "inventory_scan",
                "api_response": api_result,
                "full_data": item_data
            }
            
            print(f"[SUCCESS] Item processed: {item_name} (ID: {item_id})")
            return True, item_name, result
            
        except Exception as e:
            print(f"[ERROR] Failed to process QR code: {str(e)}")
            return False, str(e), None


def render():
    st.title("Inventario")
    st.subheader("Ground Crew")
    
    # Back link to crew home
    st.markdown("""
        <a href='?page=groundcrew' style='display:inline-block;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px;color:var(--gold);text-decoration:none;'>
            ← Volver al Home
        </a>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize QR scanner in session state
    if 'qr_scanner_active' not in st.session_state:
        st.session_state['qr_scanner_active'] = False
    if 'inventory_qr_scanner' not in st.session_state:
        # Build path relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "..", "data", "inventory.csv")
        api_base = "https://summitlogicapidb-production.up.railway.app/api"
        st.session_state['inventory_qr_scanner'] = QRInventoryScanner(csv_path, api_base, cooldown_seconds=2)
    if 'inventory_scan_history' not in st.session_state:
        st.session_state['inventory_scan_history'] = []
    
    # Create tabs for Inventory sections
    tab1, tab2, tab3 = st.tabs(["📋 Inventario General", "📷 Escáner QR", "📊 Historial"])
    
    with tab1:
        st.markdown("### Gestión de Inventario")
        
        # Get actual inventory data
        scanner = st.session_state['inventory_qr_scanner']
        
        # Check if CSV is loaded
        if scanner.inventory_data is None or scanner.inventory_data.empty:
            st.error(f"⚠️ No se pudo cargar el archivo CSV")
            st.info(f"📁 Ruta buscada: `{scanner.csv_path}`")
            
            # Debug info
            with st.expander("🔍 Información de Debug"):
                st.write(f"**Directorio actual:** `{os.getcwd()}`")
                st.write(f"**Directorio del script:** `{os.path.dirname(os.path.abspath(__file__))}`")
                st.write(f"**Ruta CSV absoluta:** `{os.path.abspath(scanner.csv_path)}`")
                st.write(f"**¿Existe el archivo?** {os.path.exists(scanner.csv_path)}")
            
            st.markdown("""
            **Formato esperado del CSV:**
            ```csv
            name,url
            Still Water,https://jsonplaceholder.typicode.com/posts/1
            Sparkling Water,https://jsonplaceholder.typicode.com/posts/2
            ...
            ```
            """)
            
            if st.button("🔄 Reintentar Carga"):
                scanner.load_inventory_data()
                st.rerun()
            return
        
        total_items = len(scanner.inventory_data)
        
        st.write("**Resumen:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Items en Inventario", total_items)
        with col2:
            unique_scanned = len(set([s.get('item_id', '') for s in st.session_state['inventory_scan_history']]))
            st.metric("Items Únicos Escaneados", unique_scanned)
        with col3:
            total_scanned = len(st.session_state.get('inventory_scan_history', []))
            st.metric("Escaneos Totales", total_scanned)
        
        st.markdown("---")
        
        # Show CSV data
        st.write("**📦 Productos en Inventario:**")
        
        # Add search filter
        search = st.text_input("🔍 Buscar producto", placeholder="Escribe el nombre del producto...")
        
        if search:
            filtered_df = scanner.inventory_data[
                scanner.inventory_data['name'].str.contains(search, case=False, na=False)
            ]
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            st.caption(f"Mostrando {len(filtered_df)} de {total_items} productos")
        else:
            st.dataframe(scanner.inventory_data, use_container_width=True, hide_index=True)
        
        # Reload button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔄 Recargar CSV", use_container_width=True):
                scanner.load_inventory_data()
                st.success("✅ CSV recargado")
                st.rerun()
        
        # Category breakdown (based on product names)
        st.markdown("---")
        st.write("**📊 Categorías de Productos:**")
        categories = {
            '💧 Bebidas': ['Water', 'Juice', 'Coffee', 'Tea', 'Cola', 'Sprite'],
            '🍷 Bebidas Alcohólicas': ['Wine', 'Beer', 'Whiskey', 'Tequila', 'Rum'],
            '🥨 Snacks': ['Peanuts', 'Pretzels', 'Cookies', 'Fruit Mix', 'Chocolate'],
            '🥪 Comidas': ['Sandwich', 'Snack Box', 'Breakfast Box', 'Pasta Box']
        }
        
        cat_cols = st.columns(4)
        for idx, (cat_name, keywords) in enumerate(categories.items()):
            count = sum(
                any(keyword.lower() in name.lower() for keyword in keywords)
                for name in scanner.inventory_data['name']
            )
            with cat_cols[idx]:
                st.metric(cat_name, count)
    
    with tab2:
        st.markdown("### 📷 Escáner de Códigos QR para Inventario")
        st.write("Apunta la cámara a un código QR para identificar productos automáticamente.")
        
        # Check if CSV is loaded
        scanner = st.session_state['inventory_qr_scanner']
        if scanner.inventory_data is None or scanner.inventory_data.empty:
            st.warning("⚠️ El archivo CSV no está cargado. Ve a la pestaña 'Inventario General' para verificar.")
            st.stop()
        
        # Toggle button for scanner
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "🟢 Detener Escáner" if st.session_state['qr_scanner_active'] else "🔴 Iniciar Escáner",
                use_container_width=True,
                key="toggle_qr_scanner"
            ):
                st.session_state['qr_scanner_active'] = not st.session_state['qr_scanner_active']
                st.rerun()
        
        # Scanner interface
        if st.session_state['qr_scanner_active']:
            st.success("✅ Escáner activo - Apunta la cámara al código QR")
            
            # Status and camera placeholders
            status_placeholder = st.empty()
            camera_placeholder = st.empty()
            
            # Get token from session
            token = st.session_state.get('token')
            
            # Try to open camera
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                st.error("❌ No se pudo acceder a la cámara. Verifica los permisos.")
                st.session_state['qr_scanner_active'] = False
                if st.button("🔄 Reintentar", key="retry_camera"):
                    st.rerun()
                st.stop()
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            try:
                # Scanning loop (limited iterations to allow page interaction)
                frame_count = 0
                max_frames = 150  # ~5 seconds at 30fps
                
                while st.session_state['qr_scanner_active'] and frame_count < max_frames:
                    ret, frame = cap.read()
                    
                    if not ret:
                        status_placeholder.error("❌ Error al leer de la cámara")
                        break
                    
                    # Decode QR codes
                    decoded_objects = scanner.decode_qr_codes(frame)
                    
                    # Annotate frame with QR info
                    annotated_frame = scanner.annotate_frame(frame.copy(), decoded_objects)
                    
                    # Process detected QR codes
                    for obj in decoded_objects:
                        qr_data = obj.data.decode('utf-8')
                        
                        # Check cooldown and process
                        if scanner.should_send(qr_data):
                            success, item_name, result = scanner.process_qr(qr_data, token)
                            
                            if success:
                                status_placeholder.success(f"✅ Producto detectado: **{item_name}**")
                                
                                # Add to history
                                st.session_state['inventory_scan_history'].insert(0, {
                                    'data': qr_data,
                                    'item_name': item_name,
                                    'item_id': result.get('item_id', 'N/A') if result else 'N/A',
                                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'status': 'success',
                                    'result': result
                                })
                            else:
                                status_placeholder.warning(f"⚠️ {item_name}")
                    
                    # Convert BGR to RGB and display
                    annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                    camera_placeholder.image(annotated_frame_rgb, channels="RGB", use_container_width=True)
                    
                    frame_count += 1
                    time.sleep(0.033)  # ~30fps
                
                # Auto-stop message
                if frame_count >= max_frames:
                    st.session_state['qr_scanner_active'] = False
                    st.info("ℹ️ Escáner pausado. Presiona 'Iniciar Escáner' para continuar.")
                    
            except Exception as e:
                st.error(f"❌ Error en el escáner: {str(e)}")
                print(f"[ERROR] Scanner exception: {e}")
            finally:
                cap.release()
        
        else:
            st.info("ℹ️ El escáner está detenido.")
            st.markdown("""
            **Instrucciones:**
            1. Presiona "🔴 Iniciar Escáner"
            2. Permite el acceso a la cámara cuando el navegador lo solicite
            3. Apunta la cámara al código QR del producto
            4. El sistema buscará el producto en el inventario y lo enviará a la API
            5. El escáner se pausará automáticamente después de ~5 segundos
            
            **Formato del QR:** El código QR debe contener la URL completa del producto:
            - Ejemplo: `https://jsonplaceholder.typicode.com/posts/1`
            """)
            
            # Show sample QR codes
            with st.expander("📋 Ver URLs de ejemplo para generar QR"):
                st.code("\n".join([f"{row['name']}: {row['url']}" 
                                  for _, row in scanner.inventory_data.head(5).iterrows()]))
    
    with tab3:
        st.markdown("### 📊 Historial de Escaneos")
        
        if st.session_state['inventory_scan_history']:
            # Show stats
            total_scans = len(st.session_state['inventory_scan_history'])
            successful_scans = len([s for s in st.session_state['inventory_scan_history'] if s['status'] == 'success'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Escaneos", total_scans)
            with col2:
                st.metric("Exitosos", successful_scans)
            with col3:
                unique_items = len(set([s.get('item_name', 'Unknown') for s in st.session_state['inventory_scan_history']]))
                st.metric("Items Únicos", unique_items)
            
            st.markdown("---")
            
            # Export and clear buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Limpiar Historial", key="clear_history", use_container_width=True):
                    st.session_state['inventory_scan_history'] = []
                    st.rerun()
            with col2:
                # Create downloadable CSV
                if st.session_state['inventory_scan_history']:
                    history_df = pd.DataFrame([
                        {
                            'Producto': s['item_name'],
                            'ID': s['item_id'],
                            'Fecha': s['timestamp'],
                            'Usuario': s.get('result', {}).get('scanned_by', 'N/A')
                        }
                        for s in st.session_state['inventory_scan_history']
                    ])
                    csv = history_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar Historial CSV",
                        data=csv,
                        file_name=f"historial_escaneos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            # Display scan history
            st.markdown("### Últimos Escaneos")
            for idx, scan in enumerate(st.session_state['inventory_scan_history'][:20]):
                item_name = scan.get('item_name', 'Unknown Item')
                item_id = scan.get('item_id', 'N/A')
                
                with st.expander(f"{'✅' if scan['status'] == 'success' else '❌'} **{item_name}** (ID: {item_id}) - {scan['timestamp']}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**🏷️ Producto:** {item_name}")
                        st.write(f"**🔢 ID:** {item_id}")
                        if scan.get('result', {}).get('item_url'):
                            st.write(f"**🔗 URL:** `{scan['result']['item_url']}`")
                    with col2:
                        st.write(f"**⏰ Hora:** {scan['timestamp']}")
                        st.write(f"**👤 Usuario:** {scan.get('result', {}).get('scanned_by', 'N/A')}")
                    
                    # Show API status
                    if scan.get('result', {}).get('api_response'):
                        api_resp = scan['result']['api_response']
                        if 'api_error' in api_resp:
                            st.warning(f"⚠️ API: {api_resp['api_error']}")
                        elif 'api_status' in api_resp:
                            st.info(f"ℹ️ API Status: {api_resp['api_status']}")
                        else:
                            st.success("✅ Enviado a API exitosamente")
                    
                    if scan.get('result') and scan['result'].get('full_data'):
                        with st.expander("📄 Ver datos completos"):
                            st.json(scan['result']['full_data'])
        else:
            st.info("📭 No hay escaneos registrados todavía. Ve a la pestaña 'Escáner QR' para comenzar.")
            
            # Show tips
            st.markdown("""
            **💡 Consejos:**
            - Asegúrate de que el código QR tenga buena iluminación
            - Mantén el QR estable frente a la cámara por 1-2 segundos
            - El QR debe contener la URL exacta del producto
            - Los datos se envían automáticamente al endpoint `/api/scanner`
            """)