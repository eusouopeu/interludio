// Gera o .docx de um capítulo a partir do .md (textos-tcc/capitulos/).
//
// Mesmo formato ABNT de gerar_docx_projeto.js (A4, margens 3/2 cm, Arial 12,
// espaçamento 1,5, recuo de 1,00 cm). Diferenças: legenda acima de Quadro,
// Tabela e Figura; tabela com número (alguma célula numérica fora da 1ª coluna)
// só com bordas horizontais no cabeçalho e no fim, números à direita (skill
// formatacao-tabelas-xlsx, seções 4 e 5); quadro (legenda "Quadro") sempre com
// grade completa, preta e de mesma espessura (ABNT), mesmo com números;
// imagem em linha própria no formato ![texto](caminho relativo ao .md);
// linhas de citação (>) e comentários HTML de rascunho são omitidos.
// Larguras de coluna pelo conteúdo e <br> na célula para linhas separadas. Regras suplementares de _docs/_instrucoes/1d_formatacao.md: título 1 à
// esquerda; título 2 em caixa alta sem negrito; nenhum espaço antes ou depois dos títulos (04/11/2026);
// espaços entre blocos feitos com linhas em branco de espaçamento simples, e não com o espaçamento do
// parágrafo (13/11/2026): 6 pt depois do parágrafo do corpo, 12 pt antes da legenda, depois da fonte
// (ou da nota) e entre as referências; referências à esquerda, em espaço simples, sob o título
// REFERÊNCIAS centralizado e em negrito (manual da UFBA), reunidas no fim no trabalho inteiro; células
// centradas na vertical; coluna de quadro só com palavras únicas centrada; legenda e fonte centralizadas;
// nota justificada, em Arial 10.
//
// Versões (_docs/_instrucoes/1c_versoes.md): o TMin é o padrão, com os .md e os
// .docx dos capítulos em textos-tcc/capitulos/ e o trabalho inteiro em textos-tcc/; o TMax fica em
// textos-tcc/capitulos/TMax/ (.md em TMax/_md/, só dos capítulos que diferem). A saída
// leva o texto só quando o capítulo difere entre as versões (<nome>_<TMin|TMax>_v<n>;
// senão, <nome>_v<n>), com n = maior versão já existente + 1; a anterior vai para
// a pasta _arquivo/ ao lado.
//
// Uso: node "_src/outros/G4_textos/gerar_docx_capitulo.js" textos-tcc/capitulos/6_plano_de_marketing.md
// Trabalho inteiro (cada capítulo começa em página nova), com PDF:
//   node "_src/outros/G4_textos/gerar_docx_capitulo.js" --trabalho TMin --pdf
//   node "_src/outros/G4_textos/gerar_docx_capitulo.js" --trabalho TMax --pdf
// --vermelho "COHEN|WILSON": frases do corpo que citam esses autores saem em vermelho
// (revisão das referências; regex sem diferenciar maiúsculas).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ImageRun,
  AlignmentType, HeadingLevel, LevelFormat, BorderStyle, ShadingType, PageNumber, Header, VerticalAlign,
  ExternalHyperlink,
} = require("docx");

const ROOT = path.resolve(__dirname, "..", "..", "..");
const CAP = path.join(ROOT, "textos-tcc", "capitulos");
const MD_TMIN = CAP, MD_TMAX = path.join(CAP, "TMax", "_md");
const ARGS = process.argv.slice(2);
const opcao = (nome) => { const i = ARGS.indexOf(nome); return i < 0 ? null : ARGS[i + 1]; };
const PDF = ARGS.includes("--pdf");
const TRABALHO = opcao("--trabalho");
const VERMELHO = opcao("--vermelho") ? new RegExp(opcao("--vermelho"), "i") : null;
const numero = (f) => Number(path.basename(f).match(/^\d+/)?.[0] ?? 99);

// Quatro partes independentes do trabalho, cada uma com as suas próprias referências no fim
// (16/11/2026): para editar cada bloco num chat separado, sem que um interfira no outro.
//   node "_src/outros/G4_textos/gerar_docx_capitulo.js" --partes [--pdf]
const PARTES = {
  1: { nome: "TCC_luderia_parte1_introducao_referencial_metodologia", caps: [1, 2, 3] },
  2: { nome: "TCC_luderia_parte2_sumario_mercado_marketing", caps: [4, 5, 6] },
  3: { nome: "TCC_luderia_parte3_operacional_juridico", caps: [7, 8] },
  4: { nome: "TCC_luderia_parte4_financeiro_risco_consideracoes", caps: [9, 10, 11] },
};
// --parte 2,4 regenera só as partes indicadas, para não sobrescrever as que estão sendo editadas
const PARTES_SEL = opcao("--parte") ? opcao("--parte").split(",").map((x) => Number(x.trim())) : null;
const PARTES_MODO = ARGS.includes("--partes") || Boolean(PARTES_SEL);
// Referências reunidas no fim do bloco montado: no trabalho inteiro e em cada parte.
const REFERENCIAS_NO_FIM = Boolean(TRABALHO) || PARTES_MODO;

let MDS, TEXTO, BASE;
if (PARTES_MODO) {
  // as partes são montadas uma a uma no fim do arquivo
} else if (TRABALHO) {
  // TMin: todos os .md de textos-tcc/capitulos/; TMax: os mesmos, trocados pelos de TMax/_md/ quando houver.
  MDS = fs.readdirSync(MD_TMIN).filter((f) => /^\d+_.*\.md$/.test(f)).sort((a, b) => numero(a) - numero(b))
    .map((f) => (TRABALHO === "TMax" && fs.existsSync(path.join(MD_TMAX, f)) ? path.join(MD_TMAX, f) : path.join(MD_TMIN, f)));
  TEXTO = TRABALHO === "TMin" ? "" : TRABALHO; // desde 13/11/2026 o TMin sai sem a sigla: TCC_luderia_v<n>
  BASE = path.join(TRABALHO === "TMax" ? path.join(CAP, "TMax") : path.dirname(CAP), "TCC_luderia");
} else {
  MDS = ARGS.filter((a, i) => a.endsWith(".md") && !["--saida", "--texto"].includes(ARGS[i - 1]))
    .map((a) => path.resolve(ROOT, a));
  if (!MDS.length || !MDS.every((m) => fs.existsSync(m))) { console.error("Informe o .md do capítulo ou --trabalho TMin|TMax."); process.exit(1); }
  const md = MDS[0], dir = path.dirname(md), nome = path.basename(md, ".md");
  const tmax = dir === MD_TMAX, tmin = dir === MD_TMIN;
  TEXTO = opcao("--texto") ?? (tmax ? "TMax" : "");
  BASE = opcao("--saida") ? path.resolve(ROOT, opcao("--saida"))
    : path.join(path.basename(dir) === "_md" ? path.dirname(dir) : dir, nome);
}

// Próxima versão de <BASE>[_<TEXTO>]: procura na pasta e em _arquivo/ e arquiva as atuais.
function versionar(base, texto) {
  const dir = path.dirname(base), arq = path.join(dir, "_arquivo");
  const sufixo = texto ? `_${texto}` : "";
  // sem sufixo, os nomes antigos com _TMin contam na numeração (TCC_luderia_TMin_v32 → TCC_luderia_v33)
  const re = new RegExp(`^${path.basename(base).replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}${sufixo || "(?:_TMin)?"}_v(\\d+)\\.(docx|pdf)$`);
  const achados = [dir, arq].filter(fs.existsSync).flatMap((d) => fs.readdirSync(d).map((f) => [d, f, f.match(re)]))
    .filter(([, , m]) => m);
  const n = Math.max(0, ...achados.map(([, , m]) => Number(m[1]))) + 1;
  fs.mkdirSync(arq, { recursive: true });
  for (const [d, f] of achados) if (d === dir) fs.renameSync(path.join(d, f), path.join(arq, f));
  return `${base}${sufixo}_v${n}`;
}
const OUT = PARTES_MODO ? null : versionar(BASE, TEXTO) + ".docx";

const FONTE = "Arial";
const TAM = 24;        // 12 pt
const TAM_QUADRO = 20; // 10 pt
const CM = 567;        // DXA por centímetro
const LARGURA = 11906 - 3 * CM - 2 * CM; // A4 menos margens esquerda e direita
const ENTRELINHA = 360; // 1,5
const SIMPLES = 240;

// Linha em branco de espaçamento simples, com a altura dada pelo corpo da fonte (pt): é o que separa
// os blocos, no lugar do espaçamento antes e depois do parágrafo (_docs/_instrucoes/1d_formatacao.md).
function branco(pt = 12, keepNext = false) {
  const p = new Paragraph({ keepNext, spacing: { line: SIMPLES, before: 0, after: 0 }, indent: { firstLine: 0 },
    run: { size: pt * 2 }, children: [new TextRun({ text: "", font: FONTE, size: pt * 2 })] });
  p._branco = true; // marca para não empilhar duas linhas em branco seguidas
  return p;
}

// Divide o texto em trechos com **negrito**, *itálico* e `código`.
function runs(texto, base = {}) {
  const partes = texto.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g).filter(Boolean);
  return partes.map((p) => {
    let t = p, bold = base.bold, italics = base.italics;
    if (p.startsWith("**") && p.endsWith("**")) { t = p.slice(2, -2); bold = true; }
    else if (p.startsWith("*") && p.endsWith("*") && p.length > 2) {
      // nas referências, o título (*...*) sai em negrito, não em itálico (24/11/2026)
      t = p.slice(1, -1); if (base.destaqueNegrito) bold = true; else italics = true;
    }
    else if (p.startsWith("`") && p.endsWith("`")) { t = p.slice(1, -1); }
    return new TextRun({ text: t, bold, italics, color: base.color, font: FONTE, size: base.size || TAM });
  });
}

// Com --vermelho, as frases que citam os autores indicados saem em vermelho.
function runsCorpo(texto) {
  if (!VERMELHO || !VERMELHO.test(texto)) return runs(texto);
  // Frase termina em . ! ? fora de parênteses, para "p. 13" e "et al." não cortarem a citação.
  const frases = [];
  let ini = 0, nivel = 0;
  for (let i = 0; i < texto.length; i++) {
    const c = texto[i];
    if (c === "(") nivel++;
    else if (c === ")") nivel = Math.max(0, nivel - 1);
    else if (".!?".includes(c) && !nivel && texto[i + 1] === " ") { frases.push(texto.slice(ini, i + 1)); ini = i + 1; }
  }
  frases.push(texto.slice(ini));
  return frases.filter(Boolean).flatMap((f) => runs(f, VERMELHO.test(f) ? { color: "FF0000" } : {}));
}

// Linha de equação numerada "x = y (n)" e as linhas de conta que a seguem ("6,40 × 7,69 = 49,22 ...").
const EQUACAO = /^[^|#*].{0,110} = .*\(\d+\)$/;
const CONTA = /^[\d(−-].{0,110} = /;
// Linha em branco que fica no documento (as de branco() saem no filtro final).
function brancoEquacao() {
  return new Paragraph({ spacing: { line: SIMPLES, before: 0, after: 0 }, indent: { firstLine: 0 },
    run: { size: TAM_QUADRO }, children: [new TextRun({ text: "", font: FONTE, size: TAM_QUADRO })] });
}
function linhaEquacao(texto) {
  return new Paragraph({ children: runs(texto, { size: TAM_QUADRO }), alignment: AlignmentType.CENTER,
    indent: { firstLine: 0 }, keepNext: true, spacing: { line: SIMPLES, before: 0, after: 0 } });
}

function corpo(texto) {
  return new Paragraph({
    children: runsCorpo(texto),
    alignment: AlignmentType.JUSTIFIED,
    indent: { firstLine: Math.round(1.0 * CM) },
    // 17/11/2026: sem linha em branco entre parágrafos; o intervalo vem de 6 pt depois do parágrafo.
    spacing: { line: ENTRELINHA, before: 0, after: 120 },
  });
}

// Legenda (título acima) ou fonte (abaixo): Arial 10, centralizada, espaço simples.
function legenda(texto, fonte = false) {
  return new Paragraph({
    children: runs(texto, { size: TAM_QUADRO }),
    alignment: AlignmentType.CENTER,
    keepNext: !fonte,
    spacing: { line: SIMPLES, before: fonte ? 60 : 120, after: fonte ? 240 : 0 },
  });
}

// Nota abaixo da fonte: Arial 10, justificada, espaço simples.
function nota(texto) {
  return new Paragraph({ children: runs(texto, { size: TAM_QUADRO }), alignment: AlignmentType.JUSTIFIED,
    indent: { firstLine: 0 }, spacing: { line: SIMPLES, before: 0, after: 240 } });
}

const NUM = /^[-−]?(R\$ ?)?[\d.]+(,\d+)?%?$/;

// Larguras das colunas pelo conteúdo: cada coluna recebe, no mínimo, o espaço da maior
// palavra; o que sobra vai para as colunas de mais texto, na proporção do que falta
// para caberem em uma linha. Colunas de pouco texto ficam estreitas, e as de muito
// texto ganham largura e ocupam menos linhas.
const CHAR = 105, CHAR_NEGRITO = 115, MARGEM = 170; // DXA por caractere (Arial 10) e margens da célula
function largurasAuto(linhas) {
  const n = linhas[0].length;
  const minimo = [], preferido = [];
  for (let j = 0; j < n; j++) {
    let maior = 0, palavra = 0;
    linhas.forEach((l, i) => {
      const cw = i === 0 ? CHAR_NEGRITO : CHAR;
      String(l[j] || "").replace(/[*`]/g, "").split("<br>").forEach((trecho) => {
        maior = Math.max(maior, trecho.length * cw);
        trecho.split(/\s+/).forEach((w) => { palavra = Math.max(palavra, w.length * cw); });
      });
    });
    minimo.push(palavra + MARGEM);
    preferido.push(Math.max(maior, palavra) + MARGEM);
  }
  const somaMin = minimo.reduce((a, b) => a + b, 0), somaPref = preferido.reduce((a, b) => a + b, 0);
  let larg;
  if (somaMin >= LARGURA) larg = minimo.map((m) => (m / somaMin) * LARGURA);
  else if (somaPref <= LARGURA) larg = preferido.map((p) => (p / somaPref) * LARGURA);
  else {
    const falta = preferido.map((p, j) => p - minimo[j]), somaFalta = falta.reduce((a, b) => a + b, 0);
    larg = minimo.map((m, j) => m + ((LARGURA - somaMin) * falta[j]) / somaFalta);
  }
  const inteiras = larg.map(Math.floor);
  inteiras[n - 1] += LARGURA - inteiras.reduce((a, b) => a + b, 0);
  return inteiras;
}

function quadro(linhas, tipo) {
  const cab = linhas[0];
  const numerica = linhas.slice(1).some((l) => l.slice(1).some((c) => NUM.test(c)));
  // Quadro: coluna em que toda célula tem uma só palavra fica centrada.
  const palavra = (c) => /^\S+$/.test(c.replace(/\*/g, ""));
  const centrada = cab.map((_, j) => !numerica && linhas.slice(1).every((l) => !l[j] || palavra(l[j]))
    && linhas.slice(1).some((l) => l[j]));
  // Número sempre à direita, salvo coluna discreta de inteiros de um dígito, ano ou código (25/11/2026).
  const discreta = cab.map((h, j) => {
    const vs = linhas.slice(1).map((l) => (l[j] || "").replace(/\*/g, "").trim()).filter((v) => NUM.test(v));
    return vs.length > 0 && vs.every((v) => /^\d+$/.test(v)) && new Set(vs.map((v) => v.length)).size === 1
      && (vs[0].length === 1 || /^(Ano|CBO|Código)$/.test(h.replace(/\*/g, "").trim()));
  });
  const alinha = (celula, i, j) => {
    if (i === 0) return AlignmentType.CENTER;
    if (NUM.test(celula.replace(/\*/g, "").trim())) return discreta[j] ? AlignmentType.CENTER : AlignmentType.RIGHT;
    return centrada[j] ? AlignmentType.CENTER : AlignmentType.LEFT;
  };
  const larguras = largurasAuto(linhas);
  const n = cab.length, ultima = linhas.length - 1;
  const borda = { style: BorderStyle.SINGLE, size: 6, color: "000000" }; // 0,75 pt
  const nada = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const ehQuadro = !numerica || tipo === "Quadro";
  // Quadro (24/11/2026): só a borda externa; cabeçalho purple 700 (7E22CE) com texto branco,
  // zebrado gray 100 (F3F4F6) só em quadro sem linha de grupo; grupo em purple 300 (D8B4FE).
  // Tabela numérica: só bordas horizontais no cabeçalho e no fim (1d_formatacao.md).
  const bordas = (i, j, span = 1) => ehQuadro ? {
    top: i === 0 ? borda : nada, bottom: i === ultima ? borda : nada,
    left: j === 0 ? borda : nada, right: j + span >= n ? borda : nada,
  } : {
    top: i === 0 ? borda : nada, left: nada, right: nada,
    bottom: (i === 0 || i === ultima) ? borda : nada,
  };
  // linha de grupo: só a primeira célula preenchida, em negrito (ex.: "**Impacto alto**")
  const grupo = (l) => /^\*\*.+\*\*$/.test(l[0]) && l.slice(1).every((c) => !c);
  let zebra = 0;
  const temGrupo = linhas.slice(1).some(grupo); // quadro com linha de grupo não tem zebrado
  const PAD = 57, PAD_CAB = 113; // 0,1 cm nas células; 0,2 cm em cima e embaixo no cabeçalho do quadro
  const celula = (texto, i, j, fill, cor, span = 1) => new TableCell({
    width: { size: larguras.slice(j, j + span).reduce((x, y) => x + y, 0), type: WidthType.DXA },
    columnSpan: span > 1 ? span : undefined,
    borders: bordas(i, j, span),
    margins: (ehQuadro && i === 0) ? { top: PAD_CAB, bottom: PAD_CAB, left: PAD, right: PAD }
      : { top: PAD, bottom: PAD, left: PAD, right: PAD },
    verticalAlign: VerticalAlign.CENTER,
    shading: { type: ShadingType.CLEAR, fill, color: "auto" },
    children: texto.split("<br>").map((trecho) => new Paragraph({
      children: runs(trecho.trim(), { bold: i === 0, size: TAM_QUADRO, color: cor }),
      alignment: span > 1 ? AlignmentType.CENTER : alinha(texto, i, j),
      spacing: { line: SIMPLES, after: 0 },
    })),
  });
  return new Table({
    width: { size: LARGURA, type: WidthType.DXA },
    columnWidths: larguras,
    rows: linhas.map((linha, i) => {
      let fill = "FFFFFF", cor;
      if (ehQuadro && i === 0) { fill = "7E22CE"; cor = "FFFFFF"; }
      else if (ehQuadro && grupo(linha)) {
        zebra = 0;
        return new TableRow({ cantSplit: true, children: [celula(linha[0], i, 0, "D8B4FE", undefined, n)] });
      } else if (ehQuadro && i > 0 && !temGrupo) { if (zebra++ % 2 === 1) fill = "F3F4F6"; }
      return new TableRow({ tableHeader: i === 0, cantSplit: true,
        children: linha.map((c, j) => celula(c, i, j, fill, cor)) });
    }),
  });
}

// Título 1 (capítulo): caixa alta, negrito, à esquerda, sem recuo. Título sem número (REFERÊNCIAS):
// igual, mas centralizado (manual da UFBA).
function titulo1(texto, quebra, centro = false) {
  return new Paragraph({ heading: HeadingLevel.TITLE, alignment: centro ? AlignmentType.CENTER : AlignmentType.LEFT, indent: { firstLine: 0 },
    pageBreakBefore: quebra, keepNext: true, children: runs(texto.toUpperCase(), { bold: true }),
    spacing: { line: ENTRELINHA, before: 240, after: 120 } });
}

// Referências: só à margem esquerda, espaço simples, sem recuo, e uma linha em branco de 12 pt
// entre uma e outra (NBR 6023 e manual da UFBA; _docs/_instrucoes/1d_formatacao.md).
// Título em negrito e endereço eletrônico como link azul (0563C1) e sublinhado (24/11/2026).
function referencia(texto) {
  const filhos = texto.split(/(https?:\/\/[^\s,;]+?)(?=[.,;]?(?:\s|$))/g).filter(Boolean).flatMap((t) =>
    /^https?:\/\//.test(t)
      ? [new ExternalHyperlink({ link: t, children: [new TextRun({ text: t, font: FONTE, size: TAM,
          color: "0563C1", underline: { type: "single", color: "0563C1" } })] })]
      : runs(t, { destaqueNegrito: true }));
  return [new Paragraph({ children: filhos, alignment: AlignmentType.LEFT,
    indent: { firstLine: 0 }, spacing: { line: SIMPLES, before: 0, after: 120 } })];
}

// No trabalho inteiro, as listas de cada capítulo viram uma só, no fim, em ordem alfabética e sem repetição.
const REFS = new Set();

let instancia = 0; // contínua entre capítulos, para cada lista numerada recomeçar em 1

// Linha em branco depois de um título quando o que vem a seguir é texto (parágrafo ou lista), e não
// outro título; antes de legenda, a linha em branco já sai com a própria legenda (1d_formatacao.md).
function brancoAposTitulo(linhas, i, blocos) {
  let j = i + 1;
  while (j < linhas.length) {
    const t = linhas[j].trim();
    if (t.startsWith("<!--")) { while (j < linhas.length && !linhas[j].includes("-->")) j++; j++; continue; }
    if (!t || /^-{3,}$/.test(t) || linhas[j].startsWith(">")) { j++; continue; }
    break;
  }
  const prox = j < linhas.length ? linhas[j] : "";
  if (prox && !/^#{1,3} /.test(prox) && !/^\*\*(Quadro|Tabela|Figura|Gráfico) [\d.]+/.test(prox)) blocos.push(branco(12, true));
}

function converte(md, MD, blocos = []) {
  const linhas = md.split("\n");
  let referencias = false;
  let anteriorNumerada = false;
  let tipoLegenda = null;
  for (let i = 0; i < linhas.length; i++) {
    const l = linhas[i];
    if (l.trim().startsWith("<!--")) { while (i < linhas.length && !linhas[i].includes("-->")) i++; continue; }
    if (!l.trim() || /^-{3,}$/.test(l.trim()) || l.startsWith(">")) continue;
    const numerada = /^\d+\. /.test(l);
    if (numerada && !anteriorNumerada) instancia++;
    anteriorNumerada = numerada;

    if (l.startsWith("# ")) {
      // sem linha em branco sobrando antes do título: com o pageBreakBefore do título, a linha
      // vazia sobrava no fim da página anterior e gerava uma página em branco (17/11/2026).
      while (blocos.length && blocos[blocos.length - 1]._branco) blocos.pop();
      blocos.push(titulo1(l.slice(2), blocos.length > 0));
      brancoAposTitulo(linhas, i, blocos);
    } else if (l.startsWith("## ")) {
      blocos.push(new Paragraph({ heading: HeadingLevel.HEADING_1, keepNext: true,
        children: runs(l.slice(3).toUpperCase(), { bold: false }), spacing: { line: ENTRELINHA, before: 240, after: 120 } }));
      brancoAposTitulo(linhas, i, blocos);
    } else if (l.startsWith("### ")) {
      blocos.push(new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true,
        children: runs(l.slice(4), { bold: true }), spacing: { line: ENTRELINHA, before: 240, after: 120 } }));
      brancoAposTitulo(linhas, i, blocos);
    } else if (/^\*\*Refer[êe]ncias[^*]*\*\*/.test(l.trim())) {
      // "Referências citadas neste capítulo": como o título 1, sem número (só no capítulo avulso).
      referencias = true;
      if (!REFERENCIAS_NO_FIM) blocos.push(titulo1(l.trim().replace(/\*\*/g, "").toUpperCase(), true, true), branco(12));
    } else if (/^\*\*(Quadro|Tabela|Figura|Gráfico) [\d.]+/.test(l)) {
      tipoLegenda = l.match(/^\*\*(Quadro|Tabela|Figura|Gráfico)/)[1];
      // sem linha em branco entre o texto e a legenda (24/11/2026): o intervalo é o de 6 pt da legenda
      while (blocos.length && blocos[blocos.length - 1]._branco) blocos.pop();
      blocos.push(legenda(l));
    } else if (/^!\[[^\]]*\]\([^)]+\)/.test(l.trim())) {
      const arq = path.resolve(path.dirname(MD), l.trim().match(/\(([^)]+)\)/)[1]);
      const buf = fs.readFileSync(arq);
      const larg = buf.readUInt32BE(16), alt = buf.readUInt32BE(20); // cabeçalho PNG
      const w = Math.round((LARGURA / 1440) * 96);
      // teto de altura (16/11/2026): a área de texto tem 24,7 cm; figura mais alta que 20 cm
      // (a planta do cap. 7 saía com 26,8 cm) não cabe na página e o LibreOffice a descarta.
      const HMAX = Math.round((20 / 2.54) * 96);
      const h0 = Math.round(w * alt / larg);
      const escala = h0 > HMAX ? HMAX / h0 : 1;
      const wFinal = Math.round(w * escala), hFinal = Math.round(h0 * escala);
      blocos.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { after: 0 },
        children: [new ImageRun({ type: "png", data: buf, transformation: { width: wFinal, height: hFinal } })] }));
    } else if (l.startsWith("Fonte:")) {
      blocos.push(legenda(l, true));
      // nota logo abaixo da fonte; depois, a linha em branco que fecha a tabela, o quadro ou a figura
      let j = i + 1;
      while (j < linhas.length && !linhas[j].trim()) j++;
      if (j < linhas.length && linhas[j].startsWith("Nota:")) { blocos.push(nota(linhas[j])); i = j; }
      blocos.push(branco(12));
    } else if (l.startsWith("|")) {
      const tab = [];
      while (i < linhas.length && linhas[i].startsWith("|")) {
        const cels = linhas[i].slice(1, -1).split("|").map((c) => c.trim());
        if (!cels.every((c) => /^-+$/.test(c))) tab.push(cels);
        i++;
      }
      i--;
      blocos.push(quadro(tab, tipoLegenda));
      tipoLegenda = null;
    } else if (/^\s*- /.test(l)) {
      blocos.push(new Paragraph({ children: runsCorpo(l.replace(/^\s*- /, "")),
        alignment: AlignmentType.JUSTIFIED,
        numbering: { reference: "topicos", level: 0 }, spacing: { line: ENTRELINHA, after: 120 } }));
    } else if (numerada) {
      blocos.push(new Paragraph({ children: runsCorpo(l.replace(/^\d+\. /, "")),
        alignment: AlignmentType.JUSTIFIED,
        numbering: { reference: "numerada", level: 0, instance: instancia }, spacing: { line: ENTRELINHA, after: 120 } }));
    } else if (EQUACAO.test(l.trim())) {
      // Equação (24/11/2026): duas linhas em branco de espaçamento simples, sem espaço antes e
      // depois, entre o texto e as linhas da fórmula, em cima e embaixo; fórmula e contas
      // centralizadas, Arial 10, espaçamento simples.
      while (blocos.length && blocos[blocos.length - 1]._branco) blocos.pop();
      blocos.push(brancoEquacao(), brancoEquacao(), linhaEquacao(l.trim()));
      let j = i + 1;
      for (;;) {
        let k = j;
        while (k < linhas.length && !linhas[k].trim()) k++;
        if (k < linhas.length && CONTA.test(linhas[k].trim())) { blocos.push(linhaEquacao(linhas[k].trim())); j = k + 1; }
        else break;
      }
      i = j - 1;
      blocos.push(brancoEquacao(), brancoEquacao());
    } else if (referencias) {
      if (REFERENCIAS_NO_FIM) REFS.add(l.trim()); else blocos.push(...referencia(l));
    } else {
      blocos.push(corpo(l), branco(12));
    }
  }
  return blocos;
}

function trabalho(arquivos = MDS) {
  const blocos = arquivos.reduce((b, md) => converte(fs.readFileSync(md, "utf-8"), md, b), []);
  if (!REFERENCIAS_NO_FIM || !REFS.size) return blocos;
  const chave = (r) => r.replace(/[*`]/g, "").normalize("NFD").replace(/[̀-ͯ]/g, "");
  // Comparação por caractere: o "." do autor sozinho vem antes do ";" da coautoria.
  const ordem = [...REFS].sort((a, b) => (chave(a).toUpperCase() < chave(b).toUpperCase() ? -1 : 1));
  return [...blocos, titulo1("REFERÊNCIAS", true, true), branco(12), ...ordem.flatMap(referencia)];
}

function documento(blocos) {
  return new Document({
  styles: {
    default: { document: { run: { font: FONTE, size: TAM } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { font: FONTE, size: TAM, bold: true, color: "000000" } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONTE, size: TAM, bold: false, color: "000000" }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONTE, size: TAM, bold: true, color: "000000" }, paragraph: { outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "topicos", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 709, hanging: 284 } } } },
      ] },
      { reference: "numerada", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 709, hanging: 360 } } } },
      ] },
    ],
  },
  sections: [{
    properties: { page: {
      size: { width: 11906, height: 16838 },
      margin: { top: 3 * CM, left: 3 * CM, bottom: 2 * CM, right: 2 * CM },
    } },
    // número da página no canto superior direito (NBR 14724 e manual da UFBA)
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: FONTE, size: TAM_QUADRO })] })] }) },
    // as linhas em branco de espaçamento saem do documento: o intervalo é o "depois" dos parágrafos
    children: blocos.filter((b) => !b._branco),
  }],
  });
}

function convertePdf(arq) {
  if (!PDF) return;
  const soffice = "/Applications/LibreOffice.app/Contents/MacOS/soffice";
  require("child_process").execFileSync(soffice, ["--headless", "--convert-to", "pdf", "--outdir", path.dirname(arq), arq],
    { stdio: "ignore" });
  console.log(`OK: ${path.relative(ROOT, arq.replace(/\.docx$/, ".pdf"))}`);
}

// uma parte por vez, com REFS e a numeração das listas reiniciadas: cada .docx é autônomo
async function partes() {
  const todos = fs.readdirSync(MD_TMIN).filter((f) => /^\d+_.*\.md$/.test(f));
  for (const [n, parte] of Object.entries(PARTES)) {
    if (PARTES_SEL && !PARTES_SEL.includes(Number(n))) continue;
    const arquivos = parte.caps.map((c) => {
      const f = todos.find((x) => numero(x) === c);
      if (!f) throw new Error(`Capítulo ${c} não encontrado em ${MD_TMIN}`);
      return path.join(MD_TMIN, f);
    });
    REFS.clear();
    instancia = 0;
    const blocos = trabalho(arquivos);
    const arq = versionar(path.join(path.dirname(CAP), parte.nome), "") + ".docx";
    fs.writeFileSync(arq, await Packer.toBuffer(documento(blocos)));
    console.log(`OK: ${path.relative(ROOT, arq)} (capítulos ${parte.caps.join(", ")})`);
    convertePdf(arq);
  }
}

if (PARTES_MODO) {
  partes().catch((e) => { console.error(e); process.exit(1); });
} else {
  Packer.toBuffer(documento(trabalho())).then((buf) => {
    fs.writeFileSync(OUT, buf);
    console.log(`OK: ${path.relative(ROOT, OUT)}`);
    convertePdf(OUT);
  });
}
