import os, json, requests
from datetime import date

# 1. Dólar — API alternativa (formato diferente)
try:
    dolar_res = requests.get(
        "https://economia.awesomeapi.com.br/json/daily/USD-BRL/1",
        timeout=10
    ).json()
    bid = float(dolar_res[0]["bid"])
    pct = float(dolar_res[0]["pctChange"])
    dolar_texto = f"R$ {bid:.2f} ({pct:+.2f}% hoje)"
except Exception as e:
    dolar_texto = "Indisponível"
    print(f"Erro dólar: {e}")

# 2. Soja
try:
    soja_res = requests.get(
        "https://query1.finance.yahoo.com/v8/finance/chart/ZS=F",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    ).json()
    soja_preco = soja_res["chart"]["result"][0]["meta"]["regularMarketPrice"]
    soja_texto = f"US$ {soja_preco:.2f}/bushel (Chicago)"
except Exception as e:
    soja_texto = "Indisponível"
    print(f"Erro soja: {e}")

# 3. Prompt
prompt = f"""Você é um analista de mercado especializado em agronegócio brasileiro e eventos B2B corporativos.

Dados de hoje ({date.today().strftime('%d/%m/%Y')}):
- Dólar (USD/BRL): {dolar_texto}
- Soja (futuro Chicago): {soja_texto}

Escreva um insight estratégico de no máximo 4 linhas para profissionais de marketing e eventos no agronegócio brasileiro. Tom direto, analítico e prático. Sem bullet points. Em português do Brasil."""

# 4. Gemini
api_key = os.environ["GEMINI_API_KEY"]
resposta = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
    json={"contents": [{"parts": [{"text": prompt}]}]},
    timeout=30
)

print("Status Gemini:", resposta.status_code)

# Tratamento de erro da API
if resposta.status_code != 200:
    print("Erro Gemini:", resposta.text)
    # Salva JSON com mensagem de fallback para não quebrar o site
    os.makedirs("public", exist_ok=True)
    with open("public/insight-do-dia.json", "w", encoding="utf-8") as f:
        json.dump({
            "data": date.today().strftime("%d/%m/%Y"),
            "dolar": dolar_texto,
            "soja": soja_texto,
            "insight": "Análise indisponível no momento. Tente novamente mais tarde."
        }, f, ensure_ascii=False, indent=2)
    exit(0)  # Sai sem erro para não quebrar o workflow

dados_gemini = resposta.json()
insight = dados_gemini["candidates"][0]["content"]["parts"][0]["text"]

# 5. Salva JSON
os.makedirs("public", exist_ok=True)
with open("public/insight-do-dia.json", "w", encoding="utf-8") as f:
    json.dump({
        "data": date.today().strftime("%d/%m/%Y"),
        "dolar": dolar_texto,
        "soja": soja_texto,
        "insight": insight
    }, f, ensure_ascii=False, indent=2)

print(f"✅ Sucesso! Insight gerado para {date.today()}")
