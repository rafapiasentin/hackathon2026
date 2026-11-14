// Leitura do arquivo enviado: transforma PDF (com texto ou escaneado), imagem ou XML em parágrafos de texto.
// Tudo roda no navegador. As bibliotecas pesadas (pdf.js e OCR) só carregam quando alguém usa o validador.
import type { Problema } from "./regras";

export type TipoArquivo = "pdf" | "pdf-escaneado" | "imagem" | "xml";

export interface Paragrafo {
  texto: string;
  pagina?: number;
}

export interface Documento {
  nome: string;
  tipo: TipoArquivo;
  paginas: number;
  paragrafos: Paragrafo[];
  /** Problemas de estrutura encontrados na própria leitura (ex.: XML fora do LexML) */
  estrutura?: Problema[];
}

export interface Etapa {
  texto: string;
  progresso?: number; // 0 a 1
}

type AoProgresso = (e: Etapa) => void;

export async function lerArquivo(arquivo: Blob, nome: string, aoProgresso: AoProgresso): Promise<Documento> {
  const ext = nome.toLowerCase().split(".").pop() ?? "";
  if (ext === "xml" || arquivo.type.includes("xml")) return lerXml(arquivo, nome, aoProgresso);
  if (ext === "pdf" || arquivo.type === "application/pdf") return lerPdf(arquivo, nome, aoProgresso);
  if (/^(png|jpe?g|webp|bmp)$/.test(ext) || arquivo.type.startsWith("image/")) return lerImagem(arquivo, nome, aoProgresso);
  throw new Error("Formato não aceito. Envie um arquivo PDF, XML ou uma imagem (PNG/JPG).");
}

// ---------------------------------------------------------------- PDF

async function abrirPdfjs() {
  const pdfjs = await import("pdfjs-dist");
  const { default: worker } = await import("pdfjs-dist/build/pdf.worker.min.mjs?url");
  pdfjs.GlobalWorkerOptions.workerSrc = worker;
  return pdfjs;
}

async function lerPdf(arquivo: Blob, nome: string, aoProgresso: AoProgresso): Promise<Documento> {
  aoProgresso({ texto: "Abrindo o PDF" });
  const pdfjs = await abrirPdfjs();
  const pdf = await pdfjs.getDocument({ data: new Uint8Array(await arquivo.arrayBuffer()) }).promise;

  const linhas: Paragrafo[] = [];
  for (let p = 1; p <= pdf.numPages; p++) {
    aoProgresso({ texto: `Lendo o texto do PDF (página ${p} de ${pdf.numPages})`, progresso: p / pdf.numPages });
    const pagina = await pdf.getPage(p);
    const conteudo = await pagina.getTextContent();
    // Agrupa os pedaços de texto por linha (mesma altura na página)
    const porLinha = new Map<number, { x: number; s: string }[]>();
    for (const item of conteudo.items) {
      if (!("str" in item) || !item.str.trim()) continue;
      const y = Math.round(item.transform[5] / 3) * 3;
      const lista = porLinha.get(y) ?? [];
      lista.push({ x: item.transform[4], s: item.str });
      porLinha.set(y, lista);
    }
    [...porLinha.entries()]
      .sort((a, b) => b[0] - a[0])
      .forEach(([, pedacos]) =>
        linhas.push({
          texto: pedacos
            .sort((a, b) => a.x - b.x)
            .map((x) => x.s)
            .join(" ")
            .replace(/\s+/g, " ")
            .trim(),
          pagina: p,
        }),
      );
  }

  const letras = linhas.reduce((n, l) => n + l.texto.length, 0);
  if (letras >= 40 * pdf.numPages) {
    return { nome, tipo: "pdf", paginas: pdf.numPages, paragrafos: juntarLinhas(linhas) };
  }

  // Quase sem texto: é uma imagem escaneada. Desenha cada página e reconhece o texto (OCR).
  aoProgresso({ texto: "Este PDF é uma imagem escaneada. Preparando o reconhecimento de texto (OCR)", progresso: 0 });
  const ocr: Paragrafo[] = [];
  for (let p = 1; p <= pdf.numPages; p++) {
    const pagina = await pdf.getPage(p);
    const viewport = pagina.getViewport({ scale: 2 });
    const canvas = document.createElement("canvas");
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    await pagina.render({ canvasContext: canvas.getContext("2d")!, viewport }).promise;
    const texto = await reconhecer(canvas, (prog) =>
      aoProgresso({
        texto: `Reconhecendo o texto da imagem (página ${p} de ${pdf.numPages})`,
        progresso: (p - 1 + prog) / pdf.numPages,
      }),
    );
    texto.split("\n").forEach((t) => t.trim() && ocr.push({ texto: t.trim(), pagina: p }));
  }
  return { nome, tipo: "pdf-escaneado", paginas: pdf.numPages, paragrafos: juntarLinhas(ocr.map(corrigirOcr)) };
}

// ---------------------------------------------------------------- Imagem / OCR

async function lerImagem(arquivo: Blob, nome: string, aoProgresso: AoProgresso): Promise<Documento> {
  aoProgresso({ texto: "Preparando o reconhecimento de texto (OCR)", progresso: 0 });
  const texto = await reconhecer(arquivo, (prog) => aoProgresso({ texto: "Reconhecendo o texto da imagem", progresso: prog }));
  const linhas = texto
    .split("\n")
    .map((t) => t.trim())
    .filter(Boolean)
    .map((t) => corrigirOcr({ texto: t, pagina: 1 }));
  return { nome, tipo: "imagem", paginas: 1, paragrafos: juntarLinhas(linhas) };
}

// O "trabalhador" do OCR é criado uma vez só (baixa o idioma português na primeira vez e guarda no navegador)
let ocrPronto: Promise<import("tesseract.js").Worker> | null = null;
let aoProgressoOcr: ((p: number) => void) | null = null;

async function reconhecer(imagem: HTMLCanvasElement | Blob, aoProgresso: (p: number) => void) {
  aoProgressoOcr = aoProgresso;
  if (!ocrPronto) {
    ocrPronto = import("tesseract.js").then(({ createWorker }) =>
      createWorker("por", 1, {
        logger: (m) => {
          if (m.status === "recognizing text") aoProgressoOcr?.(m.progress);
        },
      }),
    );
    ocrPronto.catch(() => (ocrPronto = null));
  }
  const worker = await ocrPronto;
  const { data } = await worker.recognize(imagem);
  aoProgresso(1);
  return data.text;
}

/** Pequenas correções de leitura comuns do OCR ("°" no lugar de "º", travessão). */
function corrigirOcr(p: Paragrafo): Paragrafo {
  return {
    ...p,
    texto: p.texto
      .replace(/(\bArt\.?\s*\d)\s*[°ª]/g, "$1º")
      .replace(/(§\s*\d)\s*[°ª]/g, "$1º")
      .replace(/\bN\s*[°ª]/g, "Nº")
      .replace(/\s+[—–]\s+/g, " - "),
  };
}

// ---------------------------------------------------------------- XML (LexML)

async function lerXml(arquivo: Blob, nome: string, aoProgresso: AoProgresso): Promise<Documento> {
  aoProgresso({ texto: "Lendo a estrutura do XML" });
  const texto = await arquivo.text();
  const xml = new DOMParser().parseFromString(texto, "application/xml");
  const erro = xml.querySelector("parsererror");
  if (erro) {
    return {
      nome,
      tipo: "xml",
      paginas: 1,
      paragrafos: [],
      estrutura: [
        {
          gravidade: "erro",
          titulo: "XML com erro de escrita",
          explicacao: "O arquivo não é um XML válido (alguma etiqueta não foi fechada ou está escrita errado). Corrija antes de conferir o padrão.",
          encontrado: erro.textContent?.split("\n")[0]?.slice(0, 160),
        },
      ],
    };
  }

  const todos = [...xml.getElementsByTagName("*")];
  const tem = (nomeTag: string) => todos.some((e) => e.localName.toLowerCase() === nomeTag);
  const lexml = tem("epigrafe") || tem("articulacao");
  const estrutura: Problema[] = [];
  const paragrafos: Paragrafo[] = [];

  if (lexml) {
    for (const [tag, rotulo] of [
      ["epigrafe", "Epigrafe (título)"],
      ["ementa", "Ementa"],
      ["articulacao", "Articulacao (artigos)"],
    ]) {
      if (!tem(tag))
        estrutura.push({
          gravidade: "erro",
          titulo: `Falta o elemento <${rotulo.split(" ")[0]}>`,
          explicacao: `No padrão LexML, toda lei precisa do elemento ${rotulo}.`,
          esperado: `<${rotulo.split(" ")[0]}>...</${rotulo.split(" ")[0]}>`,
        });
    }
    // Percorre na ordem do documento: título, ementa, preâmbulo e cada dispositivo (rótulo + texto)
    const DISPOSITIVOS = new Set(["artigo", "paragrafo", "inciso", "alinea", "item", "caput"]);
    const visitar = (el: Element) => {
      const tag = el.localName.toLowerCase();
      if (["epigrafe", "ementa", "preambulo", "fecho", "localdataFecho".toLowerCase(), "assinatura"].includes(tag)) {
        const t = limpar(el.textContent);
        if (t) paragrafos.push({ texto: t });
        return;
      }
      if (DISPOSITIVOS.has(tag) && tag !== "caput") {
        const rotulo = [...el.children].find((c) => c.localName.toLowerCase() === "rotulo");
        const caput = [...el.children].find((c) => c.localName.toLowerCase() === "caput");
        const corpo = [...(caput ?? el).children].filter((c) => c.localName.toLowerCase() === "p").map((c) => limpar(c.textContent));
        const linha = limpar(`${rotulo?.textContent ?? ""} ${corpo.join(" ")}`);
        if (linha) paragrafos.push({ texto: linha });
        for (const filho of [...(caput ?? el).children, ...(caput ? [...el.children] : [])]) {
          if (DISPOSITIVOS.has(filho.localName.toLowerCase()) && filho.localName.toLowerCase() !== "caput") visitar(filho);
        }
        return;
      }
      for (const filho of el.children) visitar(filho);
    };
    visitar(xml.documentElement);
  } else {
    estrutura.push({
      gravidade: "aviso",
      titulo: "XML fora do padrão LexML",
      explicacao:
        "O arquivo é um XML, mas não usa a estrutura do LexML (padrão nacional para leis em XML, com Epigrafe, Ementa e Articulacao). Conferimos só o texto.",
    });
    for (const el of todos) {
      if ([...el.children].length === 0) {
        const t = limpar(el.textContent);
        if (t) paragrafos.push({ texto: t });
      }
    }
  }
  aoProgresso({ texto: "Lendo a estrutura do XML", progresso: 1 });
  return { nome, tipo: "xml", paginas: 1, paragrafos, estrutura };
}

const limpar = (s: string | null | undefined) => (s ?? "").replace(/\s+/g, " ").trim();

// ---------------------------------------------------------------- Montagem dos parágrafos

const INICIO_DE_PARAGRAFO =
  /^(LEI\b|S[ÚU]MULA|EMENTA|A C[ÂA]MARA|Art(igo)?\.?\s*\d|§|Par[áa]grafo|[IVXLC]+\s*[-–—]\s|\d+\s*[-–—)]\s|[a-zA-Z]\)\s|Londrina,|(PREFEITO|PRESIDENTE)[^,]*$|Documento de exemplo)/;

/** Junta as linhas quebradas pelo PDF/OCR em parágrafos (cada artigo, parágrafo ou inciso vira um item). */
export function juntarLinhas(linhas: Paragrafo[]): Paragrafo[] {
  const saida: Paragrafo[] = [];
  for (const l of linhas) {
    const anterior = saida[saida.length - 1];
    const comecaNovo = !anterior || INICIO_DE_PARAGRAFO.test(l.texto) || /[.:;!?]$/.test(anterior.texto);
    if (comecaNovo) saida.push({ ...l });
    else anterior.texto = `${anterior.texto} ${l.texto}`.replace(/\s+/g, " ");
  }
  return saida;
}
