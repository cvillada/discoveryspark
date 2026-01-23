# 🚀 DiscoverySpark - Motor de Inteligência Relacional

Este projeto é um motor de inteligência relacional de alta performance. Ele automatiza a descoberta de hipóteses em dados relacionais, identifica os drivers de negócio mais importantes e gera relatórios traduzidos para linguagem executiva.

---

## 🛠️ 1. Requisitos e Instalação

O sistema foi desenvolvido para **Python 3.10, 3.11 ou 3.12.4**.

### 1.1 Ambiente Virtual Python (Recomendado)

Recomendamos fortemente o uso de ambiente virtual para isolar as dependências do projeto.

#### Criar ambiente virtual

```bash
# Criar ambiente virtual chamado 'venv'
python -m venv venv
```

#### Ativar ambiente virtual

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.\\venv\\Scripts\\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\\Scripts\\activate.bat
```

#### Verificar se o ambiente está ativo

O prompt do terminal deve mostrar o nome do ambiente entre parênteses:

```bash
(venv) usuario@computador:~$
```

### 1.2 Instalar Dependências

Com o ambiente ativado, instale as bibliotecas necessárias:

**Opção 1: Instalar individualmente**
```bash
pip install pandas featuretools scikit-learn rich numpy requests
```

**Opção 2: Usar arquivo requirements.txt**
```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` contém todas as dependências necessárias para o projeto.

#### Desativar ambiente virtual

Quando terminar de trabalhar no projeto:

```bash
deactivate
```

---

## 📁 2. Estrutura de Pastas

O motor organiza-se da seguinte forma:

```
/datasets: Local para colocar seus arquivos .csv (ex: clientes.csv)
/mapeamento: Contém os arquivos de configuração de relações (mapeamento.txt, mapeamento_exemplo.txt)
/resultados: Onde o sistema salva os datasets enriquecidos (.csv) e os relatórios (.md)
app.py: O coração do sistema (Processamento e IA)
analise_profunda.py: Sistema de análise com IA Generativa (DeepSeek API)
diagnostico_tendencia.py: Diagnóstico e validação de tendências
dashboard.py: Visualizador interativo de resultados no terminal
gerar_dados.py: Script auxiliar para criar dados de teste fictícios
executar.sh / executar.bat: Scripts de execução automatizada
requirements.txt: Lista de dependências do projeto
```

---

## ⚙️ 3. Como Configurar e Executar

### Passo A: Mapeamento de Dados

No arquivo `mapeamento/mapeamento.txt`, defina a relação no formato:

```
TABELA_PAI:pai|CHAVE#TABELA_FILHO:filho|CHAVE
```

**Exemplos:**
```
clientes:pai|id_cliente#vendas:filho|id_cliente
passagens_vendas:pai|id_empresa,id_aeroporto_origem,id_aeroporto_destino#empresa:filho|id_empresa#aeroporto:filha|id_aeroporto#aeroporto:filha|id_aeroporto
```

### Passo B: Executar o Motor

Rode o comando abaixo substituindo os valores:

```bash
python app.py --projeto MEU_PROJETO --target COLUNA_ALVO
```

**Parâmetros:**
- `--projeto`: Nome para identificar os arquivos gerados (ex: `analise_clientes`)
- `--target`: A coluna que você deseja analisar (ex: `churn`, `faturamento`, `conversao`)
  - **Suporte a múltiplos targets**: Você pode especificar várias colunas separadas por vírgula (ex: `churn,faturamento,conversao`)

**Exemplos práticos:**
```bash
# Análise de churn
python app.py --projeto analise_churn --target churn

# Análise multivariada
python app.py --projeto analise_completa --target quantidade_assentos_comercializado,id_aeroporto_origem,id_aeroporto_destino
```

### Passo C: Execução Automatizada

O projeto inclui scripts de execução automatizada:

**Linux/macOS:**
```bash
./executar.sh
```

**Windows:**
```cmd
executar.bat
```

### Passo D: Análise Profunda com IA

Para análise avançada com IA Generativa (DeepSeek API):

```bash
python analise_profunda.py
```

O sistema permitirá selecionar arquivos .md e .csv para análise profunda e geração de recomendações estratégicas.

### Passo E: Visualizar Resultados

Após o término, execute o dashboard para ver os insights:

```bash
python dashboard.py
```

---

## 🧠 4. Entendendo as Descobertas (Features)

O DiscoverySpark utiliza **Deep Feature Synthesis (DFS)** para criar novas hipóteses automaticamente:

- **Soma total de (Sum)**: Acúmulo de valores (ex: faturamento total por cliente)
- **Média de (Mean)**: Comportamento médio (ex: ticket médio)
- **Quantidade total de (Count)**: Frequência (ex: total de visitas/compras)
- **Variação de (Std)**: Oscilação de comportamento

### Direção do Insight (Tendência)

O relatório indica o impacto de cada descoberta:

- **(+) Aumenta**: O aumento desta variável faz o alvo (target) subir
- **(-) Diminui**: O aumento desta variável faz o alvo (target) descer

---

## 🤖 5. Sistema de Análise Profunda com IA

O DiscoverySpark inclui um sistema avançado de análise com IA Generativa usando a API do DeepSeek:

### 5.1 Como obter sua chave de API do DeepSeek

Para usar o sistema de análise profunda, você precisa de uma chave de API do DeepSeek:

1. **Acesse o site**: https://platform.deepseek.com/
2. **Crie uma conta** ou faça login se já tiver uma
3. **Vá para 'API Keys'** no painel de controle
4. **Crie uma nova chave de API**
5. **Copie a chave** (ela começa com `sk-`)

**Nota importante**: A chave de API é pessoal e não deve ser compartilhada. O sistema agora solicita a chave de forma segura (com entrada de senha) quando você executa o programa.

### 5.2 Funcionalidades
- **Análise de arquivos .md e .csv**: Interpreta qualquer layout de arquivo
- **Dois agentes especializados**: Analisador de Insights e Estrategista
- **Recomendações estratégicas**: Gera insights acionáveis baseados em dados
- **Salvamento automático**: Resultados salvos com timestamp para rastreabilidade
- **Validação de chave**: Verifica automaticamente se a chave tem formato válido
- **Fallback robusto**: Funciona mesmo quando a API está indisponível

### 5.3 Como usar
```bash
python analise_profunda.py
```

O sistema guiará você através de:
1. **Configuração da API**: Solicitação segura da sua chave do DeepSeek
2. **Seleção interativa de arquivos**: Escolha arquivos .md e .csv para análise
3. **Análise profunda dos dados**: Processamento por dois agentes especializados
4. **Geração de recomendações**: Insights estratégicos baseados em IA
5. **Salvamento dos resultados**: Arquivos salvos com timestamp para rastreabilidade

### 5.4 Segurança e Privacidade
- **Chave protegida**: A chave de API é solicitada com entrada de senha (não aparece na tela)
- **Validação local**: A chave é validada localmente antes de ser enviada à API
- **Nenhum armazenamento**: A chave não é salva em arquivos, apenas usada durante a sessão
- **Fallback seguro**: Se a API estiver indisponível, o sistema usa análises pré-definidas

---

## 🔍 6. Diagnóstico e Validação

Para validar o cálculo de importância e tendências:

```bash
python diagnostico_tendencia.py
```

Este script testa o sistema de cálculo de importância com dados de exemplo e valida a precisão das tendências identificadas.

---

## 📝 7. Notas Técnicas

- **Tradução**: Nomes técnicos como `SUM(vendas.valor)` são convertidos para "Soma total de valor em vendas"
- **Estabilidade**: O sistema trata automaticamente valores nulos (NaN) e evita erros de divisão por zero
- **Saída**: Gera um CSV completo para BI e um Markdown estilizado para apresentações rápidas
- **Robustez**: Inclui fallback para quando a API de IA está indisponível
- **Compatibilidade**: Usa featuretools 1.30.0 para compatibilidade com woodwork

---

## 📄 8. Licença

Este projeto está licenciado sob a **Licença MIT**.

**Autor**: Claudinei Villada - BlueShift Brasil

**Licença MIT**:
```
Copyright (c) 2024 Claudinei Villada - BlueShift Brasil

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
