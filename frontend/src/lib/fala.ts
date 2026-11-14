// Voz no navegador (gratuito, sem servidor):
// - ouvir: lê um texto em voz alta (speechSynthesis)
// - ditar: transforma a fala em texto (SpeechRecognition; Chrome e Edge)
import { useCallback, useEffect, useRef, useState } from "react";

export function useOuvir() {
  const [falando, setFalando] = useState(false);
  const suportado = typeof window !== "undefined" && "speechSynthesis" in window;

  const parar = useCallback(() => {
    if (!suportado) return;
    window.speechSynthesis.cancel();
    setFalando(false);
  }, [suportado]);

  const ouvir = useCallback(
    (texto: string) => {
      if (!suportado) return;
      window.speechSynthesis.cancel();
      const fala = new SpeechSynthesisUtterance(texto);
      fala.lang = "pt-BR";
      fala.rate = 1;
      const voz = window.speechSynthesis.getVoices().find((v) => v.lang.toLowerCase().startsWith("pt"));
      if (voz) fala.voice = voz;
      fala.onend = () => setFalando(false);
      fala.onerror = () => setFalando(false);
      setFalando(true);
      window.speechSynthesis.speak(fala);
    },
    [suportado],
  );

  useEffect(() => parar, [parar]);
  return { suportado, falando, ouvir, parar };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Reconhecimento = any;

export function useDitar(aoTerminar: (texto: string) => void) {
  const Ctor =
    typeof window !== "undefined"
      ? // eslint-disable-next-line @typescript-eslint/no-explicit-any
        ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition)
      : undefined;
  const [ouvindo, setOuvindo] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const rec = useRef<Reconhecimento>(null);
  const callback = useRef(aoTerminar);
  callback.current = aoTerminar;

  const iniciar = useCallback(() => {
    if (!Ctor) return;
    setErro(null);
    const r = new Ctor();
    r.lang = "pt-BR";
    r.interimResults = false;
    r.maxAlternatives = 1;
    r.onresult = (e: Reconhecimento) => callback.current(e.results[0][0].transcript);
    r.onerror = (e: Reconhecimento) =>
      setErro(e.error === "not-allowed" ? "Permita o uso do microfone para falar sua pergunta." : "Não consegui ouvir. Tente de novo.");
    r.onend = () => setOuvindo(false);
    rec.current = r;
    setOuvindo(true);
    r.start();
  }, [Ctor]);

  const parar = useCallback(() => rec.current?.stop(), []);
  useEffect(() => () => rec.current?.abort?.(), []);

  return { suportado: Boolean(Ctor), ouvindo, erro, iniciar, parar };
}
