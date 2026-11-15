import { AnimatePresence, motion } from "motion/react";
import { useId, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Ban,
  ChevronDown,
  ExternalLink,
  FileSpreadsheet,
  FileText,
  PenLine,
  Scale,
  TriangleAlert,
  type LucideIcon,
} from "lucide-react";
import type { Camada, Situacao } from "../api/types";
import { SITUACAO } from "../lib/leis";
import { useRota } from "../lib/rota";
import { StatusBadge } from "./StatusBadge";

const ICONE: Record<Camada["papel"], LucideIcon> = {
  lei: Scale,
  alteracao: PenLine,
  regulamentada_por: FileText,
  anexo_atualizado_por: FileSpreadsheet,
  eficacia_suspensa_por: Ban,
};

/**
 * "Ver de onde vem esta resposta": a resposta curta fica para todo mundo; aqui aparece a cadeia
 * de normas (lei -> lei que mudou o artigo -> decreto que detalha) e os avisos.
 */
export function OrigemResposta({ camadas = [], alertas = [] }: { camadas?: Camada[]; alertas?: string[] }) {
  const [aberto, setAberto] = useState(false);
  const id = useId();
  const rota = useRota();
  // Só a própria lei e nenhum aviso: o "Baseado em" já mostra tudo.
  if (camadas.length <= 1 && alertas.length === 0) return null;
  const decretos = camadas.filter((c) => c.papel !== "lei" && c.papel !== "alteracao").length;
  const resumo = [
    `${camadas.length} ${camadas.length === 1 ? "norma" : "normas"}`,
    decretos ? `${decretos} ${decretos === 1 ? "decreto" : "decretos"}` : "",
    alertas.length ? `${alertas.length} ${alertas.length === 1 ? "aviso" : "avisos"}` : "",
  ]
    .filter(Boolean)
    .join(" · ");

  return (
    <section className="mt-5 rounded-xl border border-border">
      <h3 className="m-0">
        <button
          type="button"
          onClick={() => setAberto((v) => !v)}
          aria-expanded={aberto}
          aria-controls={id}
          className="flex w-full items-center justify-between gap-3 rounded-xl px-4 py-3 text-left hover:bg-primary-soft"
        >
          <span>
            <span className="block font-semibold text-primary">Ver de onde vem esta resposta</span>
            <span className="block text-sm text-muted">{resumo}</span>
          </span>
          <ChevronDown
            aria-hidden="true"
            className={`size-5 shrink-0 text-primary transition-transform ${aberto ? "rotate-180" : ""}`}
          />
        </button>
      </h3>

      <AnimatePresence initial={false}>
        {aberto && (
          <motion.div
            id={id}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="border-t border-border px-4 pt-4 pb-5">
              <p className="text-sm text-muted">
                A regra de hoje pode estar espalhada em mais de um ato: a lei cria a regra, outra lei pode mudar o texto e
                o decreto da Prefeitura detalha como aplicar (prazo, valor, documento), sem poder contrariar a lei.
              </p>

              {alertas.length > 0 && (
                <ul className="mt-4 grid gap-2">
                  {alertas.map((a) => (
                    <li key={a} className="flex gap-2 rounded-lg border border-warn/30 bg-warn-soft px-3 py-2 text-sm text-text">
                      <TriangleAlert aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-warn" />
                      <span>{a}</span>
                    </li>
                  ))}
                </ul>
              )}

              <ol className="relative mt-5 grid gap-5">
                {camadas.map((c, i) => {
                  const Icone = ICONE[c.papel] ?? FileText;
                  const situacaoLei = c.situacao && c.situacao in SITUACAO ? (c.situacao as Situacao) : null;
                  return (
                    <li key={`${c.papel}-${c.titulo}`} className="relative grid grid-cols-[2rem_1fr] gap-3">
                      {i < camadas.length - 1 && (
                        <span aria-hidden="true" className="absolute top-9 bottom-[-1.25rem] left-4 w-px bg-border" />
                      )}
                      <span
                        aria-hidden="true"
                        className={`flex size-8 items-center justify-center rounded-full ${
                          c.papel === "eficacia_suspensa_por" ? "bg-danger-soft text-danger" : "bg-primary-soft text-primary"
                        }`}
                      >
                        <Icone className="size-4" />
                      </span>
                      <div className="min-w-0">
                        <p className="text-xs font-semibold tracking-wide text-muted uppercase">{c.descricao}</p>
                        <div className="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-1">
                          <TituloCamada camada={c} rota={rota} />
                          {(c.artigo || c.dispositivo) && (
                            <span className="text-sm text-muted">· {c.artigo ?? `anotado no ${c.dispositivo}`}</span>
                          )}
                          {situacaoLei && <StatusBadge situacao={situacaoLei} />}
                          {!c.texto_na_base && (
                            <span className="rounded-full border border-border px-2 py-0.5 text-xs text-muted">
                              texto ainda fora da base
                            </span>
                          )}
                        </div>
                        {c.ementa && <p className="mt-1 line-clamp-2 text-sm text-muted">{c.ementa}</p>}
                        {c.trecho && (
                          <blockquote className="mt-2 border-l-4 border-primary/40 pl-3 text-sm">“{c.trecho}”</blockquote>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ol>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}

function TituloCamada({ camada, rota }: { camada: Camada; rota: (caminho: string) => string }) {
  if (camada.lei_id) {
    return (
      <Link to={rota(`/lei/${camada.lei_id}`)} className="group inline-flex items-center gap-1 font-semibold text-primary">
        {camada.titulo}
        <ArrowRight aria-hidden="true" className="size-4 transition group-hover:translate-x-0.5" />
      </Link>
    );
  }
  if (camada.link) {
    return (
      <a
        href={camada.link}
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center gap-1 font-semibold text-primary underline-offset-4 hover:underline"
      >
        {camada.titulo}
        <ExternalLink aria-hidden="true" className="size-3.5" />
        <span className="sr-only">(abre em nova aba)</span>
      </a>
    );
  }
  return <span className="font-semibold">{camada.titulo}</span>;
}
