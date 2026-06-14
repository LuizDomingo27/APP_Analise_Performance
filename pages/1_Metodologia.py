import streamlit as st
from src.auth import verificar_autenticacao

st.set_page_config(page_title="Metodologia - Simulador de Metas", page_icon=":material/library_books:", layout="wide")

if not verificar_autenticacao("Metodologia"):
    st.stop()

st.markdown("""
# :material/library_books: Metodologia e Cálculo de Probabilidade

É fundamental que os dados não pareçam uma "caixa preta" mágica. O cálculo de probabilidade de entrega criado para o simulador é baseado em princípios de **Gestão de Capacidade (Capacity Management)** e heurísticas de **Análise de Risco Operacional**.

Aqui está a explicação de como a engrenagem funciona:

---

## 1. O Core do Cálculo: A Razão de Carga (Load Ratio)
A técnica principal utilizada é a **Razão de Capacidade sobre Demanda**. Nós não "chutamos" um número; nós comparamos exatamente o "tamanho do cano" com o "volume de água" que precisa passar por ele.

**A Fórmula Base:**
> `Razão = Capacidade Total no Prazo / Total de Peças Pendentes (Demanda)`

- **Capacidade Total no Prazo:** É o quanto a oficina consegue produzir (*Peças por Dia*) multiplicado pela quantidade média de *dias* que ela tem de prazo.
- **Peças Pendentes:** O que ainda falta entregar (já abatendo o que foi pro Recebimento).

---

## 2. Mapeamento de Risco em Faixas Empíricas
Em engenharia de produção, sabemos que planejar usar exatamente 100% da sua capacidade é arriscado (se uma máquina quebrar ou faltar energia, a meta falha). Por isso, usamos uma **Distribuição Empírica em Faixas** para converter a Razão de Carga em um percentual de Probabilidade:

| Razão de Carga | Significado Prático | Probabilidade Base |
| :--- | :--- | :--- |
| **≥ 1.50** | Sobra 50% ou mais de capacidade. | **97%** (Quase certeza de entrega) |
| **≥ 1.20** | Sobra 20% de capacidade. | **88%** (Alta chance, margem segura) |
| **≥ 1.00** | Capacidade empata com a demanda. | **72%** (Chance boa, sem margem de erro) |
| **≥ 0.85** | Falta 15% de capacidade. | **52%** (Risco moderado. Exige hora extra) |
| **≥ 0.70** | Falta 30% de capacidade. | **35%** (Alto risco de atraso parcial) |
| **< 0.50** | Capacidade é metade da demanda. | **8%** (Entrega inviável no prazo estipulado) |

---

## 3. O Fator de Resiliência (Ajuste por Colaboradores)
Aqui aplicamos um princípio inspirado na **Lei dos Grandes Números**. 
Uma oficina com 2 trabalhadores que tem alguém doente perde 50% da sua força de trabalho. Uma oficina com 20 trabalhadores que tem alguém doente perde apenas 5%. Oficinas maiores são estatisticamente mais resilientes a flutuações e imprevistos.

Por isso, o algoritmo aplica um ajuste fino no final:
- **Equipes Grandes (20 ou mais pessoas):** Ganham **+5%** de bônus de probabilidade.
- **Equipes Médias (10 a 19 pessoas):** Ganham **+2%** de bônus.
- **Equipes Pequenas (menos de 10 pessoas):** Sofrem uma penalidade de **-3%** de probabilidade por serem mais vulneráveis a faltas.

---

## :material/precision_manufacturing: Exemplo Real A (Cenário Seguro)
* **Oficina:** Alpha
* **Capacidade:** 200 peças/dia
* **Prazo Médio:** 10 dias
* **Peças Pendentes (Saldo):** 1.500 peças
* **Trabalhadores:** 25

**O Cálculo Passo a Passo:**
1. Capacidade no Prazo = 200 * 10 = **2.000 peças possíveis.**
2. Razão (Load Ratio) = 2.000 / 1.500 = **1.33** *(Têm 33% a mais de capacidade do que o necessário).*
3. Olhando a nossa tabela: 1.33 cai na faixa "Razão ≥ 1.20", que dá uma **Probabilidade Base de 88%**.
4. Ajuste de Resiliência: Como tem 25 trabalhadores (Equipe Grande), ganha **+5%**.
5. **Resultado Final:** Probabilidade de **93% (Entrega Viável)**.

---

## :material/precision_manufacturing: Exemplo Real B (Cenário Crítico)
* **Oficina:** Beta
* **Capacidade:** 100 peças/dia
* **Prazo Médio:** 5 dias
* **Peças Pendentes (Saldo):** 800 peças
* **Trabalhadores:** 8

**O Cálculo Passo a Passo:**
1. Capacidade no Prazo = 100 * 5 = **500 peças possíveis.**
2. Razão = 500 / 800 = **0.62** *(Têm apenas 62% da capacidade necessária).*
3. Olhando a tabela: 0.62 cai na faixa "Razão ≥ 0.50", que dá uma **Probabilidade Base de 18%**.
4. Ajuste de Resiliência: Como tem só 8 trabalhadores (Equipe Pequena), sofre penalidade de **-3%**.
5. **Resultado Final:** Probabilidade de **15% (Alto Risco)**. O sistema vai avisar que há um déficit e sugerir realocação.

---

<br><br>
<p style="color:#94a3b8;font-size:12px;text-align:center;">
<b>Resumo Técnico:</b> A técnica principal é uma combinação de <i>Load Ratio Analysis</i> (Análise de Fator de Carga) com <i>Rule-Based Weighted Heuristics</i> (Heurística Ponderada Baseada em Regras).
</p>
""", unsafe_allow_html=True)
