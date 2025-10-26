import streamlit as st
from .utils import safe_rerun


def render():
    st.title("Alcohol")
    st.subheader("Flight Crew")

    # Back link to crew home (use an anchor so the browser URL changes in one click)
    st.markdown("""
        <a href='?page=flightcrew' style='display:inline-block;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px;color:var(--gold);text-decoration:none;'>
            ← Volver al Home
        </a>
    """, unsafe_allow_html=True)

    st.write("Esta es la sección de Alcohol para el equipo de vuelo.")
    st.write("- Control de botellas")
    st.write("- Registro de consumo")
    st.write("- Alertas de stock")
