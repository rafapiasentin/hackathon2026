// Compara duas leis artigo por artigo (a antiga e a que a substituiu).
// Leis novas costumam reorganizar a numeração, então cada artigo antigo é casado com o artigo novo
// mais parecido (pelas palavras), e não só pelo número. Depois marcamos palavra por palavra o que mudou.
import type { Artigo, Lei } from "../api/types";
import { PENDENTE } from "../api/mock";
import type { Documento } from "../validador/leitura";
import { validar, type Resultado } from "../validador/regras";

export type TipoMudanca = "alterado" | "novo" | "removido" | "igual";

export interface Pedaco {
  tipo: "igual" | "saiu" | "entrou";
  texto: string;
}

export interface Dispositivo {
  rotulo: string; // "Art. 1º"
  corpo: string; // texto sem o rótulo
}

export interface ItemComparacao {
  tipo: TipoMudanca;
  antigo?: Dispositivo;
  novo?: Dispositivo;
  pedacos?: Pedaco[];
  renumerado?: boolean;
}

export interface Comparacao {
  itens: ItemComparacao[];
  contagem: Record<TipoMudanca, number>;
  temTexto: boolean;
}

const ROTULO = /^\s*(Art(?:igo)?\.?\s*\d+\s*[º°o]?\.?(?:-[A-Z](?=\s))?)\s*[-–—]?\s*/i;
const semAcento = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

function separar(a: Artigo): Dispositivo {
  const m = ROTULO.exec(a.texto);
  if (m) return { rotulo: limparRotulo(m[1]), corpo: a.texto.slice(m[0].length).trim() };
  return { rotulo: limparRotulo(a.artigo), corpo: a.texto.trim() };
}
const limparRotulo = (r: string) => r.replace(/\s+/g, " ").replace(/\s*-\s*$/, "").trim();
const numeroDoRotulo = (r: string) => Number(/\d+/.exec(r)?.[0] ?? 0);

const palavras = (s: string) =>
  semAcento(s)
    .split(/[^a-z0-9$]+/)
    .filter((p) => p.length > 2);

/** Semelhança entre dois textos (0 a 1), pelo conjunto de palavras. */
function semelhanca(a: string, b: string) {
  const A = new Set(palavras(a));
  const B = new Set(palavras(b));
  if (!A.size || !B.size) return 0;
  let comum = 0;
  for (const p of A) if (B.has(p)) comum++;
  return (2 * comum) / (A.size + B.size);
}

const normal = (s: string) => semAcento(s).replace(/\s+/g, " ").replace(/[.;:]$/, "").trim();

/** Diferença palavra por palavra (maior subsequência comum). */
export function diferencaDePalavras(antes: string, depois: string): Pedaco[] {
  const a = antes.split(/\s+/).filter(Boolean);
  const b = depois.split(/\s+/).filter(Boolean);
  const n = a.length, m = b.length;
  const tab: number[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--)
    for (let j = m - 1; j >= 0; j--)
      tab[i][j] = semAcento(a[i]) === semAcento(b[j]) ? tab[i + 1][j + 1] + 1 : Math.max(tab[i + 1][j], tab[i][j + 1]);

  const saida: Pedaco[] = [];
  const por = (tipo: Pedaco["tipo"], palavra: string) => {
    const ultimo = saida[saida.length - 1];
    if (ultimo?.tipo === tipo) ultimo.texto += " " + palavra;
    else saida.push({ tipo, texto: palavra });
  };
  let i = 0, j = 0;
  while (i < n && j < m) {
    if (semAcento(a[i]) === semAcento(b[j])) (por("igual", b[j]), i++, j++);
    else if (tab[i + 1][j] >= tab[i][j + 1]) por("saiu", a[i++]);
    else por("entrou", b[j++]);
  }
  while (i < n) por("saiu", a[i++]);
  while (j < m) por("entrou", b[j++]);
  return saida;
}

export function compararLeis(antiga: Lei, nova: Lei): Comparacao {
  const temTexto = (l: Lei) => l.artigos.some((a) => a.texto && a.texto !== PENDENTE);
  const contagem: Record<TipoMudanca, number> = { alterado: 0, novo: 0, removido: 0, igual: 0 };
  if (!temTexto(antiga) || !temTexto(nova)) return { itens: [], contagem, temTexto: false };

  const A = antiga.artigos.map(separar);
  const N = nova.artigos.map(separar);

  // Casa os pares mais parecidos primeiro
  const pares: { i: number; j: number; s: number }[] = [];
  A.forEach((a, i) =>
    N.forEach((n, j) => {
      const s = semelhanca(a.corpo, n.corpo);
      if (s >= 0.35) pares.push({ i, j, s });
    }),
  );
  pares.sort((x, y) => y.s - x.s);
  const casadoA = new Map<number, number>();
  const casadoN = new Map<number, number>();
  for (const p of pares) {
    if (casadoA.has(p.i) || casadoN.has(p.j)) continue;
    casadoA.set(p.i, p.j);
    casadoN.set(p.j, p.i);
  }

  // Monta a lista na ordem da lei nova, encaixando os artigos que saíram perto de onde estavam
  const itens: ItemComparacao[] = [];
  const removidos = A.map((_, i) => i).filter((i) => !casadoA.has(i));
  const colocarRemovidosAntes = (limite: number) => {
    while (removidos.length && removidos[0] < limite) {
      const i = removidos.shift()!;
      itens.push({ tipo: "removido", antigo: A[i] });
    }
  };
  N.forEach((n, j) => {
    const i = casadoN.get(j);
    if (i === undefined) {
      itens.push({ tipo: "novo", novo: n });
      return;
    }
    colocarRemovidosAntes(i);
    const a = A[i];
    const igual = normal(a.corpo) === normal(n.corpo);
    itens.push({
      tipo: igual ? "igual" : "alterado",
      antigo: a,
      novo: n,
      pedacos: igual ? undefined : diferencaDePalavras(a.corpo, n.corpo),
      renumerado: numeroDoRotulo(a.rotulo) !== numeroDoRotulo(n.rotulo),
    });
  });
  colocarRemovidosAntes(Infinity);

  for (const it of itens) contagem[it.tipo]++;
  return { itens, contagem, temTexto: true };
}

/** Confere o padrão de escrita (LC 95/1998) de uma lei da base, usando o mesmo validador dos arquivos. */
export function padraoDaLei(lei: Lei): Resultado | null {
  const artigos = lei.artigos.filter((a) => a.texto && a.texto !== PENDENTE);
  if (!artigos.length) return null;
  const doc: Documento = {
    nome: lei.titulo,
    tipo: "pdf",
    paginas: 1,
    paragrafos: [
      { texto: lei.titulo },
      ...(lei.ementa ? [{ texto: /^(S[ÚU]MULA|EMENTA)/i.test(lei.ementa) ? lei.ementa : `SÚMULA: ${lei.ementa}` }] : []),
      ...artigos.map((a) => ({ texto: ROTULO.test(a.texto) ? a.texto : `${a.artigo} ${a.texto}` })),
    ],
  };
  // O preâmbulo não vem nos dados da Câmara, então essa regra fica de fora aqui
  return validar(doc, { ignorar: ["preambulo"] });
}
