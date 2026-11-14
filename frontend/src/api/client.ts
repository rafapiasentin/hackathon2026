// Camada de acesso aos dados.
// Com VITE_API_URL definido, chama o backend. Sem ele, usa os dados de exemplo (mock.ts).
// O contrato esperado do backend está em frontend/README.md.
import type { Fonte, Lei, LeiResumo, Resposta, ResultadoBusca, Situacao } from "./types";
import { LEIS, respostaExemplo } from "./mock";
import { eSoReferencia, lerReferencia, type Referencia } from "../lib/referencia";
import { ementaLimpa, nomeLei, numeroLegivel } from "../lib/leis";

const API = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") || "";
export const MODO_EXEMPLO = !API;

async function get<T>(caminho: string): Promise<T> {
  const r = await fetch(API + caminho);
  if (!r.ok) throw new Error(`Erro ${r.status} ao buscar ${caminho}`);
  return r.json() as Promise<T>;
}

const esperar = (ms: number) => new Promise((ok) => setTimeout(ok, ms));
const semAcento = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export async function perguntar(pergunta: string): Promise<Resposta> {
  // "Lei 14.294/2026" ou "me mostra a lei 14294": mostra a lei direto, sem passar pela IA
  // No chat, um número sozinho ("14294") também é tratado como número de lei
  const soNumero = /^\s*(\d{1,3}(?:\.\d{3})+|\d{1,6})\s*$/.exec(pergunta);
  const ref = lerReferencia(pergunta) ?? (soNumero ? { numero: soNumero[1].replace(/\./g, "") } : null);
  if (ref && (soNumero || eSoReferencia(pergunta))) {
    if (MODO_EXEMPLO) await esperar(500);
    return respostaDaLei(ref);
  }

  if (MODO_EXEMPLO) {
    await esperar(900);
    const r = respostaExemplo(pergunta);
    // Pergunta com número de lei que o exemplo não conhece: ao menos mostra a lei citada
    return r.fontes.length === 0 && ref ? respostaDaLei(ref) : r;
  }
  const r = await fetch(`${API}/api/perguntar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pergunta }),
  });
  if (!r.ok) throw new Error(`Erro ${r.status} ao perguntar`);
  return r.json();
}

/**
 * Busca de leis. Se o texto for o número de uma lei ("Lei 14.294/2026"),
 * procura pelo número (e pelo ano, se veio); senão, procura no texto.
 */
export async function buscarLeis(q: string, situacao: Situacao | "todas", pagina = 1): Promise<ResultadoBusca> {
  const ref = lerReferencia(q);
  if (MODO_EXEMPLO) {
    await esperar(250);
    const termo = semAcento(q.trim());
    const itens: LeiResumo[] = LEIS.filter(
      (l) =>
        (situacao === "todas" || l.situacao === situacao) &&
        (ref
          ? l.chave === ref.numero && (!ref.ano || l.ano === ref.ano)
          : !termo || semAcento(`${l.chave} ${l.ano} ${l.ementa} ${l.titulo}`).includes(termo)),
    );
    return { total: itens.length, pagina: 1, itens };
  }
  const p = new URLSearchParams({ q, pagina: String(pagina) });
  if (ref) {
    p.set("numero", ref.numero);
    if (ref.ano) p.set("ano", ref.ano);
  }
  if (situacao !== "todas") p.set("situacao", situacao);
  return get(`/api/leis?${p}`);
}

export async function obterLei(id: string): Promise<Lei | null> {
  if (MODO_EXEMPLO) {
    await esperar(200);
    return LEIS.find((l) => l.id === id) ?? null;
  }
  try {
    return await get<Lei>(`/api/leis/${encodeURIComponent(id)}`);
  } catch {
    return null;
  }
}

// ---------- Resposta montada no próprio front quando a pessoa pede uma lei pelo número ----------

const comoFonte = (l: LeiResumo): Fonte => ({
  lei_id: l.id,
  chave: l.chave,
  ano: l.ano,
  ementa: l.ementa,
  situacao: l.situacao,
  artigo: null,
  trecho: null,
  link: l.link,
});

async function respostaDaLei(ref: Referencia): Promise<Resposta> {
  const pedida = ref.ano ? nomeLei(ref.numero, ref.ano) : `Lei ${numeroLegivel(ref.numero)}`;
  let itens: LeiResumo[];
  try {
    ({ itens } = await buscarLeis(`Lei ${ref.numero}${ref.ano ? "/" + ref.ano : ""}`, "todas"));
  } catch {
    itens = [];
  }

  if (itens.length === 0) {
    return {
      resposta: `Não encontrei a ${pedida} ${MODO_EXEMPLO ? "nos dados de exemplo" : "na base de leis de Londrina"}. Confira o número e o ano.`,
      fontes: [],
      ignoradas: [],
    };
  }
  if (itens.length > 1) {
    return {
      resposta: `Encontrei ${itens.length} leis com o número ${numeroLegivel(ref.numero)}. Escolha a que você procura:`,
      fontes: itens.map(comoFonte),
      ignoradas: [],
    };
  }

  const resumo = itens[0];
  const lei = await obterLei(resumo.id);
  const nome = nomeLei(resumo.chave, resumo.ano);
  const ementa = `“${ementaLimpa(resumo.ementa)}”`;
  const relacoes = lei?.relacoes ?? [];
  const lista = (tipo: string) =>
    relacoes
      .filter((r) => r.tipo === tipo)
      .map((r) => `Lei ${numeroLegivel(r.chave)}`)
      .join(", ");

  const fontes: Fonte[] = [comoFonte(resumo)];
  let texto: string;

  if (resumo.vigencia_verificada === false) {
    texto = `Consulta documental: a revisão institucional de vigência da ${nome} ainda está pendente. A situação informada no catálogo da Câmara é “${resumo.situacao}”. Resumo oficial: ${ementa}`;
  } else if (resumo.situacao === "revogada") {
    const por = relacoes.filter((r) => r.tipo === "revogada_por");
    texto = por.length
      ? `A ${nome} consta como revogada na fonte. Leis relacionadas à revogação: ${lista("revogada_por")}. Esses vínculos podem incluir revogações parciais e não comprovam, sozinhos, qual norma a substitui integralmente. Resumo oficial da lei antiga: ${ementa}`
      : `A ${nome} não vale mais: ela foi revogada. Resumo oficial: ${ementa}`;
    // Exibe as leis relacionadas sem presumir substituição integral.
    for (const r of por) {
      const nova = r.id ? await obterLei(r.id) : null;
      if (nova) fontes.push(comoFonte(nova));
    }
  } else if (resumo.situacao === "vigente_com_alteracoes") {
    const alteradaPor = lista("alterada_por");
    texto = `A ${nome} está em vigor, mas partes dela foram mudadas depois${alteradaPor ? ` pela ${alteradaPor}` : ""}. Resumo oficial: ${ementa}`;
  } else if (resumo.situacao === "inexistente") {
    texto = `O número ${numeroLegivel(resumo.chave)} consta como inexistente no catálogo da Câmara. Este registro não deve ser usado como uma lei em vigor.`;
  } else {
    texto = `A ${nome} está em vigor. Resumo oficial: ${ementa}`;
  }

  return { resposta: texto, fontes, ignoradas: [] };
}
