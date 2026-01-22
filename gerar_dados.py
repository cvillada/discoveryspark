import pandas as pd
import numpy as np
import os

def gerar_dados_teste():
    # Garante que a pasta datasets existe
    if not os.path.exists('datasets'):
        os.makedirs('datasets')

    # 1. Criar Tabela de Clientes (PAI)
    n_clientes = 100
    clientes = pd.DataFrame({
        'id_cliente': range(1, n_clientes + 1),
        'idade': np.random.randint(18, 70, size=n_clientes),
        'segmento': np.random.choice(['Premium', 'Standard', 'Econômico'], n_clientes),
        'churn': np.random.choice([0, 1], n_clientes) # O que vamos tentar prever
    })

    # 2. Criar Tabela de Vendas (FILHO)
    n_vendas = 500
    vendas = pd.DataFrame({
        'id_venda': range(1, n_vendas + 1),
        'id_cliente': np.random.randint(1, n_clientes + 1, size=n_vendas),
        'valor': np.random.uniform(10.0, 500.0, size=n_vendas),
        'categoria': np.random.choice(['Alimentos', 'Eletrônicos', 'Moda', 'Casa'], n_vendas),
        'data_venda': pd.date_range(start='2025-01-01', periods=n_vendas, freq='H')
    })

    # Salvar nos caminhos corretos
    clientes.to_csv('datasets/clientes.csv', index=False)
    vendas.to_csv('datasets/vendas.csv', index=False)
    
    print("✅ Arquivos 'clientes.csv' e 'vendas.csv' gerados em /datasets")

if __name__ == "__main__":
    gerar_dados_teste()