-- Active: 1709566645830@@baza.fmf.uni-lj.si@5432@sem2024_majc@public

-- na začetku

-- dovolimo povezavo in uporabo scheme public javnosti
GRANT CONNECT ON DATABASE sem2024_gasperdr TO javnost;
GRANT USAGE ON SCHEMA public TO javnost;

-- po ustvarjanju tabel
GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;

-- dodatne pravice za uporabo aplikacije
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO javnost;