// Preferências de acessibilidade (alto contraste e tamanho da letra), guardadas no navegador.
import { useEffect, useState } from "react";

function ler(chave: string) {
  try {
    return localStorage.getItem(chave);
  } catch {
    return null;
  }
}
function gravar(chave: string, valor: string) {
  try {
    localStorage.setItem(chave, valor);
  } catch {
    /* navegador sem armazenamento: tudo bem, só não lembra da preferência */
  }
}

export function useAcessibilidade() {
  const [contraste, setContraste] = useState(() => ler("a11y-contraste") === "1");
  const [fonte, setFonte] = useState(() => Math.min(3, Math.max(0, Number(ler("a11y-fonte") ?? 0) || 0)));

  useEffect(() => {
    document.documentElement.classList.toggle("contraste", contraste);
    gravar("a11y-contraste", contraste ? "1" : "0");
  }, [contraste]);

  useEffect(() => {
    if (fonte) document.documentElement.dataset.fonte = String(fonte);
    else delete document.documentElement.dataset.fonte;
    gravar("a11y-fonte", String(fonte));
  }, [fonte]);

  return {
    contraste,
    alternarContraste: () => setContraste((c) => !c),
    fonte,
    aumentar: () => setFonte((f) => Math.min(3, f + 1)),
    diminuir: () => setFonte((f) => Math.max(0, f - 1)),
    restaurar: () => setFonte(0),
  };
}
