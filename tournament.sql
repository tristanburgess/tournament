-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

\c tournament;

CREATE TABLE players (
    id serial PRIMARY KEY,
    name text NOT NULL,
    had_bye boolean
);

CREATE TABLE matches (
    id serial PRIMARY KEY,
    winner_id integer REFERENCES players(id),
    loser_id integer REFERENCES players(id),
	  draw boolean
);

CREATE VIEW standings AS
    SELECT p.id, p.name,
    SUM(CASE WHEN m.draw = true THEN 0.5
	         WHEN m.winner_id = p.id THEN 1
		ELSE 0
		END) AS wins,
    COUNT(m.id) AS matches
    FROM players p
    LEFT JOIN matches m ON p.id = m.winner_id OR p.id = m.loser_id
    GROUP BY p.id
    ORDER BY wins DESC;
