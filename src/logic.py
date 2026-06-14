import pandas as pd
from datetime import datetime
from typing import Tuple, Dict, Any, Optional

# ── Mapeamento EXATO das colunas das planilhas reais ──────────────────────────
# Estrutura real encontrada nos arquivos .xlsx em /data:
#
# ESTOQUE.xlsx       → ['OFICINA', 'COLABORADORES', 'CAP PECAS 65%', 'MP', 'CAP PEÇAS SEMANAL']
# ACOMPANHAMENTO.xlsx→ ['ORDEM MESTRE', 'OFICINA', 'ENVIO', 'QTD', 'MINUTOS', 'DEAD LINE', 'MP']
# RECEBIMENTO.xlsx   → ['DIA', 'OFICINA', 'ORDEM MESTRE', 'MP', 'REAL CORTADO', 'MINUTOS']
#
# Cada entrada na variante inclui o nome exato da coluna PRIMEIRO, seguido de
# alternativas para compatibilidade com versões antigas ou arquivos legados.

V = {
    # ── ESTOQUE (planilha de capacidade/controle) ─────────────────────────────
    "oficina":   ["oficina", "nome", "unidade", "workshop", "grupo"],

    "trab":      ["colaboradores", "quantidade de trabalhadores", "trabalhadores", "qtd trab"],

    "cap_dia":   ["cap pecas 65%", "cap_pecas_65", "capacidade de pecas por dia",
                  "CAP PEÇAS 65", "cap dia", "cap_dia", "pecas por dia"],
                  
    "cap_sem":   ["cap peças semanal", "cap pecas semanal", "capacidade semanal",
                  "cap_pecas_semanal", "cap semanal"],

    # ── ACOMPANHAMENTO ────────────────────────────────────────────────────────
    "om":        ["ordem mestre", "om", "ordem", "order"],
    "of_acomp":  ["oficina", "grupo", "unidade"],
    "qtd_pecas": ["qtd", "qtd pecas", "quantidade de pecas", "qty", "pecas"],
    "minutos":   ["minutos", "min", "mins", "tempo", "minutes"],
    "envio":     ["envio", "data envio", "dt envio", "data de envio", "saida"],
    "deadline":  ["dead line", "deadline", "prazo", "prazo dias", "data limite",
                  "dt limite", "vencimento"],
    "acomp_mp":  ["mp", "materia prima", "material", "insumo"],

    # ── RECEBIMENTO ───────────────────────────────────────────────────────────
    "rec_dia":   ["dia", "data", "date", "dt"],
    "rec_of":    ["oficina", "grupo", "unidade", "workshop"],
    "rec_om":    ["ordem mestre", "ordem", "om", "order"],
    "rec_qtd":   ["real cortado", "real_cortado", "qtd entregue", "qtd", "entregue", "realizado"],
    "rec_min":   ["minutos", "min", "mins", "minutes"],
    "rec_mp":    ["mp", "materia prima", "material", "insumo"],
}

META_EFICIENCIA = 0.60  # 60% é o limiar de eficiência aceitável


# ── Funções de Normalização e Busca de Colunas ───────────────────────────────

def norm(s: str) -> str:
    """Normaliza strings para comparação (minúsculas, sem espaços extras)."""
    return str(s).lower().strip()


def find_col(cols: list, variants: list) -> Optional[str]:
    """
    Busca coluna na lista de colunas pelo mapeamento de variantes.
    Primeiro tenta match exato (normalizado), depois busca por substring.
    """
    cols_norm = {norm(c): c for c in cols}

    # 1ª passagem: match exato normalizado
    for v in variants:
        if norm(v) in cols_norm:
            return cols_norm[norm(v)]

    # 2ª passagem: variante contida no nome da coluna
    for c in cols:
        cn = norm(c)
        for v in variants:
            if norm(v) in cn:
                return c

    return None


def parse_date(val) -> Optional[datetime]:
    """Converte um valor (string ou datetime) para objeto datetime."""
    if pd.isna(val) or val is None:
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return pd.Timestamp(val).to_pydatetime()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(val).strip(), fmt)
        except ValueError:
            continue
    return None


def calcular_prazo_dias(envio_val, deadline_val, fallback: int = 30) -> int:
    """
    Calcula o prazo em dias como diferença entre DEAD LINE e ENVIO.
    Se qualquer data for inválida, retorna o fallback (padrão: 30 dias).
    """
    dt_envio    = parse_date(envio_val)
    dt_deadline = parse_date(deadline_val)
    if dt_envio and dt_deadline:
        delta = (dt_deadline - dt_envio).days
        return max(delta, 1)  # mínimo 1 dia
    return fallback


# ── Cálculo de KPIs ──────────────────────────────────────────────────────────

def calcular(
    cap_dia: float,
    colaboradores: int,
    total_pecas: float,
    prazo_medio_dias: float,
    cap_semanal: float = None,
) -> Optional[Dict[str, Any]]:
    """
    Calcula KPIs de capacidade e probabilidade de entrega de uma oficina.
    Baseado no SALDO PENDENTE (total_pecas descontado o recebimento real).

    Parâmetros:
        cap_dia          – Capacidade de produção por dia (CAP PECAS 65%)
        colaboradores    – Número de trabalhadores
        total_pecas      – Saldo pendente de peças (já descontado o recebido)
        prazo_medio_dias – Prazo médio em dias (DEAD LINE − ENVIO)
        cap_semanal      – Capacidade semanal (CAP PEÇAS SEMANAL); calculada se ausente

    Retorna:
        Dicionário com todos os KPIs ou None se cap_dia <= 0.
    """
    if cap_dia <= 0:
        return None

    cap_sem_val  = cap_semanal if cap_semanal else cap_dia * 5
    cap_no_prazo = cap_dia * prazo_medio_dias

    # Sem peças pendentes → capacidade sobrando, probabilidade máxima
    if total_pecas <= 0:
        return {
            "prob":                100,
            "cap_no_prazo":        cap_no_prazo,
            "folga":               cap_no_prazo,
            "dias_necessarios":    0.0,
            "semanas_necessarias": 0.0,
            "efic":                0.0,
            "ppc":                 cap_dia / colaboradores if colaboradores > 0 else 0,
            "ratio":               0.0,
            "cap_dia":             cap_dia,
            "cap_semanal":         cap_sem_val,
        }

    dias_necessarios    = total_pecas / cap_dia
    semanas_necessarias = dias_necessarios / 5
    ratio               = cap_no_prazo / total_pecas   # >1 = capacidade sobra
    folga               = cap_no_prazo - total_pecas   # + = folga, – = déficit
    # Consumo percentual da capacidade no prazo
    efic = min((total_pecas / cap_no_prazo) * 100, 100) if cap_no_prazo > 0 else 0
    ppc  = cap_dia / colaboradores if colaboradores > 0 else 0

    # ── Probabilidade base pelo ratio ────────────────────────────────────────
    # ratio ≥ 1 significa que a capacidade no prazo COBRE o saldo pendente
    if   ratio >= 1.5:  prob = 97
    elif ratio >= 1.2:  prob = 88
    elif ratio >= 1.0:  prob = 72
    elif ratio >= 0.85: prob = 52
    elif ratio >= 0.7:  prob = 35
    elif ratio >= 0.5:  prob = 18
    else:               prob = 8

    # ── Bônus/Penalidade por equipe ──────────────────────────────────────────
    bonus = 5 if colaboradores >= 20 else (2 if colaboradores >= 10 else -3)
    prob  = max(3, min(99, prob + bonus))

    return {
        "prob":                prob,
        "cap_no_prazo":        cap_no_prazo,
        "folga":               folga,
        "dias_necessarios":    dias_necessarios,
        "semanas_necessarias": semanas_necessarias,
        "efic":                efic,
        "ppc":                 ppc,
        "ratio":               ratio,
        "cap_dia":             cap_dia,
        "cap_semanal":         cap_sem_val,
    }


# ── Funções de Status/Performance ─────────────────────────────────────────────

def status_info(prob: int) -> Tuple[str, str, str, str, str]:
    if prob >= 75: return "Entrega viavel",  "#10b981", "pill-ok",   "badge-ok",   "alert-ok"
    if prob >= 50: return "Risco moderado",  "#f59e0b", "pill-warn", "badge-warn", "alert-warn"
    return              "Alto risco",        "#ef4444", "pill-bad",  "badge-bad",  "alert-bad"


def perf_info(pct: float) -> Tuple[str, str, str]:
    if pct >= 60: return "Aceitavel",      "#10b981", "pill-ok"
    if pct >= 40: return "Atencao",        "#f59e0b", "pill-warn"
    return             "Abaixo da Meta",   "#ef4444", "pill-bad"


# ── Aplicação de Cálculo por Linha ────────────────────────────────────────────

def _calc_row(row: pd.Series) -> pd.Series:
    """Aplica calcular() em uma linha do DataFrame (usado via apply)."""
    cap_dia  = float(row.get("CAP_DIA", 0))
    cap_sem  = float(row.get("CAP_SEMANAL", 0)) if "CAP_SEMANAL" in row else cap_dia * 5
    colab    = int(row.get("COLABORADORES", 0))
    total_pc = float(row.get("TOTAL_PECAS", 0))
    prazo    = float(row.get("PRAZO_MEDIO_DIAS", 30))
    if prazo <= 0:
        prazo = 30

    r = calcular(cap_dia, colab, total_pc, prazo, cap_sem)
    if r:
        return pd.Series([
            int(r["cap_no_prazo"]),
            round(r["dias_necessarios"], 1),
            round(r["semanas_necessarias"], 1),
            int(r["folga"]),
            round(r["efic"], 1),
            r["prob"],
            status_info(r["prob"])[0],
        ])
    return pd.Series([0, 0.0, 0.0, 0, 0.0, 0, "Sem dados"])


def _eficiencia_por_oficina(df_ordens: pd.DataFrame) -> Dict[str, Any]:
    total  = len(df_ordens)
    na_meta = int((df_ordens["PCT_ENTREGUE"] >= 60).sum())
    pct    = round(na_meta / total * 100, 1) if total > 0 else 0.0
    efic_m = round(df_ordens["PCT_ENTREGUE"].mean(), 1) if total > 0 else 0.0
    return {
        "ordens_na_meta":     na_meta,
        "total_ordens":       total,
        "pct_ordens_na_meta": pct,
        "efic_media":         efic_m,
    }


# ── Função Principal de Consolidação ─────────────────────────────────────────

def consolidar(
    df_estoque: pd.DataFrame,
    df_acomp:   pd.DataFrame,
    df_rec:     pd.DataFrame,
    filtro_mp:  str = None,
    mappings:   dict = None,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame], list, list]:
    """
    Consolida as três bases (ESTOQUE, ACOMPANHAMENTO, RECEBIMENTO) e calcula o ABATIMENTO.

    Regras de negócio:
    ─────────────────
    1. ABATIMENTO: O saldo pendente de cada Ordem Mestre é calculado como:
         QTD_PENDENTE = QTD (Acompanhamento) − REAL_CORTADO (Recebimento)
       O vínculo é feito por ORDEM MESTRE (presente em ambas as planilhas).

    2. PRAZO: O prazo em dias é calculado dinamicamente como:
         PRAZO_DIAS = DEAD LINE − ENVIO (ambas as datas do Acompanhamento)

    3. CAPACIDADE: Originada do ESTOQUE:
         CAP_DIA     = 'CAP PECAS 65%'
         CAP_SEMANAL = 'CAP PEÇAS SEMANAL'

    4. CONSUMO PERCENTUAL: Percentual do saldo pendente em relação à capacidade no prazo:
         CONSUMO% = (QTD_PENDENTE / CAP_NO_PRAZO) × 100

    5. FOLGA/DÉFICIT: Peças que sobram (positivo) ou faltam (negativo) na capacidade:
         FOLGA = CAP_NO_PRAZO − QTD_PENDENTE

    6. PROBABILIDADE: Calculada pelo ratio (CAP_NO_PRAZO / QTD_PENDENTE) com bônus por equipe.

    7. STATUS: 'Entrega viavel' se Prob ≥ 75%, 'Risco moderado' se ≥ 50%, 'Alto risco' abaixo.

    8. PERFORMANCE: Percentual de ordens que atingiram ≥ 60% de entrega (QTD_ENTREGUE / QTD).
    """
    if mappings is None:
        mappings = {}

    # ── 1. Detectar colunas automaticamente ──────────────────────────────────
    # ESTOQUE
    c_of_est   = mappings.get("c_of_est")   or find_col(df_estoque.columns, V["oficina"])
    c_trab     = mappings.get("c_trab")     or find_col(df_estoque.columns, V["trab"])
    c_cap_dia  = mappings.get("c_cap_dia")  or find_col(df_estoque.columns, V["cap_dia"])
    c_cap_sem  = mappings.get("c_cap_sem")  or find_col(df_estoque.columns, V["cap_sem"])

    # ACOMPANHAMENTO
    c_of_acomp = mappings.get("c_of_acomp") or find_col(df_acomp.columns, V["of_acomp"])
    c_om       = mappings.get("c_om")       or find_col(df_acomp.columns, V["om"])
    c_qtd      = mappings.get("c_qtd")      or find_col(df_acomp.columns, V["qtd_pecas"])
    c_min      = mappings.get("c_min")      or find_col(df_acomp.columns, V["minutos"])
    c_envio    = mappings.get("c_envio")    or find_col(df_acomp.columns, V["envio"])
    c_deadline = mappings.get("c_deadline") or find_col(df_acomp.columns, V["deadline"])
    c_ac_mp    = mappings.get("c_ac_mp")    or find_col(df_acomp.columns, V["acomp_mp"])

    # RECEBIMENTO
    c_rec_of   = mappings.get("c_rec_of")   or find_col(df_rec.columns, V["rec_of"])
    c_rec_om   = mappings.get("c_rec_om")   or find_col(df_rec.columns, V["rec_om"])
    c_rec_qtd  = mappings.get("c_rec_qtd")  or find_col(df_rec.columns, V["rec_qtd"])

    # ── 2. Validar colunas obrigatórias ───────────────────────────────────────
    missing = []
    if not c_of_est:   missing.append("OFICINA em ESTOQUE")
    if not c_trab:     missing.append("COLABORADORES em ESTOQUE")
    if not c_cap_dia:  missing.append("CAP PECAS 65% em ESTOQUE")
    if not c_of_acomp: missing.append("OFICINA em ACOMPANHAMENTO")
    if not c_om:       missing.append("ORDEM MESTRE em ACOMPANHAMENTO")
    if not c_qtd:      missing.append("QTD em ACOMPANHAMENTO")
    if not c_ac_mp:    missing.append("MP em ACOMPANHAMENTO")
    if not c_rec_om:   missing.append("ORDEM MESTRE em RECEBIMENTO")
    if not c_rec_qtd:  missing.append("REAL CORTADO em RECEBIMENTO")
    if missing:
        return None, None, None, missing, []

    # ── 3. Limpar e padronizar ESTOQUE ────────────────────────────────────────
    est = df_estoque.rename(columns={
        c_of_est:  "OFICINA",
        c_trab:    "COLABORADORES",
        c_cap_dia: "CAP_DIA",
    }).copy()

    # CAP_SEMANAL é opcional — se não existir, calcula como CAP_DIA × 5
    if c_cap_sem:
        est = est.rename(columns={c_cap_sem: "CAP_SEMANAL"})
    else:
        est["CAP_SEMANAL"] = 0  # será recalculado no _calc_row

    est = est[["OFICINA", "COLABORADORES", "CAP_DIA", "CAP_SEMANAL"]].copy()
    est["OFICINA"] = est["OFICINA"].astype(str).str.strip()
    for col in ["COLABORADORES", "CAP_DIA", "CAP_SEMANAL"]:
        est[col] = pd.to_numeric(est[col], errors="coerce").fillna(0)
        
    # Garantir que a oficina seja única no ESTOQUE (somando capacidade se houver mais de uma linha para a mesma oficina - ex: linhas separadas por MP)
    est = est.groupby("OFICINA", as_index=False).agg({
        "COLABORADORES": "sum",
        "CAP_DIA": "sum",
        "CAP_SEMANAL": "sum"
    })

    # ── 4. Limpar e padronizar ACOMPANHAMENTO ─────────────────────────────────
    acomp = df_acomp.copy()
    acomp["OFICINA"] = acomp[c_of_acomp].astype(str).str.strip()
    acomp["MP"]      = acomp[c_ac_mp].astype(str).str.strip()
    acomp[c_qtd]     = pd.to_numeric(acomp[c_qtd], errors="coerce").fillna(0)

    if c_min:
        acomp[c_min] = pd.to_numeric(acomp[c_min], errors="coerce").fillna(0)

    # Calcular prazo em dias a partir das datas ENVIO e DEAD LINE
    if c_envio and c_deadline:
        acomp["PRAZO_DIAS"] = acomp.apply(
            lambda r: calcular_prazo_dias(r[c_envio], r[c_deadline]),
            axis=1
        )
    else:
        acomp["PRAZO_DIAS"] = 30  # fallback padrão

    # ── Dias restantes até o DEAD LINE (a partir de hoje) ────────────────────
    hoje = pd.Timestamp.today().normalize()
    if c_deadline:
        acomp["DL_DATE"] = pd.to_datetime(
            acomp[c_deadline].astype(str).str.strip(),
            dayfirst=True,
            errors="coerce",
        )
        acomp["DIAS_PARA_VENCER"] = (acomp["DL_DATE"] - hoje).dt.days
    else:
        acomp["DIAS_PARA_VENCER"] = None

    # ── 5. Limpar e padronizar RECEBIMENTO ────────────────────────────────────
    rec = df_rec.copy()
    rec[c_rec_qtd] = pd.to_numeric(rec[c_rec_qtd], errors="coerce").fillna(0)

    # ── 6. Identificar lista única de MPs (antes do filtro) ───────────────────
    lista_mps = sorted(acomp["MP"].unique().tolist())

    # ── 7. ABATIMENTO: cruzar ACOMPANHAMENTO com RECEBIMENTO ─────────────────
    # Agrupa o total entregue por Ordem Mestre no Recebimento
    rec_agg = (
        rec.groupby(c_rec_om)[c_rec_qtd]
        .sum()
        .reset_index()
        .rename(columns={c_rec_om: c_om, c_rec_qtd: "QTD_ENTREGUE"})
    )

    # Merge: cada ordem do Acompanhamento recebe o total já entregue
    acomp = acomp.merge(rec_agg, on=c_om, how="left")
    acomp["QTD_ENTREGUE"] = acomp["QTD_ENTREGUE"].fillna(0)

    # Saldo pendente (mínimo 0)
    acomp["QTD_PENDENTE"] = (acomp[c_qtd] - acomp["QTD_ENTREGUE"]).clip(lower=0)

    # Minutos pendentes proporcionais ao saldo
    if c_min:
        acomp["MIN_PENDENTE"] = (
            acomp[c_min] * (acomp["QTD_PENDENTE"] / acomp[c_qtd].replace(0, 1))
        ).round(0)
    else:
        acomp["MIN_PENDENTE"] = 0

    # Percentual entregue por ordem (desempenho / performance)
    acomp["PCT_ENTREGUE"] = (
        (acomp["QTD_ENTREGUE"] / acomp[c_qtd].replace(0, 1)) * 100
    ).clip(upper=100).round(1)

    # ── 8. Aplicar filtro de MP ───────────────────────────────────────────────
    if filtro_mp and filtro_mp != "Todas":
        acomp = acomp[acomp["MP"] == filtro_mp].copy()

    # ── 9. Agregar saldo pendente por oficina ─────────────────────────────────
    # Considerar apenas ordens que AINDA têm peças pendentes
    acomp_pend = acomp[acomp["QTD_PENDENTE"] > 0].copy()

    df_agg = acomp_pend.groupby("OFICINA").agg(
        TOTAL_PECAS      = (c_qtd,               "sum"),
        TOTAL_MINUTOS    = ("MIN_PENDENTE",       "sum"),
        PRAZO_MEDIO_DIAS = ("PRAZO_DIAS",         "mean"),
        DIAS_PARA_VENCER = ("DIAS_PARA_VENCER",   "min"),  # prazo mais urgente da oficina
    ).reset_index()

    df_agg["PRAZO_MEDIO_DIAS"] = df_agg["PRAZO_MEDIO_DIAS"].round(0)

    df_counts = (
        acomp_pend.groupby("OFICINA")
        .size()
        .reset_index(name="TOTAL_ORDENS")
    )
    df_agg = df_agg.merge(df_counts, on="OFICINA")

    # ── 10. Juntar ESTOQUE + saldo agregado ───────────────────────────────────
    base = est.merge(df_agg, on="OFICINA", how="left").fillna(0)
    base = base[base["TOTAL_ORDENS"] > 0].copy()  # Apenas oficinas com saldo pendente

    # ── 11. Calcular KPIs de capacidade por oficina ───────────────────────────
    base[[
        "CAP_NO_PRAZO", "DIAS_NECESSARIOS", "SEMANAS_NECESSARIAS",
        "FOLGA_DEFICIT", "EFICIENCIA_PCT", "PROBABILIDADE_PCT", "STATUS"
    ]] = base.apply(_calc_row, axis=1)

    # ── 12. Gerar tabela de detalhes por ordem ────────────────────────────────
    detalhes      = []
    efic_oficinas = []

    for _, est_row in est.iterrows():
        of = est_row["OFICINA"]
        acomp_of = acomp[acomp["OFICINA"] == of].copy()

        if len(acomp_of) == 0:
            continue

        acomp_of["PERF_STATUS"], acomp_of["PERF_COR"], acomp_of["PERF_PILL"] = zip(
            *acomp_of["PCT_ENTREGUE"].apply(perf_info)
        )

        for _, ord_row in acomp_of.iterrows():
            detalhes.append({
                "ORDEM_MESTRE":     ord_row.get(c_om, "-"),
                "OFICINA":          of,
                "MP":               ord_row.get("MP", "-"),
                "QTD_PECAS":        int(ord_row.get(c_qtd, 0)),
                "QTD_ENTREGUE":     int(ord_row.get("QTD_ENTREGUE", 0)),
                "QTD_PENDENTE":     int(ord_row.get("QTD_PENDENTE", 0)),
                "PCT_ENTREGUE":     float(ord_row.get("PCT_ENTREGUE", 0)),
                "MINUTOS":          int(ord_row.get(c_min, 0)) if c_min else 0,
                "MIN_PENDENTE":     int(ord_row.get("MIN_PENDENTE", 0)),
                # ── Datas e prazos ────────────────────────────────────
                # PRAZO_DIAS: duração total da ordem (DEAD_LINE − ENVIO) – estático
                "PRAZO_DIAS":       int(ord_row.get("PRAZO_DIAS", 30)),
                # DIAS_PARA_VENCER: dias restantes até o prazo (DEAD_LINE − HOJE) – dinâmico
                # Calculado diretamente com parse_date() para garantir robustez
                # independente do formato de data no arquivo Excel.
                "DIAS_PARA_VENCER": (
                    (lambda dl: (dl - datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)).days
                     if dl else None)(
                        parse_date(ord_row[c_deadline]) if c_deadline else None
                    )
                ),
                "ENVIO":            str(ord_row.get(c_envio, "-")) if c_envio else "-",
                "DEAD_LINE":        str(ord_row.get(c_deadline, "-")) if c_deadline else "-",
                # ── Performance ──────────────────────────────────────
                "PERF_STATUS":      ord_row.get("PERF_STATUS", "-"),
                "PERF_COR":         ord_row.get("PERF_COR",    "#94a3b8"),
                "PERF_PILL":        ord_row.get("PERF_PILL",   "pill-warn"),
            })

        # Métricas de eficiência por oficina
        ef = _eficiencia_por_oficina(acomp_of)
        efic_oficinas.append({"OFICINA": of, **ef})

    df_detalhe    = pd.DataFrame(detalhes)    if detalhes      else pd.DataFrame()
    df_eficiencia = pd.DataFrame(efic_oficinas) if efic_oficinas else pd.DataFrame()

    # ── 13. Enriquecer base com eficiência ────────────────────────────────────
    if not df_eficiencia.empty:
        base = base.merge(df_eficiencia, on="OFICINA", how="left")
        base["ordens_na_meta"]     = base["ordens_na_meta"].fillna(0).astype(int)
        base["pct_ordens_na_meta"] = base["pct_ordens_na_meta"].fillna(0)
        base["efic_media"]         = base["efic_media"].fillna(0)

    # ── 14. Garantir tipos corretos ───────────────────────────────────────────
    for col in ["COLABORADORES", "CAP_DIA", "CAP_SEMANAL", "TOTAL_ORDENS", "TOTAL_PECAS"]:
        if col in base:
            base[col] = base[col].fillna(0).astype(int)
    for col in ["TOTAL_MINUTOS", "PRAZO_MEDIO_DIAS"]:
        if col in base:
            base[col] = base[col].fillna(0).astype(int)

    return base, df_detalhe, df_eficiencia, [], lista_mps
