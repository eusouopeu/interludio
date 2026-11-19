import { createContext, useContext, useEffect, useRef, useState } from "react";
import { ABAS } from "../conteudo";

/* O usuário pode ter pedido menos animação no sistema; nesse caso tudo entra já visível. */
const semAnimacao = () =>
  typeof window !== "undefined" &&
  window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

/* Revela o conteúdo quando ele entra na viewport. */
export function Reveal({ children, delay = 0, className = "" }) {
  const ref = useRef(null);
  const [visivel, setVisivel] = useState(semAnimacao);

  useEffect(() => {
    const el = ref.current;
    if (!el || semAnimacao()) return;
    const obs = new IntersectionObserver(
      ([entrada]) => entrada.isIntersecting && setVisivel(true),
      { threshold: 0.12 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: visivel ? 1 : 0,
        transform: visivel ? "none" : "translateY(16px)",
        transition: `opacity .55s cubic-bezier(.22,1,.36,1) ${delay}ms, transform .55s cubic-bezier(.22,1,.36,1) ${delay}ms`,
      }}
    >
      {children}
    </div>
  );
}

/* Modo de leitura: "simples" (o roteiro dos slides, padrão) ou "completo" (o conteúdo detalhado). */
export const ModoContexto = createContext({ modo: "simples", alternar: () => {} });
export const useModo = () => useContext(ModoContexto);

/* Ícones Heroicons (outline, 24): apresentação (modo simples) e documento (modo completo). */
const ICONE_MODO = {
  simples: "M3.75 3v11.25A2.25 2.25 0 0 0 6 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0 1 18 16.5h-2.25m-7.5 0h7.5m-7.5 0-1 3m8.5-3 1 3m0 0 .5 1.5m-.5-1.5h-9.5m0 0-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6",
  completo: "M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z",
};

/* Botão discreto do cabeçalho: alterna entre o modo simples e o completo em todas as abas. */
function BotaoModo() {
  const { modo, alternar } = useModo();
  const dica = modo === "simples" ? "Modo simples (slides). Clique para o modo completo" : "Modo completo. Clique para o modo simples (slides)";
  return (
    <button
      onClick={alternar}
      title={dica}
      aria-label={dica}
      aria-pressed={modo === "completo"}
      className="no-print cursor-pointer rounded-md p-1 text-azul-700/60 transition-colors hover:bg-papel-100 hover:text-roxo-600"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4" aria-hidden="true">
        <path d={ICONE_MODO[modo]} />
      </svg>
    </button>
  );
}

/* Cabeçalho da aba. Número, título e subtítulo vêm de conteudo/abas/<aba>/_aba.yaml (ou de site.json). */
export function TituloSecao({ id }) {
  const s = ABAS.find((x) => x.id === id);
  if (!s) return null;
  const total = ABAS.length;
  return (
    <header className="mb-8 sm:mb-10">
      <div className="flex items-center gap-3 text-[11px] font-semibold tracking-[0.14em] text-azul-700 uppercase">
        <span className="text-roxo-600">
          {String(s.n).padStart(2, "0")}
          <span className="text-azul-700/50"> / {String(total).padStart(2, "0")}</span>
        </span>
        <span className="h-px flex-1 bg-papel-200" />
        <BotaoModo />
        <span>{s.grupo}</span>
        {s.tempo && <span className="rounded bg-lavanda-100 px-2 py-0.5 text-roxo-700">{s.tempo}</span>}
      </div>
      <h1 className="mt-4 font-display text-4xl leading-[1.05] font-bold text-azul-950 sm:text-5xl">{s.titulo}</h1>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-azul-700 sm:text-base">{s.subtituloLongo ?? s.subtitulo}</p>
      {s.capitulo && <p className="mt-2 text-xs font-medium text-azul-700/80">{s.capitulo}</p>}
    </header>
  );
}

export function Cartao({ children, className = "", tom = "claro" }) {
  const tons = {
    claro: "bg-white border-papel-200",
    areia: "bg-papel-100 border-papel-200",
    escuro: "bg-azul-950 border-azul-950 text-on-ink",
    brasa: "bg-roxo-600 border-roxo-700 text-on-ink",
  };
  return (
    <div className={`rounded-lg border ${tons[tom]} ${className}`}>
      {children}
    </div>
  );
}

export function Etiqueta({ children, cor = "var(--color-roxo-600)", escura = false }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold tracking-wide whitespace-nowrap ${
        escura ? "text-white" : "text-azul-950"
      }`}
      style={{ backgroundColor: cor }}
    >
      {children}
    </span>
  );
}

/* Números que contam a partir de zero quando entram na tela. */
export function Contador({ valor, sufixo = "", decimais = 0, duracao = 900 }) {
  const ref = useRef(null);
  const [n, setN] = useState(() => (semAnimacao() ? valor : 0));

  useEffect(() => {
    const el = ref.current;
    if (!el || semAnimacao()) return;
    const obs = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      obs.disconnect();
      const inicio = performance.now();
      const passo = (agora) => {
        const t = Math.min((agora - inicio) / duracao, 1);
        setN(valor * (1 - Math.pow(1 - t, 3)));
        if (t < 1) requestAnimationFrame(passo);
      };
      requestAnimationFrame(passo);
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, [valor, duracao]);

  return (
    <span ref={ref} className="tabular-nums">
      {n.toLocaleString("pt-BR", {
        minimumFractionDigits: decimais,
        maximumFractionDigits: decimais,
      })}
      {sufixo}
    </span>
  );
}

export function Nota({ children }) {
  return (
    <p className="mt-4 border-l-[3px] border-destaque-600/60 pl-3 text-xs leading-relaxed text-azul-700">
      {children}
    </p>
  );
}

/* Bloco recolhível. `aberto` define apenas o estado inicial. */
export function Sanfona({ titulo, subtitulo, children, aberto = false, cor, corTexto = "var(--color-on-ink)", contagem }) {
  const [ativo, setAtivo] = useState(aberto);
  const fundo = cor ?? "var(--color-papel-100)";
  const tinta = cor ? corTexto : "var(--color-azul-950)";

  return (
    <div className="overflow-hidden rounded-lg border border-papel-200 bg-white">
      <button
        onClick={() => setAtivo((v) => !v)}
        aria-expanded={ativo}
        className="flex w-full cursor-pointer items-center justify-between gap-3 px-6 py-4 text-left transition-opacity hover:opacity-90"
        style={{ backgroundColor: fundo }}
      >
        <span className="min-w-0">
          <span className="block font-display text-xl leading-tight font-semibold" style={{ color: tinta }}>
            {titulo}
          </span>
          {subtitulo && (
            <span className="mt-0.5 block text-xs" style={{ color: tinta, opacity: 0.75 }}>
              {subtitulo}
            </span>
          )}
        </span>
        <span className="flex shrink-0 items-center gap-3">
          {contagem != null && (
            <span
              className="rounded-full px-2.5 py-0.5 text-xs font-bold tabular-nums"
              style={{ backgroundColor: "rgba(255,255,255,.28)", color: tinta }}
            >
              {contagem}
            </span>
          )}
          <svg
            width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke={tinta} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
            style={{ transform: ativo ? "rotate(180deg)" : "none", transition: "transform .3s ease" }}
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </span>
      </button>
      <div className="grid transition-all duration-300" style={{ gridTemplateRows: ativo ? "1fr" : "0fr" }}>
        <div className="overflow-hidden">{children}</div>
      </div>
    </div>
  );
}
