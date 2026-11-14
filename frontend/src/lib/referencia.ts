// Reconhece quando a pessoa digitou o número de uma lei, em vez de um assunto.
// Exemplos aceitos: "Lei 14.294/2026", "lei nº 14294", "Lei Municipal n.º 14.294, de 2026",
// "14.294/2026", "14294/26", "LEI N.º 14294, DE 29 DE OUTUBRO DE 2026".
// Um número sozinho ("14294" ou "2026") continua sendo busca por texto, porque pode ser um ano.

export interface Referencia {
  numero: string; // sem pontos, igual à "chave" do leis.json
  ano?: string;
}

const PADRAO = new RegExp(
  [
    "(?:(lei)(?:\\s+(?:municipal|complementar|ordin[aá]ria))?\\s*)?", // 1: palavra "lei"
    "(n\\.?\\s*[º°o]?\\.?\\s*)?", //                                     2: "nº", "n.º", "no"
    "(\\d{1,3}(?:\\.\\d{3})+|\\d{1,6})", //                              3: número
    "(?:\\s*\\/\\s*(\\d{4}|\\d{2})\\b", //                               4: "/2026" ou "/26"
    "|\\s*,?\\s+de\\s+(?:\\d{1,2}\\s+de\\s+[a-zç]+\\s+de\\s+)?(\\d{4})\\b)?", // 5: ", de 2026" ou ", de 29 de outubro de 2026"
  ].join(""),
  "i",
);

function anoCompleto(ano: string) {
  if (ano.length === 4) return ano;
  const n = Number(ano);
  return String(n > 40 ? 1900 + n : 2000 + n);
}

export function lerReferencia(texto: string): Referencia | null {
  const m = PADRAO.exec(texto);
  if (!m) return null;
  const [, palavraLei, nro, numeroBruto, anoBarra, anoExtenso] = m;
  const ano = anoBarra ?? anoExtenso;
  const temPonto = numeroBruto.includes(".");
  // Só vale como referência se houver algo que diga "isto é uma lei"
  if (!palavraLei && !nro && !temPonto && !ano) return null;
  const numero = numeroBruto.replace(/\./g, "").replace(/^0+/, "");
  if (!numero) return null;
  return { numero, ano: ano ? anoCompleto(ano) : undefined };
}

// Palavras que não mudam o sentido de "quero ver a lei X"
const VAZIAS = new Set(
  "a o as os e de da do das dos me mostra mostre ver veja quero queria pesquisar pesquisa buscar busca procurar procuro abrir abre sobre qual quais é e o que fala diz diga que lei leis municipal numero número nº n favor por pfv prfv".split(
    " ",
  ),
);

/** true quando a pergunta é basicamente só o número da lei ("Lei 14.294/2026", "me mostra a lei 14294"). */
export function eSoReferencia(texto: string): boolean {
  const m = PADRAO.exec(texto);
  if (!m) return false;
  const resto = (texto.slice(0, m.index) + " " + texto.slice(m.index + m[0].length))
    .toLowerCase()
    .replace(/[?!.,:;"“”]/g, " ")
    .split(/\s+/)
    .filter((p) => p && !VAZIAS.has(p));
  return resto.length === 0;
}
