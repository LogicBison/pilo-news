-- 002_seed_industries.sql - five launch channels, locales, disclaimers, CTA config.
-- Idempotent: upsert by slug; safe to run on every start.

INSERT INTO industries (slug, code, name, theme, locales, disclaimers, cta, sort_order, retention_days, enabled)
VALUES
(
    'legal', 'LEGAL_TECH', 'Legal Services & Corporate Governance',
    '{"primary":"#1e3a5f","accent":"#8a4b08","bg":"#ffffff","surface":"#f6f7f9","text":"#111827","muted":"#4b5563","border":"#d8dee6","radius":"10px","font_heading":"Georgia, Times New Roman, serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"editorial"}'::jsonb,
    ARRAY['en','es']::TEXT[],
    '{"en":"News, not legal advice. Attorney advertising. No outcome is guaranteed.","es":"Noticias, no asesoría legal. Publicidad de abogados. No se garantiza resultado alguno."}'::jsonb,
    '{"kind":"consultation","headline":{"en":"Speak with a vetted legal professional","es":"Hable con un profesional legal verificado"},"body":{"en":"Tell us what you need. We route qualified requests to an independent partner, at no cost and with no obligation.","es":"Cuéntenos qué necesita. Canalizamos solicitudes calificadas a un socio independiente, sin costo ni compromiso."},"label":{"en":"Request a consultation","es":"Solicitar una consulta"},"secondary_label":{"en":"Get the weekly brief","es":"Recibir el resumen semanal"}}'::jsonb,
    10, 7, TRUE
),
(
    'financial', 'FINTECH_CORE', 'Financial Services & Banking',
    '{"primary":"#0b4f6c","accent":"#0f766e","bg":"#ffffff","surface":"#f1f5f9","text":"#0f172a","muted":"#475569","border":"#cbd5e1","radius":"6px","font_heading":"Arial, Helvetica, sans-serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"professional"}'::jsonb,
    ARRAY['en','es']::TEXT[],
    '{"en":"News, not investment advice. Investing involves risk.","es":"Noticias, no asesoría de inversión. Invertir implica riesgos."}'::jsonb,
    '{"kind":"consultation","headline":{"en":"Talk to a regulated financial advisor","es":"Hable con un asesor financiero regulado"},"body":{"en":"Share your situation. We route qualified requests to an independent, regulated partner.","es":"Cuéntenos su situación. Canalizamos solicitudes calificadas a un socio independiente y regulado."},"label":{"en":"Request a consultation","es":"Solicitar una consulta"},"secondary_label":{"en":"Get the weekly brief","es":"Recibir el resumen semanal"}}'::jsonb,
    20, 7, TRUE
),
(
    'behavioral-health', 'BEHAVIORAL_HEALTH_EHR', 'Psychiatry & Clinical Psychology',
    '{"primary":"#4c1d95","accent":"#9a3412","bg":"#ffffff","surface":"#faf5ff","text":"#1f2937","muted":"#4b5563","border":"#ddd6fe","radius":"12px","font_heading":"Georgia, Times New Roman, serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"editorial"}'::jsonb,
    ARRAY['en','es']::TEXT[],
    '{"en":"News, not medical advice. If this is an emergency, call 911.","es":"Noticias, no asesoría médica. Si es una emergencia, llame al 911."}'::jsonb,
    '{"kind":"consultation","headline":{"en":"Find the right clinician for your practice","es":"Encuentre el profesional clínico adecuado"},"body":{"en":"Tell us what you need. We route qualified requests to an independent, licensed partner.","es":"Cuéntenos qué necesita. Canalizamos solicitudes calificadas a un socio independiente y licenciado."},"label":{"en":"Request a consultation","es":"Solicitar una consulta"},"secondary_label":{"en":"Get the weekly brief","es":"Recibir el resumen semanal"}}'::jsonb,
    30, 7, TRUE
),
(
    'education', 'EDTECH_LMS', 'Education & Higher Academics',
    '{"primary":"#1d4ed8","accent":"#b45309","bg":"#fffdf7","surface":"#f8fafc","text":"#1f2937","muted":"#4b5563","border":"#dbe4f0","radius":"10px","font_heading":"Georgia, Times New Roman, serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"academic"}'::jsonb,
    ARRAY['en','es']::TEXT[],
    '{"en":"Program details and outcomes vary; verify with the institution.","es":"Los detalles y resultados de cada programa varían; confirme con la institución."}'::jsonb,
    '{"kind":"brief","headline":{"en":"Bring verified program news to your inbox","es":"Reciba noticias verificadas de programas"},"body":{"en":"A short weekly brief for counselors, faculty, and administrators. Unsubscribe anytime.","es":"Un resumen semanal breve para consejeros, docentes y administradores. Cancele cuando quiera."},"label":{"en":"Get the weekly brief","es":"Recibir el resumen semanal"},"secondary_label":{"en":"Request a consultation","es":"Solicitar una consulta"}}'::jsonb,
    40, 7, TRUE
),
(
    'logistics', 'SUPPLY_CHAIN_WMS', 'Logistics & Supply Chain',
    '{"primary":"#14532d","accent":"#b45309","bg":"#ffffff","surface":"#f0fdf4","text":"#111827","muted":"#4b5563","border":"#c7e3d0","radius":"6px","font_heading":"Arial, Helvetica, sans-serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"professional"}'::jsonb,
    ARRAY['en','es']::TEXT[],
    '{"en":"Rates and timelines vary by lane and season.","es":"Las tarifas y los plazos varían según la ruta y la temporada."}'::jsonb,
    '{"kind":"consultation","headline":{"en":"Source capacity with a vetted partner","es":"Encuentre capacidad con un socio verificado"},"body":{"en":"Tell us your lanes and volumes. We route qualified requests to an independent logistics partner.","es":"Cuéntenos sus rutas y volúmenes. Canalizamos solicitudes calificadas a un socio logístico independiente."},"label":{"en":"Request a consultation","es":"Solicitar una consulta"},"secondary_label":{"en":"Get the weekly brief","es":"Recibir el resumen semanal"}}'::jsonb,
    50, 7, TRUE
)
ON CONFLICT (slug) DO UPDATE SET
    code = EXCLUDED.code,
    name = EXCLUDED.name,
    theme = EXCLUDED.theme,
    locales = EXCLUDED.locales,
    disclaimers = EXCLUDED.disclaimers,
    cta = EXCLUDED.cta,
    sort_order = EXCLUDED.sort_order,
    retention_days = EXCLUDED.retention_days,
    enabled = EXCLUDED.enabled,
    updated_at = now();

INSERT INTO industry_locales (industry_id, locale, name, tagline)
SELECT i.id, v.locale, v.name, v.tagline
FROM industries i
JOIN (
    VALUES
        ('legal', 'en', 'Legal Services & Corporate Governance', 'Regulation, courts, and corporate governance - in plain language.'),
        ('legal', 'es', 'Servicios Legales y Gobierno Corporativo', 'Regulación, tribunales y gobierno corporativo, en lenguaje claro.'),
        ('financial', 'en', 'Financial Services & Banking', 'Markets, regulation, and banking technology for professionals.'),
        ('financial', 'es', 'Servicios Financieros y Banca', 'Mercados, regulación y tecnología bancaria para profesionales.'),
        ('behavioral-health', 'en', 'Psychiatry & Clinical Psychology', 'Clinical practice, research, and policy for mental health professionals.'),
        ('behavioral-health', 'es', 'Psiquiatría y Psicología Clínica', 'Práctica clínica, investigación y políticas para profesionales de salud mental.'),
        ('education', 'en', 'Education & Higher Academics', 'Policy, admissions, research, and learning technology.'),
        ('education', 'es', 'Educación y Academia', 'Políticas, admisiones, investigación y tecnología educativa.'),
        ('logistics', 'en', 'Logistics & Supply Chain', 'Freight, ports, customs, and supply chain operations.'),
        ('logistics', 'es', 'Logística y Cadena de Suministro', 'Carga, puertos, aduanas y operaciones de cadena de suministro.')
) AS v (slug, locale, name, tagline) ON v.slug = i.slug
ON CONFLICT (industry_id, locale) DO UPDATE SET
    name = EXCLUDED.name,
    tagline = EXCLUDED.tagline;
