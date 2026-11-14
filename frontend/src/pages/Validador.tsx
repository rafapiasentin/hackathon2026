// Validador de leis: a pessoa envia um PDF (com texto ou escaneado), uma imagem ou um XML,
// o sistema lê o documento e confere as regras de redação da LC 95/1998.
// Com ?apresentacao=1 (ou o botão "Apresentação"), roda os exemplos um a um para o pitch.
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useCallback, useEffect, useRef, useState, type DragEvent } from "react";
import { useSearchParams } from "react-router-dom";
import {
  ArrowRight,
  CircleCheck,
  CircleX,
  ExternalLink,
  FileCode,
  FileText,
  Loader2,
  MonitorPlay,
  ScanText,
  ShieldCheck,
  TriangleAlert,
  Upload,
  X,
} from "lucide-react";
import { lerArquivo, type Documento, type Etapa } from "../validador/leitura";
import { validar, type Checagem, type Problema, type Resultado } from "../validador/regras";

const EXEMPLOS = [
  {
    arquivo: "lei-fora-do-padrao.pdf",
    rotulo: "Lei fora do padrão",
    detalhe: "PDF com texto",
    legenda: "Título e data fora do padrão, artigos com erro e revogação genérica.",
  },
  {
    arquivo: "lei-escaneada.pdf",
    rotulo: "Lei escaneada",
    detalhe: "PDF de imagem (OCR)",
    legenda: "Um papel escaneado: o sistema reconhece o texto da imagem antes de conferir.",
  },
  {
    arquivo: "lei-codigo-ambiental.xml",
    rotulo: "Lei em XML",
    detalhe: "Padrão LexML",
    legenda: "O formato nacional de leis em XML: conferimos a estrutura e o texto.",
  },
  {
    arquivo: "lei-no-padrao.pdf",
    rotulo: "Lei no padrão",
    detalhe: "PDF com texto",
    legenda: "Uma lei escrita certinho: passa em todas as regras.",
  },
];

type Fase = "inicio" | "lendo" | "conferindo" | "pronto" | "falhou";

interface ProblemaNumerado extends Problema {
  n: number;
  base: string;
}

export function Validador() {
  const [params, setParams] = useSearchParams();
  const reduzir = useReducedMotion();
  const [fase, setFase] = useState<Fase>("inicio");
  const [nome, setNome] = useState("");
  const [etapa, setEtapa] = useState<Etapa | null>(null);
  const [doc, setDoc] = useState<Documento | null>(null);
  const [linhasVisiveis, setLinhasVisiveis] = useState(0);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [feitas, setFeitas] = useState(0);
  const [erroLeitura, setErroLeitura] = useState("");
  const [arrastando, setArrastando] = useState(false);
  const execucao = useRef(0);
  const entrada = useRef<HTMLInputElement>(null);

  const apresentacao = params.get("apresentacao") !== null ? Math.max(0, Number(params.get("apresentacao")) - 1 || 0) : null;
  const fator = reduzir ? 0 : apresentacao !== null ? 1.7 : 1;

  const processar = useCallback(
    async (arquivo: Blob, nomeArquivo: string) => {
      const minha = ++execucao.current;
      const cancelado = () => execucao.current !== minha;
      const pausa = (ms: number) => new Promise((ok) => setTimeout(ok, ms * fator));

      setFase("lendo");
      setNome(nomeArquivo);
      setEtapa({ texto: "Abrindo o arquivo" });
      setDoc(null);
      setResultado(null);
      setLinhasVisiveis(0);
      setFeitas(0);
      setErroLeitura("");

      let lido: Documento;
      try {
        const inicio = Date.now();
        lido = await lerArquivo(arquivo, nomeArquivo, (e) => !cancelado() && setEtapa(e));
        await pausa(Math.max(0, 600 - (Date.now() - inicio)));
      } catch (e) {
        if (cancelado()) return;
        setErroLeitura(e instanceof Error ? e.message : "Não consegui ler este arquivo.");
        setFase("falhou");
        return;
      }
      if (cancelado()) return;

      // A leitura: o texto aparece na folha, parágrafo por parágrafo
      setDoc(lido);
      for (let i = 1; i <= lido.paragrafos.length; i++) {
        setLinhasVisiveis(i);
        await pausa(110);
        if (cancelado()) return;
      }

      // O teste: cada regra é conferida, uma de cada vez
      setFase("conferindo");
      const r = validar(lido);
      setResultado(r);
      for (let i = 1; i <= r.checagens.length; i++) {
        await pausa(320);
        if (cancelado()) return;
        setFeitas(i);
      }
      await pausa(350);
      if (!cancelado()) setFase("pronto");
    },
    [fator],
  );

  const abrirExemplo = useCallback(
    async (arquivo: string) => {
      const r = await fetch(`/exemplos/${arquivo}`);
      processar(await r.blob(), arquivo);
    },
    [processar],
  );

  // Modo apresentação: cada número da URL é um exemplo
  useEffect(() => {
    if (apresentacao === null) return;
    abrirExemplo(EXEMPLOS[Math.min(apresentacao, EXEMPLOS.length - 1)].arquivo);
  }, [apresentacao, abrirExemplo]);

  const irPara = useCallback(
    (i: number | null) => {
      const p = new URLSearchParams(params);
      if (i === null) p.delete("apresentacao");
      else p.set("apresentacao", String(i + 1));
      setParams(p, { replace: true });
    },
    [params, setParams],
  );

  // Passador de slides e setas do teclado avançam a apresentação
  useEffect(() => {
    if (apresentacao === null) return;
    const tecla = (e: KeyboardEvent) => {
      if (["ArrowRight", "PageDown"].includes(e.key) && apresentacao < EXEMPLOS.length - 1) irPara(apresentacao + 1);
      if (["ArrowLeft", "PageUp"].includes(e.key) && apresentacao > 0) irPara(apresentacao - 1);
      if (e.key === "Escape") irPara(null);
    };
    window.addEventListener("keydown", tecla);
    return () => window.removeEventListener("keydown", tecla);
  }, [apresentacao, irPara]);

  function receber(arquivos: FileList | null) {
    const f = arquivos?.[0];
    if (!f) return;
    if (apresentacao !== null) irPara(null);
    processar(f, f.name);
  }

  function soltar(e: DragEvent) {
    e.preventDefault();
    setArrastando(false);
    receber(e.dataTransfer.files);
  }

  const problemas: ProblemaNumerado[] = resultado
    ? resultado.checagens
        .flatMap((c) => c.problemas.map((p) => ({ ...p, base: c.base })))
        .sort((a, b) => (a.linha ?? 9999) - (b.linha ?? 9999))
        .map((p, i) => ({ ...p, n: i + 1 }))
    : [];
  const porLinha = new Map<number, ProblemaNumerado[]>();
  for (const p of problemas) if (p.linha !== undefined) porLinha.set(p.linha, [...(porLinha.get(p.linha) ?? []), p]);

  const exemploAtual = apresentacao !== null ? EXEMPLOS[Math.min(apresentacao, EXEMPLOS.length - 1)] : null;

  return (
    <div className="mx-auto max-w-6xl px-4 pt-8 pb-20 sm:px-6">
      {/* Barra da apresentação */}
      <AnimatePresence>
        {exemploAtual && apresentacao !== null && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="sticky top-2 z-30 mb-6 flex flex-wrap items-center gap-3 rounded-2xl bg-text px-4 py-3 text-bg shadow-lg"
          >
            <MonitorPlay aria-hidden="true" className="size-5 shrink-0" />
            <p className="min-w-0 flex-1 text-sm">
              <span className="font-bold">
                Apresentação · {apresentacao + 1} de {EXEMPLOS.length}: {exemploAtual.rotulo}
              </span>{" "}
              <span className="opacity-80">({exemploAtual.detalhe}). {exemploAtual.legenda}</span>
            </p>
            <div className="flex gap-2">
              {apresentacao < EXEMPLOS.length - 1 && (
                <button
                  type="button"
                  onClick={() => irPara(apresentacao + 1)}
                  className="inline-flex items-center gap-1.5 rounded-full bg-bg px-4 py-1.5 text-sm font-bold text-text"
                >
                  Próximo <ArrowRight aria-hidden="true" className="size-4" />
                </button>
              )}
              <button
                type="button"
                onClick={() => irPara(null)}
                className="grid size-8 place-items-center rounded-full hover:bg-white/15"
                aria-label="Sair da apresentação"
              >
                <X aria-hidden="true" className="size-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
        <p className="text-sm font-semibold tracking-wide text-primary uppercase">Para quem escreve as leis</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">Validador de Leis</h1>
        <p className="mt-2 max-w-2xl text-lg text-muted">
          Envie a lei em PDF, XML ou foto. Conferimos se ela segue o padrão de redação da{" "}
          <strong className="text-text">Lei Complementar 95/1998</strong> e mostramos o que corrigir.
        </p>
      </motion.div>

      {/* Envio */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setArrastando(true);
        }}
        onDragLeave={() => setArrastando(false)}
        onDrop={soltar}
        className={`mt-6 rounded-2xl border-2 border-dashed p-5 transition sm:p-6 ${
          arrastando ? "border-primary bg-primary-soft" : "border-border bg-surface"
        } ${fase === "inicio" ? "" : "py-4"}`}
      >
        <div className="flex flex-wrap items-center gap-4">
          <span className="grid size-12 shrink-0 place-items-center rounded-xl bg-primary-soft text-primary">
            <Upload aria-hidden="true" className="size-6" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="font-semibold">{fase === "inicio" ? "Arraste o arquivo da lei para cá" : "Conferir outro arquivo"}</p>
            <p className="text-sm text-muted">PDF (com texto ou escaneado), XML no padrão LexML ou imagem (PNG, JPG)</p>
          </div>
          <input
            ref={entrada}
            type="file"
            accept=".pdf,.xml,application/pdf,application/xml,text/xml,image/*"
            className="sr-only"
            id="arquivo-lei"
            onChange={(e) => {
              receber(e.target.files);
              e.target.value = "";
            }}
          />
          <label
            htmlFor="arquivo-lei"
            className="cursor-pointer rounded-xl bg-primary px-5 py-2.5 font-semibold text-on-primary transition hover:bg-primary-strong"
          >
            Escolher arquivo
          </label>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-border pt-4">
          <span className="text-sm text-muted">Ou teste com um exemplo:</span>
          {EXEMPLOS.map((e) => (
            <span key={e.arquivo} className="inline-flex items-center overflow-hidden rounded-full border border-border bg-bg text-sm">
              <button
                type="button"
                onClick={() => {
                  if (apresentacao !== null) irPara(null);
                  abrirExemplo(e.arquivo);
                }}
                className="px-3 py-1.5 font-medium transition hover:bg-primary-soft hover:text-primary"
              >
                {e.rotulo} <span className="text-muted">· {e.detalhe}</span>
              </button>
              <a
                href={`/exemplos/${e.arquivo}`}
                target="_blank"
                rel="noreferrer"
                className="border-l border-border px-2 py-1.5 text-muted hover:text-primary"
                title="Abrir o arquivo original"
              >
                <ExternalLink aria-hidden="true" className="size-3.5" />
                <span className="sr-only">Abrir o arquivo {e.rotulo} em nova aba</span>
              </a>
            </span>
          ))}
          {apresentacao === null && (
            <button
              type="button"
              onClick={() => irPara(0)}
              className="ml-auto inline-flex items-center gap-1.5 rounded-full bg-text px-3.5 py-1.5 text-sm font-semibold text-bg"
            >
              <MonitorPlay aria-hidden="true" className="size-4" /> Apresentação
            </button>
          )}
        </div>
      </div>

      {fase === "falhou" && (
        <p role="alert" className="mt-6 flex items-start gap-3 rounded-2xl border border-danger/30 bg-danger-soft p-4 text-danger">
          <CircleX aria-hidden="true" className="mt-0.5 size-5 shrink-0" />
          <span>
            <strong>Não consegui ler “{nome}”.</strong> {erroLeitura}
          </span>
        </p>
      )}

      {fase !== "inicio" && fase !== "falhou" && (
        <div className="mt-8 grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_400px]">
          {/* A folha: o documento sendo lido */}
          <Folha
            doc={doc}
            nome={nome}
            linhasVisiveis={linhasVisiveis}
            lendo={fase === "lendo" || fase === "conferindo"}
            pronto={fase === "pronto"}
            porLinha={porLinha}
          />

          {/* O painel: leitura, teste e resultado */}
          <div className="grid gap-4 lg:sticky lg:top-4" aria-live="polite">
            <PainelLeitura fase={fase} etapa={etapa} doc={doc} />
            {resultado && <PainelTeste checagens={resultado.checagens} feitas={feitas} />}
            {fase === "pronto" && resultado && <Veredito resultado={resultado} />}
          </div>
        </div>
      )}

      {fase === "pronto" && problemas.length > 0 && (
        <section className="mt-8" aria-labelledby="titulo-correcoes">
          <h2 id="titulo-correcoes" className="text-xl font-bold">
            O que corrigir
          </h2>
          <p className="text-muted">Cada item mostra o trecho do documento e como ele deve ficar.</p>
          <ol className="mt-4 grid gap-3 md:grid-cols-2">
            {problemas.map((p, i) => (
              <CartaoProblema key={p.n} p={p} ordem={i} />
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}

// ---------------------------------------------------------------- Folha (documento)

function Folha({
  doc,
  nome,
  linhasVisiveis,
  lendo,
  pronto,
  porLinha,
}: {
  doc: Documento | null;
  nome: string;
  linhasVisiveis: number;
  lendo: boolean;
  pronto: boolean;
  porLinha: Map<number, ProblemaNumerado[]>;
}) {
  const reduzir = useReducedMotion();
  const Icone = !doc ? FileText : doc.tipo === "xml" ? FileCode : doc.tipo === "pdf" ? FileText : ScanText;

  return (
    <section aria-label="Documento lido" className="overflow-hidden rounded-2xl border border-border bg-surface shadow-card">
      <header className="flex items-center gap-2 border-b border-border px-4 py-2.5 text-sm">
        <Icone aria-hidden="true" className="size-4 text-primary" />
        <span className="min-w-0 flex-1 truncate font-semibold">{nome}</span>
        {doc && (
          <span className="text-muted">
            {doc.paginas} {doc.paginas === 1 ? "página" : "páginas"} · {doc.paragrafos.length} trechos
          </span>
        )}
      </header>

      <div className="relative min-h-[420px] bg-[color-mix(in_srgb,var(--surface)_92%,var(--border))] p-4 sm:p-8">
        <div className="relative mx-auto max-w-[640px] rounded bg-surface px-6 py-8 font-serif text-[0.95rem] leading-relaxed shadow-md sm:px-10 [.contraste_&]:border [.contraste_&]:border-border">
          {/* Barra de leitura passando pela folha */}
          {lendo && !reduzir && (
            <motion.span
              aria-hidden="true"
              className="pointer-events-none absolute inset-x-0 h-16 bg-gradient-to-b from-transparent via-primary/15 to-transparent"
              initial={{ top: "-10%" }}
              animate={{ top: ["-10%", "100%"] }}
              transition={{ duration: 1.6, repeat: Infinity, ease: "linear" }}
            />
          )}

          {!doc && (
            <div className="grid gap-3" aria-hidden="true">
              {[70, 100, 90, 100, 60, 95, 80].map((w, i) => (
                <span key={i} className="esqueleto block h-3.5 rounded" style={{ width: `${w}%` }} />
              ))}
            </div>
          )}

          {doc && doc.paragrafos.length === 0 && (
            <p className="text-muted">Nenhum texto foi encontrado neste arquivo.</p>
          )}

          {doc &&
            doc.paragrafos.slice(0, linhasVisiveis).map((p, i) => {
              const marcas = pronto ? porLinha.get(i) ?? [] : [];
              const temErro = marcas.some((m) => m.gravidade === "erro");
              const temAviso = !temErro && marcas.length > 0;
              return (
                <motion.p
                  key={i}
                  id={`trecho-${i}`}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`relative mb-2.5 rounded px-1.5 py-0.5 transition-colors duration-500 ${estiloTrecho(p.texto, i)} ${
                    temErro ? "bg-danger-soft ring-1 ring-danger/40" : temAviso ? "bg-warn-soft ring-1 ring-warn/40" : ""
                  }`}
                >
                  {marcas.length > 0 && (
                    <span className="absolute top-0.5 -left-7 flex flex-col gap-0.5 font-sans">
                      {marcas.map((m) => (
                        <a
                          key={m.n}
                          href={`#problema-${m.n}`}
                          className={`grid size-5 place-items-center rounded-full text-[0.65rem] font-bold text-white no-underline ${
                            m.gravidade === "erro" ? "bg-danger" : "bg-warn"
                          }`}
                          aria-label={`Problema ${m.n}: ${m.titulo}`}
                        >
                          {m.n}
                        </a>
                      ))}
                    </span>
                  )}
                  {p.texto}
                </motion.p>
              );
            })}
        </div>
      </div>
    </section>
  );
}

function estiloTrecho(t: string, i: number) {
  if (i === 0 && /^\s*LEI\b/i.test(t)) return "text-center font-bold";
  if (/^(S[ÚU]MULA|EMENTA)/i.test(t)) return "ml-auto w-[70%] italic";
  if (/^([IVXLC]+\s*[-–—]|\d+\s*[-–—)]|[a-zA-Z]\))\s/.test(t)) return "pl-6";
  if (/^(Londrina,|PREFEITO|PRESIDENTE|Documento de exemplo)/i.test(t)) return "text-center";
  return "text-justify";
}

// ---------------------------------------------------------------- Painel: leitura e teste

function PainelLeitura({ fase, etapa, doc }: { fase: Fase; etapa: Etapa | null; doc: Documento | null }) {
  const lendo = fase === "lendo" && !doc;
  const ocr = doc?.tipo === "pdf-escaneado" || doc?.tipo === "imagem";
  const resumo = doc
    ? doc.tipo === "xml"
      ? `XML lido: ${doc.paragrafos.length} trechos`
      : ocr
        ? `Texto reconhecido da imagem (OCR): ${doc.paragrafos.length} trechos`
        : `Texto do PDF lido: ${doc.paragrafos.length} trechos`
    : etapa?.texto ?? "Abrindo o arquivo";

  return (
    <section className="rounded-2xl border border-border bg-surface p-4 shadow-card">
      <h2 className="mb-3 text-sm font-semibold tracking-wide text-muted uppercase">1. Leitura</h2>
      <div className="flex items-start gap-3">
        {lendo ? (
          <Loader2 aria-hidden="true" className="mt-0.5 size-5 shrink-0 animate-spin text-primary" />
        ) : (
          <CircleCheck aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-ok" />
        )}
        <div className="min-w-0 flex-1">
          <p className="font-medium">{resumo}</p>
          {lendo && etapa?.progresso !== undefined && (
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-border" role="progressbar" aria-valuenow={Math.round(etapa.progresso * 100)} aria-valuemin={0} aria-valuemax={100} aria-label="Progresso da leitura">
              <motion.div className="h-full rounded-full bg-primary" animate={{ width: `${Math.round(etapa.progresso * 100)}%` }} transition={{ duration: 0.3 }} />
            </div>
          )}
          {lendo && etapa?.progresso !== undefined && <p className="mt-1 text-xs text-muted">{Math.round(etapa.progresso * 100)}%</p>}
        </div>
      </div>
    </section>
  );
}

function PainelTeste({ checagens, feitas }: { checagens: Checagem[]; feitas: number }) {
  return (
    <section className="rounded-2xl border border-border bg-surface p-4 shadow-card">
      <h2 className="mb-3 text-sm font-semibold tracking-wide text-muted uppercase">
        2. Teste · {Math.min(feitas, checagens.length)} de {checagens.length} regras
      </h2>
      <ul className="grid gap-1">
        {checagens.map((c, i) => {
          const feito = i < feitas;
          const rodando = i === feitas;
          const erros = c.problemas.filter((p) => p.gravidade === "erro").length;
          const avisos = c.problemas.length - erros;
          return (
            <li key={c.id} className={`flex items-center gap-3 rounded-lg px-2 py-1.5 transition-colors ${rodando ? "bg-primary-soft" : ""}`}>
              <span className="grid size-5 shrink-0 place-items-center">
                {!feito ? (
                  rodando ? (
                    <Loader2 aria-hidden="true" className="size-4 animate-spin text-primary" />
                  ) : (
                    <span aria-hidden="true" className="size-3 rounded-full border-2 border-border" />
                  )
                ) : (
                  <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 500, damping: 20 }}>
                    {erros ? (
                      <CircleX aria-hidden="true" className="size-5 text-danger" />
                    ) : avisos ? (
                      <TriangleAlert aria-hidden="true" className="size-5 text-warn" />
                    ) : (
                      <CircleCheck aria-hidden="true" className="size-5 text-ok" />
                    )}
                  </motion.span>
                )}
              </span>
              <span className="min-w-0 flex-1 leading-tight">
                <span className="block text-sm font-medium">{c.nome}</span>
                <span className="block text-xs text-muted">{c.base}</span>
              </span>
              {feito && (
                <motion.span
                  initial={{ opacity: 0, x: 6 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`text-xs font-semibold ${erros ? "text-danger" : avisos ? "text-warn" : "text-ok"}`}
                >
                  {erros ? `${erros} ${erros === 1 ? "erro" : "erros"}` : avisos ? `${avisos} ${avisos === 1 ? "aviso" : "avisos"}` : "ok"}
                </motion.span>
              )}
              <span className="sr-only">{feito ? (erros ? `${erros} erros` : avisos ? `${avisos} avisos` : "aprovada") : "aguardando"}</span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

function Veredito({ resultado }: { resultado: Resultado }) {
  const { conforme, erros, avisos } = resultado;
  return (
    <motion.section
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 22 }}
      className={`rounded-2xl border-2 p-5 ${conforme ? "border-ok/40 bg-ok-soft text-ok" : "border-danger/40 bg-danger-soft text-danger"}`}
      role="status"
    >
      <div className="flex items-center gap-3">
        {conforme ? <ShieldCheck aria-hidden="true" className="size-9 shrink-0" /> : <CircleX aria-hidden="true" className="size-9 shrink-0" />}
        <div>
          <p className="text-xl leading-tight font-black">{conforme ? "Em conformidade" : "Sem conformidade"}</p>
          <p className="text-sm font-medium text-text">
            {conforme
              ? avisos
                ? `Segue o padrão da LC 95/1998. ${avisos} ${avisos === 1 ? "aviso" : "avisos"} para revisar.`
                : "Segue o padrão da LC 95/1998. Pode publicar."
              : `${erros} ${erros === 1 ? "erro" : "erros"} para corrigir${avisos ? ` e ${avisos} ${avisos === 1 ? "aviso" : "avisos"}` : ""}.`}
          </p>
        </div>
      </div>
      {!conforme && (
        <a href="#titulo-correcoes" className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold underline-offset-4 hover:underline">
          Ver o que corrigir <ArrowRight aria-hidden="true" className="size-4" />
        </a>
      )}
    </motion.section>
  );
}

// ---------------------------------------------------------------- Problemas

function CartaoProblema({ p, ordem }: { p: ProblemaNumerado; ordem: number }) {
  const erro = p.gravidade === "erro";
  function verNoDocumento() {
    const el = document.getElementById(`trecho-${p.linha}`);
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    el.animate([{ outline: "3px solid var(--focus)" }, { outline: "3px solid transparent" }], { duration: 1400 });
  }
  return (
    <motion.li
      id={`problema-${p.n}`}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: Math.min(ordem, 10) * 0.05 }}
      className={`scroll-mt-6 rounded-2xl border bg-surface p-4 shadow-card ${erro ? "border-danger/30" : "border-warn/30"}`}
    >
      <div className="flex items-start gap-3">
        <span
          className={`grid size-6 shrink-0 place-items-center rounded-full text-xs font-bold text-white ${erro ? "bg-danger" : "bg-warn"}`}
          aria-hidden="true"
        >
          {p.n}
        </span>
        <div className="min-w-0 flex-1">
          <p className="font-semibold">
            <span className="sr-only">{erro ? "Erro" : "Aviso"} {p.n}: </span>
            {p.titulo}
          </p>
          <p className="text-sm text-muted">{p.explicacao}</p>
          {(p.encontrado || p.esperado) && (
            <dl className="mt-3 grid gap-1.5 text-sm">
              {p.encontrado && (
                <div className="flex flex-wrap items-baseline gap-x-2">
                  <dt className="text-xs font-semibold text-muted uppercase">Está assim</dt>
                  <dd className="rounded bg-danger-soft px-1.5 py-0.5 break-words text-danger line-through decoration-danger/60">{p.encontrado}</dd>
                </div>
              )}
              {p.esperado && (
                <div className="flex flex-wrap items-baseline gap-x-2">
                  <dt className="text-xs font-semibold text-muted uppercase">Deve ficar</dt>
                  <dd className="rounded bg-ok-soft px-1.5 py-0.5 font-medium break-words text-ok">{p.esperado}</dd>
                </div>
              )}
            </dl>
          )}
          <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
            <span>{p.base}</span>
            {p.linha !== undefined && (
              <button type="button" onClick={verNoDocumento} className="inline-flex items-center gap-1 font-semibold text-primary hover:underline">
                Ver no documento <ArrowRight aria-hidden="true" className="size-3 -rotate-90" />
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.li>
  );
}
