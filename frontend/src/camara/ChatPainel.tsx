import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Maximize2, MessageCircleQuestion, X } from "lucide-react";
import { perguntar } from "../api/client";
import type { Resposta } from "../api/types";
import { CaixaPergunta } from "../components/CaixaPergunta";
import { CartaoResposta, Pensando } from "../pages/Conversa";
import { useOuvir } from "../lib/fala";

const SUGESTOES = [
  "quais são as regras do código ambiental?",
  "quais documentos preciso para a consulta prévia de parcelamento do solo?",
  "corte de árvore em logradouro público",
  "isenção de IPTU para aposentado",
  "quem tem direito a passe escolar?",
  "posso passear com meu cachorro na praça sem guia?",
];

interface Mensagem {
  id: number;
  pergunta: string;
  resposta?: Resposta;
  erro?: string;
}

/** Ícone flutuante + painel lateral com o assistente de leis, para morar dentro do site da Câmara. */
export function ChatFlutuante() {
  const [aberto, setAberto] = useState(false);
  // Modo apresentação: /camara?demo=1 (pergunta padrão) ou /camara?demo=Lei 11.471/2012 (pergunta escolhida)
  const [params] = useSearchParams();
  const demoParam = params.get("demo");
  const perguntaDemo = demoParam ? (demoParam === "1" ? SUGESTOES[0] : demoParam) : undefined;
  const [dica, setDica] = useState(true);
  const botao = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const t = setTimeout(() => setDica(false), 9000);
    // O banner "Perguntar agora" da página inicial abre o mesmo painel
    const abrir = () => setAberto(true);
    window.addEventListener("abrir-chat-leis", abrir);
    return () => {
      clearTimeout(t);
      window.removeEventListener("abrir-chat-leis", abrir);
    };
  }, []);

  useEffect(() => {
    if (!perguntaDemo) return;
    const t = setTimeout(() => setAberto(true), 1800);
    return () => clearTimeout(t);
  }, [perguntaDemo]);

  function fechar() {
    setAberto(false);
    botao.current?.focus();
  }

  return (
    <>
      <div className="fixed right-5 bottom-5 z-40 flex items-center gap-3">
        <AnimatePresence>
          {dica && !aberto && (
            <motion.p
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 12 }}
              transition={{ delay: 0.8 }}
              className="hidden rounded-2xl rounded-br-sm bg-surface px-4 py-2.5 text-sm font-semibold text-text shadow-lg ring-1 ring-border sm:block"
            >
              Dúvida sobre uma lei? Pergunte aqui!
            </motion.p>
          )}
        </AnimatePresence>
        <motion.button
          ref={botao}
          type="button"
          onClick={() => (aberto ? fechar() : setAberto(true))}
          aria-expanded={aberto}
          aria-controls="painel-leis"
          aria-label={aberto ? "Fechar assistente de leis" : "Abrir assistente de leis: pergunte sobre as leis de Londrina"}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 260, damping: 18, delay: 0.4 }}
          className="relative grid size-16 place-items-center rounded-full bg-primary text-on-primary shadow-xl ring-4 ring-surface transition hover:bg-primary-strong"
        >
          {!aberto && (
            <span aria-hidden="true" className="absolute inset-0 animate-ping rounded-full bg-primary opacity-30 motion-reduce:hidden" />
          )}
          <AnimatePresence mode="wait" initial={false}>
            <motion.span
              key={aberto ? "fechar" : "abrir"}
              initial={{ rotate: -90, scale: 0.5, opacity: 0 }}
              animate={{ rotate: 0, scale: 1, opacity: 1 }}
              exit={{ rotate: 90, scale: 0.5, opacity: 0 }}
              transition={{ duration: 0.18 }}
              className="grid place-items-center"
            >
              {aberto ? <X aria-hidden="true" className="size-7" /> : <MessageCircleQuestion aria-hidden="true" className="size-8" />}
            </motion.span>
          </AnimatePresence>
        </motion.button>
      </div>

      <AnimatePresence>{aberto && <Painel aoFechar={fechar} perguntaDemo={perguntaDemo} />}</AnimatePresence>
    </>
  );
}

function Painel({ aoFechar, perguntaDemo }: { aoFechar: () => void; perguntaDemo?: string }) {
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [rascunho, setRascunho] = useState<string | undefined>(undefined);
  const reduzir = useReducedMotion();
  const [carregando, setCarregando] = useState(false);
  const contador = useRef(0);
  const fim = useRef<HTMLDivElement>(null);
  const voz = useOuvir();

  useEffect(() => {
    const esc = (e: KeyboardEvent) => e.key === "Escape" && aoFechar();
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [aoFechar]);

  useEffect(() => {
    fim.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [mensagens, carregando]);

  // Modo apresentação: digita a pergunta sozinho, letra por letra, e envia
  useEffect(() => {
    if (!perguntaDemo) return;
    const timers: ReturnType<typeof setTimeout>[] = [];
    let tempo = 700;
    for (let i = 1; i <= perguntaDemo.length; i++) {
      tempo += 35 + Math.random() * 45;
      timers.push(setTimeout(() => setRascunho(perguntaDemo.slice(0, i)), tempo));
    }
    timers.push(
      setTimeout(() => {
        setRascunho("");
        enviar(perguntaDemo);
      }, tempo + 450),
    );
    return () => timers.forEach(clearTimeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [perguntaDemo]);

  async function enviar(pergunta: string) {
    const id = ++contador.current;
    setMensagens((m) => [...m, { id, pergunta }]);
    setCarregando(true);
    try {
      const resposta = await perguntar(pergunta);
      setMensagens((m) => m.map((x) => (x.id === id ? { ...x, resposta } : x)));
    } catch {
      setMensagens((m) => m.map((x) => (x.id === id ? { ...x, erro: "Não consegui responder agora. Tente de novo." } : x)));
    } finally {
      setCarregando(false);
    }
  }

  return (
    <motion.section
      id="painel-leis"
      role="dialog"
      aria-labelledby="painel-leis-titulo"
      initial={reduzir ? { opacity: 0 } : { clipPath: "circle(0px at calc(100% + 28px) calc(100% + 52px))" }}
      animate={reduzir ? { opacity: 1 } : { clipPath: "circle(150% at calc(100% + 28px) calc(100% + 52px))" }}
      exit={reduzir ? { opacity: 0 } : { clipPath: "circle(0px at calc(100% + 28px) calc(100% + 52px))" }}
      transition={{ duration: 0.45, ease: [0.4, 0, 0.2, 1] }}
      className="fixed inset-x-0 bottom-0 z-50 flex h-[85vh] flex-col overflow-hidden rounded-t-3xl border border-border bg-bg shadow-2xl sm:inset-x-auto sm:right-20 sm:bottom-24 sm:h-[min(680px,calc(100vh-8rem))] sm:w-[440px] sm:rounded-3xl"
    >
      <header className="flex items-center gap-3 bg-primary px-5 py-4 text-on-primary">
        <span className="grid size-10 place-items-center rounded-full bg-white/15">
          <MessageCircleQuestion aria-hidden="true" className="size-6" />
        </span>
        <div className="min-w-0 flex-1 leading-tight">
          <h2 id="painel-leis-titulo" className="font-bold">Consulta de Leis</h2>
          <p className="text-sm opacity-85">Respostas só com leis em vigor</p>
        </div>
        <Link
          to="/camara/perguntar"
          onClick={aoFechar}
          className="grid size-9 place-items-center rounded-full hover:bg-white/15"
          aria-label="Abrir em tela cheia"
          title="Abrir em tela cheia"
        >
          <Maximize2 aria-hidden="true" className="size-4" />
        </Link>
        <button
          type="button"
          onClick={aoFechar}
          className="grid size-9 place-items-center rounded-full hover:bg-white/15"
          aria-label="Fechar assistente"
        >
          <X aria-hidden="true" className="size-5" />
        </button>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-5" aria-live="polite" aria-busy={carregando}>
        {mensagens.length === 0 ? (
          <div>
            <p className="rounded-2xl rounded-tl-md bg-surface p-4 shadow-card">
              Olá! Pergunte com suas palavras sobre qualquer lei de Londrina. Eu respondo usando só as leis que{" "}
              <strong>valem hoje</strong> e mostro de onde tirei a resposta.
            </p>
            <p className="mt-5 mb-2 text-sm font-semibold text-muted">Experimente:</p>
            <ul className="grid gap-2">
              {SUGESTOES.map((s) => (
                <li key={s}>
                  <button
                    type="button"
                    onClick={() => enviar(s)}
                    className="w-full rounded-xl border border-border bg-surface px-4 py-2.5 text-left text-sm transition hover:border-primary hover:text-primary"
                  >
                    {s}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <ol className="grid gap-6">
            {mensagens.map((m) => (
              <li key={m.id} className="grid gap-3">
                <p className="ml-auto max-w-[85%] rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-on-primary">
                  <span className="sr-only">Você perguntou: </span>
                  {m.pergunta}
                </p>
                {m.resposta && <CartaoResposta resposta={m.resposta} voz={voz} />}
                {m.erro && (
                  <p role="alert" className="rounded-2xl bg-danger-soft px-4 py-3 text-danger">
                    {m.erro}
                  </p>
                )}
                {!m.resposta && !m.erro && <Pensando />}
              </li>
            ))}
          </ol>
        )}
        <div ref={fim} />
      </div>

      <div className="border-t border-border bg-surface px-3 py-3">
        <CaixaPergunta aoEnviar={enviar} desativado={carregando} autoFocus textoExterno={rascunho} rotulo="Sua pergunta sobre as leis" />
      </div>
    </motion.section>
  );
}
