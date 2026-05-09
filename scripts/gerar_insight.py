import os, json, requests
from datetime import date

# 1. Dólar
try:
    res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10).json()
    brl = res["rates"]["BRL"]
    dolar_texto = f"R$ {brl:.2f}"
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

print(f"💵 Dólar: {dolar_texto}")
print(f"🌾 Soja: {soja_texto}")

# 3. Prompt
prompt = f"""Você é um analista de mercado especializado em agronegócio brasileiro e eventos B2B corporativos.

Dados de hoje ({date.today().strftime('%d/%m/%Y')}):
- Dólar (USD/BRL): {dolar_texto}
- Soja (futuro Chicago): {soja_texto}

Escreva um insight estratégico de no máximo 4 linhas para profissionais de marketing e eventos no agronegócio brasileiro. Tom direto, analítico e prático. Sem bullet points. Em português do Brasil."""

# 4. Groq (gratuito, sem cartão)
api_key = os.environ["GEMINI_API_KEY"]
resposta = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300
    },
    timeout=30
)

print(f"Status Groq: {resposta.status_code}")

if resposta.status_code != 200:
    print("Erro Groq:", resposta.text)
    insight = "Análise indisponível no momento."
else:
    insight = resposta.json()["choices"][0]["message"]["content"]
    print(f"✅ Insight gerado com sucesso!")

# 5. Salva JSON
os.makedirs("public", exist_ok=True)
with open("public/insight-do-dia.json", "w", encoding="utf-8") as f:
    json.dump({
        "data": date.today().strftime("%d/%m/%Y"),
        "dolar": dolar_texto,
        "soja": soja_texto,
        "insight": insight
    }, f, ensure_ascii=False, indent=2)
