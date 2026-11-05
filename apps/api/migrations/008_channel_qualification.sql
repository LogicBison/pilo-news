-- 008_channel_qualification.sql
-- Adds R4 of the lead-magnet plan: one qualification question per channel.
-- Idempotent: the column is added with IF NOT EXISTS, and each channel's
-- `cta.qualify` block is only written when it is missing (operator edits win).

ALTER TABLE leads ADD COLUMN IF NOT EXISTS qualification TEXT;

UPDATE industries
SET cta = cta || jsonb_build_object('qualify', $q${
  "label": {"en": "Matter type", "es": "Tipo de asunto"},
  "required": true,
  "options": [
    {"value": "corporate", "label": {"en": "Corporate & governance", "es": "Corporativo y gobierno"}},
    {"value": "litigation", "label": {"en": "Litigation & disputes", "es": "Litigios y disputas"}},
    {"value": "employment", "label": {"en": "Employment", "es": "Laboral"}},
    {"value": "immigration", "label": {"en": "Immigration", "es": "Migración"}},
    {"value": "other", "label": {"en": "Something else", "es": "Otro asunto"}}
  ]
}$q$::jsonb)
WHERE slug = 'legal' AND NOT (cta ? 'qualify');

UPDATE industries
SET cta = cta || jsonb_build_object('qualify', $q${
  "label": {"en": "What do you need help with?", "es": "¿Con qué necesita ayuda?"},
  "required": true,
  "options": [
    {"value": "planning", "label": {"en": "Financial planning", "es": "Planificación financiera"}},
    {"value": "retirement", "label": {"en": "Retirement", "es": "Jubilación"}},
    {"value": "tax", "label": {"en": "Tax", "es": "Impuestos"}},
    {"value": "investments", "label": {"en": "Investments", "es": "Inversiones"}},
    {"value": "other", "label": {"en": "Something else", "es": "Otro tema"}}
  ]
}$q$::jsonb)
WHERE slug = 'financial' AND NOT (cta ? 'qualify');

UPDATE industries
SET cta = cta || jsonb_build_object('qualify', $q${
  "label": {"en": "What kind of support?", "es": "¿Qué tipo de apoyo?"},
  "required": true,
  "options": [
    {"value": "therapy", "label": {"en": "Individual therapy", "es": "Terapia individual"}},
    {"value": "family", "label": {"en": "Family or couples", "es": "Familia o pareja"}},
    {"value": "substance-use", "label": {"en": "Substance use", "es": "Consumo de sustancias"}},
    {"value": "referral", "label": {"en": "A referral", "es": "Una derivación"}},
    {"value": "other", "label": {"en": "Something else", "es": "Otra opción"}}
  ]
}$q$::jsonb)
WHERE slug = 'behavioral-health' AND NOT (cta ? 'qualify');

UPDATE industries
SET cta = cta || jsonb_build_object('qualify', $q${
  "label": {"en": "Program interest", "es": "Programa de interés"},
  "required": true,
  "options": [
    {"value": "certificate", "label": {"en": "Certificate", "es": "Certificado"}},
    {"value": "degree", "label": {"en": "Degree", "es": "Título"}},
    {"value": "licensing", "label": {"en": "Licensing or exam prep", "es": "Licencia o examen"}},
    {"value": "corporate", "label": {"en": "Corporate training", "es": "Formación corporativa"}},
    {"value": "other", "label": {"en": "Something else", "es": "Otra opción"}}
  ]
}$q$::jsonb)
WHERE slug = 'education' AND NOT (cta ? 'qualify');

UPDATE industries
SET cta = cta || jsonb_build_object('qualify', $q${
  "label": {"en": "What do you need moved?", "es": "¿Qué necesita mover?"},
  "required": true,
  "options": [
    {"value": "freight", "label": {"en": "Freight", "es": "Carga"}},
    {"value": "warehousing", "label": {"en": "Warehousing", "es": "Almacenaje"}},
    {"value": "last-mile", "label": {"en": "Last mile", "es": "Última milla"}},
    {"value": "customs", "label": {"en": "Customs", "es": "Aduanas"}},
    {"value": "other", "label": {"en": "Something else", "es": "Otra opción"}}
  ]
}$q$::jsonb)
WHERE slug = 'logistics' AND NOT (cta ? 'qualify');

UPDATE industries
SET cta = cta || jsonb_build_object('qualify', $q${
  "label": {"en": "What do you need?", "es": "¿Qué necesita?"},
  "required": true,
  "options": [
    {"value": "assessment", "label": {"en": "Security assessment", "es": "Evaluación de seguridad"}},
    {"value": "incident", "label": {"en": "Incident response", "es": "Respuesta a incidentes"}},
    {"value": "compliance", "label": {"en": "Compliance", "es": "Cumplimiento"}},
    {"value": "training", "label": {"en": "Team training", "es": "Formación del equipo"}},
    {"value": "other", "label": {"en": "Something else", "es": "Otra opción"}}
  ]
}$q$::jsonb)
WHERE slug = 'cybersecurity' AND NOT (cta ? 'qualify');

UPDATE industries
SET cta = cta || jsonb_build_object('qualify', $q${
  "label": {"en": "What are you looking for?", "es": "¿Qué está buscando?"},
  "required": true,
  "options": [
    {"value": "treatment", "label": {"en": "Treatment information", "es": "Información sobre tratamiento"}},
    {"value": "trial", "label": {"en": "Clinical trials", "es": "Ensayos clínicos"}},
    {"value": "storage", "label": {"en": "Cord blood storage", "es": "Conservación de cordón"}},
    {"value": "regulatory", "label": {"en": "Regulatory questions", "es": "Consultas regulatorias"}},
    {"value": "other", "label": {"en": "Something else", "es": "Otra opción"}}
  ]
}$q$::jsonb)
WHERE slug = 'stem-cell' AND NOT (cta ? 'qualify');
