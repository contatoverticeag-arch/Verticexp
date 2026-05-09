import os, json, requests
from datetime import date

# 1. Dólar — AwesomeAPI (gratuita, sem chave)
dolar_res = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()
dolar = dolar_res["USDBRL"]
dolar_texto = f"R$ {float(dolar['bid']):.2f} ({float(dolar['pctChange']):+.2f}% hoje)"

# 2. Soja — Yahoo Finance (sem chave, símbolo ZS=F)
try:
    soja_res = requests.get(
        "https://query1.finance.yahoo.com/v8/finance/chart/ZS=F",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    ).json()
    soja_preco = soja_res["chart"]["result"][0]["meta"]["regularMarketPrice"]
    soja_texto = f"US$ {soja_preco:.2f}/bushel (Chicago)"
except:
    soja_texto = "Indisponível no momento"

# 3. Prompt para o Gemini
prompt = f"""
Você é um analista de mercado especializado em agronegócio brasileiro e eventos B2B corporativos.

Dados de hoje ({date.today().strftime('%d/%m/%Y')}):
- Dólar (USD/BRL): {dolar_texto}
- Soja (futuro Chicago): {soja_texto}

Com base nesses dados, escreva um insight estratégico de no máximo 4 linhas,
direcionado a profissionais de marketing e eventos no agronegócio brasileiro.
Tom: direto, analítico, prático. Como uma nota de briefing matinal executivo.
Não use bullet points. Escreva em português do Brasil.
"""

# 4. Chamada ao Gemini
api_key = os.environ["GEMINI_API_KEY"]
resposta = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
    json={"contents": [{"parts": [{"text": prompt}]}]},
    timeout=30
)
insight = resposta.json()["candidates"][0]["content"]["parts"][0]["text"]

# 5. Salva JSON que o site vai consumir
os.makedirs("public", exist_ok=True)
with open("public/insight-do-dia.json", "w", encoding="utf-8") as f:
    json.dump({
        "data": date.today().strftime("%d/%m/%Y"),
        "dolar": dolar_texto,
        "soja": soja_texto,
        "insight": insight
    }, f, ensure_ascii=False, indent=2)

print(f"✅ Insight gerado: {date.today()}")
print(f"💵 Dólar: {dolar_texto}")
print(f"🌾 Soja: {soja_texto}")
