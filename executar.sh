#!/bin/bash

# Cores para o terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor

echo -e "${BLUE}==== Iniciando Fluxo DiscoverySpark ====${NC}"

# 1. Gerar Dados
echo -e "${GREEN}>> Passagem 1: Gerando dados de teste...${NC}"
python3 gerar_dados.py

# 2. Executar Engine (Ajuste o --projeto e --target se desejar)
echo -e "${GREEN}>> Passagem 2: Processando Engine de IA...${NC}"
python3 app.py --projeto test_passagem --target quantidade_assentos_comercializado,id_aeroporto_origem,id_aeroporto_destino

# 3. Abrir Dashboard
echo -e "${GREEN}>> Passagem 3: Abrindo Dashboard de Resultados...${NC}"
python3 dashboard.py