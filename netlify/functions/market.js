const json = (statusCode, body) => ({
  statusCode,
  headers: {
    "Content-Type": "application/json",
    "Cache-Control": "public, max-age=180"
  },
  body: JSON.stringify(body)
});

const fetchJson = async (url) => {
  const response = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 Vértice Market Snapshot"
    }
  });
  if (!response.ok) throw new Error(`Fonte indisponivel: ${response.status}`);
  return response.json();
};

const yahooChart = async (symbol) => {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?interval=1d&range=2d`;
  const data = await fetchJson(url);
  const meta = data?.chart?.result?.[0]?.meta;
  if (!meta?.regularMarketPrice) throw new Error(`Sem cotacao para ${symbol}`);
  const price = Number(meta.regularMarketPrice);
  const previous = Number(meta.previousClose || price);
  const pct = previous ? ((price - previous) / previous) * 100 : 0;
  return { symbol, price, previous, pct };
};

const loadCurrencies = async () => {
  try {
    const fx = await fetchJson("https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL");
    return {
      source: "AwesomeAPI",
      usd: {
        brl: Number.parseFloat(fx.USDBRL.bid),
        pct: Number.parseFloat(fx.USDBRL.pctChange)
      },
      eur: {
        brl: Number.parseFloat(fx.EURBRL.bid),
        pct: Number.parseFloat(fx.EURBRL.pctChange)
      }
    };
  } catch (error) {
    const fallback = await fetchJson("https://open.er-api.com/v6/latest/USD");
    const usdBrl = Number(fallback?.rates?.BRL);
    const eurUsd = Number(fallback?.rates?.EUR);

    if (!Number.isFinite(usdBrl)) throw error;

    return {
      source: "ExchangeRate-API",
      usd: { brl: usdBrl, pct: 0 },
      eur: {
        brl: Number.isFinite(eurUsd) && eurUsd > 0 ? usdBrl / eurUsd : null,
        pct: 0
      }
    };
  }
};

exports.handler = async () => {
  const payload = {
    timestamp: new Date().toISOString(),
    sources: {
      currencies: "AwesomeAPI",
      commodities: "Yahoo Finance/CBOT",
      equities: "Yahoo Finance/B3"
    },
    currencies: {},
    commodities: {},
    equities: {},
    errors: []
  };

  try {
    const fx = await loadCurrencies();
    payload.sources.currencies = fx.source;
    payload.currencies.usd = fx.usd;
    if (fx.eur?.brl) payload.currencies.eur = fx.eur;
  } catch (error) {
    payload.errors.push({ source: "cambio", message: error.message });
  }

  const usd = payload.currencies.usd?.brl || 5.7;
  const commodityMap = [
    ["soja", "ZS=F"],
    ["milho", "ZC=F"]
  ];

  await Promise.all(commodityMap.map(async ([key, symbol]) => {
    try {
      const item = await yahooChart(symbol);
      const brlPerBushel = (item.price * usd) / 100;
      payload.commodities[key] = {
        symbol,
        raw: item.price,
        pct: item.pct,
        brlPerBag: brlPerBushel * (60 / 27.2)
      };
    } catch (error) {
      payload.errors.push({ source: symbol, message: error.message });
    }
  }));

  try {
    const ibov = await yahooChart("^BVSP");
    payload.equities.ibov = {
      symbol: "^BVSP",
      price: ibov.price,
      pct: ibov.pct
    };
  } catch (error) {
    payload.errors.push({ source: "IBOV", message: error.message });
  }

  return json(200, payload);
};
