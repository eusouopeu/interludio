// Testes do menu dos cardápios: node --test cardapio.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

// A lista do menu (lista_cardapio.js) vem antes, como no carregador (@require).
const source = fs.readFileSync(__dirname + '/lista_cardapio.js', 'utf8') + '\n' + fs.readFileSync(__dirname + '/cardapio.user.js', 'utf8');

function carregar(inicial = {}) {
  const valores = new Map(Object.entries(inicial));
  function XHR() {}
  XHR.prototype.send = () => {};
  const ambiente = {
    __test: {},
    GM_getValue: (k, padrao) => (valores.has(k) ? valores.get(k) : padrao),
    GM_setValue: (k, v) => valores.set(k, v),
    GM_deleteValue: (k) => valores.delete(k),
    unsafeWindow: { fetch: async () => ({}), XMLHttpRequest: XHR },
    window: {},
    URL,
    location: { hostname: 'latabuleria.saipos.com', href: 'https://latabuleria.saipos.com/home' },
    document: { querySelector: () => null, querySelectorAll: () => [] },
  };
  const instrumentado = source.slice(0, source.indexOf("  console.info('[Coletor de cardápio] carregado');"))
    + 'Object.assign(globalThis.__test, { ALVOS, estadoCardapio, proximoCardapio, alvoAqui, classificar, montarAlvos, linhaDaLista, slug, buscaDoCardapio });})();';
  vm.runInNewContext(instrumentado, ambiente, { filename: 'cardapio.user.js' });
  return ambiente.__test;
}

test('menu: cardápios sem repetição, estado e próximo que falta na mesma capital', () => {
  const t = carregar();
  assert.equal(new Set(t.ALVOS.map((a) => a.id)).size, t.ALVOS.length);
  const bardo = t.ALVOS.find((a) => a.id === 'bardo_mago');
  const garagem = t.ALVOS.find((a) => a.id === 'garagem_do_nerd');
  const reduto = t.ALVOS.find((a) => a.id === 'reduto');
  assert.equal(t.estadoCardapio(bardo, {}, {}), 'ok'); // 112 itens já no B1
  assert.equal(t.estadoCardapio(bardo, {}, { bardo_mago: false }), 'falta');
  assert.equal(t.estadoCardapio(garagem, {}, {}), 'parcial'); // 1 item no B1: menos de 10
  assert.equal(t.estadoCardapio(reduto, {}, {}), 'falta');
  assert.equal(t.estadoCardapio(garagem, { garagem_do_nerd: { itens: 30 } }, {}), 'ok');
  assert.equal(t.proximoCardapio('bardo_mago', {}, {}).id, 'garagem_do_nerd');
  // com os de Belo Horizonte prontos, vai para outra capital
  const bh = Object.fromEntries(t.ALVOS.filter((a) => a.capital === 'Belo Horizonte').map((a) => [a.id, {}]));
  assert.notEqual(t.proximoCardapio('bardo_mago', bh, {}).capital, 'Belo Horizonte');
  const todos = Object.fromEntries(t.ALVOS.map((a) => [a.id, true]));
  assert.equal(t.proximoCardapio('bardo_mago', {}, todos), null);
});

test('reconhece o cardápio da página aberta pelo host', () => {
  assert.equal(carregar().alvoAqui().id, 'la_tabuleria');
});

test('menu: extração sem itens vira refazer (!) e fontes divergentes viram conferir (◐)', () => {
  const t = carregar();
  const garagem = t.ALVOS.find((a) => a.id === 'garagem_do_nerd');
  assert.equal(t.estadoCardapio(garagem, {}, {}, { garagem_do_nerd: { situacao: 'refazer: nenhum item extraído' } }), 'falha');
  assert.equal(t.estadoCardapio(garagem, {}, {}, { garagem_do_nerd: { situacao: 'conferir: fontes divergem (40 × 12)' } }), 'parcial');
  assert.equal(t.estadoCardapio(garagem, { garagem_do_nerd: { itens: 30 } }, {}, { garagem_do_nerd: { situacao: 'refazer: x' } }), 'ok');
});

test('menu: as 63 casas do B1, com e sem link; sem link abre a busca do cardápio', () => {
  const t = carregar();
  assert.equal(t.ALVOS.length, 63);
  const reduto = t.ALVOS.find((a) => a.id === 'reduto');
  assert.equal(reduto.url, '');
  assert.equal(reduto.host, '');
  // busca só no site aberto: no iFood, a busca do iFood; fora dele, nenhuma (a página não muda)
  assert.equal(t.buscaDoCardapio(reduto, 'ifood.com.br'), 'https://www.ifood.com.br/busca?q=Reduto');
  const muito = t.ALVOS.find((a) => a.id === 'muito_geek');
  assert.equal(t.buscaDoCardapio(muito, 'ifood.com.br'), 'https://www.ifood.com.br/busca?q=Muito%20Geek');
  assert.equal(t.buscaDoCardapio(reduto, 'latabuleria.saipos.com'), '');
  assert.ok(!/google/.test(t.buscaDoCardapio(reduto, 'www.google.com')));
  assert.ok(t.ALVOS.filter((a) => a.url).length >= 9);
});

test('botão +: link vinculado a uma casa e casa nova entram no menu, na capital dela', () => {
  const t = carregar({
    'ccv-alvos-links': { reduto: 'https://reduto.example/cardapio' },
    'ccv-alvos-extras': [['casa_nova', 'Casa Nova', 'Salvador', 'https://casanova.example/menu', null]],
  });
  const alvos = t.montarAlvos();
  assert.equal(alvos.length, 64);
  assert.equal(alvos.find((a) => a.id === 'reduto').host, 'reduto.example');
  const i = alvos.findIndex((a) => a.id === 'casa_nova');
  assert.equal(alvos[i - 1].capital, 'Salvador');
  assert.equal(alvos[i].extra, true);
  assert.equal(t.slug('Muito Geek | TCG • Board Games'), 'muito_geek');
  assert.equal(t.linhaDaLista({ id: 'x', nome: "D'Ávila", capital: 'Salvador', url: 'https://a.b/' }), "  ['x', 'D\\'Ávila', 'Salvador', 'https://a.b/', null],");
});
