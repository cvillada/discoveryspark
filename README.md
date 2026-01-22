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

### 1.2#### Instalar Dependências

Com o ambiente ativado, instale as bibliotecas necessárias:

**Opção 1: Instalar individualmente**
```bash
pip install pandas featuretools scikit-learn rich numpy
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
/mapeamento: Contém o arquivo mapeamento.txt (configuração de relações)
/resultados: Onde o sistema salva os datasets enriquecidos (.csv) e os relatórios (.md)
app.py: O coração do sistema (Processamento e IA)
dashboard.py: Visualizador interativo de resultados no terminal
gerar_dados.py: Script auxiliar para criar dados de teste fictícios
```

---

## ⚙️ 3. Como Configurar e Executar

### Passo A: Mapeamento de Dados

No arquivo `mapeamento/mapeamento.txt`, defina a relação no formato:

```
TABELA_PAI:pai|CHAVE#TABELA_FILHO:filho|CHAVE
```

**Exemplo:**
```
clientes:pai|id_cliente#vendas:filho|id_cliente
```

### Passo B: Executar o Motor

Rode o comando abaixo substituindo os valores:

```bash
python app.py --projeto MEU_PROJETO --target COLUNA_ALVO
```
Nota sobre o Alvo (Target): O DiscoverySpark é flexível. Embora os exemplos usem churn, você pode substituir pelo nome de qualquer coluna da sua tabela Pai. O motor detectará automaticamente se é um problema de Classificação (Sim/Não) ou Regressão (Valores Numéricos) e ajustará os insights de tendência.

**Parâmetros:**
- `--projeto`: Nome para identificar os arquivos gerados (ex: `analise_clientes`)
- `--target`: A coluna que você deseja analisar (ex: `churn`, `faturamento`, `conversao`)

**Exemplo prático:**
```bash
python app.py --projeto analise_churn --target churn
```

### Passo C: Visualizar Resultados

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

## 📝 5. Notas Técnicas

- **Tradução**: Nomes técnicos como `SUM(vendas.valor)` são convertidos para "Soma total de valor em vendas"
- **Estabilidade**: O sistema trata automaticamente valores nulos (NaN) e evita erros de divisão por zero
- **Saída**: Gera um CSV completo para BI e um Markdown estilizado para apresentações rápidas

---

## 📄 6. Licença

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
