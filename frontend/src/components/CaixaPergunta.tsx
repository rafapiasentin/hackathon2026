import { ArrowUp, Mic } from "lucide-react";
import { useEffect, useId, useState, type FormEvent } from "react";
import { useDitar } from "../lib/fala";
import { Equalizador } from "./Animacoes";

interface Props {
  aoEnviar: (pergunta: string) => void;
  grande?: boolean;
  valorInicial?: string;
  desativado?: boolean;
  rotulo?: string;
  autoFocus?: boolean;
  /** Texto escrito "de fora" (modo apresentação digitando sozinho) */
  textoExterno?: string;
}

/** Campo de pergunta com envio por teclado e por voz. */
export function CaixaPergunta({
  aoEnviar,
  grande = false,
  valorInicial = "",
  desativado = false,
  rotulo = "Digite ou fale sua pergunta",
  autoFocus = false,
  textoExterno,
}: Props) {
  const [texto, setTexto] = useState(valorInicial);
  useEffect(() => {
    if (textoExterno !== undefined) setTexto(textoExterno);
  }, [textoExterno]);
  const id = useId();
  const ditar = useDitar((falado) => {
    setTexto(falado);
    aoEnviar(falado);
  });

  function enviar(e: FormEvent) {
    e.preventDefault();
    const t = texto.trim();
    if (!t || desativado) return;
    aoEnviar(t);
    setTexto("");
  }

  return (
    <form onSubmit={enviar} role="search" className="w-full">
      <label htmlFor={id} className="sr-only">
        {rotulo}
      </label>
      <div
        className={`flex items-center gap-2 rounded-2xl border border-border bg-surface shadow-card transition focus-within:border-primary focus-within:ring-4 focus-within:ring-primary/15 ${
          grande ? "p-2 pl-5" : "p-1.5 pl-4"
        }`}
      >
        <input
          id={id}
          name="pergunta"
          type="text"
          autoComplete="off"
          autoFocus={autoFocus}
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder={ditar.ouvindo ? "Pode falar, estou ouvindo..." : "Ex.: posso cortar uma árvore na frente de casa?"}
          className={`min-w-0 flex-1 bg-transparent text-text placeholder:text-muted/80 focus:outline-none ${
            grande ? "py-3 text-lg" : "py-2 text-base"
          }`}
        />
        {ditar.suportado && (
          <button
            type="button"
            onClick={ditar.ouvindo ? ditar.parar : ditar.iniciar}
            aria-pressed={ditar.ouvindo}
            aria-label={ditar.ouvindo ? "Parar de ouvir" : "Falar a pergunta"}
            className={`relative grid shrink-0 place-items-center rounded-xl text-primary transition hover:bg-primary-soft aria-pressed:bg-danger aria-pressed:text-white aria-pressed:ring-4 aria-pressed:ring-danger/25 ${
              grande ? "size-12" : "size-10"
            }`}
          >
            {ditar.ouvindo ? <Equalizador barras={5} className="h-5" /> : <Mic aria-hidden="true" className="size-5" />}
          </button>
        )}
        <button
          type="submit"
          disabled={!texto.trim() || desativado}
          aria-label="Enviar pergunta"
          className={`grid shrink-0 place-items-center rounded-xl bg-primary text-on-primary transition hover:bg-primary-strong disabled:opacity-40 ${
            grande ? "size-12" : "size-10"
          }`}
        >
          <ArrowUp aria-hidden="true" className="size-5" strokeWidth={2.5} />
        </button>
      </div>
      {ditar.erro && (
        <p role="alert" className="mt-2 text-sm text-danger">
          {ditar.erro}
        </p>
      )}
    </form>
  );
}
