-- 009_distinct_channel_palettes.sql
-- Gives every channel its own colour scheme (one dark), so no two channels
-- share a temperature or hue family. Values pass all five contrast gates.

UPDATE industries SET theme = $t${"primary":"#5b2333","accent":"#a16207","bg":"#faf7f2","surface":"#f3ede4","text":"#1c1917","muted":"#57534e","border":"#e7ded1","radius":"6px","font_heading":"Georgia, Times New Roman, serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"editorial"}$t$::jsonb WHERE slug = 'legal';

UPDATE industries SET theme = $t${"primary":"#0f2f4f","accent":"#0e7490","bg":"#f7f9fb","surface":"#eef2f6","text":"#0b1220","muted":"#4b5563","border":"#dbe3ea","radius":"4px","font_heading":"Arial, Helvetica, sans-serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"professional"}$t$::jsonb WHERE slug = 'financial';

UPDATE industries SET theme = $t${"primary":"#7c3f58","accent":"#b45309","bg":"#fdf7f5","surface":"#f9ece7","text":"#2b1d1b","muted":"#6b5250","border":"#eddcd6","radius":"22px","font_heading":"Georgia, Times New Roman, serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"editorial"}$t$::jsonb WHERE slug = 'behavioral-health';

UPDATE industries SET theme = $t${"primary":"#14532d","accent":"#b45309","bg":"#fbf8ef","surface":"#f4edda","text":"#1f2a1d","muted":"#4f5a4a","border":"#e3dcc6","radius":"10px","font_heading":"Georgia, Times New Roman, serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"academic"}$t$::jsonb WHERE slug = 'education';

UPDATE industries SET theme = $t${"primary":"#1f3d33","accent":"#c2410c","bg":"#f4f6f5","surface":"#e9efec","text":"#0f1a16","muted":"#4a5a53","border":"#d7e0da","radius":"8px","font_heading":"Arial, Helvetica, sans-serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"professional"}$t$::jsonb WHERE slug = 'logistics';

UPDATE industries SET theme = $t${"primary":"#1e3a5f","accent":"#22d3ee","bg":"#0b1220","surface":"#131c2e","text":"#e5edf7","muted":"#a3b1c6","border":"#243046","radius":"2px","font_heading":"Arial, Helvetica, sans-serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"professional"}$t$::jsonb WHERE slug = 'cybersecurity';

UPDATE industries SET theme = $t${"primary":"#0f4c5c","accent":"#9a3412","bg":"#ffffff","surface":"#f2f7f7","text":"#0f172a","muted":"#4b5563","border":"#d9e6e6","radius":"14px","font_heading":"Georgia, Times New Roman, serif","font_body":"system-ui, -apple-system, Segoe UI, sans-serif","layout":"academic"}$t$::jsonb WHERE slug = 'stem-cell';
