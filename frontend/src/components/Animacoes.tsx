// Peças de animação reaproveitadas pelo site.
// Regra: animação curta, sóbria e que nunca atrasa a informação.
// Quem ativou "reduzir movimento" no sistema vê tudo pronto, sem animar.
import { animate, motion, useInView, useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";

/** Texto que aparece palavra por palavra, como numa IA. O leitor de tela recebe o texto inteiro de uma vez. */
export function TextoDigitando({
  texto,
  aoTerminar,
  msPorPalavra = 38,
  className,
}: {
  texto: string;
  aoTerminar?: () => void;
  msPorPalavra?: number;
  className?: string;
}) {
  const reduzir = useReducedMotion();
  const palavras = texto.split(/(\s+)/); // mantém os espaços
  const total = palavras.length;
  const [mostradas, setMostradas] = useState(reduzir ? total : 0);
  const terminou = useRef(false);
  const fim = useRef(aoTerminar);
  fim.current = aoTerminar;

  useEffect(() => {
    if (reduzir) {
      setMostradas(total);
      return;
    }
    const t = setInterval(() => setMostradas((n) => Math.min(total, n + 2)), msPorPalavra * 2);
    return () => clearInterval(t);
  }, [total, msPorPalavra, reduzir]);

  useEffect(() => {
    if (mostradas >= total && !terminou.current) {
      terminou.current = true;
      fim.current?.();
    }
  }, [mostradas, total]);

  return (
    <p className={className}>
      <span className="sr-only">{texto}</span>
      <span aria-hidden="true">
        {palavras.slice(0, mostradas).join("")}
        {mostradas < total && <span className="ml-0.5 inline-block h-[1.1em] w-[3px] translate-y-[3px] animate-pulse rounded bg-primary" />}
      </span>
    </p>
  );
}

/** Número que sobe de 0 até o valor quando aparece na tela. */
export function Contador({ valor, duracao = 1.6 }: { valor: number; duracao?: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const visivel = useInView(ref, { once: true });
  const reduzir = useReducedMotion();
  const formatar = (n: number) => Math.round(n).toLocaleString("pt-BR");

  useEffect(() => {
    if (!visivel || !ref.current) return;
    if (reduzir) {
      ref.current.textContent = formatar(valor);
      return;
    }
    const controle = animate(0, valor, {
      duration: duracao,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => {
        if (ref.current) ref.current.textContent = formatar(v);
      },
    });
    return () => controle.stop();
  }, [visivel, valor, duracao, reduzir]);

  return (
    <span className="tabular-nums">
      <span className="sr-only">{formatar(valor)}</span>
      <span ref={ref} aria-hidden="true">
        {reduzir ? formatar(valor) : "0"}
      </span>
    </span>
  );
}

/** Barrinhas de equalizador: mostram que o som (ou o microfone) está ativo. */
export function Equalizador({ barras = 4, className = "h-4" }: { barras?: number; className?: string }) {
  return (
    <span aria-hidden="true" className={`inline-flex items-center gap-[3px] ${className}`}>
      {Array.from({ length: barras }, (_, i) => (
        <motion.span
          key={i}
          className="block h-full w-[3px] origin-center rounded-full bg-current"
          initial={{ scaleY: 0.35 }}
          animate={{ scaleY: [0.35, 1, 0.5, 0.85, 0.35] }}
          transition={{ duration: 0.9 + i * 0.13, repeat: Infinity, ease: "easeInOut", delay: i * 0.08 }}
        />
      ))}
    </span>
  );
}

/** Risco animado por cima de um texto (lei revogada). */
export function Riscado({ children, atraso = 0 }: { children: React.ReactNode; atraso?: number }) {
  return (
    <span className="relative inline-block">
      {children}
      <motion.span
        aria-hidden="true"
        className="absolute top-1/2 left-0 h-[2px] w-full origin-left rounded bg-danger"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 0.45, delay: atraso, ease: "easeOut" }}
      />
    </span>
  );
}

/** Bloco cinza com brilho passando, enquanto o conteúdo carrega. */
export function Esqueleto({ className = "" }: { className?: string }) {
  return <span aria-hidden="true" className={`esqueleto block rounded-lg ${className}`} />;
}
