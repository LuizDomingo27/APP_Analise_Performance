import pandas as pd
from datetime import datetime
from src.logic import status_info, perf_info
from src.utils import fmt, fmtD, fmtDate

def gerar_relatorio_html(nome_of, r, row_base, ef_data=None):
    try:
        with open("templates/report_template.html", "r", encoding="utf-8") as f:
            template = f.read()
    except Exception as e:
        return f"<h1>Erro ao ler template: {e}</h1>"

    now  = datetime.now().strftime("%d/%m/%Y %H:%M")
    prob = r["prob"]
    lbl, cor, _, _, _ = status_info(prob)
    folga = r["folga"]
    sinal = "+" if folga >= 0 else "-"
    cor_fg = "#10b981" if folga >= 0 else "#ef4444"
    bcor = "#00e5cc" if prob >= 75 else ("#f59e0b" if prob >= 50 else "#ef4444")
    bbg  = "rgba(16,185,129,0.15)" if prob >= 75 else ("rgba(245,158,11,0.15)" if prob >= 50 else "rgba(239,68,68,0.15)")
    icon = "<span class='material-symbols-outlined'>check_circle</span>" if prob >= 75 else ("<span class='material-symbols-outlined'>warning</span>" if prob >= 50 else "<span class='material-symbols-outlined'>cancel</span>")

    if prob >= 75:
        analise = (f"A <strong>{nome_of}</strong> demonstra <strong style='color:#10b981'>capacidade suficiente</strong> "
                   f"para produzir o saldo pendente de <strong>{fmt(row_base['TOTAL_PECAS'])} peças</strong> distribuídas in "
                   f"<strong>{int(row_base['TOTAL_ORDENS'])} ordens</strong> dentro do prazo médio de "
                   f"<strong>{int(row_base['PRAZO_MEDIO_DIAS'])} dias</strong>.")
        rec = "Manter ritmo atual. Considere antecipar ordens com folga de capacidade."
    elif prob >= 50:
        analise = (f"A <strong>{nome_of}</strong> opera em <strong style='color:#f59e0b'>zona de atenção</strong>. "
                   f"Com um saldo pendente de {fmt(row_base['TOTAL_PECAS'])} peças, a margem para imprevistos é limitada.")
        rec = "Revisar prioridade das ordens, redistribuir carga entre colaboradores e monitorar avanço diário."
    else:
        analise = (f"A <strong>{nome_of}</strong> apresenta <strong style='color:#ef4444'>insuficiência de capacidade</strong>. "
                   f"O saldo pendente de {fmt(row_base['TOTAL_PECAS'])} peças supera a capacidade disponível no prazo.")
        rec = "Redistribuir ordens para outras oficinas ou renegociar prazos."

    ef_pct        = float(row_base.get("pct_ordens_na_meta", 0))
    ef_ordens     = int(row_base.get("ordens_na_meta", 0))
    ef_media_val  = float(row_base.get("efic_media", 0))
    ef_lbl_v, ef_cor_v, ef_pill_v = perf_info(ef_pct)
    ef_bbg_v = ("rgba(16,185,129,0.15)" if ef_pct >= 60 else "rgba(245,158,11,0.15)" if ef_pct >= 40 else "rgba(239,68,68,0.15)")
    ef_icon_v = "<span class='material-symbols-outlined'>check_circle</span>" if ef_pct >= 60 else ("<span class='material-symbols-outlined'>warning</span>" if ef_pct >= 40 else "<span class='material-symbols-outlined'>cancel</span>")

    context = {
        "{{ nome_of }}":          nome_of,
        "{{ data_atual }}":       now,
        "{{ total_ordens }}":     str(int(row_base["TOTAL_ORDENS"])),
        "{{ total_pecas }}":      fmt(row_base["TOTAL_PECAS"]),
        "{{ prazo_medio }}":      str(int(row_base["PRAZO_MEDIO_DIAS"])),
        "{{ colaboradores }}":    str(int(row_base["COLABORADORES"])),
        "{{ prob }}":             str(prob),
        "{{ bcor }}":             bcor,
        "{{ bbg }}":              bbg,
        "{{ cor }}":              cor,
        "{{ icon }}":             icon,
        "{{ lbl }}":              lbl,
        "{{ cap_dia }}":          fmt(r["cap_dia"]),
        "{{ cap_semanal }}":      fmt(r["cap_semanal"]),
        "{{ cap_no_prazo }}":     fmt(r["cap_no_prazo"]),
        "{{ dias_necessarios }}": fmtD(r["dias_necessarios"]),
        "{{ semanas_necessarias }}": fmtD(r["semanas_necessarias"]),
        "{{ efic }}":             fmtD(r["efic"]),
        "{{ folga_abs }}":        fmt(abs(folga)),
        "{{ sinal }}":            sinal,
        "{{ cor_fg }}":           cor_fg,
        "{{ folga_bg }}":         "rgba(16,185,129,.15)" if folga >= 0 else "rgba(239,68,68,.15)",
        "{{ folga_cor }}":        "#10b981" if folga >= 0 else "#ef4444",
        "{{ folga_lbl }}":        "Suficiente" if folga >= 0 else "Déficit",
        "{{ analise }}":          analise,
        "{{ rec }}":              rec,
        "{{ total_minutos }}":    fmt(row_base.get("TOTAL_MINUTOS", 0)),
        "{{ ratio }}":            f"{r['ratio']:.2f}",
        "{{ ef_pct }}":           f"{ef_pct:.1f}",
        "{{ ef_pct_bar }}":       str(min(ef_pct, 100)),
        "{{ ef_ordens_na_meta }}": str(ef_ordens),
        "{{ ef_media }}":         f"{ef_media_val:.1f}",
        "{{ ef_lbl }}":           ef_lbl_v,
        "{{ ef_cor }}":           ef_cor_v,
        "{{ ef_bbg }}":           ef_bbg_v,
        "{{ ef_icon }}":          ef_icon_v,
        "{{ ef_pill }}":          ef_pill_v,
    }
    for k, v in context.items(): template = template.replace(k, str(v))
    return template

def gerar_relatorio_eficiencia_html(nome_of, row_base, df_det_of):
    """
    Gera o HTML do relatório de eficiência para uma oficina.
    """
    try:
        with open("templates/efficiency_report_template.html", "r", encoding="utf-8") as f:
            template = f.read()
    except Exception as e:
        return f"<h1>Erro ao ler template de eficiência: {e}</h1>"

    now          = datetime.now().strftime("%d/%m/%Y %H:%M")
    ef_pct       = float(row_base.get("pct_ordens_na_meta", 0))
    ef_ordens    = int(row_base.get("ordens_na_meta", 0))
    ef_media_val = float(row_base.get("efic_media", 0))
    total_ordens = int(row_base.get("TOTAL_ORDENS", 0))
    colaboradores = int(row_base.get("COLABORADORES", 0))

    ef_lbl_v, ef_cor_v, ef_pill_v = perf_info(ef_pct)
    ef_bbg_v  = ("rgba(16,185,129,0.15)" if ef_pct >= 60 else "rgba(245,158,11,0.15)" if ef_pct >= 40 else "rgba(239,68,68,0.15)")
    ef_icon_v = ("&#10003;" if ef_pct >= 60 else ("&#9888;" if ef_pct >= 40 else "&#10007;"))

    # ── Calcular % saldo pendente ──────────────────────────────────────────────
    total_solicitado = 0
    total_pendente   = 0
    if df_det_of is not None and not df_det_of.empty:
        total_solicitado = int(df_det_of["QTD_PECAS"].sum())
        total_pendente   = int(df_det_of.get("QTD_PENDENTE", df_det_of["QTD_PECAS"] * 0).sum())
    pct_pendente = round((total_pendente / total_solicitado * 100), 1) if total_solicitado > 0 else 0.0

    # ── Classificar ordens por urgência (DIAS_PARA_VENCER) ────────────────────
    n_vencidas  = 0
    n_urgentes  = 0
    n_no_prazo  = 0
    df_criticas = None

    if df_det_of is not None and not df_det_of.empty and "DIAS_PARA_VENCER" in df_det_of.columns:
        df_tmp = df_det_of.copy()
        df_tmp["_dpv"] = pd.to_numeric(df_tmp["DIAS_PARA_VENCER"], errors="coerce")
        n_vencidas = int((df_tmp["_dpv"] < 0).sum())
        n_urgentes = int(((df_tmp["_dpv"] >= 0) & (df_tmp["_dpv"] <= 7)).sum())
        n_no_prazo = int((df_tmp["_dpv"] > 7).sum())
        mask_crit  = df_tmp["_dpv"] <= 7
        if mask_crit.any():
            df_criticas = df_tmp[mask_crit].sort_values("_dpv")

    hm_vencidas_cls = "hm-alert" if n_vencidas > 0 else "hm-val"

    # ── Bloco de ordens críticas ───────────────────────────────────────────────
    def _badge_html(dias):
        """Gera badge colorido de urgência para o relatório HTML."""
        try:
            d = int(dias)
        except (TypeError, ValueError):
            return "<span style='color:#94a3b8'>-</span>"
        if d < 0:
            c, b = "#ef4444", "rgba(239,68,68,0.15)"
            lbl  = f"Vencido há {abs(d)}d"
        elif d == 0:
            c, b = "#ef4444", "rgba(239,68,68,0.15)"
            lbl  = "Vence hoje!"
        elif d <= 7:
            c, b = "#f59e0b", "rgba(245,158,11,0.15)"
            lbl  = f"Faltam {d}d"
        else:
            c, b = "#10b981", "rgba(16,185,129,0.15)"
            lbl  = f"Faltam {d}d"
        return (f"<span style='color:{c};background:{b};padding:2px 8px;"
                f"border-radius:4px;font-size:11px;font-weight:700'>{lbl}</span>")

    bloco_criticas = ""
    if df_criticas is not None and not df_criticas.empty:
        linhas_crit = ""
        for _, dr in df_criticas.iterrows():
            linhas_crit += (
                f"<tr>"
                f"<td class='nome'>{dr['ORDEM_MESTRE']}</td>"
                f"<td>{fmtDate(dr.get('ENVIO','-'))}</td>"
                f"<td>{fmtDate(dr.get('DEAD_LINE','-'))}</td>"
                f"<td>{_badge_html(dr.get('DIAS_PARA_VENCER'))}</td>"
                f"<td>{fmt(dr.get('QTD_PENDENTE', 0))} pc</td>"
                f"<td style='color:{dr.get('PERF_COR','#94a3b8')};font-weight:700'>"
                f"  {float(dr.get('PCT_ENTREGUE',0)):.1f}%</td>"
                f"</tr>"
            )
        bloco_criticas = (
            "<div class='sec-t'>&#128680; Ordens Críticas — Vencidas e Urgentes</div>"
            "<div class='crit-wrap'>"
            "<div class='crit-hdr'>&#9888; Atenção: estas ordens exigem ação imediata</div>"
            "<table>"
            "<tr>"
            "<th style='text-align:left'>Ordem Mestre</th>"
            "<th>Envio</th><th>Dead Line</th><th>Falta p/ Vencer</th>"
            "<th>Qtd Pendente</th><th>% Entregue</th>"
            "</tr>"
            f"{linhas_crit}"
            "</table></div>"
        )

    # ── Tabela principal de ordens ─────────────────────────────────────────────
    linhas = ""
    if df_det_of is not None and not df_det_of.empty:
        for _, dr in df_det_of.iterrows():
            linhas += (
                f"<tr>"
                f"<td class='nome'>{dr['ORDEM_MESTRE']}</td>"
                f"<td>{fmtDate(dr.get('ENVIO', '-'))}</td>"
                f"<td>{fmtDate(dr.get('DEAD_LINE', '-'))}</td>"
                f"<td>{_badge_html(dr.get('DIAS_PARA_VENCER'))}</td>"
                f"<td>{fmt(dr['QTD_PECAS'])} pc</td>"
                f"<td>{fmt(dr.get('QTD_ENTREGUE', 0))} pc</td>"
                f"<td style='color:#00e5cc;font-weight:600'>{fmt(dr.get('QTD_PENDENTE', 0))} pc</td>"
                f"<td style='color:{dr.get('PERF_COR','#94a3b8')};font-weight:700'>"
                f"  {float(dr.get('PCT_ENTREGUE', 0)):.1f}%</td>"
                f"<td>{fmt(dr.get('MINUTOS', 0))} min</td>"
                f"<td>{int(dr.get('PRAZO_DIAS', 0))}d</td>"
                f"</tr>"
            )

    # ── Análise narrativa enriquecida ──────────────────────────────────────────
    risco_str = ""
    if n_vencidas > 0:
        risco_str += (f" <strong style='color:#ef4444'>{n_vencidas} ordem(ns) já venceu(ram)</strong>"
                      f" o prazo e")
    if n_urgentes > 0:
        risco_str += (f" <strong style='color:#f59e0b'>{n_urgentes} ordem(ns) vence(m) em até 7 dias</strong>.")

    if ef_pct >= 60:
        insight_cls = "insight-ok"
        insight_txt = (
            f"<strong style='color:#10b981'>Desempenho satisfatório.</strong> "
            f"A <strong>{nome_of}</strong> atingiu a meta de eficiência em "
            f"<strong>{ef_ordens}</strong> de <strong>{total_ordens}</strong> ordens "
            f"(eficiência média: <strong>{ef_media_val:.1f}%</strong>). "
            f"O saldo pendente representa <strong>{pct_pendente:.1f}%</strong> do volume original."
            + (f" Atenção:{risco_str}" if risco_str else "")
        )
        rec_txt = (
            "&#10003; Manter o ritmo atual de entregas. "
            + (f"Priorizar as {n_vencidas + n_urgentes} ordens críticas listadas acima. " if (n_vencidas + n_urgentes) > 0 else "")
            + "Monitorar o saldo pendente diariamente para evitar acúmulo."
        )
    elif ef_pct >= 40:
        insight_cls = "insight-warn"
        insight_txt = (
            f"<strong style='color:#f59e0b'>Atenção necessária.</strong> "
            f"A <strong>{nome_of}</strong> atingiu a meta em apenas <strong>{ef_ordens}</strong> "
            f"de <strong>{total_ordens}</strong> ordens (média: <strong>{ef_media_val:.1f}%</strong>). "
            f"O saldo pendente é <strong>{pct_pendente:.1f}%</strong> do volume original."
            + (f" Situação agravada: {risco_str}" if risco_str else "")
        )
        rec_txt = (
            "&#9888; Revisar a prioridade das ordens com maior saldo pendente. "
            "Redistribuir carga entre colaboradores disponíveis. "
            + (f"Agir imediatamente sobre as {n_vencidas + n_urgentes} ordens críticas. " if (n_vencidas + n_urgentes) > 0 else "")
            + "Monitorar avanço diariamente."
        )
    else:
        insight_cls = "insight-bad"
        insight_txt = (
            f"<strong style='color:#ef4444'>Performance abaixo da meta.</strong> "
            f"A <strong>{nome_of}</strong> entregou apenas <strong>{ef_ordens}</strong> "
            f"ordens acima de 60% (média: <strong>{ef_media_val:.1f}%</strong>). "
            f"O saldo pendente representa <strong>{pct_pendente:.1f}%</strong> do volume original — "
            f"indicando risco elevado de atraso."
            + (f" {risco_str}" if risco_str else "")
        )
        rec_txt = (
            "&#10007; Acionar gestão imediatamente. "
            + (f"Existem {n_vencidas} ordens vencidas e {n_urgentes} urgentes. " if (n_vencidas + n_urgentes) > 0 else "")
            + "Avaliar redistribuição de ordens para outras oficinas ou renegociação de prazos com o cliente."
        )

    # ── Montar contexto e renderizar ──────────────────────────────────────────
    context = {
        "{{ nome_of }}":          nome_of,
        "{{ data_atual }}":       now,
        "{{ total_ordens }}":     str(total_ordens),
        "{{ ef_pct }}":           f"{ef_pct:.1f}",
        "{{ ef_ordens_na_meta }}": str(ef_ordens),
        "{{ ef_media }}":         f"{ef_media_val:.1f}",
        "{{ ef_lbl }}":           ef_lbl_v,
        "{{ ef_cor }}":           ef_cor_v,
        "{{ ef_bbg }}":           ef_bbg_v,
        "{{ ef_icon }}":          ef_icon_v,
        "{{ ef_pill }}":          ef_pill_v,
        "{{ colaboradores }}":    str(colaboradores),
        "{{ pct_pendente }}":     f"{pct_pendente:.1f}",
        "{{ ordens_vencidas }}":  str(n_vencidas),
        "{{ ordens_urgentes }}":  str(n_urgentes),
        "{{ ordens_no_prazo }}":  str(n_no_prazo),
        "{{ hm_vencidas_cls }}":  hm_vencidas_cls,
        "{{ bloco_criticas }}":   bloco_criticas,
        "{{ linhas_ordens }}":    linhas,
        "{{ insight_cls }}":      insight_cls,
        "{{ insight_txt }}":      insight_txt,
        "{{ rec_txt }}":          rec_txt,
    }
    for k, v in context.items():
        template = template.replace(k, str(v))
    return template
