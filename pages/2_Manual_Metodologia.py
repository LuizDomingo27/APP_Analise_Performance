import streamlit as st
from src.auth import verificar_autenticacao

st.set_page_config(
    page_title="Manual de Metodologia – Simulador de Metas",
    page_icon=":material/menu_book:",
    layout="wide",
)

if not verificar_autenticacao("Manual_Metodologia"):
    st.stop()

# ── CSS da página ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');

html, body, [class*="css"] { 
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
    font-size: 15px; 
}
.stApp { background: #0f0f1a; color: #f0f0ff; }

.doc-hero {
    background: linear-gradient(135deg, #1a1040 0%, #0f1a30 100%);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
}
.doc-hero h1 { font-size: 28px; font-weight: 700; color: #fff; margin: 0 0 6px; }
.doc-hero p  { color: #94a3b8; font-size: 14px; margin: 0; }
.doc-hero .tag {
    display: inline-block;
    background: rgba(124,58,237,0.2);
    border: 1px solid rgba(124,58,237,0.4);
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 12px;
    color: #c084fc;
    margin-bottom: 10px;
}

.section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 700;
    color: #00e5cc;
    border-bottom: 2px solid rgba(0,229,204,0.2);
    padding-bottom: 10px;
    margin: 2rem 0 1rem;
}
.section-title .material-symbols-outlined { font-size: 24px; }

.formula-box {
    background: #1a1a35;
    border: 1px solid rgba(124,58,237,0.4);
    border-left: 4px solid #7c3aed;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    font-family: 'Courier New', monospace;
    font-size: 16px;
    color: #e2e8f0;
}
.formula-box .label {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: #7c3aed;
    margin-bottom: 6px;
}

.info-card {
    background: #161628;
    border: 1px solid rgba(0,229,204,0.15);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: .8rem;
}
.info-card h4 {
    font-size: 14px;
    font-weight: 600;
    color: #00e5cc;
    margin: 0 0 6px;
}
.info-card p {
    font-size: 14px;
    color: #94a3b8;
    line-height: 1.7;
    margin: 0;
}

.example-block {
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin: 1rem 0;
}
.ex-green { background: rgba(16,185,129,0.07); border: 1px solid rgba(16,185,129,0.2); }
.ex-red   { background: rgba(239,68,68,0.07);  border: 1px solid rgba(239,68,68,0.2); }

.step {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 12px;
}
.step-num {
    background: #7c3aed;
    color: #fff;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    font-size: 12px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
}
.step-txt { font-size: 14px; color: #cbd5e1; line-height: 1.7; }
.step-txt strong { color: #f0f0ff; }

.ratio-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    margin: 1rem 0;
}
.ratio-table th {
    background: #7c3aed;
    color: #fff;
    padding: 9px 14px;
    text-align: center;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: .05em;
}
.ratio-table td {
    padding: 9px 14px;
    color: #f0f0ff;
    border-bottom: 1px solid rgba(0,229,204,0.09);
    text-align: center;
}
.ratio-table tr:nth-child(even) td { background: #1c1c35; }
.ratio-table tr:nth-child(odd)  td { background: #161628; }

.badge-ok   { background: rgba(16,185,129,0.15); color: #10b981; border-radius: 20px; padding: 3px 12px; font-size: 12px; font-weight: 600; }
.badge-warn { background: rgba(245,158,11,0.15);  color: #f59e0b; border-radius: 20px; padding: 3px 12px; font-size: 12px; font-weight: 600; }
.badge-bad  { background: rgba(239,68,68,0.15);   color: #ef4444; border-radius: 20px; padding: 3px 12px; font-size: 12px; font-weight: 600; }

.callout {
    background: rgba(0,229,204,0.06);
    border: 1px solid rgba(0,229,204,0.2);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 14px;
    color: #94a3b8;
    line-height: 1.7;
    margin: 1rem 0;
}
.callout strong { color: #00e5cc; }
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="doc-hero">
    <div class="tag">Documento Técnico — Uso Interno</div>
    <h1><span class="material-symbols-outlined" style="vertical-align:-5px;font-size:28px;color:#c084fc;">menu_book</span>
        Manual de Metodologia do Simulador de Metas</h1>
    <p>Explica de forma detalhada as regras de negócio, fórmulas matemáticas e critérios de decisão
       utilizados pelo sistema para calcular indicadores de capacidade, risco e performance por oficina.</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 — ABATIMENTO DE SALDO
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-title">
    <span class="material-symbols-outlined">calculate</span>
    1. Como o Sistema Calcula o Saldo Pendente (Abatimento)
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color:#94a3b8;font-size:13px;line-height:1.8;">
O simulador <strong style="color:#f0f0ff">não trabalha com o pedido original</strong>.
Ele desconta automaticamente tudo que já foi entregue (registrado na planilha de Recebimento)
e calcula o <strong style="color:#00e5cc">Saldo Pendente Real</strong> de cada Ordem.
</p>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="info-card">
        <h4><span class="material-symbols-outlined" style="font-size:14px;vertical-align:-2px;">source</span> Origem dos Dados</h4>
        <p>
            <strong style="color:#f0f0ff">Planilha de Acompanhamento:</strong> contém todas as Ordens de Serviço
            com a quantidade <em>solicitada</em> de peças para cada oficina.<br><br>
            <strong style="color:#f0f0ff">Planilha de Recebimento:</strong> contém tudo que já foi
            <em>entregue/cortado</em> até o momento, agrupado por Ordem Mestre.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="formula-box">
        <div class="label">Fórmula do Abatimento</div>
        Saldo Pendente = Qtd Solicitada − Qtd Entregue<br><br>
        <span style="color:#94a3b8;font-size:12px">
        Se o resultado for negativo, o sistema considera zero<br>
        (a ordem já foi 100% concluída e sai da fila de risco).
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="callout">
    <strong>Exemplo prático:</strong> A Ordem Mestre 5001 foi aberta com 1.000 peças.
    Até hoje, 400 foram entregues e registradas no Recebimento.
    O sistema vai calcular: <strong>1.000 − 400 = 600 peças pendentes</strong>.
    Todo o cálculo de capacidade, folga e probabilidade vai usar esses 600 como base, não os 1.000 originais.
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 — CONSUMO PERCENTUAL DA CAPACIDADE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-title">
    <span class="material-symbols-outlined">donut_large</span>
    2. Como é Calculado o Consumo Percentual da Capacidade
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color:#94a3b8;font-size:13px;line-height:1.8;">
O consumo percentual responde à pergunta: <strong style="color:#00e5cc">"Se a oficina usar toda a sua capacidade
no prazo disponível, quanto dessa capacidade será ocupada pelo saldo pendente?"</strong>
</p>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="formula-box">
        <div class="label">Passo 1 — Capacidade no Prazo</div>
        Capacidade no Prazo = Peças/Dia × Prazo Médio (dias)<br><br>
        <span style="color:#94a3b8;font-size:12px">
        Representa o máximo que a oficina consegue produzir 
        dentro do prazo restante das ordens.
        </span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="formula-box">
        <div class="label">Passo 2 — Consumo Percentual</div>
        Consumo % = (Saldo Pendente ÷ Capacidade no Prazo) × 100<br><br>
        <span style="color:#94a3b8;font-size:12px">
        Limitado a 100%. Se ultrapassar, significa que há déficit
        e a oficina não consegue entregar tudo no prazo.
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="example-block ex-green">
    <strong style="color:#10b981">Exemplo Prático (Cenário Tranquilo):</strong><br>
    <div style="margin-top:10px">
    <div class="step"><div class="step-num">1</div><div class="step-txt">
        Oficina Alpha produz <strong>200 peças/dia</strong> e o prazo médio das ordens é de <strong>15 dias</strong>.
    </div></div>
    <div class="step"><div class="step-num">2</div><div class="step-txt">
        Capacidade no Prazo = 200 × 15 = <strong>3.000 peças possíveis de produzir</strong>.
    </div></div>
    <div class="step"><div class="step-num">3</div><div class="step-txt">
        Saldo Pendente após abatimento = <strong>1.800 peças</strong>.
    </div></div>
    <div class="step"><div class="step-num">4</div><div class="step-txt">
        Consumo % = (1.800 ÷ 3.000) × 100 = <strong>60% da capacidade está comprometida</strong>.
        Os outros 40% estão livres (folga).
    </div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 — FOLGA E DÉFICIT
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-title">
    <span class="material-symbols-outlined">balance</span>
    3. Como é Calculada a Folga e o Déficit no Saldo de Peças
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color:#94a3b8;font-size:13px;line-height:1.8;">
A Folga e o Déficit são a mesma fórmula, com resultados opostos.
Eles respondem: <strong style="color:#00e5cc">"Sobram ou faltam peças de capacidade para cumprir tudo no prazo?"</strong>
</p>
""", unsafe_allow_html=True)

st.markdown("""
<div class="formula-box">
    <div class="label">Fórmula Única — Folga / Déficit</div>
    Resultado = Capacidade no Prazo − Saldo Pendente<br><br>
    <span style="color:#10b981">► Resultado POSITIVO → <strong>FOLGA</strong> (sobra capacidade, entrega no prazo garantida)</span><br>
    <span style="color:#ef4444">► Resultado NEGATIVO → <strong>DÉFICIT</strong> (falta capacidade, precisa de hora extra ou realocação)</span>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="example-block ex-green">
        <strong style="color:#10b981">Cenário com FOLGA</strong><br>
        <div style="margin-top:10px;font-size:13px;color:#94a3b8;line-height:1.8;">
        Capacidade no Prazo = <strong style="color:#f0f0ff">3.000 peças</strong><br>
        Saldo Pendente = <strong style="color:#f0f0ff">1.800 peças</strong><br>
        Resultado = 3.000 − 1.800 = <strong style="color:#10b981">+1.200 (FOLGA)</strong><br><br>
        A oficina tem fôlego para absorver novos pedidos ou imprevistos.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="example-block ex-red">
        <strong style="color:#ef4444">Cenário com DÉFICIT</strong><br>
        <div style="margin-top:10px;font-size:13px;color:#94a3b8;line-height:1.8;">
        Capacidade no Prazo = <strong style="color:#f0f0ff">500 peças</strong><br>
        Saldo Pendente = <strong style="color:#f0f0ff">800 peças</strong><br>
        Resultado = 500 − 800 = <strong style="color:#ef4444">−300 (DÉFICIT)</strong><br><br>
        Faltam 300 peças de capacidade. O sistema sinaliza necessidade de ação imediata.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 — PROBABILIDADE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-title">
    <span class="material-symbols-outlined">analytics</span>
    4. Como é Calculada a Probabilidade de Entrega
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color:#94a3b8;font-size:13px;line-height:1.8;">
A probabilidade utiliza a técnica de <strong style="color:#f0f0ff">Load Ratio Analysis
(Análise de Fator de Carga)</strong> combinada com <strong style="color:#f0f0ff">Heurística Ponderada</strong>.
O processo ocorre em dois passos:
</p>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.1])
with col1:
    st.markdown("""
    <div class="formula-box">
        <div class="label">Passo 1 — Calcular a Razão de Carga</div>
        Razão = Capacidade no Prazo ÷ Saldo Pendente<br><br>
        <span style="color:#94a3b8;font-size:12px">
        Razão > 1 = há mais capacidade do que demanda → baixo risco.<br>
        Razão < 1 = há mais demanda do que capacidade → alto risco.
        </span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="formula-box">
        <div class="label">Passo 2 — Ajuste por Resiliência da Equipe</div>
        Prob. Final = Prob. Base + Bônus/Penalidade<br><br>
        <span style="color:#10b981">≥ 20 colaboradores: +5% (mais resistente a faltas)</span><br>
        <span style="color:#f59e0b">10 a 19 colaboradores: +2%</span><br>
        <span style="color:#ef4444">< 10 colaboradores: −3% (mais vulnerável a imprevistos)</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""<p style="color:#94a3b8;font-size:12px;margin-bottom:8px;">
TABELA DE CONVERSÃO — Razão de Carga → Probabilidade Base</p>""", unsafe_allow_html=True)

st.markdown("""
<table class="ratio-table">
    <tr>
        <th>Razão de Carga</th>
        <th>Significado</th>
        <th>Probabilidade Base</th>
        <th>Nível de Risco</th>
    </tr>
    <tr>
        <td><strong>≥ 1.50</strong></td>
        <td>Sobra 50%+ de capacidade</td>
        <td><span class="badge-ok">97%</span></td>
        <td>Seguro</td>
    </tr>
    <tr>
        <td><strong>≥ 1.20</strong></td>
        <td>Sobra 20% de capacidade</td>
        <td><span class="badge-ok">88%</span></td>
        <td>Seguro</td>
    </tr>
    <tr>
        <td><strong>≥ 1.00</strong></td>
        <td>Capacidade empata com a demanda</td>
        <td><span class="badge-ok">72%</span></td>
        <td>Atenção</td>
    </tr>
    <tr>
        <td><strong>≥ 0.85</strong></td>
        <td>Falta 15% de capacidade</td>
        <td><span class="badge-warn">52%</span></td>
        <td>Moderado</td>
    </tr>
    <tr>
        <td><strong>≥ 0.70</strong></td>
        <td>Falta 30% de capacidade</td>
        <td><span class="badge-warn">35%</span></td>
        <td>Alto</td>
    </tr>
    <tr>
        <td><strong>≥ 0.50</strong></td>
        <td>Capacidade é metade da demanda</td>
        <td><span class="badge-bad">18%</span></td>
        <td>Crítico</td>
    </tr>
    <tr>
        <td><strong>< 0.50</strong></td>
        <td>Entrega inviável no prazo</td>
        <td><span class="badge-bad">8%</span></td>
        <td>Crítico</td>
    </tr>
</table>
""", unsafe_allow_html=True)

st.markdown("""
<div class="example-block ex-green" style="margin-top:1.5rem">
    <strong style="color:#10b981">Exemplo Completo de Probabilidade:</strong>
    <div style="margin-top:10px">
    <div class="step"><div class="step-num">1</div><div class="step-txt">
        Oficina Alpha: Capacidade no Prazo = <strong>3.000</strong> peças | Saldo Pendente = <strong>2.000</strong> peças | Colaboradores = <strong>25</strong>
    </div></div>
    <div class="step"><div class="step-num">2</div><div class="step-txt">
        Razão = 3.000 ÷ 2.000 = <strong>1.50</strong> → Probabilidade Base = <strong>97%</strong>
    </div></div>
    <div class="step"><div class="step-num">3</div><div class="step-txt">
        Ajuste de equipe: 25 colaboradores (≥ 20) → <strong>+5%</strong>
    </div></div>
    <div class="step"><div class="step-num">4</div><div class="step-txt">
        Probabilidade Final = 97% + 5% = <strong style="color:#10b981">99% (limitado ao máximo de 99%)</strong>
    </div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5 — STATUS VIÁVEL
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-title">
    <span class="material-symbols-outlined">verified</span>
    5. Como é Definido o Status (Viável / Risco Moderado / Alto Risco)
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color:#94a3b8;font-size:13px;line-height:1.8;">
O Status é a classificação final que resume, em uma palavra, o risco de atraso de uma oficina.
Ele é determinado <strong style="color:#f0f0ff">exclusivamente com base na Probabilidade Final</strong> calculada no passo anterior.
</p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="info-card" style="border-color: rgba(16,185,129,0.3); text-align:center;">
        <span class="material-symbols-outlined" style="color:#10b981;font-size:36px;">check_circle</span>
        <h4 style="color:#10b981;font-size:15px;margin-top:6px;">ENTREGA VIÁVEL</h4>
        <p style="text-align:center;"><strong style="color:#f0f0ff">Probabilidade ≥ 75%</strong><br><br>
        A oficina tem capacidade suficiente e alta chance de entregar tudo no prazo.
        Nenhuma ação urgente é necessária.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card" style="border-color: rgba(245,158,11,0.3); text-align:center;">
        <span class="material-symbols-outlined" style="color:#f59e0b;font-size:36px;">warning</span>
        <h4 style="color:#f59e0b;font-size:15px;margin-top:6px;">RISCO MODERADO</h4>
        <p style="text-align:center;"><strong style="color:#f0f0ff">Probabilidade entre 50% e 74%</strong><br><br>
        A oficina consegue entregar, mas está no limite. Qualquer imprevisto pode atrasar.
        Recomenda-se monitoramento.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-card" style="border-color: rgba(239,68,68,0.3); text-align:center;">
        <span class="material-symbols-outlined" style="color:#ef4444;font-size:36px;">cancel</span>
        <h4 style="color:#ef4444;font-size:15px;margin-top:6px;">ALTO RISCO</h4>
        <p style="text-align:center;"><strong style="color:#f0f0ff">Probabilidade < 50%</strong><br><br>
        A oficina não tem capacidade suficiente. É necessária ação imediata: hora extra,
        realocação de ordens ou negociação de prazo.</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 6 — PERFORMANCE (EFICIÊNCIA)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-title">
    <span class="material-symbols-outlined">trending_up</span>
    6. Como é Calculada a Performance (Eficiência) da Oficina
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p style="color:#94a3b8;font-size:13px;line-height:1.8;">
A <strong style="color:#f0f0ff">Performance (ou Eficiência)</strong> mede o quanto cada Ordem de Serviço
foi cumprida em relação ao que foi solicitado. A meta de eficiência da empresa é de <strong style="color:#00e5cc">60%</strong>.
Isso significa que uma oficina precisa entregar pelo menos 60% do volume solicitado em cada ordem para
ser considerada dentro do padrão aceitável.
</p>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="formula-box">
        <div class="label">Eficiência por Ordem (PCT Entregue)</div>
        % Entregue = (Qtd Entregue ÷ Qtd Solicitada) × 100<br><br>
        <span style="color:#10b981">≥ 60% → Aceitável</span><br>
        <span style="color:#f59e0b">40% a 59% → Atenção</span><br>
        <span style="color:#ef4444">< 40% → Abaixo da Meta</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="formula-box">
        <div class="label">Performance Global da Oficina</div>
        % Ordens na Meta = (Ordens ≥ 60%) ÷ (Total de Ordens) × 100<br><br>
        <span style="color:#94a3b8;font-size:12px">
        Indica a proporção de ordens onde a oficina cumpriu
        a meta mínima de 60% de entrega.
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="callout" style="margin-top:1rem">
    <strong>Exemplo de Eficiência:</strong><br>
    A Oficina Beta tem 10 ordens. Das 10, em 7 delas ela entregou 60% ou mais do solicitado.
    Em 3 delas ficou abaixo dos 60%.<br>
    <strong>Performance Global = (7 ÷ 10) × 100 = 70% das ordens dentro da meta.</strong><br>
    A Eficiência Média é calculada como a média do % entregue de todas as ordens daquela oficina.
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RODAPÉ
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid rgba(0,229,204,0.15);padding-top:1.2rem;text-align:center;">
    <p style="color:#475569;font-size:11px;">
        <strong style="color:#94a3b8">Simulador de Metas — Uso Interno</strong><br>
        Metodologia baseada em Load Ratio Analysis e Heurística Ponderada por Capacidade Produtiva.<br>
        Meta de Eficiência: 60% | Status Viável: Probabilidade ≥ 75%
    </p>
</div>
""", unsafe_allow_html=True)
