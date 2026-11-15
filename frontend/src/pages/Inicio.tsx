import { motion } from "motion/react";
import { useNavigate } from "react-router-dom";
import { CircleCheck, Ear, ShieldCheck } from "lucide-react";
import { CaixaPergunta } from "../components/CaixaPergunta";
import { useRota } from "../lib/rota";

const SUGESTOES = [
  "quais são as regras do código ambiental?",
  "quais documentos preciso para a consulta prévia de parcelamento do solo?",
  "corte de árvore em logradouro público",
  "isenção de IPTU para aposentado",
  "quem tem direito a passe escolar?",
  "posso passear com meu cachorro na praça sem guia?",
];

const PILARES = [
  { icone: CircleCheck, titulo: "Só leis em vigor", texto: "Leis revogadas ficam de fora da resposta." },
  { icone: ShieldCheck, titulo: "Sempre com a fonte", texto: "Cada resposta mostra a lei e o link oficial." },
  { icone: Ear, titulo: "Para todo mundo", texto: "Pergunte falando, ouça a resposta ou use Libras." },
];

export function Inicio() {
  const navegar = useNavigate();
  const rota = useRota();
  const perguntar = (pergunta: string) => navegar(rota(`/perguntar`) + `?q=${encodeURIComponent(pergunta)}`);

  return (
    <div className="mx-auto max-w-3xl px-4 pt-14 pb-20 sm:px-6 sm:pt-24">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: "easeOut" }}>
        <p className="mb-4 text-center text-sm font-semibold tracking-wide text-primary uppercase">Leis de Londrina</p>
        <h1 className="text-center text-4xl font-bold tracking-tight sm:text-5xl">
          O que você quer saber sobre as leis da cidade?
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-center text-lg text-muted">
          Pergunte com suas palavras. A resposta usa só as leis que valem hoje.
        </p>
      </motion.div>

      <motion.div
        id="busca"
        className="mt-10"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1, ease: "easeOut" }}
      >
        <CaixaPergunta aoEnviar={perguntar} grande autoFocus />
      </motion.div>

      <motion.div
        className="mt-5"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.25 }}
      >
        <h2 className="sr-only">Sugestões de perguntas</h2>
        <ul className="flex flex-wrap justify-center gap-2">
          {SUGESTOES.map((s) => (
            <li key={s}>
              <button
                type="button"
                onClick={() => perguntar(s)}
                className="rounded-full border border-border bg-surface px-4 py-2 text-sm text-text transition hover:border-primary hover:text-primary"
              >
                {s}
              </button>
            </li>
          ))}
        </ul>
      </motion.div>

      <ul className="mt-20 grid gap-6 sm:grid-cols-3">
        {PILARES.map(({ icone: Icone, titulo, texto }) => (
          <li key={titulo} className="flex gap-3 sm:flex-col sm:gap-2">
            <Icone aria-hidden="true" className="mt-0.5 size-6 shrink-0 text-primary" />
            <div>
              <h2 className="font-semibold">{titulo}</h2>
              <p className="text-sm text-muted">{texto}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
