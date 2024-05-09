-- Active: 1709566645830@@baza.fmf.uni-lj.si@5432@sem2024_majc@public
CREATE TABLE Plovilo (
    registracija SERIAL PRIMARY KEY,
    ime TEXT not null UNIQUE,
    letnik INT,
    kapaciteta INT,
    tip TEXT not null,
    dolzina DECIMAL,
    charter TEXT not null,
    cena INT
);

###############################################################

create table gost (
    emso text PRIMARY KEY,
    ime text not null
);

###############################################################
create table rezervacija (
    id SERIAL PRIMARY KEY,
    zacetek DATE not null,
    konec DATE not null,
    gost text REFERENCES gost(emso) not null,
    plovilo INTEGER REFERENCES plovilo(registracija) not null
);

###############################################################
create table charter (
    ime text PRIMARY key
);

insert into charter(ime) values ('Angelina Yacht Charter');
insert into charter(ime) values ('Euronautic');
insert into charter(ime) values ('Dream Yacht Charter');
insert into charter(ime) values ('Pitter Yachtcharter');

###############################################################

create table zaposleni (
    emso text PRIMARY KEY,
    ime text not null,
    opis text not null,
    charter text references charter(ime) not null
);

###############################################################

create table crewlist (
    id serial PRIMARY KEY,
    oseba text REFERENCES gost(emso) not null,
    vloga text not null
);