@echo off
cls
echo =========================================
echo       FLUXO AUTOMATIZADO DISCOVERYSPARK
echo =========================================

echo.
echo [1/3] Gerando dados de teste...
python gerar_dados.py

echo.
echo [2/3] Processando Engine de IA...
python app.py --projeto teste_automatizado --target churn

echo.
echo [3/3] Abrindo Dashboard de Resultados...
python dashboard.py

pause