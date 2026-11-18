// Testes do maps_ficha.user.js: node --test maps_ficha.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

// A lista do menu (lista_maps_ficha.js) vem antes, como no carregador (@require).
const source = fs.readFileSync(__dirname + '/lista_maps_ficha.js', 'utf8') + '\n' + fs.readFileSync(__dirname + '/maps_ficha.user.js', 'utf8');

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
  const instrumentado = source.slice(0, source.indexOf("  console.info('[Ficha no Maps] carregado');"))
    + 'Object.assign(globalThis.__test, { POP, DIAS, lerTurnos, lerHorarios, lerUrl, situacaoMaps, casaDoLugar, estadoCasa, proximaQueFalta, urlCasa, COLS, linhasCsv, nomeArquivo, itemDaLinha, pendentes, kit });\n})();';
  vm.runInNewContext(instrumentado, ambiente, { filename: 'maps_ficha.user.js' });
  return { t: ambiente.__test, gm };
}

// Tabela de horário do Bardo Mago, lida no Maps em 14/11/2026 (semana do feriado de 15/11).
const TABELA = [
  ['sábado', '14:00 a 00:00'],
  ['domingo(Proclamação da República)', '13:00 a 22:00, Os horários podem ser diferentes'],
  ['segunda-feira', 'Fechado'], ['terça-feira', 'Fechado'],
  ['quarta-feira', '18:00 a 00:00'], ['quinta-feira', '18:00 a 00:00'], ['sexta-feira', '18:00 a 00:00'],
];
const URL_BARDO = 'https://www.google.com/maps/place/Bardo+Mago/@-19.905169,-43.9158352,17z/data=!3m1!4b1!4m6!3m5!1s0xa69bf6688ec545:0xbda974a705f6f50e!8m2!3d-19.905169!4d-43.9158352!16s%2Fg%2F11vwwp24m9?hl=pt-BR';

test('a população traz as 63 casas do B1, sem repetição', () => {
  const { t } = carregar();
  assert.equal(t.POP.length, 63);
  assert.equal(new Set(t.POP.map((p) => p.id)).size, 63);
  // Cada casa conta numa só capital: a soma por capital fecha com o total.
  const porCapital = {};
  for (const p of t.POP) porCapital[p.capital] = (porCapital[p.capital] || 0) + 1;
  assert.equal(Object.values(porCapital).reduce((s, n) => s + n, 0), 63);
});

test('lê os turnos: travessão ou "a", dois turnos, madrugada, fechado e 24 horas', () => {
  const { t } = carregar();
  assert.deepEqual([...t.lerTurnos('14:00 a 00:00')].map((x) => [...x]), [[840, 1440]]);
  assert.deepEqual([...t.lerTurnos('18:00–01:00')].map((x) => [...x]), [[1080, 1500]]);
  assert.deepEqual([...t.lerTurnos('11:00 a 15:00, 18:00 a 23:00')].map((x) => [...x]), [[660, 900], [1080, 1380]]);
  assert.deepEqual([...t.lerTurnos('Fechado')], []);
  assert.deepEqual([...t.lerTurnos('Aberto 24 horas')].map((x) => [...x]), [[0, 1440]]);
});

test('monta o horário da semana no formato de B1_horarios.csv', () => {
  const { t } = carregar();
  const h = t.lerHorarios(TABELA);
  assert.deepEqual({ ...h }, {
    segunda: '', terca: '', quarta: '18:00-00:00', quinta: '18:00-00:00', sexta: '18:00-00:00', sabado: '14:00-00:00', domingo: '13:00-22:00',
    semana_com_feriado: 'sim', dias_abertos: 5, horas_semana: 37, abre_cedo: '13:00', fecha_tarde: '24:00', situacao: 'ok',
  });
  // Madrugada conta no dia em que abre; dois turnos separados por " | ".
  const dias = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo'];
  const h2 = t.lerHorarios(dias.map((d, i) => [d, i === 5 ? '13:00 a 18:00, 19:00 a 01:00' : i === 4 ? '18:00 a 01:00' : 'Fechado']));
  assert.equal(h2.sabado, '13:00-18:00 | 19:00-01:00');
  assert.equal(h2.sexta, '18:00-01:00');
  assert.equal(h2.horas_semana, 18);
  assert.equal(h2.fecha_tarde, '25:00');
  assert.equal(h2.dias_abertos, 2);
  assert.equal(h2.semana_com_feriado, 'não');
  assert.equal(t.lerHorarios(dias.map((d) => [d, 'Aberto 24 horas'])).situacao, '24 horas');
  assert.equal(t.lerHorarios(dias.map((d) => [d, 'Aberto 24 horas'])).segunda, '00:00-24:00');
  assert.equal(t.lerHorarios(dias.map((d) => [d, 'Fechado'])).situacao, 'fechado a semana toda');
  assert.equal(t.lerHorarios([]).situacao, 'sem horário');
  assert.equal(t.lerHorarios(TABELA.slice(0, 3)).situacao, 'horário incompleto (3 de 7 dias)');
});

test('lê coordenada, id do Maps e nome do fim da URL, e a situação do lugar', () => {
  const { t } = carregar();
  assert.deepEqual({ ...t.lerUrl(URL_BARDO) }, { id_maps: '0xa69bf6688ec545:0xbda974a705f6f50e', lat: -19.905169, lng: -43.9158352, nome_url: 'Bardo Mago' });
  // Dois lugares na URL: vale o último.
  assert.equal(t.lerUrl(URL_BARDO.replace('?hl', '!1s0x1:0x2!3d-10.5!4d-40.5?hl')).lat, -10.5);
  assert.equal(t.lerUrl('https://www.google.com/maps/').id_maps, '');
  assert.equal(t.situacaoMaps('Bar · Fechado permanentemente'), 'fechado permanentemente');
  assert.equal(t.situacaoMaps('Temporariamente fechado'), 'fechado temporariamente');
  assert.equal(t.situacaoMaps('Aberto · Fecha 00:00'), 'em funcionamento');
});

test('casa da lista pelo lugar aberto (até 300 m), estado e próxima que falta', () => {
  const { t } = carregar();
  const bardo = t.POP.find((p) => p.nome === 'Bardo Mago');
  assert.equal(t.casaDoLugar(t.lerUrl(URL_BARDO), bardo.id).id, bardo.id);
  assert.equal(t.casaDoLugar(t.lerUrl(URL_BARDO), 'outro').id, bardo.id);
  assert.equal(t.casaDoLugar({ lat: 0, lng: 0 }, bardo.id), null);
  assert.equal(t.casaDoLugar({ lat: '', lng: '' }, bardo.id), null);
  assert.equal(t.estadoCasa(null), 'falta');
  assert.equal(t.estadoCasa({ situacao: 'ok' }), 'ok');
  assert.equal(t.estadoCasa({ situacao: 'sem horário' }), 'ok');
  assert.equal(t.estadoCasa({ falha: 'lugar diferente' }), 'falha');
  assert.equal(t.estadoCasa({ falha: 'x' }, true), 'ok');
  assert.equal(t.estadoCasa({ situacao: 'ok' }, false), 'falta');
  const [p0, p1, p2] = t.POP;
  assert.equal(t.proximaQueFalta(p0.id, { [p1.id]: { situacao: 'ok' } }, {}).id, p2.id);
  assert.equal(t.proximaQueFalta(p0.id, Object.fromEntries(t.POP.map((p) => [p.id, { situacao: 'ok' }])), {}), null);
});

test('CSV: cabeçalho fixo, casas na ordem da lista e lugares da fila no fim', () => {
  const { t } = carregar();
  assert.deepEqual([...t.COLS], ['place_id', 'id_maps', 'nome', 'capital', 'categoria_maps', 'nota_media', 'n_avaliacoes', 'situacao_maps', 'endereco', 'lat', 'lng',
    'site', 'telefone', 'plus_code', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo',
    'dias_abertos', 'horas_semana', 'abre_cedo', 'fecha_tarde', 'semana_com_feriado', 'situacao', 'url', 'data_coleta']);
  const [p0, p1] = t.POP;
  const dados = { '0x1:0x2': { nome: 'Fora' }, [p1.id]: { nome: p1.nome, place_id: p1.id }, [p0.id]: { nome: p0.nome, place_id: p0.id, ...t.lerHorarios(TABELA) } };
  const linhas = t.linhasCsv(dados);
  assert.deepEqual([...linhas.map((l) => l.nome)], [p0.nome, p1.nome, 'Fora']);
  assert.equal(linhas.length, Object.keys(dados).length);
  const csv = t.kit.csv(linhas, t.COLS);
  assert.ok(csv.startsWith('﻿place_id;id_maps;nome;capital;'));
  assert.ok(csv.split('\r\n')[1].includes(';18:00-00:00;'));
  assert.equal(t.nomeArquivo(new Date(2026, 10, 14, 9, 7)), '2026-11-14_0907_maps_ficha.csv');
  assert.equal(t.nomeArquivo(new Date(2026, 10, 14, 9, 7), 'bardo_mago'), '2026-11-14_0907_maps_ficha_bardo_mago.csv');
});

test('linha da fila: link, "place_id;nome" ou nome + cidade', () => {
  const { t } = carregar();
  assert.equal(t.itemDaLinha(''), null);
  assert.equal(t.itemDaLinha('# comentário'), null);
  assert.equal(t.itemDaLinha(URL_BARDO).url, URL_BARDO);
  const i = t.itemDaLinha('ChIJx5jr3zGXpgARQGx9eX7TDmY;LudoCafé');
  assert.equal(i.pid, 'ChIJx5jr3zGXpgARQGx9eX7TDmY');
  assert.equal(i.nome, 'LudoCafé');
  assert.ok(i.url.includes('query_place_id=ChIJx5jr3zGXpgARQGx9eX7TDmY'));
  assert.ok(t.itemDaLinha('LudoCafé Belo Horizonte').url.includes('/maps/search/LudoCaf%C3%A9%20Belo%20Horizonte'));
});
