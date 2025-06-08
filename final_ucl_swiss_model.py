import os
import json
import random
import math
from datetime import datetime
from collections import defaultdict, Counter
import copy # Added for deep copying team data if necessary
import logging # Added to resolve NameError

# --- Logging Configuration ---
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

# --- Constants ---
BASE_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
LEAGUES_FILE = os.path.join(BASE_DATA_PATH, 'leagues.json')
CLUBS_DIR = os.path.join(BASE_DATA_PATH, 'leagues_clubs')
MANAGERS_FILE = os.path.join(BASE_DATA_PATH, 'managers.json') # Assuming a single file for managers
PLAYING_STYLES_FILE = os.path.join(BASE_DATA_PATH, 'playing_styles.json')
TRAITS_FILE = os.path.join(BASE_DATA_PATH, 'traits.json')
PLAYERS_FILE = os.path.join(BASE_DATA_PATH, 'players.json') # Assuming a single file for players
TEAM_PLAYER_LINKS_FILE = os.path.join(BASE_DATA_PATH, 'team_player_links.json') # Assuming this file exists

DEFAULT_FORMATION = "4-3-3"
PLAYER_POSITIONS = {
    "GK": ["GK"],
    "DEF": ["CB", "LB", "RB", "LWB", "RWB"],
    "MID": ["DM", "CM", "LM", "RM", "AM"],
    "FWD": ["LW", "RW", "ST", "CF"]
}
PLAYER_SKILL_STD_DEV = 7 # From typical player generation
BASE_RATING = 6.0
RATING_STD_DEV = 0.5
FORM_INFLUENCE = 0.2
MIN_PLAYERS_FOR_FULL_TEAM = 18 # For team setup checks

# Helper function to load JSON data
def load_json_data(file_path, schema_type="dict"): # Added schema_type for flexibility
    print(f"DEBUG: Attempting to load JSON from: {file_path}")
    if not os.path.exists(file_path):
        print(f"CRITICAL: File not found: {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"DEBUG: Successfully loaded JSON from: {file_path}")
        # Basic type check based on expected schema_type
        if schema_type == "list" and not isinstance(data, list):
            print(f"Warning: Expected a list from {file_path}, but got {type(data)}.")
            # return None # Or handle as per desired strictness
        elif schema_type == "dict" and not isinstance(data, dict):
            print(f"Warning: Expected a dict from {file_path}, but got {type(data)}.")
            # return None
        return data
    except json.JSONDecodeError as e:
        print(f"CRITICAL: JSONDecodeError in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"CRITICAL: Unexpected error loading {file_path}: {e}")
        return None

# --- Utility Functions (if any specific to this script, like print_stars) ---
def print_stars(length=50):
    print("*" * length)

def print_header(title):
    print_stars(len(title) + 6)
    print(f"** {title} **")
    print_stars(len(title) + 6)
    print("\\n")

def print_subheader(title):
    print(f"\\n--- {title} ---")

# --- Data Loading Functions ---
def load_player_data(base_data_path): # Changed signature
    print(f"DEBUG: Starting to load player data from base path: {base_data_path}")
    all_players_dict = {}
    player_team_links = defaultdict(list)
    
    league_player_dirs_found = 0
    club_player_files_found = 0
    total_players_loaded = 0

    for item in os.listdir(base_data_path):
        item_path = os.path.join(base_data_path, item)
        if os.path.isdir(item_path) and item.startswith("league_") and item.endswith("_clubs_players"):
            league_player_dirs_found += 1
            print(f"DEBUG: Scanning league player directory: {item_path}")
            for player_file_name in os.listdir(item_path):
                if player_file_name.startswith("club_") and player_file_name.endswith("_players.json"):
                    club_player_files_found += 1
                    club_id_part = player_file_name[:-len("_players.json")] # NEW: Keeps "club_" prefix. e.g. "club_juventus_players.json" -> "club_juventus"

                    player_file_path = os.path.join(item_path, player_file_name)
                    players_in_file = load_json_data(player_file_path, schema_type="list")
                    
                    if isinstance(players_in_file, list):
                        for player_data in players_in_file:
                            if isinstance(player_data, dict) and 'player_id' in player_data:
                                player_id = player_data['player_id']
                                if player_id in all_players_dict:
                                    print(f"Warning: Duplicate player_id {player_id} found. Overwriting from {player_file_path}. Original: {all_players_dict[player_id].get('source_file', 'N/A')}")
                                player_data['source_file'] = player_file_path # Keep track of origin
                                player_data['club_id_source'] = club_id_part # Store the club_id derived from filename
                                all_players_dict[player_id] = player_data
                                player_team_links[club_id_part].append(player_id)
                                total_players_loaded +=1
                            else:
                                print(f"Warning: Invalid player data format or missing 'player_id' in {player_file_path}: {player_data}")
                    else:
                        print(f"Warning: Expected a list of players in {player_file_path}, but got {type(players_in_file)}. Skipping.")
    
    print(f"DEBUG: Player data loading summary: Found {league_player_dirs_found} league player dirs, {club_player_files_found} club player files. Loaded {total_players_loaded} players into all_players_dict.")
    if not all_players_dict:
        print("CRITICAL WARNING: No players were loaded into all_players_dict.")
    if not player_team_links:
        print("WARNING: No player-team links were established.")
        
    return all_players_dict, player_team_links

# --- Data Loading Functions (specific to this simulation) ---
def load_all_club_data(clubs_dir_path, leagues_list_from_json_main, all_players_global_dict, player_team_links): # Added player data params
    print(f"DEBUG: Attempting to load club data from {clubs_dir_path}, and integrate players.")
    all_clubs_main = {}
    club_files_to_load_main = set()

    # First, gather all club metadata files (e.g., epl_clubs.json)
    if os.path.exists(clubs_dir_path):
        for filename_main in os.listdir(clubs_dir_path):
            if filename_main.endswith('.json'): # Assuming these are league-wide club list files
                club_files_to_load_main.add(os.path.join(clubs_dir_path, filename_main))
    
    # Load actual club data from these files
    for file_path_main in club_files_to_load_main:
        # These files are expected to contain a LIST of club objects for a league
        league_club_data_list = load_json_data(file_path_main, schema_type="list") 
        if isinstance(league_club_data_list, list):
            for club_main_data in league_club_data_list: # club_main_data is a dict for one club
                if isinstance(club_main_data, dict) and "id" in club_main_data:
                    club_id = club_main_data["id"]
                    
                    # Initialize 'players' list for the club
                    club_main_data['players'] = []
                    
                    # Use player_team_links to find player IDs for this club
                    # The club_id from club_main_data["id"] must match the keys in player_team_links
                    # (which were derived from club_XYZ_players.json filenames)
                    if club_id in player_team_links:
                        for player_id in player_team_links[club_id]:
                            if player_id in all_players_global_dict:
                                # Embed the full player object
                                club_main_data['players'].append(copy.deepcopy(all_players_global_dict[player_id]))
                            else:
                                print(f"Warning: Player ID {player_id} linked to club {club_id} not found in all_players_global_dict.")
                    # else:
                        # print(f"Debug: No player links found for club ID {club_id} in player_team_links (this might be okay if club has no separate player file or no players).")

                    if not club_main_data['players']:
                        print(f"Debug: Club {club_id} ({club_main_data.get('name', 'N/A')}) has no players embedded after processing links.")

                    all_clubs_main[club_id] = club_main_data
                else:
                    print(f"Warning: Club data in {file_path_main} missing 'id' or not a dict. Entry: {club_main_data}")
        else:
            print(f"Warning: Expected a list of clubs in {file_path_main}, got {type(league_club_data_list)}. Skipping.")

    if not all_clubs_main: print("DEBUG: load_all_club_data found no clubs.")
    else: print(f"DEBUG: load_all_club_data loaded {len(all_clubs_main)} clubs and attempted to embed players.")
    return all_clubs_main

def load_all_manager_data(managers_list_from_file): # Simplified signature
    print("DEBUG: Processing managers list to create a dictionary.")
    all_managers_dict = {}
    temp_id_counter = 0
    if not isinstance(managers_list_from_file, list):
        print("CRITICAL: managers_list_from_file is not a list. Cannot load managers.")
        return {}

    for i, manager_data in enumerate(managers_list_from_file):
        if not isinstance(manager_data, dict):
            print(f"Warning: Item {i} in managers list is not a dictionary: {manager_data}")
            continue

        manager_id = manager_data.get("id")
        if not manager_id:
            # Attempt to create a unique ID if 'name' exists, otherwise use a counter
            name_part = manager_data.get("name", "").replace(" ", "_").lower()
            if name_part:
                 manager_id = f"temp_manager_{name_part}_{i}"
            else:
                 manager_id = f"temp_manager_id_{temp_id_counter}"
            print(f"Warning: Manager data at index {i} missing 'id'. Assigning temporary ID: {manager_id}. Manager data: {manager_data}")
            manager_data["id"] = manager_id # Add temp ID to the dict
            temp_id_counter += 1
        
        if manager_id in all_managers_dict:
            print(f"Warning: Duplicate manager ID '{manager_id}' found. Overwriting. Original: {all_managers_dict[manager_id]}, New: {manager_data}")
        all_managers_dict[manager_id] = manager_data
            
    if not all_managers_dict:
        print("Warning: No manager data loaded into dictionary. Using defaults where necessary.")
    else:
        print(f"DEBUG: Loaded {len(all_managers_dict)} managers into dictionary.")
    return all_managers_dict

def initialize_all_leagues_and_clubs(leagues_data, managers_data, playing_styles_data, all_clubs_from_files, player_team_links):
    print("DEBUG: Entered initialize_all_leagues_and_clubs")
    
    sim_teams_by_id_lookup = {}
    league_stats_lookup = {} # For individual team stats if needed outside league table
    league_details = {} # Initialize this
    teams_by_league = {} # Initialize this

    if not isinstance(leagues_data, dict) or 'leagues' not in leagues_data:
        print("CRITICAL: leagues_data is not a dictionary or 'leagues' key is missing.")
        return {}, {}, {}, {}, {} # Match the 5 return values

    for league_info in leagues_data.get('leagues', []):
        league_id = league_info.get("id")
        if not league_id:
            print(f"Warning: League data missing 'id': {league_info}")
            continue
        
        league_details[league_id] = {
            "name": league_info.get("name", ""),
            "country": league_info.get("country", ""),
            "tier": league_info.get("tier", 1),
            "type": league_info.get("type", "domestic"),
            "reputation": league_info.get("reputation", 0),
            "avg_strength": league_info.get("avg_strength", 0),
            "qualification": league_info.get("qualification", {})
        }
        
        current_league_teams = []
        for club_id_iter, club_data_iter in all_clubs_from_files.items():
            if str(club_data_iter.get("league_id")) == str(league_id):
                 current_league_teams.append(club_id_iter)
        
        teams_by_league[league_id] = current_league_teams

    sim_teams_by_id_lookup.update(all_clubs_from_files)

    print("DEBUG: Exiting initialize_all_leagues_and_clubs")
    return all_clubs_from_files, teams_by_league, sim_teams_by_id_lookup, league_details, league_stats_lookup

# --- Club Strength Calculation (5-factor model) ---
def get_club_strength(club_data, manager_data, league_avg_strength=70, historical_performance_weight=0.3, current_form_weight=0.1):
    """Calculates club strength based on multiple factors."""
    # 1. Player Quality
    player_skills = []
    if isinstance(club_data.get('players'), list):
        for player in club_data['players']:
            if isinstance(player, dict) and 'skill' in player:
                player_skills.append(player['skill'])
            # elif isinstance(player, str): # Handling player IDs if players are not embedded dicts
                # This would require a global player lookup, not handled here for simplicity
                # print(f"Warning: Player data for {club_data.get('name')} seems to be ID, not dict: {player}")
                # pass


    if not player_skills:
        avg_player_skill = 50 
    else:
        player_skills.sort(reverse=True)
        top_n_players = player_skills[:20] # Consider top 20 players
        if top_n_players:
            avg_player_skill = sum(top_n_players) / len(top_n_players)
        else: # Should not happen if player_skills is not empty, but as a fallback
            avg_player_skill = 50


    # 2. Managerial Skill
    manager_skill = 70 
    if manager_data and isinstance(manager_data, dict):
        manager_skill = manager_data.get('manager_ability', 70)

    # 3. Historical Performance (Club's own reputation)
    historical_strength = club_data.get('reputation', 5000) / 100.0 
    historical_strength = max(1, min(100, historical_strength)) # Clamp to 1-100

    # 4. League Strength (Passed as argument, assumed 0-100)
    # league_avg_strength is used directly

    # 5. Current Form (Placeholder)
    current_form_factor = 50 # Neutral form, scale 0-100

    # Weights
    player_quality_weight = 0.40
    manager_skill_weight = 0.20
    # historical_performance_weight is an arg (default 0.3)
    league_strength_weight = 0.00 # For UCL, direct club factors are more important.
                                 # Set to 0.0 to exclude, or a small value if desired.
    # current_form_weight is an arg (default 0.1)

    # Ensure weights sum up correctly if any are changed or excluded
    total_active_weight = player_quality_weight + manager_skill_weight + historical_performance_weight + league_strength_weight + current_form_weight
    if total_active_weight == 0: return 50 # Avoid division by zero if all weights are zero

    strength = (
        (avg_player_skill * player_quality_weight) +
        (manager_skill * manager_skill_weight) +
        (historical_strength * historical_performance_weight) +
        (league_avg_strength * league_strength_weight) +
        (current_form_factor * current_form_weight)
    ) / total_active_weight

    return max(1, min(100, strength))

# --- Team Qualification ---
def get_ucl_qualified_teams(leagues_data, all_clubs, all_managers):
    """Determines UCL qualified teams based on leagues.json configuration."""
    qualified_teams_output = []
    ucl_config = leagues_data.get("competition_ucl", {})
    if not ucl_config:
        print("Error: 'competition_ucl' not found in leagues.json.")
        return []
        
    qualification_criteria = ucl_config.get("qualification_criteria", {})
    domestic_leagues_spots = qualification_criteria.get("domestic_leagues", {})

    # Placeholder for league average strengths (ideally pre-calculated)
    # For now, using a default or deriving simplistically if needed by get_club_strength
    league_avg_strengths = {lg_id: 70 for lg_id in leagues_data.get("leagues", {})} 

    processed_club_ids = set()

    # Qualification from domestic leagues
    for league_id_key, spots_info in domestic_leagues_spots.items():
        # league_id_key might be "L<ID>" or just "<ID>"
        league_id_to_match = league_id_key.replace("L","") # Normalize
        
        num_spots = 0
        if isinstance(spots_info, dict):
            num_spots = spots_info.get("spots", 0)
        elif isinstance(spots_info, int): # Older format?
            num_spots = spots_info

        league_clubs_for_qualification = []
        for club_id, club_detail in all_clubs.items():
            if str(club_detail.get("league_id")) == league_id_to_match and club_id not in processed_club_ids:
                league_clubs_for_qualification.append(club_detail)
        
        if not league_clubs_for_qualification:
            # print(f"No clubs found for league_id {league_id_to_match} or all already processed.")
            continue
            
        league_clubs_for_qualification.sort(key=lambda c: c.get('reputation', 0), reverse=True)

        for i in range(min(num_spots, len(league_clubs_for_qualification))):
            club = league_clubs_for_qualification[i]
            if club['id'] in processed_club_ids:
                continue

            manager_id = club.get("manager_id")
            manager_data = all_managers.get(manager_id)
            if not manager_data: # Provide default manager if not found
                manager_data = {
                    "id": f"default_mgr_{club['id']}", 
                    "name": f"{club.get('name', 'Unknown Club')}'s Default Manager", 
                    "manager_ability": 65, 
                    "preferred_formation": DEFAULT_FORMATION
                }
            
            club_domestic_league_avg_strength = league_avg_strengths.get(str(club.get("league_id")), 70)
            strength = get_club_strength(club, manager_data, club_domestic_league_avg_strength)

            team_entry = {
                "id": club["id"],
                "name": club.get("name", f"Club {club['id']}"),
                "country": club.get("country", leagues_data.get("leagues", {}).get(str(club.get("league_id")), {}).get("country", "Unknown")),
                "reputation": strength, # This will be used by Swiss model's match sim
                "pot": 1, # Will be re-assigned later
                "players": club.get("players", []), 
                "manager": manager_data,
                "club_data_full": club 
            }
            qualified_teams_output.append(team_entry)
            processed_club_ids.add(club['id'])

    # TODO: Add UCL/UEL title holder spots
    # TODO: Add European Performance Spots (new format)

    # Fill remaining spots if less than 36
    if len(qualified_teams_output) < 36:
        print(f"Warning: Only {len(qualified_teams_output)} teams qualified. Attempting to fill with highest reputation clubs.")
        remaining_clubs_to_consider = []
        for club_id, club_detail in all_clubs.items():
            if club_id not in processed_club_ids:
                remaining_clubs_to_consider.append(club_detail)
        
        remaining_clubs_to_consider.sort(key=lambda c: c.get('reputation', 0), reverse=True)
        
        needed = 36 - len(qualified_teams_output)
        for i in range(min(needed, len(remaining_clubs_to_consider))):
            club = remaining_clubs_to_consider[i]
            manager_id = club.get("manager_id")
            manager_data = all_managers.get(manager_id, {"id": f"default_mgr_{club['id']}", "name": "Default Fill Manager", "manager_ability": 60, "preferred_formation": DEFAULT_FORMATION})
            club_domestic_league_avg_strength = league_avg_strengths.get(str(club.get("league_id")), 70)
            strength = get_club_strength(club, manager_data, club_domestic_league_avg_strength)

            team_entry = {
                "id": club["id"], "name": club.get("name", f"Club {club['id']}"),
                "country": club.get("country", "Unknown (Filler)"), "reputation": strength,
                "pot": 4, "players": club.get("players", []), "manager": manager_data,
                "club_data_full": club
            }
            qualified_teams_output.append(team_entry)
            processed_club_ids.add(club['id'])
            if len(qualified_teams_output) == 36: break
    
    # Truncate if more than 36 (should ideally not happen with precise rules)
    if len(qualified_teams_output) > 36:
        print(f"Warning: {len(qualified_teams_output)} teams qualified. Truncating to 36 based on strength.")
        qualified_teams_output.sort(key=lambda t: t['reputation'], reverse=True)
        qualified_teams_output = qualified_teams_output[:36]
    
    # Assign pots based on final strength/reputation
    qualified_teams_output.sort(key=lambda t: t['reputation'], reverse=True)
    for i, team in enumerate(qualified_teams_output):
        if i < 9: team['pot'] = 1
        elif i < 18: team['pot'] = 2
        elif i < 27: team['pot'] = 3
        else: team['pot'] = 4
        
    if len(qualified_teams_output) < 36:
         print(f"CRITICAL WARNING: Could not gather 36 teams. Only {len(qualified_teams_output)} found. Simulation may be unstable.")

    return qualified_teams_output

# --- Player and Team Setup for Simulation ---
def setup_simulation_data(qualified_teams_from_qualification_step):
    """
    Prepares team and player data structures for the simulation.
    - `sim_teams_list`: List of team dicts for the simulation.
    - `all_players_dict`: Dict of all players from qualified teams, with stats fields.
    """
    sim_teams_list = []
    all_players_dict = {}

    for team_data_in in qualified_teams_from_qualification_step:
        current_team_player_ids_list = []
        if not isinstance(team_data_in.get('players'), list):
            print(f"Warning: Players data for team {team_data_in.get('name')} is not a list or missing. Skipping players for this team.")
            team_data_in['players'] = [] # Ensure it's an empty list

        for player_raw_data in team_data_in.get('players', []):
            if not isinstance(player_raw_data, dict) or 'player_id' not in player_raw_data:
                # print(f"Warning: Invalid player data format or missing 'player_id' for team {team_data_in.get('name')}: {player_raw_data}")
                continue

            player_id = player_raw_data['player_id']
            current_team_player_ids_list.append(player_id)

            # Initialize player stats for the simulation
            all_players_dict[player_id] = {
                "id": player_id,
                "name": player_raw_data.get("name", f"Player {player_id}"),
                "team_id": team_data_in["id"],
                "team_name": team_data_in["name"],
                "position": player_raw_data.get("position", "MID"), 
                "specific_position": player_raw_data.get("specific_position", player_raw_data.get("position", "CM")),
                "skill": player_raw_data.get("skill", 60),
                "form": round(random.uniform(0.85, 1.15), 2), 
                "avg_rating": 0.0,
                "total_rating_points": 0.0,
                "matches_played": 0,
                "goals": 0,
                "assists": 0,
                "clean_sheets": 0,
                "real_data": player_raw_data.get("real_data", False),
                "tournament_score": 0.0,
                # Store original data if needed for complex logic later, e.g. detailed attributes
                # "original_attributes": player_raw_data.get("attributes", {}) 
            }
        
        sim_team_entry = {
            "id": team_data_in["id"],
            "name": team_data_in["name"],
            "country": team_data_in["country"],
            "reputation": team_data_in["reputation"], # This is the calculated strength
            "pot": team_data_in["pot"],
            "player_ids": current_team_player_ids_list, 
            "manager": team_data_in.get("manager", {"name": "N/A", "preferred_formation": DEFAULT_FORMATION, "manager_ability": 70}),
            # "club_data_full": team_data_in.get("club_data_full") # Optional: for deep reference
        }
        sim_teams_list.append(sim_team_entry)

    if not sim_teams_list:
        print("CRITICAL ERROR: No teams prepared for simulation.")
    if not all_players_dict:
        print("CRITICAL ERROR: No players prepared for simulation (all_players_dict is empty).")
        
    return sim_teams_list, all_players_dict


# --- Swiss Model Simulation Logic (from simple_ucl_swiss_model_simulation.py) ---

FORMATIONS = { # Copied from simple_ucl_swiss_model_simulation.py
    '4-3-3': {'GK': 1, 'DEF': 4, 'MID': 3, 'FWD': 3},
    '4-2-3-1': {'GK': 1, 'DEF': 4, 'MID': 5, 'FWD': 1},
    '3-5-2': {'GK': 1, 'DEF': 3, 'MID': 5, 'FWD': 2},
    '4-4-2': {'GK': 1, 'DEF': 4, 'MID': 4, 'FWD': 2},
    '3-4-3': {'GK': 1, 'DEF': 3, 'MID': 4, 'FWD': 3},
    '4-1-4-1': {'GK': 1, 'DEF': 4, 'MID': 5, 'FWD': 1},
    '5-3-2': {'GK': 1, 'DEF': 5, 'MID': 3, 'FWD': 2}
}

def select_starting_xi(team_player_ids, all_players_data, formation_name=None):
    """Select starting XI based on formation, prioritizing skill.
       Uses all_players_data which is the central player registry.
       `team_player_ids` are the IDs of players belonging to the specific team.
    """
    lineup_ids = []
    # Filter all_players_data to get only players belonging to the current team
    available_players = [all_players_data[pid] for pid in team_player_ids if pid in all_players_data]

    if not formation_name or formation_name not in FORMATIONS:
        formation_name = DEFAULT_FORMATION
    
    positions_needed = FORMATIONS[formation_name]
    
    # Sort available players by skill primarily for selection
    available_players.sort(key=lambda x: x['skill'], reverse=True)
    
    # Group players by their general position (GK, DEF, MID, FWD)
    # This uses the 'position' field from player data (e.g., "GK", "DEF", "MID", "FWD")
    # which should align with FORMATIONS keys.
    
    player_pool_by_pos = defaultdict(list)
    for p in available_players:
        player_pool_by_pos[p['position']].append(p)

    selected_player_ids_set = set()

    for pos_code, count_needed in positions_needed.items():
        # Get players for this general position category
        eligible_for_pos_category = player_pool_by_pos[pos_code]
        
        # Sort them by skill (already done for available_players, but good to ensure if subsets change)
        # eligible_for_pos_category.sort(key=lambda x: x['skill'], reverse=True)

        selected_count_for_pos = 0
        for player in eligible_for_pos_category:
            if player['id'] not in selected_player_ids_set:
                if selected_count_for_pos < count_needed:
                    lineup_ids.append(player['id'])
                    selected_player_ids_set.add(player['id'])
                    selected_count_for_pos += 1
                else:
                    break
    
    # If lineup is short (e.g. not enough specialized players), fill with best remaining players
    # from any position, prioritizing those not already selected.
    if len(lineup_ids) < 11:
        # print(f"Warning: Lineup short ({len(lineup_ids)}/11). Filling with best available.")
        remaining_available_overall = [p for p in available_players if p['id'] not in selected_player_ids_set]
        # No need to re-sort, `available_players` was already sorted by skill.
        
        fill_needed = 11 - len(lineup_ids)
        for player in remaining_available_overall:
            if fill_needed <= 0: break
            lineup_ids.append(player['id'])
            selected_player_ids_set.add(player['id']) # Ensure set is also updated
            fill_needed -=1
            
    if len(lineup_ids) < 11:
        # This is a more critical issue, means not enough players overall for the team.
        print(f"CRITICAL WARNING: Team could not form a full XI. Only {len(lineup_ids)} players. Padding with placeholders if possible.")
        # This scenario should ideally be handled by ensuring teams have enough players during setup.
        # For now, we'll proceed, but match simulation might be skewed.
        # If absolutely necessary, one could create dummy players here, but that's a deeper fix.
        pass

    return lineup_ids[:11] # Ensure exactly 11 if somehow overfilled, or less if critically short


def assign_goals_and_assists(num_goals, team_lineup_ids, all_players_data):
    """Assigns goals and assists to players in the lineup.
       Modifies all_players_data directly.
    """
    contributions = [] # list of {'player_id': ..., 'type': 'goal'/'assist'}
    if not team_lineup_ids or num_goals == 0:
        return contributions

    lineup_players = [all_players_data[pid] for pid in team_lineup_ids if pid in all_players_data]
    if not lineup_players: # Should not happen if team_lineup_ids is valid
        print("Warning: No lineup players found for assigning goals/assists.")
        return contributions
    
    for _ in range(num_goals):
        potential_scorers = [p for p in lineup_players if p['position'] != 'GK']
        if not potential_scorers: continue

        scorer_weights = []
        for p in potential_scorers:
            # Skill and form influence scoring propensity
            effective_skill = p['skill'] * p.get('form', 1.0) 
            if p['position'] == 'FWD': scorer_weights.append(effective_skill * 3)
            elif p['position'] == 'MID': scorer_weights.append(effective_skill * 2)
            else: scorer_weights.append(effective_skill * 1) # DEF
        
        if not scorer_weights or sum(scorer_weights) == 0: # Fallback if all weights are zero
            scorer = random.choice(potential_scorers)
        else:
            scorer = random.choices(potential_scorers, weights=scorer_weights, k=1)[0]
        
        all_players_data[scorer['id']]['goals'] += 1
        contributions.append({'player_id': scorer['id'], 'type': 'goal'})

        if random.random() < 0.65: # Chance of assist
            potential_assisters = [p for p in lineup_players if p['id'] != scorer['id'] and p['position'] != 'GK']
            if not potential_assisters: continue

            assister_weights = []
            for p in potential_assisters:
                # Skill and form influence assisting propensity
                effective_skill = p['skill'] * p.get('form', 1.0)
                if p['position'] == 'MID': assister_weights.append(effective_skill * 3)
                elif p['position'] == 'FWD': assister_weights.append(effective_skill * 2)
                else: assister_weights.append(effective_skill * 1) # DEF
            
            if not assister_weights or sum(assister_weights) == 0: # Fallback
                assister = random.choice(potential_assisters)
            else:
                assister = random.choices(potential_assisters, weights=assister_weights, k=1)[0]
            
            all_players_data[assister['id']]['assists'] += 1
            contributions.append({'player_id': assister['id'], 'type': 'assist'})
            
    return contributions

def calculate_match_rating(player_id, all_players_data, team_result_char, goals_conceded_by_team, player_contributions_in_match):
    """Calculates a player's match rating and updates their stats."""
    player = all_players_data[player_id]
    rating = BASE_RATING # from constants

    p_goals = sum(1 for c in player_contributions_in_match if c['player_id'] == player_id and c['type'] == 'goal')
    p_assists = sum(1 for c in player_contributions_in_match if c['player_id'] == player_id and c['type'] == 'assist')

    if team_result_char == 'W': rating += 0.7
    elif team_result_char == 'D': rating += 0.3

    rating += p_goals * 1.2
    rating += p_assists * 0.8

    if player['position'] == 'GK':
        if goals_conceded_by_team == 0:
            rating += 1.0
            player['clean_sheets'] += 1
        rating -= goals_conceded_by_team * 0.25
    elif player['position'] == 'DEF':
        if goals_conceded_by_team == 0: rating += 0.4
        rating -= goals_conceded_by_team * 0.15
    
    # Skill and Form influence
    skill_mod = (player['skill'] - 75) / 50.0 
    form_mod = (player.get('form', 1.0) - 1.0) * FORM_INFLUENCE 
    rating += skill_mod + form_mod
    
    # Add small random variation
    rating += random.normalvariate(0, RATING_STD_DEV)

    rating = max(4.0, min(10.0, round(rating, 1)))

    player['matches_played'] += 1
    player['total_rating_points'] += rating
    if player['matches_played'] > 0:
        player['avg_rating'] = round(player['total_rating_points'] / player['matches_played'], 2)
        
    # Update player form slightly based on performance (simple model)
    # Good performance (rating > 7.0) might increase form, bad (<5.5) might decrease
    if rating > 7.2:
        player['form'] = min(1.20, round(player.get('form', 1.0) + 0.03, 2))
    elif rating < 5.8:
        player['form'] = max(0.80, round(player.get('form', 1.0) - 0.03, 2))
    else: # Drift towards mean
        player['form'] = round(player.get('form', 1.0) * 0.98 + 1.0 * 0.02, 2)


    return rating


def apply_tournament_stage_bonus(team_ids_to_bonus, bonus_points, all_teams_flat_players, teams_by_id_lookup):
    """Applies a bonus to total_rating_points for all players of the given teams.
       `all_teams_flat_players` is the global player dict.
       `teams_by_id_lookup` is a dict mapping team_id to team object (from sim_teams_list).
    """
    if not isinstance(team_ids_to_bonus, list):
        team_ids_to_bonus = [team_ids_to_bonus]

    for team_id in team_ids_to_bonus:
        team = teams_by_id_lookup.get(team_id)
        if not team:
            # print(f"Warning: Team ID {team_id} not found for applying bonus.")
            continue
        
        # print(f"Applying {bonus_points} bonus to players of {team['name']}")
        for player_id in team['player_ids']: # Corrected syntax: removed colon from slice-like notation
            player = all_teams_flat_players.get(player_id)
            if player and player['matches_played'] > 0: # Only bonus players who participated
                player['total_rating_points'] += bonus_points
                # Recalculate average rating after bonus
                player['avg_rating'] = round(player['total_rating_points'] / player['matches_played'], 2)
                # print(f"  Bonus for {player['name']}. New total points: {player['total_rating_points']}, New Avg Rating: {player['avg_rating']}")
            # elif player and player['matches_played'] == 0:
                # print(f"  Player {player['name']} did not play, no bonus.")
                # pass

def generate_league_phase_fixtures(teams_list_for_sim): # teams_list_for_sim is sim_teams_for_model
    """
    Generates fixtures for the Swiss model league phase.
    Each team plays 8 matches, 4 home and 4 away, against 8 different opponents.
    Attempts to balance pots for opponents but primarily focuses on unique opponents and H/A balance.
    """
    fixtures = []
    num_teams = len(teams_list_for_sim)
    if num_teams == 0: return fixtures

    team_schedules = {
        team['id']: {
            'opponents': set(), 
            'home_count': 0, 
            'away_count': 0, 
            'played_count': 0, 
            'pot': team['pot']
        } for team in teams_list_for_sim
    }
    team_ids = [t['id'] for t in teams_list_for_sim]
    
    # Pot-based opponent selection enhancement (simplified)
    # For each team, try to play 2 teams from each pot (including their own, if necessary for scheduling)
    # This is a guideline, main goal is 8 unique opponents with H/A balance.

    for _round_num in range(1, 9): # 8 rounds of matches
        # print(f"Generating fixtures for Round {_round_num}")
        # Sort teams by points (or initial reputation/pot for early rounds) - dynamic pairing
        # For simplicity here, we'll use a static list and try to pair
        
        teams_to_schedule_this_round = [tid for tid in team_ids if team_schedules[tid]['played_count'] < 8]
        random.shuffle(teams_to_schedule_this_round)
        
        paired_in_this_round = set()

        for i in range(len(teams_to_schedule_this_round)):
            team1_id = teams_to_schedule_this_round[i]
            if team1_id in paired_in_this_round or team_schedules[team1_id]['played_count'] >= 8:
                continue

            # Find a suitable opponent for team1_id
            potential_opponents = []
            for team2_id in teams_to_schedule_this_round:
                if team1_id == team2_id or team2_id in paired_in_this_round:
                    continue
                if team_schedules[team2_id]['played_count'] >= 8:
                    continue
                if team2_id in team_schedules[team1_id]['opponents']: # Already played
                    continue
                
                # Basic pot difference check (optional, can be complex)
                # pot_diff = abs(team_schedules[team1_id]['pot'] - team_schedules[team2_id]['pot'])
                
                potential_opponents.append(team2_id)
            
            if not potential_opponents:
                # print(f"Warning: Could not find opponent for {team1_id} in round {_round_num} among available.")
                continue

            # Simple random choice for now, could be more sophisticated (e.g. based on current standings)
            team2_id = random.choice(potential_opponents)

            # Decide home/away to balance counts
            home_id, away_id = None, None
            team1_prefers_home = team_schedules[team1_id]['home_count'] < 4
            team1_prefers_away = team_schedules[team1_id]['away_count'] < 4
            team2_prefers_home = team_schedules[team2_id]['home_count'] < 4
            team2_prefers_away = team_schedules[team2_id]['away_count'] < 4

            if team1_prefers_home and team2_prefers_away:
                home_id, away_id = team1_id, team2_id
            elif team1_prefers_away and team2_prefers_home:
                home_id, away_id = team2_id, team1_id
            elif team1_prefers_home: # team2 cannot be away or doesn't prefer it
                 home_id, away_id = team1_id, team2_id # Force if team1 can still host
            elif team2_prefers_home: # team1 cannot be away or doesn't prefer it
                 home_id, away_id = team2_id, team1_id # Force if team2 can still host
            else: # If both have filled preferred slots, or one is full for both H/A
                  # This indicates a potential issue or end of easy pairings.
                  # For now, we'll skip if no clear H/A assignment to maintain balance.
                  # A more robust scheduler would backtrack or use a cost function.
                  # print(f"Skipping pair {team1_id} vs {team2_id} due to H/A conflict or full schedules.")
                  continue 
            
            if home_id and away_id:
                fixtures.append({'home': home_id, 'away': away_id, 'round': _round_num})
                
                team_schedules[home_id]['opponents'].add(away_id)
                team_schedules[away_id]['opponents'].add(home_id)
                
                team_schedules[home_id]['home_count'] += 1
                team_schedules[away_id]['away_count'] += 1
                
                team_schedules[home_id]['played_count'] += 1
                team_schedules[away_id]['played_count'] += 1
                
                paired_in_this_round.add(home_id)
                paired_in_this_round.add(away_id)

    # Post-generation check and fill (if some teams don't have 8 games)
    # This is a simplified filler, a real Swiss system pairs based on current standings dynamically.
    for team_id in team_ids:
        fill_round_num = 9 # Use a distinct round number for filled matches
        while team_schedules[team_id]['played_count'] < 8:
            # print(f"Team {team_id} needs {8 - team_schedules[team_id]['played_count']} more games. Attempting to fill.")
            possible_fill_opponents = [
                opp_id for opp_id in team_ids 
                if opp_id != team_id and \
                   opp_id not in team_schedules[team_id]['opponents'] and \
                   team_schedules[opp_id]['played_count'] < 8
            ]
            if not possible_fill_opponents:
                # print(f"Warning: Cannot find any more unique opponents for {team_id} to reach 8 games.")
                break 
            
            opponent_id = random.choice(possible_fill_opponents)

            home_id, away_id = None, None
            if team_schedules[team_id]['home_count'] < 4 and team_schedules[opponent_id]['away_count'] < 4:
                home_id, away_id = team_id, opponent_id
            elif team_schedules[opponent_id]['home_count'] < 4 and team_schedules[team_id]['away_count'] < 4:
                home_id, away_id = opponent_id, team_id
            # If H/A counts are already at 4 for one side, try to assign the other way if possible
            elif team_schedules[team_id]['home_count'] < 4: # team_id can host
                home_id, away_id = team_id, opponent_id
            elif team_schedules[opponent_id]['home_count'] < 4: # opponent_id can host
                home_id, away_id = opponent_id, team_id
            else: # Both have 4 home games, try to assign away games if possible
                if team_schedules[team_id]['away_count'] < 4:
                     home_id, away_id = opponent_id, team_id # team_id plays away
                elif team_schedules[opponent_id]['away_count'] < 4:
                     home_id, away_id = team_id, opponent_id # opponent_id plays away
                else:
                    # print(f"Warning: Could not assign H/A for fill match between {team_id} and {opponent_id} due to H/A limits.")
                    # To prevent infinite loops if a perfect balance isn't found, break or pick one randomly.
                    # Forcing one if counts are equal but less than 4.
                    if team_schedules[team_id]['home_count'] < 4: home_id, away_id = team_id, opponent_id
                    else: break # Truly stuck
            
            if home_id and away_id:
                # print(f"  Filling match: {home_id} vs {away_id} (Round {fill_round_num})")
                fixtures.append({'home': home_id, 'away': away_id, 'round': fill_round_num})
                team_schedules[home_id]['opponents'].add(away_id)
                team_schedules[away_id]['opponents'].add(home_id)
                if home_id == team_id: team_schedules[home_id]['home_count'] +=1
                else: team_schedules[home_id]['away_count'] +=1 # team_id was away
                
                if away_id == opponent_id : team_schedules[opponent_id]['away_count'] +=1
                else: team_schedules[opponent_id]['home_count'] +=1 # opponent_id was away

                team_schedules[home_id]['played_count'] += 1
                team_schedules[away_id]['played_count'] += 1
            else:
                # print(f"Could not fill match for {team_id} against {opponent_id}. Stopping fill for this team.")
                break # Cannot find a H/A assignment
        
    # Final verification
    total_games_scheduled = len(fixtures) * 2 # Each fixture involves two teams playing
    expected_total_games = num_teams * 8
    # print(f"Total fixtures generated: {len(fixtures)} (Expected {expected_total_games / 2})")
    # for team_id_val, sched_data in team_schedules.items():
    #     if sched_data['played_count'] != 8:
    #         print(f"  Warning: Team {team_id_val} has {sched_data['played_count']} games (H:{sched_data['home_count']}, A:{sched_data['away_count']})")

    if total_games_scheduled != expected_total_games:
         print(f"WARNING: Fixture generation mismatch. Expected {expected_total_games} total game participations, got {total_games_scheduled}.")
         print("This might mean not all teams have 8 games, or H/A balance is off.")
         for tid_check, s_data in team_schedules.items():
             if s_data['played_count'] != 8 or s_data['home_count'] != 4 or s_data['away_count'] != 4:
                 print(f"  - Team {tid_check}: Played={s_data['played_count']}, H={s_data['home_count']}, A={s_data['away_count']}")

    return fixtures

def simulate_match(home_team_sim_data, away_team_sim_data, all_players_global_dict, competition_phase="League"):
    """
    Simulates a single match between two teams.
    Uses team reputation (strength) and player data. Updates player stats.
    `home_team_sim_data`, `away_team_sim_data` are from `sim_teams_for_model`.
    `all_players_global_dict` is `all_players_for_model`.
    """
    # Team reputation is the 'reputation' field in sim_team_entry, which is calculated strength
    rep_diff = home_team_sim_data['reputation'] - away_team_sim_data['reputation']
    
    # Probabilities based on reputation difference (home advantage included)
    # Base probabilities: Home Win 40%, Draw 28%, Away Win 32%
    # Adjust based on rep_diff. A 10-point rep_diff might shift win prob by ~12%
    prob_home_win = 0.40 + (rep_diff * 0.012) 
    prob_draw = 0.28 - (abs(rep_diff) * 0.006) # Draw chance decreases with larger skill gap
    
    # Ensure probabilities are within reasonable bounds (e.g., 0.05 to 0.95)
    prob_home_win = max(0.05, min(0.90, prob_home_win))
    prob_draw = max(0.05, min(0.50, prob_draw))
    
    prob_away_win = 1.0 - prob_home_win - prob_draw
    prob_away_win = max(0.05, min(0.90, prob_away_win))

    # Normalize probabilities if they don't sum to 1 (due to clamping)
    total_prob = prob_home_win + prob_draw + prob_away_win
    if total_prob == 0: # Should not happen with current clamping
        prob_home_win, prob_draw, prob_away_win = 1/3, 1/3, 1/3
    else:
        prob_home_win /= total_prob
        prob_draw /= total_prob
        prob_away_win = 1.0 - prob_home_win - prob_draw # Recalculate for precision

    rand_val = random.random()
    home_goals, away_goals = 0, 0

    # Determine winner based on probabilities
    if rand_val < prob_home_win: # Home win
        home_goals = random.randint(1, 4) # More likely to score more
        away_goals = random.randint(0, max(0, home_goals - random.choice([1, 1, 2]))) # Away scores less
    elif rand_val < prob_home_win + prob_draw: # Draw
        home_goals = random.randint(0, 2) # Draws often lower scoring
        away_goals = home_goals
    else: # Away win
        away_goals = random.randint(1, 4)
        home_goals = random.randint(0, max(0, away_goals - random.choice([1, 1, 2])))

    # --- Player Stats Logic ---
    home_manager_formation = home_team_sim_data.get('manager', {}).get('preferred_formation', DEFAULT_FORMATION)
    away_manager_formation = away_team_sim_data.get('manager', {}).get('preferred_formation', DEFAULT_FORMATION)

    home_lineup_ids = select_starting_xi(home_team_sim_data['player_ids'], all_players_global_dict, home_manager_formation)
    away_lineup_ids = select_starting_xi(away_team_sim_data['player_ids'], all_players_global_dict, away_manager_formation)

    # Assign goals and assists (modifies all_players_global_dict)
    home_contributions = assign_goals_and_assists(home_goals, home_lineup_ids, all_players_global_dict)
    away_contributions = assign_goals_and_assists(away_goals, away_lineup_ids, all_players_global_dict)

    # Determine result character for rating calculation
    home_result_char = 'W' if home_goals > away_goals else ('D' if home_goals == away_goals else 'L')
    away_result_char = 'W' if away_goals > home_goals else ('D' if away_goals == home_goals else 'L')

    # Calculate and update match ratings for all participating players
    for player_id in home_lineup_ids:
        calculate_match_rating(player_id, all_players_global_dict, home_result_char, away_goals, home_contributions)
    
    for player_id in away_lineup_ids:
        calculate_match_rating(player_id, all_players_global_dict, away_result_char, home_goals, away_contributions)
        
    # Removed random form update loop to allow performance-based form changes from calculate_match_rating to persist

    return home_goals, away_goals

def run_league_phase(teams, fixtures, all_teams_flat_players): # MODIFIED
    league_table = {
        team['id']: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0, 'name': team['name'], 'country': team['country']}
        for team in teams
    }
    teams_by_id = {team['id']: team for team in teams}
    if fixtures: # Ensure fixtures is not None
        fixtures.sort(key=lambda x: x.get('round', 0))
    else:
        print("Warning: No fixtures provided for league phase.")
        fixtures = [] # Ensure it's an empty list if None

    for fixture_idx, fixture in enumerate(fixtures):
        # if fixture_idx % 20 == 0: print(f"  Simulating league match {fixture_idx+1}/{len(fixtures)}") # Progress
        home_team_id, away_team_id = fixture['home'], fixture['away']
        home_team, away_team = teams_by_id[home_team_id], teams_by_id[away_team_id]
        
        hg, ag = simulate_match(home_team, away_team, all_teams_flat_players)

        for tid, goals_for, goals_against, outcome_pts, outcome_char in [
            (home_team_id, hg, ag, 3 if hg > ag else (1 if hg == ag else 0), 'W' if hg > ag else ('D' if hg == ag else 'L')),
            (away_team_id, ag, hg, 3 if ag > hg else (1 if ag == hg else 0), 'W' if ag > hg else ('D' if ag == hg else 'L'))
        ]:
            league_table[tid]['P'] += 1
            league_table[tid]['GF'] += goals_for
            league_table[tid]['GA'] += goals_against
            league_table[tid]['Pts'] += outcome_pts
            league_table[tid][outcome_char] += 1
            
    for team_id in league_table:
        league_table[team_id]['GD'] = league_table[team_id]['GF'] - league_table[team_id]['GA']
        
    sorted_table_items = sorted(league_table.items(), key=lambda item: (item[1]['Pts'], item[1]['GD'], item[1]['GF'], item[1]['name']), reverse=True)
    return sorted_table_items, league_table, fixtures # Return raw table and fixtures

# --- Knockout Phase Logic ---
def simulate_knockout_tie(team1_id, team2_id, teams_by_id_lookup, all_players_global_dict, neutral_venue=False, competition_phase="Knockout"):
    print(f"DEBUG: Simulating knockout tie: {teams_by_id_lookup.get(team1_id, {}).get('name', 'Unknown')} vs {teams_by_id_lookup.get(team2_id, {}).get('name', 'Unknown')} ({competition_phase})")
    team1_data = teams_by_id_lookup[team1_id]
    team2_data = teams_by_id_lookup[team2_id]

    if neutral_venue:
        t1_g, t2_g = simulate_match(team1_data, team2_data, all_players_global_dict, competition_phase=f"{competition_phase} Final")
        
        if t1_g == t2_g:
            # Penalties
            winner_id = random.choice([team1_id, team2_id])
        else:
            winner_id = team1_id if t1_g > t2_g else team2_id
        return winner_id

    # Two-legged tie
    leg1_t1_g, leg1_t2_g = simulate_match(team1_data, team2_data, all_players_global_dict, competition_phase=f"{competition_phase} Leg 1")
    leg2_t2_g, leg2_t1_g = simulate_match(team2_data, team1_data, all_players_global_dict, competition_phase=f"{competition_phase} Leg 2")
    
    total_t1_goals = leg1_t1_g + leg2_t1_g
    total_t2_goals = leg1_t2_g + leg2_t2_g

    if total_t1_goals == total_t2_goals:
        # Away goals rule (simplified: if still tied, random choice)
        # For a proper away goals rule, you'd compare leg1_t2_g (away goals for team2 in leg1) vs leg2_t1_g (away goals for team1 in leg2)
        # This is a simplification.
        winner_id = random.choice([team1_id, team2_id]) # Placeholder for tie-breaking
    else:
        winner_id = team1_id if total_t1_goals > total_t2_goals else team2_id
    return winner_id

def run_knockout_phase(league_table_sorted, sim_teams_by_id_lookup, league_phase_stats_dict, all_players_global_dict, competition_name="UCL"):
    print(f"DEBUG: Entered run_knockout_phase for {competition_name}")
    if not league_table_sorted:
        print("CRITICAL: Knockout phase cannot start without a league table.")
        return None, [], [], [], [], [], [] # Match return tuple structure

    # Determine qualifiers based on league table positions (e.g., top 8 advance directly, 9-24 to playoffs)
    # This is a simplified progression based on the new UCL format ideas.
    num_teams_total = len(league_table_sorted)
    if num_teams_total == 0: return None, [], [], [], [], [], []

    # Teams ranked 1-8 go directly to Round of 16
    direct_to_round_of_16_ids = [team_id for team_id, stats in league_table_sorted[:8]]
    print(f"DEBUG: Direct to R16: {len(direct_to_round_of_16_ids)} teams")

    # Teams ranked 9-24 go to Knockout Playoff Round
    playoff_round_contenders_ids = [team_id for team_id, stats in league_table_sorted[8:24]]
    print(f"DEBUG: Playoff Round Contenders: {len(playoff_round_contenders_ids)} teams")

    # Teams ranked 25-36 are eliminated (or go to UEL group stage - not handled here)
    # Teams ranked 17-24 from UEL group stage would also join UEL KO Playoff (not handled here)

    playoff_round_winners = []
    teams_to_uel_ko_playoff = [] # Placeholder for teams dropping to UEL

    if len(playoff_round_contenders_ids) >= 2: # Need at least 2 teams for a playoff match
        # Pair them up (e.g., 9 vs 24, 10 vs 23, etc. or random)
        # Simplified: just pair them sequentially for now if even number
        num_playoff_pairs = len(playoff_round_contenders_ids) // 2
        playoff_pairs = []
        # A more structured pairing would be 9v24, 10v23, etc.
        # For simplicity, taking first half vs second half if sorted 9 to 24.
        # This requires careful indexing if playoff_round_contenders_ids is already sorted 9 to 24.
        for i in range(num_playoff_pairs):
            # Example pairing: 9th vs 16th (from this playoff pool), 10th vs 15th, etc.
            # Or more simply, if sorted by rank: team_ranked_9 vs team_ranked_24, team_ranked_10 vs team_ranked_23
            # This requires careful indexing if playoff_round_contenders_ids is already sorted 9 to 24.
            if i < len(playoff_round_contenders_ids) - 1 - i: # Ensure we don't cross middle for odd lists / self-pair
                 playoff_pairs.append((playoff_round_contenders_ids[i], playoff_round_contenders_ids[len(playoff_round_contenders_ids)-1-i]))
            else: break # Stop if middle is reached

        print(f"DEBUG: Playoff Round Pairs ({len(playoff_pairs)}): {playoff_pairs}")
        for team1_id, team2_id in playoff_pairs:
            winner_id = simulate_knockout_tie(team1_id, team2_id, sim_teams_by_id_lookup, all_players_global_dict, competition_phase=f"{competition_name} Playoff Round")
            playoff_round_winners.append(winner_id)
            # Losers of these playoffs might go to UEL (not implemented here)
    else:
        print("DEBUG: Not enough contenders for playoff round.")

    # Round of 16: Direct qualifiers + Playoff winners
    round_of_16_participants_ids = direct_to_round_of_16_ids + playoff_round_winners
    if len(round_of_16_participants_ids) != 16:
        print(f"WARNING: Number of R16 participants is {len(round_of_16_participants_ids)}, not 16. Knockout draw might be uneven.")
        # Pad or truncate if necessary, or handle error. For now, proceed if possible.
    
    random.shuffle(round_of_16_participants_ids) # Shuffle for R16 draw
    round_of_16_winners = []
    if len(round_of_16_participants_ids) >= 2:
        num_r16_pairs = len(round_of_16_participants_ids) // 2
        for i in range(num_r16_pairs):
            team1_id = round_of_16_participants_ids[i*2]
            team2_id = round_of_16_participants_ids[i*2+1]
            winner_id = simulate_knockout_tie(team1_id, team2_id, sim_teams_by_id_lookup, all_players_global_dict, competition_phase=f"{competition_name} Round of 16")
            round_of_16_winners.append(winner_id)
    else:
        print("DEBUG: Not enough participants for Round of 16.")

    # Quarter-Finals
    quarter_finalists_ids = round_of_16_winners
    random.shuffle(quarter_finalists_ids)
    quarter_final_winners = []
    if len(quarter_finalists_ids) >= 2:
        num_qf_pairs = len(quarter_finalists_ids) // 2
        for i in range(num_qf_pairs):
            team1_id = quarter_finalists_ids[i*2]
            team2_id = quarter_finalists_ids[i*2+1]
            winner_id = simulate_knockout_tie(team1_id, team2_id, sim_teams_by_id_lookup, all_players_global_dict, competition_phase=f"{competition_name} Quarter-Final")
            quarter_final_winners.append(winner_id)
    else:
        print("DEBUG: Not enough participants for Quarter-Finals.")

    # Semi-Finals
    semi_finalists_ids = quarter_final_winners
    random.shuffle(semi_finalists_ids)
    semi_final_winners = []
    if len(semi_finalists_ids) >= 2:
        num_sf_pairs = len(semi_finalists_ids) // 2
        for i in range(num_sf_pairs):
            team1_id = semi_finalists_ids[i*2]
            team2_id = semi_finalists_ids[i*2+1]
            winner_id = simulate_knockout_tie(team1_id, team2_id, sim_teams_by_id_lookup, all_players_global_dict, competition_phase=f"{competition_name} Semi-Final")
            semi_final_winners.append(winner_id)
    else:
        print("DEBUG: Not enough participants for Semi-Finals.")

    # Final
    finalists_ids = semi_final_winners
    final_winner_id = None
    if len(finalists_ids) == 2:
        final_winner_id = simulate_knockout_tie(finalists_ids[0], finalists_ids[1], sim_teams_by_id_lookup, all_players_global_dict, neutral_venue=True, competition_phase=f"{competition_name} Final")
    elif len(finalists_ids) == 1: # Should not happen in a balanced bracket
        print(f"WARNING: Only one finalist {finalists_ids[0]}. Declaring winner by default.")
        final_winner_id = finalists_ids[0]
    else:
        print("CRITICAL: No finalists for the final match.")

    print(f"DEBUG: Exiting run_knockout_phase for {competition_name}")
    return (
        final_winner_id, 
        finalists_ids, 
        semi_finalists_ids, 
        quarter_finalists_ids, 
        round_of_16_participants_ids, # Changed from round_of_16_ids to actual participants
        playoff_round_winners, # Changed from playoff_qualifiers_ids
        teams_to_uel_ko_playoff # This remains a placeholder
    )

# --- Utility functions for printing results ---
def print_league_table(sorted_league_table_items, teams_by_id_lookup, league_stats_raw_dict):
    print_header("UCL League Phase Final Table")
    if not sorted_league_table_items:
        print("No league table data to display.")
        return

    print("""
----------------------------------------------------------------------------------------------------
| Pos | Team Name                     | Country   | P | W | D | L | GF | GA | GD | Pts |
----------------------------------------------------------------------------------------------------""")

    for i, (team_id, stats) in enumerate(sorted_league_table_items):
        team_name = stats.get('name', teams_by_id_lookup.get(team_id, {}).get('name', team_id))
        country = stats.get('country', teams_by_id_lookup.get(team_id, {}).get('country', 'N/A'))

        print(f"| {i+1:<3} | {team_name:<29} | {country:<9} | {stats['P']:<1} | {stats['W']:<1} | {stats['D']:<1} | {stats['L']:<1} | {stats['GF']:<2} | {stats['GA']:<2} | {stats['GD']:<2} | {stats['Pts']:<3} |")
    print("----------------------------------------------------------------------------------------------------\n") # Removed one backslash

def print_knockout_results(
    winner_id, finalists, semi_finalists, quarter_finalists, 
    r16_participants, playoff_winners, uel_teams, 
    teams_by_id_lookup):
    
    print_header("UCL Knockout Stage Results")

    def get_team_name(tid):
        return teams_by_id_lookup.get(tid, {}).get('name', str(tid)) if tid else "N/A"

    if playoff_winners:
        print_subheader("Knockout Playoff Winners")
        for team_id in playoff_winners: print(f"- {get_team_name(team_id)}")
        print("\n") # Removed one backslash
        
    if r16_participants:
        print_subheader("Round of 16 Participants")
        print(f"({len(r16_participants)} teams reached the Round of 16)")
        print("\n") # Removed one backslash

    if quarter_finalists:
        print_subheader("Quarter-Finalists (R16 Winners)")
        for team_id in quarter_finalists: print(f"- {get_team_name(team_id)}")
        print("\n") # Removed one backslash

    if semi_finalists:
        print_subheader("Semi-Finalists (QF Winners)")
        for team_id in semi_finalists: print(f"- {get_team_name(team_id)}")
        print("\n") # Removed one backslash

    if finalists:
        print_subheader("Finalists (SF Winners)")
        if len(finalists) == 2:
            print(f"- {get_team_name(finalists[0])} vs {get_team_name(finalists[1])}")
        elif finalists:
            print(f"- {get_team_name(finalists[0])}")
        print("\n") # Removed one backslash
    
    if winner_id:
        print_subheader("UCL Winner")
        print(f"*** {get_team_name(winner_id).upper()} ***")
    else:
        print_subheader("UCL Winner")
        print("To be determined / No winner from simulation.")
    print("\n") # Removed one backslash
# --- End Utility functions for printing results ---


def run_final_ucl_simulation():
    print("DEBUG: --- Starting run_final_ucl_simulation ---")

    print("DEBUG: Loading LEAGUES_FILE...")
    leagues_data_from_file = load_json_data(LEAGUES_FILE)
    if not isinstance(leagues_data_from_file, dict) or not leagues_data_from_file:
        print(f"CRITICAL: {LEAGUES_FILE} issue. Aborting.")
        return
    print("DEBUG: LEAGUES_FILE loaded.")

    print("DEBUG: Loading MANAGERS_FILE (as a list)...")
    managers_list_input = load_json_data(MANAGERS_FILE, schema_type="list") # Load as list
    if not managers_list_input: # Allow empty list if file is empty but valid JSON list
        print(f"Warning: Could not load data from {MANAGERS_FILE} or it's an empty list.")
        managers_list_input = [] 
    # Process the list into a dictionary using the modified load_all_manager_data
    all_managers_data_dict = load_all_manager_data(managers_list_input)
    if not all_managers_data_dict:
         print(f"CRITICAL: Processing managers from {MANAGERS_FILE} resulted in no manager data. Aborting.")
         return
    print(f"DEBUG: MANAGERS_FILE processed into dictionary with {len(all_managers_data_dict)} managers.")


    print("DEBUG: Loading PLAYING_STYLES_FILE (as a list)...")
    playing_styles_list = load_json_data(PLAYING_STYLES_FILE, schema_type="list")
    if not playing_styles_list:
        print(f"CRITICAL: Could not load data from {PLAYING_STYLES_FILE}. Aborting.")
        return
    playing_styles_data = {style['id']: style for style in playing_styles_list if isinstance(style, dict) and 'id' in style}
    if len(playing_styles_data) != len(playing_styles_list):
        print(f"Warning: Some playing styles were filtered out during conversion to dict (missing 'id' or not a dict). Original count: {len(playing_styles_list)}, Dict count: {len(playing_styles_data)}")
    if not playing_styles_data:
        print(f"CRITICAL: No valid playing styles loaded into dictionary from {PLAYING_STYLES_FILE}. Aborting.")
        return
    print(f"DEBUG: PLAYING_STYLES_FILE loaded and converted to dict with {len(playing_styles_data)} entries.")

    print("DEBUG: Loading TRAITS_FILE (as a list)...")
    traits_list = load_json_data(TRAITS_FILE, schema_type="list")
    if not traits_list:
        print(f"CRITICAL: Could not load data from {TRAITS_FILE}. Aborting.")
        return
    traits_data = {trait['id']: trait for trait in traits_list if isinstance(trait, dict) and 'id' in trait}
    if len(traits_data) != len(traits_list):
        print(f"Warning: Some traits were filtered out during conversion to dict (missing 'id' or not a dict). Original count: {len(traits_list)}, Dict count: {len(traits_data)}")
    if not traits_data:
        print(f"CRITICAL: No valid traits loaded into dictionary from {TRAITS_FILE}. Aborting.")
        return
    print(f"DEBUG: TRAITS_FILE loaded and converted to dict with {len(traits_data)} entries.")

    print("DEBUG: Loading PLAYER_DATA (from league/club specific files)...")
    # all_players_global_dict will be {player_id: player_data_dict}
    # player_team_links will be {club_id_from_filename: [player_id1, player_id2, ...]}
    all_players_global_dict, player_team_links = load_player_data(BASE_DATA_PATH) # Pass BASE_DATA_PATH
    if not all_players_global_dict:
        print(f"CRITICAL: Could not load player data (all_players_global_dict is empty/None). Aborting.")
        return
    # player_team_links might be empty if no files found, handle downstream.
    print(f"DEBUG: PLAYER_DATA loaded. {len(all_players_global_dict)} unique players, {len(player_team_links)} clubs with player links found.")

    print("DEBUG: Loading all club files and embedding players...")
    # load_all_club_data now takes all_players_global_dict and player_team_links
    # It will use CLUBS_DIR (e.g., data/leagues_clubs/) for base club metadata
    # and then embed players from all_players_global_dict using player_team_links.
    all_clubs_from_files = load_all_club_data(CLUBS_DIR, 
                                              leagues_data_from_file.get('leagues', []), 
                                              all_players_global_dict, 
                                              player_team_links)
    if not all_clubs_from_files:
        print("CRITICAL: No club data loaded from files (all_clubs_from_files is empty). Aborting.")
        return
    print(f"DEBUG: Loaded and processed data for {len(all_clubs_from_files)} clubs from files (players embedded).")


    print("DEBUG: Initializing base league/club structures (sim_teams_by_id_lookup from all clubs)...")
    # initialize_all_leagues_and_clubs now receives all_clubs_from_files (with players embedded)
    # and all_managers_data_dict (the processed dictionary of managers)
    player_team_links = None # No longer needed, players are embedded
    _all_clubs_ref, _teams_by_league_ref, initial_sim_teams_by_id_lookup, _league_details_ref, _initial_league_stats_lookup = initialize_all_leagues_and_clubs(
        leagues_data_from_file, 
        all_managers_data_dict, # Pass the processed manager dictionary
        playing_styles_data,    # Pass the processed playing styles dictionary
        all_clubs_from_files,   # Pass clubs with embedded players
        player_team_links       # This might still be useful if initialize_all_leagues_and_clubs uses it for some cross-referencing
                                # or can be removed if players are fully self-contained in all_clubs_from_files
    )
    if not initial_sim_teams_by_id_lookup:
        print("CRITICAL: Initialization of initial_sim_teams_by_id_lookup failed. Aborting.")
        return
    print(f"DEBUG: initial_sim_teams_by_id_lookup initialized with {len(initial_sim_teams_by_id_lookup)} teams (raw club data with players).")

    # Select teams for UCL based on initial_sim_teams_by_id_lookup (raw club data)
    ucl_raw_team_data_list = []
    # ... (rest of the ucl team selection logic using initial_sim_teams_by_id_lookup)
    # This part should now use get_ucl_qualified_teams which expects all_clubs (like initial_sim_teams_by_id_lookup)
    # and all_managers (like all_managers_data_dict)
    print("INFO: Qualifying UCL teams...")
    ucl_raw_team_data_list = get_ucl_qualified_teams(
        leagues_data_from_file, 
        initial_sim_teams_by_id_lookup, # This is effectively all_clubs with players embedded
        all_managers_data_dict
    )


    if not ucl_raw_team_data_list:
        print("CRITICAL: No teams selected/qualified for UCL league phase. Aborting.")
        return
    if len(ucl_raw_team_data_list) < 2:
        print(f"CRITICAL: Only {len(ucl_raw_team_data_list)} team(s) for league phase. Need at least 2. Aborting.")
        return
    print(f"DEBUG: {len(ucl_raw_team_data_list)} teams raw data prepared for UCL.")

    print("DEBUG: Setting up simulation-specific team and player data...")
    # ucl_raw_team_data_list is a list of team dicts, where each team has 'players' list (raw player dicts)
    sim_teams_list_for_model, all_players_for_model = setup_simulation_data(ucl_raw_team_data_list)
    
    if not sim_teams_list_for_model:
        print("CRITICAL: setup_simulation_data resulted in no simulation-ready teams. Aborting.")
        return
    if not all_players_for_model:
        print("CRITICAL: setup_simulation_data resulted in no simulation-ready players. Aborting.")
        return
    print(f"DEBUG: {len(sim_teams_list_for_model)} teams and {len(all_players_for_model)} players prepared for simulation.")

    sim_teams_by_id_lookup_for_sim = {team['id']: team for team in sim_teams_list_for_model}

    print("DEBUG: Generating league phase fixtures...")
    league_phase_fixtures = generate_league_phase_fixtures(sim_teams_list_for_model)
    if not league_phase_fixtures:
        print("CRITICAL: No fixtures generated for league phase. Aborting.")
        return
    print(f"DEBUG: Generated {len(league_phase_fixtures)} fixtures.")

    print("DEBUG: Running league phase simulation...")
    final_league_table_sorted_items, league_phase_raw_stats_dict, _used_fixtures = run_league_phase(
        sim_teams_list_for_model, 
        league_phase_fixtures,
        all_players_for_model
    )
    print("DEBUG: League phase simulation completed.")
    if not final_league_table_sorted_items:
        print("CRITICAL: League phase simulation did not produce a league table. Aborting.")
        return

    print_league_table(final_league_table_sorted_items, sim_teams_by_id_lookup_for_sim, league_phase_raw_stats_dict)
    
    print("DEBUG: Running knockout phase...")
    (
        final_winner_id, finalists_ids, semi_finalists_ids, quarter_finalists_ids,
        round_of_16_ids, playoff_winners_ids, uel_knockout_playoff_teams_ids
    ) = run_knockout_phase(
        final_league_table_sorted_items,
        sim_teams_by_id_lookup_for_sim,
        league_phase_raw_stats_dict, 
        all_players_for_model,
        competition_name="UCL Final Stages"
    )
    print("DEBUG: Knockout phase completed.")

    print_knockout_results(
        final_winner_id, finalists_ids, semi_finalists_ids, quarter_finalists_ids, 
        round_of_16_ids, playoff_winners_ids, uel_knockout_playoff_teams_ids, 
        sim_teams_by_id_lookup_for_sim
    )
    print("DEBUG: --- run_final_ucl_simulation finished ---")


if __name__ == "__main__":
    print("DEBUG: Script execution started.")
    start_time = datetime.now()
    print(f"UCL Swiss Model Simulation started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # The global load_all_club_data is used. No need for a local definition here.
    # Calls to load data are inside run_final_ucl_simulation.
    
    run_final_ucl_simulation()
    
    end_time = datetime.now()
    print(f"UCL Swiss Model Simulation finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total execution time: {end_time - start_time}")
    print("DEBUG: Script execution ended.")
