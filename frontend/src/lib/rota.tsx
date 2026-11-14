// As mesmas telas rodam em dois lugares: no site próprio ("/") e dentro do site da Câmara ("/camara").
// Este contexto guarda o prefixo, para os links não saírem do site em que a pessoa está.
import { createContext, useContext } from "react";

export const BaseRota = createContext("");

export function useRota() {
  const base = useContext(BaseRota);
  return (caminho: string) => (base + caminho).replace(/\/$/, "") || "/";
}
