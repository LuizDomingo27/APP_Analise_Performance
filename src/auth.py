import streamlit as st

SENHA_CORRETA = "diretoria"

def verificar_autenticacao(nome_pagina: str) -> bool:
    """
    Verifica se o usuário está autenticado para ver a página informada.
    Se a página anterior na sessão for diferente da atual, limpa a autorização.
    Retorna True se autorizado, ou exibe o formulário de login e retorna False.
    """
    # Se last_page mudou, invalida a autorização de visualização
    if st.session_state.get("last_page") != nome_pagina:
        st.session_state["metodologia_autorizada"] = False
        st.session_state["last_page"] = nome_pagina

    if st.session_state.get("metodologia_autorizada", False):
        return True

    # Renderiza o formulário de login centralizado
    st.markdown("""
    <div style="text-align:center; margin-top:3rem;">
        <span class="material-symbols-outlined" style="font-size:48px; color:#c084fc;">lock</span>
        <h2 style="font-size:22px; margin-top:10px; margin-bottom:5px; font-weight: 500;">Acesso Restrito</h2>
        <p style="color:#94a3b8; font-size:15px; margin-bottom:1.5rem;">Esta página requer autenticação da diretoria.</p>
    </div>
    """, unsafe_allow_html=True)

    # Cria uma coluna centralizada para a senha
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        senha = st.text_input("Digite a senha de acesso:", type="password", key=f"senha_input_{nome_pagina}")
        if senha:
            if senha == SENHA_CORRETA:
                st.session_state["metodologia_autorizada"] = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
                
    return False

def registrar_saida(nome_pagina: str):
    """
    Marca a última página ativa como a página informada e limpa a autorização se for diferente.
    Deve ser chamado na inicialização do painel principal (app.py).
    """
    if st.session_state.get("last_page") != nome_pagina:
        st.session_state["metodologia_autorizada"] = False
        st.session_state["last_page"] = nome_pagina
