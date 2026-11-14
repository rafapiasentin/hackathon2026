import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ArrowRight, Search } from "lucide-react";
import { buscarLeis } from "../api/client";
import type { ResultadoBusca, Situacao } from "../api/types";
import { StatusBadge } from "../components/StatusBadge";
import { useRota } from "../lib/rota";
import { SITUACAO, ementaLimpa, nomeLei, numeroLegivel } from "../lib/leis";
import { lerReferencia } from "../lib/referencia";
import { Esqueleto } from "../components/Animacoes";

const FILTROS: { valor: Situacao | "todas"; rotulo: string }[] = [
  { valor: "todas", rotulo: "Todas" },
  { valor: "vigente", rotulo: SITUACAO.vigente.rotulo },
  { valor: "vigente_com_alteracoes", rotulo: SITUACAO.vigente_com_alteracoes.rotulo },
  { valor: "revogada", rotulo: SITUACAO.revogada.rotulo },
];

export function Busca() {
  const [params, setParams] = useSearchParams();
  const rota = useRota();
  const q = params.get("q") ?? "";
  const situacao = (params.get("situacao") as Situacao | null) ?? "todas";
  const [texto, setTexto] = useState(q);
  const [resultado, setResultado] = useState<ResultadoBusca | null>(null);
  // Mantém a lista anterior na tela enquanto busca de novo: os itens se reorganizam em vez de piscar
  const [buscando, setBuscando] = useState(true);

  useEffect(() => {
    let ativo = true;
    setBuscando(true);
    buscarLeis(q, situacao).then((r) => {
      if (!ativo) return;
      setResultado(r);
      setBuscando(false);
    });
    return () => {
      ativo = false;
    };
  }, [q, situacao]);

  function atualizar(novo: { q?: string; situacao?: string }) {
    const p = new URLSearchParams(params);
    for (const [k, v] of Object.entries(novo)) {
      if (!v || v === "todas") p.delete(k);
      else p.set(k, v);
    }
    setParams(p, { replace: true });
  }

  return (
    <div className="mx-auto max-w-3xl px-4 pt-10 pb-20 sm:px-6">
      <motion.h1
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="text-3xl font-bold tracking-tight"
      >
        Buscar leis
      </motion.h1>
      <p className="mt-2 text-muted">Procure pelo número da lei (ex.: Lei 14.294/2026), pelo ano ou por um assunto.</p>

      <form
        id="busca"
        role="search"
        className="mt-6"
        onSubmit={(e) => {
          e.preventDefault();
          atualizar({ q: texto.trim() });
        }}
      >
        <label htmlFor="campo-busca" className="sr-only">
          Número, ano ou assunto da lei
        </label>
        <div className="flex items-center gap-2 rounded-2xl border border-border bg-surface p-1.5 pl-4 shadow-card focus-within:border-primary focus-within:ring-4 focus-within:ring-primary/15">
          <Search aria-hidden="true" className="size-5 text-muted" />
          <input
            id="campo-busca"
            type="search"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Ex.: Lei 14.294/2026, código ambiental, 2026"
            className="min-w-0 flex-1 bg-transparent py-2 focus:outline-none"
          />
          <button type="submit" className="rounded-xl bg-primary px-4 py-2 font-semibold text-on-primary hover:bg-primary-strong">
            Buscar
          </button>
        </div>
      </form>

      <fieldset className="mt-4">
        <legend className="sr-only">Mostrar leis por situação</legend>
        <div className="flex flex-wrap gap-2">
          {FILTROS.map((f) => (
            <label key={f.valor} className="cursor-pointer">
              <input
                type="radio"
                name="situacao"
                value={f.valor}
                checked={situacao === f.valor}
                onChange={() => atualizar({ situacao: f.valor })}
                className="peer sr-only"
              />
              <span className="relative inline-block rounded-full border border-border bg-surface px-3.5 py-1.5 text-sm font-medium text-muted transition-colors peer-checked:border-primary peer-checked:text-primary-strong peer-focus-visible:outline-3 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-[var(--focus)]">
                {situacao === f.valor && (
                  <motion.span
                    layoutId="filtro-ativo"
                    aria-hidden="true"
                    className="absolute inset-0 rounded-full bg-primary-soft"
                    transition={{ type: "spring", stiffness: 420, damping: 34 }}
                  />
                )}
                <span className="relative">{f.rotulo}</span>
              </span>
            </label>
          ))}
        </div>
      </fieldset>

      <div className="mt-8" aria-live="polite" aria-busy={buscando}>
        {!resultado ? (
          <div role="status">
            <span className="sr-only">Buscando...</span>
            <Esqueleto className="mb-3 h-4 w-32" />
            <div className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-surface">
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="grid gap-2 p-5">
                  <div className="flex gap-2">
                    <Esqueleto className="h-5 w-36" />
                    <Esqueleto className="h-5 w-20 rounded-full" />
                  </div>
                  <Esqueleto className="h-4 w-full" />
                  <Esqueleto className="h-4 w-2/3" />
                </div>
              ))}
            </div>
          </div>
        ) : resultado.itens.length === 0 ? (
          <p className="text-muted">{semResultado(q)}</p>
        ) : (
          <>
            <p className="mb-3 text-sm text-muted">
              {resultado.total.toLocaleString("pt-BR")} {resultado.total === 1 ? "lei encontrada" : "leis encontradas"}
            </p>
            <motion.ul
              layout
              className={`divide-y divide-border overflow-hidden rounded-2xl border border-border bg-surface transition-opacity ${
                buscando ? "opacity-60" : ""
              }`}
            >
              <AnimatePresence initial={false} mode="popLayout">
              {resultado.itens.map((l, i) => (
                <motion.li
                  key={l.id}
                  layout
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0, transition: { duration: 0.25, delay: Math.min(i, 8) * 0.04 } }}
                  exit={{ opacity: 0, transition: { duration: 0.15 } }}
                >
                  <Link to={rota(`/lei/${l.id}`)} className="group flex items-start gap-4 p-4 transition hover:bg-primary-soft sm:p-5">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-semibold text-text">{nomeLei(l.chave, l.ano)}</span>
                        <StatusBadge situacao={l.situacao} />
                        {l.exemplo && <span className="rounded-full border border-warn/30 bg-warn-soft px-2 py-0.5 text-xs font-semibold text-warn">Exemplo</span>}
                      </div>
                      <p className="mt-1 line-clamp-2 text-muted">{ementaLimpa(l.ementa)}</p>
                    </div>
                    <ArrowRight aria-hidden="true" className="mt-1 size-5 shrink-0 text-muted transition group-hover:translate-x-0.5 group-hover:text-primary" />
                  </Link>
                </motion.li>
              ))}
              </AnimatePresence>
            </motion.ul>
          </>
        )}
      </div>
    </div>
  );
}

function semResultado(q: string) {
  const ref = lerReferencia(q);
  if (!ref) return "Nenhuma lei encontrada. Tente outra palavra ou o número da lei.";
  const nome = `Lei ${numeroLegivel(ref.numero)}${ref.ano ? "/" + ref.ano : ""}`;
  return `Não encontramos a ${nome}. Confira o número e o ano, ou procure pelo assunto.`;
}
