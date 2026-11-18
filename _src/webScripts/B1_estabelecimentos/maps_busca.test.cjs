// Testes do maps_busca.user.js: node --test maps_busca.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

// A lista do menu (lista_maps_busca.js) vem antes, como no carregador (@require).
const source = fs.readFileSync(__dirname + '/lista_maps_busca.js', 'utf8') + '\n' + fs.readFileSync(__dirname + '/maps_busca.user.js', 'utf8');

function carregar() {
  const gm = new Map();
  const ambiente = {
    __test: {}, structuredClone,
    GM_getValue: (k, p) => (gm.has(k) ? structuredClone(gm.get(k)) : p),
    GM_setValue: (k, v) => gm.set(k, structuredClone(v)),
    GM_deleteValue: (k) => gm.delete(k),
    location: { href: 'https://www.google.com/maps/', pathname: '/maps/' },
    document: { querySelector: () => null, querySelectorAll: () => [] },
  };
  const instrumentado = source.slice(0, source.indexOf("  console.info('[Busca no Maps] carregado');"))
    + 'Object.assign(globalThis.__test, { ALVOS, alvoDaUrl, urlBusca, lerHref, lerNumeroAvaliacoes, lerNota, lerCartao, registrar, estadoBusca, proximaQueFalta, COLS, COLS_BUSCAS, linhasCandidatos, linhasBuscas, naOrdem, unicos, nomeArquivo, pendentes, lerDados, kit });\n})();';
  vm.runInNewContext(instrumentado, ambiente, { filename: 'maps_busca.user.js' });
  return { t: ambiente.__test, gm };
}

// Cartões e links lidos no Maps em 14/11/2026 (busca "luderia Belo Horizonte").
const HREF = 'https://www.google.com/maps/place/LudoCaf%C3%A9/data=!4m7!3m6!1s0xa69731dfeb98c7:0x660ed37e797d6c40!8m2!3d-19.944717!4d-43.946234!16s%2Fg%2F11hzpk908_!19sChIJx5jr3zGXpgARQGx9eX7TDmY?authuser=0&hl=pt-BR&rclk=1';
const CARTAO = 'LudoCafé\nLudoCafé\n4,6(592)\nLoja de jogos ·  · R. Antônio Dias, 201\nAberto · Fecha 00:00 · (31) 3646-6046\n\nWebsite\n\nRotas';

test('as buscas são os 15 termos em cada uma das 28 cidades, sem repetição', () => {
  const { t } = carregar();
  assert.equal(t.ALVOS.length, 15 * 28);
  assert.equal(new Set(t.ALVOS.map((a) => a.id)).size, 420);
  assert.equal(t.ALVOS[0].consulta, 'ludobar em Rio Branco');
  assert.ok(t.ALVOS.some((a) => a.consulta === 'luderia em Campinas' && a.uf === 'SP'));
  // Cada busca conta numa só cidade: a soma por cidade fecha com o total.
  const porCidade = {};
  for (const a of t.ALVOS) porCidade[a.cidade] = (porCidade[a.cidade] || 0) + 1;
  assert.equal(Object.values(porCidade).reduce((s, n) => s + n, 0), t.ALVOS.length);
});

test('reconhece a busca aberta pela URL, com acento, "+" e maiúsculas', () => {
  const { t } = carregar();
  const a = t.ALVOS.find((x) => x.consulta === 'café de jogos de tabuleiro em São Paulo');
  assert.equal(t.alvoDaUrl(t.urlBusca(a)).id, a.id);
  assert.equal(t.alvoDaUrl('https://www.google.com/maps/search/caf%C3%A9+de+jogos+de+tabuleiro+em+S%C3%A3o+Paulo/@-23.5,-46.6,12z/data=!3m1!4b1').id, a.id);
  assert.equal(t.alvoDaUrl('https://www.google.com/maps/search/pizzaria+em+Salvador/'), null);
  assert.equal(t.alvoDaUrl('https://www.google.com/maps/place/LudoCaf%C3%A9/'), null);
});

test('lê o cartão da lista: nota, avaliações, categoria, endereço, coordenada e place_id', () => {
  const { t } = carregar();
  const c = t.lerCartao('LudoCafé', CARTAO, HREF);
  assert.deepEqual({ ...c }, {
    nome: 'LudoCafé', categoria_maps: 'Loja de jogos', endereco: 'R. Antônio Dias, 201', nota_media: '4.6', n_avaliacoes: '592', situacao_maps: '',
    lat: -19.944717, lng: -43.946234, place_id: 'ChIJx5jr3zGXpgARQGx9eX7TDmY', id_maps: '0xa69731dfeb98c7:0x660ed37e797d6c40',
    link_google_maps: HREF.split('?')[0],
  });
  // Sem o "·" duplo, com preço e sem avaliação.
  assert.equal(t.lerCartao('X', 'X\n4,4(167)\nLoja de jogos · Av. Amazonas, 2310', '').endereco, 'Av. Amazonas, 2310');
  assert.equal(t.lerCartao('X', 'X\n4,0(1.731) · $$\nBar · Rua A, 1', '').categoria_maps, 'Bar');
  assert.equal(t.lerCartao('X', 'X\nNenhuma avaliação\nBar · Rua A, 1', '').n_avaliacoes, '0');
  assert.equal(t.lerCartao('X', 'X\nBar · Rua A, 1', '').n_avaliacoes, '');
  assert.equal(t.lerCartao('X', 'X\n4,5(12)\nBar · Rua A, 1\nPermanentemente fechado', '').situacao_maps, 'fechado permanentemente');
  assert.equal(t.lerNumeroAvaliacoes('4,7(1,2 mil)'), '1200');
});

test('estado da busca e próxima que falta, primeiro na mesma cidade', () => {
  const { t } = carregar();
  assert.equal(t.estadoBusca(null), 'falta');
  assert.equal(t.estadoBusca({ estado: 'lista', fim: true }), 'ok');
  assert.equal(t.estadoBusca({ estado: 'lista', fim: false }), 'parcial');
  assert.equal(t.estadoBusca({ estado: 'vazio' }), 'ok');
  assert.equal(t.estadoBusca({ estado: 'lugar', fim: true }), 'ok');
  assert.equal(t.estadoBusca({ estado: 'bloqueado' }), 'falha');
  assert.equal(t.estadoBusca({ estado: 'falhou' }, true), 'ok');
  assert.equal(t.estadoBusca({ estado: 'lista', fim: true }, false), 'falta');
  const [a0, a1, a2] = t.ALVOS;
  assert.equal(t.proximaQueFalta(a0.id, { [a1.id]: { estado: 'lista', fim: true } }, {}).id, a2.id);
  // Última busca de uma cidade: segue para a cidade seguinte.
  assert.equal(t.proximaQueFalta(t.ALVOS[14].id, {}, {}).id, t.ALVOS[0].id);
  const tudo = Object.fromEntries(t.ALVOS.map((a) => [a.id, { estado: 'vazio' }]));
  assert.equal(t.proximaQueFalta(a0.id, tudo, {}), null);
});

test('registra a busca com a posição e exporta candidatos e buscas com cabeçalho fixo', () => {
  const { t } = carregar();
  const [a, b] = t.ALVOS;
  const item = t.lerCartao('LudoCafé', CARTAO, HREF);
  const dia = new Date(2026, 10, 14, 22, 5);
  t.registrar(b, { estado: 'lista', fim: true, itens: [item, { ...item, nome: 'Outro', place_id: 'ChIJoutro' }] }, dia);
  t.registrar(a, { estado: 'vazio', fim: true, itens: [] }, dia);
  const buscas = t.naOrdem(t.lerDados());
  assert.deepEqual([...buscas.map((x) => x.id)], [a.id, b.id]);
  const cand = t.linhasCandidatos(buscas);
  // Uma linha por busca × resultado: a soma dos resultados das buscas fecha com as linhas.
  assert.equal(cand.length, buscas.reduce((s, x) => s + x.n, 0));
  assert.deepEqual([...cand.map((l) => l.posicao)], [1, 2]);
  assert.equal(cand[0].termo_busca, 'luderia');
  assert.equal(cand[0].cidade_busca, 'Rio Branco');
  assert.equal(cand[0].chegou_ao_fim, 'sim');
  assert.equal(cand[0].data_coleta, '2026-11-14');
  assert.equal(t.unicos(buscas), 2);
  assert.deepEqual([...t.linhasBuscas(buscas)].map((l) => `${l.situacao}:${l.n_resultados}`), ['sem resultado:0', 'lista lida:2']);
  assert.deepEqual([...t.COLS], ['place_id', 'id_maps', 'nome', 'endereco', 'categoria_maps', 'nota_media', 'n_avaliacoes', 'situacao_maps', 'lat', 'lng',
    'cidade_busca', 'uf_busca', 'termo_busca', 'consulta', 'posicao', 'n_resultados', 'chegou_ao_fim', 'link_google_maps', 'data_coleta']);
  assert.deepEqual([...t.COLS_BUSCAS], ['cidade_busca', 'uf_busca', 'termo_busca', 'consulta', 'situacao', 'n_resultados', 'chegou_ao_fim', 'data_coleta', 'url']);
  const csv = t.kit.csv(cand, t.COLS);
  assert.ok(csv.startsWith('﻿place_id;id_maps;nome;'));
  assert.equal(csv.split('\r\n').length, 3);
  assert.equal(t.nomeArquivo('candidatos', dia), '2026-11-14_2205_maps_busca_candidatos.csv');
  assert.equal(t.nomeArquivo('candidatos', dia, 'salvador_luderia'), '2026-11-14_2205_maps_busca_candidatos_salvador_luderia.csv');
  assert.equal(t.pendentes(t.lerDados(), 0), 2);
  assert.equal(t.pendentes(t.lerDados(), dia.getTime()), 0);
});
