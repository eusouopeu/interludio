// ==UserScript==
// @name         Ficha do lugar no Google Maps (TCC Luderia)
// @namespace    tcc-luderia
// @version      2026.11.16-1
// @description  Lê a ficha de cada casa do B1 no Google Maps (nota, nº de avaliações, categoria, situação, endereço, coordenada, site, telefone e horário de funcionamento por dia) e exporta CSV para dados-brutos/B1_estabelecimentos/ficha_maps/.
// @match        https://www.google.com/maps/*
// @match        https://www.google.com.br/maps/*
// @run-at       document-idle
// @noframes
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_deleteValue
// @grant        GM_download
// @downloadURL  https://raw.githubusercontent.com/eusouopeu/interludio/main/_src/webScripts/_instalaveis/maps_ficha.user.js
// @updateURL    https://raw.githubusercontent.com/eusouopeu/interludio/main/_src/webScripts/_instalaveis/maps_ficha.user.js
// ==/UserScript==
// Gerado por gerar_instalaveis.py a partir de B1_estabelecimentos/maps_ficha.user.js; não editar aqui.

// ---------- lista_maps_ficha.js ----------
// lista_maps_ficha.js: itens do menu do maps_ficha.user.js (Ficha do lugar no Maps).
// O carregador do Tampermonkey lê este arquivo (@require) antes do script; editar aqui
// muda o menu no próximo recarregar da página, sem reinstalar.

// População: as 63 casas do B1 (dados-agregados/B1_estabelecimentos/B1_horarios.csv), com as
// coordenadas de dados-agregados/B1_entorno/B1_entorno_maps_fila.csv. A mesma lista do
// lista_maps_horarios_pico.js; outros lugares (ex.: os candidatos do maps_busca) entram pela
// fila do painel.
// [place_id, nome, capital, lat, lng]
var LISTA_MAPS_FICHA = [
  ["ChIJRcWOaPabpgARDvX2Bad0qb0", "Bardo Mago", "Belo Horizonte", -19.905169, -43.915835],
  ["ChIJpzB8zc2XpgARoJTUu90J6Pw", "Comdado Bar e Jogos", "Belo Horizonte", -19.927646, -43.954388],
  ["ChIJsUAT-dObpgARCT2C5QpnVKU", "Garagem do Nerd", "Belo Horizonte", -19.917242, -43.901223],
  ["ChIJ-17ZQDG9pgARc-AxpXmaNRU", "La Tabuleria", "Belo Horizonte", -19.976597, -43.977367],
  ["ChIJx5jr3zGXpgARQGx9eX7TDmY", "LudoCafé", "Belo Horizonte", -19.944717, -43.946234],
  ["ChIJ6ZLMZw-XpgAR_OR6SwY5xKo", "Shelf Bar e Jogos", "Belo Horizonte", -19.937803, -43.944948],
  ["ChIJ-97tiEeNpJIRb_eV7a-sxBs", "Ludoteca Sidequest", "Belém", -1.44916, -48.486457],
  ["ChIJyXjE650xWpMRJL-J6QbGkt4", "FORTALÚDICA - BURGERS & JOGOS", "Brasília", -15.833121, -47.983815],
  ["ChIJ172cu2U7WpMR-GxnGmUHCkc", "Gruta BSB", "Brasília", -15.76649, -47.877086],
  ["ChIJdUv4La46WpMRnBvNknmOqWo", "Inside Games", "Brasília", -15.82264, -47.919744],
  ["ChIJzdFNP3AyWpMRH2P6HEuhE-I", "Loja de Jogos - Asgard", "Brasília", -15.84384, -48.029229],
  ["ChIJ15nLgwAwWpMRY1whwD29ZSo", "Ludoteca BGC", "Brasília", -15.819414, -47.899706],
  ["ChIJN8BZeb85WpMRgVKT05caxB4", "Utopia Games & Food", "Brasília", -15.737604, -47.895234],
  ["ChIJGXginrXGyJQR0LFEVIzp4hI", "Metropoly Bar", "Campinas", -22.821702, -47.076784],
  ["ChIJz-2zsLTHyJQRyn6ZZtDZgBI", "Muito Geek | TCG • Board Games • Fliperama", "Campinas", -22.883997, -47.070259],
  ["ChIJ5ehtIcbFyJQRf7QBB6TJ6XE", "Nergeek", "Campinas", -22.88954, -47.033546],
  ["ChIJ3ekLtDjl3JQRHwtNgmINgLo", "Alçapão Jogos", "Curitiba", -25.418006, -49.265488],
  ["ChIJY_lqHVLl3JQRvDHacOMDKuc", "BoardZ Game Pub", "Curitiba", -25.452186, -49.268753],
  ["ChIJOczn8z7l3JQRNBEL_ZJ3iQo", "Joyjoy Café", "Curitiba", -25.437043, -49.241465],
  ["ChIJK5Dhtunj3JQRniPWHB3haDU", "Paladino Hobbies", "Curitiba", -25.434156, -49.302922],
  ["ChIJc66HomXk3JQRNl28jz_VsPc", "Taverna Game House", "Curitiba", -25.441605, -49.270879],
  ["ChIJ1wjBJD7k3JQRQi7trfp_0aQ", "Vila Celta Hobby Store - Jogos e Café", "Curitiba", -25.44302, -49.266283],
  ["ChIJawIVeV0JM0oR5BtnD_poQeA", "CCG Floripa", "Florianópolis", -27.58156, -48.526293],
  ["ChIJc3F7ka83J5URQZ1XTl-_iak", "Chef on Play", "Florianópolis", -27.587931, -48.523133],
  ["ChIJJz8-gcY3J5URYdZrEXdHaAk", "Cineplay- Restaurante e Jogos", "Florianópolis", -27.611552, -48.627225],
  ["ChIJ0yXbI35IxwcR0_jLi-uINUU", "Balboa's Hobby Games", "Fortaleza", -3.734689, -38.500261],
  ["ChIJQURqeMZJxwcR95O-XLbS2mk", "Dominaria Cards & Games", "Fortaleza", -3.738413, -38.53968],
  ["ChIJ89uEICDxXpMRdaEvN0XiWK0", "Paladins Game Store", "Goiânia", -16.712706, -49.264019],
  ["ChIJHSDPTgF5GZURKmSqKITyoGM", "Arcadea Gaming Pub", "Porto Alegre", -30.021524, -51.206899],
  ["ChIJ41pgHNFDGZURC7yTegyn7nU", "Toca do Rato - Pizzaria e Jogos de Tabuleiro", "Porto Alegre", -29.61081, -51.166349],
  ["ChIJRUjwU66WoGgRzc9yJU7jkwM", "Nala Land - Bar de Jogos de Tabuleiro em Recife", "Recife", -8.023976, -34.895067],
  ["ChIJPx_QtT17mQAR9cO9ARQW00g", "Cheio de Fome - Vila da Penha", "Rio de Janeiro", -22.840402, -43.308167],
  ["ChIJu1yUroF_mQAR7qxqAfxKSw4", "Game Of Boards", "Rio de Janeiro", -22.954819, -43.180991],
  ["ChIJ90Gs_9rVmwAReA7MnIyPLTE", "Luderia Carioca", "Rio de Janeiro", -22.9232, -43.177488],
  ["ChIJYzHxUhR-mQARpqVtYD9th0c", "Magic Store Brazil", "Rio de Janeiro", -22.916493, -43.241072],
  ["ChIJ1SAzAGF_mQARQgP-yrPBxbQ", "RED jogos", "Rio de Janeiro", -22.909066, -43.177219],
  ["ChIJxXhMZN5_mQARj2JCqcWfTD8", "Reduto", "Rio de Janeiro", -22.953503, -43.196112],
  ["ChIJOcVssmeDmQARZZrnWu2mnwA", "TabuClub", "Rio de Janeiro", -22.898584, -43.10234],
  ["ChIJoTlvBfMbFgcRHvuCKHBQrXQ", "São Jogue - Bela Vista", "Salvador", -12.969436, -38.473681],
  ["ChIJfWR3S3ZazpQR6aC6xpbPMwU", "60 Minutos Escape, Hamburgueria e Boardgames", "São Paulo", -23.624451, -46.669091],
  ["ChIJYTHwWgBbzpQRFenbJdM5cxU", "Arena BG | Jogos de Tabuleiro | Hamburgueria", "São Paulo", -23.599307, -46.601688],
  ["ChIJKeHwNv5ZzpQRlmzx9rCTWdM", "Bodogami Restaurante e Cafeteria", "São Paulo", -23.556847, -46.6366],
  ["ChIJ__9TTnxCzpQRwVSzrOijkRY", "Bravo Jogos", "São Paulo", -23.662974, -46.525198],
  ["ChIJRU7FUX1CzpQRj3E7xMzGPvA", "CHQ Jogos", "São Paulo", -23.668268, -46.538039],
  ["ChIJrT_EWwBZzpQRGAZzptZbtsY", "Cartola Luderia Bar", "São Paulo", -23.563561, -46.638521],
  ["ChIJbZRHQPRfzpQRz97-ZOg0yXA", "Castelos Bar & Boardgames", "São Paulo", -23.542591, -46.562184],
  ["ChIJF9j3OCRbzpQRkk74_QtOk_0", "Coletivo Geek", "São Paulo", -23.614642, -46.666278],
  ["ChIJ7_DDAlH1zpQRJVJ0UHnItH8", "Covil Game Bar", "São Paulo", -23.465036, -46.523386],
  ["ChIJSU_eTQBDzpQRv_GdRUp0f-g", "Covil Game Bar SBC", "São Paulo", -23.687824, -46.56191],
  ["ChIJiZJ_DnIDz5QRaVafFCXGkUE", "Dungeon Games Store", "São Paulo", -23.509005, -46.873919],
  ["ChIJZz29dnVXzpQRvRh7_YKyUN4", "Encounter | Jogos de Tabuleiro | Board Games", "São Paulo", -23.606458, -46.673858],
  ["ChIJBUzaCedbzpQRkSqbwW7yAvQ", "Espaço 162 - Meu Karaokê Box", "São Paulo", -23.585295, -46.611131],
  ["ChIJ_aN4OAxXzpQR0UH63sAeVCA", "Fan Hour Games and Burgers", "São Paulo", -23.561704, -46.680473],
  ["ChIJa3UsDhRczpQRPPSuDl6acO8", "Flow Games - Burgers, Cards & Comunidade", "São Paulo", -23.581556, -46.58485],
  ["ChIJn7uU0RNbzpQRI4GI9KHOo_s", "Jogasampa", "São Paulo", -23.612477, -46.663246],
  ["ChIJTaG5ALpZzpQRUDErQ-RkfTs", "Ludus Luderia", "São Paulo", -23.561838, -46.64621],
  ["ChIJE43rt29ZzpQRnvADt6pXfto", "OMNIVERSE", "São Paulo", -23.613038, -46.676947],
  ["ChIJo-6lZMlezpQRmgUpUPfmRIs", "Pitta's Board Games", "São Paulo", -23.547275, -46.592412],
  ["ChIJkWsGmd1czpQRGLydxc29vbw", "Place Games", "São Paulo", -23.621405, -46.561556],
  ["ChIJNcHw7jNYzpQRKRHPOrb4jEw", "Play Easy", "São Paulo", -23.551913, -46.656812],
  ["ChIJsU5BAwBRzpQRAgLVvqg68os", "Tubaleria", "São Paulo", -23.632058, -46.709815],
  ["ChIJi5zbZadgzpQRIYeuK_eqQio", "XPlace", "São Paulo", -23.532507, -46.515814],
  ["ChIJfyav9YI9uAARjwbBqcRm2_k", "Café Geek Cafeteria e Ludoteca", "Vitória", -20.344746, -40.310846],
];

// ---------- maps_ficha.user.js ----------
/*
 * Bloco B1, etapa 2: ficha dos estabelecimentos (caps. 5 e 7: nota, volume de avaliações,
 * categoria, localização e horário de funcionamento).
 * Coleta: B1_estabelecimentos/ (brutos em dados-brutos/B1_estabelecimentos/ficha_maps/).
 *
 * Para que serve: a coleta original (B1c_details.py e B1c_localizacoes.py) usa a Places
 * API, que é paga e pede chave. Este script lê os mesmos campos na página do lugar, sem
 * chave, para a ficha ser replicável por qualquer pessoa.
 *
 * Limites a declarar: o Maps mostra o horário desta semana; em semana com feriado, o dia
 * do feriado pode trazer horário especial (coluna semana_com_feriado = sim: conferir ou
 * recoletar em outra semana). A nota e o nº de avaliações são os da data da coleta.
 *
 * Fluxo:
 *  1. Abra o Google Maps. O menu traz as 63 casas do B1 por capital, com ✓ lida (com as
 *     horas por semana), ! falhou e ○ falta.
 *  2. Escolher uma casa abre a página dela e lê a ficha. "Todas" faz o mesmo com as que
 *     faltam, com pausa de 4 a 8 s. "Coletar" lê o lugar aberto.
 *  3. Outros lugares (ex.: os candidatos do maps_busca) entram pela seção Fila: um link do
 *     Maps, "place_id;nome" ou nome + cidade por linha.
 *  4. "CSV" baixa uma linha por lugar, com o horário no formato de B1_horarios.csv
 *     ("18:00-00:00"; dois turnos, "11:00-15:00 | 18:00-23:00"; vazio = fechado).
 *
 * Leitura (conferida no Maps em 14/11/2026):
 *  - nome: h1.DUwDvf; nota e avaliações: div.F7nice ("4,8 (831)"); categoria:
 *    button[jsaction*="category"];
 *  - endereço, site, telefone e Plus Code: [data-item-id] = "address", "authority",
 *    "phone:tel:…" e "oloc" (aria-label "Endereço: …"; o site, no href);
 *  - horário: table.eK4R0e, uma linha por dia; a 2ª célula (td.mxowUb) traz no aria-label
 *    "14:00 a 00:00", "Fechado" ou "Aberto 24 horas", e ", Os horários podem ser
 *    diferentes" em dia de feriado;
 *  - coordenada e id do Maps: no fim da URL (!3d<lat>!4d<lng>, !1s0x…:0x…). O place_id
 *    não vem na URL do lugar: vale o do menu (ou o da linha da fila).
 */

(function () {
  'use strict';

  const NOME = '[Ficha no Maps]';
  const CHAVE_DADOS = 'tcc-ficha-dados';     // { chave do lugar: registro }
  const CHAVE_FILA = 'tcc-ficha-fila';       // { ativa, parar, itens: [{ pid, nome, url }], pos, abriu }
  const CHAVE_ABRIR = 'tcc-ficha-abrir';     // { pid, em }
  const CHAVE_ITEM = 'tcc-ficha-item';
  const CHAVE_MARCAS = 'tcc-ficha-marcas';
  const CHAVE_EXPORTACAO = 'tcc-ficha-exportado-em';
  const PASTA_DOWNLOAD = 'dados-brutos/B1_estabelecimentos/ficha_maps';
  const LIMITE_M = 300;
  const PAUSA_ENTRE_LUGARES = [4000, 8000];
  const AVISO_PENDENTES = 25;
  // Colunas dos dias, na ordem de B1_horarios.csv.
  const DIAS = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'];
  const DIAS_RE = [/segunda|monday/, /terca|tuesday/, /quarta|wednesday/, /quinta|thursday/, /sexta|friday/, /sabado|saturday/, /domingo|sunday/];

  // A lista vem de lista_maps_ficha.js, lida pelo carregador (@require) antes deste arquivo.
  if (typeof LISTA_MAPS_FICHA === 'undefined') {
    const msg = `${NOME} lista_maps_ficha.js não foi carregada: reinstale o carregador (python3 _src/outros/G5_outros/gerar_carregadores.py --abrir).`;
    console.error(msg);
    if (typeof alert === 'function') alert(msg);
    return;
  }
  const POP = LISTA_MAPS_FICHA.map(([id, nome, capital, lat, lng]) => ({ id, nome, capital, lat, lng }));

  // ---------- utilidades ----------

  const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
  const sortear = ([a, b]) => a + Math.random() * (b - a);
  const semAcento = (t) => String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const doisDig = (n) => String(n).padStart(2, '0');
  const dataLocal = (d = new Date()) => `${d.getFullYear()}-${doisDig(d.getMonth() + 1)}-${doisDig(d.getDate())}`;
  const horaLocal = (d = new Date()) => `${doisDig(d.getHours())}${doisDig(d.getMinutes())}`;

  function ler(chave, padrao) {
    try { const v = GM_getValue(chave, padrao); return v ?? padrao; } catch (_) { return padrao; }
  }
  function gravar(chave, valor) {
    try { if (valor == null) GM_deleteValue(chave); else GM_setValue(chave, valor); return true; } catch (e) { status(`Não consegui gravar no Tampermonkey: ${e.message}`, 'erro'); return false; }
  }

  function distancia(lat1, lng1, lat2, lng2) {
    const r = Math.PI / 180;
    const a = Math.sin((lat2 - lat1) * r / 2) ** 2 + Math.cos(lat1 * r) * Math.cos(lat2 * r) * Math.sin((lng2 - lng1) * r / 2) ** 2;
    return 2 * 6371000 * Math.asin(Math.sqrt(a));
  }

  // ---------- horário de funcionamento ----------

  const hhmm = (min) => `${doisDig(Math.floor(min / 60))}:${doisDig(min % 60)}`;

  // "14:00 a 00:00", "11:00–15:00, 18:00–23:00", "Fechado", "Aberto 24 horas" → turnos em minutos
  // [[abre, fecha]]; o turno que passa da meia-noite fecha depois de 24:00 (conta no dia em que abre).
  function lerTurnos(texto) {
    const t = semAcento(texto);
    if (/24 horas|24 hours/.test(t)) return [[0, 1440]];
    const turnos = [];
    for (const m of t.matchAll(/(\d{1,2}):(\d{2})\s*(?:a|as|ate|to|–|—|-)\s*(\d{1,2}):(\d{2})/g)) {
      const abre = +m[1] * 60 + +m[2];
      let fecha = +m[3] * 60 + +m[4];
      if (fecha <= abre) fecha += 1440;
      turnos.push([abre, fecha]);
    }
    return turnos;
  }

  // linhas: [[dia, horário]] como na tabela do Maps ("domingo(Proclamação da República)",
  // "13:00 a 22:00, Os horários podem ser diferentes"). Devolve as colunas dos dias no
  // formato de B1_horarios.csv e os totais da semana.
  function lerHorarios(linhas) {
    const out = Object.fromEntries(DIAS.map((d) => [d, '']));
    const turnosDia = {};
    let lidos = 0, feriado = false;
    for (const [dia, horas] of linhas) {
      const i = DIAS_RE.findIndex((re) => re.test(semAcento(dia)));
      if (i < 0) continue;
      lidos++;
      if (/\(/.test(dia) || /podem ser diferentes|might differ|may differ/.test(semAcento(horas))) feriado = true;
      turnosDia[DIAS[i]] = lerTurnos(horas);
      out[DIAS[i]] = turnosDia[DIAS[i]].map(([a, f]) => `${hhmm(a)}-${hhmm(f >= 1440 && a === 0 && f === 1440 ? 1440 : f % 1440)}`).join(' | ');
    }
    const todos = Object.values(turnosDia).flat();
    const base = { ...out, semana_com_feriado: feriado ? 'sim' : lidos ? 'não' : '' };
    if (lidos < 7) return { ...base, dias_abertos: '', horas_semana: '', abre_cedo: '', fecha_tarde: '', situacao: lidos ? `horário incompleto (${lidos} de 7 dias)` : 'sem horário' };
    if (!todos.length) return { ...base, dias_abertos: 0, horas_semana: 0, abre_cedo: '', fecha_tarde: '', situacao: 'fechado a semana toda' };
    const total = todos.reduce((s, [a, f]) => s + f - a, 0);
    return {
      ...base,
      dias_abertos: DIAS.filter((d) => turnosDia[d].length).length,
      horas_semana: Math.round(total / 6) / 10,
      abre_cedo: hhmm(Math.min(...todos.map(([a]) => a))),
      fecha_tarde: hhmm(Math.max(...todos.map(([, f]) => f))),
      situacao: total === 7 * 1440 ? '24 horas' : 'ok',
    };
  }

  // ---------- leitura da página do lugar ----------

  function situacaoMaps(texto) {
    const t = semAcento(texto);
    if (/permanentemente fechado|fechado permanentemente|permanently closed/.test(t)) return 'fechado permanentemente';
    if (/temporariamente fechado|fechado temporariamente|temporarily closed/.test(t)) return 'fechado temporariamente';
    return 'em funcionamento';
  }

  // Coordenada e id do Maps: quem abre um lugar a partir de outro leva os dois na URL; o aberto é o último.
  function lerUrl(url) {
    const u = String(url || '');
    const ultimo = (re) => [...u.matchAll(re)].pop();
    const coord = ultimo(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/g) || [];
    let nome = '';
    try { nome = decodeURIComponent(((u.match(/\/maps\/place\/([^/@?]+)/) || [])[1] || '').replace(/\+/g, ' ')); } catch (_) { /* URL malformada */ }
    return { id_maps: (ultimo(/!1s(0x[0-9a-f]+:0x[0-9a-f]+)/gi) || [])[1] || '', lat: coord[1] ? +coord[1] : '', lng: coord[2] ? +coord[2] : '', nome_url: nome };
  }

  const rotulo = (sel, re) => (document.querySelector(sel)?.getAttribute('aria-label') || '').replace(re, '').trim();

  function lerFicha() {
    const resumo = (document.querySelector('div.F7nice')?.innerText || '').replace(/\n/g, ' ');
    const linhas = [...document.querySelectorAll('table.eK4R0e tr')].map((tr) => {
      const [dia, horas] = tr.children;
      return [dia?.innerText || '', horas?.getAttribute('aria-label') || horas?.innerText || ''];
    });
    const main = document.querySelector('div[role="main"]');
    return {
      nome: document.querySelector('h1.DUwDvf, div[role="main"] h1')?.innerText.trim() || '',
      categoria_maps: document.querySelector('button[jsaction*="category"]')?.innerText.trim() || '',
      nota_media: ((resumo.match(/(\d[.,]\d)/) || [])[1] || '').replace(',', '.'),
      n_avaliacoes: ((resumo.match(/\(([\d.\s]+)\)/) || [])[1] || '').replace(/\D/g, '') || (/nenhuma avaliacao|no reviews/.test(semAcento(main?.innerText.slice(0, 600) || '')) ? '0' : ''),
      situacao_maps: situacaoMaps(main?.innerText.slice(0, 1500) || ''),
      endereco: rotulo('button[data-item-id="address"]', /^(endereço|address):\s*/i),
      site: document.querySelector('a[data-item-id="authority"]')?.href || '',
      telefone: rotulo('button[data-item-id^="phone:tel:"]', /^(telefone|phone):\s*/i),
      plus_code: rotulo('button[data-item-id="oloc"]', /^plus code:\s*/i),
      ...lerUrl(location.href),
      ...lerHorarios(linhas),
      url: location.href.split('?')[0],
    };
  }

  // O Maps troca o painel e a URL em momentos diferentes: só lê quando o título do painel e
  // o nome no fim da URL batem e a URL já traz o código do lugar.
  const chaveNome = (t) => semAcento(t).replace(/[^a-z0-9]/g, '');
  function incoerencia() {
    const titulo = chaveNome(document.querySelector('h1.DUwDvf, div[role="main"] h1')?.innerText || '');
    const u = lerUrl(location.href);
    if (!titulo) return 'nenhum lugar aberto';
    if (!u.id_maps || !u.nome_url) return 'a URL ainda não traz o lugar aberto';
    const k = chaveNome(u.nome_url);
    return k === titulo || (k.length >= 4 && (titulo.startsWith(k) || k.startsWith(titulo))) ? '' : `URL em "${u.nome_url}" e painel em outro lugar`;
  }

  async function esperarLugar(ms = 15000) {
    let motivo = 'nenhum lugar aberto';
    for (let t = 0; t < ms && motivo; t += 500) { motivo = incoerencia(); if (motivo) await esperar(500); }
    return motivo;
  }

  // A tabela do horário costuma vir no HTML mesmo recolhida; se não vier, abre a linha do horário.
  async function garantirHorario() {
    for (let i = 0; i < 4; i++) {
      if (document.querySelectorAll('table.eK4R0e tr').length >= 7) return;
      await esperar(500);
    }
    const linha = document.querySelector('[data-item-id="oh"], div[jsaction*="openhours"], [aria-label*="horário de funcionamento" i]');
    if (linha) { try { linha.click(); } catch (_) { /* sem clique */ } await esperar(900); }
  }

  // ---------- registro e estado ----------

  const lerDados = () => ler(CHAVE_DADOS, {}) || {};
  const lerMarcas = () => ler(CHAVE_MARCAS, {}) || {};
  const urlCasa = (p) => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(p.nome)}&query_place_id=${p.id}&hl=pt-BR`;

  // Casa da lista a que o lugar aberto corresponde: a escolhida, se estiver a até 300 m.
  function casaDoLugar(ficha, pid, pop = POP) {
    if (ficha.lat === '' || ficha.lng === '') return null;
    const perto = (p) => distancia(ficha.lat, ficha.lng, p.lat, p.lng) <= LIMITE_M;
    const escolhida = pop.find((p) => p.id === pid);
    if (escolhida && perto(escolhida)) return escolhida;
    return pop.filter(perto).sort((a, b) => distancia(ficha.lat, ficha.lng, a.lat, a.lng) - distancia(ficha.lat, ficha.lng, b.lat, b.lng))[0] || null;
  }

  // ok (ficha lida, com ou sem horário publicado), falha ou falta. A marca à mão prevalece.
  function estadoCasa(reg, marca) {
    if (marca === true) return 'ok';
    if (marca === false) return 'falta';
    if (!reg) return 'falta';
    return reg.falha ? 'falha' : 'ok';
  }

  function proximaQueFalta(pidAtual, dados = lerDados(), marcas = lerMarcas(), pop = POP) {
    const i0 = pop.findIndex((p) => p.id === pidAtual);
    const atual = pop[i0] || pop[0];
    const ordem = [...pop.slice(i0 + 1), ...pop.slice(0, Math.max(i0, 0))]
      .filter((p) => p.id !== pidAtual && estadoCasa(dados[p.id], marcas[p.id]) !== 'ok');
    return ordem.find((p) => p.capital === atual.capital) || ordem[0] || null;
  }

  // Lê o lugar aberto e guarda. item: { pid, nome } da lista ou da fila (pid opcional).
  async function coletarEste(item = {}) {
    const motivo = await esperarLugar();
    const agora = new Date();
    const base = { data_coleta: dataLocal(agora), coletado_ms: agora.getTime() };
    const dados = lerDados();
    if (motivo) {
      if (item.pid) { dados[item.pid] = { ...base, place_id: item.pid, nome: item.nome || '', capital: POP.find((p) => p.id === item.pid)?.capital || '', falha: motivo, situacao: `não lida: ${motivo}`, url: location.href.split('?')[0] }; gravar(CHAVE_DADOS, dados); }
      return { ok: false, msg: `Não li a ficha: ${motivo}.` };
    }
    await garantirHorario();
    const ficha = lerFicha();
    const casa = casaDoLugar(ficha, item.pid);
    const daLista = POP.find((p) => p.id === item.pid);
    // Pedida uma casa da lista e aberto outro lugar (a mais de 300 m): não grava por cima.
    if (daLista && casa?.id !== daLista.id) {
      dados[daLista.id] = { ...base, place_id: daLista.id, nome: daLista.nome, capital: daLista.capital, falha: 'lugar diferente', situacao: `não lida: abriu "${ficha.nome}", fora dos ${LIMITE_M} m da casa`, url: ficha.url };
      gravar(CHAVE_DADOS, dados);
      return { ok: false, msg: `Abriu "${ficha.nome}", que não é ${daLista.nome} (mais de ${LIMITE_M} m).` };
    }
    const pid = casa?.id || item.pid || '';
    const chave = pid || ficha.id_maps;
    dados[chave] = { ...base, ...ficha, place_id: pid, capital: casa?.capital || '' };
    if (!gravar(CHAVE_DADOS, dados)) return { ok: false, msg: 'Não consegui gravar a ficha.' };
    return { ok: true, casa, reg: dados[chave], msg: `${ficha.nome}: ${ficha.situacao === 'ok' ? `${String(ficha.horas_semana).replace('.', ',')} h por semana, ${ficha.dias_abertos} dias` : ficha.situacao}.` };
  }

  // ---------- exportação ----------

  const COLS = ['place_id', 'id_maps', 'nome', 'capital', 'categoria_maps', 'nota_media', 'n_avaliacoes', 'situacao_maps', 'endereco', 'lat', 'lng',
    'site', 'telefone', 'plus_code', ...DIAS, 'dias_abertos', 'horas_semana', 'abre_cedo', 'fecha_tarde', 'semana_com_feriado', 'situacao', 'url', 'data_coleta'];

  // As casas da lista na ordem dela; depois, os lugares da fila.
  function linhasCsv(dados, pop = POP) {
    const daLista = pop.map((p) => dados[p.id]).filter(Boolean);
    const ids = new Set(pop.map((p) => p.id));
    return [...daLista, ...Object.entries(dados).filter(([k]) => !ids.has(k)).map(([, r]) => r)];
  }
  const nomeArquivo = (d = new Date(), sufixo = '') => `${dataLocal(d)}_${horaLocal(d)}_maps_ficha${sufixo ? `_${sufixo}` : ''}.csv`;
  const nomeCurto = (s) => semAcento(s).replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '').slice(0, 50) || 'lugar';

  async function baixarCsv(registro = null) {
    const linhas = registro ? [registro] : linhasCsv(lerDados());
    await kit.baixarArquivo(nomeArquivo(new Date(), registro ? nomeCurto(registro.nome) : ''), kit.csv(linhas, COLS));
    if (!registro) gravar(CHAVE_EXPORTACAO, Date.now());
    return linhas.length;
  }

  const pendentes = (dados, exportadoEm) => Object.values(dados).filter((r) => (r.coletado_ms || 0) > exportadoEm).length;

  // Linha da fila: link do Maps, "place_id;nome" ou nome + cidade.
  function itemDaLinha(linha) {
    const t = String(linha || '').trim();
    if (!t || t.startsWith('#')) return null;
    if (/^https?:\/\//.test(t)) return { pid: '', nome: '', url: t };
    const m = t.match(/^(ChIJ[\w-]+)\s*[;,\t]\s*(.+)$/);
    if (m) return { pid: m[1], nome: m[2].trim(), url: urlCasa({ id: m[1], nome: m[2].trim() }) };
    return { pid: '', nome: t, url: `https://www.google.com/maps/search/${encodeURIComponent(t)}?hl=pt-BR` };
  }

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

  const kit = kitPainel({ id: 'tcc-ficha', prefixo: 'tcc-ficha', ler, gravar, pastaDownload: PASTA_DOWNLOAD, abertos: ['ficha'] });
  const { criar, icone } = kit;
  const el = {};

  const CSS_PAINEL = `
    .caixa{background:var(--sup);border-radius:10px;padding:7px 10px;margin:7px 0}
    .grade{display:grid;grid-template-columns:auto 1fr;gap:2px 8px;font-size:12.5px;align-items:baseline}
    .grade .k{color:var(--suave)} .grade .v{font-variant-numeric:tabular-nums;font-weight:500;min-width:0;overflow-wrap:anywhere}
    .selo{display:inline-flex;align-items:center;gap:3px} .selo svg,.aberto svg{width:14px;height:14px}
    .aberto{font-size:12.5px;display:flex;align-items:center;gap:4px;margin:7px 0;color:var(--suave)}
    .ok{color:var(--ok)} .alerta{color:var(--alerta)}
    textarea{white-space:pre;overflow:auto}`;

  function status(t, tipo = '') { kit.status(t, tipo); }
  const pidAtual = () => ler(CHAVE_ITEM, POP[0].id);
  const filaAtiva = () => !!ler(CHAVE_FILA, null)?.ativa;
  const ROTULO_DIA = { segunda: 'Seg', terca: 'Ter', quarta: 'Qua', quinta: 'Qui', sexta: 'Sex', sabado: 'Sáb', domingo: 'Dom' };

  function mostrarFicha(r) {
    const casa = (k, v) => [criar('span', { className: 'k', textContent: k }), criar('span', { className: 'v', textContent: v === '' || v == null ? '–' : String(v) })];
    if (!r) { el.ficha.replaceChildren(criar('p', { className: 'vazio', textContent: 'Ficha ainda não lida.' })); return; }
    if (r.falha) { el.ficha.replaceChildren(criar('p', { className: 'aviso', textContent: r.situacao })); return; }
    el.ficha.replaceChildren(criar('div', { className: 'grade' }, [
      ...casa('Nota', r.nota_media ? `${String(r.nota_media).replace('.', ',')} · ${Number(r.n_avaliacoes || 0).toLocaleString('pt-BR')} avaliações` : ''),
      ...casa('Categoria', r.categoria_maps), ...casa('Situação', r.situacao_maps), ...casa('Endereço', r.endereco),
      ...casa('Site', r.site), ...casa('Telefone', r.telefone),
      ...DIAS.flatMap((d) => casa(ROTULO_DIA[d], r[d] || (r.situacao === 'sem horário' ? '' : 'fechado'))),
      ...casa('Semana', r.situacao === 'ok' ? `${String(r.horas_semana).replace('.', ',')} h em ${r.dias_abertos} dias${r.semana_com_feriado === 'sim' ? ' (com feriado)' : ''}` : r.situacao),
      ...casa('Lida em', (r.data_coleta || '').split('-').reverse().join('/')),
    ]));
  }

  function atualizar() {
    if (!el.menu) return;
    const dados = lerDados();
    el.menu.rotular();
    const exportado = ler(CHAVE_EXPORTACAO, 0);
    const pend = pendentes(dados, exportado);
    el.pendentes.className = pend >= AVISO_PENDENTES ? 'selo alerta' : pend ? 'selo' : exportado ? 'selo ok' : 'selo';
    el.pendentes.replaceChildren(...[pend >= AVISO_PENDENTES ? icone('exclamation-triangle') : !pend && exportado ? icone('check') : null,
      pend ? `${pend} fora do CSV` : exportado ? 'em dia' : ''].filter(Boolean));
    kit.dica(el.pendentes, exportado ? `Último CSV: ${new Date(exportado).toLocaleString('pt-BR')}` : 'Nenhum CSV baixado ainda');
    const fora = Object.keys(dados).filter((k) => !POP.some((p) => p.id === k)).length;
    el.foraSelo.textContent = fora ? `+${fora}` : '';
    kit.dica(el.foraSelo, fora ? `${fora} lugar(es) da fila, fora da lista das casas do B1: entram no CSV depois delas` : '');
    const fila = ler(CHAVE_FILA, null);
    if (!kit.ocupado) {
      kit.atualizarAcoes(!!fila?.ativa);
      if (!fila?.ativa && kit.el.ponto.classList.contains('rodando')) kit.estado('');
    }
    if (fila?.ativa) kit.progresso('fila', fila.pos / fila.itens.length, `Fila: ${fila.pos} de ${fila.itens.length} lugares`); else kit.progresso('fila', null);
    mostrarFicha(dados[el.menu.select.value]);
    mostrarAberto();
  }

  // Lugar aberto × casa escolhida, pelas coordenadas da URL.
  function mostrarAberto() {
    if (!el.aberto) return;
    const u = lerUrl(location.href);
    const nome = document.querySelector('h1.DUwDvf')?.innerText.trim() || '';
    if (!nome || incoerencia()) { el.aberto.className = 'aberto'; el.aberto.replaceChildren('Nenhum lugar aberto.'); return; }
    const casa = casaDoLugar(u, pidAtual());
    const confere = casa && casa.id === pidAtual();
    el.aberto.className = confere ? 'aberto ok' : 'aberto alerta';
    el.aberto.replaceChildren(icone(confere ? 'check' : 'exclamation-triangle'), confere ? nome : casa ? `${nome} (é ${casa.nome})` : `${nome} (fora da lista)`);
  }

  function abrirCasa(p) {
    gravar(CHAVE_ITEM, p.id);
    gravar(CHAVE_ABRIR, { pid: p.id, em: Date.now() });
    status(`Abrindo ${p.nome}…`);
    location.href = urlCasa(p);
  }

  async function coletarAoAbrir() {
    const pedido = ler(CHAVE_ABRIR, null);
    if (!pedido) return;
    gravar(CHAVE_ABRIR, null);
    const casa = POP.find((p) => p.id === pedido.pid);
    if (!casa || Date.now() - pedido.em > 2 * 60 * 1000) return;
    kit.minimizar(false);
    await kit.executar(async () => {
      status(`Lendo ${casa.nome}…`);
      const r = await coletarEste({ pid: casa.id, nome: casa.nome });
      atualizar();
      if (!r.ok) throw new Error(r.msg);
      status(r.msg, 'ok');
    });
    atualizar();
  }

  // ---------- fila ----------

  function iniciarFila(itens) {
    if (!itens.length) { status('Nada na fila.', 'alerta'); return; }
    gravar(CHAVE_FILA, { ativa: true, parar: false, itens, pos: 0, abriu: -1 });
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
    const item = fila.itens[fila.pos];
    if (!item) { encerrarFila(fila, 'Fila concluída.', 'ok'); return; }
    if (fila.abriu !== fila.pos) {
      fila.abriu = fila.pos;
      gravar(CHAVE_FILA, fila);
      if (item.pid && POP.some((p) => p.id === item.pid)) gravar(CHAVE_ITEM, item.pid);
      location.href = item.url;
      return;
    }
    kit.minimizar(false);
    let r = { ok: false, msg: '' };
    await kit.executar(async () => { status(`Lendo ${item.nome || 'o lugar'}…`); r = await coletarEste(item); }, { avisar: false });
    if (kit.baixarCada && r.ok) await baixarCsv(r.reg);
    const f = ler(CHAVE_FILA, fila);
    f.pos += 1;
    f.falhas = (f.falhas || 0) + (r.ok ? 0 : 1);
    if (f.pos >= f.itens.length || f.parar) {
      const parou = f.parar && f.pos < f.itens.length;
      if (kit.autobaixar) await baixarCsv();
      encerrarFila(f, `${parou ? 'Fila interrompida' : 'Fila concluída'}: ${f.pos} de ${f.itens.length} lugares${f.falhas ? `, ${f.falhas} sem leitura` : ''}.${kit.autobaixar ? ' CSV baixado.' : ''}`, parou || f.falhas ? 'alerta' : 'ok');
      return;
    }
    gravar(CHAVE_FILA, f);
    atualizar();
    const pausa = sortear(PAUSA_ENTRE_LUGARES);
    kit.atualizarAcoes(true);
    status(`${f.pos}/${f.itens.length} · ${r.msg} Próximo em ${Math.round(pausa / 1000)} s.`, r.ok ? '' : 'alerta');
    await esperar(pausa);
    const g = ler(CHAVE_FILA, f);
    if (g.parar || !g.ativa) { encerrarFila(g, `Fila interrompida: ${g.pos} de ${g.itens.length} lugares.`, 'alerta'); return; }
    continuarFila();
  }

  function parar() {
    const f = ler(CHAVE_FILA, null);
    if (f?.ativa) { f.parar = true; gravar(CHAVE_FILA, f); }
    kit.parar = true;
    status(f?.ativa ? 'Parando: a fila não segue para o próximo lugar.' : 'Parando…', 'alerta');
  }

  // Reiniciar (lixeira): baixa antes o CSV de tudo e apaga as fichas e o histórico de coleta.
  const CHAVES_COLETA = [CHAVE_DADOS, CHAVE_MARCAS, CHAVE_FILA, CHAVE_ABRIR, CHAVE_EXPORTACAO, CHAVE_ITEM];
  async function reiniciar() {
    const n = Object.keys(lerDados()).length;
    if (n) await baixarCsv();
    for (const c of CHAVES_COLETA) gravar(c, null);
    kit.estado('');
    atualizar();
    status(n ? `Reiniciado: ${n} fichas apagadas (CSV baixado antes) e histórico zerado.` : 'Reiniciado: histórico de coleta zerado.', 'ok');
  }

  function montarPainel() {
    const { botao, linha, esp, secao, selo } = kit;
    let cache = null;
    const registro = () => { if (!cache) { cache = { dados: lerDados(), marcas: lerMarcas() }; setTimeout(() => { cache = null; }, 0); } return cache; };
    const estadoDe = (p) => estadoCasa(registro().dados[p.id], registro().marcas[p.id]);
    const ocupadoAgora = () => filaAtiva() || kit.ocupado;
    el.menu = kit.menuAlvos({
      itens: () => POP, unidade: 'casas', estadoDe, atual: pidAtual,
      detalhe: (p, e) => { const r = registro().dados[p.id]; return !r ? '' : e === 'falha' ? 'falhou' : r.situacao === 'ok' ? `${String(r.horas_semana).replace('.', ',')} h` : r.situacao || ''; },
      aoEscolher: async (p) => {
        if (!p) return;
        if (ocupadoAgora()) { atualizar(); status('Espere a coleta em curso terminar (ou pare).', 'alerta'); return; }
        if (casaDoLugar(lerUrl(location.href), p.id)?.id === p.id && !incoerencia()) { gravar(CHAVE_ITEM, p.id); atualizar(); return; }
        if (estadoDe(p) === 'ok' && !(await kit.confirmar(`${p.nome} já foi lida. Refazer?`))) { gravar(CHAVE_ITEM, p.id); atualizar(); return; }
        abrirCasa(p);
      },
      aoProximo: () => {
        if (ocupadoAgora()) { status('Espere a coleta em curso terminar (ou pare).', 'alerta'); return; }
        const p = proximaQueFalta(pidAtual());
        if (!p) { status('Todas as casas do B1 estão lidas.', 'ok'); return; }
        abrirCasa(p);
      },
      aoMarcar: (p) => {
        if (!p) return;
        const col = estadoDe(p) === 'ok';
        gravar(CHAVE_MARCAS, { ...lerMarcas(), [p.id]: !col });
        gravar(CHAVE_ITEM, p.id);
        status(col ? `${p.nome} volta a faltar.` : `${p.nome} marcada como lida.`);
        atualizar();
      },
    });
    kit.dica(el.menu.select, 'Casas do B1, por capital: escolher uma abre no Maps e lê a ficha. ✓ lida (com as horas por semana), ! falhou, ○ falta');
    const bColetar = botao('document-text', 'Coletar', () => kit.executar(async () => {
      status('Lendo…');
      const escolhida = POP.find((p) => p.id === el.menu.select.value);
      const r = await coletarEste(casaDoLugar(lerUrl(location.href), escolhida?.id) ? { pid: casaDoLugar(lerUrl(location.href), escolhida?.id).id } : {});
      if (r.casa) gravar(CHAVE_ITEM, r.casa.id);
      atualizar();
      if (!r.ok) throw new Error(r.msg);
      if (!r.casa) mostrarFicha(r.reg);
      status(r.msg, 'ok');
    }).then(atualizar), { classe: 'primario', dica: 'Coletar este lugar: lê a ficha do lugar aberto e guarda (substitui a leitura anterior do mesmo lugar)' });
    const bAbrir = botao('map-pin', '', () => abrirCasa(POP.find((p) => p.id === el.menu.select.value) || POP[0]), { dica: 'Abrir: abre no Maps a casa escolhida e lê a ficha quando carregar' });
    const bTodas = botao('play', '', () => {
      const dados = lerDados(), marcas = lerMarcas();
      const faltam = POP.filter((p) => estadoCasa(dados[p.id], marcas[p.id]) !== 'ok');
      if (!faltam.length) { status('Todas as casas do B1 estão lidas.', 'ok'); return; }
      iniciarFila(faltam.map((p) => ({ pid: p.id, nome: p.nome, url: urlCasa(p) })));
    }, { dica: 'Coletar todas: abre cada casa que falta, uma após a outra, com pausa de 4 a 8 s; no fim, toca um som e baixa o CSV. Rode numa janela própria' });
    kit.dica(kit.botaoParar(parar), 'Parar: a leitura em curso termina e a fila não segue para o próximo lugar');
    const bCsv = botao('arrow-down-tray', 'CSV', async () => {
      const n = await baixarCsv();
      kit.confirmarBotao(bCsv);
      atualizar();
      status(`CSV baixado (${n} lugares).`, 'ok');
    }, { classe: 'mini', dica: `Baixar CSV: uma linha por lugar, com tudo o que está guardado, em ${PASTA_DOWNLOAD}/` });
    const bLimpar = kit.botaoPerigo('trash', '', reiniciar, { classe: 'leve',
      dica: 'Reiniciar: apaga as fichas guardadas e o histórico de coleta (marcas e fila). Baixa antes o CSV de tudo. As preferências ficam' });
    el.aberto = criar('div', { className: 'aberto' });
    el.pendentes = selo('');
    el.foraSelo = selo('', 'roxo');
    el.ficha = criar('div', { className: 'caixa' });
    el.fila = criar('textarea', { placeholder: 'Link do Maps, place_id;nome ou nome + cidade', 'aria-label': 'Fila de lugares' });
    const bFila = botao('queue-list', 'Fila', () => iniciarFila(el.fila.value.split('\n').map(itemDaLinha).filter(Boolean)),
      { classe: 'mini', dica: 'Coletar fila: abre cada linha (link do Maps, "place_id;nome" ou nome + cidade), lê a ficha e passa à próxima; serve para os candidatos do maps_busca' });
    kit.el.status = criar('div', { className: 'status' });
    kit.acoes = [bColetar, bAbrir, bTodas, bFila, bCsv, bLimpar, el.menu.bProx];
    kit.montar({
      nome: 'Ficha', largura: 350, autobaixar: true, css: CSS_PAINEL,
      extras: [kit.botaoBaixarCada('Baixar cada lugar ao terminar (fila): além do CSV do fim')],
      filhos: [
        el.menu.caixa,
        linha([bColetar, bAbrir, bTodas, kit.el.parar]),
        el.aberto,
        kit.barra('fila'),
        kit.el.status,
        linha([bCsv, el.pendentes, el.foraSelo, esp(), bLimpar]),
        secao('ficha', ['Ficha', kit.ajuda('O que foi lido da casa escolhida. Horário desta semana: em semana com feriado, o dia pode trazer horário especial.')], [el.ficha]),
        secao('fila', ['Fila', kit.ajuda('Lugares fora da lista das casas do B1. Um por linha.')], [el.fila, linha([bFila])]),
      ],
    });
    el.menu.select.addEventListener('change', () => mostrarFicha(lerDados()[el.menu.select.value]));
  }

  let urlVista = '';
  function verificar() {
    if (!kit.hospedeiro()) { montarPainel(); atualizar(); }
    kit.garantir();
    if (location.href !== urlVista) { urlVista = location.href; atualizar(); } else mostrarAberto();
  }

  // Aviso ao fechar a aba com muitas fichas fora de CSV; a fila troca de página sozinha e não dispara.
  if (typeof window !== 'undefined' && window.addEventListener) {
    window.addEventListener('beforeunload', (e) => {
      if (filaAtiva() || ler(CHAVE_ABRIR, null) || pendentes(lerDados(), ler(CHAVE_EXPORTACAO, 0)) < AVISO_PENDENTES) return;
      e.preventDefault();
      e.returnValue = '';
    });
  }

  console.info('[Ficha no Maps] carregado');
  verificar();
  setInterval(() => { try { verificar(); } catch (e) { console.error(NOME, e); } }, 1500);
  if (filaAtiva()) continuarFila().catch((e) => status(`Erro na fila: ${e.message}`, 'erro'));
  else coletarAoAbrir().catch((e) => status(`Erro na coleta: ${e.message}`, 'erro'));
})();
