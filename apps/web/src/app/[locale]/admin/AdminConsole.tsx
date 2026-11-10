"use client";

import Link from "next/link";
import { Fragment, useCallback, useEffect, useRef, useState } from "react";
import type { FormEvent, KeyboardEvent, ReactNode } from "react";

import { Button, SelectField, TextArea, TextField } from "@/components/ui";
import type { OfferConfig } from "@/lib/api";
import { t, type Locale } from "@/lib/i18n";

type Tab =
  | "overview"
  | "channels"
  | "offers"
  | "sources"
  | "topics"
  | "articles"
  | "pins"
  | "refresh"
  | "keys"
  | "audit"
  | "leads"
  | "contacts"
  | "partners"
  | "funnel";

const TABS: readonly Tab[] = [
  "overview",
  "channels",
  "offers",
  "sources",
  "topics",
  "articles",
  "pins",
  "refresh",
  "keys",
  "audit",
  "leads",
  "contacts",
  "partners",
  "funnel",
];

interface FunnelChannel {
  industry: string;
  /** Set for cross-desk events (the apex lobby); empty for channel events. */
  surface?: string;
  events: Record<string, number>;
  placements: Record<string, number>;
  leads_by_kind: Record<string, number>;
  rates: {
    click_rate: number | null;
    start_rate: number | null;
    submit_rate: number | null;
    lead_rate: number | null;
  };
}

interface FunnelData {
  window_days: number;
  industry: string;
  stages: string[];
  totals: { events: number; leads: number };
  channels: FunnelChannel[];
}

interface AdminIndustry {
  slug: string;
  name: string;
  enabled: boolean;
  fetch_interval_minutes: number | null;
  effective_fetch_interval_minutes: number;
  auto_fetch_enabled: boolean;
  offers: OfferConfig;
  asset?: string | null;
}

interface OfferItem {
  headline: string;
  change: string;
  date: string;
  jurisdiction: string;
  action: string;
  source_name: string;
  source_url: string;
}

interface OfferIssue {
  id: string;
  industry: string;
  offer_slug: string;
  issue_date: string;
  scope: string;
  status: string;
  title: string;
  standfirst: string;
  items: OfferItem[];
  sources: { name: string; url: string }[];
  source_version: string | null;
  reviewer: string | null;
  error: string | null;
  generated_at: string;
  published_at: string | null;
}

interface ChannelDraft {
  slug: string;
  autoFetch: boolean;
  useDefault: boolean;
  hours: string;
  consultation: boolean;
  question: boolean;
  secondary: "none" | "brief" | "asset";
}
interface Source {
  id: string;
  name: string;
  feed_url: string;
  language: string;
  trust: number;
  enabled: boolean;
  status: string;
  last_success_at: string | null;
  consecutive_failures: number;
  fail_streak?: number;
  last_error: string | null;
  cooldown_until?: string | null;
  cooldown_reason?: string;
}
interface Topic {
  id: string;
  slug: string;
  label: Record<string, string>;
  weight: number;
}
interface AdminArticle {
  id: string;
  title: string;
  url: string;
  publisher: string;
  language: string;
  published_at: string;
  industry: string;
  status: string;
}
interface Pin {
  id: string;
  article_id: string;
  position: number;
  title: string | null;
  status: string | null;
}
interface Run {
  run_id: string;
  industry: string | null;
  trigger: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  stats: Record<string, unknown>;
}
interface ApiKey {
  id: string;
  label: string;
  prefix: string;
  rate_limit: number;
  enabled: boolean;
  last_used_at: string | null;
}
interface AuditEvent {
  id: string;
  actor: string;
  action: string;
  entity: string;
  entity_id: string | null;
  created_at: string;
}
interface Lead {
  id: string;
  industry: string;
  name: string;
  email: string;
  phone: string | null;
  status: string;
  created_at: string;
}
interface Contact {
  id: string;
  industry: string | null;
  name: string;
  email: string;
  phone: string | null;
  message: string;
  locale: string;
  status: string;
  source_page: string | null;
  utm: Record<string, string>;
  country: string | null;
  session_hash: string | null;
  created_at: string;
}

interface Partner {
  id: string;
  industry: string;
  name: string;
  contact_email: string;
  status: string;
}

interface ApiResult<T> {
  ok: boolean;
  status: number;
  data: T | null;
  detail: string | null;
}

type Status = { kind: "ok" | "error"; text: string };

const LEAD_STATUSES = ["new", "routed", "contacted", "qualified", "closed", "spam"] as const;
const CONTACT_STATUSES = ["new", "read", "closed"] as const;

const RUN_STATUS_KEY: Record<string, string> = {
  queued: "admin.queued",
  running: "admin.running",
  ok: "admin.ok",
  partial: "admin.partial",
  failed: "admin.failed",
};

const OFFER_STATUS_KEY: Record<string, string> = {
  queued: "admin.queued",
  building: "admin.running",
  draft: "admin.offerDraft",
  empty: "admin.offerEmpty",
  failed: "admin.failed",
  published: "admin.published",
};

/** Quiet row action — keeps destructive controls below the panel's primary submit. */
const QUIET_BUTTON =
  "rounded border border-[var(--sn-border)] px-3 py-1.5 text-sm text-[var(--sn-text)] transition-colors hover:border-[var(--sn-primary)] disabled:opacity-60";

const DESTRUCTIVE_BUTTON =
  "rounded border border-[var(--sn-border)] px-3 py-1.5 text-sm text-[var(--sn-accent)] transition-colors hover:border-[var(--sn-accent)] disabled:opacity-60";

function readCookie(name: string): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match?.[1] ? decodeURIComponent(match[1]) : "";
}

function readDetail(payload: unknown): string | null {
  if (!payload || typeof payload !== "object" || !("detail" in payload)) return null;
  const detail = (payload as { detail?: unknown }).detail;
  return typeof detail === "string" && detail.length > 0 ? detail : null;
}

async function apiRequest<T>(
  path: string,
  options: { method?: string; body?: unknown; csrf?: string } = {},
): Promise<ApiResult<T>> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (options.csrf) headers["x-csrf-token"] = options.csrf;
  try {
    const response = await fetch(path, {
      method: options.method ?? "GET",
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      credentials: "same-origin",
      cache: "no-store",
    });
    const payload: unknown =
      response.status === 204 ? null : await response.json().catch(() => null);
    return {
      ok: response.ok,
      status: response.status,
      data: payload as T | null,
      detail: response.ok ? null : readDetail(payload),
    };
  } catch {
    return { ok: false, status: 0, data: null, detail: null };
  }
}

function focusElement(id: string) {
  requestAnimationFrame(() => document.getElementById(id)?.focus());
}

function failureText(result: { status: number; detail: string | null }, locale: Locale): string {
  if (result.detail) return result.detail;
  return `${t(locale, "common.error")} (${result.status})`;
}

function runStatusLabel(status: string, locale: Locale): string {
  const key = RUN_STATUS_KEY[status];
  return key ? t(locale, key) : status;
}

function offerStatusLabel(status: string, locale: Locale): string {
  const key = OFFER_STATUS_KEY[status];
  return key ? t(locale, key) : status;
}

/** Visually hidden table caption — the table stays readable, the panel keeps its name. */
function Caption({ children }: { children: ReactNode }) {
  return <caption className="sr-only">{children}</caption>;
}

function Th({ children, numeric = false }: { children?: ReactNode; numeric?: boolean }) {
  return (
    <th scope="col" className={["p-2 font-semibold", numeric ? "text-right" : "text-left"].join(" ")}>
      {children}
    </th>
  );
}

function EmptyRow({ columns, locale }: { columns: number; locale: Locale }) {
  return (
    <tr>
      <td colSpan={columns} className="p-2 text-sm text-[var(--sn-muted)]">
        {t(locale, "admin.empty")}
      </td>
    </tr>
  );
}

export function AdminConsole({
  locale,
  defaultIndustry,
}: {
  locale: Locale;
  defaultIndustry: string;
}) {
  const [phase, setPhase] = useState<"checking" | "signedOut" | "signedIn">("checking");
  const [operator, setOperator] = useState<string | null>(null);
  const [csrf, setCsrf] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
  const [panelLoading, setPanelLoading] = useState(false);

  const [tab, setTab] = useState<Tab>("overview");
  const [focusTab, setFocusTab] = useState<Tab>("overview");
  const [industry, setIndustry] = useState(defaultIndustry);

  const [industries, setIndustries] = useState<AdminIndustry[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [articles, setArticles] = useState<AdminArticle[]>([]);
  const [pins, setPins] = useState<Pin[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [openContact, setOpenContact] = useState<string | null>(null);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [funnel, setFunnel] = useState<FunnelData | null>(null);
  const [offers, setOffers] = useState<OfferIssue[]>([]);
  const [openOffer, setOpenOffer] = useState<string | null>(null);
  const [publishTarget, setPublishTarget] = useState<string | null>(null);
  const [publishReviewer, setPublishReviewer] = useState("");

  const [auditAction, setAuditAction] = useState("");
  const [newKey, setNewKey] = useState("");
  const [defaultFetchInterval, setDefaultFetchInterval] = useState(720);
  const [channelDraft, setChannelDraft] = useState<ChannelDraft | null>(null);

  const [articleForm, setArticleForm] = useState<{ id: string; kind: "hide" | "pin" } | null>(null);
  const [hideReason, setHideReason] = useState("");
  const [pinPosition, setPinPosition] = useState("1");
  const [pinWeight, setPinWeight] = useState("1");
  const [confirming, setConfirming] = useState<string | null>(null);

  const [refreshIndustry, setRefreshIndustry] = useState("all");
  const [fullReset, setFullReset] = useState(false);
  const [confirmation, setConfirmation] = useState("");

  const csrfToken = csrf || readCookie("sn_csrf");
  const tabRefs = useRef(new Map<Tab, HTMLButtonElement | null>());
  const panelRef = useRef<HTMLDivElement | null>(null);

  const endSession = useCallback((notice: string) => {
    setOperator(null);
    setCsrf("");
    setPhase("signedOut");
    setPassword("");
    setLoginError(notice);
    setStatus(null);
    setBusy(null);
    setPanelLoading(false);
    setArticleForm(null);
    setHideReason("");
    setConfirming(null);
    setNewKey("");
    setFullReset(false);
    setConfirmation("");
    setIndustries([]);
    setSources([]);
    setTopics([]);
    setArticles([]);
    setPins([]);
    setRuns([]);
    setKeys([]);
    setAudit([]);
    setLeads([]);
    setContacts([]);
    setOpenContact(null);
    setPartners([]);
    setFunnel(null);
    setOffers([]);
    setOpenOffer(null);
    setPublishTarget(null);
    setPublishReviewer("");
    if (typeof document !== "undefined") {
      // `sn_admin` is httpOnly; only the readable CSRF cookie can be cleared here.
      document.cookie = "sn_csrf=; Max-Age=0; path=/";
    }
  }, []);

  const expire = useCallback(() => {
    endSession(t(locale, "admin.sessionExpired"));
  }, [endSession, locale]);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const me = await apiRequest<{ operator: { email: string } }>("/api/proxy/v1/admin/auth/me");
      if (cancelled) return;
      if (me.ok && me.data?.operator) {
        setOperator(me.data.operator.email);
        setCsrf(readCookie("sn_csrf"));
        setPhase("signedIn");
      } else {
        setPhase("signedOut");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!operator) return;
    let cancelled = false;
    void apiRequest<{ data: AdminIndustry[]; defaults?: { fetch_interval_minutes: number } }>(
      "/api/proxy/v1/admin/industries",
    ).then((result) => {
      if (cancelled) return;
      if (result.status === 401) {
        expire();
        return;
      }
      if (result.ok) {
        setIndustries(result.data?.data ?? []);
        if (result.data?.defaults) setDefaultFetchInterval(result.data.defaults.fetch_interval_minutes);
      } else setStatus({ kind: "error", text: failureText(result, locale) });
    });
    return () => {
      cancelled = true;
    };
  }, [operator, expire, locale]);

  const load = useCallback(
    async (activeTab: Tab, activeIndustry: string) => {
      let expired = false;
      const read = async <T,>(path: string): Promise<T | null> => {
        if (expired) return null;
        const result = await apiRequest<T>(path);
        if (result.ok) return result.data;
        if (result.status === 401) {
          expired = true;
          expire();
          return null;
        }
        setStatus({ kind: "error", text: failureText(result, locale) });
        return null;
      };

      if (activeTab === "overview") {
        const sourcesData = await read<{ data: Source[] }>("/api/proxy/v1/admin/sources");
        if (sourcesData) setSources(sourcesData.data ?? []);
        const runsData = await read<{ data: Run[] }>("/api/proxy/v1/admin/refresh");
        if (runsData) setRuns(runsData.data ?? []);
      } else if (activeTab === "channels") {
        const data = await read<{
          data: AdminIndustry[];
          defaults?: { fetch_interval_minutes: number };
        }>("/api/proxy/v1/admin/industries");
        if (data) {
          setIndustries(data.data ?? []);
          if (data.defaults) setDefaultFetchInterval(data.defaults.fetch_interval_minutes);
        }
      } else if (activeTab === "offers") {
        const data = await read<{ data: OfferIssue[] }>("/api/proxy/v1/admin/offers?limit=50");
        if (data) setOffers(data.data ?? []);
      } else if (activeTab === "sources") {
        const data = await read<{ data: Source[] }>(
          `/api/proxy/v1/admin/sources?industry=${encodeURIComponent(activeIndustry)}`,
        );
        if (data) setSources(data.data ?? []);
      } else if (activeTab === "topics") {
        const data = await read<{ data: Topic[] }>(
          `/api/proxy/v1/admin/topics?industry=${encodeURIComponent(activeIndustry)}`,
        );
        if (data) setTopics(data.data ?? []);
      } else if (activeTab === "articles") {
        const data = await read<{ data: AdminArticle[] }>(
          `/api/proxy/v1/admin/articles?industry=${encodeURIComponent(activeIndustry)}`,
        );
        if (data) setArticles(data.data ?? []);
        const pinData = await read<{ data: Pin[] }>(
          `/api/proxy/v1/admin/pins?industry=${encodeURIComponent(activeIndustry)}`,
        );
        if (pinData) setPins(pinData.data ?? []);
      } else if (activeTab === "pins") {
        const data = await read<{ data: Pin[] }>(
          `/api/proxy/v1/admin/pins?industry=${encodeURIComponent(activeIndustry)}`,
        );
        if (data) setPins(data.data ?? []);
      } else if (activeTab === "refresh") {
        const data = await read<{ data: Run[] }>("/api/proxy/v1/admin/refresh");
        if (data) setRuns(data.data ?? []);
      } else if (activeTab === "keys") {
        const data = await read<{ data: ApiKey[] }>("/api/proxy/v1/admin/api-keys");
        if (data) setKeys(data.data ?? []);
      } else if (activeTab === "audit") {
        const query = auditAction ? `?action=${encodeURIComponent(auditAction)}` : "";
        const data = await read<{ data: AuditEvent[] }>(`/api/proxy/v1/admin/audit${query}`);
        if (data) setAudit(data.data ?? []);
      } else if (activeTab === "leads") {
        const data = await read<{ data: Lead[] }>("/api/proxy/v1/admin/leads");
        if (data) setLeads(data.data ?? []);
      } else if (activeTab === "contacts") {
        const data = await read<{ data: Contact[] }>("/api/proxy/v1/admin/contacts?limit=100");
        if (data) setContacts(data.data ?? []);
      } else if (activeTab === "partners") {
        const data = await read<{ data: Partner[] }>("/api/proxy/v1/admin/partners");
        if (data) setPartners(data.data ?? []);
      } else if (activeTab === "funnel") {
        const data = await read<FunnelData>("/api/proxy/v1/admin/funnel?days=30");
        if (data) setFunnel(data);
      }
    },
    [auditAction, expire, locale],
  );

  useEffect(() => {
    if (!operator) return;
    let cancelled = false;
    setPanelLoading(true);
    void load(tab, industry).finally(() => {
      if (!cancelled) setPanelLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [operator, tab, industry, load]);

  function focusPanel() {
    requestAnimationFrame(() => panelRef.current?.focus());
  }

  function activateTab(next: Tab) {
    setTab(next);
    setFocusTab(next);
    setStatus(null);
    setArticleForm(null);
    setConfirming(null);
    setPublishTarget(null);
    setPublishReviewer("");
    setOpenContact(null);
    focusPanel();
  }

  function onTabKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    const currentIndex = TABS.findIndex(
      (item) => tabRefs.current.get(item) === document.activeElement,
    );
    const from = currentIndex === -1 ? TABS.indexOf(tab) : currentIndex;

    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      activateTab(focusTab);
      return;
    }

    let nextIndex: number;
    if (event.key === "ArrowRight") nextIndex = (from + 1) % TABS.length;
    else if (event.key === "ArrowLeft") nextIndex = (from - 1 + TABS.length) % TABS.length;
    else if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = TABS.length - 1;
    else return;

    event.preventDefault();
    const target = TABS[nextIndex];
    if (!target) return;
    setFocusTab(target);
    tabRefs.current.get(target)?.focus();
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy === "login") return;
    setBusy("login");
    setLoginError("");
    const result = await apiRequest<{ operator: { email: string }; csrf_token: string }>(
      "/api/proxy/v1/admin/auth/login",
      { method: "POST", body: { email, password } },
    );
    setBusy(null);
    if (!result.ok) {
      setLoginError(
        result.status === 503
          ? t(locale, "admin.notConfigured")
          : result.status === 401
            ? t(locale, "admin.invalid")
            : failureText(result, locale),
      );
      return;
    }
    setOperator(result.data?.operator.email ?? email);
    setCsrf(result.data?.csrf_token ?? readCookie("sn_csrf"));
    setPassword("");
    setStatus(null);
    setPhase("signedIn");
  }

  async function handleLogout() {
    if (busy === "logout") return;
    setBusy("logout");
    await apiRequest("/api/proxy/v1/admin/auth/logout", { method: "POST", csrf: csrfToken });
    endSession("");
  }

  async function mutate(
    id: string,
    path: string,
    method: string,
    body?: unknown,
  ): Promise<boolean> {
    setBusy(id);
    setStatus(null);
    const result = await apiRequest<{ data: unknown }>(path, { method, body, csrf: csrfToken });
    if (result.status === 401) {
      expire();
      return false;
    }
    if (!result.ok) {
      setBusy(null);
      setStatus({ kind: "error", text: failureText(result, locale) });
      return false;
    }
    setStatus({ kind: "ok", text: t(locale, "admin.saved") });
    await load(tab, industry);
    setBusy(null);
    return true;
  }

  async function handleCreateIndustry(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const ok = await mutate("channel:create", "/api/proxy/v1/admin/industries", "POST", {
      slug: data.get("slug"),
      name: data.get("name"),
      code: data.get("code"),
      theme: { layout: "editorial" },
    });
    if (ok) form.reset();
  }

  function formatInterval(minutes: number, activeLocale: Locale): string {
    if (minutes % 60 === 0) {
      return t(activeLocale, "admin.hoursValue", { n: minutes / 60 });
    }
    return t(activeLocale, "admin.minutesValue", { n: minutes });
  }

  function openChannelEditor(item: AdminIndustry) {
    setStatus(null);
    fillChannelDraft(item);
  }

  function fillChannelDraft(item: AdminIndustry) {
    const interval = item.fetch_interval_minutes ?? defaultFetchInterval;
    setChannelDraft({
      slug: item.slug,
      autoFetch: item.auto_fetch_enabled,
      useDefault: item.fetch_interval_minutes === null,
      hours: String(Number((interval / 60).toFixed(2))),
      consultation: item.offers.consultation,
      question: item.offers.question,
      secondary: item.offers.asset ? "asset" : item.offers.brief ? "brief" : "none",
    });
  }

  function patchChannelDraft(patch: Partial<ChannelDraft>) {
    setChannelDraft((current) => (current ? { ...current, ...patch } : current));
  }

  async function saveChannel(event: FormEvent<HTMLFormElement>, item: AdminIndustry) {
    event.preventDefault();
    if (!channelDraft) return;
    const hours = Number(channelDraft.hours);
    const minutes = Math.round(hours * 60);
    if (!Number.isFinite(hours) || minutes < 5 || minutes > 1440) {
      setStatus({ kind: "error", text: t(locale, "admin.cadenceInvalid") });
      return;
    }
    if (channelDraft.secondary === "asset" && !item.asset) {
      setStatus({ kind: "error", text: t(locale, "admin.assetUnavailable") });
      return;
    }
    const ok = await mutate(
      `channel:save:${item.slug}`,
      `/api/proxy/v1/admin/industries/${item.slug}`,
      "PATCH",
      {
        auto_fetch_enabled: channelDraft.autoFetch,
        fetch_interval_minutes: channelDraft.useDefault ? null : minutes,
        offers: {
          consultation: channelDraft.consultation,
          question: channelDraft.question,
          brief: channelDraft.secondary === "brief",
          asset: channelDraft.secondary === "asset",
        },
      },
    );
    if (ok) setChannelDraft(null);
  }

  function openPublish(issue: OfferIssue) {
    setOpenOffer(issue.id);
    setPublishTarget(issue.id);
    setPublishReviewer("");
  }

  async function submitPublish(issue: OfferIssue) {
    const reviewer = publishReviewer.trim();
    if (reviewer.length < 2) return;
    const ok = await mutate(
      `offer:publish:${issue.id}`,
      `/api/proxy/v1/admin/offers/${issue.id}/publish`,
      "POST",
      { reviewer },
    );
    if (ok) {
      setPublishTarget(null);
      setPublishReviewer("");
    }
  }

  async function unpublishOffer(issue: OfferIssue) {
    const ok = await mutate(
      `offer:unpublish:${issue.id}`,
      `/api/proxy/v1/admin/offers/${issue.id}/unpublish`,
      "POST",
    );
    if (ok) setConfirming(null);
  }

  async function buildOffer(issue: OfferIssue) {
    await mutate(
      `offer:build:${issue.industry}:${issue.offer_slug}`,
      "/api/proxy/v1/admin/offers/build",
      "POST",
      { industry: issue.industry, offer: issue.offer_slug, force: true },
    );
  }

  async function handleCreateSource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const ok = await mutate("source:create", "/api/proxy/v1/admin/sources", "POST", {
      industry,
      name: data.get("name"),
      feed_url: data.get("feed_url"),
      language: data.get("language"),
      trust: Number(data.get("trust") || 0.7),
    });
    if (ok) form.reset();
  }

  async function handleCreateTopic(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const ok = await mutate("topic:create", "/api/proxy/v1/admin/topics", "POST", {
      industry,
      slug: data.get("slug"),
      label: { en: data.get("label_en"), es: data.get("label_es") },
      weight: Number(data.get("weight") || 1),
      keywords: { en: [], es: [] },
    });
    if (ok) form.reset();
  }

  async function handleRefresh(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const ok = await mutate("refresh", "/api/proxy/v1/admin/refresh", "POST", {
      industry: refreshIndustry,
      force: true,
      full_reset: fullReset,
      confirmation: fullReset ? confirmation : null,
    });
    if (ok) {
      setFullReset(false);
      setConfirmation("");
    }
  }

  async function handleCreateKey(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    setBusy("key:create");
    setStatus(null);
    const result = await apiRequest<{ data: ApiKey & { key: string } }>(
      "/api/proxy/v1/admin/api-keys",
      {
        method: "POST",
        csrf: csrfToken,
        body: { label: data.get("label"), rate_limit: 600 },
      },
    );
    if (result.status === 401) {
      expire();
      return;
    }
    if (!result.ok || !result.data?.data) {
      setBusy(null);
      setStatus({ kind: "error", text: failureText(result, locale) });
      return;
    }
    setNewKey(result.data.data.key);
    form.reset();
    setStatus({ kind: "ok", text: t(locale, "admin.saved") });
    await load(tab, industry);
    setBusy(null);
  }

  function openArticleForm(id: string, kind: "hide" | "pin") {
    setStatus(null);
    setArticleForm({ id, kind });
    setHideReason("");
    setPinPosition("1");
    setPinWeight("1");
  }

  const cancelArticleForm = useCallback(() => {
    if (articleForm) focusElement(`article-action-${articleForm.kind}-${articleForm.id}`);
    setArticleForm(null);
    setHideReason("");
  }, [articleForm]);

  async function submitHide(articleId: string) {
    const reason = hideReason.trim();
    if (reason.length < 1 || reason.length > 200) return;
    const ok = await mutate(
      `article:hide:${articleId}`,
      `/api/proxy/v1/admin/articles/${articleId}/hide`,
      "POST",
      { reason },
    );
    if (ok) {
      setArticleForm(null);
      setHideReason("");
      focusPanel();
    }
  }

  async function submitPin(articleId: string) {
    const position = Number(pinPosition);
    const weight = Number(pinWeight);
    if (!Number.isInteger(position) || position < 1 || position > 5) return;
    if (!Number.isFinite(weight) || weight <= 0 || weight > 10) return;
    const ok = await mutate(`pin:create:${articleId}`, "/api/proxy/v1/admin/pins", "POST", {
      article_id: articleId,
      position,
      weight,
    });
    if (ok) {
      setArticleForm(null);
      setPinPosition("1");
      setPinWeight("1");
      focusPanel();
    }
  }

  const cancelConfirm = useCallback((rowKey: string) => {
    setConfirming(null);
    focusElement(`confirm-trigger-${rowKey}`);
  }, []);

  // Escape closes an open inline disclosure or two-step confirmation, wherever
  // focus sits (a submitting control is disabled while it runs, which drops focus).
  useEffect(() => {
    if (!articleForm && !confirming) return;
    function handleKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key !== "Escape") return;
      event.preventDefault();
      if (articleForm) cancelArticleForm();
      else if (confirming) cancelConfirm(confirming);
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [articleForm, confirming, cancelArticleForm, cancelConfirm]);

  async function deleteContact(contactId: string) {
    const ok = await mutate(
      `contact:delete:${contactId}`,
      `/api/proxy/v1/admin/contacts/${contactId}`,
      "DELETE",
    );
    if (ok) setConfirming(null);
  }

  async function deleteLead(leadId: string) {
    const ok = await mutate(`lead:delete:${leadId}`, `/api/proxy/v1/admin/leads/${leadId}`, "DELETE");
    if (ok) {
      setConfirming(null);
      focusPanel();
    }
  }

  async function revokeKey(keyId: string) {
    const ok = await mutate(
      `key:revoke:${keyId}`,
      `/api/proxy/v1/admin/api-keys/${keyId}`,
      "DELETE",
    );
    if (ok) {
      setConfirming(null);
      focusPanel();
    }
  }

  if (phase === "checking") {
    return (
      <p role="status" className="text-sm text-[var(--sn-muted)]">
        {t(locale, "admin.loading")}
      </p>
    );
  }

  if (phase !== "signedIn" || !operator) {
    return (
      <div className="mx-auto max-w-md">
        <h1 className="text-3xl font-semibold">{t(locale, "admin.loginTitle")}</h1>
        <p className="mt-2 text-sm text-[var(--sn-muted)]">{t(locale, "admin.loginIntro")}</p>
        <form onSubmit={handleLogin} className="sn-card mt-6 space-y-4 p-6">
          <TextField
            name="email"
            type="email"
            label={t(locale, "admin.email")}
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="username"
            required
          />
          <TextField
            name="password"
            type="password"
            label={t(locale, "admin.password")}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
          {loginError ? (
            <p role="alert" className="text-sm font-medium text-[var(--sn-accent)]">
              {loginError}
            </p>
          ) : null}
          <Button type="submit" className="w-full" disabled={busy === "login"}>
            {busy === "login" ? t(locale, "admin.saving") : t(locale, "admin.signIn")}
          </Button>
        </form>
        <p className="mt-4 text-sm">
          <Link href="/" className="underline">
            {t(locale, "nav.home")}
          </Link>
        </p>
      </div>
    );
  }

  const hideLength = hideReason.trim().length;
  const canHide = hideLength >= 1 && hideReason.length <= 200;
  const pinWeightValue = Number(pinWeight);
  const canPin = Number.isFinite(pinWeightValue) && pinWeightValue > 0 && pinWeightValue <= 10;
  const canReset = !fullReset || confirmation === "RESET";
  const auditActions = Array.from(new Set(audit.map((event) => event.action))).sort();
  const auditOptions =
    auditAction && !auditActions.includes(auditAction) ? [auditAction, ...auditActions] : auditActions;
  const industryOptions = industries.some((item) => item.slug === industry)
    ? industries
    : [
        ...industries,
        {
          slug: industry,
          name: industry,
          enabled: true,
          fetch_interval_minutes: null,
          effective_fetch_interval_minutes: defaultFetchInterval,
          auto_fetch_enabled: true,
          offers: { consultation: true, brief: true, question: true, asset: false },
          asset: null,
        },
      ];

  return (
    <div className="min-w-0">
      <header className="flex flex-wrap items-center gap-3 border-b border-[var(--sn-border)] pb-4">
        <h1 className="text-2xl font-semibold">{t(locale, "admin.title")}</h1>
        <span className="min-w-0 break-words text-sm text-[var(--sn-muted)]">{operator}</span>
        <div className="ml-auto flex flex-wrap items-center gap-3">
          <Link href="/" className="text-sm underline">
            {t(locale, "admin.viewSite")}
          </Link>
          <Button variant="ghost" onClick={() => void handleLogout()} disabled={busy === "logout"}>
            {busy === "logout" ? t(locale, "admin.saving") : t(locale, "admin.signOut")}
          </Button>
        </div>
      </header>

      <div role="tablist" aria-label={t(locale, "admin.title")} className="mt-4 flex flex-wrap gap-2">
        {TABS.map((item) => (
          <button
            key={item}
            id={`admin-tab-${item}`}
            type="button"
            role="tab"
            aria-selected={tab === item}
            aria-controls="admin-panel"
            tabIndex={focusTab === item ? 0 : -1}
            ref={(node) => {
              tabRefs.current.set(item, node);
            }}
            onClick={() => activateTab(item)}
            onKeyDown={onTabKeyDown}
            className={[
              "rounded-full px-4 py-2 text-sm font-medium transition-colors",
              tab === item
                ? "bg-[var(--sn-primary)] text-white"
                : "border border-[var(--sn-border)] text-[var(--sn-text)] hover:border-[var(--sn-primary)]",
            ].join(" ")}
          >
            {t(locale, `admin.tabs.${item}`)}
          </button>
        ))}
      </div>

      <div className="mt-3">
        <p role="status" aria-atomic="true" className="text-sm text-[var(--sn-muted)]">
          {status?.kind === "ok" ? status.text : ""}
        </p>
        <p role="alert" aria-atomic="true" className="text-sm font-medium text-[var(--sn-accent)]">
          {status?.kind === "error" ? status.text : ""}
        </p>
      </div>

      <div
        id="admin-panel"
        ref={panelRef}
        role="tabpanel"
        aria-labelledby={`admin-tab-${tab}`}
        tabIndex={0}
        className="mt-2"
      >
        {panelLoading ? (
          <p className="text-sm text-[var(--sn-muted)]">{t(locale, "admin.loading")}</p>
        ) : null}

        {tab === "overview" ? (
          <section>
            <dl className="sn-card grid gap-4 p-4 sm:grid-cols-3">
              <div>
                <dt className="text-sm text-[var(--sn-muted)]">{t(locale, "admin.sources")}</dt>
                <dd className="text-3xl font-semibold">{sources.length}</dd>
              </div>
              <div>
                <dt className="text-sm text-[var(--sn-muted)]">{t(locale, "admin.tabs.refresh")}</dt>
                <dd className="text-3xl font-semibold">{runs.length}</dd>
              </div>
              <div>
                <dt className="text-sm text-[var(--sn-muted)]">{t(locale, "admin.industry")}</dt>
                <dd className="text-3xl font-semibold">{industries.length}</dd>
              </div>
            </dl>
            <h2 className="mt-6 text-sm font-semibold">{t(locale, "admin.refresh")}</h2>
            <RunTable runs={runs.slice(0, 5)} locale={locale} />
          </section>
        ) : null}

        {tab === "channels" ? (
          <section>
            <div className="sn-card p-4">
              <p className="text-sm text-[var(--sn-text)]">{t(locale, "admin.channelsIntro")}</p>
              <p className="mt-1 text-xs text-[var(--sn-muted)]">
                {t(locale, "admin.deploymentDefault", {
                  interval: formatInterval(defaultFetchInterval, locale),
                })}
              </p>
            </div>

            <details className="sn-card mt-4 p-4">
              <summary className="cursor-pointer text-sm font-semibold">
                {t(locale, "admin.newIndustry")}
              </summary>
              <form
                className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"
                onSubmit={handleCreateIndustry}
              >
                <TextField name="slug" label={t(locale, "admin.slug")} required autoComplete="off" />
                <TextField name="name" label={t(locale, "admin.name")} required />
                <TextField name="code" label={t(locale, "admin.code")} required />
                <div className="flex items-end">
                  <Button type="submit" disabled={busy === "channel:create"}>
                    {busy === "channel:create" ? t(locale, "admin.saving") : t(locale, "admin.createIndustry")}
                  </Button>
                </div>
              </form>
              <p className="mt-2 text-xs text-[var(--sn-muted)]">{t(locale, "common.requiredNote")}</p>
            </details>

            <ul className="mt-4 border-t border-[var(--sn-border)]">
              {industries.length === 0 ? (
                <li className="border-b border-[var(--sn-border)] py-3 text-sm text-[var(--sn-muted)]">
                  {t(locale, "admin.empty")}
                </li>
              ) : (
                industries.map((item) => {
                  const editing = channelDraft?.slug === item.slug;
                  const interval = item.fetch_interval_minutes ?? defaultFetchInterval;
                  const schedule = !item.enabled
                    ? t(locale, "admin.channelDisabled")
                    : !item.auto_fetch_enabled
                      ? t(locale, "admin.autoFetchOff")
                      : item.fetch_interval_minutes !== null
                        ? t(locale, "admin.customCadence", {
                            interval: formatInterval(interval, locale),
                          })
                        : t(locale, "admin.defaultCadence", {
                            interval: formatInterval(interval, locale),
                          });
                  const activeOffers = [
                    item.offers.consultation && t(locale, "admin.offerConsultation"),
                    item.offers.question && t(locale, "admin.offerQuestion"),
                    item.offers.brief && t(locale, "admin.secondaryBrief"),
                    item.offers.asset && t(locale, "admin.secondaryAsset"),
                  ]
                    .filter((value): value is string => Boolean(value))
                    .join(" · ");
                  return (
                    <li key={item.slug} className="border-b border-[var(--sn-border)] py-4 text-sm">
                      <div className="flex flex-wrap items-start gap-3">
                        <div className="min-w-0">
                          <p>
                            <span className="font-medium">{item.name}</span>{" "}
                            <span className="text-[var(--sn-muted)]">/{item.slug}</span>{" "}
                            {item.enabled ? null : (
                              <span className="sn-chip">{t(locale, "admin.disabled")}</span>
                            )}
                          </p>
                          <p className="mt-1 text-xs text-[var(--sn-muted)]">{schedule}</p>
                          <p className="text-xs text-[var(--sn-muted)]">
                            {activeOffers || t(locale, "admin.offersInactive")}
                          </p>
                        </div>
                        <div className="ml-auto flex flex-wrap gap-2">
                          <button
                            type="button"
                            aria-expanded={editing}
                            onClick={() => (editing ? setChannelDraft(null) : openChannelEditor(item))}
                            className={QUIET_BUTTON}
                          >
                            {editing ? t(locale, "admin.close") : t(locale, "admin.manage")}
                          </button>
                          <button
                            type="button"
                            onClick={() =>
                              void mutate(
                                `channel:${item.slug}`,
                                `/api/proxy/v1/admin/industries/${item.slug}`,
                                "PATCH",
                                { enabled: !item.enabled },
                              )
                            }
                            disabled={busy === `channel:${item.slug}`}
                            className={QUIET_BUTTON}
                          >
                            {item.enabled ? t(locale, "admin.disable") : t(locale, "admin.enable")}
                          </button>
                        </div>
                      </div>

                      {editing && channelDraft ? (
                        <form
                          className="mt-4 grid gap-4 border-t border-[var(--sn-border)] pt-4"
                          onSubmit={(event) => void saveChannel(event, item)}
                        >
                          <fieldset>
                            <legend className="text-sm font-semibold">{t(locale, "admin.automation")}</legend>
                            <label className="mt-2 flex items-start gap-2">
                              <input
                                type="checkbox"
                                checked={channelDraft.autoFetch}
                                onChange={(event) => patchChannelDraft({ autoFetch: event.target.checked })}
                                className="mt-0.5 h-4 w-4"
                              />
                              <span>
                                {t(locale, "admin.autoFetch")}
                                <span className="mt-0.5 block text-xs text-[var(--sn-muted)]">
                                  {t(locale, "admin.autoFetchHint")}
                                </span>
                              </span>
                            </label>
                          </fieldset>

                          <fieldset>
                            <legend className="text-sm font-semibold">{t(locale, "admin.cadence")}</legend>
                            <label className="mt-2 flex items-center gap-2">
                              <input
                                type="radio"
                                name={`cadence-${item.slug}`}
                                checked={channelDraft.useDefault}
                                onChange={() =>
                                  patchChannelDraft({
                                    useDefault: true,
                                    hours: String(Number((defaultFetchInterval / 60).toFixed(2))),
                                  })
                                }
                              />
                              {t(locale, "admin.cadenceDefaultOption", {
                                interval: formatInterval(defaultFetchInterval, locale),
                              })}
                            </label>
                            <label className="mt-2 flex items-center gap-2">
                              <input
                                type="radio"
                                name={`cadence-${item.slug}`}
                                checked={!channelDraft.useDefault}
                                onChange={() => patchChannelDraft({ useDefault: false })}
                              />
                              {t(locale, "admin.cadenceCustomOption")}
                            </label>
                            {!channelDraft.useDefault ? (
                              <div className="mt-2 max-w-xs">
                                <TextField
                                  name={`hours-${item.slug}`}
                                  type="number"
                                  step="0.25"
                                  min="0.1"
                                  max="24"
                                  label={t(locale, "admin.cadenceHours")}
                                  hint={t(locale, "admin.cadenceHoursHint")}
                                  value={channelDraft.hours}
                                  onChange={(event) => patchChannelDraft({ hours: event.target.value })}
                                />
                              </div>
                            ) : null}
                          </fieldset>

                          <fieldset>
                            <legend className="text-sm font-semibold">{t(locale, "admin.freeOffers")}</legend>
                            <p className="mt-1 text-xs text-[var(--sn-muted)]">
                              {t(locale, "admin.freeOffersHint")}
                            </p>
                            <div className="mt-2 grid gap-3 sm:grid-cols-2">
                              <label className="flex items-start gap-2">
                                <input
                                  type="checkbox"
                                  checked={channelDraft.consultation}
                                  onChange={(event) =>
                                    patchChannelDraft({ consultation: event.target.checked })
                                  }
                                  className="mt-0.5 h-4 w-4"
                                />
                                <span>
                                  {t(locale, "admin.offerConsultation")}
                                  <span className="mt-0.5 block text-xs text-[var(--sn-muted)]">
                                    {t(locale, "admin.offerConsultationHint")}
                                  </span>
                                </span>
                              </label>
                              <label className="flex items-start gap-2">
                                <input
                                  type="checkbox"
                                  checked={channelDraft.question}
                                  onChange={(event) => patchChannelDraft({ question: event.target.checked })}
                                  className="mt-0.5 h-4 w-4"
                                />
                                <span>
                                  {t(locale, "admin.offerQuestion")}
                                  <span className="mt-0.5 block text-xs text-[var(--sn-muted)]">
                                    {t(locale, "admin.offerQuestionHint")}
                                  </span>
                                </span>
                              </label>
                            </div>
                          </fieldset>

                          <fieldset>
                            <legend className="text-sm font-semibold">{t(locale, "admin.secondaryOffer")}</legend>
                            <p className="mt-1 text-xs text-[var(--sn-muted)]">
                              {t(locale, "admin.secondaryOfferHint")}
                            </p>
                            {(
                              [
                                ["none", t(locale, "admin.secondaryNone"), false],
                                ["brief", t(locale, "admin.secondaryBrief"), false],
                                ["asset", t(locale, "admin.secondaryAsset"), !item.asset],
                              ] as const
                            ).map(([value, label, disabled]) => (
                              <label key={value} className="mt-2 flex items-center gap-2">
                                <input
                                  type="radio"
                                  name={`secondary-${item.slug}`}
                                  checked={channelDraft.secondary === value}
                                  disabled={disabled}
                                  onChange={() => patchChannelDraft({ secondary: value })}
                                />
                                {label}
                              </label>
                            ))}
                            {!item.asset ? (
                              <p className="mt-1 text-xs text-[var(--sn-muted)]">
                                {t(locale, "admin.assetUnavailable")}
                              </p>
                            ) : null}
                          </fieldset>

                          <div className="flex flex-wrap items-center gap-2">
                            <Button
                              type="submit"
                              disabled={busy === `channel:save:${item.slug}`}
                            >
                              {busy === `channel:save:${item.slug}`
                                ? t(locale, "admin.saving")
                                : t(locale, "admin.saveChannel")}
                            </Button>
                            <Button variant="ghost" onClick={() => setChannelDraft(null)}>
                              {t(locale, "admin.cancel")}
                            </Button>
                            <p className="text-xs text-[var(--sn-muted)]">
                              {t(locale, "admin.propagationHint")}
                            </p>
                          </div>
                        </form>
                      ) : null}
                    </li>
                  );
                })
              )}
            </ul>
          </section>
        ) : null}

        {tab === "offers" ? (
          <section>
            <p className="text-sm text-[var(--sn-muted)]">{t(locale, "admin.offersIntro")}</p>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <Caption>{t(locale, "admin.tabs.offers")}</Caption>
                <thead>
                  <tr className="border-b border-[var(--sn-border)]">
                    <Th>{t(locale, "admin.industry")}</Th>
                    <Th>{t(locale, "admin.offerIssue")}</Th>
                    <Th>{t(locale, "admin.issueDate")}</Th>
                    <Th>{t(locale, "admin.scope")}</Th>
                    <Th numeric>{t(locale, "admin.offerRows")}</Th>
                    <Th>{t(locale, "admin.status")}</Th>
                    <Th>{t(locale, "admin.offerGenerated")}</Th>
                    <Th>{t(locale, "admin.action")}</Th>
                  </tr>
                </thead>
                <tbody>
                  {offers.length === 0 ? (
                    <EmptyRow columns={8} locale={locale} />
                  ) : (
                    offers.map((issue) => {
                      const open = openOffer === issue.id;
                      const busyKey = `offer:build:${issue.industry}:${issue.offer_slug}`;
                      return (
                        <Fragment key={issue.id}>
                          <tr className="border-b border-[var(--sn-border)] align-top">
                            <td className="p-2">
                              {issue.industry}
                              <br />
                              <span className="text-xs text-[var(--sn-muted)]">{issue.offer_slug}</span>
                            </td>
                            <td className="p-2">
                              {issue.title}
                              <br />
                              <span className="text-xs text-[var(--sn-muted)]">
                                {issue.reviewer ?? t(locale, "admin.notSigned")}
                              </span>
                            </td>
                            <td className="whitespace-nowrap p-2">{issue.issue_date}</td>
                            <td className="p-2">{issue.scope}</td>
                            <td className="p-2 text-right tabular-nums">{issue.items.length}</td>
                            <td className="p-2">{offerStatusLabel(issue.status, locale)}</td>
                            <td className="whitespace-nowrap p-2">
                              {new Date(issue.generated_at).toLocaleString()}
                            </td>
                            <td className="whitespace-nowrap p-2 text-right">
                              <button
                                type="button"
                                aria-expanded={open}
                                onClick={() => setOpenOffer(open ? null : issue.id)}
                                className={QUIET_BUTTON}
                              >
                                {open ? t(locale, "admin.hide") : t(locale, "admin.view")}
                              </button>
                              {issue.status === "published" ? (
                                confirming === `offer-unpublish:${issue.id}` ? (
                                  <span className="ml-2 inline-flex flex-wrap items-center gap-2">
                                    <button
                                      type="button"
                                      autoFocus
                                      onClick={() => void unpublishOffer(issue)}
                                      disabled={busy === `offer:unpublish:${issue.id}`}
                                      className={DESTRUCTIVE_BUTTON}
                                    >
                                      {busy === `offer:unpublish:${issue.id}`
                                        ? t(locale, "admin.saving")
                                        : t(locale, "admin.confirmUnpublish")}
                                    </button>
                                    <button
                                      type="button"
                                      onClick={() => cancelConfirm(`offer-unpublish:${issue.id}`)}
                                      className={QUIET_BUTTON}
                                    >
                                      {t(locale, "admin.cancel")}
                                    </button>
                                  </span>
                                ) : (
                                  <button
                                    id={`confirm-trigger-offer-unpublish:${issue.id}`}
                                    type="button"
                                    onClick={() => setConfirming(`offer-unpublish:${issue.id}`)}
                                    className={[DESTRUCTIVE_BUTTON, "ml-2"].join(" ")}
                                  >
                                    {t(locale, "admin.unpublish")}
                                  </button>
                                )
                              ) : (
                                <>
                                  {issue.status === "draft" && issue.items.length > 0 ? (
                                    <button
                                      type="button"
                                      onClick={() => openPublish(issue)}
                                      className={[QUIET_BUTTON, "ml-2"].join(" ")}
                                    >
                                      {t(locale, "admin.publish")}
                                    </button>
                                  ) : null}
                                  <button
                                    type="button"
                                    onClick={() => void buildOffer(issue)}
                                    disabled={busy === busyKey}
                                    className={[QUIET_BUTTON, "ml-2"].join(" ")}
                                  >
                                    {busy === busyKey ? t(locale, "admin.saving") : t(locale, "admin.buildOffer")}
                                  </button>
                                </>
                              )}
                            </td>
                          </tr>
                          {open ? (
                            <tr className="border-b border-[var(--sn-border)] bg-[var(--sn-surface)]">
                              <td colSpan={8} className="p-3">
                                <p className="text-sm text-[var(--sn-text)]">{issue.standfirst}</p>
                                {publishTarget === issue.id ? (
                                  <form
                                    className="mt-3 border border-[var(--sn-border)] p-3"
                                    onSubmit={(event) => {
                                      event.preventDefault();
                                      void submitPublish(issue);
                                    }}
                                  >
                                    <TextField
                                      name={`reviewer-${issue.id}`}
                                      label={t(locale, "admin.publishReviewer")}
                                      hint={t(locale, "admin.publishHint")}
                                      value={publishReviewer}
                                      onChange={(event) => setPublishReviewer(event.target.value)}
                                      maxLength={120}
                                      required
                                      autoFocus
                                    />
                                    <div className="mt-2 flex flex-wrap items-center gap-2">
                                      <Button
                                        type="submit"
                                        disabled={
                                          publishReviewer.trim().length < 2 ||
                                          busy === `offer:publish:${issue.id}`
                                        }
                                      >
                                        {busy === `offer:publish:${issue.id}`
                                          ? t(locale, "admin.saving")
                                          : t(locale, "admin.publish")}
                                      </Button>
                                      <Button
                                        variant="ghost"
                                        onClick={() => {
                                          setPublishTarget(null);
                                          setPublishReviewer("");
                                        }}
                                      >
                                        {t(locale, "admin.cancel")}
                                      </Button>
                                    </div>
                                  </form>
                                ) : null}
                                {issue.error ? (
                                  <p role="alert" className="mt-2 text-sm font-medium text-[var(--sn-accent)]">
                                    {issue.error}
                                  </p>
                                ) : null}
                                <div className="mt-3 overflow-x-auto">
                                  <table className="w-full text-sm">
                                    <Caption>{t(locale, "admin.offerIssue")}</Caption>
                                    <thead>
                                      <tr className="border-b border-[var(--sn-border)]">
                                        <Th>{t(locale, "admin.createdAt")}</Th>
                                        <Th>{t(locale, "admin.titleColumn")}</Th>
                                        <Th>{t(locale, "admin.action")}</Th>
                                        <Th>{t(locale, "admin.source")}</Th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {issue.items.length === 0 ? (
                                        <EmptyRow columns={4} locale={locale} />
                                      ) : (
                                        issue.items.map((item) => (
                                          <tr key={`${issue.id}:${item.source_url}:${item.date}`} className="border-b border-[var(--sn-border)] align-top">
                                            <td className="whitespace-nowrap p-2">{item.date}</td>
                                            <td className="max-w-md p-2">
                                              <p className="font-medium">{item.headline}</p>
                                              <p className="mt-1 text-xs text-[var(--sn-muted)]">{item.change}</p>
                                            </td>
                                            <td className="max-w-xs p-2 text-xs">{item.action}</td>
                                            <td className="p-2 text-xs">
                                              <a
                                                href={item.source_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="underline"
                                              >
                                                {item.source_name}
                                              </a>
                                            </td>
                                          </tr>
                                        ))
                                      )}
                                    </tbody>
                                  </table>
                                </div>
                                <p className="mt-3 text-xs text-[var(--sn-muted)]">
                                  {t(locale, "admin.offerSourceVersion")}: {issue.source_version ?? "-"}
                                </p>
                              </td>
                            </tr>
                          ) : null}
                        </Fragment>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        {tab === "sources" ? (
          <section>
            <IndustryPicker industries={industryOptions} value={industry} onChange={setIndustry} locale={locale} />
            <form className="sn-card mt-4 grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-5" onSubmit={handleCreateSource}>
              <TextField name="name" label={t(locale, "admin.name")} required />
              <TextField
                name="feed_url"
                label={t(locale, "admin.feedUrl")}
                wrapperClassName="sm:col-span-2"
                required
                autoComplete="off"
              />
              <SelectField name="language" label={t(locale, "admin.language")} defaultValue="en">
                <option value="en">{t(locale, "localeSwitch.en")}</option>
                <option value="es">{t(locale, "localeSwitch.es")}</option>
              </SelectField>
              <TextField
                name="trust"
                type="number"
                step="0.05"
                min="0"
                max="1"
                defaultValue="0.7"
                label={t(locale, "admin.trust")}
              />
              <div className="sm:col-span-2 lg:col-span-5">
                <Button type="submit" disabled={busy === "source:create"}>
                  {busy === "source:create" ? t(locale, "admin.saving") : t(locale, "admin.create")}
                </Button>
              </div>
            </form>
            <p className="mt-2 text-xs text-[var(--sn-muted)]">{t(locale, "common.requiredNote")}</p>
            <div className="mt-6 overflow-x-auto">
              <table className="w-full text-sm">
                <Caption>{t(locale, "admin.tabs.sources")}</Caption>
                <thead>
                  <tr className="border-b border-[var(--sn-border)]">
                    <Th>{t(locale, "admin.name")}</Th>
                    <Th>{t(locale, "admin.language")}</Th>
                    <Th numeric>{t(locale, "admin.trust")}</Th>
                    <Th>{t(locale, "admin.status")}</Th>
                    <Th>
                      {t(locale, "admin.action")}
                    </Th>
                  </tr>
                </thead>
                <tbody>
                  {sources.length === 0 ? (
                    <EmptyRow columns={5} locale={locale} />
                  ) : (
                    sources.map((source) => (
                      <tr key={source.id} className="border-b border-[var(--sn-border)] align-top">
                        <td className="p-2">
                          {source.name}
                          <br />
                          <span className="break-all text-xs text-[var(--sn-muted)]">{source.feed_url}</span>
                        </td>
                        <td className="p-2">{source.language}</td>
                        <td className="p-2 text-right tabular-nums">{source.trust}</td>
                        <td className="p-2">
                          {source.status}
                          {source.consecutive_failures ? ` (${source.consecutive_failures})` : ""}
                          {source.cooldown_until ? (
                            <span className="mt-1 block text-xs text-[var(--sn-muted)]">
                              {t(locale, "admin.cooldown", {
                                when: source.cooldown_until.slice(0, 16).replace("T", " "),
                                reason: source.cooldown_reason || t(locale, "admin.reason"),
                              })}
                            </span>
                          ) : null}
                          {source.last_error ? (
                            <span className="mt-1 block break-all text-xs text-[var(--sn-muted)]">
                              {t(locale, "admin.lastError", { error: source.last_error })}
                            </span>
                          ) : null}
                        </td>
                        <td className="whitespace-nowrap p-2 text-right">
                          <button
                            type="button"
                            onClick={() =>
                              void mutate(
                                `source:toggle:${source.id}`,
                                `/api/proxy/v1/admin/sources/${source.id}`,
                                "PATCH",
                                { enabled: !source.enabled },
                              )
                            }
                            disabled={busy === `source:toggle:${source.id}`}
                            className={QUIET_BUTTON}
                          >
                            {source.enabled ? t(locale, "admin.hide") : t(locale, "admin.unhide")}
                          </button>
                          <button
                            type="button"
                            onClick={() =>
                              void mutate(
                                `source:delete:${source.id}`,
                                `/api/proxy/v1/admin/sources/${source.id}`,
                                "DELETE",
                              )
                            }
                            disabled={busy === `source:delete:${source.id}`}
                            className={[DESTRUCTIVE_BUTTON, "ml-2"].join(" ")}
                          >
                            {t(locale, "admin.delete")}
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        {tab === "topics" ? (
          <section>
            <IndustryPicker industries={industryOptions} value={industry} onChange={setIndustry} locale={locale} />
            <form className="sn-card mt-4 grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-5" onSubmit={handleCreateTopic}>
              <TextField name="slug" label={t(locale, "admin.slug")} required autoComplete="off" />
              <TextField
                name="label_en"
                label={`${t(locale, "admin.label")} (${t(locale, "localeSwitch.en")})`}
                required
              />
              <TextField
                name="label_es"
                label={`${t(locale, "admin.label")} (${t(locale, "localeSwitch.es")})`}
                required
              />
              <TextField
                name="weight"
                type="number"
                step="0.1"
                min="0.1"
                max="10"
                defaultValue="1"
                label={t(locale, "admin.sortOrder")}
              />
              <div className="sm:col-span-2 lg:col-span-5">
                <Button type="submit" disabled={busy === "topic:create"}>
                  {busy === "topic:create" ? t(locale, "admin.saving") : t(locale, "admin.create")}
                </Button>
              </div>
            </form>
            <p className="mt-2 text-xs text-[var(--sn-muted)]">{t(locale, "common.requiredNote")}</p>
            <ul className="mt-4 border-t border-[var(--sn-border)]">
              {topics.length === 0 ? (
                <li className="border-b border-[var(--sn-border)] py-3 text-sm text-[var(--sn-muted)]">
                  {t(locale, "admin.empty")}
                </li>
              ) : (
                topics.map((topic) => (
                  <li
                    key={topic.id}
                    className="flex flex-wrap items-center gap-3 border-b border-[var(--sn-border)] py-3 text-sm"
                  >
                    <span className="font-medium">{topic.slug}</span>
                    <span className="text-[var(--sn-muted)]">
                      {topic.label.en} / {topic.label.es}
                    </span>
                    <span className="ml-auto tabular-nums">{topic.weight}</span>
                    <button
                      type="button"
                      onClick={() =>
                        void mutate(`topic:delete:${topic.id}`, `/api/proxy/v1/admin/topics/${topic.id}`, "DELETE")
                      }
                      disabled={busy === `topic:delete:${topic.id}`}
                      className={DESTRUCTIVE_BUTTON}
                    >
                      {t(locale, "admin.delete")}
                    </button>
                  </li>
                ))
              )}
            </ul>
          </section>
        ) : null}

        {tab === "articles" ? (
          <section>
            <IndustryPicker industries={industryOptions} value={industry} onChange={setIndustry} locale={locale} />
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <Caption>{t(locale, "admin.tabs.articles")}</Caption>
                <thead>
                  <tr className="border-b border-[var(--sn-border)]">
                    <Th>{t(locale, "admin.titleColumn")}</Th>
                    <Th>{t(locale, "admin.language")}</Th>
                    <Th>{t(locale, "admin.status")}</Th>
                    <Th>
                      {t(locale, "admin.action")}
                    </Th>
                  </tr>
                </thead>
                <tbody>
                  {articles.length === 0 ? <EmptyRow columns={4} locale={locale} /> : null}
                  {articles.map((article) => {
                    const hideOpen = articleForm?.id === article.id && articleForm.kind === "hide";
                    const pinOpen = articleForm?.id === article.id && articleForm.kind === "pin";
                    return (
                      <Fragment key={article.id}>
                        <tr className="border-b border-[var(--sn-border)] align-top">
                          <td className="max-w-md p-2">
                            {article.title}
                            <br />
                            <span className="text-xs text-[var(--sn-muted)]">{article.publisher}</span>
                          </td>
                          <td className="p-2">{article.language}</td>
                          <td className="p-2">{article.status}</td>
                          <td className="whitespace-nowrap p-2 text-right">
                            {article.status === "hidden" ? (
                              <button
                                type="button"
                                onClick={() =>
                                  void mutate(
                                    `article:unhide:${article.id}`,
                                    `/api/proxy/v1/admin/articles/${article.id}/unhide`,
                                    "POST",
                                  )
                                }
                                disabled={busy === `article:unhide:${article.id}`}
                                className={QUIET_BUTTON}
                              >
                                {t(locale, "admin.unhide")}
                              </button>
                            ) : (
                              <button
                                id={`article-action-hide-${article.id}`}
                                type="button"
                                aria-expanded={hideOpen}
                                onClick={() => openArticleForm(article.id, "hide")}
                                className={QUIET_BUTTON}
                              >
                                {t(locale, "admin.hide")}
                              </button>
                            )}
                            <button
                              id={`article-action-pin-${article.id}`}
                              type="button"
                              aria-expanded={pinOpen}
                              onClick={() => openArticleForm(article.id, "pin")}
                              className={[QUIET_BUTTON, "ml-2"].join(" ")}
                            >
                              {t(locale, "admin.pin")}
                            </button>
                          </td>
                        </tr>

                        {hideOpen ? (
                          <tr className="border-b border-[var(--sn-border)] bg-[var(--sn-surface)]">
                            <td colSpan={4} className="p-3">
                              <form
                                onSubmit={(event) => {
                                  event.preventDefault();
                                  void submitHide(article.id);
                                }}
                                onKeyDown={(event) => {
                                  if (event.key === "Escape") {
                                    event.stopPropagation();
                                    cancelArticleForm();
                                  }
                                }}
                              >
                                <TextArea
                                  name={`reason-${article.id}`}
                                  label={t(locale, "admin.reason")}
                                  autoFocus
                                  hint={t(locale, "admin.reasonCount", { n: hideReason.length })}
                                  rows={3}
                                  maxLength={200}
                                  value={hideReason}
                                  onChange={(event) => setHideReason(event.target.value)}
                                  required
                                />
                                <div className="mt-2 flex flex-wrap items-center gap-2">
                                  <Button
                                    type="submit"
                                    disabled={!canHide || busy === `article:hide:${article.id}`}
                                  >
                                    {busy === `article:hide:${article.id}`
                                      ? t(locale, "admin.saving")
                                      : t(locale, "admin.save")}
                                  </Button>
                                  <Button variant="ghost" onClick={cancelArticleForm}>
                                    {t(locale, "admin.cancel")}
                                  </Button>
                                </div>
                              </form>
                            </td>
                          </tr>
                        ) : null}

                        {pinOpen ? (
                          <tr className="border-b border-[var(--sn-border)] bg-[var(--sn-surface)]">
                            <td colSpan={4} className="p-3">
                              <form
                                className="flex flex-wrap items-end gap-3"
                                onSubmit={(event) => {
                                  event.preventDefault();
                                  void submitPin(article.id);
                                }}
                                onKeyDown={(event) => {
                                  if (event.key === "Escape") {
                                    event.stopPropagation();
                                    cancelArticleForm();
                                  }
                                }}
                              >
                                <SelectField
                                  name={`position-${article.id}`}
                                  label={t(locale, "admin.position")}
                                  wrapperClassName="w-full sm:w-32"
                                  autoFocus
                                  value={pinPosition}
                                  onChange={(event) => setPinPosition(event.target.value)}
                                >
                                  {[1, 2, 3, 4, 5].map((value) => (
                                    <option key={value} value={String(value)}>
                                      {value}
                                    </option>
                                  ))}
                                </SelectField>
                                <TextField
                                  name={`weight-${article.id}`}
                                  type="number"
                                  step="0.1"
                                  min="0.1"
                                  max="10"
                                  label={t(locale, "admin.sortOrder")}
                                  wrapperClassName="w-full sm:w-32"
                                  value={pinWeight}
                                  onChange={(event) => setPinWeight(event.target.value)}
                                />
                                <Button
                                  type="submit"
                                  disabled={!canPin || busy === `pin:create:${article.id}`}
                                >
                                  {busy === `pin:create:${article.id}`
                                    ? t(locale, "admin.saving")
                                    : t(locale, "admin.save")}
                                </Button>
                                <Button variant="ghost" onClick={cancelArticleForm}>
                                  {t(locale, "admin.cancel")}
                                </Button>
                              </form>
                            </td>
                          </tr>
                        ) : null}
                      </Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <h2 className="mt-6 text-sm font-semibold">{t(locale, "admin.pins")}</h2>
            <ul className="mt-2 border-t border-[var(--sn-border)]">
              {pins.length === 0 ? (
                <li className="border-b border-[var(--sn-border)] py-3 text-sm text-[var(--sn-muted)]">
                  {t(locale, "admin.empty")}
                </li>
              ) : (
                pins.map((pin) => (
                  <li
                    key={pin.id}
                    className="flex flex-wrap items-center gap-3 border-b border-[var(--sn-border)] py-3 text-sm"
                  >
                    <span>
                      #{pin.position} {pin.title}
                    </span>
                    <button
                      type="button"
                      onClick={() =>
                        void mutate(`pin:delete:${pin.id}`, `/api/proxy/v1/admin/pins/${pin.id}`, "DELETE")
                      }
                      disabled={busy === `pin:delete:${pin.id}`}
                      className={[DESTRUCTIVE_BUTTON, "ml-auto"].join(" ")}
                    >
                      {t(locale, "admin.unpin")}
                    </button>
                  </li>
                ))
              )}
            </ul>
          </section>
        ) : null}

        {tab === "pins" ? (
          <section>
            <IndustryPicker industries={industryOptions} value={industry} onChange={setIndustry} locale={locale} />
            <ul className="mt-4 border-t border-[var(--sn-border)]">
              {pins.length === 0 ? (
                <li className="border-b border-[var(--sn-border)] py-3 text-sm text-[var(--sn-muted)]">
                  {t(locale, "admin.empty")}
                </li>
              ) : (
                pins.map((pin) => (
                  <li
                    key={pin.id}
                    className="flex flex-wrap items-center gap-3 border-b border-[var(--sn-border)] py-3 text-sm"
                  >
                    <span>
                      #{pin.position} {pin.title}
                    </span>
                    <button
                      type="button"
                      onClick={() =>
                        void mutate(`pin:delete:${pin.id}`, `/api/proxy/v1/admin/pins/${pin.id}`, "DELETE")
                      }
                      disabled={busy === `pin:delete:${pin.id}`}
                      className={[DESTRUCTIVE_BUTTON, "ml-auto"].join(" ")}
                    >
                      {t(locale, "admin.unpin")}
                    </button>
                  </li>
                ))
              )}
            </ul>
          </section>
        ) : null}

        {tab === "refresh" ? (
          <section>
            <form className="sn-card grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-4" onSubmit={handleRefresh}>
              <SelectField
                name="refresh_industry"
                label={t(locale, "admin.industry")}
                value={refreshIndustry}
                onChange={(event) => setRefreshIndustry(event.target.value)}
              >
                <option value="all">{t(locale, "admin.total")}</option>
                {industries.map((item) => (
                  <option key={item.slug} value={item.slug}>
                    {item.slug}
                  </option>
                ))}
              </SelectField>
              <TextField
                name="confirmation"
                label={t(locale, "admin.confirmReset")}
                value={confirmation}
                onChange={(event) => setConfirmation(event.target.value)}
                disabled={!fullReset}
                autoComplete="off"
              />
              <label className="flex items-center gap-2 text-sm sm:col-span-2">
                <input
                  type="checkbox"
                  name="full_reset"
                  checked={fullReset}
                  onChange={(event) => setFullReset(event.target.checked)}
                  className="h-4 w-4"
                />
                {t(locale, "admin.fullReset")}
              </label>
              <div className="sm:col-span-2 lg:col-span-4">
                <Button type="submit" disabled={busy === "refresh" || !canReset}>
                  {busy === "refresh" ? t(locale, "admin.saving") : t(locale, "admin.triggerRefresh")}
                </Button>
              </div>
            </form>
            <div className="mt-6">
              <RunTable runs={runs} locale={locale} />
            </div>
          </section>
        ) : null}

        {tab === "keys" ? (
          <section>
            <form className="sn-card flex flex-wrap items-end gap-3 p-4" onSubmit={handleCreateKey}>
              <div className="w-full sm:max-w-xs">
                <TextField name="label" label={t(locale, "admin.label")} required autoComplete="off" />
              </div>
              <Button type="submit" disabled={busy === "key:create"}>
                {busy === "key:create" ? t(locale, "admin.saving") : t(locale, "admin.create")}
              </Button>
            </form>
            <p className="mt-2 text-xs text-[var(--sn-muted)]">{t(locale, "common.requiredNote")}</p>

            {newKey ? (
              <div className="mt-4 border border-[var(--sn-accent)] p-3 text-sm">
                <p className="font-semibold">{t(locale, "admin.keyShownOnce")}</p>
                <code className="mt-1 block break-all">{newKey}</code>
                <Button variant="ghost" className="mt-3" onClick={() => setNewKey("")}>
                  {t(locale, "common.dismiss")}
                </Button>
              </div>
            ) : null}

            <ul className="mt-4 border-t border-[var(--sn-border)]">
              {keys.length === 0 ? (
                <li className="border-b border-[var(--sn-border)] py-3 text-sm text-[var(--sn-muted)]">
                  {t(locale, "admin.empty")}
                </li>
              ) : (
                keys.map((key) => {
                  const rowKey = `key-${key.id}`;
                  const confirmingRow = confirming === rowKey;
                  return (
                    <li
                      key={key.id}
                      className="flex flex-wrap items-center gap-3 border-b border-[var(--sn-border)] py-3 text-sm"
                    >
                      <span className="font-medium">{key.label}</span>
                      <span className="text-[var(--sn-muted)]">{key.prefix}…</span>
                      <span className="text-[var(--sn-muted)]">
                        {t(locale, "admin.lastUsed")}:{" "}
                        {key.last_used_at ? new Date(key.last_used_at).toLocaleString() : "-"}
                      </span>
                      {confirmingRow ? (
                        <span
                          className="ml-auto flex flex-wrap items-center gap-2"
                          onKeyDown={(event) => {
                            if (event.key === "Escape") {
                              event.preventDefault();
                              cancelConfirm(rowKey);
                            }
                          }}
                        >
                          <button
                            type="button"
                            autoFocus
                            onClick={() => void revokeKey(key.id)}
                            disabled={busy === `key:revoke:${key.id}`}
                            className={DESTRUCTIVE_BUTTON}
                          >
                            {busy === `key:revoke:${key.id}`
                              ? t(locale, "admin.saving")
                              : t(locale, "admin.confirmDelete")}
                          </button>
                          <button type="button" onClick={() => cancelConfirm(rowKey)} className={QUIET_BUTTON}>
                            {t(locale, "admin.cancel")}
                          </button>
                        </span>
                      ) : (
                        <button
                          id={`confirm-trigger-${rowKey}`}
                          type="button"
                          onClick={() => setConfirming(rowKey)}
                          className={[DESTRUCTIVE_BUTTON, "ml-auto"].join(" ")}
                        >
                          {t(locale, "admin.revoke")}
                        </button>
                      )}
                    </li>
                  );
                })
              )}
            </ul>
          </section>
        ) : null}

        {tab === "audit" ? (
          <section>
            <div className="max-w-xs">
              <SelectField
                name="audit_action"
                label={t(locale, "admin.filterAction")}
                value={auditAction}
                onChange={(event) => setAuditAction(event.target.value)}
              >
                <option value="">{t(locale, "admin.allActions")}</option>
                {auditOptions.map((action) => (
                  <option key={action} value={action}>
                    {action}
                  </option>
                ))}
              </SelectField>
            </div>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <Caption>{t(locale, "admin.audit")}</Caption>
                <thead>
                  <tr className="border-b border-[var(--sn-border)]">
                    <Th>{t(locale, "admin.createdAt")}</Th>
                    <Th>{t(locale, "admin.action")}</Th>
                    <Th>{t(locale, "admin.entity")}</Th>
                    <Th>{t(locale, "admin.email")}</Th>
                  </tr>
                </thead>
                <tbody>
                  {audit.length === 0 ? (
                    <EmptyRow columns={4} locale={locale} />
                  ) : (
                    audit.map((event) => (
                      <tr key={event.id} className="border-b border-[var(--sn-border)]">
                        <td className="p-2 whitespace-nowrap">
                          {new Date(event.created_at).toLocaleString()}
                        </td>
                        <td className="p-2">{event.action}</td>
                        <td className="p-2">{event.entity}</td>
                        <td className="p-2">{event.actor}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        {tab === "leads" ? (
          <section>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <Caption>{t(locale, "admin.leads")}</Caption>
                <thead>
                  <tr className="border-b border-[var(--sn-border)]">
                    <Th>{t(locale, "admin.industry")}</Th>
                    <Th>{t(locale, "admin.name")}</Th>
                    <Th>{t(locale, "admin.email")}</Th>
                    <Th>{t(locale, "admin.status")}</Th>
                    <Th>
                      {t(locale, "admin.action")}
                    </Th>
                  </tr>
                </thead>
                <tbody>
                  {leads.length === 0 ? (
                    <EmptyRow columns={5} locale={locale} />
                  ) : (
                    leads.map((lead) => {
                      const rowKey = `lead-${lead.id}`;
                      const confirmingRow = confirming === rowKey;
                      return (
                        <tr key={lead.id} className="border-b border-[var(--sn-border)]">
                          <td className="p-2">{lead.industry}</td>
                          <td className="p-2">{lead.name}</td>
                          <td className="p-2">{lead.email}</td>
                          <td className="p-2">
                            <select
                              aria-label={t(locale, "admin.status")}
                              value={lead.status}
                              onChange={(event) =>
                                void mutate(
                                  `lead:status:${lead.id}`,
                                  `/api/proxy/v1/admin/leads/${lead.id}`,
                                  "PATCH",
                                  { status: event.target.value },
                                )
                              }
                              disabled={busy === `lead:status:${lead.id}`}
                              className="rounded border border-[var(--sn-border)] bg-[var(--sn-bg)] px-2 py-1 text-sm"
                            >
                              {LEAD_STATUSES.map((status) => (
                                <option key={status} value={status}>
                                  {status}
                                </option>
                              ))}
                            </select>
                          </td>
                          <td className="whitespace-nowrap p-2 text-right">
                            <a
                              href={`/api/proxy/v1/admin/leads/${lead.id}/export`}
                              target="_blank"
                              rel="noreferrer"
                              className={QUIET_BUTTON}
                            >
                              {t(locale, "admin.export")}
                            </a>
                            {confirmingRow ? (
                              <span
                                className="ml-2 inline-flex flex-wrap items-center gap-2"
                                onKeyDown={(event) => {
                                  if (event.key === "Escape") {
                                    event.preventDefault();
                                    cancelConfirm(rowKey);
                                  }
                                }}
                              >
                                <button
                                  type="button"
                                  autoFocus
                                  onClick={() => void deleteLead(lead.id)}
                                  disabled={busy === `lead:delete:${lead.id}`}
                                  className={DESTRUCTIVE_BUTTON}
                                >
                                  {busy === `lead:delete:${lead.id}`
                                    ? t(locale, "admin.saving")
                                    : t(locale, "admin.confirmDelete")}
                                </button>
                                <button
                                  type="button"
                                  onClick={() => cancelConfirm(rowKey)}
                                  className={QUIET_BUTTON}
                                >
                                  {t(locale, "admin.cancel")}
                                </button>
                              </span>
                            ) : (
                              <button
                                id={`confirm-trigger-${rowKey}`}
                                type="button"
                                onClick={() => setConfirming(rowKey)}
                                className={[DESTRUCTIVE_BUTTON, "ml-2"].join(" ")}
                              >
                                {t(locale, "admin.delete")}
                              </button>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        {tab === "contacts" ? (
          <section>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <Caption>{t(locale, "admin.tabs.contacts")}</Caption>
                <thead>
                  <tr className="border-b border-[var(--sn-border)]">
                    <Th>{t(locale, "admin.industry")}</Th>
                    <Th>{t(locale, "admin.name")}</Th>
                    <Th>{t(locale, "admin.country")}</Th>
                    <Th>{t(locale, "admin.source")}</Th>
                    <Th>{t(locale, "admin.status")}</Th>
                    <Th>{t(locale, "admin.createdAt")}</Th>
                    <Th>{t(locale, "admin.action")}</Th>
                  </tr>
                </thead>
                <tbody>
                  {contacts.length === 0 ? (
                    <EmptyRow columns={7} locale={locale} />
                  ) : (
                    contacts.map((contact) => {
                      const rowKey = `contact-${contact.id}`;
                      const confirmingRow = confirming === rowKey;
                      const open = openContact === contact.id;
                      const campaign = Object.entries(contact.utm)
                        .map(([key, value]) => `${key.replace("utm_", "")}=${value}`)
                        .join(" · ");
                      return (
                        <Fragment key={contact.id}>
                          <tr className="border-b border-[var(--sn-border)] align-top">
                            <td className="p-2">{contact.industry ?? "-"}</td>
                            <td className="p-2">
                              {contact.name}
                              <br />
                              <span className="text-xs text-[var(--sn-muted)]">{contact.email}</span>
                            </td>
                            <td className="p-2">{contact.country ?? "-"}</td>
                            <td className="max-w-xs p-2 text-xs text-[var(--sn-muted)]">
                              {contact.source_page ?? "-"}
                              {campaign ? <span className="block">{campaign}</span> : null}
                            </td>
                            <td className="p-2">
                              <select
                                aria-label={t(locale, "admin.status")}
                                value={contact.status}
                                onChange={(event) =>
                                  void mutate(
                                    `contact:status:${contact.id}`,
                                    `/api/proxy/v1/admin/contacts/${contact.id}`,
                                    "PATCH",
                                    { status: event.target.value },
                                  )
                                }
                                disabled={busy === `contact:status:${contact.id}`}
                                className="rounded border border-[var(--sn-border)] bg-[var(--sn-bg)] px-2 py-1 text-sm"
                              >
                                {CONTACT_STATUSES.map((status) => (
                                  <option key={status} value={status}>
                                    {status}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td className="whitespace-nowrap p-2">
                              {new Date(contact.created_at).toLocaleString()}
                            </td>
                            <td className="whitespace-nowrap p-2 text-right">
                              <button
                                type="button"
                                aria-expanded={open}
                                onClick={() => setOpenContact(open ? null : contact.id)}
                                className={QUIET_BUTTON}
                              >
                                {open ? t(locale, "admin.hide") : t(locale, "admin.view")}
                              </button>
                              {confirmingRow ? (
                                <span className="ml-2 inline-flex flex-wrap items-center gap-2">
                                  <button
                                    type="button"
                                    autoFocus
                                    onClick={() => void deleteContact(contact.id)}
                                    disabled={busy === `contact:delete:${contact.id}`}
                                    className={DESTRUCTIVE_BUTTON}
                                  >
                                    {busy === `contact:delete:${contact.id}`
                                      ? t(locale, "admin.saving")
                                      : t(locale, "admin.confirmDelete")}
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => cancelConfirm(rowKey)}
                                    className={QUIET_BUTTON}
                                  >
                                    {t(locale, "admin.cancel")}
                                  </button>
                                </span>
                              ) : (
                                <button
                                  id={`confirm-trigger-${rowKey}`}
                                  type="button"
                                  onClick={() => setConfirming(rowKey)}
                                  className={[DESTRUCTIVE_BUTTON, "ml-2"].join(" ")}
                                >
                                  {t(locale, "admin.delete")}
                                </button>
                              )}
                            </td>
                          </tr>
                          {open ? (
                            <tr className="border-b border-[var(--sn-border)] bg-[var(--sn-surface)]">
                              <td colSpan={7} className="p-3 text-sm">
                                {contact.phone ? (
                                  <p>
                                    <span className="font-semibold">{t(locale, "admin.phone")}:</span>{" "}
                                    {contact.phone}
                                  </p>
                                ) : null}
                                <p className="mt-2 whitespace-pre-line">{contact.message}</p>
                                <p className="mt-2 text-xs text-[var(--sn-muted)]">
                                  {t(locale, "admin.campaign")}: {campaign || "-"}
                                </p>
                                <p className="mt-1 text-xs text-[var(--sn-muted)]">
                                  {t(locale, "admin.session")}: {contact.session_hash ?? "-"}
                                </p>
                              </td>
                            </tr>
                          ) : null}
                        </Fragment>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        {tab === "partners" ? (
          <section>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <Caption>{t(locale, "admin.partners")}</Caption>
                <thead>
                  <tr className="border-b border-[var(--sn-border)]">
                    <Th>{t(locale, "admin.industry")}</Th>
                    <Th>{t(locale, "admin.name")}</Th>
                    <Th>{t(locale, "admin.email")}</Th>
                    <Th>{t(locale, "admin.status")}</Th>
                    <Th>
                      {t(locale, "admin.action")}
                    </Th>
                  </tr>
                </thead>
                <tbody>
                  {partners.length === 0 ? (
                    <EmptyRow columns={5} locale={locale} />
                  ) : (
                    partners.map((partner) => (
                      <tr key={partner.id} className="border-b border-[var(--sn-border)]">
                        <td className="p-2">{partner.industry}</td>
                        <td className="p-2">{partner.name}</td>
                        <td className="p-2">{partner.contact_email}</td>
                        <td className="p-2">{partner.status}</td>
                        <td className="whitespace-nowrap p-2 text-right">
                          <button
                            type="button"
                            onClick={() =>
                              void mutate(
                                `partner:save:${partner.id}`,
                                `/api/proxy/v1/admin/partners/${partner.id}`,
                                "PATCH",
                                { status: partner.status === "active" ? "disabled" : "active" },
                              )
                            }
                            disabled={busy === `partner:save:${partner.id}`}
                            className={QUIET_BUTTON}
                          >
                            {t(locale, "admin.save")}
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        {tab === "funnel" ? (
          <section className="overflow-x-auto">
            <table className="w-full text-sm">
              <Caption>{t(locale, "admin.tabs.funnel")}</Caption>
              <thead>
                <tr className="border-b border-[var(--sn-border)]">
                  <Th>{t(locale, "admin.industry")}</Th>
                  <Th numeric>Impr.</Th>
                  <Th numeric>Clicks</Th>
                  <Th numeric>CTR</Th>
                  <Th numeric>Starts</Th>
                  <Th numeric>Submit</Th>
                  <Th numeric>{t(locale, "admin.leads")}</Th>
                </tr>
              </thead>
              <tbody>
                {!funnel || funnel.channels.length === 0 ? (
                  <EmptyRow columns={7} locale={locale} />
                ) : (
                  funnel.channels.map((row) => (
                    <tr
                      key={`${row.surface ?? ""}|${row.industry}`}
                      className="border-b border-[var(--sn-border)]"
                    >
                      <td className="p-2 font-medium">
                        {row.surface ? `${row.surface}:${row.industry || "all"}` : row.industry}
                      </td>
                      <td className="p-2 text-right tabular-nums">{row.events.cta_impression ?? 0}</td>
                      <td className="p-2 text-right tabular-nums">{row.events.cta_click ?? 0}</td>
                      <td className="p-2 text-right tabular-nums">
                        {row.rates.click_rate === null
                          ? "-"
                          : `${Math.round(row.rates.click_rate * 1000) / 10}%`}
                      </td>
                      <td className="p-2 text-right tabular-nums">{row.events.lead_form_start ?? 0}</td>
                      <td className="p-2 text-right tabular-nums">
                        {(row.events.lead_submit ?? 0) + (row.events.question_submit ?? 0)}
                      </td>
                      <td className="p-2 text-right tabular-nums">
                        {Object.values(row.leads_by_kind).reduce((sum, value) => sum + value, 0)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </section>
        ) : null}
      </div>
    </div>
  );
}

function IndustryPicker({
  industries,
  value,
  onChange,
  locale,
}: {
  industries: AdminIndustry[];
  value: string;
  onChange: (value: string) => void;
  locale: Locale;
}) {
  return (
    <div className="max-w-xs">
      <SelectField
        name="industry"
        label={t(locale, "admin.industry")}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {industries.map((item) => (
          <option key={item.slug} value={item.slug}>
            {item.slug}
          </option>
        ))}
      </SelectField>
    </div>
  );
}

function RunTable({ runs, locale }: { runs: Run[]; locale: Locale }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <Caption>{t(locale, "admin.refresh")}</Caption>
        <thead>
          <tr className="border-b border-[var(--sn-border)]">
            <Th>{t(locale, "admin.industry")}</Th>
            <Th>{t(locale, "admin.tabs.refresh")}</Th>
            <Th>{t(locale, "admin.status")}</Th>
            <Th>{t(locale, "admin.createdAt")}</Th>
          </tr>
        </thead>
        <tbody>
          {runs.length === 0 ? (
            <EmptyRow columns={4} locale={locale} />
          ) : (
            runs.map((run) => (
              <tr key={run.run_id} className="border-b border-[var(--sn-border)]">
                <td className="p-2">{run.industry ?? "-"}</td>
                <td className="p-2">{run.trigger}</td>
                <td className="p-2">{runStatusLabel(run.status, locale)}</td>
                <td className="p-2 whitespace-nowrap">{new Date(run.started_at).toLocaleString()}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
