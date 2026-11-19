import { useEffect, useState, useCallback, useRef } from "react";
import { ABAS as SECOES, META, BARRA, RODAPE, secoesDe } from "./conteudo";
import { ModoContexto } from "./components/ui";
import Secao from "./sections/Secao";
import S8Panorama from "./sections/S8Panorama";
import S9Metropoles from "./sections/S9Metropoles";
import S10Regioes from "./sections/S10Regioes";
import S11Conteudo from "./sections/S11Conteudo";
import S12Auditorias from "./sections/S12Auditorias";

// Abas de dados têm componente próprio; as do plano usam a aba genérica (conteudo/abas/).
const ESPECIAIS = {
  panorama: S8Panorama,
  metropoles: S9Metropoles,
  regioes: S10Regioes,
  conteudo: S11Conteudo,
  auditorias: S12Auditorias,
};

const GRUPOS = [...new Set(SECOES.map((s) => s.grupo))];

/* Endereço: #<aba> ou #<aba>/<seção>, com a seção contada a partir de 1. */
function lerHash(modo) {
  const [id, n] = window.location.hash.replace("#", "").split("/");
  const aba = SECOES.find((s) => s.id === id) ?? SECOES[0];
  const total = secoesDe(aba, modo)?.length ?? 1;
  const sec = Math.min(Math.max((parseInt(n, 10) || 1) - 1, 0), total - 1);
  return { id: aba.id, sec };
}

/* Ícones Heroicons (outline, 24): sol, lua e monitor. */
const ICONES = {
  claro: "M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z",
  escuro: "M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z",
};
const Icone = ({ nome, className = "h-4 w-4" }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
    <path d={ICONES[nome]} />
  </svg>
);

/* Tema: segue o sistema até o usuário escolher; a escolha fica só neste navegador. */
const escuroNoSistema = () => window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false;
function useTema() {
  const [tema, setTema] = useState(() => {
    try { return localStorage.getItem("tema") ?? "sistema"; } catch { return "sistema"; }
  });
  useEffect(() => {
    const raiz = document.documentElement;
    if (tema === "sistema") raiz.removeAttribute("data-tema");
    else raiz.setAttribute("data-tema", tema);
    try {
      if (tema === "sistema") localStorage.removeItem("tema");
      else localStorage.setItem("tema", tema);
    } catch { /* sem armazenamento */ }
  }, [tema]);
  const escuro = tema === "escuro" || (tema === "sistema" && escuroNoSistema());
  return [escuro, () => setTema(escuro ? "claro" : "escuro")];
}

/* Botão-ícone que alterna entre o tema claro e o escuro: mostra o tema para o qual vai mudar. */
function BotaoTema({ escuro, alternar, className = "" }) {
  const dica = escuro ? "Usar o tema claro" : "Usar o tema escuro";
  return (
    <button
      onClick={alternar}
      title={dica}
      aria-label={dica}
      className={`cursor-pointer rounded-lg border border-papel-200 bg-white p-2 text-azul-700 transition-colors hover:border-roxo-600 hover:text-roxo-600 ${className}`}
    >
      <Icone nome={escuro ? "claro" : "escuro"} />
    </button>
  );
}

/* Modo de leitura: simples (slides) por padrão; a escolha fica só neste navegador. */
function useModoLeitura() {
  const [modo, setModo] = useState(() => {
    try { return localStorage.getItem("modo") === "completo" ? "completo" : "simples"; } catch { return "simples"; }
  });
  useEffect(() => {
    try { localStorage.setItem("modo", modo); } catch { /* sem armazenamento */ }
  }, [modo]);
  return [modo, setModo];
}

export default function App() {
  const [modo, setModo] = useModoLeitura();
  const [pos, setPos] = useState(() => lerHash(modo));
  const { id: ativa, sec } = pos;
  const [escuro, alternarTema] = useTema();
  const faixa = useRef(null);

  const indice = SECOES.findIndex((s) => s.id === ativa);
  const Especial = ESPECIAIS[ativa];

  const aba = SECOES[indice];
  const secoes = secoesDe(aba, modo);
  const totalSec = secoes?.length ?? 1;

  // ultima: abre a aba na última seção (ao voltar de uma aba para a anterior pelo teclado).
  const ir = useCallback((id, s = 0, ultima = false) => {
    const alvo = SECOES.find((x) => x.id === id);
    const n = ultima ? (secoesDe(alvo, modo)?.length ?? 1) - 1 : s;
    setPos({ id, sec: n });
    window.location.hash = n > 0 ? `${id}/${n + 1}` : id;
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [modo]);
  const irSecao = useCallback((s) => ir(ativa, s), [ativa, ir]);

  useEffect(() => {
    const aoMudarHash = () => setPos(lerHash(modo));
    window.addEventListener("hashchange", aoMudarHash);
    return () => window.removeEventListener("hashchange", aoMudarHash);
  }, [modo]);

  // Ao trocar de modo, a aba fica e a seção volta para a primeira.
  const alternarModo = useCallback(() => {
    setModo((m) => (m === "simples" ? "completo" : "simples"));
    setPos((p) => ({ id: p.id, sec: 0 }));
    window.location.hash = ativa;
  }, [ativa, setModo]);

  // Setas do teclado passam as seções; na primeira ou na última, passam para a aba vizinha.
  // A aba ativa fica à vista na faixa do celular.
  useEffect(() => {
    const aoTeclar = (e) => {
      if (e.target?.matches?.("input, textarea") || e.altKey || e.ctrlKey || e.metaKey) return;
      if (e.key === "ArrowRight") {
        if (sec < totalSec - 1) ir(ativa, sec + 1);
        else if (indice < SECOES.length - 1) ir(SECOES[indice + 1].id);
      }
      if (e.key === "ArrowLeft") {
        if (sec > 0) ir(ativa, sec - 1);
        else if (indice > 0) ir(SECOES[indice - 1].id, 0, true);
      }
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [indice, ir, ativa, sec, totalSec]);

  useEffect(() => {
    faixa.current?.querySelector("[aria-current='page']")?.scrollIntoView({ inline: "center", block: "nearest", behavior: "smooth" });
  }, [ativa]);

  return (
    <div className="flex min-h-screen bg-papel-50 font-sans text-azul-950">
      <a href="#conteudo-principal" className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:bg-roxo-600 focus:px-3 focus:py-2 focus:text-on-ink">
        Pular para o conteúdo
      </a>

      {/* ─────────── Barra lateral (telas grandes) ─────────── */}
      <aside className="no-print fixed inset-y-0 left-0 z-40 hidden w-64 shrink-0 flex-col border-r border-papel-200 bg-papel-100 lg:flex xl:w-72">
        <div className="px-5 pt-6 pb-4 xl:px-6 xl:pt-8">
          <h1 className="font-display text-[2rem] leading-[1] font-black xl:text-4xl">{META.titulo}</h1>
          <p className="mt-3 text-xs leading-relaxed font-bold text-roxo-700">{META.subtitulo.split(",")[0]}</p>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 pb-4" aria-label={BARRA.rotuloNavegacao}>
          {GRUPOS.map((g) => (
            <div key={g} className="mb-3">
              <p className="px-3 pt-2 pb-1 text-[10px] font-semibold tracking-[0.16em] text-azul-700/80 uppercase">{g}</p>
              <ul>
                {SECOES.filter((s) => s.grupo === g).map((s) => {
                  const ativo = s.id === ativa;
                  return (
                    <li key={s.id}>
                      <button
                        onClick={() => ir(s.id)}
                        aria-current={ativo ? "page" : undefined}
                        className={`group relative flex w-full cursor-pointer items-start gap-3 rounded-lg px-3 py-2 text-left transition-colors ${
                          ativo ? "bg-lavanda-100" : "hover:bg-papel-200/60"
                        }`}
                      >
                        <span className={`mt-[2px] w-5 shrink-0 text-[11px] font-bold tabular-nums ${ativo ? "text-roxo-600" : "text-azul-700/60"}`}>
                          {String(s.n).padStart(2, "0")}
                        </span>
                        <span className="min-w-0 flex-1">
                          <span className={`block text-[13px] leading-snug font-semibold ${ativo ? "text-roxo-700" : "text-azul-900"}`}>{s.titulo}</span>
                          {ativo && <span className="mt-0.5 block text-[11px] leading-snug text-azul-700">{s.subtitulo}</span>}
                        </span>
                        {s.tempo && s.grupo === "Plano" && (
                          <span className="mt-[2px] shrink-0 text-[10px] text-azul-700/70 tabular-nums">{s.tempo}</span>
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        <div className="space-y-3 border-t border-papel-200 px-5 py-4 xl:px-6">
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className="text-xs font-semibold">{META.autor}</p>
              <p className="mt-0.5 text-[11px] leading-snug text-azul-700">{META.curso}</p>
              {META.orientador && <p className="mt-0.5 text-[11px] leading-snug text-azul-700">{META.orientador}</p>}
            </div>
          </div>
          <p className="flex items-center gap-1.5 text-[10px] text-azul-700/80">
            <kbd className="rounded border border-papel-200 bg-white px-1.5 py-0.5">←</kbd>
            <kbd className="rounded border border-papel-200 bg-white px-1.5 py-0.5">→</kbd>
            <span>{BARRA.dicaTeclado.replace(/^Use ← → para /, "")}</span>
          </p>
        </div>
      </aside>

      {/* ─────────── Conteúdo ─────────── */}
      <div className="papel-milimetrado flex min-w-0 flex-1 flex-col pb-[calc(4.25rem+env(safe-area-inset-bottom))] lg:pb-0 lg:pl-64 xl:pl-72">
        <header className="no-print sticky top-0 z-20 flex items-center gap-3 border-b border-papel-200 bg-papel-50/95 px-4 py-3 backdrop-blur lg:hidden">
          <span className="shrink-0 text-sm font-bold text-roxo-600 tabular-nums">{String(SECOES[indice].n).padStart(2, "0")}</span>
          <span className="min-w-0 flex-1 truncate font-display text-lg font-bold">{SECOES[indice].titulo}</span>
          <BotaoTema escuro={escuro} alternar={alternarTema} />
        </header>

        <div className="no-print h-1 w-full bg-papel-200" role="progressbar" aria-valuemin={1} aria-valuemax={SECOES.length} aria-valuenow={indice + 1} aria-label="Progresso da apresentação">
          <div className="h-full bg-roxo-600 transition-all duration-500" style={{ width: `${((indice + 1) / SECOES.length) * 100}%` }} />
        </div>

        <main id="conteudo-principal" className="relative mx-auto w-full max-w-5xl flex-1 px-4 py-8 sm:px-6 md:px-8 md:py-10 lg:py-14">
          <BotaoTema escuro={escuro} alternar={alternarTema} className="no-print absolute top-3 right-4 hidden sm:right-6 md:right-8 lg:block" />
          <ModoContexto.Provider value={{ modo, alternar: alternarModo }}>
            {Especial ? (
              <div className={modo === "simples" ? "so-resumo" : undefined}><Especial key={ativa} /></div>
            ) : (
              <Secao key={ativa} aba={aba} secoes={secoes} atual={sec} irPara={irSecao} />
            )}
          </ModoContexto.Provider>
        </main>

        <footer className="no-print border-t border-papel-200 bg-papel-50/90 backdrop-blur">
          <div className="mx-auto flex w-full max-w-5xl items-center justify-between gap-2 px-4 py-4 sm:gap-4 sm:px-6 sm:py-5 md:px-8">
            <button
              onClick={() => indice > 0 && ir(SECOES[indice - 1].id)}
              disabled={indice === 0}
              className="min-w-0 cursor-pointer truncate rounded-lg border border-papel-200 bg-white px-3 py-2.5 text-xs font-semibold text-azul-900 transition-colors hover:border-roxo-600 disabled:cursor-default disabled:opacity-30 sm:px-4 sm:text-sm"
            >
              ← {indice > 0 ? SECOES[indice - 1].titulo : RODAPE.inicio}
            </button>
            <span className="shrink-0 text-xs text-azul-700 tabular-nums">{indice + 1} / {SECOES.length}</span>
            <button
              onClick={() => indice < SECOES.length - 1 && ir(SECOES[indice + 1].id)}
              disabled={indice === SECOES.length - 1}
              className="min-w-0 cursor-pointer truncate rounded-lg bg-roxo-600 px-3 py-2.5 text-xs font-semibold text-on-ink transition-colors hover:bg-roxo-700 disabled:cursor-default disabled:opacity-30 sm:px-4 sm:text-sm"
            >
              {indice < SECOES.length - 1 ? SECOES[indice + 1].titulo : RODAPE.fim} →
            </button>
          </div>
        </footer>
      </div>

      {/* ─────────── Faixa inferior (telas pequenas e médias) ─────────── */}
      <nav
        className="no-print fixed inset-x-0 bottom-0 z-40 border-t border-papel-200 bg-papel-100/95 backdrop-blur lg:hidden"
        style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
        aria-label={BARRA.rotuloNavegacao}
      >
        <ul ref={faixa} className="flex items-stretch gap-1 overflow-x-auto px-2 py-2">
          {SECOES.map((s) => {
            const ativo = s.id === ativa;
            return (
              <li key={s.id} className="shrink-0">
                <button
                  onClick={() => ir(s.id)}
                  aria-label={`${s.n}. ${s.titulo}`}
                  aria-current={ativo ? "page" : undefined}
                  className={`flex h-10 min-w-10 cursor-pointer items-center justify-center rounded-lg px-3 text-sm font-bold tabular-nums transition-colors ${
                    ativo ? "bg-roxo-600 text-on-ink" : "text-azul-700 hover:text-azul-950"
                  }`}
                >
                  {String(s.n).padStart(2, "0")}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>
    </div>
  );
}
