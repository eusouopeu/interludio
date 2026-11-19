import { TituloSecao } from "../components/ui";
import { Bloco } from "../components/blocos";

/* Aba do plano: mostra uma seção por vez (conteudo/abas/<aba>/<simples|completo>/<seção>.yaml). Os botões de cima escolhem a seção;
   os de baixo passam para a anterior e a próxima. As tabelas vêm de tabelas.json. */
export default function Secao({ aba, secoes, atual, irPara }) {
  const s = secoes[atual] ?? secoes[0];
  const total = secoes.length;

  return (
    <>
      <TituloSecao id={aba.id} />
      {total > 1 && (
        <nav aria-label="Seções da aba" className="no-print -mt-4 mb-8 flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-semibold tracking-[0.14em] text-azul-700 uppercase">Seções</span>
          {secoes.map((x, i) => (
            <button
              key={x.arquivo}
              onClick={() => irPara(i)}
              aria-current={i === atual ? "step" : undefined}
              className={`cursor-pointer rounded-full border px-3 py-1 text-xs font-semibold transition-colors ${
                i === atual
                  ? "border-roxo-600 bg-roxo-600 text-on-ink"
                  : "border-papel-200 bg-white text-azul-800 hover:border-roxo-600 hover:text-roxo-600"
              }`}
            >
              {x.titulo}
            </button>
          ))}
        </nav>
      )}

      <section key={s.arquivo}>
        <div className="mb-4">
          <h2 className="font-display text-2xl font-bold text-azul-950 sm:text-[1.7rem]">{s.titulo}</h2>
          {s.descricao && <p className="mt-1 max-w-3xl text-sm leading-relaxed text-azul-700">{s.descricao}</p>}
        </div>
        <div className="space-y-6">
          {s.blocos.map((b, i) => <Bloco key={i} b={b} />)}
        </div>
        {s.fonte && <p className="mt-4 text-xs text-azul-700/80">Fonte: {s.fonte}</p>}
      </section>

      {total > 1 && (
        <div className="no-print mt-10 flex items-center justify-between gap-2 border-t border-papel-200 pt-5">
          <button
            onClick={() => irPara(atual - 1)}
            disabled={atual === 0}
            className="min-w-0 cursor-pointer truncate rounded-lg border border-papel-200 bg-white px-3 py-2 text-xs font-semibold text-azul-900 transition-colors hover:border-roxo-600 disabled:cursor-default disabled:opacity-30 sm:text-sm"
          >
            ← {atual > 0 ? secoes[atual - 1].titulo : "Seção anterior"}
          </button>
          <span className="shrink-0 text-xs text-azul-700 tabular-nums">Seção {atual + 1} / {total}</span>
          <button
            onClick={() => irPara(atual + 1)}
            disabled={atual === total - 1}
            className="min-w-0 cursor-pointer truncate rounded-lg border border-roxo-600 bg-white px-3 py-2 text-xs font-semibold text-roxo-700 transition-colors hover:bg-lavanda-100 disabled:cursor-default disabled:opacity-30 sm:text-sm"
          >
            {atual < total - 1 ? secoes[atual + 1].titulo : "Próxima seção"} →
          </button>
        </div>
      )}
    </>
  );
}
