## Tournament

Tournament is a database-driven Swiss tournament management app.
It's main functionality is to produce next-round pairings and current standings
output, based on the recorded players and match information between them.
Odd player counts (byes), rematch avoidance, and draw handling have been additionally implemented.


## Table of contents

* [Quick start](#getting-started)
* [What's Included](#what's-included)
* [Creators](#creators)


## Getting started

Requirements:

* PostgreSQL version 9.4 or greater.
* Python version 2.7.11

Here's how to get started:

* [Download the latest release](https://github.com/tristanburgess/tournament/archive/master.zip) OR
* Clone the repo: `git clone https://github.com/tristanburgess/tournament.git`
* Navigate to the directory where you have downloaded the repo, and unzip if necessary
* Create the tournmanet database: `psql [-U username] [-p password] -f tournament.sql`
* Run the test suite: `python tournament_test.py`

## What's included

Within the download, you'll find the following files:

```
tournament/
├── tournament.py
├── tournament.sql
├── tournament_test.py
```


## Creators

**Tristan Burgess**

* <https://www.linkedin.com/in/tristanburgess1>
* <https://github.com/tristanburgess>
