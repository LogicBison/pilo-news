"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { t, type Locale } from "@/lib/i18n";

type Tab =
  | "overview"
  | "channels"
  | "sources"
  | "topics"
  | "articles"
  | "pins"
  | "refresh"
  | "keys"
  | "audit"
  | "leads"
  | "partners";

interface AdminIndustry {
  slug: string;
  name: string;
  enabled: boolean;
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
interface Partner {
  id: string;
  industry: string;
  name: string;
  contact_email: string;
  status: string;
}

function readCookie(name: string): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match?.[1] ? decodeURIComponent(match[1]) : "";
}

async function apiRequest<T>(
  path: string,
  options: { method?: string; body?: unknown; csrf?: string } = {},
): Promise<{ ok: boolean; status: number; data: T | null }> {
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
    const payload = response.status === 204 ? null : await response.json().catch(() => null);
    return { ok: response.ok, status: response.status, data: payload as T | null };
  } catch {
    return { ok: false, status: 0, data: null };
  }
}

export function AdminConsole({ locale }: { locale: Locale }) {
  const [operator, setOperator] = useState<string | null>(null);
  const [csrf, setCsrf] = useState("");
  const [tab, setTab] = useState<Tab>("overview");
  const [industry, setIndustry] = useState("legal");
  const [industries, setIndustries] = useState<AdminIndustry[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [articles, setArticles] = useState<AdminArticle[]>([]);
  const [pins, setPins] = useState<Pin[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [message, setMessage] = useState("");
  const [newKey, setNewKey] = useState("");
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("");

  const csrfToken = csrf || readCookie("sn_csrf");

  const load = useCallback(
    async (activeTab: Tab, activeIndustry: string) => {
      if (!operator) return;
      if (activeTab === "channels") {
        const result = await apiRequest<{ data: AdminIndustry[] }>("/api/proxy/v1/admin/industries");
        setIndustries(result.data?.data ?? []);
      } else if (activeTab === "overview") {
        const [sourcesResult, runsResult] = await Promise.all([
          apiRequest<{ data: Source[] }>("/api/proxy/v1/admin/sources"),
          apiRequest<{ data: Run[] }>("/api/proxy/v1/admin/refresh"),
        ]);
        setSources(sourcesResult.data?.data ?? []);
        setRuns(runsResult.data?.data ?? []);
      } else if (activeTab === "sources") {
        const result = await apiRequest<{ data: Source[] }>(
          `/api/proxy/v1/admin/sources?industry=${activeIndustry}`,
        );
        setSources(result.data?.data ?? []);
      } else if (activeTab === "topics") {
        const result = await apiRequest<{ data: Topic[] }>(
          `/api/proxy/v1/admin/topics?industry=${activeIndustry}`,
        );
        setTopics(result.data?.data ?? []);
      } else if (activeTab === "articles") {
        const result = await apiRequest<{ data: AdminArticle[] }>(
          `/api/proxy/v1/admin/articles?industry=${activeIndustry}`,
        );
        setArticles(result.data?.data ?? []);
        const pinResult = await apiRequest<{ data: Pin[] }>(
          `/api/proxy/v1/admin/pins?industry=${activeIndustry}`,
        );
        setPins(pinResult.data?.data ?? []);
      } else if (activeTab === "pins") {
        const result = await apiRequest<{ data: Pin[] }>(
          `/api/proxy/v1/admin/pins?industry=${activeIndustry}`,
        );
        setPins(result.data?.data ?? []);
      } else if (activeTab === "refresh") {
        const result = await apiRequest<{ data: Run[] }>("/api/proxy/v1/admin/refresh");
        setRuns(result.data?.data ?? []);
      } else if (activeTab === "keys") {
        const result = await apiRequest<{ data: ApiKey[] }>("/api/proxy/v1/admin/api-keys");
        setKeys(result.data?.data ?? []);
      } else if (activeTab === "audit") {
        const result = await apiRequest<{ data: AuditEvent[] }>("/api/proxy/v1/admin/audit");
        setAudit(result.data?.data ?? []);
      } else if (activeTab === "leads") {
        const result = await apiRequest<{ data: Lead[] }>("/api/proxy/v1/admin/leads");
        setLeads(result.data?.data ?? []);
      } else if (activeTab === "partners") {
        const result = await apiRequest<{ data: Partner[] }>("/api/proxy/v1/admin/partners");
        setPartners(result.data?.data ?? []);
      }
    },
    [operator],
  );

  useEffect(() => {
    async function bootstrap() {
      const me = await apiRequest<{ operator: { email: string } }>("/api/proxy/v1/admin/auth/me");
      if (me.ok && me.data?.operator) {
        setOperator(me.data.operator.email);
        setCsrf(readCookie("sn_csrf"));
      }
      const industryResult = await apiRequest<{ data: AdminIndustry[] }>(
        "/api/proxy/v1/admin/industries",
      );
      if (industryResult.ok && industryResult.data?.data) {
        setIndustries(industryResult.data.data);
      }
    }
    void bootstrap();
  }, []);

  useEffect(() => {
    if (operator) void load(tab, industry);
  }, [operator, tab, industry, load]);

  useEffect(() => {
    if (!operator) return;
    void apiRequest<{ data: AdminIndustry[] }>("/api/proxy/v1/admin/industries").then((result) => {
      if (result.ok && result.data?.data) setIndustries(result.data.data);
    });
  }, [operator]);

  async function login(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    const result = await apiRequest<{ operator: { email: string }; csrf_token: string }>(
      "/api/proxy/v1/admin/auth/login",
      { method: "POST", body: { email, password } },
    );
    if (!result.ok) {
      setMessage(result.status === 503 ? t(locale, "admin.notConfigured") : t(locale, "admin.invalid"));
      return;
    }
    setOperator(result.data?.operator.email ?? email);
    setCsrf(result.data?.csrf_token ?? readCookie("sn_csrf"));
    setPassword("");
  }

  async function logout() {
    await apiRequest("/api/proxy/v1/admin/auth/logout", { method: "POST", csrf: csrfToken });
    setOperator(null);
    setCsrf("");
  }

  async function mutate(path: string, method: string, body?: unknown) {
    setMessage("");
    const result = await apiRequest<{ data: unknown }>(path, { method, body, csrf: csrfToken });
    if (!result.ok) {
      setMessage(`${t(locale, "common.error")} (${result.status})`);
      return false;
    }
    await load(tab, industry);
    return true;
  }

  if (!operator) {
    return (
      <div className="mx-auto max-w-md">
        <h1 className="text-3xl font-semibold">{t(locale, "admin.loginTitle")}</h1>
        <p className="mt-2 text-sm text-[var(--sn-muted)]">{t(locale, "admin.loginIntro")}</p>
        <form onSubmit={login} className="sn-card mt-6 space-y-4 p-6">
          <label className="flex flex-col gap-1 text-sm font-medium">
            {t(locale, "admin.email")}
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              className="sn-input"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm font-medium">
            {t(locale, "admin.password")}
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              className="sn-input"
            />
          </label>
          <div aria-live="polite" className="text-sm text-red-700">{message}</div>
          <button type="submit" className="sn-btn">
            {t(locale, "admin.signIn")}
          </button>
        </form>
        <p className="mt-4 text-sm">
          <Link href={`/${locale === "es" ? "es/" : ""}legal`} className="underline">
            {t(locale, "nav.home")}
          </Link>
        </p>
      </div>
    );
  }

  const tabs: Tab[] = [
    "overview",
    "channels",
    "sources",
    "topics",
    "articles",
    "pins",
    "refresh",
    "keys",
    "audit",
    "leads",
    "partners",
  ];

  return (
    <div>
      <div className="flex flex-wrap items-center gap-3 border-b border-[var(--sn-border)] pb-4">
        <h1 className="text-2xl font-semibold">{t(locale, "admin.title")}</h1>
        <span className="text-sm text-[var(--sn-muted)]">{operator}</span>
        <button type="button" onClick={logout} className="ml-auto rounded-full border border-[var(--sn-border)] px-4 py-2 text-sm">
          {t(locale, "admin.signOut")}
        </button>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {tabs.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setTab(item)}
            className={`rounded-full px-4 py-2 text-sm font-medium ${
              tab === item ? "bg-[var(--sn-primary)] text-white" : "border border-[var(--sn-border)]"
            }`}
          >
            {t(locale, `admin.tabs.${item}`)}
          </button>
        ))}
      </div>
      <div aria-live="polite" className="mt-3 text-sm text-red-700">{message}</div>

      {tab === "overview" ? (
        <section className="mt-6 grid gap-4 sm:grid-cols-3">
          <div className="sn-card p-4">
            <p className="text-sm text-[var(--sn-muted)]">{t(locale, "admin.sources")}</p>
            <p className="text-3xl font-semibold">{sources.length}</p>
          </div>
          <div className="sn-card p-4">
            <p className="text-sm text-[var(--sn-muted)]">{t(locale, "admin.tabs.refresh")}</p>
            <p className="text-3xl font-semibold">{runs.length}</p>
          </div>
          <div className="sn-card p-4">
            <p className="text-sm text-[var(--sn-muted)]">{t(locale, "admin.industry")}</p>
            <p className="text-3xl font-semibold">{industries.length}</p>
          </div>
          <div className="sm:col-span-3">
            <RunTable runs={runs.slice(0, 5)} locale={locale} />
          </div>
        </section>
      ) : null}

      {tab === "channels" ? (
        <section className="mt-6">
          <form
            className="grid gap-3 sn-card p-4 md:grid-cols-5"
            onSubmit={async (event) => {
              event.preventDefault();
              const form = event.currentTarget;
              const data = new FormData(form);
              const ok = await mutate("/api/proxy/v1/admin/industries", "POST", {
                slug: data.get("slug"),
                name: data.get("name"),
                code: data.get("code"),
                theme: { layout: data.get("layout") ?? "editorial" },
              });
              if (ok) {
                form.reset();
                const result = await apiRequest<{ data: AdminIndustry[] }>("/api/proxy/v1/admin/industries");
                setIndustries(result.data?.data ?? []);
              }
            }}
          >
            <input name="slug" aria-label={t(locale, "admin.slug")} placeholder={t(locale, "admin.slug")} required className="sn-card px-3 py-2 text-sm" />
            <input name="name" aria-label={t(locale, "admin.name")} placeholder={t(locale, "admin.name")} required className="sn-card px-3 py-2 text-sm" />
            <input name="code" aria-label={t(locale, "admin.code")} placeholder={t(locale, "admin.code")} required className="sn-card px-3 py-2 text-sm" />
            <select name="layout" className="sn-card px-3 py-2 text-sm">
              <option value="editorial">editorial</option>
              <option value="professional">professional</option>
              <option value="academic">academic</option>
            </select>
            <button type="submit" className="sn-btn px-4 py-2">{t(locale, "admin.createIndustry")}</button>
          </form>
          <ul className="mt-4 space-y-2">
            {industries.map((item) => (
              <li key={item.slug} className="flex items-center gap-3 sn-card p-3 text-sm">
                <span className="font-medium">{item.name}</span>
                <span className="text-[var(--sn-muted)]">/{item.slug}</span>
                <span className="ml-auto">{item.enabled ? "on" : "off"}</span>
                <button
                  type="button"
                  onClick={() => mutate(`/api/proxy/v1/admin/industries/${item.slug}`, "PATCH", { enabled: !item.enabled })}
                  className="sn-card px-3 py-1"
                >
                  {item.enabled ? t(locale, "admin.disable") : t(locale, "admin.enable")}
                </button>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {tab === "sources" ? (
        <section className="mt-6">
          <IndustryPicker industries={industries} value={industry} onChange={setIndustry} locale={locale} />
          <form
            className="mt-4 grid gap-3 sn-card p-4 md:grid-cols-5"
            onSubmit={async (event) => {
              event.preventDefault();
              const form = event.currentTarget;
              const data = new FormData(form);
              const ok = await mutate("/api/proxy/v1/admin/sources", "POST", {
                industry,
                name: data.get("name"),
                feed_url: data.get("feed_url"),
                language: data.get("language"),
                trust: Number(data.get("trust") ?? 0.7),
              });
              if (ok) form.reset();
            }}
          >
            <input name="name" aria-label={t(locale, "admin.name")} placeholder={t(locale, "admin.name")} required className="sn-card px-3 py-2 text-sm" />
            <input name="feed_url" aria-label={t(locale, "admin.feedUrl")} placeholder={t(locale, "admin.feedUrl")} required className="sn-card px-3 py-2 text-sm md:col-span-2" />
            <select name="language" className="sn-card px-3 py-2 text-sm" defaultValue="en">
              <option value="en">en</option>
              <option value="es">es</option>
            </select>
            <button type="submit" className="sn-btn px-4 py-2">
              {t(locale, "admin.create")}
            </button>
          </form>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead><tr className="border-b border-[var(--sn-border)]"><th className="p-2">{t(locale, "admin.name")}</th><th className="p-2">{t(locale, "admin.language")}</th><th className="p-2">{t(locale, "admin.trust")}</th><th className="p-2">{t(locale, "admin.status")}</th><th className="p-2" /></tr></thead>
              <tbody>
                {sources.map((source) => (
                  <tr key={source.id} className="border-b border-[var(--sn-border)]">
                    <td className="p-2">{source.name}<br /><span className="text-xs text-[var(--sn-muted)]">{source.feed_url}</span></td>
                    <td className="p-2">{source.language}</td>
                    <td className="p-2">{source.trust}</td>
                    <td className="p-2">{source.status}{source.consecutive_failures ? ` (${source.consecutive_failures})` : ""}</td>
                    <td className="p-2 text-right">
                      <button type="button" onClick={() => mutate(`/api/proxy/v1/admin/sources/${source.id}`, "PATCH", { enabled: !source.enabled })} className="sn-card px-3 py-1">
                        {source.enabled ? t(locale, "admin.hide") : t(locale, "admin.unhide")}
                      </button>
                      <button type="button" onClick={() => mutate(`/api/proxy/v1/admin/sources/${source.id}`, "DELETE")} className="ml-2 rounded border border-red-300 px-3 py-1 text-red-700">
                        {t(locale, "admin.delete")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {tab === "topics" ? (
        <section className="mt-6">
          <IndustryPicker industries={industries} value={industry} onChange={setIndustry} locale={locale} />
          <form
            className="mt-4 grid gap-3 sn-card p-4 md:grid-cols-5"
            onSubmit={async (event) => {
              event.preventDefault();
              const form = event.currentTarget;
              const data = new FormData(form);
              const ok = await mutate("/api/proxy/v1/admin/topics", "POST", {
                industry,
                slug: data.get("slug"),
                label: { en: data.get("label_en"), es: data.get("label_es") },
                weight: Number(data.get("weight") ?? 1),
                keywords: { en: [], es: [] },
              });
              if (ok) form.reset();
            }}
          >
            <input name="slug" aria-label="slug" placeholder="slug" required className="sn-card px-3 py-2 text-sm" />
            <input name="label_en" aria-label="Label EN" placeholder="Label EN" required className="sn-card px-3 py-2 text-sm" />
            <input name="label_es" aria-label="Label ES" placeholder="Label ES" required className="sn-card px-3 py-2 text-sm" />
            <input name="weight" type="number" step="0.1" defaultValue="1" aria-label={t(locale, "admin.sortOrder")} className="sn-card px-3 py-2 text-sm" />
            <button type="submit" className="sn-btn px-4 py-2">{t(locale, "admin.create")}</button>
          </form>
          <ul className="mt-4 space-y-2">
            {topics.map((topic) => (
              <li key={topic.id} className="flex items-center gap-3 sn-card p-3 text-sm">
                <span className="font-medium">{topic.slug}</span>
                <span className="text-[var(--sn-muted)]">{topic.label.en} / {topic.label.es}</span>
                <span className="ml-auto">{topic.weight}</span>
                <button type="button" onClick={() => mutate(`/api/proxy/v1/admin/topics/${topic.id}`, "DELETE")} className="rounded border border-red-300 px-3 py-1 text-red-700">{t(locale, "admin.delete")}</button>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {tab === "articles" ? (
        <section className="mt-6">
          <IndustryPicker industries={industries} value={industry} onChange={setIndustry} locale={locale} />
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead><tr className="border-b border-[var(--sn-border)]"><th className="p-2">{t(locale, "admin.titleColumn")}</th><th className="p-2">{t(locale, "admin.language")}</th><th className="p-2">{t(locale, "admin.status")}</th><th className="p-2" /></tr></thead>
              <tbody>
                {articles.map((article) => (
                  <tr key={article.id} className="border-b border-[var(--sn-border)]">
                    <td className="max-w-md p-2">{article.title}<br /><span className="text-xs text-[var(--sn-muted)]">{article.publisher}</span></td>
                    <td className="p-2">{article.language}</td>
                    <td className="p-2">{article.status}</td>
                    <td className="p-2 text-right">
                      {article.status === "hidden" ? (
                        <button type="button" onClick={() => mutate(`/api/proxy/v1/admin/articles/${article.id}/unhide`, "POST")} className="sn-card px-3 py-1">{t(locale, "admin.unhide")}</button>
                      ) : (
                        <button type="button" onClick={() => {
                          const reason = window.prompt(t(locale, "admin.reason"));
                          if (reason) void mutate(`/api/proxy/v1/admin/articles/${article.id}/hide`, "POST", { reason });
                        }} className="rounded border border-amber-300 px-3 py-1 text-amber-800">{t(locale, "admin.hide")}</button>
                      )}
                      <button type="button" onClick={() => {
                        const position = Number(window.prompt(t(locale, "admin.position"), "1") ?? 0);
                        if (position >= 1 && position <= 5) void mutate("/api/proxy/v1/admin/pins", "POST", { article_id: article.id, position, weight: 1 });
                      }} className="ml-2 sn-card px-3 py-1">{t(locale, "admin.pin")}</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {pins.length > 0 ? (
            <div className="mt-4">
              <h3 className="text-sm font-semibold">{t(locale, "admin.pins")}</h3>
              <ul className="mt-2 space-y-1 text-sm">
                {pins.map((pin) => (
                  <li key={pin.id} className="flex items-center gap-3 sn-card p-2">
                    <span>#{pin.position} {pin.title}</span>
                    <button type="button" onClick={() => mutate(`/api/proxy/v1/admin/pins/${pin.id}`, "DELETE")} className="ml-auto rounded border border-red-300 px-3 py-1 text-red-700">{t(locale, "admin.unpin")}</button>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>
      ) : null}

      {tab === "pins" ? <section className="mt-6"><IndustryPicker industries={industries} value={industry} onChange={setIndustry} locale={locale} /><ul className="mt-4 space-y-2">{pins.map((pin) => (<li key={pin.id} className="flex items-center gap-3 sn-card p-3 text-sm"><span>#{pin.position} {pin.title}</span><button type="button" onClick={() => mutate(`/api/proxy/v1/admin/pins/${pin.id}`, "DELETE")} className="ml-auto rounded border border-red-300 px-3 py-1 text-red-700">{t(locale, "admin.unpin")}</button></li>))}</ul></section> : null}

      {tab === "refresh" ? (
        <section className="mt-6">
          <form
            className="grid gap-3 sn-card p-4 md:grid-cols-5"
            onSubmit={async (event) => {
              event.preventDefault();
              const data = new FormData(event.currentTarget);
              const fullReset = data.get("full_reset") === "on";
              await mutate("/api/proxy/v1/admin/refresh", "POST", {
                industry: data.get("industry"),
                force: true,
                full_reset: fullReset,
                confirmation: fullReset ? data.get("confirmation") : null,
              });
            }}
          >
            <select name="industry" className="sn-card px-3 py-2 text-sm">
              <option value="all">all</option>
              {industries.map((item) => <option key={item.slug} value={item.slug}>{item.slug}</option>)}
            </select>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" name="full_reset" />{t(locale, "admin.fullReset")}</label>
            <input name="confirmation" placeholder={t(locale, "admin.confirmReset")} className="sn-card px-3 py-2 text-sm" />
            <button type="submit" className="sn-btn px-4 py-2">{t(locale, "admin.triggerRefresh")}</button>
          </form>
          <div className="mt-4"><RunTable runs={runs} locale={locale} /></div>
        </section>
      ) : null}

      {tab === "keys" ? (
        <section className="mt-6">
          <form
            className="flex flex-wrap gap-3 sn-card p-4"
            onSubmit={async (event) => {
              event.preventDefault();
              const data = new FormData(event.currentTarget);
              const result = await apiRequest<{ data: ApiKey & { key: string } }>("/api/proxy/v1/admin/api-keys", {
                method: "POST",
                csrf: csrfToken,
                body: { label: data.get("label"), rate_limit: Number(data.get("rate_limit") ?? 600) },
              });
              if (result.ok && result.data?.data) {
                setNewKey(result.data.data.key);
                event.currentTarget.reset();
                await load(tab, industry);
              } else {
                setMessage(`${t(locale, "common.error")} (${result.status})`);
              }
            }}
          >
            <input name="label" aria-label={t(locale, "admin.label")} placeholder={t(locale, "admin.label")} required className="sn-card px-3 py-2 text-sm" />
            <input name="rate_limit" type="number" defaultValue="600" aria-label={t(locale, "admin.prefix")} className="w-32 sn-card px-3 py-2 text-sm" />
            <button type="submit" className="sn-btn px-4 py-2">{t(locale, "admin.create")}</button>
          </form>
          {newKey ? <p className="mt-3 rounded border border-amber-300 bg-amber-50 p-3 text-sm"><strong>{t(locale, "admin.keyShownOnce")}</strong><br /><code className="break-all">{newKey}</code></p> : null}
          <ul className="mt-4 space-y-2">
            {keys.map((key) => (
              <li key={key.id} className="flex items-center gap-3 sn-card p-3 text-sm">
                <span className="font-medium">{key.label}</span><span className="text-[var(--sn-muted)]">{key.prefix}…</span><span>{key.enabled ? "on" : "off"}</span>
                <button type="button" onClick={() => mutate(`/api/proxy/v1/admin/api-keys/${key.id}`, "DELETE")} className="ml-auto rounded border border-red-300 px-3 py-1 text-red-700">{t(locale, "admin.revoke")}</button>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {tab === "audit" ? (
        <section className="mt-6 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead><tr className="border-b border-[var(--sn-border)]"><th className="p-2">{t(locale, "admin.createdAt")}</th><th className="p-2">{t(locale, "admin.action")}</th><th className="p-2">{t(locale, "admin.entity")}</th><th className="p-2">{t(locale, "admin.email")}</th></tr></thead>
            <tbody>{audit.map((event) => (<tr key={event.id} className="border-b border-[var(--sn-border)]"><td className="p-2">{new Date(event.created_at).toLocaleString()}</td><td className="p-2">{event.action}</td><td className="p-2">{event.entity}</td><td className="p-2">{event.actor}</td></tr>))}</tbody>
          </table>
        </section>
      ) : null}

      {tab === "leads" ? (
        <section className="mt-6 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead><tr className="border-b border-[var(--sn-border)]"><th className="p-2">{t(locale, "admin.industry")}</th><th className="p-2">{t(locale, "admin.name")}</th><th className="p-2">{t(locale, "admin.email")}</th><th className="p-2">{t(locale, "admin.status")}</th><th className="p-2" /></tr></thead>
            <tbody>{leads.map((lead) => (<tr key={lead.id} className="border-b border-[var(--sn-border)]"><td className="p-2">{lead.industry}</td><td className="p-2">{lead.name}</td><td className="p-2">{lead.email}</td><td className="p-2"><select value={lead.status} onChange={(event) => mutate(`/api/proxy/v1/admin/leads/${lead.id}`, "PATCH", { status: event.target.value })} className="sn-card px-2 py-1 text-sm">{["new","routed","contacted","qualified","closed","spam"].map((status) => <option key={status} value={status}>{status}</option>)}</select></td><td className="p-2 text-right"><a href={`/api/proxy/v1/admin/leads/${lead.id}/export`} target="_blank" rel="noreferrer" className="sn-card px-3 py-1">{t(locale, "admin.export")}</a><button type="button" onClick={() => mutate(`/api/proxy/v1/admin/leads/${lead.id}`, "DELETE")} className="ml-2 rounded border border-red-300 px-3 py-1 text-red-700">{t(locale, "admin.delete")}</button></td></tr>))}</tbody>
          </table>
        </section>
      ) : null}

      {tab === "partners" ? (
        <section className="mt-6 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead><tr className="border-b border-[var(--sn-border)]"><th className="p-2">{t(locale, "admin.industry")}</th><th className="p-2">{t(locale, "admin.name")}</th><th className="p-2">{t(locale, "admin.email")}</th><th className="p-2">{t(locale, "admin.status")}</th><th className="p-2" /></tr></thead>
            <tbody>{partners.map((partner) => (<tr key={partner.id} className="border-b border-[var(--sn-border)]"><td className="p-2">{partner.industry}</td><td className="p-2">{partner.name}</td><td className="p-2">{partner.contact_email}</td><td className="p-2">{partner.status}</td><td className="p-2 text-right"><button type="button" onClick={() => mutate(`/api/proxy/v1/admin/partners/${partner.id}`, "PATCH", { status: partner.status === "active" ? "disabled" : "active" })} className="sn-card px-3 py-1">{t(locale, "admin.save")}</button></td></tr>))}</tbody>
          </table>
        </section>
      ) : null}
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
    <label className="flex flex-wrap items-center gap-2 text-sm font-medium">
      {t(locale, "admin.industry")}
      <select value={value} onChange={(event) => onChange(event.target.value)} className="sn-card px-3 py-2 text-sm">
        {industries.map((item) => <option key={item.slug} value={item.slug}>{item.slug}</option>)}
      </select>
    </label>
  );
}

function RunTable({ runs, locale }: { runs: Run[]; locale: Locale }) {
  if (runs.length === 0) return <p className="text-sm text-[var(--sn-muted)]">{t(locale, "admin.empty")}</p>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead><tr className="border-b border-[var(--sn-border)]"><th className="p-2">{t(locale, "admin.industry")}</th><th className="p-2">{t(locale, "admin.tabs.refresh")}</th><th className="p-2">{t(locale, "admin.status")}</th><th className="p-2">{t(locale, "admin.createdAt")}</th></tr></thead>
        <tbody>{runs.map((run) => (<tr key={run.run_id} className="border-b border-[var(--sn-border)]"><td className="p-2">{run.industry ?? "-"}</td><td className="p-2">{run.trigger}</td><td className="p-2">{run.status}</td><td className="p-2">{new Date(run.started_at).toLocaleString()}</td></tr>))}</tbody>
      </table>
    </div>
  );
}
