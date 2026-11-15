import { AnimatePresence, motion } from "motion/react";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ArrowRight, CircleX, ExternalLink, Info, Square, Volume2 } from "lucide-react";
import { perguntar } from "../api/client";
import type { Resposta } from "../api/types";
import { CaixaPergunta } from "../components/CaixaPergunta";
import { OrigemResposta } from "../components/OrigemResposta";
import { StatusBadge } from "../components/StatusBadge";
import { Equalizador, Riscado, TextoDigitando } from "../components/Animacoes";
import { useRota } from "../lib/rota";
import { ementaLimpa, nomeLei } from "../lib/leis";
import { useOuvir } from "../lib/fala";

interface Mensagem {
  id: number;
  pergunta: string;
  resposta?: Resposta;
  erro?: string;
}

export function Conversa() {
  const [params, setParams] = useSearchParams();
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [topo, setTopo] = useState(16);
  const contador = useRef(0);
  const ultimaPergunta = useRef<HTMLParagraphElement>(null);
  const aguardando = useRef<number | null>(null);
  const enviada = useRef<number | null>(null);
  const posicaoEnvio = useRef(0);
  const rolagemManual = useRef(false);
  const voz = useOuvir();

  useEffect(() => {
    const teclas = new Set(["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End", " "]);
    const marcar = () => {
      if (aguardando.current !== null) rolagemManual.current = true;
    };
    const tecla = (e: KeyboardEvent) => {
      if (teclas.has(e.key) && !(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement)) marcar();
    };
    window.addEventListener("wheel", marcar, { passive: true });
    window.addEventListener("touchmove", marcar, { passive: true });
    window.addEventListener("keydown", tecla);
    return () => {
      window.removeEventListener("wheel", marcar);
      window.removeEventListener("touchmove", marcar);
      window.removeEventListener("keydown", tecla);
    };
  }, []);

  useLayoutEffect(() => {
    const cabecalho = document.querySelector("header");
    if (!cabecalho) return;
    const medir = () => {
      const fixo = ["fixed", "sticky"].includes(getComputedStyle(cabecalho).position);
      setTopo((fixo ? cabecalho.getBoundingClientRect().height : 0) + 16);
    };
    medir();
    const observador = new ResizeObserver(medir);
    observador.observe(cabecalho);
    return () => observador.disconnect();
  }, []);

  function rolarAtePergunta() {
    const el = ultimaPergunta.current;
    if (!el) return;
    const suave = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const destino = el.getBoundingClientRect().top + window.scrollY - topo;
    const maximo = document.documentElement.scrollHeight - window.innerHeight;
    posicaoEnvio.current = Math.max(0, Math.min(destino, maximo));
    el.scrollIntoView({ behavior: suave ? "smooth" : "auto", block: "start" });
  }

  useEffect(() => {
    const ultima = mensagens[mensagens.length - 1];
    if (!ultima) return;
    if (enviada.current === ultima.id) {
      enviada.current = null;
      aguardando.current = ultima.id;
      rolagemManual.current = false;
      rolarAtePergunta();
    } else if (aguardando.current === ultima.id && (ultima.resposta || ultima.erro)) {
      aguardando.current = null;
      const afastou = rolagemManual.current && Math.abs(window.scrollY - posicaoEnvio.current) > 48;
      if (!afastou) rolarAtePergunta();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mensagens]);

  async function enviar(pergunta: string) {
    const id = ++contador.current;
    enviada.current = id;
    setMensagens((m) => [...m, { id, pergunta }]);
    setCarregando(true);
    try {
      const resposta = await perguntar(pergunta);
      setMensagens((m) => m.map((x) => (x.id === id ? { ...x, resposta } : x)));
    } catch {
      setMensagens((m) =>
        m.map((x) => (x.id === id ? { ...x, erro: "Não consegui responder agora. Verifique a conexão e tente de novo." } : x)),
      );
    } finally {
      setCarregando(false);
    }
  }

  // Pergunta que veio da página inicial (?q=...)
  const jaLeu = useRef(false);
  useEffect(() => {
    if (jaLeu.current) return; // o React (modo dev) roda efeitos duas vezes
    jaLeu.current = true;
    const q = params.get("q");
    if (q) {
      setParams({}, { replace: true });
      enviar(q);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="mx-auto flex max-w-3xl flex-col px-4 pt-8 pb-40 sm:px-6 [&_article]:scroll-mb-40">
      <h1 className="sr-only">Conversa sobre as leis de Londrina</h1>

      {mensagens.length === 0 && !carregando && (
        <p className="py-16 text-center text-muted">Faça sua pergunta no campo abaixo.</p>
      )}

      <ol className="grid gap-8" aria-live="polite" aria-busy={carregando}>
        <AnimatePresence initial={false}>
          {mensagens.map((m, i) => (
            <motion.li
              key={m.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              className="grid content-start gap-4"
              style={i === mensagens.length - 1 ? { minHeight: `calc(100dvh - ${topo}px - 10rem)` } : undefined}
            >
              <p
                ref={i === mensagens.length - 1 ? ultimaPergunta : undefined}
                style={{ scrollMarginTop: topo }}
                className="ml-auto max-w-[85%] rounded-2xl rounded-br-md bg-primary px-4 py-3 text-on-primary"
              >
                <span className="sr-only">Você perguntou: </span>
                {m.pergunta}
              </p>

              {m.resposta && <CartaoResposta resposta={m.resposta} voz={voz} rolarAoFim={false} />}
              {m.erro && (
                <p role="alert" className="rounded-2xl border border-danger/30 bg-danger-soft px-4 py-3 text-danger">
                  {m.erro}
                </p>
              )}
              {!m.resposta && !m.erro && <Pensando />}
            </motion.li>
          ))}
        </AnimatePresence>
      </ol>

      <div className="fixed inset-x-0 bottom-0 border-t border-border bg-bg/90 backdrop-blur">
        <div id="busca" className="mx-auto max-w-3xl px-4 py-3 sm:px-6">
          <CaixaPergunta aoEnviar={enviar} desativado={carregando} autoFocus rotulo="Faça outra pergunta" />
          <p className="mt-2 text-center text-xs text-muted">
            Respostas baseadas nas leis da Câmara Municipal de Londrina. Não substituem orientação jurídica.
          </p>
        </div>
      </div>
    </div>
  );
}

export function Pensando() {
  return (
    <div className="flex items-center gap-3 text-muted" role="status">
      <span className="flex gap-1" aria-hidden="true">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="size-2 rounded-full bg-primary"
            animate={{ opacity: [0.25, 1, 0.25] }}
            transition={{ duration: 1, repeat: Infinity, delay: i * 0.15 }}
          />
        ))}
      </span>
      Procurando nas leis em vigor...
    </div>
  );
}

export function CartaoResposta({
  resposta,
  voz,
  rolarAoFim = true,
}: {
  resposta: Resposta;
  voz: ReturnType<typeof useOuvir>;
  rolarAoFim?: boolean;
}) {
  const [verTrechos, setVerTrechos] = useState(false);
  // Fontes e avisos entram depois que o texto termina de aparecer
  const [pronto, setPronto] = useState(false);
  const rota = useRota();
  const temTrechos = resposta.fontes.some((f) => f.trecho);
  const aparecer = (ordem: number) => ({
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3, delay: ordem * 0.12, ease: "easeOut" as const },
  });
  const atrasoIgnoradas = resposta.fontes.length + 1;

  // Enquanto as fontes entram, a rolagem acompanha até o fim do cartão
  const cartao = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!pronto || !rolarAoFim) return;
    const descer = () => cartao.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    const timers = [80, (atrasoIgnoradas + 1) * 120 + 450].map((ms) => setTimeout(descer, ms));
    return () => timers.forEach(clearTimeout);
  }, [pronto, atrasoIgnoradas, rolarAoFim]);

  return (
    <article ref={cartao} className="scroll-mb-4 rounded-2xl border border-border bg-surface p-5 shadow-card sm:p-6">
      <h2 className="sr-only">Resposta</h2>
      <TextoDigitando texto={resposta.resposta} aoTerminar={() => setPronto(true)} className="text-lg leading-relaxed" />

      {pronto && voz.suportado && (
        <motion.button
          {...aparecer(0)}
          type="button"
          onClick={() => (voz.falando ? voz.parar() : voz.ouvir(resposta.resposta))}
          className="mt-4 inline-flex items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-sm font-medium text-primary hover:bg-primary-soft"
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
              Ouvir resposta
            </>
          )}
        </motion.button>
      )}

      {pronto && (
        <motion.div {...aparecer(0)}>
          <OrigemResposta camadas={resposta.camadas} alertas={resposta.alertas} />
        </motion.div>
      )}

      {pronto && resposta.fontes.length > 0 && (
        <section className="mt-6 border-t border-border pt-5">
          <motion.h3 {...aparecer(0)} className="mb-3 text-sm font-semibold text-muted">
            Baseado em
          </motion.h3>
          <ul className="grid gap-3">
            {resposta.fontes.map((f, i) => (
              <motion.li {...aparecer(i + 1)} key={`${f.lei_id}-${f.artigo}`} className="rounded-xl bg-bg p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <Link to={rota(`/lei/${f.lei_id}`)} className="group inline-flex items-center gap-1.5 font-semibold text-primary">
                    {nomeLei(f.chave, f.ano)}
                    {f.artigo && <span className="font-normal text-muted">· {f.artigo}</span>}
                    <ArrowRight aria-hidden="true" className="size-4 transition group-hover:translate-x-0.5" />
                  </Link>
                  <StatusBadge situacao={f.situacao} animado atraso={(i + 1) * 0.12 + 0.15} />
                </div>
                <p className="mt-1 text-sm text-muted">{ementaLimpa(f.ementa)}</p>
                <AnimatePresence initial={false}>
                  {verTrechos && f.trecho && (
                    <motion.blockquote
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.25 }}
                      className="overflow-hidden border-l-4 border-primary/40 pl-3 text-sm"
                    >
                      <span className="block pt-3">“{f.trecho}”</span>
                    </motion.blockquote>
                  )}
                </AnimatePresence>
              </motion.li>
            ))}
          </ul>
          {temTrechos && (
            <button
              type="button"
              onClick={() => setVerTrechos((v) => !v)}
              aria-expanded={verTrechos}
              className="mt-3 text-sm font-medium text-primary underline-offset-4 hover:underline"
            >
              {verTrechos ? "Esconder o texto da lei" : "Ver o texto da lei"}
            </button>
          )}
        </section>
      )}

      {pronto && resposta.ignoradas.length > 0 && (
        <motion.section {...aparecer(atrasoIgnoradas)} className="mt-5 flex gap-3 rounded-xl border border-border p-4 text-sm">
          <Info aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-primary" />
          <div>
            <h3 className="font-semibold">Leis que deixamos de fora</h3>
            <ul className="mt-1 grid gap-1 text-muted">
              {resposta.ignoradas.map((ig, i) => (
                <li key={ig.chave} className="flex flex-wrap items-center gap-x-2">
                  <CircleX aria-hidden="true" className="size-4 text-danger" />
                  <Riscado atraso={atrasoIgnoradas * 0.12 + 0.35 + i * 0.15}>
                    {ig.lei_id ? (
                      <Link to={rota(`/lei/${ig.lei_id}`)} className="text-text underline-offset-4 hover:underline">
                        {nomeLei(ig.chave, ig.ano)}
                      </Link>
                    ) : (
                      <span className="text-text">{nomeLei(ig.chave, ig.ano)}</span>
                    )}
                  </Riscado>
                  <span>· {ig.motivo}</span>
                  {ig.lei_id && ig.revogada_por_id && (
                    <Link
                      to={rota(`/comparar/${ig.lei_id}/${ig.revogada_por_id}`)}
                      className="inline-flex items-center gap-1 font-semibold text-primary underline-offset-4 hover:underline"
                    >
                      · Ver o que mudou <ArrowRight aria-hidden="true" className="size-3.5" />
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </motion.section>
      )}

      {pronto && resposta.fontes[0] && (
        <motion.a
          {...aparecer(atrasoIgnoradas + 1)}
          href={resposta.fontes[0].link}
          target="_blank"
          rel="noreferrer"
          className="mt-5 inline-flex items-center gap-1.5 text-sm text-muted underline-offset-4 hover:text-primary hover:underline"
        >
          Ver no site da Câmara <ExternalLink aria-hidden="true" className="size-3.5" />
          <span className="sr-only">(abre em nova aba)</span>
        </motion.a>
      )}
    </article>
  );
}
