#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
# author        -- Tristan Burgess
#

import psycopg2
from random import choice
from itertools import combinations


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    con = connect()
    cur = con.cursor()
    cur.execute("DELETE FROM matches;")
    con.commit()
    con.close()


def deletePlayers():
    """Remove all the player records from the database."""
    con = connect()
    cur = con.cursor()
    cur.execute("DELETE FROM players;")
    con.commit()
    con.close()


def countPlayers():
    """Returns the number of players currently registered."""
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM players;")
    player_count = cur.fetchone()[0]
    con.close()
    return player_count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    con = connect()
    cur = con.cursor()
    cur.execute("INSERT INTO players (name, had_bye) VALUES (%s, %s);",
                (name, False,))
    con.commit()
    con.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    standings = []
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT * FROM standings;")
    for row in cur:
	    standings.append((row[0], row[1], row[2], row[3]))
    con.close()
    return standings


def reportMatch(winner, loser, draw=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      draw:   a boolean flag which indicates a draw did or did not occur
    """
    con = connect()
    cur = con.cursor()

    cur.execute("""INSERT INTO matches (winner_id, loser_id, draw)
                   VALUES (%s, %s, %s);""", (winner, loser, draw,))
    con.commit()
    con.close()


def hadMatch(player1_id, player2_id):
    """Given two player ids, checks to see if a match has already occured
       between the two players. Returns true if they have, false otherwise.

    Args:
      player1_id: the id number of the first player to be checked
      player2_id: the id number of the potential opponent of player1
    """
    con = connect()
    cur = con.cursor()

    cur.execute("""SELECT COUNT(*)
                   FROM matches
                   WHERE (winner_id = %s AND loser_id = %s) OR
                         (winner_id = %s AND loser_id = %s);""",
                (player1_id, player2_id, player2_id, player1_id,))

    res = cur.fetchone()[0]
    con.close()
    return res != 0


def assignNewBye():
    """Assigns a bye round for a player that has not yet received one.
       The candidates are weighted by the lowest number of wins.
       The selected candidate will get a reported match where they are both
       the winner, and the loser.
    """
    con = connect()
    cur = con.cursor()
    cur.execute("""SELECT p.id, p.name
                   FROM players p
                   JOIN standings s ON p.id = s.id
                   WHERE s.wins = (SELECT MIN(s.wins)
                                   FROM players p
                                   JOIN standings s ON p.id = s.id
                                   WHERE p.had_bye = false);""")

    bye_candidates = [item[0] for item in cur.fetchall()]
    bye_electee = random.choice(bye_candidates)
    reportMatch(bye_electee, bye_electee)
    cur.execute("UPDATE players SET had_bye = true WHERE id = %s",
                (bye_electee,))
    con.commit()
    con.close()

    return bye_electee


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings. Re-matches between players are avoided.

    For an odd number of players, one player receives a bye for the round,
    and the rest of the players are paired up according to the rules for even
    players above.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()

    # Assign a bye electee and remove him from the pairing candidates
    if countPlayers() % 2 == 1:
        bye_electee = assignNewBye()
        standings = [(i, j, k, l)
                     for i, j, k, l in standings
                     if i != bye_electee]

    done = False
    # List of all possible match combinations
    match_combinations = list(combinations(range(len(standings)), 2))
    while not done and match_combinations:
        done = True
        pairings = []
        pair_candidates = []
        players_considered = []

        for x in match_combinations:
            player1_id = standings[x[0]][0]
            player1_name = standings[x[0]][1]
            player2_id = standings[x[1]][0]
            player2_name = standings[x[1]][1]

            if (player1_id not in players_considered and
               player2_id not in players_considered):
                # If a rematch has been found while exploring the pair space,
                # pair candidates that led up to and include the rematch pair
                # are removed from the pair space, and we try again.
                if hadMatch(player1_id, player2_id):
                    done = False
                    match_combinations.remove(x)
                    for y in pair_candidates:
                        if y in match_combinations:
                            match_combinations.remove(y)
                    break
                else:
                    pair_candidates.append(x)
                    players_considered.append(player1_id)
                    players_considered.append(player2_id)
                    pairings.append((player1_id, player1_name,
                                     player2_id, player2_name))

    return pairings
