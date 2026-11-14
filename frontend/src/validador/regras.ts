// Regras de redação de leis da Lei Complementar nº 95/1998 (com o formato de título usado pela Câmara de Londrina).
// São regras fixas: sempre dão o mesmo resultado e cada erro aponta o trecho e como corrigir.
import type { Documento, Paragrafo } from "./leitura";

export type Gravidade = "erro" | "aviso";

export interface Problema {
  gravidade: Gravidade;
  titulo: string;
  explicacao: string;
  encontrado?: string;
  esperado?: string;
  /** Índice do parágrafo no documento, para destacar e rolar até ele */
  linha?: number;
}

export interface Checagem {
  id: string;
  nome: string;
  base: string;
  problemas: Problema[];
}

export interface Resultado {
  conforme: boolean;
  erros: number;
  avisos: number;
  checagens: Checagem[];
}

const MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
const semAcento = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const indiceMes = (nome: string) => MESES.findIndex((m) => semAcento(m) === semAcento(nome));
const diasNoMes = (m: number, a: number) => new Date(a, m + 1, 0).getDate();
const maiuscula = (s: string) => s === s.toLocaleUpperCase("pt-BR");
const comPonto = (n: string) => Number(n).toLocaleString("pt-BR");
const curto = (s: string, max = 140) => (s.length > max ? s.slice(0, max - 1) + "…" : s);

function dataExtenso(dia: number, mes: number, ano: number | string) {
  return `${dia === 1 ? "1º" : dia} DE ${MESES[mes].toUpperCase()} DE ${ano}`;
}

function romano(n: number) {
  const tabela: [number, string][] = [[100, "C"], [90, "XC"], [50, "L"], [40, "XL"], [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]];
  let s = "";
  for (const [v, r] of tabela) while (n >= v) (s += r), (n -= v);
  return s;
}
function deRomano(s: string) {
  const v: Record<string, number> = { I: 1, V: 5, X: 10, L: 50, C: 100 };
  let total = 0;
  for (let i = 0; i < s.length; i++) {
    const a = v[s[i]], b = v[s[i + 1]] ?? 0;
    total += a < b ? -a : a;
  }
  return total;
}

// ---------------------------------------------------------------- Leitura das datas

type DataLida =
  | { forma: "extenso"; dia: number; mes: number; ano: number; texto: string; zero: boolean; semOrdinal: boolean }
  | { forma: "mes-invalido"; texto: string; mes: string }
  | { forma: "numerica"; dia: number; mes: number; ano: number; texto: string }
  | { forma: "so-ano"; ano: number; texto: string }
  | { forma: "nenhuma" };

function lerData(s: string): DataLida {
  const num = /(\d{1,2})\/(\d{1,2})\/(\d{2,4})/.exec(s);
  if (num) {
    const ano = num[3].length === 2 ? 2000 + Number(num[3]) : Number(num[3]);
    return { forma: "numerica", dia: Number(num[1]), mes: Number(num[2]) - 1, ano, texto: num[0] };
  }
  const ext = /(\d{1,2})\s*([º°o])?\s+de\s+([A-Za-zÀ-ÿçÇ]+)\s+de\s+(\d{4})/i.exec(s);
  if (ext) {
    const mes = indiceMes(ext[3]);
    if (mes < 0) return { forma: "mes-invalido", texto: ext[0], mes: ext[3] };
    return {
      forma: "extenso",
      dia: Number(ext[1]),
      mes,
      ano: Number(ext[4]),
      texto: ext[0],
      zero: ext[1].length === 2 && ext[1].startsWith("0"),
      semOrdinal: Number(ext[1]) === 1 && !ext[2],
    };
  }
  const ano = /\bde\s+(\d{4})\b/i.exec(s);
  if (ano) return { forma: "so-ano", ano: Number(ano[1]), texto: ano[0] };
  return { forma: "nenhuma" };
}

// ---------------------------------------------------------------- Validação

export function validar(doc: Documento, opcoes: { ignorar?: string[] } = {}): Resultado {
  const ps = doc.paragrafos;
  const checagens: Checagem[] = [];

  if (doc.tipo === "xml") {
    checagens.push({ id: "xml", nome: "Estrutura do XML (LexML)", base: "Padrão LexML Brasil", problemas: doc.estrutura ?? [] });
  }

  // Posições importantes do documento
  const iTitulo = ps.slice(0, 5).findIndex((p) => /^\s*LEI\b/i.test(p.texto));
  const ehArtigo = (p: Paragrafo) => /^Art(igo)?\.?\s*\d/i.test(p.texto);
  const iPrimeiroArt = ps.findIndex(ehArtigo);
  const iPreambulo = ps.findIndex(
    (p, i) => i > iTitulo && (iPrimeiroArt < 0 || i < iPrimeiroArt) && /SANCIONO|PROMULGO|APROVOU|DECRETA/i.test(p.texto),
  );

  // 1. Título (epígrafe) e 2. Data
  const titulo: Problema[] = [];
  const data: Problema[] = [];
  if (iTitulo < 0) {
    titulo.push({
      gravidade: "erro",
      titulo: "Título da lei não encontrado",
      explicacao: "A lei deve começar pelo título (epígrafe), com a espécie, o número e a data.",
      esperado: "LEI Nº 14.300, DE 11 DE NOVEMBRO DE 2026",
    });
  } else {
    const t = ps[iTitulo].texto.trim();
    const numero = /N\s*\.?\s*[º°o]?\s*\.?\s*(\d{1,3}(?:\.\d{3})+|\d+)/i.exec(t)?.[1] ?? /(\d{1,3}(?:\.\d{3})+|\d{2,6})/.exec(t)?.[1];
    const d = lerData(t);
    const especie = /^LEI\s+COMPLEMENTAR/i.test(t) ? "LEI COMPLEMENTAR" : "LEI";
    const dataCerta =
      d.forma === "extenso" ? dataExtenso(d.dia, d.mes, d.ano) : d.forma === "numerica" && d.mes >= 0 && d.mes < 12 ? dataExtenso(d.dia, d.mes, d.ano) : "DIA DE MÊS DE ANO";
    const esperado = `${especie} Nº ${numero ? comPonto(numero.replace(/\./g, "")) : "0.000"}, DE ${dataCerta}`;

    const motivos: string[] = [];
    if (!maiuscula(t)) motivos.push("deve estar todo em letras maiúsculas");
    if (!/^LEI(\s+COMPLEMENTAR)?\s+N\s*\.?\s*[º°]/i.test(t)) motivos.push("falta o “Nº” antes do número");
    if (!numero) motivos.push("falta o número da lei");
    if (!/\d\s*,\s*DE\s/i.test(t)) motivos.push("falta a vírgula e o “DE” entre o número e a data");
    if (d.forma !== "extenso") motivos.push("a data deve vir por extenso");

    if (motivos.length) {
      titulo.push({
        gravidade: "erro",
        titulo: "Título fora do padrão",
        explicacao: `O título ${motivos.join("; ")}.`,
        encontrado: t,
        esperado,
        linha: iTitulo,
      });
    } else if (numero && !numero.includes(".") && Number(numero) >= 1000) {
      titulo.push({
        gravidade: "aviso",
        titulo: "Número da lei sem ponto",
        explicacao: "Números com mais de três algarismos levam ponto separando os milhares.",
        encontrado: `Nº ${numero}`,
        esperado: `Nº ${comPonto(numero)}`,
        linha: iTitulo,
      });
    }

    if (d.forma === "numerica") {
      data.push({
        gravidade: "erro",
        titulo: "Data fora do padrão",
        explicacao: "No título, a data é escrita por extenso, com o mês em letras.",
        encontrado: d.texto,
        esperado: d.mes >= 0 && d.mes < 12 ? dataExtenso(d.dia, d.mes, d.ano) : "DIA DE MÊS DE ANO",
        linha: iTitulo,
      });
    } else if (d.forma === "so-ano") {
      data.push({
        gravidade: "erro",
        titulo: "Data incompleta",
        explicacao: "O título tem só o ano. Ele deve ter o dia, o mês e o ano da lei.",
        encontrado: d.texto.toUpperCase(),
        esperado: `DE ${"DIA"} DE MÊS DE ${d.ano}`,
        linha: iTitulo,
      });
    } else if (d.forma === "nenhuma") {
      data.push({ gravidade: "erro", titulo: "Data não encontrada no título", explicacao: "O título deve terminar com a data da lei por extenso.", esperado: esperado, linha: iTitulo });
    } else if (d.forma === "mes-invalido") {
      data.push({ gravidade: "erro", titulo: "Mês não reconhecido", explicacao: `“${d.mes}” não é um mês. Confira a grafia.`, encontrado: d.texto, linha: iTitulo });
    } else {
      if (d.dia < 1 || d.dia > diasNoMes(d.mes, d.ano))
        data.push({
          gravidade: "erro",
          titulo: "Data inválida",
          explicacao: `${MESES[d.mes]} de ${d.ano} não tem o dia ${d.dia}.`,
          encontrado: d.texto,
          linha: iTitulo,
        });
      if (d.zero)
        data.push({ gravidade: "aviso", titulo: "Zero à esquerda no dia", explicacao: "O dia é escrito sem zero à esquerda.", encontrado: d.texto, esperado: dataExtenso(d.dia, d.mes, d.ano), linha: iTitulo });
      if (d.semOrdinal)
        data.push({ gravidade: "aviso", titulo: "Primeiro dia do mês", explicacao: "O primeiro dia do mês se escreve “1º”.", encontrado: d.texto, esperado: dataExtenso(1, d.mes, d.ano), linha: iTitulo });
    }

    // Data no fecho ("Londrina, 11 de novembro de 2026.")
    const iFecho = ps.findIndex((p, i) => i > iTitulo && /^Londrina\s*,/i.test(p.texto));
    if (iFecho >= 0) {
      const f = lerData(ps[iFecho].texto);
      if (f.forma === "numerica") {
        data.push({
          gravidade: "erro",
          titulo: "Data do fecho fora do padrão",
          explicacao: "No fecho (local e data no fim da lei), a data também é escrita por extenso.",
          encontrado: ps[iFecho].texto,
          esperado: f.mes >= 0 && f.mes < 12 ? `Londrina, ${f.dia} de ${MESES[f.mes]} de ${f.ano}.` : undefined,
          linha: iFecho,
        });
      } else if (f.forma === "extenso" && d.forma === "extenso" && (f.dia !== d.dia || f.mes !== d.mes || f.ano !== d.ano)) {
        data.push({
          gravidade: "aviso",
          titulo: "Data do fecho diferente da data do título",
          explicacao: "A data no fim da lei não bate com a data do título. Confira qual está certa.",
          encontrado: ps[iFecho].texto,
          esperado: `Londrina, ${d.dia} de ${MESES[d.mes]} de ${d.ano}.`,
          linha: iFecho,
        });
      }
    }
  }
  checagens.push({ id: "titulo", nome: "Título (epígrafe)", base: "LC 95/1998, art. 4º", problemas: titulo });
  checagens.push({ id: "data", nome: "Data da lei", base: "LC 95/1998, art. 4º", problemas: data });

  // 3. Ementa
  const ementa: Problema[] = [];
  const fimEmenta = iPreambulo >= 0 ? iPreambulo : iPrimeiroArt >= 0 ? iPrimeiroArt : ps.length;
  if (iTitulo >= 0 && fimEmenta - iTitulo <= 1) {
    ementa.push({
      gravidade: "erro",
      titulo: "Falta a ementa (súmula)",
      explicacao: "Logo abaixo do título deve vir um resumo curto do que a lei trata.",
      esperado: "SÚMULA: Institui o Programa Municipal de ...",
      linha: iTitulo,
    });
  }
  checagens.push({ id: "ementa", nome: "Ementa (súmula)", base: "LC 95/1998, art. 5º", problemas: ementa });

  // 4. Preâmbulo
  const preambulo: Problema[] = [];
  if (iPreambulo < 0) {
    preambulo.push({
      gravidade: "aviso",
      titulo: "Preâmbulo não encontrado",
      explicacao: "Antes dos artigos, o preâmbulo indica quem aprovou e sancionou a lei.",
      esperado: "A CÂMARA MUNICIPAL DE LONDRINA, ESTADO DO PARANÁ, APROVOU E EU, PREFEITO DO MUNICÍPIO, SANCIONO A SEGUINTE LEI:",
      linha: iPrimeiroArt >= 0 ? iPrimeiroArt : undefined,
    });
  }
  checagens.push({ id: "preambulo", nome: "Preâmbulo", base: "LC 95/1998, art. 6º", problemas: preambulo });

  // 5. Artigos, 6. Parágrafos, 7. Incisos e alíneas
  const artigos: Problema[] = [];
  const paragrafos: Problema[] = [];
  const incisos: Problema[] = [];
  let artAnterior = 0;
  let paragrafosDoArt: { n: number; linha: number }[] = [];
  let incisoAnterior = 0;
  let alineaAnterior = "";
  const tracos: { linha: number; encontrado: string; esperado: string }[] = [];

  const fecharArtigo = () => {
    if (paragrafosDoArt.length === 1 && paragrafosDoArt[0].n === 1) {
      paragrafos.push({
        gravidade: "erro",
        titulo: "Parágrafo único numerado",
        explicacao: "Quando o artigo tem um só parágrafo, ele se chama “Parágrafo único”, por extenso.",
        encontrado: curto(ps[paragrafosDoArt[0].linha].texto, 60),
        esperado: "Parágrafo único. ...",
        linha: paragrafosDoArt[0].linha,
      });
    }
    paragrafosDoArt = [];
  };

  if (iPrimeiroArt < 0) {
    artigos.push({ gravidade: "erro", titulo: "Nenhum artigo encontrado", explicacao: "O texto da lei é dividido em artigos: “Art. 1º”, “Art. 2º”…" });
  }

  ps.forEach((p, i) => {
    const t = p.texto;
    const art = /^(Art(?:igo)?)(\.?)\s*(\d+)\s*([º°o])?(\.)?(?:-([A-Z])(?=\s))?/i.exec(t);
    if (art) {
      fecharArtigo();
      incisoAnterior = 0;
      alineaAnterior = "";
      const [, palavra, ponto, nStr, ordinal, , letra] = art;
      const n = Number(nStr);
      const certo = n <= 9 ? `Art. ${n}º` : `Art. ${n}.`;
      const motivos: string[] = [];
      if (/^artigo$/i.test(palavra)) motivos.push("a palavra “artigo” é abreviada como “Art.”");
      else if (palavra !== "Art") motivos.push("escreva “Art.” com só a primeira letra maiúscula");
      else if (!ponto) motivos.push("falta o ponto em “Art.”");
      if (n <= 9 && !ordinal) motivos.push("do 1º ao 9º, o número é ordinal (com º)");
      if (n >= 10 && ordinal) motivos.push("a partir do 10, o número é cardinal, sem º");
      // Padrão antigo: "Art. 1º - Texto" (com traço). Hoje o texto vem direto depois do número.
      const traco = /^Art(?:igo)?\.?\s*\d+\s*[º°o]?\.?\s*[-–—]\s/i.exec(t);
      if (traco && !motivos.length) tracos.push({ linha: i, encontrado: traco[0].trim(), esperado: certo });
      if (motivos.length)
        artigos.push({
          gravidade: "erro",
          titulo: `Numeração do artigo fora do padrão`,
          explicacao: `${motivos.join("; ")}.`.replace(/^./, (c) => c.toUpperCase()),
          encontrado: art[0].trim(),
          esperado: letra ? `${certo.replace(/\.$/, "")}-${letra}` : certo,
          linha: i,
        });
      if (!letra) {
        if (n === artAnterior)
          artigos.push({ gravidade: "erro", titulo: "Artigo repetido", explicacao: `Existem dois artigos com o número ${n}.`, encontrado: art[0].trim(), linha: i });
        else if (n !== artAnterior + 1)
          artigos.push({
            gravidade: "erro",
            titulo: "Numeração dos artigos fora de ordem",
            explicacao: artAnterior
              ? `Depois do Art. ${artAnterior}${artAnterior <= 9 ? "º" : ""} deveria vir o Art. ${artAnterior + 1}${artAnterior + 1 <= 9 ? "º" : ""}.`
              : "A lei deve começar pelo Art. 1º.",
            encontrado: art[0].trim(),
            esperado: artAnterior + 1 <= 9 ? `Art. ${artAnterior + 1}º` : `Art. ${artAnterior + 1}.`,
            linha: i,
          });
        artAnterior = n;
      }
      return;
    }

    // Parágrafos
    const par = /^(§{1,2})\s*(\d+|[úu]nico)\s*([º°o])?/i.exec(t);
    const parExtenso = /^Par[áa]grafo\s+([úu]nico|\d+\s*[º°o]?)/i.exec(t);
    if (par || parExtenso) {
      incisoAnterior = 0;
      alineaAnterior = "";
      if (par && /[úu]nico/i.test(par[2])) {
        paragrafos.push({ gravidade: "erro", titulo: "“§ único” fora do padrão", explicacao: "O parágrafo único é escrito por extenso.", encontrado: par[0], esperado: "Parágrafo único.", linha: i });
      } else if (parExtenso && !/[úu]nico/i.test(parExtenso[1])) {
        paragrafos.push({
          gravidade: "erro",
          titulo: "Parágrafo numerado por extenso",
          explicacao: "Parágrafos numerados usam o símbolo §.",
          encontrado: parExtenso[0],
          esperado: `§ ${parseInt(parExtenso[1])}º`,
          linha: i,
        });
      } else if (par) {
        const n = Number(par[2]);
        if (n <= 9 && !par[3])
          paragrafos.push({ gravidade: "erro", titulo: "Parágrafo sem o º", explicacao: "Do § 1º ao § 9º, o número é ordinal.", encontrado: par[0], esperado: `§ ${n}º`, linha: i });
        if (n >= 10 && par[3])
          paragrafos.push({ gravidade: "erro", titulo: "Parágrafo com º depois do 9", explicacao: "A partir do § 10, o número é cardinal.", encontrado: par[0], esperado: `§ ${n}.`, linha: i });
        paragrafosDoArt.push({ n, linha: i });
      }
      return;
    }

    // Incisos (algarismos romanos) e alíneas (letras minúsculas)
    const inciso = /^([IVXLC]+)\s*[-–—]\s+/.exec(t);
    const incisoArabico = /^(\d+)\s*[-–—)]\s+/.exec(t);
    const alinea = /^([a-zA-Z])\)\s+/.exec(t);
    if (inciso) {
      const n = deRomano(inciso[1]);
      if (n !== incisoAnterior + 1)
        incisos.push({
          gravidade: "erro",
          titulo: "Incisos fora de ordem",
          explicacao: `Depois do inciso ${romano(incisoAnterior) || "(início)"} deveria vir o ${romano(incisoAnterior + 1)}.`,
          encontrado: inciso[0].trim(),
          esperado: `${romano(incisoAnterior + 1)} -`,
          linha: i,
        });
      incisoAnterior = n;
      alineaAnterior = "";
    } else if (incisoArabico && iPrimeiroArt >= 0 && i > iPrimeiroArt) {
      const n = Number(incisoArabico[1]);
      incisos.push({
        gravidade: "erro",
        titulo: "Inciso com número comum",
        explicacao: "Incisos são numerados com algarismos romanos (I, II, III…).",
        encontrado: incisoArabico[0].trim(),
        esperado: `${romano(n)} -`,
        linha: i,
      });
      incisoAnterior = n;
    } else if (alinea) {
      const letra = alinea[1];
      const esperada = alineaAnterior ? String.fromCharCode(alineaAnterior.charCodeAt(0) + 1) : "a";
      if (letra !== letra.toLowerCase())
        incisos.push({ gravidade: "erro", titulo: "Alínea com letra maiúscula", explicacao: "Alíneas usam letras minúsculas: a), b), c)…", encontrado: alinea[0].trim(), esperado: `${letra.toLowerCase()})`, linha: i });
      else if (letra !== esperada)
        incisos.push({ gravidade: "erro", titulo: "Alíneas fora de ordem", explicacao: `Deveria vir a alínea ${esperada}).`, encontrado: alinea[0].trim(), esperado: `${esperada})`, linha: i });
      alineaAnterior = letra.toLowerCase();
    }
  });
  fecharArtigo();
  if (tracos.length)
    artigos.push({
      gravidade: "aviso",
      titulo: "Traço depois do número do artigo",
      explicacao: `Padrão antigo: hoje o texto vem logo depois do número, sem traço.${tracos.length > 1 ? ` Aparece em ${tracos.length} artigos.` : ""}`,
      encontrado: tracos[0].encontrado,
      esperado: tracos[0].esperado,
      linha: tracos[0].linha,
    });

  checagens.push({ id: "artigos", nome: "Artigos", base: "LC 95/1998, art. 10, I", problemas: artigos });
  checagens.push({ id: "paragrafos", nome: "Parágrafos", base: "LC 95/1998, art. 10, III", problemas: paragrafos });
  checagens.push({ id: "incisos", nome: "Incisos e alíneas", base: "LC 95/1998, art. 10, IV", problemas: incisos });

  // 8. Vigência
  const vigencia: Problema[] = [];
  if (!ps.some((p) => /entra(r[áa])?\s+em\s+vigor/i.test(p.texto))) {
    vigencia.push({
      gravidade: "erro",
      titulo: "Falta a cláusula de vigência",
      explicacao: "A lei precisa dizer quando começa a valer.",
      esperado: "Art. Xº Esta Lei entra em vigor na data de sua publicação.",
    });
  }
  checagens.push({ id: "vigencia", nome: "Cláusula de vigência", base: "LC 95/1998, art. 8º", problemas: vigencia });

  // 9. Revogação
  const revogacao: Problema[] = [];
  ps.forEach((p, i) => {
    if (/revogam-se\s+as\s+disposi[çc][õo]es\s+em\s+contr[áa]rio/i.test(p.texto))
      revogacao.push({
        gravidade: "erro",
        titulo: "Revogação genérica não é permitida",
        explicacao: "A cláusula de revogação deve citar quais leis ou artigos são revogados. Se nada for revogado, retire o artigo.",
        encontrado: curto(p.texto, 80),
        esperado: "Fica revogada a Lei nº 0.000, de 1º de janeiro de 2000.",
        linha: i,
      });
  });
  checagens.push({ id: "revogacao", nome: "Cláusula de revogação", base: "LC 95/1998, art. 9º", problemas: revogacao });

  if (opcoes.ignorar?.length) {
    for (let k = checagens.length - 1; k >= 0; k--) if (opcoes.ignorar.includes(checagens[k].id)) checagens.splice(k, 1);
  }
  const todos = checagens.flatMap((c) => c.problemas);
  const erros = todos.filter((p) => p.gravidade === "erro").length;
  return { conforme: erros === 0, erros, avisos: todos.length - erros, checagens };
}
