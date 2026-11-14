// "O que mudou": compara uma lei antiga com a lei que a substituiu.
// A) Mudanças nas regras: artigo por artigo, palavra por palavra.
// B) Mudanças no jeito de escrever: o padrão da LC 95/1998 em cada uma.
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowRight, CircleCheck, CircleX, Columns2, FlaskConical, Rows3, ShieldCheck, TriangleAlert } from "lucide-react";
import { obterLei } from "../api/client";
import type { Lei } from "../api/types";
import { StatusBadge } from "../components/StatusBadge";
import { Contador, Esqueleto } from "../components/Animacoes";
import { compararLeis, padraoDaLei, type ItemComparacao, type Pedaco, type TipoMudanca } from "../lib/comparar";
import { dataLegivel, ementaLimpa, nomeLei, numeroLegivel } from "../lib/leis";
import { useRota } from "../lib/rota";
import type { Problema, Resultado } from "../validador/regras";

const TIPOS: Record<TipoMudanca, { rotulo: string; plural: string; classes: string; ponto: string }> = {
  alterado: { rotulo: "Alterado", plural: "alterados", classes: "bg-warn-soft text-warn border-warn/30", ponto: "bg-warn" },
  novo: { rotulo: "Novo", plural: "novos", classes: "bg-ok-soft text-ok border-ok/30", ponto: "bg-ok" },
  removido: { rotulo: "Saiu", plural: "saíram", classes: "bg-danger-soft text-danger border-danger/30", ponto: "bg-danger" },
  igual: { rotulo: "Sem mudança", plural: "sem mudança", classes: "bg-bg text-muted border-border", ponto: "bg-border" },
};

const FILTROS: (TipoMudanca | "mudancas" | "todos")[] = ["mudancas", "alterado", "novo", "removido", "todos"];

export function Comparar() {
  const { antiga: idAntiga = "exemplo-1980", nova: idNova = "exemplo-2026" } = useParams();
  const rota = useRota();
  const [leis, setLeis] = useState<[Lei | null, Lei | null] | null>(null);
  const [aba, setAba] = useState<"regras" | "escrita">("regras");

  useEffect(() => {
    setLeis(null);
    Promise.all([obterLei(idAntiga), obterLei(idNova)]).then(([a, n]) => setLeis([a, n]));
  }, [idAntiga, idNova]);

  if (!leis) {
    return (
      <div className="mx-auto max-w-5xl px-4 pt-10 sm:px-6" role="status">
        <span className="sr-only">Carregando as leis...</span>
        <Esqueleto className="h-10 w-72" />
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <Esqueleto className="h-40 rounded-2xl" />
          <Esqueleto className="h-40 rounded-2xl" />
        </div>
      </div>
    );
  }
  const [antiga, nova] = leis;
  if (!antiga || !nova) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="text-2xl font-bold">Não encontramos as duas leis para comparar</h1>
        <Link to={rota("/leis")} className="mt-4 inline-flex items-center gap-2 font-medium text-primary">
          Buscar leis <ArrowRight aria-hidden="true" className="size-4" />
        </Link>
      </div>
    );
  }

  const comparacao = compararLeis(antiga, nova);
  const exemplo = antiga.exemplo || nova.exemplo;

  return (
    <div className="mx-auto max-w-5xl px-4 pt-8 pb-20 sm:px-6">
      {exemplo && (
        <p className="mb-5 flex items-center gap-2 rounded-xl border border-warn/30 bg-warn-soft px-4 py-2 text-sm text-warn">
          <FlaskConical aria-hidden="true" className="size-4 shrink-0" />
          Leis de exemplo, inventadas para demonstrar esta tela. Não existem no site da Câmara.
        </p>
      )}

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
        <p className="text-sm font-semibold tracking-wide text-primary uppercase">Histórico de alteração</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">O que mudou</h1>
        <p className="mt-2 text-lg text-muted">{ementaLimpa(nova.ementa)}</p>
      </motion.div>

      {/* As duas leis, lado a lado */}
      <div className="mt-6 grid items-stretch gap-3 sm:grid-cols-[1fr_auto_1fr]">
        <CartaoLei lei={antiga} papel="Lei antiga" atraso={0} />
        <motion.span
          aria-hidden="true"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.35 }}
          className="grid place-items-center text-primary"
        >
          <span className="grid size-10 rotate-90 place-items-center rounded-full bg-primary-soft sm:rotate-0">
            <ArrowRight className="size-5" />
          </span>
        </motion.span>
        <CartaoLei lei={nova} papel="Lei que vale hoje" atraso={0.2} />
      </div>

      <LinhaDoTempo antiga={antiga} nova={nova} />

      {/* Abas: A (regras) e B (escrita) */}
      <div role="tablist" aria-label="Tipo de mudança" className="mt-8 flex gap-1 rounded-2xl border border-border bg-surface p-1">
        {(
          [
            ["regras", "O que mudou nas regras"],
            ["escrita", "O que mudou no jeito de escrever"],
          ] as const
        ).map(([id, rotulo]) => (
          <button
            key={id}
            role="tab"
            id={`aba-${id}`}
            aria-selected={aba === id}
            aria-controls={`painel-${id}`}
            onClick={() => setAba(id)}
            className={`relative flex-1 rounded-xl px-3 py-2.5 text-sm font-semibold transition-colors sm:text-base ${
              aba === id ? "text-on-primary" : "text-muted hover:text-text"
            }`}
          >
            {aba === id && (
              <motion.span layoutId="aba-ativa" aria-hidden="true" className="absolute inset-0 rounded-xl bg-primary" transition={{ type: "spring", stiffness: 400, damping: 34 }} />
            )}
            <span className="relative">{rotulo}</span>
          </button>
        ))}
      </div>

      <div role="tabpanel" id={`painel-${aba}`} aria-labelledby={`aba-${aba}`} className="mt-6">
        {aba === "regras" ? (
          comparacao.temTexto ? (
            <MudancasNasRegras itens={comparacao.itens} contagem={comparacao.contagem} antiga={antiga} nova={nova} />
          ) : (
            <SemTexto />
          )
        ) : (
          <MudancasNaEscrita antiga={antiga} nova={nova} />
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------- Cabeçalho

function CartaoLei({ lei, papel, atraso }: { lei: Lei; papel: string; atraso: number }) {
  const rota = useRota();
  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: atraso }}
      className="rounded-2xl border border-border bg-surface p-5 shadow-card"
    >
      <p className="text-xs font-semibold tracking-wide text-muted uppercase">{papel}</p>
      <p className="mt-1 text-5xl font-black tracking-tight text-primary">{lei.ano}</p>
      <Link to={rota(`/lei/${lei.id}`)} className="mt-1 inline-flex items-center gap-1 font-bold hover:underline">
        {nomeLei(lei.chave, lei.ano)} <ArrowRight aria-hidden="true" className="size-4" />
      </Link>
      <div className="mt-2">
        <StatusBadge situacao={lei.situacao} />
      </div>
      <p className="mt-2 text-sm text-muted">{ementaLimpa(lei.ementa)}</p>
    </motion.article>
  );
}

function LinhaDoTempo({ antiga, nova }: { antiga: Lei; nova: Lei }) {
  const alteracoes = antiga.relacoes.filter((r) => r.tipo === "alterada_por");
  const marcos = [
    { quando: antiga.ano, texto: `Criada a ${nomeLei(antiga.chave, antiga.ano)}`, cor: "bg-primary" },
    ...alteracoes.map((r) => ({ quando: "", texto: `Alterada pela Lei ${numeroLegivel(r.chave)}`, cor: "bg-warn" })),
    { quando: nova.ano, texto: `Substituída pela ${nomeLei(nova.chave, nova.ano)}`, cor: "bg-danger" },
  ];
  return (
    <section aria-label="Linha do tempo" className="mt-6 rounded-2xl border border-border bg-surface p-5 shadow-card">
      <h2 className="mb-4 text-sm font-semibold tracking-wide text-muted uppercase">Linha do tempo</h2>
      <ol className="relative grid gap-4 sm:grid-flow-col sm:gap-2" style={{ gridAutoColumns: "1fr" }}>
        <motion.span
          aria-hidden="true"
          className="absolute top-3 right-[8%] left-[8%] hidden h-0.5 origin-left bg-border sm:block"
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 0.9, delay: 0.3, ease: "easeInOut" }}
        />
        {marcos.map((m, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + i * 0.3 }}
            className="relative flex items-center gap-3 sm:flex-col sm:text-center"
          >
            <span className={`relative size-6 shrink-0 rounded-full border-4 border-surface ${m.cor}`} aria-hidden="true" />
            <span>
              {m.quando && <span className="block text-lg font-black">{m.quando}</span>}
              <span className="block text-sm text-muted">{m.texto}</span>
            </span>
          </motion.li>
        ))}
      </ol>
    </section>
  );
}

function SemTexto() {
  return (
    <p className="rounded-2xl border border-border bg-surface p-5 text-muted">
      O texto completo destas leis ainda não está na base. Quando o front estiver ligado ao banco de leis, a comparação artigo por
      artigo aparece aqui.
    </p>
  );
}

// ---------------------------------------------------------------- A) Mudanças nas regras

function MudancasNasRegras({
  itens,
  contagem,
  antiga,
  nova,
}: {
  itens: ItemComparacao[];
  contagem: Record<TipoMudanca, number>;
  antiga: Lei;
  nova: Lei;
}) {
  const [filtro, setFiltro] = useState<(typeof FILTROS)[number]>("mudancas");
  const [ladoALado, setLadoALado] = useState(false);
  const visiveis = itens.filter((it) =>
    filtro === "todos" ? true : filtro === "mudancas" ? it.tipo !== "igual" : it.tipo === filtro,
  );
  const rotuloFiltro = (f: (typeof FILTROS)[number]) =>
    f === "todos" ? `Todos (${itens.length})` : f === "mudancas" ? `Só o que mudou (${itens.length - contagem.igual})` : `${TIPOS[f].rotulo} (${contagem[f]})`;

  return (
    <div>
      {/* Resumo com números animados */}
      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {(["alterado", "novo", "removido", "igual"] as TipoMudanca[]).map((t) => (
          <div key={t} className={`rounded-2xl border p-4 ${TIPOS[t].classes}`}>
            <dd className="text-3xl font-black">
              <Contador valor={contagem[t]} duracao={0.8} />
            </dd>
            <dt className="text-sm font-semibold">
              {contagem[t] === 1 ? "artigo" : "artigos"} {t === "removido" ? (contagem[t] === 1 ? "saiu" : "saíram") : t === "igual" ? "sem mudança" : contagem[t] === 1 ? TIPOS[t].plural.replace(/s$/, "") : TIPOS[t].plural}
            </dt>
          </div>
        ))}
      </dl>

      <div className="mt-5 flex flex-wrap items-center gap-2">
        <fieldset className="flex flex-wrap gap-2">
          <legend className="sr-only">Mostrar</legend>
          {FILTROS.map((f) => (
            <label key={f} className="cursor-pointer">
              <input type="radio" name="filtro-mudanca" className="peer sr-only" checked={filtro === f} onChange={() => setFiltro(f)} />
              <span className="relative inline-block rounded-full border border-border bg-surface px-3.5 py-1.5 text-sm font-medium text-muted transition-colors peer-checked:border-primary peer-checked:text-primary-strong peer-focus-visible:outline-3 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-[var(--focus)]">
                {filtro === f && (
                  <motion.span layoutId="filtro-mudanca" aria-hidden="true" className="absolute inset-0 rounded-full bg-primary-soft" transition={{ type: "spring", stiffness: 420, damping: 34 }} />
                )}
                <span className="relative">{rotuloFiltro(f)}</span>
              </span>
            </label>
          ))}
        </fieldset>
        <button
          type="button"
          onClick={() => setLadoALado((v) => !v)}
          aria-pressed={ladoALado}
          className="ml-auto inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3.5 py-1.5 text-sm font-medium text-primary hover:bg-primary-soft"
        >
          {ladoALado ? <Rows3 aria-hidden="true" className="size-4" /> : <Columns2 aria-hidden="true" className="size-4" />}
          {ladoALado ? "Ver junto" : "Ver lado a lado"}
        </button>
      </div>

      <p className="mt-4 flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted">
        <span>
          <del className="rounded bg-danger-soft px-1 text-danger">texto riscado</del> = saiu da lei de {antiga.ano}
        </span>
        <span>
          <ins className="rounded bg-ok-soft px-1 text-ok no-underline">texto verde</ins> = entrou na lei de {nova.ano}
        </span>
      </p>

      <motion.ol layout className="mt-4 grid gap-3">
        <AnimatePresence initial={false} mode="popLayout">
          {visiveis.map((it, i) => (
            <motion.li
              key={`${it.antigo?.rotulo ?? ""}>${it.novo?.rotulo ?? ""}`}
              layout
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0, transition: { duration: 0.3, delay: Math.min(i, 10) * 0.06 } }}
              exit={{ opacity: 0, transition: { duration: 0.15 } }}
            >
              <CartaoMudanca item={it} ladoALado={ladoALado} anoAntigo={antiga.ano} anoNovo={nova.ano} />
            </motion.li>
          ))}
        </AnimatePresence>
      </motion.ol>
    </div>
  );
}

function CartaoMudanca({ item, ladoALado, anoAntigo, anoNovo }: { item: ItemComparacao; ladoALado: boolean; anoAntigo: string; anoNovo: string }) {
  const t = TIPOS[item.tipo];
  const rotulo = item.novo?.rotulo ?? item.antigo?.rotulo ?? "";
  return (
    <article className="rounded-2xl border border-border bg-surface p-4 shadow-card sm:p-5">
      <header className="mb-2 flex flex-wrap items-center gap-2">
        <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-bold ${t.classes}`}>
          <span aria-hidden="true" className={`size-2 rounded-full ${t.ponto}`} />
          {t.rotulo}
        </span>
        <h3 className="font-bold">{rotulo}</h3>
        {item.renumerado && item.antigo && <span className="text-sm text-muted">(era o {item.antigo.rotulo})</span>}
      </header>

      {item.tipo === "novo" && item.novo && (
        <p className="leading-relaxed">
          <ins className="rounded bg-ok-soft px-1 text-ok no-underline">
            <span className="sr-only">Entrou: </span>
            {item.novo.corpo}
          </ins>
        </p>
      )}
      {item.tipo === "removido" && item.antigo && (
        <p className="leading-relaxed">
          <del className="rounded bg-danger-soft px-1 text-danger">
            <span className="sr-only">Saiu: </span>
            {item.antigo.corpo}
          </del>
        </p>
      )}
      {item.tipo === "igual" && item.novo && <p className="leading-relaxed text-muted">{item.novo.corpo}</p>}

      {item.tipo === "alterado" && item.pedacos && (
        ladoALado ? (
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl bg-bg p-3">
              <p className="mb-1 text-xs font-semibold text-muted uppercase">Como era em {anoAntigo}</p>
              <Pedacos pedacos={item.pedacos} lado="antes" />
            </div>
            <div className="rounded-xl bg-bg p-3">
              <p className="mb-1 text-xs font-semibold text-muted uppercase">Como ficou em {anoNovo}</p>
              <Pedacos pedacos={item.pedacos} lado="depois" />
            </div>
          </div>
        ) : (
          <Pedacos pedacos={item.pedacos} lado="junto" />
        )
      )}
    </article>
  );
}

function Pedacos({ pedacos, lado }: { pedacos: Pedaco[]; lado: "antes" | "depois" | "junto" }) {
  return (
    <p className="leading-relaxed">
      {pedacos.map((p, i) => {
        if (p.tipo === "igual") return <span key={i}>{p.texto} </span>;
        if (p.tipo === "saiu" && lado !== "depois")
          return (
            <span key={i}>
              <motion.del
                initial={{ backgroundColor: "rgba(0,0,0,0)" }}
                animate={{ backgroundColor: "var(--danger-soft)" }}
                transition={{ delay: 0.2 + i * 0.05 }}
                className="rounded px-0.5 text-danger"
              >
                <span className="sr-only">[saiu: </span>
                {p.texto}
                <span className="sr-only">]</span>
              </motion.del>{" "}
            </span>
          );
        if (p.tipo === "entrou" && lado !== "antes")
          return (
            <span key={i}>
              <motion.ins
                initial={{ backgroundColor: "rgba(0,0,0,0)" }}
                animate={{ backgroundColor: "var(--ok-soft)" }}
                transition={{ delay: 0.3 + i * 0.05 }}
                className="rounded px-0.5 font-medium text-ok no-underline"
              >
                <span className="sr-only">[entrou: </span>
                {p.texto}
                <span className="sr-only">]</span>
              </motion.ins>{" "}
            </span>
          );
        return null;
      })}
    </p>
  );
}

// ---------------------------------------------------------------- B) Mudanças no jeito de escrever

function MudancasNaEscrita({ antiga, nova }: { antiga: Lei; nova: Lei }) {
  const rAntiga = padraoDaLei(antiga);
  const rNova = padraoDaLei(nova);
  if (!rAntiga || !rNova) return <SemTexto />;

  return (
    <div>
      <p className="max-w-3xl text-muted">
        Desde 1998, a <strong className="text-text">Lei Complementar 95</strong> define como as leis devem ser escritas: título, data,
        numeração dos artigos, cláusula de revogação. Leis mais antigas seguiam outros costumes. Veja como cada uma se sai nas mesmas
        regras do <strong className="text-text">Validador de Leis</strong>.
      </p>

      {/* Título antes e depois: o exemplo mais visível */}
      <div className="mt-5 grid gap-2 rounded-2xl border border-border bg-surface p-4 shadow-card sm:grid-cols-[auto_1fr] sm:gap-x-4">
        <span className="text-xs font-semibold text-muted uppercase sm:pt-1">Título em {antiga.ano}</span>
        <span className="font-serif text-lg">{antiga.titulo}</span>
        <span className="text-xs font-semibold text-muted uppercase sm:pt-1">Título em {nova.ano}</span>
        <span className="font-serif text-lg font-bold">{nova.titulo}</span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <ColunaPadrao lei={antiga} resultado={rAntiga} atraso={0} />
        <ColunaPadrao lei={nova} resultado={rNova} atraso={0.25} />
      </div>
    </div>
  );
}

function ColunaPadrao({ lei, resultado, atraso }: { lei: Lei; resultado: Resultado; atraso: number }) {
  const problemas: (Problema & { base: string })[] = resultado.checagens.flatMap((c) => c.problemas.map((p) => ({ ...p, base: c.base })));
  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: atraso, duration: 0.35 }}
      className="rounded-2xl border border-border bg-surface p-4 shadow-card"
      aria-label={`Padrão de escrita da lei de ${lei.ano}`}
    >
      <p className="text-xs font-semibold tracking-wide text-muted uppercase">
        {nomeLei(lei.chave, lei.ano)}
        {lei.data_lei && <> · {dataLegivel(lei.data_lei, lei.ano)}</>}
      </p>
      <div className={`mt-2 flex items-center gap-3 rounded-xl p-3 ${resultado.conforme ? "bg-ok-soft text-ok" : "bg-danger-soft text-danger"}`}>
        {resultado.conforme ? <ShieldCheck aria-hidden="true" className="size-7 shrink-0" /> : <CircleX aria-hidden="true" className="size-7 shrink-0" />}
        <div>
          <p className="font-black">{resultado.conforme ? "Segue o padrão atual" : "Fora do padrão atual"}</p>
          <p className="text-sm font-medium text-text">
            {resultado.erros} {resultado.erros === 1 ? "erro" : "erros"} · {resultado.avisos} {resultado.avisos === 1 ? "aviso" : "avisos"}
          </p>
        </div>
      </div>

      <ul className="mt-3 grid gap-1">
        {resultado.checagens.map((c, i) => {
          const erros = c.problemas.filter((p) => p.gravidade === "erro").length;
          const avisos = c.problemas.length - erros;
          return (
            <motion.li
              key={c.id}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: atraso + 0.2 + i * 0.08 }}
              className="flex items-center gap-2 text-sm"
            >
              {erros ? (
                <CircleX aria-hidden="true" className="size-4 shrink-0 text-danger" />
              ) : avisos ? (
                <TriangleAlert aria-hidden="true" className="size-4 shrink-0 text-warn" />
              ) : (
                <CircleCheck aria-hidden="true" className="size-4 shrink-0 text-ok" />
              )}
              <span className="flex-1">{c.nome}</span>
              <span className={`text-xs font-semibold ${erros ? "text-danger" : avisos ? "text-warn" : "text-ok"}`}>
                {erros ? `${erros} ${erros === 1 ? "erro" : "erros"}` : avisos ? `${avisos} ${avisos === 1 ? "aviso" : "avisos"}` : "ok"}
              </span>
            </motion.li>
          );
        })}
      </ul>

      {problemas.length > 0 && (
        <details className="mt-3 rounded-xl border border-border p-3 text-sm" open={problemas.length <= 4}>
          <summary className="cursor-pointer font-semibold">Ver os {problemas.length} pontos fora do padrão</summary>
          <ul className="mt-2 grid gap-3">
            {problemas.map((p, i) => (
              <li key={i}>
                <p className="font-medium">{p.titulo}</p>
                {p.encontrado && (
                  <p>
                    <del className="rounded bg-danger-soft px-1 text-danger">{p.encontrado}</del>
                  </p>
                )}
                {p.esperado && (
                  <p>
                    → <span className="rounded bg-ok-soft px-1 text-ok">{p.esperado}</span>
                  </p>
                )}
                <p className="text-xs text-muted">{p.base}</p>
              </li>
            ))}
          </ul>
        </details>
      )}
    </motion.section>
  );
}
