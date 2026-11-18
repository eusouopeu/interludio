// ==UserScript==
// @name         Busca de estabelecimentos no Google Maps (TCC Luderia)
// @namespace    tcc-luderia
// @version      2026.11.16-1
// @description  Faz no Google Maps as buscas "<termo> em <cidade>" da etapa 1 do B1 (15 termos × 28 cidades), lê a lista de resultados de cada uma (nome, place_id, nota, nº de avaliações, categoria, endereço, coordenada) e exporta os candidatos em CSV para dados-brutos/B1_estabelecimentos/busca_maps/.
// @match        https://www.google.com/maps/*
// @match        https://www.google.com.br/maps/*
// @match        https://www.google.com/sorry/*
// @match        https://www.google.com.br/sorry/*
// @run-at       document-idle
// @noframes
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_deleteValue
// @grant        GM_download
// @downloadURL  https://raw.githubusercontent.com/eusouopeu/interludio/main/_src/webScripts/_instalaveis/maps_busca.user.js
// @updateURL    https://raw.githubusercontent.com/eusouopeu/interludio/main/_src/webScripts/_instalaveis/maps_busca.user.js
// ==/UserScript==
// Gerado por gerar_instalaveis.py a partir de B1_estabelecimentos/maps_busca.user.js; não editar aqui.

// ---------- lista_maps_busca.js ----------
// lista_maps_busca.js: itens do menu do maps_busca.user.js (Busca de estabelecimentos no Maps).
// O carregador do Tampermonkey lê este arquivo (@require) antes do script; editar aqui
// muda o menu no próximo recarregar da página, sem reinstalar.

// Termos e cidades da etapa 1 do B1 (_src/pyScripts/B1_Estabelecimentos/1_collect/B1c_places.py):
// os 15 termos de busca e as 27 capitais, mais Campinas (15ª metrópole da REGIC 2018, a única
// que não é capital). Cada busca é "<termo> em <cidade>", como na coleta pela Places API.
// cidades: [cidade, UF]
var LISTA_MAPS_BUSCA = {
  termos: [
    "ludobar", "luderia", "ludoteca", "quiz bar", "board game bar", "board game café",
    "café de jogos de tabuleiro", "bar de jogos de tabuleiro", "jogos de tabuleiro",
    "loja de jogos de tabuleiro", "loja de board game", "loja de card game", "loja de RPG",
    "board game", "clube de jogos de tabuleiro",
  ],
  cidades: [
    ["Rio Branco", "AC"], ["Maceió", "AL"], ["Macapá", "AP"], ["Manaus", "AM"], ["Salvador", "BA"],
    ["Fortaleza", "CE"], ["Brasília", "DF"], ["Vitória", "ES"], ["Goiânia", "GO"], ["São Luís", "MA"],
    ["Cuiabá", "MT"], ["Campo Grande", "MS"], ["Belo Horizonte", "MG"], ["Belém", "PA"],
    ["João Pessoa", "PB"], ["Curitiba", "PR"], ["Recife", "PE"], ["Teresina", "PI"],
    ["Rio de Janeiro", "RJ"], ["Natal", "RN"], ["Porto Alegre", "RS"], ["Porto Velho", "RO"],
    ["Boa Vista", "RR"], ["Florianópolis", "SC"], ["São Paulo", "SP"], ["Aracaju", "SE"],
    ["Palmas", "TO"], ["Campinas", "SP"],
  ],
};

// ---------- maps_busca.user.js ----------
/*
 * Bloco B1, etapa 1: descoberta dos estabelecimentos (a população do trabalho, 3.2 e cap. 5).
 * Coleta: B1_estabelecimentos/ (brutos em dados-brutos/B1_estabelecimentos/busca_maps/).
 *
 * Para que serve: a coleta original (B1c_places.py) usa a Places API, que é paga e pede
 * chave. Este script repete as mesmas buscas no site do Google Maps, sem chave, para a
 * descoberta ser replicável por qualquer pessoa. As buscas são as mesmas: cada termo de
 * lista_maps_busca.js "em" cada cidade (27 capitais e Campinas).
 *
 * Limite a declarar: a lista do site não é idêntica à da API. O site ordena pela área do
 * mapa e pelo navegador de quem busca e mostra até cerca de 120 resultados; a API devolve
 * até 60. O conjunto de candidatos pode diferir do coletado em setembro de 2026; o recorte
 * (mais de 100 avaliações, metrópoles da REGIC) e a triagem seguem no build em Python.
 *
 * Fluxo:
 *  1. Abra o Google Maps. No painel, o menu traz as buscas por cidade, com ✓ lida até o fim
 *     (ou sem resultado), ◐ lista que não chegou ao fim, ! falhou e ○ falta.
 *  2. Escolher uma busca abre a página dela, rola a lista até o fim e guarda os resultados.
 *     "Todas" faz o mesmo com as que faltam, uma após a outra, com pausa de 4 a 8 s.
 *     Rode numa janela própria: aba em segundo plano deixa a fila lenta.
 *  3. "CSV" baixa dois arquivos: os candidatos (uma linha por busca × resultado, com a
 *     posição na lista) e as buscas (uma linha por busca, com a situação).
 *  4. A ficha de cada candidato (horário, site, telefone) sai pelo maps_ficha.user.js.
 *
 * Coletar não descarta nada: o mesmo lugar aparece uma vez por busca em que foi achado, e
 * a união por place_id fica para o build.
 *
 * Leitura (conferida no Maps em 14/11/2026):
 *  - lista: div[role="feed"]; cada resultado, a.hfpxzc (aria-label = nome; o href traz
 *    !3d<lat>!4d<lng>, !1s<id do Maps> e !19s<place_id>);
 *  - cartão (texto do pai do link): "Nome / 4,6(592) / Loja de jogos · · R. Antônio Dias, 201 /
 *    Aberto · Fecha 00:00 · (31) 3646-6046";
 *  - fim da lista: "Você chegou ao final da lista.";
 *  - busca com um só resultado abre direto o lugar (/maps/place/): lê o h1, div.F7nice
 *    e o botão da categoria.
 * Desafio do Google (página /sorry/ ou "tráfego incomum"): a fila para e avisa.
 */

(function () {
  'use strict';

  const NOME = '[Busca no Maps]';
  const CHAVE_DADOS = 'tcc-busca-dados';     // { id da busca: registro }
  const CHAVE_FILA = 'tcc-busca-fila';       // { ativa, parar, ids, pos, abriu }
  const CHAVE_ABRIR = 'tcc-busca-abrir';     // { id, em }: busca aberta pelo menu, a coletar ao carregar
  const CHAVE_ITEM = 'tcc-busca-item';       // busca escolhida no menu
  const CHAVE_MARCAS = 'tcc-busca-marcas';   // { id: true (dada por coletada) | false (desfeita) }
  const CHAVE_EXPORTACAO = 'tcc-busca-exportado-em';
  const PASTA_DOWNLOAD = 'dados-brutos/B1_estabelecimentos/busca_maps';
  const PAUSA_ENTRE_BUSCAS = [4000, 8000];
  const ROLAGENS_MAX = 45; // a lista do site vai até cerca de 120 resultados
  const AVISO_PENDENTES = 25;

  // A lista vem de lista_maps_busca.js, lida pelo carregador (@require) antes deste arquivo.
  if (typeof LISTA_MAPS_BUSCA === 'undefined') {
    const msg = `${NOME} lista_maps_busca.js não foi carregada: reinstale o carregador (python3 _src/outros/G5_outros/gerar_carregadores.py --abrir).`;
    console.error(msg);
    if (typeof alert === 'function') alert(msg);
    return;
  }

  // ---------- utilidades ----------

  const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
  const sortear = ([a, b]) => a + Math.random() * (b - a);
  const semAcento = (t) => String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const slug = (t) => semAcento(t).replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
  const doisDig = (n) => String(n).padStart(2, '0');
  // Data local (não UTC: depois das 21h em Brasília, toISOString já dá o dia seguinte).
  const dataLocal = (d = new Date()) => `${d.getFullYear()}-${doisDig(d.getMonth() + 1)}-${doisDig(d.getDate())}`;
  const horaLocal = (d = new Date()) => `${doisDig(d.getHours())}${doisDig(d.getMinutes())}`;

  function ler(chave, padrao) {
    try { const v = GM_getValue(chave, padrao); return v ?? padrao; } catch (_) { return padrao; }
  }
  function gravar(chave, valor) {
    try { if (valor == null) GM_deleteValue(chave); else GM_setValue(chave, valor); return true; } catch (e) { status(`Não consegui gravar no Tampermonkey: ${e.message}`, 'erro'); return false; }
  }

  // ---------- alvos: uma busca por cidade × termo ----------

  const consultaDe = (termo, cidade) => `${termo} em ${cidade}`;
  const ALVOS = LISTA_MAPS_BUSCA.cidades.flatMap(([cidade, uf]) => LISTA_MAPS_BUSCA.termos.map((termo) => ({
    id: `${slug(cidade)}|${slug(termo)}`, cidade, uf, termo, consulta: consultaDe(termo, cidade), capital: cidade, nome: `${termo} · ${cidade}`,
  })));
  const urlBusca = (a) => `https://www.google.com/maps/search/${encodeURIComponent(a.consulta)}?hl=pt-BR`;

  // Busca aberta na página, pelo texto da URL (/maps/search/<consulta>/). Uma busca de um só
  // resultado vira /maps/place/ e não é reconhecida aqui: vale o pedido gravado (CHAVE_ABRIR, fila).
  function alvoDaUrl(href, alvos = ALVOS) {
    const m = String(href || '').match(/\/maps\/search\/([^/@?]+)/);
    if (!m) return null;
    let texto = '';
    try { texto = decodeURIComponent(m[1].replace(/\+/g, ' ')); } catch (_) { return null; }
    const k = semAcento(texto).replace(/\s+/g, ' ').trim();
    return alvos.find((a) => semAcento(a.consulta) === k) || null;
  }

  // ---------- leitura da lista ----------

  function lerHref(href) {
    const h = String(href || '');
    const coord = h.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/) || [];
    return {
      lat: coord[1] ? +coord[1] : '',
      lng: coord[2] ? +coord[2] : '',
      place_id: (h.match(/!19s(ChIJ[^!?&]+)/) || [])[1] || '',
      id_maps: (h.match(/!1s(0x[0-9a-f]+:0x[0-9a-f]+)/i) || [])[1] || '',
    };
  }

  // Número de avaliações entre parênteses: "(1.731)", "(1,2 mil)" ou "(12 mil)".
  function lerNumeroAvaliacoes(texto) {
    const m = String(texto || '').match(/\(\s*(\d+(?:,\d+)?\s*mil|\d{1,3}(?:[.\s]\d{3})*)\s*\)/i);
    if (!m) return '';
    if (/mil/i.test(m[1])) return String(Math.round(parseFloat(m[1].replace(',', '.')) * 1000));
    return m[1].replace(/\D/g, '');
  }

  const lerNota = (texto) => ((String(texto || '').match(/(^|\s)(\d[.,]\d)(?=\s*\()/) || [])[2] || '').replace(',', '.');

  function situacaoMaps(texto) {
    const t = semAcento(texto);
    if (/permanentemente fechado|fechado permanentemente|permanently closed/.test(t)) return 'fechado permanentemente';
    if (/temporariamente fechado|fechado temporariamente|temporarily closed/.test(t)) return 'fechado temporariamente';
    return '';
  }

  // Cartão da lista: "Nome\n4,6(592)\nLoja de jogos ·  · R. Antônio Dias, 201\nAberto · Fecha 00:00 · (31) 3646-6046"
  function lerCartao(nome, texto, href) {
    const linhas = String(texto || '').split('\n').map((l) => l.trim()).filter(Boolean);
    const ehNota = (s) => /^\d[.,]\d\s*\(/.test(s) || /^\$+$|^R\$/.test(s) || !s;
    const ehHorario = (l) => /^(aberto|fechado|abre|fecha|open|closed|opens|closes|permanentemente|temporariamente)\b/.test(semAcento(l));
    // Linha da categoria: a primeira com "·" que não é a do horário nem a da nota.
    const linhaCat = linhas.find((l) => l.includes('·') && !ehHorario(l) && !/^\d[.,]\d\s*\(/.test(l)) || '';
    const partes = linhaCat.split('·').map((s) => s.trim()).filter((s) => !ehNota(s));
    const notaLinha = linhas.find((l) => /^\d[.,]\d\s*\(/.test(l)) || '';
    // Sem a linha da nota: "Nenhuma avaliação" vale 0; o resto fica em branco (não lida).
    const semAvaliacao = linhas.some((l) => /^(nenhuma avaliacao|sem avaliacoes|no reviews)$/.test(semAcento(l)));
    return {
      nome: String(nome || '').trim(),
      categoria_maps: partes[0] || '',
      endereco: partes.length > 1 ? partes[partes.length - 1] : '',
      nota_media: lerNota(notaLinha),
      n_avaliacoes: notaLinha ? lerNumeroAvaliacoes(notaLinha) : semAvaliacao ? '0' : '',
      situacao_maps: situacaoMaps(linhas.join(' ')),
      ...lerHref(href),
      link_google_maps: String(href || '').split('?')[0],
    };
  }

  const lista = () => document.querySelector('div[role="feed"]');
  const fimDaLista = (feed) => /chegou ao final da lista|reached the end of the list/i.test(feed?.innerText || '');

  function bloqueado() {
    if (/^\/sorry\//.test(location.pathname)) return true;
    if (lista()) return false;
    return /trafego incomum|unusual traffic|nao sou um robo|not a robot/.test(semAcento((document.body?.innerText || '').slice(0, 3000)));
  }

  const semResultados = () => /nao encontrou|nao conseguiu encontrar|nenhum resultado|no results|can't find/
    .test(semAcento(document.querySelector('div[role="main"]')?.innerText || ''));

  const resultadosNaTela = () => [...document.querySelectorAll('a.hfpxzc')]
    .map((a) => lerCartao(a.getAttribute('aria-label'), a.parentElement?.innerText, a.href));

  // Espera a busca: lista, lugar único (h1), "nenhum resultado" ou bloqueio.
  // Sem nenhum desses em 20 s, a busca falhou (não é zero resultados).
  async function esperarBusca() {
    for (let i = 0; i < 40; i++) {
      if (bloqueado()) return 'bloqueado';
      if (lista() && document.querySelector('a.hfpxzc')) return 'lista';
      if (document.querySelector('h1.DUwDvf') && /\/maps\/place\//.test(location.href)) return 'lugar';
      if (semResultados()) return 'vazio';
      await esperar(500);
    }
    return 'falhou';
  }

  // Lê a busca aberta: rola a lista até o fim (ou até parar de crescer) e devolve os cartões.
  async function lerBusca(aoRolar = () => {}) {
    const estado = await esperarBusca();
    if (estado === 'bloqueado' || estado === 'falhou' || estado === 'vazio') return { estado, itens: [], fim: estado === 'vazio' };
    await esperar(1200);
    if (estado === 'lugar') {
      const resumo = document.querySelector('div.F7nice')?.innerText || '';
      const html = document.documentElement.innerHTML;
      const ids = [...new Set(html.match(/ChIJ[\w-]{20,30}/g) || [])];
      return { estado, fim: true, itens: [{
        nome: document.querySelector('h1.DUwDvf')?.innerText.trim() || '',
        categoria_maps: document.querySelector('button[jsaction*="category"]')?.innerText || '',
        endereco: (document.querySelector('button[data-item-id="address"]')?.getAttribute('aria-label') || '').replace(/^(endereço|address):\s*/i, '').trim(),
        nota_media: lerNota(resumo.replace(/\n/g, ' ')),
        n_avaliacoes: lerNumeroAvaliacoes(resumo) || (/nenhuma avaliacao|no reviews/.test(semAcento(resumo)) ? '0' : ''),
        situacao_maps: situacaoMaps(document.querySelector('div[role="main"]')?.innerText.slice(0, 1500) || ''),
        ...lerHref(location.href),
        // O place_id não vem na URL do lugar: só vale o do HTML quando é o único.
        place_id: ids.length === 1 ? ids[0] : '',
        link_google_maps: location.href.split('?')[0],
      }] };
    }
    const feed = lista();
    let antes = -1, parado = 0;
    for (let i = 0; i < ROLAGENS_MAX && !fimDaLista(feed) && !kit.parar; i++) {
      const n = document.querySelectorAll('a.hfpxzc').length;
      if (n === antes) { if (++parado >= 3) break; } else parado = 0;
      antes = n;
      aoRolar(n);
      feed.scrollTop = feed.scrollHeight;
      await esperar(1300);
    }
    return { estado, itens: resultadosNaTela().filter((r) => r.place_id || r.id_maps), fim: fimDaLista(feed) };
  }

  // ---------- registro e estado ----------

  const lerDados = () => ler(CHAVE_DADOS, {}) || {};
  const lerMarcas = () => ler(CHAVE_MARCAS, {}) || {};
  const SITUACAO = { lista: 'lista lida', lugar: 'um só resultado', vazio: 'sem resultado', falhou: 'a busca não carregou', bloqueado: 'bloqueio do Google' };

  function registrar(alvo, r, agora = new Date()) {
    const dados = lerDados();
    dados[alvo.id] = {
      id: alvo.id, cidade: alvo.cidade, uf: alvo.uf, termo: alvo.termo, consulta: alvo.consulta,
      estado: r.estado, fim: !!r.fim, n: r.itens.length, data_coleta: dataLocal(agora), coletado_ms: agora.getTime(),
      url: urlBusca(alvo), itens: r.itens.map((x, i) => ({ ...x, posicao: i + 1 })),
    };
    return gravar(CHAVE_DADOS, dados) ? dados[alvo.id] : null;
  }

  // ok (lida até o fim, um só resultado ou sem resultado), parcial (a lista não chegou ao
  // fim), falha (não carregou ou bloqueio) ou falta. A marca à mão prevalece.
  function estadoBusca(reg, marca) {
    if (marca === true) return 'ok';
    if (marca === false) return 'falta';
    if (!reg) return 'falta';
    if (reg.estado === 'falhou' || reg.estado === 'bloqueado') return 'falha';
    return reg.estado === 'lista' && !reg.fim ? 'parcial' : 'ok';
  }

  // Próxima busca que falta: primeiro na mesma cidade, depois na ordem da lista.
  function proximaQueFalta(idAtual, dados = lerDados(), marcas = lerMarcas(), alvos = ALVOS) {
    const i0 = alvos.findIndex((a) => a.id === idAtual);
    const atual = alvos[i0] || alvos[0];
    const ordem = [...alvos.slice(i0 + 1), ...alvos.slice(0, Math.max(i0, 0))]
      .filter((a) => a.id !== idAtual && estadoBusca(dados[a.id], marcas[a.id]) !== 'ok');
    return ordem.find((a) => a.cidade === atual.cidade) || ordem[0] || null;
  }

  // ---------- exportação ----------

  const COLS = ['place_id', 'id_maps', 'nome', 'endereco', 'categoria_maps', 'nota_media', 'n_avaliacoes', 'situacao_maps', 'lat', 'lng',
    'cidade_busca', 'uf_busca', 'termo_busca', 'consulta', 'posicao', 'n_resultados', 'chegou_ao_fim', 'link_google_maps', 'data_coleta'];
  const COLS_BUSCAS = ['cidade_busca', 'uf_busca', 'termo_busca', 'consulta', 'situacao', 'n_resultados', 'chegou_ao_fim', 'data_coleta', 'url'];

  const naOrdem = (dados, alvos = ALVOS) => alvos.map((a) => dados[a.id]).filter(Boolean);
  const baseBusca = (b) => ({ cidade_busca: b.cidade, uf_busca: b.uf, termo_busca: b.termo, consulta: b.consulta,
    n_resultados: b.n, chegou_ao_fim: b.fim ? 'sim' : 'não', data_coleta: b.data_coleta });
  // Uma linha por busca × resultado: o mesmo lugar se repete entre buscas (a união é do build).
  const linhasCandidatos = (buscas) => buscas.flatMap((b) => b.itens.map((x) => ({ ...x, ...baseBusca(b) })));
  const linhasBuscas = (buscas) => buscas.map((b) => ({ ...baseBusca(b), situacao: SITUACAO[b.estado] || b.estado, url: b.url }));
  const unicos = (buscas) => new Set(buscas.flatMap((b) => b.itens.map((x) => x.place_id || x.id_maps))).size;
  const nomeArquivo = (parte, d = new Date(), sufixo = '') => `${dataLocal(d)}_${horaLocal(d)}_maps_busca_${parte}${sufixo ? `_${sufixo}` : ''}.csv`;

  // Sem argumentos, tudo o que está guardado (candidatos e buscas); com uma busca, só os
  // candidatos dela (opção "baixar cada busca"), e o nome ganha a busca no fim.
  async function baixarCsv(busca = null) {
    const buscas = busca ? [busca] : naOrdem(lerDados());
    const d = new Date();
    await kit.baixarArquivo(nomeArquivo('candidatos', d, busca ? busca.id.replace('|', '_') : ''), kit.csv(linhasCandidatos(buscas), COLS));
    if (!busca) {
      await kit.baixarArquivo(nomeArquivo('buscas', d), kit.csv(linhasBuscas(buscas), COLS_BUSCAS));
      gravar(CHAVE_EXPORTACAO, Date.now());
    }
    return buscas.length;
  }

  const pendentes = (dados, exportadoEm) => Object.values(dados).filter((b) => (b.coletado_ms || 0) > exportadoEm).length;

  // ---------- painel (kit dos painéis: _kit_painel/kit_painel.js) ----------

  // >>> kit_painel (cópia de _src/webScripts/_kit_painel/kit_painel.js; regerar com: node _src/webScripts/_kit_painel/embutir.js)
  // Kit dos painéis dos webscripts do TCC Luderia. Fonte única: o embutir.js copia este
  // bloco para dentro de cada .user.js, entre os marcadores; não editar a cópia.
  // Padrão (o do maps_avaliacoes): canto superior direito, shadow DOM preso ao <html> e
  // reposto se sumir, arrastável e redimensionável com posição salva, Montserrat,
  // Heroicons outline, roxo como cor primária, verde/âmbar/vermelho para o desfecho,
  // explicações em dicas (ⓘ ou sobre o próprio botão) em vez de texto solto; perguntas
  // (confirmar, perguntar) dentro do painel, nunca confirm() ou prompt() do navegador.
  // Só define funções: nada toca o DOM antes de montar() (os testes rodam no Node).
  function kitPainel(op = {}) {
    const P = op.prefixo || op.id || 'tcc';
    const temGM = typeof GM_getValue === 'function' && typeof GM_setValue === 'function';
    const ler = op.ler || ((c, padrao) => {
      try {
        if (temGM) return GM_getValue(c, padrao);
        const v = localStorage.getItem(c);
        return v == null ? padrao : JSON.parse(v);
      } catch (_) { return padrao; }
    });
    const gravar = op.gravar || ((c, v) => {
      try {
        if (temGM) { if (v == null && typeof GM_deleteValue === 'function') GM_deleteValue(c); else GM_setValue(c, v); return; }
        if (v == null) localStorage.removeItem(c); else localStorage.setItem(c, JSON.stringify(v));
      } catch (_) { /* sem armazenamento */ }
    });
    const chave = (s) => `${P}:kit:${s}`;
    const k = {
      el: {}, ocupado: false, parar: false, acoes: [], ler, gravar,
      som: ler(chave('som'), true), autobaixar: ler(chave('autobaixar'), true),
      // Modo semiautomático (fila): baixar o arquivo de cada item (casa, perfil, busca) assim que
      // ele termina, além do arquivo do fim da fila. Desligado por padrão.
      baixarCada: ler(chave('baixarcada'), false),
    };
    const dicas = new WeakMap();
    let hospedeiro = null, painel = null;

    // ---------- elementos ----------
    function criar(tag, props = {}, filhos = []) {
      const n = document.createElement(tag);
      for (const [a, v] of Object.entries(props)) {
        if (v == null) continue;
        if (a === 'dica') dica(n, v);
        else if (a === 'style') n.style.cssText = v;
        else if (a === 'role' || a.startsWith('aria-') || a.startsWith('data-')) n.setAttribute(a, v);
        else n[a] = v;
      }
      for (const f of [].concat(filhos)) {
        if (f == null || f === false) continue;
        n.appendChild(typeof f === 'object' ? f : document.createTextNode(String(f)));
      }
      return n;
    }

    // Heroicons 24/outline (traço 1.5).
    const ICONES = {
      'adjustments-horizontal': 'M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75',
      'arrow-down': 'M19.5 13.5 12 21m0 0-7.5-7.5M12 21V3',
      'arrow-down-on-square': 'M9 8.25H7.5a2.25 2.25 0 0 0-2.25 2.25v9a2.25 2.25 0 0 0 2.25 2.25h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25H15M9 12l3 3m0 0 3-3m-3 3V2.25',
      'arrow-down-on-square-stack': 'M7.5 7.5h-.75A2.25 2.25 0 0 0 4.5 9.75v7.5a2.25 2.25 0 0 0 2.25 2.25h7.5a2.25 2.25 0 0 0 2.25-2.25v-7.5a2.25 2.25 0 0 0-2.25-2.25h-.75m-6 3.75 3 3m0 0 3-3m-3 3V1.5m6 9h.75a2.25 2.25 0 0 1 2.25 2.25v7.5a2.25 2.25 0 0 1-2.25 2.25h-7.5a2.25 2.25 0 0 1-2.25-2.25v-.75',
    'arrow-down-tray': 'M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3',
      'arrow-path': 'M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99',
      'arrow-top-right-on-square': 'M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25',
      'arrow-up': 'M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18',
      'arrow-up-tray': 'M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5',
      'arrow-uturn-right': 'm15 15 6-6m0 0-6-6m6 6H9a6 6 0 0 0 0 12h3',
      'arrow-uturn-left': 'M9 15 3 9m0 0 6-6M3 9h12a6 6 0 0 1 0 12h-3',
      'bell': 'M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0',
      'bell-slash': 'M9.143 17.082a24.248 24.248 0 0 0 3.844.148m-3.844-.148a23.856 23.856 0 0 1-5.455-1.31 8.964 8.964 0 0 0 2.3-5.542m3.155 6.852a3 3 0 0 0 5.667 1.97m1.965-2.277L21 21m-4.225-4.225a23.81 23.81 0 0 0 3.536-1.003A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6.53 6.53m10.245 10.245L6.53 6.53M3 3l3.53 3.53',
      'bookmark': 'M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z',
      'calendar-days': 'M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5',
      'chart-bar': 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z',
      'check': 'm4.5 12.75 6 6 9-13.5',
      'chevron-double-down': 'm4.5 5.25 7.5 7.5 7.5-7.5m-15 6 7.5 7.5 7.5-7.5',
      'chevron-down': 'm19.5 8.25-7.5 7.5-7.5-7.5',
      'chevron-left': 'M15.75 19.5 8.25 12l7.5-7.5',
      'chevron-right': 'm8.25 4.5 7.5 7.5-7.5 7.5',
      'chevron-up': 'm4.5 15.75 7.5-7.5 7.5 7.5',
      'clock': 'M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
      'code-bracket': 'M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5',
      'cube': 'm21 7.5-9-5.25L3 7.5m18 0-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9',
      'document-chart-bar': 'M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25M9 16.5v.75m3-3v3M15 12v5.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z',
      'document-check': 'M10.125 2.25h-4.5c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125v-9M10.125 2.25h.375a9 9 0 0 1 9 9v.375M10.125 2.25A3.375 3.375 0 0 1 13.5 5.625v1.5c0 .621.504 1.125 1.125 1.125h1.5a3.375 3.375 0 0 1 3.375 3.375M9 15l2.25 2.25L15 12',
      'document-duplicate': 'M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75',
      'document-text': 'M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z',
      'exclamation-triangle': 'M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z',
      'eye': 'M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178ZM15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
      'folder': 'M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z',
      'forward': 'M3 8.689c0-.864.933-1.406 1.683-.977l7.108 4.061a1.125 1.125 0 0 1 0 1.954l-7.108 4.061A1.125 1.125 0 0 1 3 16.811V8.69ZM12.75 8.689c0-.864.933-1.406 1.683-.977l7.108 4.061a1.125 1.125 0 0 1 0 1.954l-7.108 4.061a1.125 1.125 0 0 1-1.683-.977V8.69Z',
      'funnel': 'M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 0 1-.659 1.591l-5.432 5.432a2.25 2.25 0 0 0-.659 1.591v2.927a2.25 2.25 0 0 1-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 0 0-.659-1.591L3.659 7.409A2.25 2.25 0 0 1 3 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0 1 12 3Z',
      'hashtag': 'M5.25 8.25h15m-16.5 7.5h15m-1.8-13.5-3.9 19.5m-2.1-19.5-3.9 19.5',
      'information-circle': 'm11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z',
      'magnifying-glass': 'm21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z',
      'map-pin': 'M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z',
      'minus': 'M5 12h14',
      'bolt': 'm3.75 13.5 10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75Z',
      'bolt-slash': 'M11.412 15.655 9.75 21.75l3.745-4.012M9.257 13.5H3.75l2.659-2.849m2.048-2.194L14.25 2.25 12 10.5h8.25l-4.707 5.043M8.457 8.457 3 3m5.457 5.457 7.086 7.086m0 0L21 21',
      'no-symbol': 'M18.364 18.364A9 9 0 0 0 5.636 5.636m12.728 12.728A9 9 0 0 1 5.636 5.636m12.728 12.728L5.636 5.636',
      'play': 'M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z',
      'plus': 'M12 4.5v15m7.5-7.5h-15',
      'queue-list': 'M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 0 1 0 3.75H5.625a1.875 1.875 0 0 1 0-3.75Z',
      'stop': 'M5.25 7.5A2.25 2.25 0 0 1 7.5 5.25h9a2.25 2.25 0 0 1 2.25 2.25v9a2.25 2.25 0 0 1-2.25 2.25h-9a2.25 2.25 0 0 1-2.25-2.25v-9Z',
      'tag': 'M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z M6 6h.008v.008H6V6Z',
      'trash': 'm14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0',
      'truck': 'M8.25 18.75a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 0 1-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 0 0-3.213-9.193 2.056 2.056 0 0 0-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 0 0-10.026 0 1.106 1.106 0 0 0-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12',
      'x-mark': 'M6 18 18 6M6 6l12 12',
    };

    function icone(nome, classe = '') {
      const NS = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(NS, 'svg');
      for (const [a, v] of Object.entries({ viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'aria-hidden': 'true' })) svg.setAttribute(a, v);
      if (classe) svg.setAttribute('class', classe);
      const p = document.createElementNS(NS, 'path');
      p.setAttribute('d', ICONES[nome] || '');
      p.setAttribute('stroke-linecap', 'round');
      p.setAttribute('stroke-linejoin', 'round');
      svg.appendChild(p);
      return svg;
    }

    // ---------- dicas: balão próprio (mais rápido que o title do navegador) ----------
    // Qualquer elemento com dica mostra o balão ao parar o mouse (ou com foco); o ⓘ
    // abre na hora e, clicado, fica fixo até Esc, rolagem ou clique fora.
    let dicaAncora = null, dicaFixa = false, timerDica = 0;

    function dica(n, conteudo) {
      if (!conteudo) { dicas.delete(n); n.removeAttribute('data-dica'); return n; }
      dicas.set(n, conteudo);
      n.setAttribute('data-dica', typeof conteudo === 'string' ? conteudo : '');
      if (typeof conteudo === 'string' && n.tagName === 'BUTTON' && !n.textContent.trim()) n.setAttribute('aria-label', conteudo);
      return n;
    }

    function abrirDica(ancora, fixa = false) {
      clearTimeout(timerDica);
      const c = dicas.get(ancora);
      if (!c || !k.el.dica) return;
      dicaAncora = ancora; dicaFixa = fixa;
      const v = typeof c === 'function' ? c() : c;
      k.el.dica.replaceChildren(typeof v === 'object' ? v : document.createTextNode(String(v)));
      k.el.dica.hidden = false;
      const r = ancora.getBoundingClientRect(), d = k.el.dica.getBoundingClientRect(), M = 10;
      const left = Math.min(Math.max(M, r.left + r.width / 2 - d.width / 2), innerWidth - d.width - M);
      let top = r.bottom + 6;
      if (top + d.height > innerHeight - M) top = Math.max(M, r.top - d.height - 6);
      k.el.dica.style.left = `${left}px`;
      k.el.dica.style.top = `${top}px`;
    }

    function fecharDica() {
      clearTimeout(timerDica);
      if (k.el.dica) k.el.dica.hidden = true;
      dicaAncora = null; dicaFixa = false;
    }

    const comDica = (e) => e.composedPath().find((n) => n.nodeType === 1 && dicas.has(n));

    function ajuda(conteudo, rotulo = 'Explicação') {
      const i = criar('span', { className: 'ajuda', tabIndex: 0, role: 'button', 'aria-label': rotulo }, [icone('information-circle')]);
      return dica(i, conteudo);
    }

    // ---------- controles ----------
    // botao('arrow-down-tray', 'CSV', fn, { classe: 'mini', dica: '…' }); sem texto vira botão-ícone.
    function botao(ico, texto, fn, { classe = '', dica: d = '' } = {}) {
      const b = criar('button', { type: 'button', className: `${texto ? '' : 'ico '}${classe}`.trim(), onclick: fn },
        [ico ? icone(ico) : null, texto || null]);
      if (d) dica(b, d);
      return b;
    }

    // Ação destrutiva em dois cliques: o primeiro arma (vermelho, treme) e o segundo, em até 3 s, executa.
    function botaoPerigo(ico, texto, fn, { classe = '', dica: d = '' } = {}) {
      const b = botao(ico, texto, null, { classe: `perigo ${classe}`, dica: d });
      let armado = 0;
      const desarmar = () => { clearTimeout(armado); armado = 0; b.classList.remove('armado'); dica(b, d); };
      b.onclick = () => {
        if (!armado) {
          b.classList.add('armado');
          dica(b, 'Clique de novo para confirmar');
          abrirDica(b);
          armado = setTimeout(desarmar, 3000);
          return;
        }
        desarmar(); fecharDica(); fn();
      };
      return b;
    }

    // Etiqueta liga/desliga: cinza desligada, azul ligada. `checked` imita a caixa de marcar.
    function etiqueta(rotulo, aoAlternar, { ligada = false, dica: d = '', ico = '' } = {}) {
      const b = criar('button', { type: 'button', className: 'tag' }, [ico ? icone(ico) : null, rotulo]);
      if (d) dica(b, d);
      const pintar = (v) => b.setAttribute('aria-pressed', String(v));
      pintar(ligada);
      Object.defineProperty(b, 'checked', { get: () => b.getAttribute('aria-pressed') === 'true', set: (v) => pintar(!!v) });
      b.onclick = () => { pintar(!b.checked); aoAlternar(b.checked); };
      return b;
    }

    // Botão-ícone de preferência (fica roxo ligado); a dica diz o estado.
    function alternaIcone({ ico, icoDesligado = ico, rotulo, ligado, aoMudar, classe = 'leve' }) {
      const b = criar('button', { type: 'button', className: `ico ${classe}` });
      let v = !!ligado;
      const pintar = () => {
        b.setAttribute('aria-pressed', String(v));
        b.replaceChildren(icone(v ? ico : icoDesligado));
        dica(b, `${rotulo}: ${v ? 'ligado' : 'desligado'}`);
        b.setAttribute('aria-label', rotulo);
      };
      b.onclick = () => { v = !v; pintar(); aoMudar(v); if (dicaAncora === b) abrirDica(b); };
      Object.defineProperty(b, 'checked', { get: () => v, set: (x) => { v = !!x; pintar(); } });
      pintar();
      return b;
    }

    // Opção da fila: baixar cada item ao terminar (k.baixarCada, gravada por script).
    function botaoBaixarCada(rotulo = 'Baixar cada item ao terminar (fila)') {
      return alternaIcone({ ico: 'arrow-down-on-square-stack', rotulo, ligado: k.baixarCada,
        aoMudar: (v) => { k.baixarCada = v; gravar(chave('baixarcada'), v); } });
    }

    // Controle segmentado: [[valor, texto, dica]].
    function pills(opcoes, valor, aoMudar) {
      const caixa = criar('div', { className: 'pills', role: 'tablist' });
      const bs = opcoes.map(([v, t, d]) => {
        const b = criar('button', { type: 'button', className: 'pill', role: 'tab', 'data-valor': v }, [t]);
        if (d) b.appendChild(ajuda(d));
        b.onclick = () => { caixa.valor = v; aoMudar(v); };
        return b;
      });
      Object.defineProperty(caixa, 'valor', {
        get: () => valor,
        set: (v) => { valor = v; for (const b of bs) b.setAttribute('aria-selected', String(b.dataset.valor === String(v))); },
      });
      caixa.append(...bs);
      caixa.valor = valor;
      return caixa;
    }

    // Seção recolhível que lembra se estava aberta.
    const abertos = new Set(ler(chave('abertos'), op.abertos || []));
    function secao(id, cabeca, filhos, aoAbrir = null) {
      const d = criar('details', { open: abertos.has(id) }, [
        criar('summary', {}, [icone('chevron-right', 'seta'), ...[].concat(cabeca)]), ...filhos]);
      d.addEventListener('toggle', () => {
        if (d.open) abertos.add(id); else abertos.delete(id);
        gravar(chave('abertos'), [...abertos]);
        if (d.open && aoAbrir) aoAbrir();
      });
      return d;
    }

    // Botão dentro do <summary> que não abre nem fecha a seção.
    const naoAlterna = (fn) => (e) => { e.preventDefault(); e.stopPropagation(); fn(e); };

    const linha = (filhos, classe = '') => criar('div', { className: `linha ${classe}`.trim() }, filhos);
    const esp = () => criar('span', { className: 'esp' });
    const rotulo = (t, d) => criar('span', { className: 'rotulo' }, [t, d ? ajuda(d) : null]);
    const selo = (t = '', classe = '') => criar('span', { className: `selo ${classe}`.trim(), textContent: t });

    // ---------- status, resumo e progresso ----------
    function animarStatus() {
      const s = k.el.status;
      s.classList.remove('entra');
      void s.offsetWidth;
      s.classList.add('entra');
    }

    function status(t, tipo = '') {
      if (!k.el.status) return;
      const cls = `status${tipo ? ` st-${tipo}` : ''}`;
      if (k.el.status.className.replace(' entra', '') !== cls || k.el.status.textContent !== t) {
        const mudouTipo = k.el.status.className.replace(' entra', '') !== cls;
        k.el.status.className = cls;
        k.el.status.textContent = t;
        if (mudouTipo) animarStatus();
      }
      if (tipo === 'ok' || tipo === 'erro' || tipo === 'alerta') estado(tipo);
    }

    // Resumo do desfecho: cabeçalho com a cor do resultado, contagens e avisos.
    // linhas: [[número, texto, detalhe]]; avisos: textos em âmbar.
    function resumo({ titulo, sub = '', linhas = [], avisos = [], tipo = '' }) {
      if (!k.el.status) return;
      const item = ([n, t, det]) => criar('li', {}, [criar('b', { textContent: String(n) }), ` ${t}`,
        det ? criar('span', { className: 'suave', textContent: ` · ${det}` }) : null]);
      k.el.status.className = `status rico${tipo ? ` st-${tipo}` : ''}`;
      k.el.status.replaceChildren(...[
        criar('div', { className: 'cab' }, [criar('span', { className: 'ponto' }), titulo]),
        sub ? criar('div', { className: 'suave', textContent: sub }) : null,
        linhas.length ? criar('ul', {}, linhas.map(item)) : null,
        ...avisos.filter(Boolean).map((t) => criar('p', { className: 'aviso', textContent: t })),
      ].filter(Boolean));
      animarStatus();
      if (tipo) estado(tipo);
    }

    // Barra de progresso: barra('coleta') cria; progresso('coleta', 0.4, 'texto'),
    // progresso('coleta', true, 'texto') indeterminada e progresso('coleta', null) esconde.
    const barras = {};
    function barra(nome) {
      const b = { preenchido: criar('div', { className: 'preenchido' }), texto: criar('span'), pct: criar('span') };
      b.trilho = criar('div', { className: 'trilho' }, [b.preenchido]);
      b.caixa = criar('div', { className: 'barra', hidden: true }, [criar('div', { className: 'txt' }, [b.texto, b.pct]), b.trilho]);
      barras[nome] = b;
      return b.caixa;
    }

    function progresso(nome, frac, texto = '') {
      const b = barras[nome];
      if (!b) return;
      if (frac == null || frac === false) { b.caixa.hidden = true; return; }
      b.caixa.hidden = false;
      b.texto.textContent = texto;
      const indef = frac === true;
      b.trilho.classList.toggle('indef', indef);
      b.preenchido.classList.toggle('rodando', !indef && k.ocupado);
      if (indef) { b.pct.textContent = ''; return; }
      const pct = Math.round(Math.min(1, Math.max(0, frac)) * 100);
      b.preenchido.style.width = `${pct}%`;
      b.pct.textContent = `${pct}%`;
    }

    // Ponto do cabeçalho (visível minimizado): cinza parado, roxo pulsando em curso,
    // verde concluído, âmbar interrompido ou incerto, vermelho erro.
    function estado(s = '') {
      if (k.el.ponto) k.el.ponto.className = `ponto-estado ${s}`.trim();
    }

    // Liga e desliga as ações conforme a tarefa em curso.
    function atualizarAcoes(ocupado = k.ocupado) {
      for (const b of k.acoes) b.disabled = ocupado;
      if (k.el.parar) k.el.parar.disabled = !ocupado;
      if (ocupado) estado('rodando');
    }

    const botaoParar = (fn = () => { k.parar = true; status('Parando…'); }) =>
      (k.el.parar = botao('stop', '', fn, { classe: 'parar', dica: 'Parar' }));

    // Roda uma tarefa travando as ações; "Parar" põe k.parar = true.
    async function executar(fn, { avisar = true } = {}) {
      if (k.ocupado) return false;
      k.ocupado = true; k.parar = false; atualizarAcoes();
      let ok = true;
      try { await fn(); } catch (e) { ok = false; if (!k.parar) status(`Erro: ${e.message}`, 'erro'); }
      const parado = k.parar;
      k.ocupado = false; atualizarAcoes();
      estado(!ok && !parado ? 'erro' : parado ? 'alerta' : 'ok');
      if (parado && ok) status('Interrompido.', 'alerta');
      if (avisar) tocar(ok && !parado);
      return ok && !parado;
    }

    // ---------- microinterações ----------
    let audio = null;
    function liberarAudio() {
      try { audio = audio || new AudioContext(); if (audio.state === 'suspended') audio.resume(); } catch (_) { audio = null; }
    }

    function tocar(ok = true) {
      if (!k.som) return;
      liberarAudio();
      if (!audio) return;
      (ok ? [880, 1320] : [440, 330]).forEach((f, i) => {
        const o = audio.createOscillator(), g = audio.createGain();
        o.frequency.value = f;
        o.connect(g); g.connect(audio.destination);
        const t = audio.currentTime + i * 0.22;
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(0.3, t + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 0.2);
        o.start(t); o.stop(t + 0.21);
      });
    }

    // Brilho rápido num elemento (verde = feito, vermelho = falhou).
    function piscar(n, tipo = 'ok') {
      if (!n) return;
      n.classList.remove('pisca-ok', 'pisca-erro');
      void n.offsetWidth;
      n.classList.add(`pisca-${tipo}`);
      setTimeout(() => n.classList.remove(`pisca-${tipo}`), 800);
    }

    // O botão vira um ✓ verde por um instante.
    // (O conteúdo original fica guardado: um segundo clique antes de 1,2 s não grava o ✓ no lugar dele.)
    const confirmando = new WeakMap();
    function confirmarBotao(b) {
      if (!b) return;
      const pendente = confirmando.get(b);
      if (pendente) clearTimeout(pendente.timer);
      const antes = pendente ? pendente.antes : [...b.childNodes];
      b.classList.add('feito');
      b.replaceChildren(icone('check'), ...antes.filter((n) => n.nodeType === 3));
      const timer = setTimeout(() => { confirmando.delete(b); b.classList.remove('feito'); b.replaceChildren(...antes); }, 1200);
      confirmando.set(b, { antes, timer });
    }

    // ---------- perguntas no painel ----------
    // No lugar do confirm() e do prompt() do navegador, que travam a página e fogem do padrão:
    // uma faixa âmbar no topo do painel, com ✓ (Enter) e ✗ (Esc). Devolvem uma Promise:
    // confirmar() → true/false; perguntar() → o texto digitado ou null. Sem painel montado
    // (testes no Node, página sem painel), caem no diálogo do navegador.
    let fecharPergunta = null;
    function abrirPergunta(texto, { campo = null, sim = 'Confirmar', nao = 'Cancelar' } = {}) {
      if (fecharPergunta) fecharPergunta(campo ? null : false);
      return new Promise((resolve) => {
        if (painel.classList.contains('min')) minimizar(false);
        const caixa = k.el.pergunta;
        const fim = (v) => { fecharPergunta = null; caixa.hidden = true; caixa.replaceChildren(); fecharDica(); resolve(v); };
        fecharPergunta = fim;
        const bSim = botao('check', '', () => fim(campo ? campo.value : true), { classe: 'verde', dica: `${sim} (Enter)` });
        const bNao = botao('x-mark', '', () => fim(campo ? null : false), { classe: 'leve', dica: `${nao} (Esc)` });
        caixa.onkeydown = (e) => {
          if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); bSim.click(); } else if (e.key === 'Escape') { e.preventDefault(); bNao.click(); }
        };
        caixa.replaceChildren(...[criar('span', { className: 'txt', textContent: texto }), campo, linha([esp(), bNao, bSim], 'compacta')].filter(Boolean));
        caixa.hidden = false;
        painel.scrollTop = 0;
        estado('alerta');
        try { (campo || bSim).focus(); } catch (_) { /* sem foco */ }
      });
    }
    function confirmar(texto, opcoes) {
      if (!painel || !k.el.pergunta) return Promise.resolve(typeof confirm === 'function' ? confirm(texto) : true);
      return abrirPergunta(texto, opcoes);
    }
    function perguntar(texto, { valor = '', placeholder = '', ...opcoes } = {}) {
      if (!painel || !k.el.pergunta) return Promise.resolve(typeof prompt === 'function' ? prompt(texto, valor) : null);
      return abrirPergunta(texto, { ...opcoes, campo: criar('input', { type: 'text', value: valor, placeholder, 'aria-label': texto }) });
    }

    async function copiar(texto, b) {
      try { await navigator.clipboard.writeText(texto); } catch (_) {
        const t = criar('textarea', { value: texto });
        hospedeiro.shadowRoot.appendChild(t);
        t.select();
        document.execCommand('copy');
        t.remove();
      }
      confirmarBotao(b);
    }

    // ---------- arquivos ----------
    const celula = (v) => {
      const s = v == null ? '' : String(v);
      return /[;"\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    // CSV com ";" e BOM (abre direto no Excel pt-BR; no pandas, sep=";").
    const csv = (linhas, cols) => '﻿' + [cols.join(';'), ...linhas.map((l) => cols.map((c) => celula(l[c])).join(';'))].join('\r\n');

    // Baixa o arquivo e devolve uma Promise que resolve quando o download foi entregue ao
    // navegador (quem navega logo depois espera por ela; até 13/11/2026 o segundo CSV de um
    // par se perdia na navegação). Com GM_download (script com @grant) e op.pasta (ex.:
    // "dados-brutos/B1_entorno"), salva sem perguntar em Downloads/TCC Luderia/<pasta>/,
    // para o arquivo não cair na pasta de outra coleta; se o Tampermonkey recusar (modo de
    // download nativo, extensão fora da lista), cai no download comum.
    const pastaDoArquivo = (pasta, nome) => (pasta ? `TCC Luderia/${String(pasta).replace(/^\/+|\/+$/g, '')}/${nome}` : nome);
    function baixarComum(nome, url) {
      const a = criar('a', { href: url, download: nome });
      (document.body || document.documentElement).appendChild(a);
      a.click();
      a.remove();
    }
    function baixarArquivo(nome, conteudo, tipo = 'text/csv;charset=utf-8', opcoes = {}) {
      const pasta = opcoes.pasta ?? op.pastaDownload ?? '';
      const url = URL.createObjectURL(new Blob([conteudo], { type: tipo }));
      const soltar = () => setTimeout(() => URL.revokeObjectURL(url), 10000);
      if (typeof GM_download !== 'function' || !pasta) {
        baixarComum(nome, url);
        soltar();
        return esperarMs(600).then(() => ({ nome, via: 'navegador' }));
      }
      return new Promise((resolve) => {
        let feito = false, espera = 0;
        const fim = (via) => { if (feito) return; feito = true; clearTimeout(espera); soltar(); resolve({ nome: via === 'pasta' ? pastaDoArquivo(pasta, nome) : nome, via }); };
        const comum = () => { baixarComum(nome, url); setTimeout(() => fim('navegador'), 600); };
        try {
          GM_download({ url, name: pastaDoArquivo(pasta, nome), saveAs: false, onload: () => fim('pasta'), onerror: () => { if (!feito) comum(); }, ontimeout: () => { if (!feito) comum(); } });
          // Sem resposta do Tampermonkey em 15 s: segue (o download pode ainda sair).
          espera = setTimeout(() => fim('pasta'), 15000);
        } catch (_) { comum(); }
      });
    }
    const esperarMs = (ms) => new Promise((r) => setTimeout(r, ms));

    // ---------- menu de alvos (casas, perfis, cardápios, acervos) ----------
    // Seletor por grupo com ✓ ok, ◐ parcial, ! refazer, ○ falta; contador com barra fina;
    // botões Próximo (o que falta, primeiro no mesmo grupo), Marcar/Desfazer e Só os que faltam.
    const SIMBOLO = { ok: '✓', parcial: '◐', falha: '!', falta: '○' };
    // aoAdicionar (opcional): botão "+" que acrescenta um alvo à lista (o script pergunta os dados
    // e guarda); depois de mudar a lista, recarregar() refaz as opções do seletor.
    function menuAlvos({ itens, id = (x) => x.id, grupo = (x) => x.capital, nome = (x) => x.nome, detalhe = () => '',
      estadoDe, atual, aoEscolher, aoProximo, aoMarcar, aoAdicionar, dicaAdicionar = 'Adicionar à lista de alvos da coleta',
      unidade = 'coletados' }) {
      let lista = [];
      const select = criar('select', { 'aria-label': 'Alvo da coleta' });
      function opcoes() {
        lista = itens();
        const grupos = [...new Set(lista.map(grupo))];
        select.replaceChildren(...grupos.map((g) => criar('optgroup', { label: g },
          lista.filter((x) => grupo(x) === g).map((x) => criar('option', { value: id(x), textContent: nome(x) })))));
      }
      opcoes();
      dica(select, `✓ ok · ◐ parcial · ! refazer · ○ falta. Escolher abre o alvo e coleta.`);
      select.onchange = () => aoEscolher(lista.find((x) => id(x) === select.value));
      let soFaltam = ler(chave('soFaltam'), false);
      const bProx = botao('forward', 'Próximo', () => aoProximo(), { classe: 'mini', dica: 'Abre o próximo que falta (primeiro no mesmo grupo) e coleta sozinho' });
      // Sem aoMarcar, o menu fica sem o botão Marcar/Desfazer.
      const bMarcar = aoMarcar ? botao('check', '', () => aoMarcar(lista.find((x) => id(x) === select.value)), { classe: 'leve' }) : null;
      const bFiltro = alternaIcone({ ico: 'funnel', rotulo: 'Só os que faltam', ligado: soFaltam,
        aoMudar: (v) => { soFaltam = v; gravar(chave('soFaltam'), v); rotular(); } });
      const bAdicionar = aoAdicionar ? botao('plus', '', async () => { if (await aoAdicionar()) { opcoes(); rotular(); } },
        { classe: 'leve', dica: dicaAdicionar }) : null;
      const cont = criar('span', { className: 'pos' });
      const trilho = criar('div', { className: 'trilho fino' }, [criar('div', { className: 'preenchido' })]);
      const caixa = criar('div', { className: 'menu' }, [
        linha([select]),
        linha([criar('div', { className: 'contador' }, [cont, trilho]), bProx, bMarcar, bFiltro, bAdicionar], 'compacta'),
      ]);
      function rotular() {
        const a = atual();
        let prontos = 0;
        for (const o of select.querySelectorAll('option')) {
          const x = lista.find((y) => id(y) === o.value);
          const e = estadoDe(x);
          if (e === 'ok') prontos++;
          const t = `${SIMBOLO[e] || '○'} ${nome(x)}${detalhe(x, e) ? ` · ${detalhe(x, e)}` : ''}`;
          if (o.textContent !== t) o.textContent = t;
          o.className = e;
          o.hidden = soFaltam && e === 'ok' && id(x) !== a;
        }
        for (const g of select.querySelectorAll('optgroup')) g.hidden = [...g.querySelectorAll('option')].every((o) => o.hidden);
        if (a && select.value !== a) select.value = a;
        cont.textContent = `${prontos}/${lista.length} ${unidade}`;
        trilho.firstChild.style.width = `${Math.round((100 * prontos) / (lista.length || 1))}%`;
        const xa = lista.find((y) => id(y) === select.value);
        const col = xa && estadoDe(xa) === 'ok';
        if (!bMarcar) return;
        bMarcar.replaceChildren(icone(col ? 'arrow-uturn-left' : 'check'));
        dica(bMarcar, col ? 'Desfazer: volta a faltar' : 'Marcar como coletado, sem nova coleta');
      }
      return { caixa, select, rotular, bProx, bAdicionar, recarregar: () => { opcoes(); rotular(); } };
    }

    // ---------- painel ----------
    const CSS = `
      :host{--fundo:#fff;--texto:#18181b;--suave:#71717a;--sup:#f4f4f5;--sup2:#e4e4e7;--linha:#ececef;
        --caneta:#7e22ce;--caneta-forte:#6b21a8;--caneta-100:#f3e8ff;--azul:#2563eb;--azul-100:#dbeafe;
        --ok:#15803d;--ok-100:#dcfce7;--erro:#b91c1c;--erro-100:#fee2e2;--alerta:#b45309;--alerta-100:#fef3c7;
        --fonte:Montserrat,system-ui,-apple-system,"Segoe UI",sans-serif}
      @media (prefers-color-scheme:dark){:host{--fundo:#18181b;--texto:#f4f4f5;--suave:#a1a1aa;--sup:#27272a;--sup2:#3f3f46;
        --linha:#27272a;--caneta:#a855f7;--caneta-forte:#9333ea;--caneta-100:#3b0764;--azul:#3b82f6;--azul-100:#172554;
        --ok:#4ade80;--ok-100:#052e16;--erro:#f87171;--erro-100:#450a0a;--alerta:#fbbf24;--alerta-100:#451a03}}
      *{box-sizing:border-box}
      [hidden]{display:none!important}
      #painel{position:fixed;top:12px;right:12px;z-index:2147483647;width:var(--largura,272px);max-height:calc(100vh - 24px);
        overflow:auto;background:var(--fundo);color:var(--texto);border-radius:14px;
        box-shadow:0 8px 28px rgba(0,0,0,.2);font:13.5px/1.45 var(--fonte);padding:8px 12px 10px;
        resize:both;min-width:224px;min-height:44px;max-width:calc(100vw - 24px);transition:box-shadow .2s}
      #painel.min{height:auto!important;min-height:0;resize:none;width:auto!important;min-width:0}
      #painel.min>*:not(header){display:none}
      #painel.min header>button:not(.b-min){display:none}
      #painel.arrastando{user-select:none;opacity:.92;box-shadow:0 14px 40px rgba(0,0,0,.3)}
      header{display:flex;align-items:center;gap:2px;cursor:grab;touch-action:none;min-height:32px}
      #painel.arrastando header{cursor:grabbing}
      header .nome{flex:1;font-weight:700;font-size:14.5px;cursor:pointer;user-select:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-right:6px}
      .ponto-estado{width:8px;height:8px;border-radius:50%;background:var(--sup2);margin-right:8px;flex:none;transition:background .3s}
      .ponto-estado.rodando{background:var(--caneta);animation:pulso 1.2s ease-in-out infinite}
      .ponto-estado.ok{background:var(--ok)} .ponto-estado.alerta{background:var(--alerta)} .ponto-estado.erro{background:var(--erro)}
      @keyframes pulso{0%,100%{box-shadow:0 0 0 0 rgba(147,51,234,.55)}50%{box-shadow:0 0 0 5px rgba(147,51,234,0)}}
      svg{width:18px;height:18px;flex:none}
      button{font:inherit;color:inherit;border:0;background:var(--sup);border-radius:8px;padding:6px 10px;cursor:pointer;
        display:inline-flex;align-items:center;justify-content:center;gap:6px;white-space:nowrap;
        transition:background .15s,color .15s,transform .1s,box-shadow .2s}
      button:hover:not(:disabled){background:var(--sup2)}
      button:active:not(:disabled){transform:scale(.94)}
      button:disabled{opacity:.35;cursor:default}
      :focus-visible{outline:2px solid var(--azul);outline-offset:1px}
      .ico{width:32px;height:32px;padding:0;flex:none}
      .ico.leve{background:transparent;color:var(--suave)}
      .ico.leve:hover:not(:disabled){background:var(--sup);color:var(--texto)}
      .ico.leve[aria-pressed=true]{color:var(--caneta);background:var(--caneta-100)}
      .primario{background:var(--caneta);color:#fff;font-weight:600;flex:1}
      .primario:hover:not(:disabled){background:var(--caneta-forte)}
      .verde{background:var(--ok-100);color:var(--ok)}
      .vermelho{background:var(--erro-100);color:var(--erro)}
      .verde:hover:not(:disabled),.vermelho:hover:not(:disabled){filter:brightness(.95)}
      .verde[aria-pressed=true]{background:var(--ok);color:#fff} .vermelho[aria-pressed=true]{background:var(--erro);color:#fff}
      .parar:not(:disabled){background:var(--erro-100);color:var(--erro)}
      .perigo{color:var(--suave)} .perigo:hover:not(:disabled){color:var(--erro);background:var(--erro-100)}
      button.armado{background:var(--erro)!important;color:#fff!important;animation:tremer .3s}
      @keyframes tremer{25%{transform:translateX(-2px)}75%{transform:translateX(2px)}}
      button.feito{background:var(--ok-100)!important;color:var(--ok)!important}
      .pisca-ok{animation:piscaOk .8s} .pisca-erro{animation:piscaErro .8s}
      @keyframes piscaOk{0%{box-shadow:0 0 0 0 rgba(21,128,61,.6)}100%{box-shadow:0 0 0 8px rgba(21,128,61,0)}}
      @keyframes piscaErro{0%{box-shadow:0 0 0 0 rgba(185,28,28,.6)}100%{box-shadow:0 0 0 8px rgba(185,28,28,0)}}
      .mini{padding:4px 9px;font-size:12.5px}
      .mini svg{width:16px;height:16px}
      .linha{display:flex;align-items:center;gap:6px;margin:7px 0;flex-wrap:wrap}
      .linha.compacta{flex-wrap:nowrap;margin-top:4px}
      .linha>.primario{min-width:0}
      .esp{flex:1}
      .rotulo{font-size:12px;font-weight:600;color:var(--suave);display:inline-flex;align-items:center;gap:4px}
      .suave{color:var(--suave)}
      select,input[type=text],input[type=search],input[type=date],textarea{font:inherit;color:inherit;background:var(--sup);border:0;border-radius:8px;padding:6px 8px;min-width:0}
      select{padding:5px 4px;cursor:pointer;flex:1;width:100%}
      select option{color:#111;background:#fff}
      select option.ok{color:#9ca3af} select option.parcial{color:#2563eb} select option.falha{color:#b45309}
      input{flex:1}
      input[type=date]{color-scheme:light dark;padding:4px 6px;font-size:12.5px;flex:1 1 0}
      input::placeholder,textarea::placeholder{color:var(--suave)}
      textarea{width:100%;height:60px;font:12px/1.45 ui-monospace,Menlo,monospace;resize:vertical;display:block}
      .busca{display:flex;align-items:center;gap:6px;background:var(--sup);border-radius:8px;padding:0 4px 0 10px;flex:1}
      .busca input{background:transparent;padding:6px 0}
      .busca>svg{color:var(--suave);width:16px;height:16px}
      .contador{flex:1;min-width:0;display:flex;flex-direction:column;gap:3px}
      .barra{margin:7px 0}
      .barra[hidden]{display:none}
      .barra .txt{display:flex;justify-content:space-between;font-size:12px;color:var(--suave);font-variant-numeric:tabular-nums}
      .trilho{height:6px;background:var(--sup);border-radius:999px;overflow:hidden;display:flex;position:relative}
      .trilho.fino{height:4px}
      .preenchido{height:100%;width:0;background:var(--caneta);border-radius:999px;transition:width .35s ease}
      .contador .preenchido{background:var(--ok)}
      .preenchido.rodando{background-image:linear-gradient(90deg,transparent,rgba(255,255,255,.4),transparent);background-size:200% 100%;animation:brilho 1.4s linear infinite}
      .trilho.indef .preenchido{width:35%!important;animation:indef 1.2s ease-in-out infinite}
      @keyframes brilho{from{background-position:200% 0}to{background-position:-200% 0}}
      @keyframes indef{from{transform:translateX(-100%)}to{transform:translateX(300%)}}
      details{border-top:1px solid var(--linha)}
      details[open]{padding-bottom:6px}
      summary{list-style:none;display:flex;align-items:center;gap:6px;cursor:pointer;font-size:14px;font-weight:600;padding:7px 0;user-select:none}
      summary::-webkit-details-marker{display:none}
      summary .seta{width:15px;height:15px;color:var(--suave);transition:transform .2s}
      details[open]>summary .seta{transform:rotate(90deg)}
      summary .ico{width:28px;height:28px;background:transparent;color:var(--suave)}
      summary .ico:hover:not(:disabled){background:var(--sup);color:var(--texto)}
      .selo{font-size:11.5px;font-weight:600;background:var(--sup);color:var(--suave);border-radius:999px;padding:1px 8px;white-space:nowrap}
      .selo:empty{display:none}
      .selo.ok{background:var(--ok-100);color:var(--ok)} .selo.alerta{background:var(--alerta-100);color:var(--alerta)}
      .selo.erro{background:var(--erro-100);color:var(--erro)} .selo.roxo{background:var(--caneta-100);color:var(--caneta)}
      .pos{font-size:12px;color:var(--suave);font-variant-numeric:tabular-nums;font-weight:500;white-space:nowrap}
      .subtitulo{font-size:12px;font-weight:600;color:var(--suave);margin:10px 0 5px;display:flex;align-items:center;gap:4px}
      .tags{display:flex;flex-wrap:wrap;gap:5px;margin:6px 0}
      .tag{padding:3px 10px;border-radius:999px;font-size:12.5px;background:var(--sup);color:var(--suave);gap:4px}
      .tag svg{width:15px;height:15px}
      .tag[aria-pressed=true]{background:var(--azul);color:#fff}
      .tag[aria-pressed=true]:hover{background:var(--azul);filter:brightness(1.08)}
      .tag[aria-pressed=true] .ajuda{color:#fffc}
      .pills{display:flex;background:var(--sup);border-radius:999px;padding:3px;gap:2px;flex:1}
      .pill{flex:1;background:transparent;border-radius:999px;padding:3px 6px;font-size:12.5px;color:var(--suave);gap:4px}
      .pill:hover:not(:disabled){background:var(--sup2)}
      .pill[aria-selected=true]{background:var(--fundo);color:var(--caneta);font-weight:600;box-shadow:0 1px 2px rgba(0,0,0,.08)}
      .ajuda{display:inline-flex;color:var(--suave);cursor:help;border-radius:999px}
      .ajuda svg{width:15px;height:15px}
      .ajuda:hover{color:var(--caneta)}
      .dica{position:fixed;z-index:2147483647;max-width:280px;background:var(--texto);color:var(--fundo);
        font:12.5px/1.5 var(--fonte);padding:7px 10px;border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,.25);pointer-events:none;
        white-space:pre-line;animation:entra .12s ease-out}
      .dica[hidden]{display:none}
      .status{font-size:13px;border-radius:10px;padding:7px 10px;background:var(--sup);white-space:pre-line;margin:7px 0;transition:background .25s}
      .status:empty{display:none}
      .status.entra{animation:entra .25s ease-out}
      @keyframes entra{from{opacity:0;transform:translateY(-3px)}to{opacity:1;transform:none}}
      .status.rico{white-space:normal}
      .status .cab{font-weight:600;display:flex;gap:8px;align-items:center}
      .status ul{margin:4px 0 0;padding-left:18px}
      .status li::marker{color:var(--suave)}
      .ponto{width:8px;height:8px;border-radius:50%;background:var(--suave);flex:none}
      .st-ok{background:var(--ok-100)} .st-ok .ponto{background:var(--ok)}
      .st-alerta{background:var(--alerta-100)} .st-alerta .ponto{background:var(--alerta)}
      .st-erro{background:var(--erro-100)} .st-erro .ponto{background:var(--erro)}
      .aviso{color:var(--alerta);font-size:12.5px;margin:5px 0 0;font-weight:500}
      .aviso::before{content:"⚠ "}
      .st-alerta .aviso,.st-erro .aviso{color:inherit}
      .pergunta{font-size:13px;background:var(--alerta-100);border-radius:10px;padding:7px 10px;margin:7px 0;animation:entra .2s ease-out}
      .pergunta .txt{display:block;white-space:pre-line;font-weight:500}
      .pergunta input{width:100%;margin-top:6px;background:var(--fundo)}
      .pergunta .linha{margin:6px 0 0}
      .info{font-size:12.5px;background:var(--sup);border-radius:10px;padding:7px 10px;margin:7px 0;white-space:pre-line}
      .info:empty{display:none}
      .mono{font:11.5px/1.4 ui-monospace,Menlo,monospace;color:var(--suave);word-break:break-all}
      .chip{font-size:11.5px;font-weight:600;border-radius:999px;padding:1px 8px;white-space:nowrap;background:var(--sup);color:var(--suave)}
      .chip.ok{background:var(--ok-100);color:var(--ok)} .chip.alerta{background:var(--alerta-100);color:var(--alerta)}
      .chip.erro{background:var(--erro-100);color:var(--erro)} .chip.azul{background:var(--azul-100);color:var(--azul)}
      .lista{max-height:280px;overflow:auto;display:flex;flex-direction:column;gap:1px;margin-top:4px}
      .vazio{font-size:12.5px;color:var(--suave);margin:6px 0}
      table{width:100%;border-collapse:collapse;font-size:12px;margin-top:4px;font-variant-numeric:tabular-nums}
      td,th{padding:3px 4px;border-bottom:1px solid var(--linha);text-align:left}
      th{color:var(--suave);font-weight:600} td.n,th.n{text-align:right}
      tr.total td{font-weight:700;border-bottom:0}
      @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}`;

    function carregarFonte() {
      if (document.getElementById('tcc-fonte-montserrat') || !document.head) return;
      document.head.appendChild(criar('link', { id: 'tcc-fonte-montserrat', rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap' }));
    }

    // Painéis 20% mais estreitos desde 13/11/2026: a largura pedida pelo script vale ×ESCALA, e a
    // largura já salva pelo autor é reduzida uma vez (marca `escala`).
    const ESCALA = 0.8;
    // Posição e tamanho escolhidos pelo autor; sem posição salva, vale posicaoPadrao().
    let posicao = ler(chave('posicao'), null);
    if (posicao?.width && posicao.escala !== ESCALA) {
      const px = parseFloat(posicao.width);
      posicao = { ...posicao, width: Number.isFinite(px) ? `${Math.round(px * ESCALA)}px` : posicao.width, escala: ESCALA };
      gravar(chave('posicao'), posicao);
    }
    let arrastou = false;

    function posicionar() {
      if (!painel) return;
      const p = painel;
      if (posicao?.width && !p.style.width && !p.classList.contains('min')) { p.style.width = posicao.width; p.style.height = posicao.height || ''; }
      if (posicao && posicao.left != null) {
        const w = p.offsetWidth || 272;
        const left = Math.min(Math.max(0, posicao.left), Math.max(0, innerWidth - w));
        const top = Math.min(Math.max(0, posicao.top), Math.max(0, innerHeight - 44));
        if (p.style.left !== `${left}px` || p.style.top !== `${top}px`) {
          Object.assign(p.style, { left: `${left}px`, right: 'auto', top: `${top}px`, maxHeight: `calc(100vh - ${top + 12}px)` });
        }
        return;
      }
      const pad = op.posicaoPadrao?.() || {};
      const top = pad.top ?? 12, right = pad.right ?? 12;
      if (p.style.top !== `${top}px` || p.style.right !== `${right}px` || p.style.left) {
        Object.assign(p.style, { left: '', right: `${right}px`, top: `${top}px`, maxHeight: `calc(100vh - ${top + 12}px)` });
      }
    }

    function prepararArraste(cab) {
      cab.addEventListener('pointerdown', (e) => {
        if (e.button !== 0 || e.composedPath().some((n) => n.tagName === 'BUTTON')) return;
        const r = painel.getBoundingClientRect();
        const x0 = e.clientX, y0 = e.clientY;
        let moveu = false;
        const mover = (ev) => {
          if (!moveu && Math.hypot(ev.clientX - x0, ev.clientY - y0) < 4) return;
          moveu = true;
          painel.classList.add('arrastando');
          fecharDica();
          posicao = { ...posicao, left: Math.round(r.left + ev.clientX - x0), top: Math.round(r.top + ev.clientY - y0) };
          posicionar();
        };
        const soltar = () => {
          removeEventListener('pointermove', mover);
          removeEventListener('pointerup', soltar);
          painel.classList.remove('arrastando');
          if (!moveu) return;
          gravar(chave('posicao'), posicao);
          arrastou = true;
          setTimeout(() => { arrastou = false; }, 0);
        };
        addEventListener('pointermove', mover);
        addEventListener('pointerup', soltar);
      });
      cab.addEventListener('dblclick', (e) => {
        if (e.composedPath().some((n) => n.tagName === 'BUTTON')) return;
        posicao = null;
        gravar(chave('posicao'), null);
        painel.style.width = painel.style.height = painel.style.left = '';
        posicionar();
        status('Painel de volta ao canto.');
      });
    }

    function minimizar(v = !painel.classList.contains('min')) {
      painel.classList.toggle('min', v);
      k.el.bMin.replaceChildren(icone(v ? 'plus' : 'minus'));
      dica(k.el.bMin, v ? 'Expandir' : 'Minimizar');
      if (v) { painel.style.width = ''; painel.style.height = ''; } else posicionar();
      gravar(chave('min'), v);
      fecharDica();
    }

    // montar({ nome, filhos, extras (botões do cabeçalho), aposAuto (botões logo depois do download automático), largura, autobaixar, minimizado, css })
    function montar({ nome, filhos, extras = [], aposAuto = [], largura = 340, autobaixar = false, minimizado, css = '' }) {
      carregarFonte();
      k.el.ponto = criar('span', { className: 'ponto-estado' });
      k.el.nome = criar('span', { className: 'nome', textContent: nome });
      k.el.bMin = botao('minus', '', () => minimizar(), { classe: 'leve b-min', dica: 'Minimizar' });
      const bSom = alternaIcone({ ico: 'bell', icoDesligado: 'bell-slash', rotulo: 'Som ao concluir', ligado: k.som,
        aoMudar: (v) => { k.som = v; gravar(chave('som'), v); if (v) tocar(true); } });
      const bAuto = autobaixar ? alternaIcone({ ico: 'arrow-down-tray', rotulo: 'Download automático', ligado: k.autobaixar,
        aoMudar: (v) => { k.autobaixar = v; gravar(chave('autobaixar'), v); } }) : null;
      const cab = criar('header', {}, [k.el.ponto, k.el.nome, ...extras, bSom, bAuto, ...aposAuto, k.el.bMin]);
      dica(k.el.nome, 'Clique para minimizar · arraste para mover · duplo clique volta ao canto');
      k.el.pergunta = criar('div', { className: 'pergunta', hidden: true, role: 'alertdialog' });
      painel = criar('div', { id: 'painel', style: `--largura:${Math.round(largura * ESCALA)}px` }, [cab, k.el.pergunta, ...filhos]);
      k.el.painel = painel;
      k.el.nome.onclick = () => { if (!arrastou) minimizar(); };
      prepararArraste(cab);

      // O tamanho só muda pela alça de redimensionar, que grava largura e altura no estilo.
      addEventListener('pointerup', () => {
        if (!painel || painel.classList.contains('min')) return;
        const { width, height } = painel.style;
        if (width && (width !== posicao?.width || height !== posicao?.height)) {
          posicao = { ...posicao, width, height, escala: ESCALA };
          gravar(chave('posicao'), posicao);
        }
      });
      painel.addEventListener('click', liberarAudio);
      painel.addEventListener('scroll', fecharDica);
      // As teclas digitadas no painel não chegam aos atalhos do site.
      for (const tipo of ['keydown', 'keyup', 'keypress']) painel.addEventListener(tipo, (e) => {
        if (tipo === 'keydown' && e.key === 'Escape') fecharDica();
        e.stopPropagation();
      });
      // Dicas: abre com atraso curto sobre botões e na hora sobre o ⓘ.
      painel.addEventListener('pointerover', (e) => {
        const n = comDica(e);
        if (!n || dicaFixa || n === dicaAncora) return;
        clearTimeout(timerDica);
        timerDica = setTimeout(() => abrirDica(n), n.classList.contains('ajuda') ? 0 : 350);
      });
      painel.addEventListener('pointerout', (e) => {
        const n = comDica(e);
        if (!n || dicaFixa || (e.relatedTarget && n.contains(e.relatedTarget))) return;
        clearTimeout(timerDica);
        timerDica = setTimeout(fecharDica, 80);
      });
      painel.addEventListener('focusin', (e) => { const n = comDica(e); if (n && n.matches(':focus-visible')) abrirDica(n); });
      painel.addEventListener('focusout', () => { if (!dicaFixa) fecharDica(); });
      // Captura: tocar no ⓘ dentro de um botão não aciona o botão.
      painel.addEventListener('click', (e) => {
        const i = e.composedPath().find((n) => n.classList?.contains('ajuda'));
        if (!i) return;
        e.stopPropagation(); e.preventDefault();
        if (dicaAncora === i && dicaFixa) fecharDica(); else abrirDica(i, true);
      }, true);
      addEventListener('keydown', (e) => { if (e.key === 'Escape') fecharDica(); });
      addEventListener('scroll', () => { if (!dicaFixa) fecharDica(); }, true);
      addEventListener('click', (e) => { if (dicaAncora && !e.composedPath().includes(dicaAncora)) fecharDica(); });

      k.el.dica = criar('div', { className: 'dica', hidden: true, role: 'tooltip' });
      hospedeiro = criar('div', { id: `${op.id || P}-hospedeiro` });
      const raiz = hospedeiro.attachShadow({ mode: 'open' });
      raiz.append(criar('style', { textContent: CSS + css }), painel, k.el.dica);
      if (minimizado ?? ler(chave('min'), false)) minimizar(true);
      atualizarAcoes();
      garantir();
      return painel;
    }

    // O React e outros sites podem refazer o <body>: o painel fica preso ao <html> e volta se sumir.
    function garantir() {
      if (!hospedeiro || !document.documentElement) return;
      if (!hospedeiro.isConnected) document.documentElement.appendChild(hospedeiro);
      posicionar();
    }

    Object.assign(k, {
      criar, icone, dica, ajuda, botao, botaoPerigo, botaoParar, etiqueta, alternaIcone, botaoBaixarCada, pills, secao, naoAlterna,
      linha, esp, rotulo, selo, status, resumo, barra, progresso, estado, atualizarAcoes, executar, tocar, piscar,
      confirmarBotao, confirmar, perguntar, copiar, celula, csv, baixarArquivo, pastaDoArquivo, menuAlvos, montar, garantir, minimizar,
      nome: (t) => { if (k.el.nome && k.el.nome.textContent !== t) k.el.nome.textContent = t; },
      hospedeiro: () => hospedeiro,
    });
    return k;
  }
  // <<< kit_painel

  const kit = kitPainel({ id: 'tcc-busca', prefixo: 'tcc-busca', ler, gravar, pastaDownload: PASTA_DOWNLOAD, abertos: ['resultados'] });
  const { criar, icone } = kit;
  const el = {};

  // Só o que o kit não traz: a grade do quadro-resumo e a lista dos resultados.
  const CSS_PAINEL = `
    .caixa{background:var(--sup);border-radius:10px;padding:7px 10px;margin:7px 0}
    .grade{display:grid;grid-template-columns:auto 1fr auto 1fr;gap:2px 8px;font-size:12.5px;align-items:center}
    .grade .k{color:var(--suave)} .grade .v{font-variant-numeric:tabular-nums;font-weight:500}
    .selo{display:inline-flex;align-items:center;gap:3px} .selo svg{width:14px;height:14px}
    .item{display:flex;gap:6px;align-items:center;font-size:12.5px;padding:2px 4px;border-radius:6px}
    .item:hover{background:var(--sup)}
    .item .pos{min-width:2em;text-align:right}
    .item .nome-item{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}`;

  function status(t, tipo = '') { kit.status(t, tipo); }
  const idAtual = () => alvoDaUrl(location.href)?.id || ler(CHAVE_ITEM, ALVOS[0].id);
  const filaAtiva = () => !!ler(CHAVE_FILA, null)?.ativa;

  function mostrarResultados(reg) {
    el.resultadosSelo.textContent = reg ? String(reg.n) : '';
    el.resultados.replaceChildren(...(reg?.itens.length ? reg.itens.slice(0, 150).map((x) => criar('div', {
      className: 'item', dica: `${x.categoria_maps || 'sem categoria'} · ${x.endereco || 'sem endereço'}${x.situacao_maps ? ` · ${x.situacao_maps}` : ''}`,
    }, [
      criar('span', { className: 'pos', textContent: String(x.posicao) }),
      criar('span', { className: 'nome-item', textContent: x.nome }),
      x.n_avaliacoes !== '' ? criar('span', { className: `chip${+x.n_avaliacoes > 100 ? ' ok' : ''}`, textContent: Number(x.n_avaliacoes).toLocaleString('pt-BR') }) : null,
    ])) : [criar('p', { className: 'vazio', textContent: reg ? 'Sem resultado.' : 'Nenhuma busca lida aqui.' })]));
  }

  function atualizar() {
    if (!el.menu) return;
    const dados = lerDados();
    const buscas = naOrdem(dados);
    el.menu.rotular();
    const n = { ok: 0, parcial: 0, falha: 0, falta: 0 };
    const marcas = lerMarcas();
    for (const a of ALVOS) n[estadoBusca(dados[a.id], marcas[a.id])]++;
    const casa = (classe, t) => criar('span', { className: classe, textContent: t });
    el.grade.replaceChildren(
      casa('k', 'Buscas'), casa('v', `${n.ok}/${ALVOS.length}`),
      casa('k', 'A refazer'), casa(`v${n.parcial + n.falha ? ' alerta' : ''}`, String(n.parcial + n.falha)),
      casa('k', 'Resultados'), casa('v', linhasCandidatos(buscas).length.toLocaleString('pt-BR')),
      casa('k', 'Lugares'), casa('v', unicos(buscas).toLocaleString('pt-BR')),
    );
    kit.dica(el.grade, 'Buscas lidas até o fim; a refazer (lista incompleta ou falha); resultados somados; lugares sem repetição (por place_id)');
    const exportado = ler(CHAVE_EXPORTACAO, 0);
    const pend = pendentes(dados, exportado);
    el.pendentes.className = pend >= AVISO_PENDENTES ? 'selo alerta' : pend ? 'selo' : exportado ? 'selo ok' : 'selo';
    el.pendentes.replaceChildren(...[pend >= AVISO_PENDENTES ? icone('exclamation-triangle') : !pend && exportado ? icone('check') : null,
      pend ? `${pend} fora do CSV` : exportado ? 'em dia' : ''].filter(Boolean));
    kit.dica(el.pendentes, exportado ? `Último CSV: ${new Date(exportado).toLocaleString('pt-BR')}` : 'Nenhum CSV baixado ainda');
    const fila = ler(CHAVE_FILA, null);
    if (!kit.ocupado) {
      kit.atualizarAcoes(!!fila?.ativa);
      if (!fila?.ativa && kit.el.ponto.classList.contains('rodando')) kit.estado('');
    }
    if (fila?.ativa) kit.progresso('fila', fila.pos / fila.ids.length, `Fila: ${fila.pos} de ${fila.ids.length} buscas`); else kit.progresso('fila', null);
    mostrarResultados(dados[el.menu.select.value] || dados[idAtual()]);
  }

  function abrirBusca(a) {
    gravar(CHAVE_ITEM, a.id);
    gravar(CHAVE_ABRIR, { id: a.id, em: Date.now() });
    status(`Abrindo "${a.consulta}"…`);
    location.href = urlBusca(a);
  }

  // Lê a busca aberta como sendo a do alvo e guarda. Devolve o registro (ou null se não gravou).
  async function coletar(alvo) {
    kit.progresso('lista', true, `Lendo "${alvo.consulta}"`);
    let r;
    try { r = await lerBusca((n) => kit.progresso('lista', true, `${n} resultados carregados`)); } finally { kit.progresso('lista', null); }
    const reg = registrar(alvo, r);
    gravar(CHAVE_ITEM, alvo.id);
    atualizar();
    if (!reg) return null;
    const tipo = estadoBusca(reg) === 'ok' ? 'ok' : estadoBusca(reg) === 'parcial' ? 'alerta' : 'erro';
    kit.resumo({
      titulo: reg.estado === 'lista' ? `${reg.n} resultados` : SITUACAO[reg.estado],
      sub: alvo.consulta, tipo,
      linhas: reg.n ? [[reg.itens.filter((x) => +x.n_avaliacoes > 100).length, 'com mais de 100 avaliações']] : [],
      avisos: [reg.estado === 'lista' && !reg.fim ? 'A lista não chegou ao fim: refazer.' : '',
        reg.estado === 'bloqueado' ? 'Resolva o desafio do Google na página e colete de novo.' : ''],
    });
    return reg;
  }

  // Busca aberta pelo menu: coleta sozinha quando a página carrega.
  async function coletarAoAbrir() {
    const pedido = ler(CHAVE_ABRIR, null);
    if (!pedido) return;
    gravar(CHAVE_ABRIR, null);
    const alvo = ALVOS.find((a) => a.id === pedido.id);
    if (!alvo || Date.now() - pedido.em > 2 * 60 * 1000) return;
    kit.minimizar(false);
    await kit.executar(async () => { const reg = await coletar(alvo); if (reg && estadoBusca(reg) === 'falha') throw new Error(SITUACAO[reg.estado]); });
    atualizar();
  }

  // ---------- fila ----------

  function iniciarFila() {
    const dados = lerDados(), marcas = lerMarcas();
    const ids = ALVOS.filter((a) => estadoBusca(dados[a.id], marcas[a.id]) !== 'ok').map((a) => a.id);
    if (!ids.length) { status('Todas as buscas já foram lidas.', 'ok'); return; }
    gravar(CHAVE_FILA, { ativa: true, parar: false, ids, pos: 0, abriu: '' });
    continuarFila();
  }

  function encerrarFila(fila, msg, tipo) {
    fila.ativa = false;
    gravar(CHAVE_FILA, fila);
    atualizar();
    status(msg, tipo);
    kit.tocar(tipo === 'ok');
  }

  async function continuarFila() {
    const fila = ler(CHAVE_FILA, null);
    if (!fila?.ativa) return;
    const alvo = ALVOS.find((a) => a.id === fila.ids[fila.pos]);
    if (!alvo) { encerrarFila(fila, 'Fila concluída.', 'ok'); return; }
    // A página da busca da vez ainda não foi aberta por esta fila: abre e continua ao carregar.
    if (fila.abriu !== alvo.id) {
      fila.abriu = alvo.id;
      gravar(CHAVE_FILA, fila);
      gravar(CHAVE_ITEM, alvo.id);
      location.href = urlBusca(alvo);
      return;
    }
    kit.minimizar(false);
    let reg = null;
    await kit.executar(async () => { reg = await coletar(alvo); }, { avisar: false });
    if (kit.baixarCada && reg && reg.n) await baixarCsv(reg);
    const f = ler(CHAVE_FILA, fila);
    if (reg?.estado === 'bloqueado') { encerrarFila(f, 'Bloqueio do Google: resolva o desafio na página e clique em "Todas" para retomar.', 'alerta'); return; }
    f.pos += 1;
    if (f.pos >= f.ids.length || f.parar) {
      const parou = f.parar && f.pos < f.ids.length;
      if (kit.autobaixar) await baixarCsv();
      encerrarFila(f, `${parou ? 'Fila interrompida' : 'Fila concluída'}: ${f.pos} de ${f.ids.length} buscas.${kit.autobaixar ? ' CSV baixado.' : ''}`, parou ? 'alerta' : 'ok');
      return;
    }
    gravar(CHAVE_FILA, f);
    atualizar();
    const pausa = sortear(PAUSA_ENTRE_BUSCAS);
    kit.atualizarAcoes(true);
    status(`${f.pos}/${f.ids.length} · próxima busca em ${Math.round(pausa / 1000)} s.`);
    await esperar(pausa);
    const g = ler(CHAVE_FILA, f);
    if (g.parar || !g.ativa) { encerrarFila(g, `Fila interrompida: ${g.pos} de ${g.ids.length} buscas.`, 'alerta'); return; }
    continuarFila();
  }

  function parar() {
    const f = ler(CHAVE_FILA, null);
    if (f?.ativa) { f.parar = true; gravar(CHAVE_FILA, f); }
    kit.parar = true;
    status(f?.ativa ? 'Parando: a fila não segue para a próxima busca.' : 'Parando…', 'alerta');
  }

  // Reiniciar (lixeira): baixa antes os CSVs de tudo e apaga os resultados guardados e o
  // histórico de coleta (marcas, fila, pedido de abertura e data do último CSV).
  const CHAVES_COLETA = [CHAVE_DADOS, CHAVE_MARCAS, CHAVE_FILA, CHAVE_ABRIR, CHAVE_EXPORTACAO, CHAVE_ITEM];
  async function reiniciar() {
    const n = Object.keys(lerDados()).length;
    if (n) await baixarCsv();
    for (const c of CHAVES_COLETA) gravar(c, null);
    kit.estado('');
    atualizar();
    status(n ? `Reiniciado: ${n} buscas apagadas (CSVs baixados antes) e histórico zerado.` : 'Reiniciado: histórico de coleta zerado.', 'ok');
  }

  function montarPainel() {
    const { botao, linha, esp, secao, selo } = kit;
    // O registro é lido uma vez por rotulagem, não uma por opção (420 buscas).
    let cache = null;
    const registro = () => { if (!cache) { cache = { dados: lerDados(), marcas: lerMarcas() }; setTimeout(() => { cache = null; }, 0); } return cache; };
    const estadoDe = (a) => estadoBusca(registro().dados[a.id], registro().marcas[a.id]);
    el.menu = kit.menuAlvos({
      itens: () => ALVOS, unidade: 'buscas', estadoDe, atual: idAtual,
      detalhe: (a, e) => { const r = registro().dados[a.id]; return !r ? '' : e === 'falha' ? 'falhou' : e === 'parcial' ? `${r.n}, incompleta` : String(r.n); },
      aoEscolher: async (a) => {
        if (!a) return;
        if (filaAtiva() || kit.ocupado) { atualizar(); status('Espere a coleta em curso terminar (ou pare).', 'alerta'); return; }
        if (estadoDe(a) === 'ok' && !(await kit.confirmar(`"${a.consulta}" já foi lida. Refazer?`))) { gravar(CHAVE_ITEM, a.id); atualizar(); return; }
        abrirBusca(a);
      },
      aoProximo: () => {
        if (filaAtiva() || kit.ocupado) { status('Espere a coleta em curso terminar (ou pare).', 'alerta'); return; }
        const a = proximaQueFalta(idAtual());
        if (!a) { status('Todas as buscas já foram lidas.', 'ok'); return; }
        abrirBusca(a);
      },
      aoMarcar: (a) => {
        if (!a) return;
        const col = estadoDe(a) === 'ok';
        gravar(CHAVE_MARCAS, { ...lerMarcas(), [a.id]: !col });
        gravar(CHAVE_ITEM, a.id);
        status(col ? `"${a.consulta}" volta a faltar.` : `"${a.consulta}" marcada como lida.`);
        atualizar();
      },
    });
    kit.dica(el.menu.select, 'Buscas "<termo> em <cidade>", por cidade: escolher uma abre no Maps e lê a lista. ✓ lida até o fim (com o nº de resultados), ◐ lista incompleta, ! falhou, ○ falta');
    const bColetar = botao('magnifying-glass', 'Coletar', () => {
      const a = alvoDaUrl(location.href);
      if (!a) { abrirBusca(ALVOS.find((x) => x.id === el.menu.select.value) || ALVOS[0]); return; }
      kit.executar(async () => { const reg = await coletar(a); if (reg && estadoBusca(reg) === 'falha') throw new Error(SITUACAO[reg.estado]); }).then(atualizar);
    }, { classe: 'primario', dica: 'Coletar esta busca: rola a lista aberta até o fim e guarda os resultados (substitui a leitura anterior da mesma busca); sem busca da lista aberta, abre a escolhida no menu' });
    const bTodas = botao('play', '', iniciarFila, { dica: 'Coletar todas: abre cada busca que falta, uma após a outra, com pausa de 4 a 8 s; no fim, toca um som e baixa os CSVs. Rode numa janela própria' });
    kit.dica(kit.botaoParar(parar), 'Parar: a leitura em curso termina e a fila não segue para a próxima busca');
    const bCsv = botao('arrow-down-tray', 'CSV', async () => {
      const n = await baixarCsv();
      kit.confirmarBotao(bCsv);
      atualizar();
      status(`CSVs baixados (${n} buscas).`, 'ok');
    }, { classe: 'mini', dica: `Baixar CSV: os candidatos (uma linha por busca × resultado) e as buscas (uma linha por busca), em ${PASTA_DOWNLOAD}/` });
    const bLimpar = kit.botaoPerigo('trash', '', reiniciar, { classe: 'leve',
      dica: 'Reiniciar: apaga os resultados guardados e o histórico de coleta (marcas e fila). Baixa antes os CSVs de tudo. As preferências ficam' });
    el.grade = criar('div', { className: 'grade' });
    el.pendentes = selo('');
    el.resultados = criar('div', { className: 'lista' });
    el.resultadosSelo = selo('');
    kit.el.status = criar('div', { className: 'status' });
    kit.acoes = [bColetar, bTodas, bCsv, bLimpar, el.menu.bProx];
    kit.montar({
      nome: 'Busca', largura: 340, autobaixar: true, css: CSS_PAINEL,
      extras: [kit.botaoBaixarCada('Baixar cada busca ao terminar (fila): além dos CSVs do fim')],
      filhos: [
        el.menu.caixa,
        linha([bColetar, bTodas, kit.el.parar]),
        kit.barra('fila'), kit.barra('lista'),
        kit.el.status,
        linha([bCsv, el.pendentes, esp(), bLimpar]),
        criar('div', { className: 'caixa' }, [el.grade]),
        secao('resultados', ['Resultados', kit.ajuda('Resultados da busca escolhida, na ordem da lista do Maps, com o nº de avaliações (verde acima de 100, o recorte do B1).'), el.resultadosSelo], [el.resultados]),
      ],
    });
    el.menu.select.addEventListener('change', () => mostrarResultados(lerDados()[el.menu.select.value]));
  }

  let urlVista = '';
  function verificar() {
    if (!kit.hospedeiro()) { montarPainel(); atualizar(); }
    kit.garantir();
    if (location.href !== urlVista) { urlVista = location.href; atualizar(); }
  }

  // Aviso ao fechar a aba com muitas buscas fora de CSV; a fila troca de página sozinha e não dispara.
  if (typeof window !== 'undefined' && window.addEventListener) {
    window.addEventListener('beforeunload', (e) => {
      if (filaAtiva() || ler(CHAVE_ABRIR, null) || pendentes(lerDados(), ler(CHAVE_EXPORTACAO, 0)) < AVISO_PENDENTES) return;
      e.preventDefault();
      e.returnValue = '';
    });
  }

  console.info('[Busca no Maps] carregado');
  verificar();
  setInterval(() => { try { verificar(); } catch (e) { console.error(NOME, e); } }, 1500);
  if (filaAtiva()) continuarFila().catch((e) => status(`Erro na fila: ${e.message}`, 'erro'));
  else coletarAoAbrir().catch((e) => status(`Erro na coleta: ${e.message}`, 'erro'));
})();
