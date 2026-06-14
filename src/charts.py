import plotly.graph_objects as go
from src.utils import fmt

def gauge_fig(prob, title=""):
    cor = "#00e5cc" if prob >= 75 else ("#f59e0b" if prob >= 50 else "#ef4444")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=prob,
        number={"suffix": "%", "font": {"size": 32, "color": cor, "family": "Inter"}},
        title={"text": title, "font": {"size": 13, "color": "#94a3b8"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94a3b8", "tickfont": {"color": "#94a3b8", "size": 10}},
            "bar": {"color": cor, "thickness": 0.26},
            "bgcolor": "#1c1c35", "borderwidth": 0,
            "steps": [{"range": [0, 100], "color": "#1a1a2e"}],
            "threshold": {"line": {"color": cor, "width": 3}, "thickness": 0.82, "value": prob},
        },
    ))
    fig.update_layout(paper_bgcolor="#161628", plot_bgcolor="#161628",
                      margin=dict(t=35, b=8, l=15, r=15), height=210,
                      font={"family": "Inter"})
    return fig

def gauge_efic(pct):
    cor = "#10b981" if pct >= 60 else ("#f59e0b" if pct >= 40 else "#ef4444")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=pct,
        number={"suffix": "%", "font": {"size": 28, "color": cor, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94a3b8", "tickfont": {"color": "#94a3b8", "size": 10}},
            "bar": {"color": cor, "thickness": 0.26},
            "bgcolor": "#1c1c35", "borderwidth": 0,
            "steps": [
                {"range": [0, 60],  "color": "rgba(239,68,68,0.08)"},
                {"range": [60, 100],"color": "rgba(16,185,129,0.08)"},
            ],
            "threshold": {"line": {"color": "#f59e0b", "width": 2}, "thickness": 0.75, "value": 60},
        },
    ))
    fig.update_layout(paper_bgcolor="#161628", plot_bgcolor="#161628",
                      margin=dict(t=15, b=8, l=15, r=15), height=190,
                      font={"family": "Inter"})
    return fig

def bar_comparativo(cap_prazo, total_pecas):
    fig = go.Figure(go.Bar(
        x=["Cap. no Prazo", "Peças Pendentes"],
        y=[cap_prazo, total_pecas],
        marker_color=["#00e5cc", "#7c3aed"],
        text=[fmt(cap_prazo), fmt(total_pecas)],
        textposition="outside",
        textfont={"color": "#f0f0ff", "size": 11},
        width=0.45,
    ))
    fig.update_layout(paper_bgcolor="#161628", plot_bgcolor="#161628",
                      margin=dict(t=25, b=15, l=15, r=15), height=220,
                      yaxis=dict(showgrid=False, visible=False),
                      xaxis=dict(tickfont={"color": "#94a3b8", "size": 11}),
                      showlegend=False)
    return fig

def bar_ranking(df_base):
    df_s = df_base.sort_values("PROBABILIDADE_PCT", ascending=True).tail(8)
    cores = ["#10b981" if p >= 75 else ("#f59e0b" if p >= 50 else "#ef4444") for p in df_s["PROBABILIDADE_PCT"]]
    fig = go.Figure(go.Bar(
        y=df_s["OFICINA"], x=df_s["PROBABILIDADE_PCT"],
        orientation="h", marker_color=cores,
        text=[f"{p}%" for p in df_s["PROBABILIDADE_PCT"]],
        textposition="outside",
        textfont={"color": "#f0f0ff", "size": 11},
    ))
    fig.update_layout(paper_bgcolor="#161628", plot_bgcolor="#161628",
                      margin=dict(t=10, b=10, l=10, r=40), height=280,
                      xaxis=dict(range=[0, 110], showgrid=False, visible=False),
                      yaxis=dict(tickfont={"color": "#f0f0ff", "size": 12}),
                      showlegend=False)
    return fig

def bar_pecas(df_base):
    df_s = df_base.sort_values("TOTAL_PECAS", ascending=False).head(8)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Pendente (Saldo)", y=df_s["OFICINA"], x=df_s["TOTAL_PECAS"],
                         orientation="h", marker_color="#7c3aed",
                         text=[fmt(v) for v in df_s["TOTAL_PECAS"]], textposition="outside",
                         textfont={"color": "#f0f0ff", "size": 10}))
    fig.add_trace(go.Bar(name="Cap. no Prazo", y=df_s["OFICINA"], x=df_s["CAP_NO_PRAZO"],
                         orientation="h", marker_color="#00e5cc",
                         text=[fmt(v) for v in df_s["CAP_NO_PRAZO"]], textposition="outside",
                         textfont={"color": "#f0f0ff", "size": 10}))
    fig.update_layout(paper_bgcolor="#161628", plot_bgcolor="#161628", barmode="group",
                      margin=dict(t=10, b=10, l=10, r=50), height=300,
                      xaxis=dict(showgrid=False, visible=False),
                      yaxis=dict(tickfont={"color": "#f0f0ff", "size": 11}),
                      legend=dict(font=dict(color="#94a3b8", size=11),
                                  bgcolor="rgba(0,0,0,0)", orientation="h",
                                  yanchor="bottom", y=1.02))
    return fig

def bar_eficiencia(df_eficiencia):
    if df_eficiencia is None or df_eficiencia.empty:
        return None
    df_s = df_eficiencia.sort_values("efic_media", ascending=True)
    cores = ["#10b981" if p >= 60 else ("#f59e0b" if p >= 40 else "#ef4444") for p in df_s["efic_media"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_s["OFICINA"], x=df_s["efic_media"],
        orientation="h", marker_color=cores,
        text=[f"{p:.1f}%" for p in df_s["efic_media"]],
        textposition="outside",
        textfont={"color": "#f0f0ff", "size": 11},
        name="Eficiência Média",
    ))
    fig.add_vline(x=60, line_width=2, line_dash="dash", line_color="#f59e0b",
                  annotation_text="Meta 60%", annotation_position="top right",
                  annotation_font_color="#f59e0b")
    fig.update_layout(paper_bgcolor="#161628", plot_bgcolor="#161628",
                      margin=dict(t=20, b=10, l=10, r=60), height=300,
                      xaxis=dict(range=[0, 115], showgrid=False, visible=False),
                      yaxis=dict(tickfont={"color": "#f0f0ff", "size": 12}),
                      showlegend=False)
    return fig
