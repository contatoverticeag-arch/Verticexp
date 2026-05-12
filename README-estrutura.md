# Estrutura Vértice

Base criada para um site estático profissional com arquivos HTML independentes.

## Arquivos compartilhados

- `styles.css`: identidade visual, tipografia, header, footer, botões, cards, animações de entrada, responsividade e barra de progresso de scroll.
- `components.js`: injeta header e footer em todas as páginas, controla menu mobile, ativa o link da página atual, configura animações e guarda apenas a configuração pública da planilha.

## Como usar em cada HTML

Inclua no `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
```

Inclua no `<body>`:

```html
<div data-component="header"></div>
<main class="page-shell">
  <!-- Conteúdo da página -->
</main>
<div data-component="footer"></div>
<script src="components.js"></script>
```

## Configurações

### Blog

O `blog.html` já tem a URL CSV publicada como padrão. Se quiser trocar a planilha depois, configure no console do navegador:

```js
localStorage.setItem("vt_sheets", "https://docs.google.com/spreadsheets/d/e/.../pub?output=csv");
```

### Analises do diagnostico e mercado

A chave da Groq nao fica no HTML, nem no `localStorage`, nem no GitHub. Ela deve ficar como variavel de ambiente no Netlify:

- Nome: `GROQ_API_KEY`
- Valor: sua chave nova da Groq
- Opcional: `GROQ_MODEL`, por exemplo `llama-3.3-70b-versatile`

As paginas chamam a funcao segura em `/.netlify/functions/groq`. Se a funcao nao estiver configurada, o site ainda mostra uma analise local de apoio, mas a experiencia completa depende do Netlify com a variavel `GROQ_API_KEY`.
