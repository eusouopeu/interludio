# Dados em jogo — apresentação do TCC

Site de apresentação do TCC *"Dados em jogo: plano de negócios baseado em evidências para uma luderia em
Salvador"* — Bacharelado em Administração, Escola de Administração, UFBA.

Catorze abas na barra lateral, em dois grupos: nove do **plano** e cinco de **dados de apoio**, para responder à banca.

| # | Aba | Capítulo do TMin | Tempo |
|---|---|---|---|
| 1 | Introdução | 1 | 1min |
| 2 | Referencial teórico | 2 | 1min |
| 3 | Metodologia | 3 | 1min30 |
| 4 | Síntese dos resultados | 9 e 11 | 30s |
| 5 | Análise de mercado | 5 e 6 | 1min30 |
| 6 | Plano de marketing | 6 | 1min30 |
| 7 | Plano operacional | 7 e 8 | 1min |
| 8 | Plano financeiro | 9 | 1min30 |
| 9 | Análise de riscos | 10 e 11 | 1min |
| 10 a 14 | Panorama (B1), por metrópole, por região, análise de conteúdo (B2) e auditoria | dados | apoio |

Cada aba mostra uma seção por vez: os botões do topo escolhem a seção, os do pé da seção passam para a anterior e a
próxima, e os do rodapé passam de aba. As setas **←** e **→** do teclado passam as seções e, na primeira ou na
última, a aba. O endereço guarda a aba e a seção (`#marketing/2`).

Um botão discreto no cabeçalho alterna o **modo simples** (padrão: o roteiro dos slides da defesa, em 20 minutos) e
o **modo completo** (o conteúdo detalhado, com as tabelas do TMin). Nas abas de dados, o modo simples mostra só o
resumo e os achados. O botão do canto superior direito alterna o tema claro e o escuro.

## De onde vêm os números

- **Texto das abas 1 a 9:** `src/conteudo/abas/`, uma pasta por aba e um `.yaml` por seção, em `simples/` e
  `completo/`, sem código; o guia dos campos está em `src/conteudo/abas/LEIA-ME.md`.
- **Tabelas e quadros:** não são digitados. `scripts/sincronizar_tabelas.py` extrai todas as tabelas e quadros do TMin
  (`textos/capitulos/`) para `src/conteudo/tabelas.json`, e o `.yaml` da seção só aponta o número ("Tabela 5").
  Depois de cada versão do texto: `pnpm run tabelas`.
- **Abas 9 a 13:** `src/conteudo/b1-estatisticas.json`, `b2-conteudo.json` e `auditorias.json`, com os textos em
  `s8-*.json`, `s11-*.json` e `s12-*.json`.
- **Downloads (aba 1):** `scripts/copiar_downloads.py` roda antes do `dev` e do `build` e copia para
  `public/downloads/` (fora do git) o `textos/TCC_luderia_v<n>.docx` de maior n, o
  `slides-video-apresentacao/slides-vfinal.pptx` e as `textos/planilhas/B<n>_dados_agregados*.xlsx`, com o índice em
  `src/conteudo/downloads.json`. Arquivo ausente na máquina vira botão desativado.
- **Abas de dados de apoio e moldura do site:** `src/conteudo/site.json`; títulos e tempos das abas do plano, no
  `_aba.yaml` de cada pasta.

Os números escritos à mão nos `.yaml` (chamadas, KPIs e cartões) seguem a apresentação final
(`slides-vfinal.pptx`, TMin v50) e o modelo financeiro de 26/11/2026 e precisam ser conferidos quando o texto mudar.

## Identidade visual

Padrão purple e slate dos apps (skill `identidade-visual-apps`): tema claro por padrão, escuro pelo sistema, borda de
1,5 px e nenhuma sombra, ação primária em cor sólida, Lato nos títulos e Montserrat no resto (arquivos `.woff2` locais
em `public/fonts/`). As cores são variáveis CSS em `src/index.css`; os nomes de cor dos JSON (`azul`, `roxo`,
`lavanda`…) apontam para a escala do purple (`src/tema.js`), e os gráficos das abas de dados usam `COR`
(`src/formato.js`). No tema escuro, o purple de ação clareia para `#a78bfa`.

## Rodar localmente

```bash
pnpm install
pnpm dev
```

## Publicar no GitHub Pages

```bash
pnpm run deploy
```

Esse comando roda o build e envia o resultado para a branch `gh-pages` do repositório `interludio`, servida em
<https://eusouopeu.github.io/interludio/> (prefixo `base` em `vite.config.js`).

## Onde fica

O site mora aqui, em `interludio/site-apresentacao/`, e não no repositório do TCC. Os scripts de `scripts/` e os
scripts do TCC que geram `b1-estatisticas.json`, `b2-conteudo.json` e `auditorias.json` esperam o `tcc-luderia` como
pasta irmã do `interludio` (`~/Codigos/analise-dados/`).
