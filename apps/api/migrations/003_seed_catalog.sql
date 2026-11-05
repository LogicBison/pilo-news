-- 003_seed_catalog.sql - topics, launch feed portfolio, and one partner per channel.
-- Idempotent: inserts only missing catalog rows; never overwrites operator edits.

INSERT INTO topics (industry_id, slug, label, weight, keywords)
SELECT i.id, v.slug, v.label::jsonb, v.weight, v.keywords::jsonb
FROM industries i
JOIN (
    VALUES
        ('legal', 'litigation', '{"en":"Litigation","es":"Litigios"}', 1.30,
         '{"en":["litigation","lawsuit","court","trial","verdict","appeal"],"es":["litigio","demanda","tribunal","juicio","sentencia","apelación"]}'),
        ('legal', 'regulation', '{"en":"Regulation & Compliance","es":"Regulación y Cumplimiento"}', 1.40,
         '{"en":["regulation","compliance","gdpr","sec","ftc","rule"],"es":["regulación","cumplimiento","protección de datos","norma","regla"]}'),
        ('legal', 'corporate', '{"en":"Corporate Governance","es":"Gobierno Corporativo"}', 1.20,
         '{"en":["merger","acquisition","governance","board","shareholder","deal"],"es":["fusión","adquisición","gobierno corporativo","consejo","accionista"]}'),
        ('legal', 'legal-tech', '{"en":"Legal Technology","es":"Tecnología Legal"}', 1.10,
         '{"en":["legal tech","artificial intelligence","automation","software","e-discovery"],"es":["tecnología legal","inteligencia artificial","automatización","software"]}'),
        ('financial', 'banking', '{"en":"Banking","es":"Banca"}', 1.30,
         '{"en":["bank","banking","deposits","lending","credit"],"es":["banco","banca","depósitos","crédito","préstamos"]}'),
        ('financial', 'markets', '{"en":"Markets","es":"Mercados"}', 1.20,
         '{"en":["market","stocks","bond","equities","trading","yield"],"es":["mercado","bolsa","bonos","acciones","renta fija"]}'),
        ('financial', 'regulation', '{"en":"Regulation","es":"Regulación"}', 1.40,
         '{"en":["sec","finra","aml","kyc","regulation","compliance"],"es":["regulación","cumplimiento","blanqueo","supervisión"]}'),
        ('financial', 'fintech', '{"en":"Fintech & Payments","es":"Fintech y Pagos"}', 1.20,
         '{"en":["fintech","payments","digital wallet","open banking","stablecoin"],"es":["fintech","pagos","billetera digital","banca abierta"]}'),
        ('behavioral-health', 'clinical', '{"en":"Clinical Practice","es":"Práctica Clínica"}', 1.30,
         '{"en":["therapy","therapist","psychotherapy","counseling","clinician"],"es":["terapia","terapeuta","psicoterapia","consejería","clínico"]}'),
        ('behavioral-health', 'research', '{"en":"Research","es":"Investigación"}', 1.20,
         '{"en":["study","research","trial","findings","journal"],"es":["estudio","investigación","ensayo","hallazgos","revista"]}'),
        ('behavioral-health', 'policy', '{"en":"Policy & Access","es":"Políticas y Acceso"}', 1.30,
         '{"en":["policy","medicaid","insurance","access","healthcare"],"es":["política","cobertura","seguro","acceso","salud mental"]}'),
        ('behavioral-health', 'practice', '{"en":"Practice Management","es":"Gestión de Consultorio"}', 1.10,
         '{"en":["practice","telehealth","reimbursement","burnout","workforce"],"es":["consultorio","telesalud","reembolso","desgaste","personal"]}'),
        ('education', 'policy', '{"en":"Education Policy","es":"Política Educativa"}', 1.40,
         '{"en":["policy","department of education","funding","federal","state"],"es":["política","ministerio","financiamiento","federal","estatal"]}'),
        ('education', 'admissions', '{"en":"Admissions & Enrollment","es":"Admisiones y Matrícula"}', 1.20,
         '{"en":["admissions","enrollment","applicants","tuition","financial aid"],"es":["admisiones","matrícula","solicitantes","colegiatura","becas"]}'),
        ('education', 'research', '{"en":"Research & Outcomes","es":"Investigación y Resultados"}', 1.20,
         '{"en":["research","study","outcomes","graduation","assessment"],"es":["investigación","estudio","resultados","graduación","evaluación"]}'),
        ('education', 'edtech', '{"en":"Learning Technology","es":"Tecnología Educativa"}', 1.10,
         '{"en":["edtech","online learning","lms","ai","classroom"],"es":["tecnología educativa","aprendizaje en línea","plataforma","inteligencia artificial"]}'),
        ('logistics', 'shipping', '{"en":"Ocean & Air Freight","es":"Carga Marítima y Aérea"}', 1.30,
         '{"en":["shipping","freight","vessel","container","air cargo"],"es":["transporte marítimo","flete","buque","contenedor","carga aérea"]}'),
        ('logistics', 'trucking', '{"en":"Trucking & Road","es":"Transporte Terrestre"}', 1.30,
         '{"en":["truck","trucking","driver","carrier","road"],"es":["camión","transportista","conductor","carretera"]}'),
        ('logistics', 'ports', '{"en":"Ports & Terminals","es":"Puertos y Terminales"}', 1.20,
         '{"en":["port","terminal","dock","throughput","congestion"],"es":["puerto","terminal","muelle","congestión"]}'),
        ('logistics', 'customs', '{"en":"Customs & Trade","es":"Aduanas y Comercio"}', 1.40,
         '{"en":["customs","tariff","trade","import","export"],"es":["aduana","arancel","comercio","importación","exportación"]}')
) AS v (industry_slug, slug, label, weight, keywords) ON v.industry_slug = i.slug
ON CONFLICT (industry_id, slug) DO UPDATE SET
    label = EXCLUDED.label,
    weight = EXCLUDED.weight,
    keywords = EXCLUDED.keywords,
    updated_at = now();

INSERT INTO sources (industry_id, name, feed_url, language, trust, enabled, poll_interval_min)
SELECT i.id, v.name, v.feed_url, v.language, v.trust, TRUE, 720
FROM industries i
JOIN (
    VALUES
        ('legal', 'ABA Journal', 'https://www.abajournal.com/rss', 'en', 0.92),
        ('legal', 'Confilegal', 'https://confilegal.com/feed/', 'es', 0.80),
        ('financial', 'Finextra', 'https://www.finextra.com/rss/headlines.aspx', 'en', 0.90),
        ('financial', 'Expansión', 'https://e00-expansion.uecdn.es/rss/portada.xml', 'es', 0.82),
        ('behavioral-health', 'Psychiatric Times', 'https://www.psychiatrictimes.com/rss', 'en', 0.88),
        ('behavioral-health', 'Psicología y Mente', 'https://www.psicologiaymente.com/feed', 'es', 0.78),
        ('education', 'Inside Higher Ed', 'https://www.insidehighered.com/rss.xml', 'en', 0.90),
        ('education', 'Educación 3.0', 'https://www.educaciontrespuntocero.com/feed/', 'es', 0.78),
        ('logistics', 'FreightWaves', 'https://www.freightwaves.com/feed', 'en', 0.88),
        ('logistics', 'Diario del Transporte', 'https://www.diariodetransporte.com/feed/', 'es', 0.76)
) AS v (industry_slug, name, feed_url, language, trust) ON v.industry_slug = i.slug
ON CONFLICT (industry_id, feed_url) DO NOTHING;

INSERT INTO partners (industry_id, name, contact_email, status, regions)
SELECT i.id, v.name, v.contact_email, 'active', '[]'::jsonb
FROM industries i
JOIN (
    VALUES
        ('legal', 'Launch Legal Partner', 'legal-partner@example.com'),
        ('financial', 'Launch Financial Partner', 'financial-partner@example.com'),
        ('behavioral-health', 'Launch Clinical Partner', 'clinical-partner@example.com'),
        ('education', 'Launch Education Partner', 'education-partner@example.com'),
        ('logistics', 'Launch Logistics Partner', 'logistics-partner@example.com')
) AS v (industry_slug, name, contact_email) ON v.industry_slug = i.slug
ON CONFLICT (industry_id) DO NOTHING;
