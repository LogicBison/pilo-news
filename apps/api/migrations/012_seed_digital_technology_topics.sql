-- 012_seed_digital_technology_topics.sql
-- The three topics behind the digital-technology demand test (M10), seeded so
-- every environment and the test database agree without running a CLI import.
-- The deployment profile stays the source of truth; this is the safety net.
-- Idempotent: the unique (industry_id, slug) constraint makes the insert a no-op.

INSERT INTO topics (industry_id, slug, label, weight, keywords)
SELECT i.id, t.slug, t.label::jsonb, t.weight::numeric, t.keywords::jsonb
FROM industries i
JOIN (
    VALUES
        (
            'ai-infrastructure',
            '{"en": "AI Infrastructure", "es": "Infraestructura de IA"}',
            1.30,
            '{"en": ["gpu", "accelerator", "inference", "training cluster", "tpu", "datacenter", "data center", "hyperscaler"], "es": ["gpu", "acelerador", "inferencia", "centro de datos", "clúster", "hiperescalar"]}'
        ),
        (
            'chips-supply',
            '{"en": "Chips & Supply", "es": "Chips y Suministro"}',
            1.25,
            '{"en": ["semiconductor", "foundry", "wafer", "lithography", "export control", "chipmaker"], "es": ["semiconductor", "fundición", "oblea", "litografía", "control de exportaciones", "fabricante de chips"]}'
        ),
        (
            'ai-rules',
            '{"en": "AI Rules", "es": "Normas de IA"}',
            1.20,
            '{"en": ["ai act", "ai regulation", "algorithmic", "model transparency", "ai governance", "ai liability"], "es": ["reglamento de ia", "regulación de ia", "algorítmic", "transparencia de modelos", "gobernanza de ia"]}'
        )
) AS t(slug, label, weight, keywords) ON TRUE
WHERE i.slug = 'cybersecurity'
ON CONFLICT (industry_id, slug) DO NOTHING;
