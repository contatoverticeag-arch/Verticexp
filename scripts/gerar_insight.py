import os, json, requests
from datetime import date

def buscar_yahoo(simbolo, nome):
    try:
        res = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{simbolo}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        ).json()
        meta = res["chart"]["result"][0]["meta"]
        preco = meta["regularMarketPrice"]
        anterior = meta["chartPreviousClose"]
        variacao = ((preco - anterior) / anterior) * 100
        return f"{preco:.2f} ({variacao:+.2f}%)"
    except Exception as e:
        print(f"Erro {nome}: {e}")
        return "Indisponível"

# 1. Dólar
try:
    res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10).json()
    brl = res["rates"]["BRL"]
    dolar_texto = f"R$ {brl:.2f}"
except Exception as e:
    dolar_texto = "Indisponível"
    print(f"Erro dólar: {e}")

# 2. Commodities agrícolas
soja_texto   = "US$ " + buscar_yahoo("ZS=F", "Soja")   + "/bushel"
milho_texto  = "US$ " + buscar_yahoo("ZC=F", "Milho")  + "/bushel"
cafe_texto   = "US$ " + buscar_yahoo("KC=F", "Café")   + "/libra"

# 3. Mercado de tecnologia e mídia (relevante para marketing)
meta_texto   = "US$ " + buscar_yahoo("META", "Meta")   + "/ação"
google_texto = "US$ " + buscar_yahoo("GOOGL", "Google") + "/ação"

# 4. Mercado brasileiro
ibov_texto   = buscar_yahoo("^BVSP", "Ibovespa") + " pts"

print(f"💵 Dólar: {dolar_texto}")
print(f"🌾 Soja: {soja_texto}")
print(f"🌽 Milho: {milho_texto}")
print(f"☕ Café: {cafe_texto}")
print(f"📱 Meta: {meta_texto}")
print(f"🔍 Google: {google_texto}")
print(f"📈 Ibovespa: {ibov_texto}")

# 5. Prompt enriquecido
prompt = f"""Você é o analista-chefe de estratégia da Vértice, empresa especializada em engenharia de experiências para o agronegócio brasileiro.

Seu público são profissionais de marketing, gestores de eventos e líderes comerciais de empresas do agro (insumos, tecnologia agrícola, cooperativas, tradings).

DADOS DE MERCADO DE HOJE — {date.today().strftime('%d/%m/%Y')}:

🌾 AGRONEGÓCIO:
- Dólar (USD/BRL): {dolar_texto}
- Soja (Chicago): {soja_texto}
- Milho (Chicago): {milho_texto}
- Café (Nova York): {cafe_texto}

📱 TECNOLOGIA & MÍDIA (impacto em marketing digital):
- Meta Platforms (ações): {meta_texto}
- Alphabet/Google (ações): {google_texto}

📈 BRASIL:
- Ibovespa: {ibov_texto}

Com base nesses dados, gere uma análise estratégica estruturada com exatamente este formato:

**CONTEXTO DO DIA**
[2 linhas conectando os dados macro ao humor de investimento do agronegócio brasileiro]

**IMPACTO NO MARKETING**
[2 linhas sobre como esse cenário afeta decisões de verba, mídia paga e eventos corporativos]

**OPORTUNIDADE DA SEMANA**
[1 linha com uma ação concreta que um profissional de marketing do agro deveria considerar agora]

**ALERTA**
[1 linha com um risco ou ponto de atenção para essa semana]

Seja direto, analítico e use linguagem executiva. Não repita os números já listados acima — interprete-os."""

# 6. Groq
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
        "max_tokens": 500
    },
    timeout=30
)

print(f"Status Groq: {resposta.status_code}")

if resposta.status_code != 200:
    print("Erro Groq:", resposta.text)
    insight = "Análise indisponível no momento."
else:
    insight = resposta.json()["choices"][0]["message"]["content"]
    print(f"✅ Insight gerado!")
    print(insight)

# 7. Salva JSON
os.makedirs("public", exist_ok=True)
with open("public/insight-do-dia.json", "w", encoding="utf-8") as f:
    json.dump({
        "data": date.today().strftime("%d/%m/%Y"),
        "dolar": dolar_texto,
        "soja": soja_texto,
        "milho": milho_texto,
        "cafe": cafe_texto,
        "meta_acao": meta_texto,
        "google_acao": google_texto,
        "ibovespa": ibov_texto,
        "insight": insight
    }, f, ensure_ascii=False, indent=2)
