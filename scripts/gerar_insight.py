import os, json, requests
from datetime import date

# 1. Busca cotação do Dólar
try:
    dolar_res = requests.get(
        "https://economia.awesomeapi.com.br/json/last/USD-BRL",
        timeout=10
    ).json()
    dolar = dolar_res["USDBRL"]
    dolar_texto = f"R$ {float(dolar['bid']):.2f} ({float(dolar['pctChange']):+.2f}% hoje)"
except Exception as e:
    dolar_texto = "Indisponível"
    print(f"Erro dólar: {e}")

# 2. Busca cotação da Soja
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

# 3. Monta o prompt
prompt = f"""Você é um analista de mercado especializado em agronegócio brasileiro e eventos B2B corporativos.

Dados de hoje ({date.today().strftime('%d/%m/%Y')}):
- Dólar (USD/BRL): {dolar_texto}
- Soja (futuro Chicago): {soja_texto}

Escreva um insight estratégico de no máximo 4 linhas para profissionais de marketing e eventos no agronegócio brasileiro. Tom direto, analítico e prático. Sem bullet points. Em português do Brasil."""

# 4. Chama o Gemini
api_key = os.environ["GEMINI_API_KEY"]
resposta = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
    json={"contents": [{"parts": [{"text": prompt}]}]},
    timeout=30
)

print("Status Gemini:", resposta.status_code)
print("Resposta raw:", resposta.text[:500])

dados_gemini = resposta.json()
insight = dados_gemini["candidates"][0]["content"]["parts"][0]["text"]

# 5. Salva o JSON
os.makedirs("public", exist_ok=True)
resultado = {
    "data": date.today().strftime("%d/%m/%Y"),
    "dolar": dolar_texto,
    "soja": soja_texto,
    "insight": insight
}
with open("public/insight-do-dia.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print(f"✅ Sucesso! Insight gerado para {date.today()}")
