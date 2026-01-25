# Relatorio de Inteligencia: TEST_PASSAGEM

**Alvos Analisados:** quantidade_assentos_comercializado,id_aeroporto_origem,id_aeroporto_destino | **Tipo:** Múltiplos

## 📊 Sumário Executivo - Análise Multivariada

Foram analisados 3 targets simultaneamente:

- **valor_passagem**: Regressão (Top 10 insights)
- **COUNT(empresa)**: Classificação (Top 10 insights)
- **ano_referencia**: Classificação (Top 10 insights)
- **mes_referencia**: Classificação (Top 10 insights)
- **quantidade_assentos_comercializado**: Regressão (Top 10 insights)

**🔗 Interações entre targets:**
- Foram identificadas 1 interações significativas entre targets

---

## 🔗 Interações entre Targets

| Target 1 | Target 2 | Correlação | Força | Direção |
| :--- | :--- | :--- | :--- | :--- |
| valor_passagem | quantidade_assentos_comercializado | -0.125 | Fraca | Negativa |

## 🎯 Análise Individual para: valor_passagem (Regressão)

| Rank | Insight | Impacto | Tendencia |
| :--- | :--- | :--- | :--- |
| #1 | Id_aeroporto_destino | 34.81% | (+) Quanto maior, mais aumenta o(a) valor_passagem |
| #2 | Id_aeroporto_origem | 32.54% | (+) Quanto maior, mais aumenta o(a) valor_passagem |
| #3 | Quantidade_assentos_comercializado | 20.86% | (-) Quanto maior, mais diminui o(a) valor_passagem |
| #4 | Id_empresa | 11.78% | (-) Quanto maior, mais diminui o(a) valor_passagem |
| #5 | Quantidade total de empresa | 3.67e-06 | (+) Quanto maior, mais aumenta o(a) valor_passagem |
| #6 | Ano_referencia | 0.00e+00 | (-) Quanto maior, mais diminui o(a) valor_passagem |
| #7 | Mes_referencia | 0.00e+00 | (-) Quanto maior, mais diminui o(a) valor_passagem |

## 🎯 Análise Individual para: COUNT(empresa) (Classificação)

| Rank | Insight | Impacto | Tendencia |
| :--- | :--- | :--- | :--- |
| #1 | Id_aeroporto_origem | 49.94% | (+) Quanto maior, mais aumenta o(a) COUNT(empresa) |
| #2 | Valor_passagem | 30.63% | (+) Quanto maior, mais aumenta o(a) COUNT(empresa) |
| #3 | Id_aeroporto_destino | 14.25% | (-) Quanto maior, mais diminui o(a) COUNT(empresa) |
| #4 | Quantidade_assentos_comercializado | 3.45% | (-) Quanto maior, mais diminui o(a) COUNT(empresa) |
| #5 | Id_empresa | 1.72% | (-) Quanto maior, mais diminui o(a) COUNT(empresa) |
| #6 | Ano_referencia | 0.00e+00 | (-) Quanto maior, mais diminui o(a) COUNT(empresa) |
| #7 | Mes_referencia | 0.00e+00 | (-) Quanto maior, mais diminui o(a) COUNT(empresa) |

## 🎯 Análise Individual para: ano_referencia (Classificação)

| Rank | Insight | Impacto | Tendencia |
| :--- | :--- | :--- | :--- |
| #1 | Mes_referencia | 0.00e+00 | (-) Quanto maior, mais diminui o(a) ano_referencia |
| #2 | Id_empresa | 0.00e+00 | (-) Quanto maior, mais diminui o(a) ano_referencia |
| #3 | Id_aeroporto_origem | 0.00e+00 | (-) Quanto maior, mais diminui o(a) ano_referencia |
| #4 | Id_aeroporto_destino | 0.00e+00 | (-) Quanto maior, mais diminui o(a) ano_referencia |
| #5 | Valor_passagem | 0.00e+00 | (-) Quanto maior, mais diminui o(a) ano_referencia |
| #6 | Quantidade_assentos_comercializado | 0.00e+00 | (-) Quanto maior, mais diminui o(a) ano_referencia |
| #7 | Quantidade total de empresa | 0.00e+00 | (-) Quanto maior, mais diminui o(a) ano_referencia |

## 🎯 Análise Individual para: mes_referencia (Classificação)

| Rank | Insight | Impacto | Tendencia |
| :--- | :--- | :--- | :--- |
| #1 | Ano_referencia | 0.00e+00 | (-) Quanto maior, mais diminui o(a) mes_referencia |
| #2 | Id_empresa | 0.00e+00 | (-) Quanto maior, mais diminui o(a) mes_referencia |
| #3 | Id_aeroporto_origem | 0.00e+00 | (-) Quanto maior, mais diminui o(a) mes_referencia |
| #4 | Id_aeroporto_destino | 0.00e+00 | (-) Quanto maior, mais diminui o(a) mes_referencia |
| #5 | Valor_passagem | 0.00e+00 | (-) Quanto maior, mais diminui o(a) mes_referencia |
| #6 | Quantidade_assentos_comercializado | 0.00e+00 | (-) Quanto maior, mais diminui o(a) mes_referencia |
| #7 | Quantidade total de empresa | 0.00e+00 | (-) Quanto maior, mais diminui o(a) mes_referencia |

## 🎯 Análise Individual para: quantidade_assentos_comercializado (Regressão)

| Rank | Insight | Impacto | Tendencia |
| :--- | :--- | :--- | :--- |
| #1 | Valor_passagem | 47.86% | (-) Quanto maior, mais diminui o(a) quantidade_assentos_comercializado |
| #2 | Id_aeroporto_origem | 24.28% | (+) Quanto maior, mais aumenta o(a) quantidade_assentos_comercializado |
| #3 | Id_aeroporto_destino | 24.04% | (+) Quanto maior, mais aumenta o(a) quantidade_assentos_comercializado |
| #4 | Id_empresa | 3.82% | (+) Quanto maior, mais aumenta o(a) quantidade_assentos_comercializado |
| #5 | Quantidade total de empresa | 1.18e-09 | (-) Quanto maior, mais diminui o(a) quantidade_assentos_comercializado |
| #6 | Ano_referencia | 0.00e+00 | (-) Quanto maior, mais diminui o(a) quantidade_assentos_comercializado |
| #7 | Mes_referencia | 0.00e+00 | (-) Quanto maior, mais diminui o(a) quantidade_assentos_comercializado |



--- 
*Gerado em: 25/01/2026 11:55:05*