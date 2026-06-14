# 📋 Resumo do Projeto: Simulador de Metas - Oficinas

Este documento consolida a visão geral, a arquitetura técnica, as regras de negócio e todo o histórico de implementações do **Simulador de Metas para Oficinas (Versão 4)**.

---

## 1. Descrição Geral do Projeto
O **Simulador de Metas** é uma aplicação web desenvolvida em **Python** utilizando o framework **Streamlit**. O objetivo da ferramenta é monitorar, prever e auditar a capacidade produtiva e a performance de entrega de diferentes oficinas de costura/produção.

A ferramenta permite que gestores importem dados reais da operação, simulem cenários operacionais alterando a capacidade diária, número de funcionários ou prazos, e exportem relatórios de análise de risco e eficiência prontos para impressão.

### Stack Tecnológica
* **Linguagem:** Python 3.x
* **Interface Web:** Streamlit
* **Processamento de Dados:** Pandas, Openpyxl
* **Visualizações Gráficas:** Plotly (gráficos de velocímetro, barras comparativas e rankings)
* **Estilização:** CSS Customizado (Tema Escuro/Premium com gradientes modernos)
* **Tipografia e Ícones:** Google Material Symbols e fontes otimizadas para relatórios corporativos (`Segoe UI`, `Roboto`)

---

## 2. Arquitetura do Projeto (Boas Práticas & Camadas)
Seguindo padrões de arquitetura de software sênior, o projeto foi modularizado para separar as responsabilidades de visualização, lógica de negócio, estilos e templates:

```text
simulador_metas/
│
├── app.py                     # View/Interface principal em Streamlit
├── requirements.txt           # Dependências do projeto
├── create_mock.py             # Script utilitário para gerar dados sintéticos de teste
│
├── src/                       # Camada de Lógica e Segurança
│   ├── __init__.py
│   ├── logic.py               # Algoritmo de cruzamento, abatimento e cálculos de KPIs
│   └── auth.py                # Módulo de autenticação e controle de acesso das abas
│
├── assets/                    # Camada de Estilo Visual
│   └── styles.css             # CSS global com a identidade visual e fontes do app
│
├── templates/                 # Templates de exportação de relatórios
│   ├── report_template.html   # Template HTML/CSS do Relatório Consolidado Geral
│   └── efficiency_report_template.html # Template HTML/CSS do Relatório de Eficiência
│
├── pages/                     # Abas/Páginas adicionais do Streamlit
│   ├── 1_Metodologia.py       # Explicação básica das regras (Protegido por senha)
│   └── 2_Manual_Metodologia.py # Manual detalhado para a Diretoria (Protegido por senha)
│
├── data/                      # Base de dados (Planilhas Mocks de Teste)
│   ├── CONTROLE.xlsx          # Cadastro de capacidade das Oficinas
│   ├── ACOMPANHAMENTO.xlsx    # Carteira de ordens de serviço pendentes
│   └── RECEBIMENTO.xlsx       # Registro de baixas e peças cortadas/entregues
│
└── Resume/                    # Documentação do projeto
    └── resumo_projeto.md      # Este documento histórico
```

---

## 3. Regras de Negócio & Algoritmos Principais

### A. Lógica do Abatimento de Saldo (Baixa de Ordens)
O simulador cruza o planejado (Acompanhamento) com o realizado (Recebimento) através da chave única de **Ordem Mestre**:
$$\text{Saldo Pendente} = \text{Quantidade Solicitada (Acompanhamento)} - \text{Quantidade Entregue (Recebimento)}$$
* Se o saldo pendente for $\le 0$, a ordem é considerada concluída e removida dos cálculos de sobrecarga.
* Os minutos pendentes são recalculados de forma proporcional à quantidade pendente restante.

### B. Consumo Percentual de Capacidade
Mede quanto o saldo pendente de peças consome da capacidade máxima disponível no prazo restante:
$$\text{Capacidade no Prazo} = \text{Capacidade Diária} \times \text{Prazo Médio das Ordens (dias)}$$
$$\text{Consumo \%} = \left(\frac{\text{Saldo Pendente}}{\text{Capacidade no Prazo}}\right) \times 100$$

### C. Folga e Déficit
Indica se a capacidade disponível no prazo é suficiente para cobrir a demanda pendente:
$$\text{Resultado} = \text{Capacidade no Prazo} - \text{Saldo Pendente}$$
* **Resultado Positivo (+):** Representa **Folga** (sobra de capacidade).
* **Resultado Negativo (-):** Representa **Déficit** (falta de capacidade produtiva).

### D. Probabilidade de Entrega (Load Ratio + Resiliência)
Calcula a chance matemática de a oficina entregar o saldo pendente no prazo estipulado:
1. **Razão de Carga (Load Ratio):** $\text{Razão} = \frac{\text{Capacidade no Prazo}}{\text{Saldo Pendente}}$
2. **Faixas de Risco Base:**
   * $\text{Razão} \ge 1.50 \rightarrow \mathbf{97\%}$ (Seguro)
   * $\text{Razão} \ge 1.20 \rightarrow \mathbf{88\%}$ (Seguro)
   * $\text{Razão} \ge 1.00 \rightarrow \mathbf{7 2\%}$ (Atenção)
   * $\text{Razão} \ge 0.85 \rightarrow \mathbf{52\%}$ (Moderado)
   * $\text{Razão} \ge 0.70 \rightarrow \mathbf{35\%}$ (Alto Risco)
   * $\text{Razão} \ge 0.50 \rightarrow \mathbf{18\%}$ (Crítico)
   * $\text{Razão} < 0.50 \rightarrow \mathbf{8\%}$ (Crítico)
3. **Modificador de Resiliência (Tamanho da Equipe):**
   * $\ge 20$ colaboradores: **+5%** de bônus na probabilidade.
   * $10$ a $19$ colaboradores: **+2%** de bônus.
   * $< 10$ colaboradores: **-3%** de penalidade (equipes pequenas são mais sensíveis a absenteísmo).
4. A probabilidade final é limitada ao intervalo entre $3\%$ e $99\%$.

### E. Critério de Classificação do Status de Risco
* **Entrega Viável:** Probabilidade $\ge 75\%$ (Verde)
* **Risco Moderado:** Probabilidade entre $50\%$ e $74\%$ (Amarelo)
* **Alto Risco:** Probabilidade $< 50\%$ (Vermelho)

### F. Performance de Eficiência (Meta de 60%)
Reflete a consistência da oficina nas ordens solicitadas:
* Uma ordem individual é considerada **aceitável** se a quantidade entregue atingir no mínimo **60%** da solicitada.
* **Performance Global da Oficina:** Porcentagem de ordens de serviço daquela oficina que atingiram ou superaram a meta de 60% de eficiência.

---

## 4. Histórico Completo de Implementações (Linha do Tempo)

### 📅 Fase 1: Arquitetura de Software e Modularização (Boas Práticas)
* **Objetivo:** Transformar o código monolítico inicial em um projeto limpo e extensível por um desenvolvedor sênior.
* **Ações:**
  * Criação do diretório `src/` e migração das fórmulas matemáticas para `src/logic.py`.
  * Criação do diretório `assets/` isolando toda a estilização CSS no arquivo `styles.css`.
  * Criação da pasta `templates/` com os arquivos HTML puros de relatórios.
  * Centralização do alinhamento das tabelas (colunas de valores centralizados via classe CSS `.tr`).

### 📅 Fase 2: Implementação do Abatimento Dinâmico de Saldo
* **Objetivo:** Substituir a simulação com base na demanda total pela simulação baseada apenas no saldo real pendente.
* **Ações:**
  * Desenvolvimento da rotina de agregação em `src/logic.py` que calcula a diferença entre o Acompanhamento e o Recebimento.
  * Tornou-se **obrigatória** a importação da planilha de Recebimento. Caso o usuário não faça o upload das 3 planilhas, a aplicação exibe um banner vermelho crítico de bloqueio.
  * Correção da lógica de identificação de colunas (`find_col`) para evitar falsos positivos de strings parciais (ex: coluna "MP" sendo incorretamente detectada como "tempo/minutos").

### 📅 Fase 3: Filtro Global de Matéria-Prima (MP)
* **Objetivo:** Adicionar granularidade às análises de insumos e capacidade.
* **Ações:**
  * Atualização do gerador `create_mock.py` para gerar colunas de MP de forma correlacionada entre as planilhas.
  * Criação de um seletor global (Dropdown) no topo da aplicação para filtrar dados por MP específica.
  * Adição de cálculo de impacto de MP na simulação individual: mostra o consumo exato da matéria-prima selecionada frente à capacidade total da oficina (ex: *"A matéria prima Malha PV consome 43% da capacidade disponível no prazo"*).

### 📅 Fase 4: Sistema de Relatórios e Impressão
* **Objetivo:** Permitir ao usuário exportar dados simulados em formato visual de alta qualidade para apresentações e auditorias físicas.
* **Ações:**
  * Criação de dois botões de relatórios individuais por oficina:
    1. **Relatório Geral:** Análise consolidada de capacidade, riscos e pendências.
    2. **Relatório de Eficiência:** Foco na análise histórica de cumprimento da meta de 60%.
  * Implementação de rotina em Javascript/Base64 para gerar o PDF a partir de strings HTML abrindo uma nova aba limpa diretamente no navegador do usuário, com formatação específica para impressão de documentos (usando media-queries `@media print`).

### 📅 Fase 5: Multipage App e Sistema de Acesso Restrito (Senha)
* **Objetivo:** Proteger a documentação e manuais metodológicos criados para o Diretor Geral.
* **Ações:**
  * Configuração da pasta `pages/` dividindo a aplicação em "Painel Principal", "Metodologia" e "Manual da Metodologia".
  * Desenvolvimento do módulo [src/auth.py](file:///c:/Users/luiz-/Downloads/simulador_metas/src/auth.py) para controlar o acesso às páginas secundárias.
  * **Senha cadastrada:** `diretoria`.
  * Criação de um sistema de rastreamento de navegação com reset de credencial: caso o usuário saia das abas metodológicas e volte para a página do App, o status de autorização é redefinido para `False`. Ao tentar voltar na documentação, ele deve digitar a senha novamente.

### 📅 Fase 6: Padronização Visual Corporativa (Identidade Google)
* **Objetivo:** Adequar a estética do app aos padrões executivos de alta fidelidade da Google.
* **Ações:**
  * Substituição de todos os emojis por ícones oficiais do pacote **Google Material Symbols** (`analytics`, `monitoring`, `library_books`, `warning`, etc.).
  * Atualização da pilha de fontes nos arquivos CSS locais e globais para um stack web clássico de informação (`Segoe UI`, `Roboto`, `Helvetica`, `Arial`).
  * Aumento da escala global de fontes do app (aumento de base para `15px` e tabelas para `15px`) para melhorar a exibição em projeções e relatórios executivos.

---
*Atualizado em junho de 2026.*
