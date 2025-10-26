import streamlit as st
from .utils import safe_rerun


def render():
    st.title("Entrenamiento")
    st.subheader("Flight Crew")

    # Back link to crew home
    st.markdown("""
        <a href='?page=flightcrew' style='display:inline-block;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px;color:var(--gold);text-decoration:none;'>
            ← Volver al Home
        </a>
    """, unsafe_allow_html=True)

    # Initialize session state for quiz (with flight prefix to avoid conflicts)
    if 'flight_current_question' not in st.session_state:
        st.session_state.flight_current_question = 0
    if 'flight_selected_answer' not in st.session_state:
        st.session_state.flight_selected_answer = None
    if 'flight_answer_submitted' not in st.session_state:
        st.session_state.flight_answer_submitted = False
    if 'flight_correct_answer_index' not in st.session_state:
        st.session_state.flight_correct_answer_index = None

    # ============================================
    # GEMINI BOT API INTEGRATION SECTION - START
    # ============================================
    # TODO: Integrate Gemini Bot API here
    # Expected variables to be set:
    # - question_text: str - The question to display
    # - answer_options: list[str] - List of 4 answer options
    # - correct_answer_index: int - Index (0-3) of the correct answer
    # 
    # Example structure:
    # question_text = gemini_api.get_question(crew_type="flight")
    # answer_options = gemini_api.get_answer_options()
    # correct_answer_index = gemini_api.get_correct_answer_index()
    
    # Placeholder values (remove when API is integrated)
    question_text = "¿Cuál es el procedimiento correcto para verificar la seguridad de la cabina antes del despegue?"
    answer_options = [
        "Verificar cinturones de seguridad, equipaje asegurado y salidas despejadas",
        "Solo revisar que los pasajeros estén sentados",
        "Verificar únicamente las salidas de emergencia",
        "Esperar indicaciones del capitán sin verificación previa"
    ]
    correct_answer_index = 0
    # ============================================
    # GEMINI BOT API INTEGRATION SECTION - END
    # ============================================

    # Store correct answer in session state
    if st.session_state.flight_correct_answer_index is None:
        st.session_state.flight_correct_answer_index = correct_answer_index

    # Custom CSS for styling
    st.markdown("""
        <style>
        .question-box {
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(218, 165, 32, 0.3);
            border-radius: 12px;
            padding: 30px;
            margin: 20px 0;
            text-align: center;
            font-size: 1.2em;
            color: white;
        }
        
        .answer-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
            max-width: 100%;
        }
        
        .answer-box {
            background: rgba(255, 255, 255, 0.03);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        
        .answer-box:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(218, 165, 32, 0.5);
        }
        
        .answer-box-correct {
            border: 3px solid #00ff00 !important;
            background: rgba(0, 255, 0, 0.1) !important;
        }
        
        .answer-box-incorrect {
            border: 3px solid #ff0000 !important;
            background: rgba(255, 0, 0, 0.1) !important;
        }
        
        .nav-container {
            display: flex;
            justify-content: flex-end;
            margin-top: 20px;
        }
        
        .arrow-button {
            background: rgba(218, 165, 32, 0.2);
            border: 2px solid rgba(218, 165, 32, 0.6);
            border-radius: 8px;
            color: rgb(218, 165, 32);
            padding: 10px 20px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .arrow-button:hover {
            background: rgba(218, 165, 32, 0.4);
            border-color: rgb(218, 165, 32);
        }
        
        .arrow-button:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display question in main box
    st.markdown(f"""
        <div class="question-box">
            <strong>Pregunta {st.session_state.flight_current_question + 1}</strong><br><br>
            {question_text}
        </div>
    """, unsafe_allow_html=True)

    # Create 2x2 grid for answer options
    col1, col2 = st.columns(2)
    
    with col1:
        for i in [0, 2]:
            if i < len(answer_options):
                # Determine box styling
                box_class = "answer-box"
                if st.session_state.flight_answer_submitted:
                    if i == st.session_state.flight_correct_answer_index:
                        box_class += " answer-box-correct"
                    elif i == st.session_state.flight_selected_answer:
                        box_class += " answer-box-incorrect"
                
                # Create clickable answer box
                if st.button(
                    answer_options[i],
                    key=f"flight_answer_{i}",
                    disabled=st.session_state.flight_answer_submitted,
                    use_container_width=True
                ):
                    st.session_state.flight_selected_answer = i
                    st.session_state.flight_answer_submitted = True
                    st.rerun()

    with col2:
        for i in [1, 3]:
            if i < len(answer_options):
                # Determine box styling
                box_class = "answer-box"
                if st.session_state.flight_answer_submitted:
                    if i == st.session_state.flight_correct_answer_index:
                        box_class += " answer-box-correct"
                    elif i == st.session_state.flight_selected_answer:
                        box_class += " answer-box-incorrect"
                
                # Create clickable answer box
                if st.button(
                    answer_options[i],
                    key=f"flight_answer_{i}",
                    disabled=st.session_state.flight_answer_submitted,
                    use_container_width=True
                ):
                    st.session_state.flight_selected_answer = i
                    st.session_state.flight_answer_submitted = True
                    st.rerun()

    # Navigation arrow (only forward, only after answer is submitted)
    if st.session_state.flight_answer_submitted:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col3:
            if st.button("Siguiente →", key="flight_next_button", use_container_width=True):
                # Move to next question
                st.session_state.flight_current_question += 1
                st.session_state.flight_selected_answer = None
                st.session_state.flight_answer_submitted = False
                st.session_state.flight_correct_answer_index = None
                
                # ============================================
                # GEMINI BOT API - LOAD NEXT QUESTION
                # ============================================
                # TODO: Call Gemini API to load next question here
                # gemini_api.load_next_question(crew_type="flight")
                # ============================================
                
                st.rerun()

    # Display feedback message
    if st.session_state.flight_answer_submitted:
        if st.session_state.flight_selected_answer == st.session_state.flight_correct_answer_index:
            st.success("¡Correcto! Has seleccionado la respuesta correcta.")
        else:
            st.error("Incorrecto. Por favor revisa la respuesta correcta marcada en verde.")