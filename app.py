import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import io
import base64
from datetime import datetime
from src.logic import consolidar, calcular, status_info, perf_info, V, META_EFICIENCIA, find_col
from src.auth import registrar_saida

st.set_page_config(
    page_title="Nivel de Serviço",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Registrar a página atual para controle de acesso/reset de senha
registrar_saida("App")

# ── CSS ─────────────────────────────────────────────────────────────────────────
def load_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo de estilos '{file_name}' não encontrado.")

load_css("assets/styles.css")

# ── IMPORTAÇÕES DE MÓDULOS REFATORADOS ──────────────────────────────────────────
from src.utils import fmt, fmtD, fmtPct, fmtDate, prazo_badge
from src.charts import (
    gauge_fig,
    gauge_efic,
    bar_comparativo,
    bar_ranking,
    bar_pecas,
    bar_eficiencia,
)
from src.reports import gerar_relatorio_html, gerar_relatorio_eficiencia_html
from src.excel_exporter import exportar_xlsx_executivo, exportar_recebimento_xlsx_executivo

@st.cache_data
def exportar_xlsx(df_base, df_detalhe, df_eficiencia):
    return exportar_xlsx_executivo(df_base, df_detalhe, df_eficiencia)

@st.cache_data
def exportar_recebimento(df_rec_of, c_om, c_qtd, c_min, c_dia):
    return exportar_recebimento_xlsx_executivo(df_rec_of, c_om, c_qtd, c_min, c_dia)





# ── LEITURA DE ARQUIVO ──────────────────────────────────────────────────────────
def read_file(f):
    if f is None: return None
    try:
        return pd.read_csv(f, sep=None, engine="python") if f.name.endswith(".csv") else pd.read_excel(f)
    except Exception as e:
        st.error(f"Erro ao ler {f.name}: {e}")
        return None

# ── PROCESSAMENTO COM CACHE ─────────────────────────────────────────────────────
@st.cache_data
def process_files_v2(f_ctrl, f_acomp, f_rec, filtro_mp=None):
    """
    Processa os três arquivos (com filtro de ordens > 0 e agregação unificada de oficinas):
      f_ctrl  → ESTOQUE.xlsx   (OFICINA, COLABORADORES, CAP PECAS 65%, CAP PEÇAS SEMANAL)
      f_acomp → ACOMPANHAMENTO.xlsx (ORDEM MESTRE, OFICINA, ENVIO, QTD, MINUTOS, DEAD LINE, MP)
      f_rec   → RECEBIMENTO.xlsx   (DIA, OFICINA, ORDEM MESTRE, MP, REAL CORTADO, MINUTOS)
    """
    df_estoque_raw = read_file(f_ctrl)
    df_acomp_raw   = read_file(f_acomp)
    df_rec_raw     = read_file(f_rec)

    if df_estoque_raw is not None and df_acomp_raw is not None and df_rec_raw is not None:
        return consolidar(df_estoque_raw, df_acomp_raw, df_rec_raw, filtro_mp)
    return None, None, None, [], []

# ── ESTADO ──────────────────────────────────────────────────────────────────────


# ── CABEÇALHO ───────────────────────────────────────────────────────────────────
st.markdown('''
<div style="display:flex; align-items:center; gap:15px; margin-bottom:1rem;">
    <div style="background:linear-gradient(135deg, #7c3aed, #4f46e5); width:46px; height:46px; border-radius:11px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        <span class="material-symbols-outlined" style="color:#ffffff; font-size:26px;">analytics</span>
    </div>
    <div>
        <h1 style="margin:0;font-weight:bold; font-size:2.7rem;">Analise de Performance - Nível de Serviço </h1>
        <p style="color:#94a3b8; font-size:12px; margin:0;">Central das Oficinas</p>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── TABS PRINCIPAIS ─────────────────────────────────────────────────────────────
tab_import, tab_visao, tab_oficina = st.tabs([
    "📥 Importar Arquivos", 
    "📊 Visão Geral", 
    "🏢 Análise por Oficina"
])

df_base, df_detalhe, df_eficiencia, lista_mps = None, None, None, []

with tab_import:
    st.markdown('<div class="sec">1. Importar Arquivos</div>', unsafe_allow_html=True)
    uc1, uc2, uc3 = st.columns(3)
    with uc1: f_ctrl  = st.file_uploader(":material/content_paste: Planilha ESTOQUE", type=["xlsx","xls","csv"], key="f_ctrl")
    with uc2: f_acomp = st.file_uploader(":material/bar_chart: Planilha ACOMPANHAMENTO", type=["xlsx","xls","csv"], key="f_acomp")
    with uc3: f_rec   = st.file_uploader(":material/inventory_2: Planilha RECEBIMENTO", type=["xlsx","xls","csv"], key="f_rec")

    arquivos_faltando = []
    if not f_ctrl:  arquivos_faltando.append("ESTOQUE")
    if not f_acomp: arquivos_faltando.append("ACOMPANHAMENTO")
    if not f_rec:   arquivos_faltando.append("RECEBIMENTO")

    if arquivos_faltando:
        nomes = " | ".join(f"**{a}**" for a in arquivos_faltando)
        st.markdown(
            f'<div style="background:rgba(239,68,68,0.12);border:2px solid #ef4444;'
            f'border-radius:12px;padding:1rem 1.2rem;margin:1rem 0;">'
            f'<div style="font-size:15px;font-weight:700;color:#ef4444;margin-bottom:4px"><span class="material-symbols-outlined" style="vertical-align:-4px;font-size:18px;">warning</span> ATENÇÃO — Faltam arquivos</div>'
            f'<div style="font-size:13px;color:#fca5a5">Envie: {nomes}.</div></div>', unsafe_allow_html=True)

if f_ctrl and f_acomp and f_rec:
    # Passo 1: Extrair MPs disponíveis
    _, _, _, erros_iniciais, lista_mps = process_files_v2(f_ctrl, f_acomp, f_rec, None)

    if erros_iniciais:
        st.error(f"⚠️ Colunas não encontradas: {', '.join(erros_iniciais)}")
        st.stop()

    with tab_visao:
        # ── FILTROS GLOBAIS ─────────────────────────────────────────────────────────
        st.markdown('<div class="sec">Filtrar Dados (Consumo de Capacidade)</div>', unsafe_allow_html=True)
        
        # 1º Filtro: MP (Pois ele influencia no abatimento/recálculo)
        base_full, det_full, efic_full, erros, _ = process_files_v2(f_ctrl, f_acomp, f_rec, None)
        
        fc1, fc2 = st.columns(2)
        with fc1:
            sel_mp = st.selectbox("Selecione a Matéria-Prima (MP):", ["Todas"] + lista_mps)
            filtro_mp = None if sel_mp == "Todas" else sel_mp

        # Obter os dados já calculados para a MP selecionada (ou todas)
        base, det, efic, erros, _ = process_files_v2(f_ctrl, f_acomp, f_rec, filtro_mp)

        if base is not None:
            lista_oficinas = sorted(base["OFICINA"].unique().tolist())
            with fc2:
                sel_oficina = st.selectbox("Selecione a Oficina (Opcional):", ["Todas"] + lista_oficinas)
                filtro_oficina = None if sel_oficina == "Todas" else sel_oficina

            # Aplicar o filtro de Oficina diretamente nos DataFrames
            if filtro_oficina:
                df_base = base[base["OFICINA"] == filtro_oficina].copy()
                df_detalhe = det[det["OFICINA"] == filtro_oficina].copy() if det is not None else None
                df_eficiencia = efic[efic["OFICINA"] == filtro_oficina].copy() if efic is not None else None
            else:
                df_base, df_detalhe, df_eficiencia = base, det, efic
                
            lbl_chip = "Consolidado Geral"
            if filtro_mp and filtro_oficina:
                lbl_chip = f"Filtrado: MP {filtro_mp} | Oficina {filtro_oficina}"
            elif filtro_mp:
                lbl_chip = f"Filtrado: Apenas MP {filtro_mp}"
            elif filtro_oficina:
                lbl_chip = f"Filtrado: Apenas Oficina {filtro_oficina}"

            st.markdown(
                f'<div class="chip" style="margin-bottom:1.5rem;"><span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px;">check_circle</span> {lbl_chip} &nbsp;&bull;&nbsp; '
                f'{len(df_base)} Grupos ativos | '
                f'{int(df_base["TOTAL_ORDENS"].sum())} ordens pendentes | '
                f'{fmt(df_base["TOTAL_PECAS"].sum())} peças pendentes</div>',
                unsafe_allow_html=True
            )

with tab_visao:
    if df_base is not None:
        st.markdown('<div class="sec">Visão Geral — Saldo Pendente</div>', unsafe_allow_html=True)

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        total_of  = len(df_base)
        total_ord = int(df_base["TOTAL_ORDENS"].sum())
        total_pc  = int(df_base["TOTAL_PECAS"].sum())
        total_min = int(df_base.get("TOTAL_MINUTOS", pd.Series([0])).sum())
        viaveis   = int((df_base["PROBABILIDADE_PCT"] >= 75).sum())
        na_meta   = int(df_base.get("ordens_na_meta", pd.Series([0])).sum()) if "ordens_na_meta" in df_base else 0

        k1.markdown(f'<div class="kpi-wrap"><div class="kpi-lbl">Grupos com Saldo</div><div class="kpi-val" style="color:#00e5cc">{total_of}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="kpi-wrap"><div class="kpi-lbl">Ordens Pendentes</div><div class="kpi-val" style="color:#c084fc">{fmt(total_ord)}</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="kpi-wrap"><div class="kpi-lbl">Peças Pendentes</div><div class="kpi-val" style="color:#00e5cc">{fmt(total_pc)}</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="kpi-wrap"><div class="kpi-lbl">Min. Pendentes</div><div class="kpi-val" style="color:#2dd4bf">{fmt(total_min)}</div></div>', unsafe_allow_html=True)
        k5.markdown(f'<div class="kpi-wrap"><div class="kpi-lbl">Entrega Viável</div><div class="kpi-val" style="color:#10b981">{viaveis}/{total_of}</div></div>', unsafe_allow_html=True)
        k6.markdown(f'<div class="kpi-wrap"><div class="kpi-lbl">Ordens na Meta</div><div class="kpi-val" style="color:#f59e0b">{na_meta}/{total_ord}</div></div>', unsafe_allow_html=True)

        # ── Tabela consolidada ────────────────────────────────────────────────────
        st.markdown("")
        rows_html = ""
        for _, row in df_base.iterrows():
            p = row["PROBABILIDADE_PCT"]
            lbl2, cor2, pill2, _, _ = status_info(p) if p > 0 else ("Concluído", "#10b981", "pill-ok", "", "")
            fg = row["FOLGA_DEFICIT"]
            sinal = "+" if fg >= 0 else "-"
            cfg  = "#10b981" if fg >= 0 else "#ef4444"

            # Eficiência e Consumo
            ef_pct  = row.get("pct_ordens_na_meta", 0)
            ef_lbl, ef_cor, ef_pill = perf_info(ef_pct)
            ef_meta = f'{int(row.get("ordens_na_meta", 0))}/{int(row.get("TOTAL_ORDENS", 0))}'
            
            consumo = (row['TOTAL_PECAS'] / row['CAP_NO_PRAZO'] * 100) if row.get('CAP_NO_PRAZO', 0) > 0 else 0

            rows_html += (
                f"<tr>"
                f"<td><strong>{row['OFICINA']}</strong></td>"
                f"<td class='tr'>{int(row['COLABORADORES'])}</td>"
                f"<td class='tr'>{fmt(row['CAP_DIA'])}</td>"
                f"<td class='tr' style='color:#2dd4bf'>{fmt(row.get('CAP_SEMANAL', 0))}</td>"
                f"<td class='tr' style='color:#c084fc'>{int(row['TOTAL_ORDENS'])}</td>"
                f"<td class='tr' style='color:#00e5cc;font-weight:600'>{fmt(row['TOTAL_PECAS'])}</td>"
                f"<td class='tr'>{fmt(row.get('TOTAL_MINUTOS',0))}</td>"
                f"<td class='tr' style='color:#f59e0b;font-weight:600'>{consumo:.1f}%</td>"
                f"<td class='tr' style='color:{cfg};font-weight:600'>{sinal}{fmt(abs(fg))}</td>"
                f"</tr>"
            )

        st.markdown(
            f"<div style='overflow-x:auto'>"
            f"<table class='tbl'><thead><tr>"
            f"<th>Oficina</th><th class='tr'>Colab.</th><th class='tr'>Cap/Dia</th>"
            f"<th class='tr'>Cap/Semana</th>"
            f"<th class='tr'>Ordens Pnd.</th><th class='tr'>Peças Pnd.</th>"
            f"<th class='tr'>Min. Pnd.</th><th class='tr'>Consumo da Cap.</th>"
            f"<th class='tr'>Folga/Déficit (Saldo)</th>"
            f"</tr></thead><tbody>{rows_html}</tbody></table></div>",
            unsafe_allow_html=True
        )

        st.markdown("")
        col_btn, _ = st.columns([1, 3])
        with col_btn:
            st.download_button(
                "Exportar Base Consolidada (.xlsx)",
                data=exportar_xlsx(df_base, df_detalhe, df_eficiencia),
                file_name=f"base_consolidada_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=False,
            )
    else:
        st.markdown('<div class="card" style="text-align:center;padding:2rem;">'
                    '<p><span class="material-symbols-outlined" style="font-size:48px; color:#94a3b8;">note_add</span></p>'
                    '<p style="color:#94a3b8;margin-top:.5rem">Importe os <strong>três</strong> arquivos na aba <strong>Importar & Filtrar</strong> para começar a análise</p>'
                    '</div>', unsafe_allow_html=True)

with tab_oficina:
    if df_base is not None:
        st.markdown('<div class="sec">Análise por Oficina</div>', unsafe_allow_html=True)

        nomes  = df_base["OFICINA"].tolist()
        sel    = st.selectbox("Oficina", ["Selecione a oficina..."] + nomes)

        if sel != "Selecione a oficina...":
            row_b = df_base[df_base["OFICINA"] == sel].iloc[0]

            tab_pendentes, tab_recebimento = st.tabs(["📋 Ordens Pendentes", "📦 Recebimento (Entregues)"])

            with tab_pendentes:
                # ── Tabela de ordens pendentes ───────────────────────────────────────
                if df_detalhe is not None and not df_detalhe.empty:
                    det_of = df_detalhe[df_detalhe["OFICINA"] == sel].reset_index(drop=True)
                    if len(det_of):
                        st.markdown("")
                        st.markdown(f'<div class="sec">Ordens Pendentes da {sel}</div>', unsafe_allow_html=True)
                        d_rows = ""
                        for _, dr in det_of.iterrows():
                            # ── Formatação de datas e prazo ───────────────────────────
                            envio_fmt    = fmtDate(dr.get("ENVIO", "-"))
                            deadline_fmt = fmtDate(dr.get("DEAD_LINE", "-"))
                            # Usa DIAS_PARA_VENCER (dinâmico = DEAD_LINE - HOJE) para o badge
                            prazo_html   = prazo_badge(dr.get("DIAS_PARA_VENCER"))

                            d_rows += (
                                f"<tr>"
                                f"<td>{dr['ORDEM_MESTRE']}</td>"
                                f"<td><span style='color:#a855f7;background:rgba(168,85,247,0.1);padding:2px 6px;border-radius:4px;font-size:11px'>{dr['MP']}</span></td>"
                                f"<td class='tr' style='color:#94a3b8'>{fmt(dr['QTD_PECAS'])} pc</td>"
                                f"<td class='tr' style='color:#10b981'>{fmt(dr.get('QTD_ENTREGUE',0))} pc</td>"
                                f"<td class='tr' style='color:#00e5cc;font-weight:700'>{fmt(dr.get('QTD_PENDENTE',0))} pc</td>"
                                f"<td class='tr'>{fmt(dr.get('MIN_PENDENTE',0))} min</td>"
                                f"<td class='tr' style='color:#94a3b8'>{envio_fmt}</td>"
                                f"<td class='tr' style='color:#c084fc'>{deadline_fmt}</td>"
                                f"<td class='tr' style='color:#64748b'>{dr.get('PRAZO_DIAS', '-')}d</td>"
                                f"<td class='tr'>{prazo_html}</td>"
                                f"</tr>"
                            )
                        # ── Renderiza a tabela completa após construir todas as linhas ─
                        st.markdown(
                            f"<div style='overflow-x:auto'>"
                            f"<table class='tbl'><thead><tr>"
                            f"<th>Ordem</th><th>MP</th><th class='tr'>Solicitado</th><th class='tr'>Entregue</th>"
                            f"<th class='tr'>Pendente (Saldo)</th><th class='tr'>Min. Pnd.</th>"
                            f"<th class='tr'>Envio</th><th class='tr'>Dead Line</th>"
                            f"<th class='tr'>Prazo (dias)</th><th class='tr'>Falta p/ Vencer</th>"
                            f"</tr></thead><tbody>{d_rows}</tbody></table></div>",
                            unsafe_allow_html=True,
                        )

                # ── Relatório ─────────────────────────────────────────────────────────
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown('<div class="sec">Gerar Relatórios para Gestor</div>', unsafe_allow_html=True)

                # Calcular o dicionário 'r' com os dados reais para alimentar os geradores de relatório HTML
                r = calcular(
                    cap_dia=float(row_b["CAP_DIA"]),
                    colaboradores=int(row_b["COLABORADORES"]),
                    total_pecas=float(row_b["TOTAL_PECAS"]),
                    prazo_medio_dias=float(row_b["PRAZO_MEDIO_DIAS"]),
                    cap_semanal=float(row_b["CAP_SEMANAL"])
                )

                html_rel = gerar_relatorio_html(sel, r, row_b.to_dict())
                html_bytes = html_rel.encode("utf-8")
                b64_str = base64.b64encode(html_bytes).decode("ascii")
                fname_rel = f"relatorio_{sel.replace(' ','_')}_{datetime.now().strftime('%d%m%Y_%H%M')}.html"

                rr1, rr2 = st.columns(2)
                with rr1:
                    components.html(f"""
                    <body style="margin:0;background:transparent;">
                    <button onclick="(function(){{
                        try {{
                            var bin = atob('{b64_str}'); var bytes = new Uint8Array(bin.length);
                            for(var i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
                            var html = new TextDecoder('utf-8').decode(bytes);
                            var w = window.open('','_blank'); w.document.open(); w.document.write(html); w.document.close();
                        }} catch(e) {{ alert('Erro: '+e); }} }})()"
                    style="width:100%;height:38px;margin:0;border:1px solid #059669;background:#065f46;
                           color:#fff;font-weight:600;border-radius:8px;font-size:13.5px;cursor:pointer;
                           font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
                        Abrir no Navegador
                    </button>
                    </body>""", height=40)
                with rr2:
                    det_of_ef = df_detalhe[df_detalhe["OFICINA"] == sel].reset_index(drop=True) if df_detalhe is not None and not df_detalhe.empty else pd.DataFrame()
                    html_ef = gerar_relatorio_eficiencia_html(sel, row_b.to_dict(), det_of_ef)
                    html_ef_bytes = html_ef.encode("utf-8")
                    b64_ef = base64.b64encode(html_ef_bytes).decode("ascii")
                    fname_ef = f"eficiencia_{sel.replace(' ','_')}_{datetime.now().strftime('%d%m%Y_%H%M')}.html"
                    components.html(f"""
                    <body style="margin:0;background:transparent;">
                    <button onclick="(function(){{
                        try {{
                            var bin = atob('{b64_ef}'); var bytes = new Uint8Array(bin.length);
                            for(var i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
                            var html = new TextDecoder('utf-8').decode(bytes);
                            var w = window.open('','_blank'); w.document.open(); w.document.write(html); w.document.close();
                        }} catch(e) {{ alert('Erro: '+e); }} }})()"
                    style="width:100%;height:38px;margin:0;border:1px solid #b45309;background:#78350f;
                           color:#fff;font-weight:600;border-radius:8px;font-size:13.5px;cursor:pointer;
                           font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
                        Abrir Relatório de Eficiência
                    </button>
                    </body>""", height=40)

            with tab_recebimento:
                df_rec_raw = read_file(f_rec)
                if df_rec_raw is not None and not df_rec_raw.empty:
                    # Mapeamento
                    c_rec_of  = find_col(df_rec_raw.columns, V["rec_of"])
                    c_rec_om  = find_col(df_rec_raw.columns, V["rec_om"])
                    c_rec_qtd = find_col(df_rec_raw.columns, V["rec_qtd"])
                    c_rec_min = find_col(df_rec_raw.columns, V["rec_min"])
                    c_rec_dia = find_col(df_rec_raw.columns, V["rec_dia"])

                    if c_rec_of and c_rec_om and c_rec_qtd and c_rec_dia:
                        # Filtrar pela oficina selecionada
                        rec_of = df_rec_raw[df_rec_raw[c_rec_of].astype(str).str.strip() == sel].copy()
                        
                        # KPIs
                        total_ordens_entregues = rec_of[c_rec_om].nunique()
                        total_pecas_entregues = int(pd.to_numeric(rec_of[c_rec_qtd], errors="coerce").fillna(0).sum())
                        
                        if c_rec_min:
                            total_minutos_entregues = int(pd.to_numeric(rec_of[c_rec_min], errors="coerce").fillna(0).sum())
                        else:
                            total_minutos_entregues = 0

                        st.markdown("")
                        st.markdown(f'<div class="sec">Resumo de Entregas da {sel}</div>', unsafe_allow_html=True)
                        
                        rk1, rk2, rk3 = st.columns(3)
                        rk1.markdown(f'<div class="kpi-wrap"><div class="kpi-lbl">Total de Ordens Entregues</div><div class="kpi-val" style="color:#10b981">{fmt(total_ordens_entregues)}</div></div>', unsafe_allow_html=True)
                        rk2.markdown(f'<div class="kpi-wrap"><div class="kpi-lbl">Total de Peças Entregues</div><div class="kpi-val" style="color:#00e5cc">{fmt(total_pecas_entregues)}</div></div>', unsafe_allow_html=True)
                        rk3.markdown(f'<div class="kpi-wrap"><div class="kpi-lbl">Total de Minutos Entregues</div><div class="kpi-val" style="color:#c084fc">{fmt(total_minutos_entregues)}</div></div>', unsafe_allow_html=True)

                        # Botão para exportar recebimento em formato executivo
                        st.markdown("")
                        st.download_button(
                            "Exportar Recebimento (.xlsx)",
                            data=exportar_recebimento(rec_of, c_rec_om, c_rec_qtd, c_rec_min, c_rec_dia),
                            file_name=f"recebimento_{sel.replace(' ', '_')}_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=False,
                        )

                        # Tabela
                        if not rec_of.empty:
                            st.markdown("")
                            st.markdown(f'<div class="sec">Histórico de Recebimento da {sel}</div>', unsafe_allow_html=True)
                            r_rows = ""
                            for _, dr in rec_of.iterrows():
                                om_val  = dr[c_rec_om]
                                qtd_val = pd.to_numeric(dr[c_rec_qtd], errors="coerce")
                                qtd_val = int(qtd_val) if not pd.isna(qtd_val) else 0
                                min_val = pd.to_numeric(dr[c_rec_min], errors="coerce") if c_rec_min else 0
                                min_val = int(min_val) if not pd.isna(min_val) else 0
                                dia_fmt = fmtDate(dr[c_rec_dia])

                                r_rows += (
                                    f"<tr>"
                                    f"<td>{om_val}</td>"
                                    f"<td class='tr' style='color:#00e5cc;font-weight:600'>{fmt(qtd_val)} pc</td>"
                                    f"<td class='tr'>{fmt(min_val)} min</td>"
                                    f"<td class='tr' style='color:#94a3b8'>{dia_fmt}</td>"
                                    f"</tr>"
                                )
                            
                            st.markdown(
                                f"<div style='overflow-x:auto'>"
                                f"<table class='tbl'><thead><tr>"
                                f"<th>Ordem Mestre (OM)</th>"
                                f"<th class='tr'>Qtd Entregue (Peças)</th>"
                                f"<th class='tr'>Minutos</th>"
                                f"<th class='tr'>Data de Entrega (Dia)</th>"
                                f"</tr></thead><tbody>{r_rows}</tbody></table></div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.info("Nenhuma ordem entregue registrada para esta oficina.")
                    else:
                        st.warning("⚠️ Colunas obrigatórias para o histórico de recebimento não foram encontradas na planilha.")
                else:
                    st.warning("⚠️ Planilha de Recebimento está vazia ou não pôde ser carregada.")
    else:
        st.markdown('<div class="card" style="text-align:center;padding:2rem;">'
                    '<p><span class="material-symbols-outlined" style="font-size:48px; color:#94a3b8;">note_add</span></p>'
                    '<p style="color:#94a3b8;margin-top:.5rem">Importe os <strong>três</strong> arquivos na aba <strong>Importar & Filtrar</strong> para começar a análise</p>'
                    '</div>', unsafe_allow_html=True)
