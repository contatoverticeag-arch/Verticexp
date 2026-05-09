name: Gerar Insight Diário
on:
  schedule:
    - cron: "0 11 * * *"  # Todo dia às 8h BRT (11h UTC)
  workflow_dispatch:       # Permite rodar manualmente também

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Buscar dados e gerar insight
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          # Busca cotação do dólar (AwesomeAPI)
          DOLAR=$(curl -s "https://economia.awesomeapi.com.br/json/last/USD-BRL" | python3 -c "import sys,json; d=json.load(sys.stdin)['USDBRL']; print(f\"{d['bid']} ({d['pctChange']}%)\") ")
          
          # Gera insight via Gemini
          python3 scripts/gerar_insight.py "$DOLAR" > public/insight-do-dia.json

      - name: Commit e push do insight
        run: |
          git config --global user.email "bot@vertice.com.br"
          git config --global user.name "Vértice Bot"
          git add public/insight-do-dia.json
          git diff --staged --quiet || git commit -m "feat: insight do dia $(date +%Y-%m-%d)"
          git push
