import streamlit as st
from .utils import safe_rerun


def render():
    st.title("Inventario")
    st.subheader("Ground Crew")

    # Back link to crew home (anchor ensures single-click URL navigation)
    st.markdown("""
        <a href='?page=groundcrew' style='display:inline-block;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:6px;color:var(--gold);text-decoration:none;'>
            ← Volver al Home
        </a>
    """, unsafe_allow_html=True)

    st.write("Esta es la sección de Inventario para el equipo de tierra.")
    st.write("- Listado de items")
    st.write("- Niveles de stock")
    st.write("- Historial de movimientos")
