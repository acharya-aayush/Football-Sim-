# Project Docs: Aayush's Football Sim ⚽

**Author:** Aayush Acharya (CSIT Student)
    *   GitHub: [github.com/acharya-aayush](https://github.com/acharya-aayush)
    *   Insta: [instagram.com/aayushacharya_gz](https://instagram.com/aayushacharya_gz)
    *   LinkedIn: [linkedin.com/in/acharyaaayush](https://linkedin.com/in/acharyaaayush)
**Project:** Football Career Sim (Side Hustle)
**Inspo:** Football Superstar 2 (Lazy Games Development)
**Last Updated:** May 26, 2025
**Status:** 🎉 **DATA FOUNDATION COMPLETE!** 🎉

## 1. So, What's This All About?

This whole thing is me building a single-player, web-based football career sim with a **rock-solid data foundation**. The main goal? Make a career mode that's actually engaging long-term. You know, where you can develop your player, deal with club drama, and just live the football life. Messi is the Goat, and this game should at least try to be worthy of his digital presence.

**MAJOR MILESTONE:** As of May 26, 2025, the entire data infrastructure is complete with 100% integrity verification! We're talking 10 leagues, 201 clubs, 5,377 players, and 197 managers – all cross-referenced, validated, and ready for game development.

## 1.5. Data Storage & Creation Strategy ✅ IMPLEMENTED

### SQLite Database for Players (Planned)

Initially, I was yeeting all player data into JSON files. Seemed easy, right? Wrong. Once you start thinking about tens of thousands of players, a single massive JSON or even per-club JSONs become a hot mess for performance.

So, big brain move (thanks to some solid DBMS teachings from **Sandeep sir** – cheers, legend!): **we're planning SQLite migration for player data.**

*   **Current:** JSON with comprehensive validation system
*   **Future:** SQLite for performance, querying power, and scalability
*   **Why the delay?** The JSON system with proper validation works perfectly for development phase
*   **Migration Plan:** Once core game mechanics are built, migrate to SQLite for production

### Player Creation Strategy - The Enhanced Hybrid Approach ✅ COMPLETE

After extensive development, I've successfully implemented a comprehensive hybrid approach:

*   **Manual Creation for Top Clubs:** Hand-crafted detailed player profiles for major clubs
*   **Sophisticated Generation System:** AI-powered player generation for all remaining clubs with:
    *   Club reputation-based quality scaling
    *   Position-appropriate attribute distributions
    *   Realistic age and contract structures
    *   **League-specific nationality distributions:**
        *   **EPL:** 60% English, diverse international mix
        *   **La Liga:** 60% Spanish, strong South American presence
        *   **Serie A:** 55% Italian, Brazilian and Argentine representation
        *   **Bundesliga:** 60% German, Central European focus
        *   **Ligue 1:** 60% French, significant African representation
        *   **Second Divisions:** Higher domestic percentages (80-85%)

The `club_player_generations.py` script handles the creation of these generated players with realistic attributes, while `regenerate_players.py` can be used to refresh player data across multiple leagues while maintaining the appropriate nationality distributions.

## 1.7. New Leagues Integration (May 2025)

### Overview
In May 2025, the data system was expanded to include three additional European leagues:
- **Turkish Süper Lig** (19 teams)
- **Belgian Pro League** (16 teams)
- **Swiss Super League** (12 teams)

**Key integration details:**
- All clubs have authentic names, stadiums, and city/country data
- Player generation uses realistic Turkish, Belgian, and Swiss name pools
- Nationality distributions reflect real-world league patterns
- Each club has a full 29-player squad and a manager with appropriate tactical profile
- League structures, relegation, and reputation match the 2024-25 season
- All data verified with enhanced scripts for consistency and realism

**Stats:**
- 47 new clubs
- 1,363 new players
- 47 new managers

**You can now simulate, manage, and transfer players in these new leagues alongside the original 10 major European leagues!**

## 1.8. Next Wave: European League Expansion (Planned, May 2025)

To make Champions League, Europa League, and Conference League simulations truly realistic, the next step is to add more top divisions from key UEFA countries. The following leagues are now planned for the next expansion phase:

- **Russian Premier League**
- **Ukrainian Premier League**
- **Scottish Premiership**
- **Austrian Bundesliga**
- **Greek Super League**

These will bring the system much closer to full coverage of real-life European competitions. Each league will include:
- Authentic club and stadium data
- Realistic player and manager generation (with local name pools)
- League structure and relegation rules

**Status:**
- Data research and club list gathering in progress
- JSON structure and player/manager generation scripts will be adapted for these leagues
- Documentation and verification scripts will be updated as each league is integrated

---

## 2. Features I'm Thinking About (And Kinda Building)

## 2. The Vision: What's This Game Gonna Be? 🎮

**Current Status: Data Foundation Complete ✅**

The data infrastructure is now 100% ready! Here's what we've accomplished and what's coming next:

### ✅ **Completed Features:**

*   **Complete League System:** 10 European leagues fully populated and validated
*   **Comprehensive Player Database:** 5,377 players with full attribute sets and contracts
*   **Manager System:** 197 managers with tactical preferences and career histories  
*   **Data Integrity:** Bulletproof validation system ensuring 0% data corruption
*   **Realistic Demographics:** League-specific nationality distributions implemented
*   **Goalkeeper Specialization:** All 128+ goalkeepers have specialized attributes
*   **Unique Identity System:** Every player has a unique ID with descriptive naming
*   **European Competition Support:** With the next wave of league additions, the system will soon support realistic Champions League, Europa League, and Conference League simulations.

### 🔄 **Next Phase: Game Engine Development**

*   **Player Progression:** Dynamic attribute growth based on performance and training
*   **Club & League World:** Financial systems, stadium atmosphere, rivalries
*   **Career Mode:** Interactive choices affecting player development and career path
*   **Match Simulation:** Text-based initially, with plans for visual enhancements
*   **Transfer System:** AI-driven market with realistic valuations and negotiations

### 🎯 **Core Game Features (Planned):**

*   **Player Development:**
    *   Attributes: Technical, mental, physical, GK specializations (0-100 scale)
    *   Growth: Age-based progression with potential caps
    *   Contracts: Wages, release clauses, performance bonuses
    *   Personality: Traits affecting development and team chemistry
    *   Injuries: Realistic injury system with recovery periods
    *   International: National team selection and competitions

*   **Club & League Dynamics:**
    *   Promotion/Relegation: Teams moving between divisions
    *   Finances: Transfer budgets, wage caps, financial fair play
    *   AI Management: Intelligent computer-controlled managers
    *   Competition: Realistic league tables and cup competitions

*   **Career Immersion:**
    *   Player Creation: Customizable starting attributes and background
    *   Interactions: Agent meetings, manager relationships, media
    *   Training: Specialized sessions to improve specific attributes
    *   Life Events: Choices that impact career trajectory
    *   Achievements: Trophies, records, and milestone recognition

## 3. Data Architecture: The Solid Foundation 🏗️

**Status: 100% Complete and Validated**

### 3.1. `leagues.json` ✅
*   **Purpose:** Complete league definitions for all 10 European competitions
*   **Contents:** League hierarchy, reputation systems, promotion/relegation rules
*   **Coverage:** EPL, La Liga, Serie A, Bundesliga, Ligue 1 + their second divisions
*   **Validation:** All cross-references verified, no orphaned data

### 3.2. Club Files ✅ 
*   **Location:** `data/leagues_clubs/` directory
*   **Files:** Separate JSON files for each league (e.g., `epl_clubs.json`, `laliga_clubs.json`)
*   **Contents:** Complete club profiles including stadiums, finances, history, rivalries
*   **Coverage:** 201 clubs across all 10 leagues
*   **Validation:** All club IDs properly formatted and cross-referenced

### 3.3. Player Database ✅
*   **Location:** `data/league_*_clubs_players/` directories
*   **Format:** JSON files organized by league and club
*   **Coverage:** 5,377 players across 197 clubs
*   **Quality Assurance:** 
    * All duplicate IDs resolved with unique naming conventions
    * Club references standardized across all files
    * Goalkeeper attributes added to all 128+ keepers
    * League-specific nationality distributions maintained
*   **Future Migration:** Planning SQLite transition for enhanced performance
*   **Current state:** Moving away from API-fetched data to a hybrid manual/generation approach. SQLite integration in progress.

### 3.4. `traits.json`
*   **What it is:** Defines various player traits that can affect gameplay.
*   **Key bits:** `name`, `description`, `associated_positions`, `key_attributes` (attributes that contribute to acquiring the trait), `bonus_effects` (descriptive impact of the trait).
*   **Current state:** Initial set of 15 traits defined.

### 3.5. `managers.json`
*   **What it is:** Contains data for football managers.
*   **Key bits:** `manager_id`, `name`, `nationality_code`, `current_club_id`, `preferred_formation`, `playing_style_primary`, `playing_style_secondary`, `attributes` (coaching stats like tactical knowledge, player development, etc.).
*   **Current state:** Populated with managers from EPL, derived from `epl_clubs.json`.

### 3.6. `playing_styles.json`
*   **What it is:** Defines different tactical playing styles that managers can adopt.
*   **Key bits:** `id`, `name`, `description`, `bonus_effects` (structured list of attribute modifications), `countered_by` (list of style IDs that counter this style).
*   **Current state:** Eight core playing styles defined with structured bonus effects for game engine integration.

### 3.7. `update_players.py`
*   **What it is:** Python script to help with player data. Used for bulk updates, calculations, and generating fictional players. Will be updated to work with the SQLite database.

### 3.8. `update_current_ability.py`
*   **What it is:** Python script responsible for calculating `current_ability` for players based on their attributes and position. It also handles the normalization of all player attributes and potential ability to a 0-100 scale.

### 3.9. `starting_XI_Selection.py`
*   **What it is:** Python script that selects the optimal starting XI for a given club and formation.
*   **Key Logic:**
    *   Loads player data for the specified club.
    *   Calculates `position_effectiveness` for each player in every position of the formation, considering their primary, secondary, and other viable positions. An adaptability factor is used to determine how well a player fits a non-primary role.
    *   Performs an initial greedy selection of the starting XI by picking the player with the highest `effective_ability` (current ability * positional effectiveness factor) for each required position, ensuring no player is selected twice.
    *   Implements a refinement phase: Iteratively checks if swapping the positions of two already selected players can lead to a higher combined `effective_ability` for those two specific slots. This process continues until no more beneficial 2-player swaps can be found.
    *   Displays the selected starting XI in a traditional formation order (Goalkeeper, Defenders, Midfielders, Attackers), along with each player's name, chosen position, and their `current_ability`.

### 3.10 Player Generation Framework (Upcoming)
*   **What it is:** A comprehensive system for generating fictional players with realistic attributes
*   **Key Components:**
    * **Position-Based Templates:** Base attribute distributions for each position (e.g., strikers have higher shooting, defenders have better tackling)
    * **Club-Aware Generation:** Players generated for top clubs will have higher average attributes than those for lower-tier clubs
    * **Age Distribution:** Realistic age curves with appropriate attribute progression/decline
    * **Nationality Logic:** Weighted probabilities based on club's country and scouting regions
    * **Name Generation:** Region-appropriate name generation for authenticity
    * **Trait Assignment:** Logical assignment of traits based on player's attributes and position
    * **Potential Calculation:** Younger players receive appropriate potential ratings based on club reputation
*   **Key Functions:**
    *   Calculates `current_ability` using position-specific attribute weights.
    *   Normalizes `current_ability` to a 0-100 scale.
    *   Provides functionality (via `--scale` argument) to convert all player attributes (technical, mental, physical, goalkeeping, hidden attributes like injury proneness, consistency) and `potential_ability_range` from their original scales (e.g., 0-20, 100-200) to a unified 0-100 scale.
    *   Includes data integrity checks to prevent attributes from exceeding the 0-100 scale after multiple runs and to correct invalid potential ability ranges.

## 4. Tech Stack (What I'm Using)

*   **Data:** JSON.
*   **Backend/Tools:** Python (for data, scripts, maybe a simple server later).
*   **Frontend (The Dream):** HTML, CSS, JavaScript. Maybe Vue.js or React if I learn how to use them properly without crying.

## 5. Where We At & What's Next

*   **Done (ish):**
    *   Leagues defined.
    *   Club data structure and population for big leagues completed.
    *   Player data structure finalized with 0-100 attribute scale standardization.
    *   Manually created player data for top clubs (Barcelona, Real Madrid, Man City, etc.).
    *   Created `traits.json` with comprehensive player traits.
    *   Created `managers.json` with EPL managers.
    *   Created and refined `playing_styles.json` with core tactical styles.
    *   Created `gameplay.md` outlining core game mechanics and features.
    *   Implemented Starting XI selection logic in `starting_XI_Selection.py`.
    *   Decided on hybrid approach for player data (manual for top clubs, generated for others).
    *   Implemented league-specific nationality distributions for generated players.
    *   Created `club_player_generations.py` for generating realistic fictional players.
    *   Developed `regenerate_players.py` for refreshing player data across multiple leagues.
    *   Removed API-fetched data after hitting API limitations.
*   **Up Next (The Grind):**
    *   **Player Enhancement:** Continue refining the player generation algorithms for more realism.
    *   **SQLite Migration:** Set up the SQLite database structure and migration scripts for player data.
    *   **Data Check:** Make sure all the IDs line up. `club_id` in players matches a club, `key_player_ids` in clubs match players. You get it.
    *   **Manager Expansion:** Populate `managers.json` with managers from other leagues.
    *   **Trait Integration:** Plan how traits will be assigned and affect players/simulation.
    *   **Playing Style Logic:** Develop game engine logic to utilize `playing_styles.json`.
    *   **Script Improvements:** Enhance helper scripts for SQLite and player data management.
    *   **Planned Expansion:** Next up: Russian, Ukrainian, Scottish, Austrian, and Greek top divisions for full European competition realism (see section 1.8).
*   **Future Sometime (Medium Term):**
    *   Basic sim engine (match results, league tables).
    *   Start the web UI.
    *   Core career stuff (training, job offers).

## 6. Headaches & Thoughts

*   **Data Strategy:** Decided on the hybrid approach - manually create players for top clubs, generate for the rest. Took a while to land on this after API limitations killed that plan, but tbh this gives more control.
*   **Nationality Distributions:** Implemented realistic nationality distributions for each league, making generated squads more authentic. EPL has mostly English players with a diverse mix of international talent; La Liga is predominantly Spanish with South American influence; Serie A focuses on Italian players with Brazilian and Argentine representation; Bundesliga is German-heavy with neighboring countries well represented; and Ligue 1 features mostly French players with significant African presence.
*   **Player Regeneration:** Created a system to refresh player data across leagues while maintaining proper nationality distributions, useful for implementing transfer windows or starting new seasons.
*   **SQLite Migration:** JSON worked for initial exploration, but with thousands of players, SQLite is the move. Migration in progress.
*   **Attribute Balance:** Making sure player attributes make sense across the 0-100 scale, especially when comparing manually created vs. generated players.
*   **Sim Logic:** Making the sim realistic but also fun. Tricky balance.
*   **UI/UX:** Making it not look like it was designed in 1998.
*   **Player Generation:** The algorithm for generating realistic fictional players with position-appropriate attributes and traits is working well, but still needs refinement for youth players and potential ability calculation.

## Simulation Realism Update (2025-05-27)

### Motivation
Recent testing revealed that simulated seasons produced too many clean sheets for goalkeepers and top player ratings were unrealistically clustered (e.g., 7.9, 7.89, 7.87, etc.). Real-world league data shows that top GKs typically have 7–15 clean sheets per season, and top player ratings are more spread out.

### What Was Changed
- **Goal Frequency:**
  - Increased the minimum Poisson lambda for team goals from 0.5 to 1.1. This raises the average number of goals per match, making 0-0 and 1-0 results less common and reducing the number of clean sheets.
- **Player Rating Spread:**
  - Lowered the maximum possible match rating from 8.0 to 7.8.
  - Increased the negative randomness in the match rating formula, so top player averages are less tightly clustered and more realistic.
  - Slightly reduced the star performance bonus, making 7.8+ averages even rarer.

### Effect
- **Goalkeeper Stats:**
  - Clean sheets for top GKs now fall in the 7–15 range, matching real-world Bundesliga, LaLiga, and EPL stats.
- **Player Ratings:**
  - Top player season averages are now more spread out, with only exceptional players approaching the 7.8 cap.
  - The distribution of ratings is more natural, with more variance and fewer ties at the top.

### Technical Details
- In the match simulation, the Poisson mean (`lambda`) for each team's goals is now clamped to a minimum of 1.1 instead of 0.5.
- The player match rating formula now includes a larger negative random factor and a lower cap.
- The star performance bonus (for 2+ goals/assists) was reduced from 0.2 to 0.12.

### Why This Matters
These changes make the simulation output much closer to real football league stats, improving both realism and enjoyment for users analyzing season results.

## Manager Data System (2025 Update)

- All manager attributes are on a 0–100 scale.
- `manager_ability` is a weighted average of the main attributes, with a minimum for star_manager_trait 4 (≥80) and 5 (≥90).
- `star_manager_trait` (1–5) is a major variable for manager reputation/impact.
- Trophy fields: `league_titles`, `ucl_titles`, `uel_titles`, `domestic_cup_titles` (all integers, counts only).
- `age` field for realism and career simulation.
- The script `convert_manager_scale.py` is idempotent and safe to run multiple times.

This doc is mostly for me to keep track of things. If you're reading this, cool. Hope it makes some sense. IDK, ask if it doesn't, idc.

-- Aayush
