Football Sim
Local football career simulation. All data, all Python, all offline.
No APIs, no cloud, just pure code and data.

Made by Aayush Acharya

What’s This?
Football Sim is an offline football career simulator where everything (players, clubs, managers, leagues) lives and runs locally, fully editable. If you think EA FC is mid, this is your playground.

Quickstart
sh
git clone https://github.com/acharya-aayush/Football-Sim-.git
cd Football-Sim-
# Run the Python scripts to validate, generate, or play with data
All data is in JSON under /data/. Edit, break, or remix it however you want.

Project Structure
Path / File	Purpose
data/leagues.json	League list and configs
data/leagues_clubs/	Club lists per league
data/managers/	Manager data, league-specific
data/league_*_clubs_players/	Player data by league/club
standardize_file_naming.py	Script: fixes and standardizes filenames
comprehensive_data_check.py	Script: validates all data for issues
PYTHON_SCRIPTS_ORGANIZATION.md	Python script documentation
Key Scripts
standardize_file_naming.py — Makes all your data filenames sane.
comprehensive_data_check.py — Checks the entire data model for errors.
See PYTHON_SCRIPTS_ORGANIZATION.md for more info on scripts.
Features
Fully local, fully editable football sim world
Realistic player and manager data (with league-accurate stats)
No duplicate IDs, no messy references
Add new leagues/clubs/players whenever you feel like it
Data Model
Leagues: Defined in leagues.json
Clubs: In league folders, referencing managers and players
Managers: League-specific files, modern attribute system, star ratings
Players: Custom attribute pools, nationality logic, unique IDs
Dev/Contributing
Use Python best practices (DRY, KISS, SOLID)
Stick to the file structure and naming conventions
Write clean code and comments
Test your changes if you add logic
Open PRs or issues—idk, just don’t break stuff without fixing it
Status
Data: Complete and validated
Scripts: Core management scripts included
Game engine: In progress
PRs and collabs: Fork and PR, or DM if you're bold
About
A project by Aayush Acharya

GitHub
Instagram
LinkedIn
