import { motion } from "motion/react";
// Réplica do "casco" do site da Câmara Municipal de Londrina (cabeçalho, menu e rodapé),
// para mostrar o assistente funcionando DENTRO do site oficial, e não como mais um site solto.
// Protótipo do hackathon: não usa imagens nem dados do site real.
import { useEffect } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import {
  ChevronDown,
  Contrast,
  Clock,
  Facebook,
  House,
  Instagram,
  Mail,
  MapPin,
  Menu,
  Music2,
  Phone,
  Search,
  Network,
  Sparkles,
  UserRound,
  Youtube,
  Accessibility,
} from "lucide-react";
import { BaseRota } from "../lib/rota";
import { useAcessibilidade } from "../lib/acessibilidade";
import { ChatFlutuante } from "./ChatPainel";

const MENU = ["A Câmara", "Vereadores", "Atividades Legislativas", "Comunicação", "Transparência"];

export function CamaraLayout() {
  const { pathname } = useLocation();
  const a11y = useAcessibilidade();
  const naConversa = pathname.startsWith("/camara/perguntar");

  useEffect(() => {
    window.scrollTo(0, 0);
    document.getElementById("conteudo")?.focus({ preventScroll: true });
  }, [pathname]);

  return (
    <BaseRota.Provider value="/camara">
      <div className="tema-camara flex min-h-screen flex-col bg-bg">
        <a
          href="#conteudo"
          className="sr-only z-50 bg-[var(--focus)] px-4 py-2 font-semibold text-black focus:not-sr-only focus:fixed focus:top-2 focus:left-2"
        >
          Ir para o conteúdo
        </a>

        <p className="bg-neutral-900 px-4 py-1 text-center text-xs text-white/80">
          Protótipo de integração · Hackathon Smart Cities Londrina 2026 · não é o site oficial da Câmara
        </p>

        {/* Cabeçalho com degradê azul-petróleo, como no site da Câmara */}
        <header className="cabecalho-camara text-white">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 pt-2 text-[0.8rem] font-bold">
            <ul className="flex gap-1.5" aria-label="Redes sociais">
              {[Facebook, Instagram, Music2, Youtube].map((Icone, i) => (
                <li key={i}>
                  <span className="grid size-7 place-items-center rounded bg-white text-[#015d7a]">
                    <Icone aria-hidden="true" className="size-4" />
                  </span>
                </li>
              ))}
            </ul>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
              <span className="hidden items-center gap-1.5 md:flex">
                <Menu aria-hidden="true" className="size-4" /> Menu Principal
              </span>
              <span className="hidden items-center gap-1.5 md:flex">
                <Search aria-hidden="true" className="size-4" /> Pesquisa
              </span>
              <span className="hidden items-center gap-1.5 lg:flex">
                <Network aria-hidden="true" className="size-4" /> Mapa do Site
              </span>
              <span className="flex items-center gap-1.5">
                <Accessibility aria-hidden="true" className="size-4" /> Acessibilidade
              </span>
              <span className="flex items-center gap-2.5">
                <button type="button" onClick={a11y.aumentar} aria-label="Aumentar letra" className="hover:underline">A+</button>
                <button type="button" onClick={a11y.diminuir} aria-label="Diminuir letra" className="hover:underline">A-</button>
                <button type="button" onClick={a11y.restaurar} aria-label="Letra normal" className="hover:underline">A</button>
                <button type="button" onClick={a11y.alternarContraste} aria-pressed={a11y.contraste} aria-label="Alto contraste">
                  <Contrast aria-hidden="true" className="size-4" />
                </button>
              </span>
              <span className="flex items-center gap-1.5 rounded-full bg-white px-3 py-1 text-[#015d7a]">
                <UserRound aria-hidden="true" className="size-4" /> Faça seu Login/Cadastro
              </span>
            </div>
          </div>

          <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-4 py-5">
            <Link to="/camara" className="flex items-end gap-3" aria-label="Câmara Municipal de Londrina, página inicial">
              <LogoPredio />
              <span className="leading-none tracking-tight uppercase">
                <span className="block text-[1.05rem] font-light sm:text-[1.35rem]">Câmara Municipal de</span>
                <span className="block text-[2.2rem] font-black sm:text-[2.9rem]">Londrina</span>
              </span>
            </Link>
            <SeloTransparencia />
            <div className="hidden text-right text-sm leading-snug font-bold md:block">
              <p className="flex items-center justify-end gap-1.5">
                <Clock aria-hidden="true" className="size-4" /> De segunda a sexta-feira
              </p>
              <p>Das 13h às 19h</p>
              <p className="mt-2 flex items-center justify-end gap-1.5">
                <Phone aria-hidden="true" className="size-4" /> (43) 3374-1300
              </p>
              <p className="font-semibold opacity-90">Ramal 1 (Ouvidoria) · Ramal 2 (e-SIC)</p>
            </div>
          </div>

          <nav aria-label="Menu principal" className="bg-[#015d7a] [.contraste_&]:bg-black">
            <ul className="sem-barra mx-auto flex max-w-7xl items-center gap-0.5 overflow-x-auto px-2 text-[0.95rem] font-bold whitespace-nowrap">
              <li>
                <NavLink to="/camara" end className="flex items-center px-3 py-3" aria-label="Início">
                  <House aria-hidden="true" className="size-5" />
                </NavLink>
              </li>
              {MENU.map((m) => (
                <li key={m}>
                  <span className="flex cursor-default items-center gap-1 px-2.5 py-3 opacity-95">
                    <ChevronDown aria-hidden="true" className="size-4" /> {m}
                  </span>
                </li>
              ))}
              <li>
                <span className="flex cursor-default items-center px-3 py-3 opacity-95">Atendimento</span>
              </li>
              {/* O que o nosso projeto adiciona ao menu da Câmara */}
              <li className="py-1.5">
                <NavLink
                  to="/camara/consulta"
                  className={({ isActive }) =>
                    `relative flex items-center gap-2 rounded-full px-4 py-1.5 text-[#0c2d3a] shadow transition hover:brightness-105 ${
                      isActive ? "bg-white" : "bg-[#ffd23f]"
                    }`
                  }
                >
                  <Sparkles aria-hidden="true" className="size-4" />
                  Consulta de Leis
                  <span className="rounded-full bg-[#0c2d3a] px-1.5 py-0.5 text-[0.65rem] font-black text-[#ffd23f] uppercase">
                    Novo
                  </span>
                </NavLink>
              </li>
              <li>
                <NavLink to="/camara/leis" className="flex items-center gap-1.5 px-3 py-3 hover:underline">
                  <Search aria-hidden="true" className="size-4" /> Pesquisa
                </NavLink>
              </li>
            </ul>
          </nav>
        </header>

        <main id="conteudo" tabIndex={-1} className="flex-1 focus:outline-none">
          {/* Troca de página: só opacidade (deslocar com transform quebraria as barras fixas da conversa) */}
          <motion.div key={pathname} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.25, ease: "easeOut" }}>
            <Outlet />
          </motion.div>
        </main>

        {!naConversa && (
          <footer id="rodape" tabIndex={-1} className="bg-[#00445a] text-white [.contraste_&]:bg-black">
            <div className="mx-auto grid max-w-7xl gap-8 px-4 py-10 text-sm sm:grid-cols-2 lg:grid-cols-3">
              <div className="grid gap-2">
                <p className="text-base font-bold">Câmara Municipal de Londrina/PR</p>
                <p className="flex gap-2">
                  <MapPin aria-hidden="true" className="mt-0.5 size-4 shrink-0" /> Rua Gov. Parigot de Souza, 145 · Centro Cívico,
                  Londrina/PR
                </p>
                <p className="flex gap-2">
                  <Phone aria-hidden="true" className="mt-0.5 size-4 shrink-0" /> (43) 3374-1300
                </p>
                <p className="flex gap-2">
                  <Mail aria-hidden="true" className="mt-0.5 size-4 shrink-0" /> protocolo@cml.pr.gov.br
                </p>
              </div>
              <div className="grid content-start gap-1">
                <p className="font-bold">Horário de Atendimento</p>
                <p>De segunda a sexta-feira, das 13h às 19h</p>
                <p className="mt-3 font-bold">Horário das Sessões</p>
                <p>Terças e quintas-feiras, a partir das 14h</p>
              </div>
              <div className="grid content-start gap-2 rounded-2xl bg-white/10 p-4">
                <p className="flex items-center gap-2 font-bold">
                  <Sparkles aria-hidden="true" className="size-4 text-[#ffd23f]" /> Consulta de Leis
                </p>
                <p className="opacity-90">
                  Assistente que responde com base apenas nas leis em vigor, com a fonte de cada resposta. Feito a partir dos Dados
                  Abertos da Câmara.
                </p>
                <Link to="/camara/validador" className="mt-1 inline-flex items-center gap-1.5 font-semibold text-[#ffd23f] hover:underline">
                  Validador de Leis: confira o padrão de uma lei →
                </Link>
              </div>
            </div>
            <p className="border-t border-white/15 px-4 py-4 text-center text-xs opacity-80">
              Dados Abertos | Política de Privacidade | Protótipo do Hackathon Smart Cities Londrina 2026
            </p>
          </footer>
        )}

        {!naConversa && !pathname.startsWith("/camara/validador") && <ChatFlutuante />}
      </div>
    </BaseRota.Provider>
  );
}

/** Desenho simples de um prédio com colunas, no lugar do logotipo oficial. */
function LogoPredio() {
  return (
    <svg viewBox="0 0 64 52" aria-hidden="true" className="h-14 w-auto shrink-0 sm:h-16">
      <rect x="2" y="4" width="60" height="5" rx="1" fill="currentColor" />
      <rect x="6" y="11" width="52" height="3" fill="currentColor" opacity=".8" />
      {[10, 20, 30, 40, 50].map((x) => (
        <rect key={x} x={x} y="16" width="4" height="28" fill="currentColor" opacity=".9" />
      ))}
      <rect x="2" y="45" width="60" height="5" rx="1" fill="currentColor" />
    </svg>
  );
}

function SeloTransparencia() {
  return (
    <div
      aria-label="Selo Diamante de Transparência Pública"
      className="hidden size-24 shrink-0 place-items-center rounded-full bg-gradient-to-br from-white via-slate-200 to-slate-400 p-1 text-center shadow-lg ring-4 ring-white/40 lg:grid"
    >
      <span className="grid size-full place-items-center rounded-full border-2 border-[#015d7a]/30 text-[#015d7a]">
        <span className="leading-tight">
          <span className="block text-[0.5rem] font-bold uppercase">Transparência</span>
          <span className="block text-sm font-black uppercase">Diamante</span>
          <span className="block text-[0.6rem] font-bold">2025</span>
        </span>
      </span>
    </div>
  );
}
