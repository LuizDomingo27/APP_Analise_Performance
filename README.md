# 🔧 Simulador de Metas — Oficinas

App Python com Streamlit para calcular a probabilidade de entrega de oficinas com base na capacidade produtiva.

---

## 📋 Pré-requisitos

- Python 3.9 ou superior
- pip

---

## 🚀 Instalação e execução

### 1. Clone ou extraia os arquivos do projeto

```
simulador_metas/
├── app.py
├── requirements.txt
└── README.md
```

### 2. (Recomendado) Crie um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute o app

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em **http://localhost:8501**

---

## 📊 Estrutura esperada da planilha

O app aceita `.xlsx`, `.xls` e `.csv`.
A detecção das colunas é automática — os nomes são reconhecidos de forma flexível.

| Coluna | Nome esperado |
|--------|--------------|
| Nome da oficina | `Oficina` / `Nome` / `Unidade` |
| Capacidade | `Capacidade de Pecas` |
| Qtd. solicitada | `Quantidade Solicitada` |
| Prazo | `Quantidade Dias Para Entrega` |
| Colaboradores | `Total de Colaboradores` |

---

## ⚙️ Lógica de probabilidade

| Razão (capacidade / solicitado) | Probabilidade base |
|---------------------------------|--------------------|
| ≥ 1.5 | 97% |
| ≥ 1.2 | 88% |
| ≥ 1.0 | 72% |
| ≥ 0.85 | 52% |
| ≥ 0.7 | 35% |
| ≥ 0.5 | 18% |
| < 0.5 | 8% |

Bônus de colaboradores: +5% (≥20), +2% (≥10), −3% (<10)

---

## 🎨 Design

- Tema **dark** com paleta cyan `#00e5cc`, roxo `#7c3aed` e verde-água `#2dd4bf`
- Gauge de probabilidade interativo (Plotly)
- Gráfico comparativo capacidade × demanda
- Leitura automática de planilha com preenchimento dos campos
