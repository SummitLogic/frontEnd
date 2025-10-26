import streamlit as st
import json
import os
from datetime import datetime
from .utils import safe_rerun


def load_questions():
    """Load questions from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'quiz_questions.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['questions']


def load_leaderboard():
    """Load leaderboard from JSON file"""
    leaderboard_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'leaderboard.json')
    if os.path.exists(leaderboard_path):
        with open(leaderboard_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"scores": []}


def save_leaderboard(leaderboard):
    """Save leaderboard to JSON file"""
    leaderboard_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'leaderboard.json')
    with open(leaderboard_path, 'w', encoding='utf-8') as f:
        json.dump(leaderboard, f, indent=2, ensure_ascii=False)


def render():
    st.title("Entrenamiento")
    st.subheader("Ground Crew")

    # Back link to crew home
    st.markdown("""
        <a href='?page=groundcrew' style='display:inline-block;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px;color:var(--gold);text-decoration:none;'>
            ← Volver al Home
        </a>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = load_questions()
    if 'current_question_idx' not in st.session_state:
        st.session_state.current_question_idx = 0
    if 'selected_answer' not in st.session_state:
        st.session_state.selected_answer = None
    if 'answer_submitted' not in st.session_state:
        st.session_state.answer_submitted = False
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'show_leaderboard' not in st.session_state:
        st.session_state.show_leaderboard = False
    if 'username' not in st.session_state:
        st.session_state.username = st.session_state.get('user', {}).get('name', 'Usuario')

    # Tab selection
    tab1, tab2 = st.tabs(["📝 Cuestionario", "🏆 Leaderboard"])
    
    with tab1:
        render_quiz()
    
    with tab2:
        render_leaderboard()


def render_quiz():
    """Render the quiz interface"""
    questions = st.session_state.quiz_questions
    current_idx = st.session_state.current_question_idx
    
    # Check if quiz is completed
    if st.session_state.quiz_completed:
        st.success(f"¡Felicidades! Has completado el cuestionario")
        st.info(f"Puntuación: {st.session_state.quiz_score}/{len(questions)}")
        
        # Save to leaderboard
        if st.button("💾 Guardar Puntuación en Leaderboard"):
            leaderboard = load_leaderboard()
            leaderboard["scores"].append({
                "name": st.session_state.username,
                "score": st.session_state.quiz_score,
                "total": len(questions),
                "percentage": round((st.session_state.quiz_score / len(questions)) * 100, 2),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "crew_type": "Ground Crew"
            })
            save_leaderboard(leaderboard)
            st.success("¡Puntuación guardada!")
            st.balloons()
        
        if st.button("🔄 Reiniciar Cuestionario"):
            st.session_state.current_question_idx = 0
            st.session_state.selected_answer = None
            st.session_state.answer_submitted = False
            st.session_state.quiz_score = 0
            st.session_state.quiz_completed = False
            st.rerun()
        return
    
    # Progress bar
    progress = (current_idx + 1) / len(questions)
    st.progress(progress)
    st.caption(f"Pregunta {current_idx + 1} de {len(questions)}")
    
    # Get current question
    question = questions[current_idx]
    
    # Custom CSS
    st.markdown("""
        <style>
        .question-box {
            background: linear-gradient(135deg, rgba(218, 165, 32, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
            border: 2px solid rgba(218, 165, 32, 0.3);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            text-align: center;
            font-size: 1.3em;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .category-badge {
            display: inline-block;
            background: rgba(218, 165, 32, 0.2);
            border: 1px solid rgba(218, 165, 32, 0.5);
            border-radius: 20px;
            padding: 5px 15px;
            font-size: 0.8em;
            margin-bottom: 15px;
            color: rgb(218, 165, 32);
        }
        
        .stButton button {
            width: 100%;
            min-height: 80px;
            border-radius: 10px;
            font-size: 1.1em;
            transition: all 0.3s ease;
        }
        
        .correct-answer {
            background-color: rgba(0, 255, 0, 0.2) !important;
            border: 3px solid #00ff00 !important;
        }
        
        .incorrect-answer {
            background-color: rgba(255, 0, 0, 0.2) !important;
            border: 3px solid #ff0000 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display question
    st.markdown(f"""
        <div class="question-box">
            <div class="category-badge">{question['category']} - {question['difficulty'].capitalize()}</div><br>
            <strong>{question['question']}</strong>
        </div>
    """, unsafe_allow_html=True)
    
    # Display answer options in 2x2 grid
    col1, col2 = st.columns(2)
    
    for i, option in enumerate(question['options']):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            # Determine button state and styling
            disabled = st.session_state.answer_submitted
            
            if st.button(
                f"{chr(65+i)}. {option}",
                key=f"answer_{i}",
                disabled=disabled,
                type="secondary"
            ):
                st.session_state.selected_answer = i
                st.session_state.answer_submitted = True
                
                # Check if answer is correct
                if i == question['correct_answer']:
                    st.session_state.quiz_score += 1
                
                st.rerun()
    
    # Show feedback and navigation
    if st.session_state.answer_submitted:
        selected = st.session_state.selected_answer
        correct = question['correct_answer']
        
        if selected == correct:
            st.success("✅ ¡Correcto! Excelente trabajo.")
        else:
            st.error(f"❌ Incorrecto. La respuesta correcta es: {chr(65+correct)}. {question['options'][correct]}")
        
        # Next button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col3:
            if st.button("Siguiente →", type="primary", use_container_width=True):
                # Move to next question
                if current_idx + 1 < len(questions):
                    st.session_state.current_question_idx += 1
                    st.session_state.selected_answer = None
                    st.session_state.answer_submitted = False
                else:
                    st.session_state.quiz_completed = True
                st.rerun()


def render_leaderboard():
    """Render the leaderboard"""
    st.subheader("🏆 Tabla de Posiciones")
    
    leaderboard = load_leaderboard()
    
    if not leaderboard["scores"]:
        st.info("No hay puntuaciones registradas aún. ¡Sé el primero en completar el cuestionario!")
        return
    
    # Sort by score (descending) and date (most recent first)
    sorted_scores = sorted(
        leaderboard["scores"],
        key=lambda x: (x["score"], x["date"]),
        reverse=True
    )
    
    # Display top scores
    st.markdown("### 🥇 Top 10 Mejores Puntuaciones")
    
    for idx, entry in enumerate(sorted_scores[:10], 1):
        # Medal emojis for top 3
        medal = ""
        if idx == 1:
            medal = "🥇"
        elif idx == 2:
            medal = "🥈"
        elif idx == 3:
            medal = "🥉"
        else:
            medal = f"#{idx}"
        
        # Color based on ranking
        if idx <= 3:
            color = "rgba(218, 165, 32, 0.2)"
            border_color = "rgba(218, 165, 32, 0.6)"
        else:
            color = "rgba(255, 255, 255, 0.05)"
            border_color = "rgba(255, 255, 255, 0.2)"
        
        st.markdown(f"""
            <div style="background: {color}; border: 2px solid {border_color}; border-radius: 10px; padding: 15px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="font-size: 1.5em;">{medal}</span>
                        <div>
                            <strong style="font-size: 1.1em;">{entry['name']}</strong><br>
                            <small style="color: #888;">{entry['crew_type']} • {entry['date']}</small>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <strong style="font-size: 1.3em; color: rgb(218, 165, 32);">{entry['score']}/{entry['total']}</strong><br>
                        <small>{entry['percentage']}%</small>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)