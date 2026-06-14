"""
Script para geração de dados MOCK consistentes entre as três bases:
  - CONTROLE.xlsx      → Capacidade das oficinas
  - ACOMPANHAMENTO.xlsx → Ordens de produção abertas
  - RECEBIMENTO.xlsx   → Registros reais de entrega por ordem/dia

Execute: python create_mock.py
Os arquivos serão salvos em data/
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
Path("data").mkdir(exist_ok=True)

# ─── PARÂMETROS ────────────────────────────────────────────────────────────────
OFICINAS = [
    {"OFICINA": "Oficina Alpha",    "COLABORADORES": 22, "CAP_DIA": 400, "CAP_SEMANAL": 2000},
    {"OFICINA": "Oficina Beta",     "COLABORADORES": 14, "CAP_DIA": 280, "CAP_SEMANAL": 1400},
    {"OFICINA": "Oficina Gamma",    "COLABORADORES": 8,  "CAP_DIA": 150, "CAP_SEMANAL":  750},
    {"OFICINA": "Oficina Delta",    "COLABORADORES": 30, "CAP_DIA": 600, "CAP_SEMANAL": 3000},
    {"OFICINA": "Oficina Epsilon",  "COLABORADORES": 18, "CAP_DIA": 360, "CAP_SEMANAL": 1800},
    {"OFICINA": "Oficina Zeta",     "COLABORADORES": 11, "CAP_DIA": 220, "CAP_SEMANAL": 1100},
]

MATERIAS_PRIMAS = ["Algodão 30/1", "Poliester 50D", "Viscose 40/1", "Malha PV", "Ribana 2x1", "Moletom 2F"]

# ─── BASE 1: CONTROLE ──────────────────────────────────────────────────────────
df_controle = pd.DataFrame(OFICINAS, columns=["OFICINA", "COLABORADORES", "CAP_DIA", "CAP_SEMANAL"])
df_controle.to_excel("data/CONTROLE.xlsx", index=False)
print("[OK] data/CONTROLE.xlsx criado.")

# ─── BASE 2: ACOMPANHAMENTO ────────────────────────────────────────────────────
ordens = []
ordem_num = 1000

for of in OFICINAS:
    n_ordens = random.randint(8, 18)
    for _ in range(n_ordens):
        qtd  = random.randint(80, 500)
        mins = int(qtd * random.uniform(0.8, 1.5))
        prazo = random.randint(5, 25)
        ordens.append({
            "ORDEM MESTRE":                ordem_num,
            "OFICINA":                     of["OFICINA"],
            "MP":                          random.choice(MATERIAS_PRIMAS),
            "QTD PECAS":                   qtd,
            "MINUTOS":                     mins,
            "PRAZO DIAS":                  prazo,
            "STATUS ORDEM":                "Em andamento",
        })
        ordem_num += 1

df_acomp = pd.DataFrame(ordens)
df_acomp.to_excel("data/ACOMPANHAMENTO.xlsx", index=False)
print("[OK] data/ACOMPANHAMENTO.xlsx criado.")

# ─── BASE 3: RECEBIMENTO ──────────────────────────────────────────────────────
# Para cada ordem, gera 1–3 lançamentos parciais de entrega ao longo dos dias
recebimentos = []
data_base = datetime(2026, 5, 1)

for _, ordem_row in df_acomp.iterrows():
    qtd_solicitada = int(ordem_row["QTD PECAS"])
    oficina        = ordem_row["OFICINA"]
    ordem_id       = int(ordem_row["ORDEM MESTRE"])
    mp             = ordem_row["MP"]

    # Define se a oficina vai atingir >= 60% (70% dos casos sim, 30% não)
    atingiu_meta = random.random() < 0.70
    if atingiu_meta:
        pct_entregue = random.uniform(0.60, 1.05)
    else:
        pct_entregue = random.uniform(0.10, 0.59)

    qtd_total_entregue = int(qtd_solicitada * pct_entregue)
    n_lancamentos      = random.randint(1, 3)
    qtds_parc          = sorted(random.sample(range(1, max(qtd_total_entregue, n_lancamentos + 1)), min(n_lancamentos, qtd_total_entregue)))

    acumulado = 0
    for i, qtd_parc in enumerate(qtds_parc):
        entregue = qtd_parc if i < len(qtds_parc) - 1 else qtd_total_entregue - acumulado
        if entregue <= 0:
            continue
        mins_parc = int(entregue * random.uniform(0.8, 1.4))
        dia       = data_base + timedelta(days=random.randint(0, 25))

        recebimentos.append({
            "DIA":              dia.strftime("%d/%m/%Y"),
            "OFICINA":          oficina,
            "ORDEM MESTRE":     ordem_id,
            "REAL CORTADO":     entregue,
            "MIN":              mins_parc,
            "MP":               mp,
        })
        acumulado += entregue

df_recebimento = pd.DataFrame(recebimentos)
df_recebimento.to_excel("data/RECEBIMENTO.xlsx", index=False)
print("[OK] data/RECEBIMENTO.xlsx criado.")
print(f"\nResumo do Mock:")
print(f"  Oficinas:          {len(OFICINAS)}")
print(f"  Ordens abertas:    {len(df_acomp)}")
print(f"  Lançamentos rec.:  {len(df_recebimento)}")
