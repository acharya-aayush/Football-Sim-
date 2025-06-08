Football Sim
Local football career simulation. All Python, all offline, all data-driven.
No APIs, no cloud, just pure code and JSON.
Made by Aayush Acharya

What is This?
Football Sim is an offline football career simulator. All data (players, clubs, managers, leagues) is stored locally, fully editable, and managed by Python scripts.

Quickstart
sh
git clone https://github.com/acharya-aayush/Football-Sim-.git
cd Football-Sim-
# Run the Python scripts to validate, generate, or manage data
All core data is in JSON inside /data/.

Project Structure
Path / File	Description
data/leagues.json	League definitions and configuration
data/leagues_clubs/	Club lists per league
data/managers/	Manager data, league-specific
data/league_*_clubs_players/	Player data per league/club
standardize_file_naming.py	Script for fixing and standardizing filenames
comprehensive_data_check.py	Script to validate all data for consistency
PYTHON_SCRIPTS_ORGANIZATION.md	Python script documentation
Key Scripts
standardize_file_naming.py
Cleans up and standardizes all data filenames.

comprehensive_data_check.py
Runs validation on the entire data model.

PYTHON_SCRIPTS_ORGANIZATION.md
Docs and breakdown for all scripts.

Features
Fully local, editable football sim world (no third-party APIs)
Realistic player and manager data (league-accurate stats)
No duplicate IDs or messy refs
Easy to add new leagues, clubs, players
Data Model
Leagues: Defined in leagues.json
Clubs: Grouped by league, each club references players and manager
Managers: League-specific files, modern attributes, star ratings
Players: Custom attribute pools, nationality logic, unique IDs
Contributing
Use Python best practices (DRY, KISS, SOLID)
Stick to the file structure and naming conventions
Write clean code and comments
Test your changes if you add logic
Open PRs or issues—don’t break stuff without fixing it
Status
Data: Complete and validated
Scripts: Core management scripts included
Game engine: In progress
PRs and collabs: Fork and PR, or DM if you’re bold
About
A project by Aayush Acharya
GitHub: acharya-aayush
Insta: @aayushacharya_gz
LinkedIn: acharyaaayush

License
MIT

TL;DR:
Clone it, mess with football sim data, build your own thing, don’t ask for permission.
