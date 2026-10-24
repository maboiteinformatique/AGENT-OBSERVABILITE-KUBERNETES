import streamlit as st
from ao import diagnostiquer

st.set_page_config(page_title="Nova", page_icon="🤖")
st.title("Nova — Agent IA (Local)")

# historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# affichage historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# input utilisateur
if prompt := st.chat_input("Écrivez votre message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            answer = diagnostiquer(prompt)

        except Exception as e:
            answer = f"Erreur serveur: {e}"

        st.write(answer)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )