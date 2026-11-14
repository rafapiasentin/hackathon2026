import { motion } from "motion/react";
import type { Situacao } from "../api/types";
import { SITUACAO } from "../lib/leis";

/**
 * Selo da situação da lei: sempre cor + ícone + texto.
 * Com `animado`, o selo surge e o ícone se desenha (usado quando a resposta acabou de chegar).
 */
export function StatusBadge({
  situacao,
  grande = false,
  animado = false,
  atraso = 0,
}: {
  situacao: Situacao;
  grande?: boolean;
  animado?: boolean;
  atraso?: number;
}) {
  const s = SITUACAO[situacao];
  const Icone = s.icone;
  const classes = `inline-flex items-center gap-1.5 rounded-full border font-semibold whitespace-nowrap ${s.classes} ${
    grande ? "px-4 py-1.5 text-base" : "px-2.5 py-0.5 text-sm"
  }`;
  const tamanho = grande ? "size-5" : "size-4";

  if (!animado) {
    return (
      <span className={classes}>
        <Icone aria-hidden="true" className={tamanho} strokeWidth={2.25} />
        {s.rotulo}
      </span>
    );
  }

  const desenho = (d: number) => ({
    initial: { pathLength: 0 },
    animate: { pathLength: 1 },
    transition: { duration: 0.35, delay: atraso + d, ease: "easeOut" as const },
  });

  return (
    <motion.span
      className={classes}
      initial={{ opacity: 0, scale: 0.85 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", stiffness: 380, damping: 22, delay: atraso }}
    >
      <svg
        viewBox="0 0 24 24"
        aria-hidden="true"
        className={tamanho}
        fill="none"
        stroke="currentColor"
        strokeWidth={2.25}
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {situacao === "vigente_com_alteracoes" ? (
          <>
            <motion.path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" {...desenho(0)} />
            <motion.path d="M12 9v4" {...desenho(0.3)} />
            <motion.path d="M12 17h.01" {...desenho(0.45)} />
          </>
        ) : (
          <>
            <motion.circle cx="12" cy="12" r="10" {...desenho(0)} />
            {situacao === "vigente" ? (
              <motion.path d="m8 12.5 2.8 2.8L16.5 9.5" {...desenho(0.3)} />
            ) : (
              <>
                <motion.path d="m15 9-6 6" {...desenho(0.3)} />
                <motion.path d="m9 9 6 6" {...desenho(0.42)} />
              </>
            )}
          </>
        )}
      </svg>
      {s.rotulo}
    </motion.span>
  );
}
