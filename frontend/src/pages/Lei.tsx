import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ArrowRight, ChevronDown, ExternalLink, FlaskConical, GitCompareArrows, Volume2, Square } from "lucide-react";
import { obterLei } from "../api/client";
import type { DecretoDaLei, Lei as TLei, Relacao } from "../api/types";
import { StatusBadge } from "../components/StatusBadge";
import { useRota } from "../lib/rota";
import { RELACAO, SITUACAO, dataLegivel, ementaLimpa, nomeLei, numeroLegivel } from "../lib/leis";
import { useOuvir } from "../lib/fala";
import { Equalizador, Esqueleto } from "../components/Animacoes";

export function Lei() {
  const { id = "" } = useParams();
  const [lei, setLei] = useState<TLei | null | undefined>(undefined);
  const [abrirTexto, setAbrirTexto] = useState(false);
  const voz = useOuvir();
  const rota = useRota();

  useEffect(() => {
    setLei(undefined);
    setAbrirTexto(false);
    obterLei(id).then(setLei);
  }, [id]);

  if (lei === undefined) {
    return (
      <div className="mx-auto max-w-3xl px-4 pt-10 pb-20 sm:px-6" role="status">
        <span className="sr-only">Carregando a lei...</span>
        <Esqueleto className="mb-6 h-4 w-16" />
        <div className="flex gap-3">
          <Esqueleto className="h-9 w-36 rounded-full" />
          <Esqueleto className="h-9 w-24" />
        </div>
        <Esqueleto className="mt-5 h-10 w-64" />
        <Esqueleto className="mt-4 h-6 w-full" />
        <Esqueleto className="mt-2 h-6 w-3/4" />
        <Esqueleto className="mt-8 h-24 w-full rounded-2xl" />
      </div>
    );
  }
  if (lei === null) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="text-2xl font-bold">Lei não encontrada</h1>
        <p className="mt-2 text-muted">Ela pode não estar na base ainda. Tente procurar pelo número.</p>
        <Link to={rota("/leis")} className="mt-6 inline-flex items-center gap-2 font-medium text-primary">
          <ArrowLeft aria-hidden="true" className="size-4" /> Buscar leis
        </Link>
      </div>
    );
  }

  const s = SITUACAO[lei.situacao];
  const resumo = ementaLimpa(lei.ementa);
  const revogadaPor = lei.relacoes.filter((r) => r.tipo === "revogada_por");
  // Pares para a tela "O que mudou": esta lei com a que a substituiu, ou com a antiga que ela revogou
  const comparacoes = [
    ...revogadaPor.filter((r) => r.id).map((r) => ({ antiga: lei.id, nova: r.id!, texto: `Ver o que mudou na Lei ${numeroLegivel(r.chave)}` })),
    ...lei.relacoes
      .filter((r) => r.tipo === "revoga" && r.id)
      .map((r) => ({ antiga: r.id!, nova: lei.id, texto: `Comparar com a lei antiga (Lei ${numeroLegivel(r.chave)})` })),
  ];

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="mx-auto max-w-3xl px-4 pt-10 pb-20 sm:px-6"
    >
      <button
        type="button"
        onClick={() => history.back()}
        className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-muted hover:text-primary"
      >
        <ArrowLeft aria-hidden="true" className="size-4" /> Voltar
      </button>

      <div className="flex flex-wrap items-center gap-3">
        <StatusBadge situacao={lei.situacao} grande />
        <span className="text-sm text-muted">{dataLegivel(lei.data_lei, lei.ano)}</span>
      </div>

      <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">{nomeLei(lei.chave, lei.ano)}</h1>
      <p className="mt-3 text-xl leading-relaxed">{resumo}</p>
      {lei.vigencia_verificada === false && (
        <p className="mt-3 text-sm text-muted">Consulta documental: situação informada pela Câmara. Revisão institucional de vigência pendente.</p>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        {voz.suportado && (
          <button
            type="button"
            onClick={() =>
              voz.falando ? voz.parar() : voz.ouvir(`${nomeLei(lei.chave, lei.ano)}. ${s.rotulo}. ${resumo}`)
            }
            className="inline-flex items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-sm font-medium text-primary hover:bg-primary-soft"
          >
            {voz.falando ? (
              <>
                <Square aria-hidden="true" className="size-4" />
                <Equalizador className="h-3.5" />
                Parar
              </>
            ) : (
              <>
                <Volume2 aria-hidden="true" className="size-4" />
                Ouvir
              </>
            )}
          </button>
        )}
        {lei.link && (
          <a
            href={lei.link}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-sm font-medium text-primary hover:bg-primary-soft"
          >
            Ver no site da Câmara <ExternalLink aria-hidden="true" className="size-4" />
            <span className="sr-only">(abre em nova aba)</span>
          </a>
        )}
      </div>

      {lei.exemplo && (
        <p className="mt-4 flex items-center gap-2 rounded-xl border border-warn/30 bg-warn-soft px-4 py-2 text-sm text-warn">
          <FlaskConical aria-hidden="true" className="size-4 shrink-0" />
          Lei de exemplo, inventada para demonstração. Não existe no site da Câmara.
        </p>
      )}

      {/* Aviso principal: a coisa mais importante para o cidadão */}
      <div className={`mt-8 rounded-2xl border p-5 ${s.classes}`}>
        <p className="font-semibold">{s.explicacao}</p>
        {lei.situacao === "revogada" && revogadaPor.length > 0 && (
          <p className="mt-1 text-text">
            Consulte a lei que vale hoje:{" "}
            {revogadaPor.map((r, i) => (
              <span key={r.chave}>
                {i > 0 && ", "}
                <LinkLei r={r} />
              </span>
            ))}
          </p>
        )}
        {comparacoes.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {comparacoes.map((c) => (
              <Link
                key={c.antiga + c.nova}
                to={rota(`/comparar/${c.antiga}/${c.nova}`)}
                className="inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-sm font-semibold text-on-primary hover:bg-primary-strong"
              >
                <GitCompareArrows aria-hidden="true" className="size-4" /> {c.texto}
              </Link>
            ))}
          </div>
        )}
      </div>

      {lei.relacoes.length > 0 && (
        <section className="mt-10">
          <h2 className="text-lg font-semibold">Histórico desta lei</h2>
          <motion.ol
            className="relative mt-4 grid gap-0"
            initial="oculto"
            whileInView="visivel"
            viewport={{ once: true, margin: "0px 0px -15% 0px" }}
          >
            {lei.relacoes.length > 1 && (
              <motion.span
                aria-hidden="true"
                className="absolute top-3 bottom-6 left-[0.6875rem] w-0.5 origin-top bg-border"
                variants={{ oculto: { scaleY: 0 }, visivel: { scaleY: 1, transition: { duration: 0.3 * lei.relacoes.length, ease: "easeInOut" } } }}
              />
            )}
            {lei.relacoes.map((r, i) => (
              <motion.li
                key={`${r.tipo}-${r.chave}`}
                className="relative flex gap-4 pb-6 last:pb-0"
                variants={{
                  oculto: { opacity: 0, x: -8 },
                  visivel: { opacity: 1, x: 0, transition: { duration: 0.3, delay: 0.1 + i * 0.3 } },
                }}
              >
                <motion.span
                  variants={{
                    oculto: { scale: 0 },
                    visivel: { scale: 1, transition: { type: "spring", stiffness: 420, damping: 18, delay: 0.1 + i * 0.3 } },
                  }}
                  aria-hidden="true"
                  className={`relative mt-1 size-6 shrink-0 rounded-full border-4 border-surface ${
                    r.tipo === "revogada_por" ? "bg-danger" : r.tipo === "alterada_por" ? "bg-warn" : "bg-primary"
                  }`}
                />
                <div>
                  <p className="text-sm text-muted">{RELACAO[r.tipo]}</p>
                  <p className="font-semibold">
                    <LinkLei r={r} />
                  </p>
                </div>
              </motion.li>
            ))}
          </motion.ol>
        </section>
      )}

      {lei.decretos && lei.decretos.length > 0 && <DecretosDaLei decretos={lei.decretos} />}

      <section className="mt-10 border-t border-border pt-6">
        <button
          type="button"
          onClick={() => setAbrirTexto((v) => !v)}
          aria-expanded={abrirTexto}
          aria-controls="texto-lei"
          className="flex w-full items-center justify-between gap-4 rounded-lg py-2 text-left text-lg font-semibold"
        >
          Texto completo ({lei.artigos.length} {lei.artigos.length === 1 ? "artigo" : "artigos"})
          <ChevronDown aria-hidden="true" className={`size-5 transition ${abrirTexto ? "rotate-180" : ""}`} />
        </button>
        <AnimatePresence initial={false}>
        {abrirTexto && (
          <motion.ol
            id="texto-lei"
            className="grid gap-4 overflow-hidden pt-4"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            {lei.artigos.map((a) => (
              <li key={a.ordem} className="leading-relaxed">
                <strong>{a.artigo}</strong> {a.revogado ? "Revogado." : a.texto.replace(/^Art\.\s*\d+[º°o]?\.?\s*/, "")}
                {a.texto_riscado && (
                  <details className="mt-1 text-sm text-muted">
                    <summary className="cursor-pointer">Redação anterior — histórico</summary>
                    <p className="mt-2"><s>{a.texto_riscado}</s></p>
                  </details>
                )}
              </li>
            ))}
          </motion.ol>
        )}
        </AnimatePresence>
        <p className="mt-4 text-sm text-muted">Título oficial: {lei.titulo}</p>
      </section>
    </motion.article>
  );
}

function LinkLei({ r }: { r: Relacao }) {
  const rota = useRota();
  const texto = `Lei ${numeroLegivel(r.chave)}`;
  if (!r.id) return <span>{texto}</span>;
  return (
    <Link to={rota(`/lei/${r.id}`)} className="inline-flex items-center gap-1 text-primary underline-offset-4 hover:underline">
      {texto}
      <ArrowRight aria-hidden="true" className="size-4" />
    </Link>
  );
}

const VINCULO: Record<DecretoDaLei["vinculo"], string> = {
  regulamentada_por: "Regulamenta esta lei",
  anexo_atualizado_por: "Atualizou um anexo",
  eficacia_suspensa_por: "Suspendeu a eficácia",
};

/** Decretos citados pela Câmara ou pela súmula do próprio decreto. Os revogados ficam no fim, riscados. */
function DecretosDaLei({ decretos }: { decretos: DecretoDaLei[] }) {
  const ordenados = [...decretos].sort((a, b) => Number(a.situacao === "revogado") - Number(b.situacao === "revogado"));
  return (
    <section className="mt-10">
      <h2 className="text-lg font-semibold">Decretos ligados a esta lei</h2>
      <p className="mt-1 text-sm text-muted">
        O decreto da Prefeitura detalha como aplicar a lei (prazos, valores, documentos), sem poder contrariá-la. O
        decreto legislativo da Câmara pode suspender a eficácia de uma lei.
      </p>
      <ul className="mt-4 grid gap-3">
        {ordenados.map((d) => {
          const revogado = d.situacao === "revogado";
          return (
            <li key={`${d.id}-${d.vinculo}`} className="rounded-xl bg-bg p-4">
              <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                {d.link && !revogado ? (
                  <a
                    href={d.link}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 font-semibold text-primary underline-offset-4 hover:underline"
                  >
                    {d.titulo}
                    <ExternalLink aria-hidden="true" className="size-3.5" />
                    <span className="sr-only">(abre em nova aba)</span>
                  </a>
                ) : (
                  <span className={`font-semibold ${revogado ? "text-muted line-through" : ""}`}>{d.titulo}</span>
                )}
                <span className="text-sm text-muted">· {VINCULO[d.vinculo]}</span>
                {d.dispositivos.length > 0 && (
                  <span className="text-sm text-muted">· {d.dispositivos.slice(0, 4).join(", ")}{d.dispositivos.length > 4 ? "…" : ""}</span>
                )}
              </div>
              {d.ementa && <p className="mt-1 text-sm text-muted">{d.ementa}</p>}
              <p className="mt-1 text-xs text-muted">
                {revogado
                  ? `Revogado${d.revogado_por ? ` pelo ${d.revogado_por}` : ""}.`
                  : d.texto_disponivel
                    ? "Texto incluído na base: o chat usa este decreto nas respostas."
                    : "Citado pela Câmara; o texto ainda não está na base."}
              </p>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
