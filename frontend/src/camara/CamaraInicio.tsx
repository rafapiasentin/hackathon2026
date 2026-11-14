// Página inicial da réplica do site da Câmara, com o nosso banner e o atalho "Consulta de Leis".
// Notícias e nomes são textos públicos do site, só para dar contexto na apresentação.
import { motion } from "motion/react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  BookOpen,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  CircleCheck,
  FileBadge,
  FileCheck,
  Gavel,
  Landmark,
  Megaphone,
  MessageCircleQuestion,
  Navigation,
  Newspaper,
  Radio,
  ScrollText,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Contador } from "../components/Animacoes";

export const abrirChat = () => window.dispatchEvent(new Event("abrir-chat-leis"));

const NOTICIAS_LADO = [
  "Câmara realiza reunião pública sobre retomada das obras do Centro de Reabilitação",
  "Câmara de Londrina aprova três projetos para adequar legislação municipal ao ProLegis",
  "Frente Parlamentar das Estradas Rurais articula recursos para a Estrada do Limoeiro",
  "Câmara de Londrina recebe capacitação do TCE-PR sobre avaliação de contas públicas",
];

const ULTIMAS = [
  {
    data: "05/11/2026",
    titulo: "Vereadores aprovam projeto que diferencia fiscalização sanitária para açougues e supermercados",
    resumo: "Proposta altera regras do Serviço de Inspeção Municipal para estabelecimentos varejistas.",
  },
  {
    data: "04/11/2026",
    titulo: "Câmara de Londrina entregará em novembro títulos de Cidadão Honorário e Cidadão Benemérito",
    resumo: "Homenagens serão na Sala de Sessões, com transmissão ao vivo.",
  },
  {
    data: "03/11/2026",
    titulo: "Em 2º turno, Câmara aprova projeto que reestrutura vagas para professores da rede municipal",
    resumo: "Projeto extingue 258 vagas de 20 horas e cria 171 vagas de 30 horas semanais.",
  },
  {
    data: "29/10/2026",
    titulo: "Câmara aprova em 1º turno projetos que redesenham cargos na Educação e na Saúde",
    resumo: "Propostas tratam de vagas de professor e de gratificações em UBS.",
  },
];

const ATALHOS: { rotulo: string; icone: LucideIcon }[] = [
  { rotulo: "Certidão de Utilidade Pública", icone: FileBadge },
  { rotulo: "Pautas", icone: BookOpen },
  { rotulo: "Acompanhe ao Vivo", icone: Radio },
  { rotulo: "LGPD", icone: ShieldCheck },
  { rotulo: "GPS Legislativo", icone: Navigation },
  { rotulo: "Ouvidoria", icone: Megaphone },
  { rotulo: "SIC", icone: Landmark },
  { rotulo: "Diário Oficial", icone: Newspaper },
  { rotulo: "Licitações", icone: Gavel },
  { rotulo: "Legislativo em Pauta", icone: ScrollText },
];

const VEREADORES = [
  "Anne Ada", "Antônio Amaral", "Chavão", "Deivid Wisley", "Emanoel", "Giovani Mattos",
  "Jessicão", "Lenir de Assis", "Marcelo Oguido", "Marinho", "Matheus Thum", "Mestre Madureira",
  "Professora Flávia Cabral", "Régis Choucino", "Roberto Fu", "Santão", "Sídnei Matias", "Valdir Santa Fé",
];

const EVENTOS = [
  { dia: "16", hora: "14:00", titulo: "38ª Reunião Ordinária de Comissão" },
  { dia: "16", hora: "16:20", titulo: "48ª Reunião Ordinária de Comissão" },
  { dia: "18", hora: "14:00", titulo: "Sessão Ordinária" },
];

function iniciais(nome: string) {
  const p = nome.split(" ").filter((x) => x.length > 2 || nome.split(" ").length === 1);
  return (p[0][0] + (p.length > 1 ? p[p.length - 1][0] : "")).toUpperCase();
}

export function CamaraInicio() {
  return (
    <div className="mx-auto max-w-7xl px-3 py-4 sm:px-4">
      <h1 className="sr-only">Câmara Municipal de Londrina: página inicial</h1>

      <div className="grid gap-3 lg:grid-cols-[1.35fr_0.9fr_1.05fr]">
        {/* Destaque */}
        <article className="relative overflow-hidden bg-surface">
          <div className="p-4">
            <p className="text-xs font-bold text-muted uppercase">Notícias</p>
            <h2 className="mt-1 text-2xl leading-snug font-bold text-[#4a4a4a] [.contraste_&]:text-text">
              Câmara de Londrina conquista pela segunda vez consecutiva o Selo Diamante de Transparência
            </h2>
          </div>
          <div className="relative grid h-64 place-items-center bg-gradient-to-br from-[#062a4a] via-[#0b4f7c] to-[#0a7a8c] text-white sm:h-80">
            <div className="text-center">
              <p className="text-sm font-semibold tracking-widest uppercase opacity-80">Transparência que evolui</p>
              <p className="mt-2 text-7xl font-black">98,2%</p>
              <p className="mt-1 font-bold text-[#ffd23f]">Selo Diamante 2026</p>
            </div>
            <span className="absolute inset-y-0 left-2 grid place-items-center">
              <ChevronLeft aria-hidden="true" className="size-8 opacity-70" />
            </span>
            <span className="absolute inset-y-0 right-2 grid place-items-center">
              <ChevronRight aria-hidden="true" className="size-8 opacity-70" />
            </span>
          </div>
        </article>

        {/* Notícias menores */}
        <ul className="grid content-start gap-3">
          {NOTICIAS_LADO.map((t, i) => (
            <li key={t} className="flex gap-3 bg-surface p-2">
              <span
                aria-hidden="true"
                className="grid h-20 w-28 shrink-0 place-items-center bg-gradient-to-br from-slate-500 to-slate-700 text-white/70"
                style={{ filter: `hue-rotate(${i * 25}deg)` }}
              >
                <Users className="size-7" />
              </span>
              <div className="min-w-0">
                <p className="text-xs font-bold text-muted uppercase">Notícias</p>
                <p className="line-clamp-3 text-[0.95rem] leading-snug font-semibold text-[#4a4a4a] [.contraste_&]:text-text">{t}</p>
              </div>
            </li>
          ))}
        </ul>

        {/* Coluna da direita: o NOSSO banner no lugar de destaque + atalhos */}
        <div className="grid content-start gap-3">
          <BannerConsulta />
          <ul className="grid grid-cols-2 gap-2">
            <li className="col-span-2">
              <Link
                to="/camara/consulta"
                className="flex items-center gap-3 rounded-sm bg-[#ffd23f] px-3 py-3 font-bold text-[#0c2d3a] shadow transition hover:brightness-105"
              >
                <Sparkles aria-hidden="true" className="size-5" />
                Consulta de Leis
                <span className="ml-auto rounded-full bg-[#0c2d3a] px-2 py-0.5 text-[0.65rem] font-black text-[#ffd23f] uppercase">
                  Novo
                </span>
              </Link>
            </li>
            <li className="col-span-2">
              <Link
                to="/camara/validador"
                className="flex items-center gap-3 rounded-sm border-2 border-[#ffd23f] bg-[#00445a] px-3 py-2.5 font-bold text-white shadow transition hover:bg-[#015d7a] [.contraste_&]:bg-black"
              >
                <FileCheck aria-hidden="true" className="size-5 text-[#ffd23f]" />
                <span className="leading-tight">
                  Validador de Leis
                  <span className="block text-xs font-medium opacity-85">Confira o padrão antes de publicar</span>
                </span>
                <span className="ml-auto rounded-full bg-[#ffd23f] px-2 py-0.5 text-[0.65rem] font-black text-[#0c2d3a] uppercase">Novo</span>
              </Link>
            </li>
            {ATALHOS.map(({ rotulo, icone: Icone }) => (
              <li key={rotulo}>
                <span className="flex h-full items-center gap-2.5 rounded-sm bg-[#015d7a] px-3 py-2.5 text-[0.9rem] leading-tight font-semibold text-white [.contraste_&]:border [.contraste_&]:border-white [.contraste_&]:bg-black">
                  <Icone aria-hidden="true" className="size-5 shrink-0 opacity-90" />
                  {rotulo}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Últimas notícias + calendário */}
      <div className="mt-6 grid gap-6 lg:grid-cols-[2fr_1fr]">
        <section className="bg-surface p-4">
          <h2 className="mb-3 flex items-center gap-2 text-lg font-bold text-[#015d7a] [.contraste_&]:text-text">
            <Newspaper aria-hidden="true" className="size-5" /> Últimas notícias
          </h2>
          <ul className="divide-y divide-border">
            {ULTIMAS.map((n, i) => (
              <li key={n.titulo} className="flex gap-4 py-3">
                <span
                  aria-hidden="true"
                  className="hidden h-20 w-32 shrink-0 bg-gradient-to-br from-[#2b6a7d] to-[#14394a] sm:block"
                  style={{ filter: `hue-rotate(${i * 30}deg)` }}
                />
                <div>
                  <p className="text-xs text-muted">
                    <span className="font-bold uppercase">Notícias</span> · {n.data}
                  </p>
                  <p className="font-bold text-[#4a4a4a] [.contraste_&]:text-text">{n.titulo}</p>
                  <p className="text-sm text-muted">{n.resumo}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="bg-surface p-4">
          <h2 className="mb-3 flex items-center gap-2 text-lg font-bold text-[#015d7a] [.contraste_&]:text-text">
            <CalendarDays aria-hidden="true" className="size-5" /> Calendário de Eventos
          </h2>
          <ul className="grid gap-3">
            {EVENTOS.map((e) => (
              <li key={e.hora + e.titulo} className="flex gap-3 border-b border-border pb-3 last:border-0">
                <span className="grid w-14 shrink-0 place-items-center rounded bg-[#e1f1f5] py-1 text-[#015d7a] [.contraste_&]:bg-black [.contraste_&]:text-text">
                  <span className="text-2xl leading-none font-black">{e.dia}</span>
                  <span className="text-[0.6rem] font-bold uppercase">Novembro</span>
                </span>
                <div className="text-sm">
                  <p className="text-muted">{e.hora}</p>
                  <p className="font-semibold">{e.titulo}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>

      {/* Vereadores */}
      <section className="mt-6 bg-surface p-4">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-[#015d7a] [.contraste_&]:text-text">
          <Users aria-hidden="true" className="size-5" /> Vereadores em Exercício
        </h2>
        <ul className="grid grid-cols-3 gap-4 sm:grid-cols-6 lg:grid-cols-9">
          {VEREADORES.map((v) => (
            <li key={v} className="text-center">
              <span
                aria-hidden="true"
                className="mx-auto grid aspect-[4/5] w-full max-w-24 place-items-center rounded bg-gradient-to-b from-slate-200 to-slate-300 text-xl font-black text-slate-500 [.contraste_&]:from-black [.contraste_&]:to-black [.contraste_&]:text-text"
              >
                {iniciais(v)}
              </span>
              <p className="mt-1.5 text-sm leading-tight font-semibold">{v}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function BannerConsulta() {
  return (
    <motion.section
      aria-labelledby="banner-consulta"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="relative overflow-hidden bg-gradient-to-br from-[#00445a] via-[#015d7a] to-[#0a8aa0] p-5 text-white [.contraste_&]:border [.contraste_&]:border-white [.contraste_&]:from-black [.contraste_&]:via-black [.contraste_&]:to-black"
    >
      <span aria-hidden="true" className="absolute -top-10 -right-10 size-40 rounded-full bg-white/10" />
      <span aria-hidden="true" className="absolute -right-4 -bottom-16 size-32 rounded-full bg-[#ffd23f]/20" />

      <p className="relative inline-flex items-center gap-1.5 rounded-full bg-[#ffd23f] px-2.5 py-0.5 text-xs font-black text-[#0c2d3a] uppercase">
        <Sparkles aria-hidden="true" className="size-3.5" /> Novo
      </p>
      <h2 id="banner-consulta" className="relative mt-3 text-3xl leading-tight font-black">
        Consulta de Leis
      </h2>
      <p className="relative mt-2 text-[0.95rem] leading-snug opacity-95">
        Tem dúvida sobre uma lei de Londrina? Pergunte com suas palavras.
      </p>
      <ul className="relative mt-3 grid gap-1 text-sm">
        {["Só leis em vigor", "Sempre com a fonte oficial", "Fale, ouça ou use Libras"].map((t) => (
          <li key={t} className="flex items-center gap-2">
            <CircleCheck aria-hidden="true" className="size-4 text-[#ffd23f]" /> {t}
          </li>
        ))}
      </ul>
      {/* Números reais da coleta (leis.json): 14.308 leis, 1.298 revogadas */}
      <dl className="relative mt-4 grid grid-cols-2 gap-2 rounded-xl bg-white/10 p-3">
        <div>
          <dt className="sr-only">Leis analisadas</dt>
          <dd className="text-2xl leading-none font-black">
            <Contador valor={14308} />
          </dd>
          <dd className="mt-1 text-xs opacity-90">leis analisadas</dd>
        </div>
        <div>
          <dt className="sr-only">Leis revogadas filtradas</dt>
          <dd className="text-2xl leading-none font-black text-[#ffd23f]">
            <Contador valor={1298} />
          </dd>
          <dd className="mt-1 text-xs opacity-90">revogadas filtradas</dd>
        </div>
      </dl>
      <div className="relative mt-4 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={abrirChat}
          className="inline-flex items-center gap-2 rounded-full bg-[#ffd23f] px-4 py-2 font-bold text-[#0c2d3a] shadow transition hover:brightness-105"
        >
          <MessageCircleQuestion aria-hidden="true" className="size-5" /> Perguntar agora
        </button>
        <Link
          to="/camara/leis"
          className="inline-flex items-center gap-1.5 rounded-full px-3 py-2 font-semibold text-white underline-offset-4 hover:underline"
        >
          Buscar uma lei <ArrowRight aria-hidden="true" className="size-4" />
        </Link>
      </div>
    </motion.section>
  );
}
