// Junta o conteúdo do site. As abas do plano vêm de conteudo/abas/: uma pasta por aba, com _aba.yaml e duas
// subpastas, simples/ (o roteiro dos slides) e completo/ (o conteúdo detalhado), cada uma com um .yaml por seção,
// na ordem do número no nome. As abas de dados de apoio e a moldura do site vêm de conteudo/site.json.
import yaml from "js-yaml";
import site from "./conteudo/site.json";

const arquivos = import.meta.glob("./conteudo/abas/**/*.yaml", { query: "?raw", import: "default", eager: true });

const pastas = {};
for (const [caminho, texto] of Object.entries(arquivos)) {
  const m = caminho.match(/abas\/([^/]+)\/(?:(simples|completo)\/)?([^/]+)\.yaml$/);
  if (!m) continue;
  const [, pasta, modo, arquivo] = m;
  const p = (pastas[pasta] ??= { aba: null, simples: [], completo: [] });
  const dados = yaml.load(texto) ?? {};
  if (!modo && arquivo === "_aba") p.aba = dados;
  else if (modo) p[modo].push({ arquivo, ...dados, blocos: dados.blocos ?? [] });
}

const ordenar = (lista) => lista.sort((a, b) => a.arquivo.localeCompare(b.arquivo));

const doPlano = Object.keys(pastas)
  .sort()
  .map((pasta) => {
    const { aba, simples, completo } = pastas[pasta];
    return {
      id: pasta.replace(/^\d+-/, ""),
      grupo: "Plano",
      ...aba,
      subtituloLongo: aba?.cabecalho ?? aba?.subtitulo,
      secoes: { simples: ordenar(simples), completo: ordenar(completo) },
    };
  });

export const ABAS = [...doPlano, ...site.secoes].map((s, i) => ({ ...s, n: i + 1 }));
export const META = site.meta;
export const QRCODE = site.qrcode;
export const BARRA = site.barraLateral;
export const RODAPE = site.rodape;

/* Seções da aba no modo pedido; o modo que faltar usa o outro. Abas de dados têm uma seção só. */
export function secoesDe(aba, modo) {
  if (!aba.secoes) return null;
  const s = aba.secoes[modo];
  return s?.length ? s : aba.secoes[modo === "simples" ? "completo" : "simples"];
}
