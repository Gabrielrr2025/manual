import pandas as pd
import numpy as np

# ----- TABELA DE VOLATILIDADES PRESUMIDAS (anualizadas) -----
volatilidades_padrao = {
    "Ações (Ibovespa)": 0.25,
    "Juros-Pré": 0.08,
    "Câmbio (Dólar)": 0.15,
    "Cupom Cambial": 0.12,
    "Crédito Privado": 0.05,
    "Multimercado": 0.18,
    "Outros": 0.10
}

# ----- INPUT DO USUÁRIO -----
print("--- Cálculo de VaR e Estresse - Modo Manual ---")
PL_fundo = float(input("Digite o Patrimônio Líquido (R$): "))

# Horizonte de tempo
opcoes_horizonte = [1, 10, 21]
print("\nSelecione o horizonte de dias para o VaR:")
for i, op in enumerate(opcoes_horizonte):
    print(f"{i + 1}. {op} dias")
indice_horizonte = int(input("Opção: ")) - 1
horizonte_dias = opcoes_horizonte[indice_horizonte]

# Nível de confiança
opcoes_conf = {"1": (0.95, 1.65), "2": (0.99, 2.33)}
print("\nSelecione o nível de confiança:")
print("1. 95%\n2. 99%")
conf_choice = input("Opção: ")
conf_level, z_score = opcoes_conf.get(conf_choice, (0.95, 1.65))

# Composição da carteira
carteira = []
print("\nSelecione as classes da carteira (insira a concentração em %):")
for classe, vol in volatilidades_padrao.items():
    try:
        perc = float(input(f"{classe} (% do PL): "))
        if perc > 0:
            carteira.append({
                "classe": classe,
                "%PL": perc,
                "vol_anual": vol
            })
    except ValueError:
        continue

# Cálculo de VaR por classe
for item in carteira:
    vol_diaria = item['vol_anual'] / np.sqrt(252)
    var_percentual = z_score * vol_diaria * np.sqrt(horizonte_dias)
    var_reais = PL_fundo * (item['%PL'] / 100) * var_percentual
    item.update({
        "VaR_%": round(var_percentual * 100, 4),
        "VaR_R$": round(var_reais, 2)
    })

# Cálculo de Estresse
cenarios_estresse = {
    "Ibovespa": -0.15,
    "Juros-Pré": 0.02,
    "Cupom Cambial": -0.01,
    "Dólar": -0.05,
    "Outros": -0.03
}

estresse_resultados = {}
for fator, choque in cenarios_estresse.items():
    impacto_total = 0
    for item in carteira:
        if fator.lower() in item['classe'].lower():
            impacto = choque * (item['%PL'] / 100)
            impacto_total += impacto
    estresse_resultados[fator] = impacto_total

# Exportar resultados para CSV
df_var = pd.DataFrame(carteira)
df_var.to_csv("resultado_var.csv", index=False)

df_estresse = pd.DataFrame.from_dict(estresse_resultados, orient='index', columns=['Impacto % do PL'])
df_estresse.reset_index(inplace=True)
df_estresse.rename(columns={'index': 'Fator de Risco'}, inplace=True)
df_estresse.to_csv("resultado_estresse.csv", index=False)

# Exibir resumo
print("\n--- RESULTADOS DO CÁLCULO ---")
var_total = sum([x['VaR_R$'] for x in carteira])
print(f"VaR Total ({int(conf_level*100)}% em {horizonte_dias} dias):")
print(f"- R$ {var_total:,.2f} ({round((var_total / PL_fundo) * 100, 4)}% do PL)")
print("Modelo utilizado: Paramétrico - Delta Normal")

print("\n--- IMPACTO DOS CENÁRIOS DE ESTRESSE ---")
for fator, impacto in estresse_resultados.items():
    print(f"{fator}: impacto estimado = {round(impacto * 100, 4)}% do PL")

print("\nArquivos gerados: resultado_var.csv e resultado_estresse.csv")
