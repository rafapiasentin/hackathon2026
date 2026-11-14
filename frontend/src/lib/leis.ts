import { CircleCheck, CircleX, TriangleAlert, type LucideIcon } from "lucide-react";
import type { Situacao, TipoRelacao } from "../api/types";

/** Linguagem simples para a situação. A cor nunca aparece sozinha: sempre com ícone e texto. */
export const SITUACAO: Record<Situacao, { rotulo: string; explicacao: string; icone: LucideIcon; classes: string }> = {
  vigente: {
    rotulo: "Em vigor",
    explicacao: "Esta lei vale hoje.",
    icone: CircleCheck,
    classes: "bg-ok-soft text-ok border-ok/30",
  },
  vigente_com_alteracoes: {
    rotulo: "Vale, com mudanças",
    explicacao: "Esta lei vale hoje, mas partes dela foram alteradas por outras leis.",
    icone: TriangleAlert,
    classes: "bg-warn-soft text-warn border-warn/30",
  },
  revogada: {
    rotulo: "Não vale mais",
    explicacao: "Esta lei foi revogada e não deve ser usada.",
    icone: CircleX,
    classes: "bg-danger-soft text-danger border-danger/30",
  },
  inexistente: {
    rotulo: "Número inexistente",
    explicacao: "Este número ficou vago no catálogo e não identifica uma lei publicada.",
    icone: CircleX,
    classes: "bg-warn-soft text-warn border-warn/30",
  },
};

export const RELACAO: Record<TipoRelacao, string> = {
  altera: "Altera",
  alterada_por: "Foi alterada por",
  revoga: "Revoga",
  revogada_por: "Foi revogada por",
};

/** "14294" -> "14.294"; "520-A" continua "520-A". */
export function numeroLegivel(chave: string) {
  const m = chave.match(/^(\d+)(.*)$/);
  if (!m) return chave;
  return Number(m[1]).toLocaleString("pt-BR") + m[2];
}

export function nomeLei(chave: string, ano: string) {
  return `Lei ${numeroLegivel(chave)}/${ano}`;
}

export function dataLegivel(iso: string | null, ano: string) {
  if (!iso) return ano;
  const [a, m, d] = iso.split("-").map(Number);
  return new Date(a, m - 1, d).toLocaleDateString("pt-BR", { day: "numeric", month: "long", year: "numeric" });
}

/** Tira o "SÚMULA:" que as leis novas trazem na ementa. */
export function ementaLimpa(ementa: string | null | undefined) {
  return ementa?.replace(/^\s*S[ÚU]MULA:\s*/i, "").trim() || "Ementa não disponível na fonte.";
}
