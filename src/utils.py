import re

def fmt(n):
    try:
        return f"{int(round(float(n))):,}".replace(",", ".")
    except:
        return str(n)

def fmtD(n):
    try:
        return f"{float(n):.1f}".replace(".", ",")
    except:
        return "-"

def fmtPct(n):
    try:
        return f"{float(n):.1f}%"
    except:
        return "-"

def fmtDate(val):
    """Formata uma data para dd/mm/aaaa. Retorna '-' se inválida."""
    import pandas as pd
    from datetime import datetime
    if val is None or pd.isna(val):
        return "-"
    s = str(val).strip()
    if s in ("", "nan", "None", "-"):
        return "-"
    
    # Se for objeto datetime/Timestamp
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.strftime("%d/%m/%Y")
        
    # Match yyyy-mm-dd ou yyyy/mm/dd (formato ISO) no início da string
    m_iso = re.match(r"^(\d{4})[/\-](\d{2})[/\-](\d{2})", s)
    if m_iso:
        return f"{m_iso.group(3)}/{m_iso.group(2)}/{m_iso.group(1)}"
        
    # Match dd-mm-yyyy ou dd/mm/yyyy no início da string
    m_br = re.match(r"^(\d{2})[/\-](\d{2})[/\-](\d{4})", s)
    if m_br:
        return f"{m_br.group(1)}/{m_br.group(2)}/{m_br.group(3)}"
        
    # Fallback: tentar converter com pandas
    try:
        dt = pd.to_datetime(s, errors="raise")
        return dt.strftime("%d/%m/%Y")
    except:
        return s


def prazo_badge(dias_para_vencer):
    """
    Retorna HTML de badge colorido com os dias restantes até o vencimento.
    Usa DIAS_PARA_VENCER = DEAD_LINE − HOJE (dinâmico).
    """
    if dias_para_vencer is None:
        return "<span style='color:#94a3b8'>-</span>"
    try:
        d = int(dias_para_vencer)
    except (ValueError, TypeError):
        return "<span style='color:#94a3b8'>-</span>"
    if d < 0:
        cor, bg = "#ef4444", "rgba(239,68,68,0.15)"
        label = f"Vencido há {abs(d)}d"
    elif d == 0:
        cor, bg = "#ef4444", "rgba(239,68,68,0.15)"
        label = "Vence hoje!"
    elif d <= 7:
        cor, bg = "#f59e0b", "rgba(245,158,11,0.15)"
        label = f"Faltam {d}d"
    elif d <= 15:
        cor, bg = "#eab308", "rgba(234,179,8,0.15)"
        label = f"Faltam {d}d"
    else:
        cor, bg = "#10b981", "rgba(16,185,129,0.15)"
        label = f"Faltam {d}d"
    return (f"<span style='color:{cor};background:{bg};"
            f"padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700'>{label}</span>")
