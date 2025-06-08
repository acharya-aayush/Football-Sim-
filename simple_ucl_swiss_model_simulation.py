#!/usr/bin/env python3
"""
Simple UCL Season Simulator (New Swiss Model) with Player Stats
"""
import random
import json
from collections import defaultdict
import uuid # Added for unique player IDs

# --- Formation Templates ---
FORMATIONS = {
    '4-3-3': {'GK': 1, 'DEF': 4, 'MID': 3, 'FWD': 3},
    '4-2-3-1': {'GK': 1, 'DEF': 4, 'MID': 5, 'FWD': 1},
    '3-5-2': {'GK': 1, 'DEF': 3, 'MID': 5, 'FWD': 2},
    '4-4-2': {'GK': 1, 'DEF': 4, 'MID': 4, 'FWD': 2},
    '3-4-3': {'GK': 1, 'DEF': 3, 'MID': 4, 'FWD': 3},
    '4-1-4-1': {'GK': 1, 'DEF': 4, 'MID': 5, 'FWD': 1},
    '5-3-2': {'GK': 1, 'DEF': 5, 'MID': 3, 'FWD': 2}
}

DEFAULT_FORMATION = '4-3-3'

# --- Configuration ---
PREDEFINED_UCL_TEAMS = {
    'ENG': ['Manchester City', 'Liverpool', 'Arsenal', 'Aston Villa'],
    'GER': ['Bayer Leverkusen', 'Bayern Munich', 'Borussia Dortmund', 'RB Leipzig'],
    'ESP': ['Real Madrid', 'Barcelona', 'Real Sociedad', 'Atletico Madrid'],
    'ITA': ['Inter Milan', 'AC Milan', 'Napoli', 'Juventus'],
    'FRA': ['Paris Saint-Germain', 'Lyon', 'OGC Nice', 'AS Monaco']
}
ALL_COUNTRIES_FOR_PLACEHOLDERS = ['POR', 'NED', 'BEL', 'SCO', 'AUT', 'TUR', 'SUI', 'UKR', 'RUS', 'GRE', 'DEN', 'CRO', 'CZE', 'NOR', 'SWE']

PLAYER_POSITIONS_ALLOCATION = {'GK': 3, 'DEF': 7, 'MID': 7, 'FWD': 6} # Squad composition for 23 players
TOTAL_PLAYERS_PER_TEAM = sum(PLAYER_POSITIONS_ALLOCATION.values()) # Should be 23

# --- Helper Functions ---
def generate_club_id(name):
    return "club_" + name.lower().replace(" ", "_").replace("-", "_")

def generate_player_id():
    return f"player_{uuid.uuid4()}"

def create_player(team_id, team_club_name, player_idx_in_team, position, base_skill_range=(55,85)):
    player_id = generate_player_id()
    # Simplified name generation
    player_name = f"{position.upper()}{player_idx_in_team}_{team_club_name[:3].upper()}"
    return {
        'id': player_id,
        'name': player_name,
        'team_id': team_id,
        'team_name': team_club_name,
        'position': position,
        'skill': random.randint(*base_skill_range),
        'goals': 0,
        'assists': 0,
        'matches_played': 0,
        'total_rating_points': 0.0,
        'clean_sheets': 0,
        'avg_rating': 0.0
    }

def load_players_from_json(team_name):
    """Load players for a given team from JSON file."""
    # Try multiple potential file paths based on the team name
    possible_paths = [
        f'data/league_ucl_clubs_players/{team_name.lower().replace(" ", "_")}_players.json',
        f'data/00_1_clubs_players/club_{team_name.lower().replace(" ", "_")}_players.json',
        f'data/00_2_clubs_players/club_{team_name.lower().replace(" ", "_")}_players.json',
        f'data/00_3_clubs_players/club_{team_name.lower().replace(" ", "_")}_players.json',
        f'data/00_4_clubs_players/club_{team_name.lower().replace(" ", "_")}_players.json',
        f'data/00_5_clubs_players/club_{team_name.lower().replace(" ", "_")}_players.json',
        f'data/00_12_clubs_players/club_{team_name.lower().replace(" ", "_")}_players.json',
        f'data/00_11_clubs_players/club_{team_name.lower().replace(" ", "_")}_players.json'
    ]
    
    for file_path in possible_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                players_data = json.load(f)
                print(f"Successfully loaded {len(players_data)} players for {team_name} from {file_path}")
                return convert_players_to_simulation_format(players_data, team_name)
        except FileNotFoundError:
            continue
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for {team_name} at {file_path}: {e}")
            continue
    
    print(f"No player file found for {team_name} in any expected location")
    return []

def convert_players_to_simulation_format(players_data, team_name):
    """Convert real player data to simulation format."""
    converted_players = []
    team_id = generate_club_id(team_name)
    
    for player_data in players_data:
        # Extract primary position
        primary_positions = player_data.get('positions_primary', ['MID'])
        position = primary_positions[0] if primary_positions else 'MID'
        
        # Convert position format if needed
        if position == 'GK':
            sim_position = 'GK'
        elif position in ['CB', 'LB', 'RB', 'LWB', 'RWB', 'DF']:
            sim_position = 'DEF'
        elif position in ['CM', 'CDM', 'CAM', 'LM', 'RM', 'MF']:
            sim_position = 'MID'
        elif position in ['ST', 'CF', 'LW', 'RW', 'FW']:
            sim_position = 'FWD'
        else:
            sim_position = 'MID'  # Default fallback
        
        # Calculate skill from technical attributes (simplified)
        technical_attrs = player_data.get('technical_attributes', {})
        if technical_attrs:
            # Average key technical attributes
            key_attrs = ['finishing', 'passing', 'dribbling', 'ball_control', 'crossing']
            total_skill = 0
            attr_count = 0
            for attr in key_attrs:
                if attr in technical_attrs:
                    total_skill += technical_attrs[attr]
                    attr_count += 1
            skill = int(total_skill / attr_count) if attr_count > 0 else 70
        else:
            # Fallback based on market value or wage
            market_value = player_data.get('market_value_eur', 1000000)
            if market_value > 50000000:
                skill = random.randint(85, 95)
            elif market_value > 20000000:
                skill = random.randint(75, 85)
            elif market_value > 5000000:
                skill = random.randint(65, 80)
            else:
                skill = random.randint(55, 70)
        
        converted_player = {
            'id': player_data.get('id', generate_player_id()),
            'name': player_data.get('known_as', player_data.get('full_name', 'Unknown Player')),
            'team_id': team_id,
            'team_name': team_name,
            'position': sim_position,
            'skill': max(40, min(99, skill)),  # Clamp between 40-99
            'goals': 0,
            'assists': 0,
            'matches_played': 0,
            'total_rating_points': 0.0,
            'clean_sheets': 0,
            'avg_rating': 0.0,
            'real_data': True  # Flag to indicate this is real player data
        }
        converted_players.append(converted_player)
    
    return converted_players

def load_manager_data(team_name):
    """Load manager data for a given team."""    # Try multiple league manager files
    possible_manager_files = [
        'data/managers/25.json',  # UCL managers
        'data/managers/1.json',   # EPL managers
        'data/managers/2.json',   # LaLiga managers
        'data/managers/3.json',   # Bundesliga managers
        'data/managers/4.json',   # Serie A managers
        'data/managers/5.json',   # Ligue 1 managers
        'data/managers/11.json',  # Primeira Liga managers
        'data/managers/12.json'   # Eredivisie managers
    ]
    
    target_club_id = generate_club_id(team_name)
    
    for file_path in possible_manager_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both direct list and nested structure
                managers = data if isinstance(data, list) else data.get('managers', [])
                
                for manager in managers:
                    if manager.get('current_club_id') == target_club_id:
                        print(f"Found manager {manager.get('name', 'Unknown')} for {team_name}")
                        return manager
        except FileNotFoundError:
            continue
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for managers in {file_path}: {e}")
            continue
    
    print(f"Manager not found for {team_name} (club_id: {target_club_id})")
    return None

def setup_teams_and_players():
    """Sets up the 36 UCL teams and their players for the simulation."""
    teams = []
    all_teams_flat_players = {} # Central player registry: {player_id: player_object}
    team_names_added = set()

    # 1. Add predefined teams
    for country_code, club_list in PREDEFINED_UCL_TEAMS.items():
        for club_name in club_list:
            if club_name not in team_names_added:
                team_id = generate_club_id(club_name)
                players = load_players_from_json(club_name)
                if not players:
                    # Generate placeholder players if no real data is available
                    players = [
                        create_player(team_id, club_name, idx, position, 
                                       base_skill_range=(random.randint(65, 75), random.randint(80, 95)) # Skill relative to team rep
                                      )
                        for position, count in PLAYER_POSITIONS_ALLOCATION.items()
                        for idx in range(1, count + 1)
                    ]
                manager = load_manager_data(club_name)
                teams.append({
                    'id': team_id,
                    'name': club_name,
                    'country': country_code,
                    'reputation': random.randint(80, 95),
                    'pot': 0,
                    'player_ids': [player['id'] for player in players],
                    'manager': manager
                })
                for player in players:
                    all_teams_flat_players[player['id']] = player
                team_names_added.add(club_name)

    # 2. Add more teams to reach 36
    other_leagues_potential_qualifiers = {
        'POR': ['FC Porto', 'Benfica', 'Sporting CP'],
        'NED': ['Ajax', 'PSV Eindhoven', 'Feyenoord'],
        'BEL': ['Club Brugge'], 'SCO': ['Celtic', 'Rangers'],
        'AUT': ['Red Bull Salzburg'], 'TUR': ['Galatasaray', 'Fenerbahce'],
    }
    candidate_teams_data = []
    for country, clubs in other_leagues_potential_qualifiers.items():
        for club_name in clubs:
            if club_name not in team_names_added:
                team_id = generate_club_id(club_name)
                candidate_teams_data.append({
                    'id': team_id,
                    'name': club_name,
                    'country': country,
                    'reputation': random.randint(70, 85),
                    'pot': 0,
                    'player_ids': []
                })
    
    random.shuffle(candidate_teams_data)
    for team_data in candidate_teams_data:
        if len(teams) < 36 and team_data['name'] not in team_names_added:
            # Load real players for these teams too
            club_name = team_data['name']
            team_id = team_data['id']
            players = load_players_from_json(club_name)
            if not players:
                # Generate placeholder players if no real data is available
                players = [
                    create_player(team_id, club_name, idx, position, 
                                   base_skill_range=(team_data['reputation']-15, team_data['reputation']+5)
                                  )
                    for position, count in PLAYER_POSITIONS_ALLOCATION.items()
                    for idx in range(1, count + 1)
                ]
            manager = load_manager_data(club_name)
            team_data['player_ids'] = [player['id'] for player in players]
            team_data['manager'] = manager
            
            # Add players to central registry
            for player in players:
                all_teams_flat_players[player['id']] = player
            
            teams.append(team_data)
            team_names_added.add(team_data['name'])
        if len(teams) == 36:
            break
    
    # 3. Fill remaining slots with generic teams
    generic_country_idx = 0
    while len(teams) < 36:
        country = ALL_COUNTRIES_FOR_PLACEHOLDERS[generic_country_idx % len(ALL_COUNTRIES_FOR_PLACEHOLDERS)]
        team_name = f"{country} Challenger {len(teams) - sum(len(v) for v in PREDEFINED_UCL_TEAMS.values()) + 1}"
        if team_name not in team_names_added:
            team_id = generate_club_id(team_name)
            # Try to load real players for generic teams too
            players = load_players_from_json(team_name)
            if not players:
                # Generate players for generic teams
                players = [
                    create_player(team_id, team_name, idx, position, 
                                   base_skill_range=(60, 75) # Lower skill for generic teams
                                  )
                    for position, count in PLAYER_POSITIONS_ALLOCATION.items()
                    for idx in range(1, count + 1)
                ]
            manager = load_manager_data(team_name)
            teams.append({
                'id': team_id,
                'name': team_name,
                'country': country,
                'reputation': random.randint(65, 75),
                'pot': 0,
                'player_ids': [player['id'] for player in players],
                'manager': manager
            })
            # Add players to central registry
            for player in players:
                all_teams_flat_players[player['id']] = player
            team_names_added.add(team_name)
        generic_country_idx +=1

    # Assign pots
    teams.sort(key=lambda x: x['reputation'], reverse=True)
    for i, team in enumerate(teams):
        if i < 9: team['pot'] = 1
        elif i < 18: team['pot'] = 2
        elif i < 27: team['pot'] = 3
        else: team['pot'] = 4
                
    return teams, all_teams_flat_players

def select_starting_xi(team_player_ids, all_players_data, formation=None):
    """Select starting XI based on formation, prioritizing real players and highest skill."""
    lineup_ids = []
    available_players = [all_players_data[pid] for pid in team_player_ids]
    
    # Use provided formation or default
    if formation is None:
        formation = DEFAULT_FORMATION
    
    positions_needed = FORMATIONS.get(formation, FORMATIONS[DEFAULT_FORMATION])
    
    for pos_code, count_needed in positions_needed.items():
        # Filter players for this position and sort by: 1) Real data flag, 2) Skill
        eligible_for_pos = [p for p in available_players if p['position'] == pos_code and p['id'] not in lineup_ids]
        eligible_for_pos.sort(key=lambda x: (x.get('real_data', False), x['skill']), reverse=True)
        
        selected_count = 0
        for player in eligible_for_pos:
            if selected_count < count_needed:
                lineup_ids.append(player['id'])
                selected_count += 1
            else:
                break
    
    # If lineup is short (e.g. not enough specialized players), fill with best remaining players
    if len(lineup_ids) < 11:
        remaining_available = [p for p in available_players if p['id'] not in lineup_ids]
        # Sort by real data flag first, then skill
        remaining_available.sort(key=lambda x: (x.get('real_data', False), x['skill']), reverse=True)
        fill_count = 11 - len(lineup_ids)
        for player in remaining_available:
            if fill_count <= 0: break
            lineup_ids.append(player['id'])
            fill_count -=1
            
    return lineup_ids[:11] # Ensure exactly 11

def assign_goals_and_assists(num_goals, team_lineup_ids, all_players_data):
    contributions = [] # list of (player_id, 'goal'/'assist')
    if not team_lineup_ids or num_goals == 0:
        return contributions

    lineup_players = [all_players_data[pid] for pid in team_lineup_ids]
    
    for i in range(num_goals):
        # Scorer: FWDs > MIDs > DEFs. GKs don't score in this simple model.
        potential_scorers = [p for p in lineup_players if p['position'] != 'GK']
        if not potential_scorers: continue

        scorer_weights = []
        for p in potential_scorers:
            if p['position'] == 'FWD': scorer_weights.append(p['skill'] * 3)
            elif p['position'] == 'MID': scorer_weights.append(p['skill'] * 2)
            else: scorer_weights.append(p['skill'] * 1) # DEF
        
        if sum(scorer_weights) == 0: scorer_weights = [1] * len(potential_scorers)

        scorer = random.choices(potential_scorers, weights=scorer_weights, k=1)[0]
        all_players_data[scorer['id']]['goals'] += 1
        contributions.append({'player_id': scorer['id'], 'type': 'goal'})

        # Assist (optional, ~65% chance per goal, not by scorer, MIDs > FWDs > DEFs)
        if random.random() < 0.65:
            potential_assisters = [p for p in lineup_players if p['id'] != scorer['id'] and p['position'] != 'GK']
            if not potential_assisters: continue

            assister_weights = []
            for p in potential_assisters:
                if p['position'] == 'MID': assister_weights.append(p['skill'] * 3)
                elif p['position'] == 'FWD': assister_weights.append(p['skill'] * 2)
                else: assister_weights.append(p['skill'] * 1) # DEF
            
            if sum(assister_weights) == 0: assister_weights = [1] * len(potential_assisters)
                
            assister = random.choices(potential_assisters, weights=assister_weights, k=1)[0]
            all_players_data[assister['id']]['assists'] += 1
            contributions.append({'player_id': assister['id'], 'type': 'assist'})
            
    return contributions

def calculate_match_rating(player_id, all_players_data, team_result_char, goals_conceded_by_team, player_contributions_in_match):
    player = all_players_data[player_id]
    rating = 6.0  # Base rating for participation

    p_goals = sum(1 for c in player_contributions_in_match if c['player_id'] == player_id and c['type'] == 'goal')
    p_assists = sum(1 for c in player_contributions_in_match if c['player_id'] == player_id and c['type'] == 'assist')

    if team_result_char == 'W': rating += 0.7
    elif team_result_char == 'D': rating += 0.3
    # No change for L from base

    rating += p_goals * 1.2  # Goal bonus
    rating += p_assists * 0.8 # Assist bonus

    if player['position'] == 'GK':
        if goals_conceded_by_team == 0:
            rating += 1.0  # Clean sheet
            player['clean_sheets'] += 1
        rating -= goals_conceded_by_team * 0.25 # Penalty per goal conceded
    elif player['position'] == 'DEF':
        if goals_conceded_by_team == 0:
            rating += 0.4 # Part of clean sheet defense
        rating -= goals_conceded_by_team * 0.15

    # Skill influence: (skill - 75 (avg skill anchor)) / 50 (divisor to scale impact)
    skill_mod = (player['skill'] - 75) / 50.0 
    rating += skill_mod
    
    rating = max(4.0, min(10.0, round(rating, 1))) # Clamp and round

    player['matches_played'] += 1
    player['total_rating_points'] += rating
    if player['matches_played'] > 0:
        player['avg_rating'] = round(player['total_rating_points'] / player['matches_played'], 2)
        
    return rating

def apply_tournament_stage_bonus(team_ids_to_bonus, bonus_points, all_teams_flat_players, teams_by_id):
    """Applies a bonus to total_rating_points for all players of the given teams."""
    if not isinstance(team_ids_to_bonus, list):
        team_ids_to_bonus = [team_ids_to_bonus]

    for team_id in team_ids_to_bonus:
        team = teams_by_id.get(team_id)
        if not team:
            # print(f"Warning: Team ID {team_id} not found for applying bonus.")
            continue
        
        # print(f"Applying {bonus_points} bonus to players of {team['name']}")
        for player_id in team['player_ids']:
            player = all_teams_flat_players.get(player_id)
            if player and player['matches_played'] > 0: # Only bonus players who participated
                player['total_rating_points'] += bonus_points
                # print(f"  Bonus for {player['name']}. New total points: {player['total_rating_points']}")
            elif player and player['matches_played'] == 0:
                # print(f"  Player {player['name']} did not play, no bonus.")
                pass


def generate_league_phase_fixtures(teams):
    """
    Simplified fixture generation for Swiss model. Aims for 8 unique games per team, 4H/4A.
    Does not strictly enforce pot-based opponent selection for scheduling simplicity here.
    """
    fixtures = []
    team_schedules = {t['id']: {'opponents': set(), 'home_count': 0, 'away_count': 0, 'played_count': 0} for t in teams}
    team_ids = [t['id'] for t in teams]
    
    # Create a list of all teams, shuffle for varied pairing attempts
    
    for _round in range(8): # 8 match "days" or rounds of pairings
        available_teams_for_round = team_ids[:]
        random.shuffle(available_teams_for_round)
        
        round_fixtures_temp = []
        used_in_round = set()

        for i in range(0, len(available_teams_for_round), 2):
            if i + 1 >= len(available_teams_for_round):
                break # Odd number, one team sits out this pairing iteration

            team1_id = available_teams_for_round[i]
            team2_id = available_teams_for_round[i+1]

            if team1_id in used_in_round or team2_id in used_in_round: continue
            if team_schedules[team1_id]['played_count'] >= 8 or team_schedules[team2_id]['played_count'] >= 8: continue
            if team2_id in team_schedules[team1_id]['opponents']: continue # Already played

            # Decide home/away to balance
            team1_can_host = team_schedules[team1_id]['home_count'] < 4
            team2_can_be_away = team_schedules[team2_id]['away_count'] < 4
            team2_can_host = team_schedules[team2_id]['home_count'] < 4
            team1_can_be_away = team_schedules[team1_id]['away_count'] < 4

            home_id, away_id = None, None
            if team1_can_host and team2_can_be_away and (team_schedules[team1_id]['home_count'] <= team_schedules[team2_id]['home_count'] or not (team2_can_host and team1_can_be_away) ):
                home_id, away_id = team1_id, team2_id
            elif team2_can_host and team1_can_be_away:
                home_id, away_id = team2_id, team1_id
            else: # Fallback if perfect balance isn't immediately possible, try to force if counts allow
                if team1_can_host and team2_can_be_away: home_id, away_id = team1_id, team2_id
                elif team2_can_host and team1_can_be_away: home_id, away_id = team2_id, team1_id
                else: continue # Cannot schedule this pair now with H/A balance

            if home_id and away_id:
                round_fixtures_temp.append({'home': home_id, 'away': away_id, 'round': _round + 1})
                team_schedules[home_id]['opponents'].add(away_id)
                team_schedules[away_id]['opponents'].add(home_id)
                team_schedules[home_id]['home_count'] += 1
                team_schedules[away_id]['away_count'] += 1
                team_schedules[home_id]['played_count'] += 1
                team_schedules[away_id]['played_count'] += 1
                used_in_round.add(home_id)
                used_in_round.add(away_id)
        
        fixtures.extend(round_fixtures_temp)

    # Post-check and fill if necessary (very simplified fill)
    for team_id in team_ids:
        while team_schedules[team_id]['played_count'] < 8:
            potential_opponents = [opp_id for opp_id in team_ids if opp_id != team_id and \
                                   opp_id not in team_schedules[team_id]['opponents'] and \
                                   team_schedules[opp_id]['played_count'] < 8]
            if not potential_opponents: break
            opponent_id = random.choice(potential_opponents)

            home_id, away_id = None, None
            if team_schedules[team_id]['home_count'] < 4 and team_schedules[opponent_id]['away_count'] < 4:
                home_id, away_id = team_id, opponent_id
            elif team_schedules[opponent_id]['home_count'] < 4 and team_schedules[team_id]['away_count'] < 4:
                 home_id, away_id = opponent_id, team_id
            else: # if one side is full for home/away, try to make it work if the other isn't
                if team_schedules[team_id]['home_count'] < 4 : home_id, away_id = team_id, opponent_id
                elif team_schedules[opponent_id]['home_count'] < 4 : home_id, away_id = opponent_id, team_id
                else: break # Can't easily assign H/A

            if home_id and away_id:
                fixtures.append({'home': home_id, 'away': away_id, 'round': 99}) # Mark as filled
                team_schedules[home_id]['opponents'].add(away_id)
                team_schedules[away_id]['opponents'].add(home_id)
                if home_id == team_id: team_schedules[home_id]['home_count'] +=1
                else: team_schedules[home_id]['away_count'] +=1
                if away_id == opponent_id : team_schedules[away_id]['away_count'] +=1
                else: team_schedules[away_id]['home_count'] +=1
                team_schedules[home_id]['played_count'] += 1
                team_schedules[away_id]['played_count'] += 1
            else: break # Could not fill

    # Verify counts
    final_fixture_count = 0
    for team_id_check in team_schedules:
        final_fixture_count += team_schedules[team_id_check]['played_count']
        if team_schedules[team_id_check]['played_count'] != 8:
             print(f"Warning: Team {teams.copy().pop(0)['name'] if teams else team_id_check} has {team_schedules[team_id_check]['played_count']} games. (H:{team_schedules[team_id_check]['home_count']}, A:{team_schedules[team_id_check]['away_count']})")
    
    if final_fixture_count / 2 != 144 :
        print(f"Warning: Total unique fixtures {final_fixture_count/2}, expected 144.")
        
    return fixtures


def simulate_match(home_team, away_team, all_teams_flat_players): # MODIFIED
    rep_diff = home_team['reputation'] - away_team['reputation']
    prob_home_win = 0.40 + (rep_diff * 0.012) 
    prob_draw = 0.28 - (abs(rep_diff) * 0.006)
    prob_away_win = 1.0 - prob_home_win - prob_draw
    
    if prob_draw < 0.05: prob_draw = 0.05
    if prob_home_win < 0.05: prob_home_win = 0.05 # Ensure non-negative and minimal chance
    if prob_away_win < 0.05: prob_away_win = 0.05
    
    total_prob = prob_home_win + prob_draw + prob_away_win
    prob_home_win /= total_prob
    prob_draw /= total_prob
    # prob_away_win is 1 - prob_home_win - prob_draw

    rand_val = random.random()
    home_goals, away_goals = 0,0

    if rand_val < prob_home_win:
        home_goals = random.randint(1, 4)
        away_goals = random.randint(0, max(0, home_goals - random.choice([1,1,2]))) # Away scores less often
    elif rand_val < prob_home_win + prob_draw:
        home_goals = random.randint(0, 2) # Draws are lower scoring
        away_goals = home_goals
    else:
        away_goals = random.randint(1, 4)
        home_goals = random.randint(0, max(0, away_goals-random.choice([1,1,2])))

    # --- Player Stats Logic with Formation Awareness ---
    # Get manager formations if available
    home_formation = DEFAULT_FORMATION
    away_formation = DEFAULT_FORMATION
    
    if home_team.get('manager') and home_team['manager'].get('preferred_formation'):
        home_formation = home_team['manager']['preferred_formation']
        
    if away_team.get('manager') and away_team['manager'].get('preferred_formation'):
        away_formation = away_team['manager']['preferred_formation']
    
    home_lineup_ids = select_starting_xi(home_team['player_ids'], all_teams_flat_players, home_formation)
    away_lineup_ids = select_starting_xi(away_team['player_ids'], all_teams_flat_players, away_formation)

    home_contributions = assign_goals_and_assists(home_goals, home_lineup_ids, all_teams_flat_players)
    away_contributions = assign_goals_and_assists(away_goals, away_lineup_ids, all_teams_flat_players)

    home_result_char = 'W' if home_goals > away_goals else ('D' if home_goals == away_goals else 'L')
    away_result_char = 'W' if away_goals > home_goals else ('D' if away_goals == home_goals else 'L')

    match_player_ratings = {} # For potential display or detailed logging

    for player_id in home_lineup_ids:
        rating = calculate_match_rating(player_id, all_teams_flat_players, home_result_char, away_goals, home_contributions)
        match_player_ratings[player_id] = rating
    
    for player_id in away_lineup_ids:
        rating = calculate_match_rating(player_id, all_teams_flat_players, away_result_char, home_goals, away_contributions)
        match_player_ratings[player_id] = rating
        
    # print(f"Match Ratings for {home_team['name']} vs {away_team['name']}: {match_player_ratings}") # Optional: very verbose
    return home_goals, away_goals

def run_league_phase(teams, fixtures, all_teams_flat_players): # MODIFIED
    league_table = {
        team['id']: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0, 'name': team['name'], 'country': team['country']}
        for team in teams
    }
    teams_by_id = {team['id']: team for team in teams}
    fixtures.sort(key=lambda x: x.get('round', 0))

    for fixture_idx, fixture in enumerate(fixtures):
        # if fixture_idx % 20 == 0: print(f"  Simulating league match {fixture_idx+1}/{len(fixtures)}") # Progress
        home_team_id, away_team_id = fixture['home'], fixture['away']
        home_team, away_team = teams_by_id[home_team_id], teams_by_id[away_team_id]
        
        hg, ag = simulate_match(home_team, away_team, all_teams_flat_players) # MODIFIED CALL

        # Update stats
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
        
    return sorted(league_table.items(), key=lambda item: (item[1]['Pts'], item[1]['GD'], item[1]['GF'], item[1]['name']), reverse=True)

def simulate_knockout_tie(team1_id, team2_id, teams_by_id, all_teams_flat_players, neutral_venue=False): # MODIFIED
    team1, team2 = teams_by_id[team1_id], teams_by_id[team2_id]
    if neutral_venue:
        print(f"  Final: {team1['name']} vs {team2['name']}")
        t1_g, t2_g = simulate_match(team1, team2, all_teams_flat_players) # MODIFIED CALL
        if t1_g == t2_g:
            print(f"    Score: {t1_g}-{t2_g}. Penalties...")
            # Penalty shootout doesn't typically update player stats like goals/assists in detail here
            # For simplicity, ratings from the match stand.
            winner = random.choice([team1_id, team2_id]) 
            print(f"    {teams_by_id[winner]['name']} wins on penalties!")
            return winner
        return team1_id if t1_g > t2_g else team2_id

    # Two-legged tie
    print(f"  Tie: {team1['name']} vs {team2['name']}")
    # Leg 1 (team1 home)
    leg1_t1_g, leg1_t2_g = simulate_match(team1, team2, all_teams_flat_players) # MODIFIED CALL
    print(f"    Leg 1: {team1['name']} {leg1_t1_g} - {leg1_t2_g} {team2['name']}")
    # Leg 2 (team2 home)
    leg2_t2_g, leg2_t1_g = simulate_match(team2, team1, all_teams_flat_players) # MODIFIED CALL
    print(f"    Leg 2: {team2['name']} {leg2_t2_g} - {leg2_t1_g} {team1['name']}")
    
    total_t1 = leg1_t1_g + leg2_t1_g
    total_t2 = leg1_t2_g + leg2_t2_g
    print(f"    Aggregate: {team1['name']} {total_t1} - {total_t2} {team2['name']}")

    if total_t1 == total_t2: # Away goals rule is no longer in UCL, direct to pens if aggregate tied (simplified here)
        print("    Aggregate tied! Coin flip winner (simplified for no extra time/pens simulation)...")
        # In a real sim, ET would occur, then pens. ET would be another "match" segment for stats.
        return random.choice([team1_id, team2_id])
    return team1_id if total_t1 > total_t2 else team2_id

def display_player_stats(all_players_data, teams_by_id, min_matches_for_avg_rating=3):
    if not all_players_data:
        print("No player data available to display stats.")
        return

    players_list = list(all_players_data.values())

    print("\n--- Top Scorers ---")
    top_scorers = sorted([p for p in players_list if p['goals'] > 0], key=lambda x: x['goals'], reverse=True)
    for i, p in enumerate(top_scorers[:10]):
        print(f"{i+1}. {p['name']} ({p['team_name']}) - {p['goals']} goals ({p['matches_played']} matches)")

    print("\n--- Top Assisters ---")
    top_assisters = sorted([p for p in players_list if p['assists'] > 0], key=lambda x: x['assists'], reverse=True)
    for i, p in enumerate(top_assisters[:10]):
        print(f"{i+1}. {p['name']} ({p['team_name']}) - {p['assists']} assists ({p['matches_played']} matches)")

    print("\n--- Top Goals + Assists ---")
    players_with_ga = [p for p in players_list if (p['goals'] + p['assists']) > 0]
    top_ga = sorted(players_with_ga, key=lambda x: (x['goals'] + x['assists'], x['goals']), reverse=True)
    for i, p in enumerate(top_ga[:10]):
        print(f"{i+1}. {p['name']} ({p['team_name']}) - {p['goals'] + p['assists']} (G:{p['goals']}, A:{p['assists']}) [{p['matches_played']} matches]")

    print("\n--- Goalkeeper Clean Sheets ---")
    gk_clean_sheets = sorted([p for p in players_list if p['position'] == 'GK' and p['clean_sheets'] > 0], 
                             key=lambda x: x['clean_sheets'], reverse=True)
    for i, p in enumerate(gk_clean_sheets[:5]): # Top 5 GKs
        print(f"{i+1}. {p['name']} ({p['team_name']}) - {p['clean_sheets']} clean sheets ({p['matches_played']} matches)")

    print(f"\n--- Highest Average Match Rating (Min {min_matches_for_avg_rating} Matches) ---")
    # Ensure avg_rating is calculated if not already
    for p_id in all_players_data:
        player = all_players_data[p_id]
        if player['matches_played'] > 0 and player['avg_rating'] == 0.0: # Recalc if missed
             player['avg_rating'] = round(player['total_rating_points'] / player['matches_played'], 2)

    rated_players = sorted([p for p in players_list if p['matches_played'] >= min_matches_for_avg_rating], 
                           key=lambda x: x['avg_rating'], reverse=True)
    for i, p in enumerate(rated_players[:10]):
        print(f"{i+1}. {p['name']} ({p['team_name']}) - {p['avg_rating']:.2f} avg rating ({p['matches_played']} matches)")    # Tournament Best Player (considering total rating points, goals+assists, and match participation)
    print("\n--- Tournament Best Player Analysis ---")
    qualified_players = [p for p in players_list if p['matches_played'] >= min_matches_for_avg_rating]
    
    if qualified_players:
        # Calculate combined score: total_rating_points + bonus for goals/assists
        for player in qualified_players:
            player['tournament_score'] = (
                player['total_rating_points'] + 
                (player['goals'] * 2.0) + 
                (player['assists'] * 1.5) + 
                (player['clean_sheets'] * 1.0 if player['position'] == 'GK' else 0)
            )
        
        best_player = max(qualified_players, key=lambda x: x['tournament_score'])
        
        print(f"*** TOURNAMENT BEST PLAYER: {best_player['name']} ({best_player['team_name']})")
        print(f"   Position: {best_player['position']} | Skill: {best_player['skill']}")
        print(f"   Matches: {best_player['matches_played']} | Avg Rating: {best_player['avg_rating']:.2f}")
        print(f"   Goals: {best_player['goals']} | Assists: {best_player['assists']}")
        if best_player['position'] == 'GK':
            print(f"   Clean Sheets: {best_player['clean_sheets']}")
        print(f"   Tournament Score: {best_player['tournament_score']:.2f}")
        
        if best_player.get('real_data'):
            print("   *** Real Player Data")
    else:
        print("   No players qualified for best player award (minimum matches not met)")    # Tournament Best XI (4-3-3 Formation) - Rating-Based Selection
    print("\n--- Tournament Best XI (4-3-3 Formation) ---")
    display_best_xi(qualified_players)


def display_best_xi(qualified_players):
    """Display the Tournament Best XI in a proper 4-3-3 formation using average ratings."""
    
    # Position mapping for 4-3-3 formation with flexible assignments
    formation_positions = {
        'GK': {'count': 1, 'name': 'Goalkeeper'},
        'RB': {'count': 1, 'name': 'Right-Back'},
        'CB1': {'count': 1, 'name': 'Centre-Back'},
        'CB2': {'count': 1, 'name': 'Centre-Back'},
        'LB': {'count': 1, 'name': 'Left-Back'},
        'CM1': {'count': 1, 'name': 'Centre Midfielder'},
        'CM2': {'count': 1, 'name': 'Centre Midfielder'},
        'CM3': {'count': 1, 'name': 'Centre Midfielder'},
        'RW': {'count': 1, 'name': 'Right Winger'},
        'ST': {'count': 1, 'name': 'Striker'},
        'LW': {'count': 1, 'name': 'Left Winger'}
    }
    
    # Position eligibility mapping with rating penalties for secondary positions
    position_eligibility = {
        'GK': {
            'GK': {'primary': True, 'penalty': 0.0}
        },
        'RB': {
            'DEF': {'primary': True, 'penalty': 0.0},
            'MID': {'primary': False, 'penalty': 0.15}  # Wing-backs/defensive mids
        },
        'CB1': {
            'DEF': {'primary': True, 'penalty': 0.0},
            'MID': {'primary': False, 'penalty': 0.20}  # Defensive midfielders only
        },
        'CB2': {
            'DEF': {'primary': True, 'penalty': 0.0},
            'MID': {'primary': False, 'penalty': 0.20}  # Defensive midfielders only
        },
        'LB': {
            'DEF': {'primary': True, 'penalty': 0.0},
            'MID': {'primary': False, 'penalty': 0.15}  # Wing-backs/defensive mids
        },
        'CM1': {
            'MID': {'primary': True, 'penalty': 0.0},
            'DEF': {'primary': False, 'penalty': 0.25},  # Defensive mids to CB
            'FWD': {'primary': False, 'penalty': 0.15}   # Attacking mids/false 9s
        },
        'CM2': {
            'MID': {'primary': True, 'penalty': 0.0},
            'DEF': {'primary': False, 'penalty': 0.25},
            'FWD': {'primary': False, 'penalty': 0.15}
        },
        'CM3': {
            'MID': {'primary': True, 'penalty': 0.0},
            'DEF': {'primary': False, 'penalty': 0.25},
            'FWD': {'primary': False, 'penalty': 0.15}
        },
        'RW': {
            'FWD': {'primary': True, 'penalty': 0.0},
            'MID': {'primary': False, 'penalty': 0.10}   # Wing midfielders
        },
        'ST': {
            'FWD': {'primary': True, 'penalty': 0.0},
            'MID': {'primary': False, 'penalty': 0.20}   # Attacking midfielders
        },
        'LW': {
            'FWD': {'primary': True, 'penalty': 0.0},
            'MID': {'primary': False, 'penalty': 0.10}   # Wing midfielders
        }
    }
    
    selected_best_xi = {}
    used_player_ids = set()
    
    # Selection order prioritizes harder-to-fill positions
    selection_order = ['GK', 'CB1', 'CB2', 'RB', 'LB', 'CM1', 'CM2', 'CM3', 'ST', 'RW', 'LW']
    
    for formation_pos in selection_order:
        eligible_positions = position_eligibility[formation_pos]
        candidates = []
        
        # Find all eligible players for this formation position
        for sim_position, eligibility in eligible_positions.items():
            position_players = [p for p in qualified_players 
                             if p['position'] == sim_position and p['id'] not in used_player_ids]
            
            for player in position_players:
                # Calculate adjusted rating with penalty
                adjusted_rating = player['avg_rating'] * (1 - eligibility['penalty'])
                candidates.append({
                    'player': player,
                    'adjusted_rating': adjusted_rating,
                    'original_rating': player['avg_rating'],
                    'penalty': eligibility['penalty'],
                    'is_primary': eligibility['primary']
                })
        
        # Sort candidates by adjusted rating
        candidates.sort(key=lambda x: x['adjusted_rating'], reverse=True)
        
        if candidates:
            best_candidate = candidates[0]
            selected_best_xi[formation_pos] = best_candidate
            used_player_ids.add(best_candidate['player']['id'])
    
    # Display the Best XI
    if len(selected_best_xi) == 11:
        print("   *** TOURNAMENT BEST XI (4-3-3 Formation) ***")
        print("   Based on Average Match Rating with Positional Flexibility")
        print()
        
        # Display in formation order
        for formation_pos in selection_order:
            if formation_pos in selected_best_xi:
                candidate = selected_best_xi[formation_pos]
                player = candidate['player']
                pos_name = formation_positions[formation_pos]['name']
                
                # Position indicator
                pos_indicator = ""
                if not candidate['is_primary']:
                    pos_indicator = f" (adapted from {player['position']})"
                elif candidate['penalty'] > 0:
                    pos_indicator = f" (secondary role)"
                
                real_tag = " *** Real Player" if player.get('real_data') else ""
                
                print(f"   {pos_name}: {player['name']} ({player['team_name']})")
                print(f"      Rating: {player['avg_rating']:.2f} | Matches: {player['matches_played']} | "
                      f"G+A: {player['goals'] + player['assists']}{pos_indicator}{real_tag}")
        
        # Calculate team average rating
        total_rating = sum(candidate['original_rating'] for candidate in selected_best_xi.values())
        average_rating = total_rating / 11
        print(f"\n   Best XI Average Rating: {average_rating:.2f}")
        
        # Show formation flexibility stats
        adapted_players = sum(1 for c in selected_best_xi.values() if not c['is_primary'])
        if adapted_players > 0:
            print(f"   Positional Adaptations: {adapted_players}/11 players in secondary roles")
    
    else:
        print("   Unable to form complete Best XI - insufficient qualified players")
        print(f"   Selected: {len(selected_best_xi)}/11 positions")


def track_manager_performance(teams, final_table):
    """Track manager performance based on team results."""
    manager_stats = {}
      # Create a lookup for table positions
    table_positions = {team_id: idx + 1 for idx, (team_id, _) in enumerate(final_table)}
    
    for team in teams:
        manager = team.get('manager') or {}
        manager_id = manager.get('id', f"mgr_{team['id']}")
        manager_name = manager.get('name', f"{team['name']} Manager")
        
        # Find team performance in final table
        team_data = None
        for tid, data in final_table:
            if tid == team['id']:
                team_data = data
                break
        
        if team_data:
            manager_stats[manager_id] = {
                'name': manager_name,
                'team_name': team['name'],
                'team_id': team['id'],
                'formation': manager.get('preferred_formation', '4-3-3'),
                'ability': manager.get('manager_ability', 75),
                'points': team_data['Pts'],
                'wins': team_data['W'],
                'draws': team_data['D'],
                'losses': team_data['L'],
                'goals_for': team_data['GF'],
                'goals_against': team_data['GA'],
                'goal_difference': team_data['GD'],
                'table_position': table_positions.get(team['id'], 37),
                'qualified_ko': table_positions.get(team['id'], 37) <= 24,
                'direct_r16': table_positions.get(team['id'], 37) <= 8
            }
    
    return manager_stats

def calculate_manager_score(manager_data):
    """Calculate manager performance score based on various factors."""
    base_score = 0
    
    # Points earned (main factor)
    base_score += manager_data['points'] * 10
    
    # Table position bonus (higher position = lower number = better)
    position_bonus = max(0, 37 - manager_data['table_position']) * 5
    base_score += position_bonus
    
    # Qualification bonuses
    if manager_data['qualified_ko']:
        base_score += 100  # Qualified for knockout stage
    if manager_data['direct_r16']:
        base_score += 150  # Direct to Round of 16
    
    # Goal difference bonus/penalty
    base_score += manager_data['goal_difference'] * 2
    
    # Win percentage bonus
    total_matches = manager_data['wins'] + manager_data['draws'] + manager_data['losses']
    if total_matches > 0:
        win_percentage = manager_data['wins'] / total_matches
        base_score += win_percentage * 50
    
    # Manager ability modifier
    ability_modifier = (manager_data['ability'] - 70) * 2
    base_score += ability_modifier
    
    return max(0, base_score)  # Ensure non-negative score

def display_manager_awards(manager_stats):
    """Display manager awards and rankings."""
    print("\n--- Manager Performance Awards ---")
    
    if not manager_stats:
        print("   No manager data available for awards")
        return
    
    # Calculate scores for all managers
    manager_scores = []
    for manager_id, data in manager_stats.items():
        score = calculate_manager_score(data)
        manager_scores.append((score, data))
      # Sort by score (descending)
    manager_scores.sort(key=lambda x: x[0], reverse=True)
    
    if manager_scores:
        best_score, best_manager = manager_scores[0]
        print(f"*** Manager of the Tournament: {best_manager['name']} ({best_manager['team_name']})")
        print(f"   Formation: {best_manager['formation']}")
        print(f"   Final Position: {best_manager['table_position']}")
        print(f"   Record: {best_manager['wins']}W-{best_manager['draws']}D-{best_manager['losses']}L")
        print(f"   Goals: {best_manager['goals_for']}-{best_manager['goals_against']} (GD: {best_manager['goal_difference']:+d})")
        print(f"   Manager Score: {best_score:.0f}")
        
        if best_manager['qualified_ko']:
            print(f"   QUALIFIED for Knockout Stage")
        if best_manager['direct_r16']:
            print(f"   QUALIFIED for Direct Round of 16")
    
    # Show top 5 managers
    print("\n   Top 5 Managers:")
    for i, (score, manager) in enumerate(manager_scores[:5], 1):
        qualification_status = ""
        if manager['direct_r16']:
            qualification_status = " (Direct R16)"
        elif manager['qualified_ko']:
            qualification_status = " (Playoff)"
        print(f"   {i}. {manager['name']} ({manager['team_name']}) - "
              f"Pos: {manager['table_position']}, Score: {score:.0f}{qualification_status}")


def run_ucl_simulation():
    print("*** Starting UEFA Champions League Simulation (New Swiss Model with Player Stats) ***")
    all_teams, all_teams_flat_players = setup_teams_and_players()
    teams_by_id = {team['id']: team for team in all_teams}
    
    print("\n--- Qualified Teams (36) ---")
    for i, team in enumerate(all_teams): 
        print(f"{i+1}. {team['name']} ({team['country']}) - Pot {team['pot']} (Rep: {team['reputation']})")

    league_fixtures = generate_league_phase_fixtures(all_teams)
    print(f"\n--- League Phase Fixtures Generated: {len(league_fixtures)} ---")

    print("\n--- Simulating League Phase ---")
    final_table = run_league_phase(all_teams, league_fixtures, all_teams_flat_players)
    print("\n--- Final League Phase Table ---")
    for i, (tid, data) in enumerate(final_table): 
        print(f"{i+1:2d}. {data['name']:<25} ({data['country']}) {data['P']:2d} {data['W']:2d} {data['D']:2d} {data['L']:2d} {data['GF']:3d}-{data['GA']:<3d} {data['GD']:+3d} {data['Pts']:3d}")

    direct_to_r16_ids = [item[0] for item in final_table[:8]]
    playoff_round_ids = [item[0] for item in final_table[8:24]]
    print("\n--- Knockout Stage Qualifications ---")
    print("Direct to R16 (Top 8):", ", ".join([teams_by_id[tid]['name'] for tid in direct_to_r16_ids]))
    
    playoff_seeded_ids, playoff_unseeded_ids = playoff_round_ids[:8], playoff_round_ids[8:]
    print("Knockout Playoff Round (9th-24th):")
    for i in range(8): 
        print(f"  - {teams_by_id[playoff_seeded_ids[i]]['name']} (S) vs {teams_by_id[playoff_unseeded_ids[i]]['name']} (U)")

    print("\n--- Simulating Knockout Playoff Round ---")
    playoff_winners_ids = []
    for i in range(8):
        winner_id = simulate_knockout_tie(playoff_seeded_ids[i], playoff_unseeded_ids[i], teams_by_id, all_teams_flat_players)
        playoff_winners_ids.append(winner_id)
    for wid in playoff_winners_ids: print(f"    Winner: {teams_by_id[wid]['name']}")
    apply_tournament_stage_bonus(playoff_winners_ids, 2.0, all_teams_flat_players, teams_by_id)
    
    print("\n--- Simulating Round of 16 ---")
    r16_seeded, r16_unseeded = direct_to_r16_ids[:], playoff_winners_ids[:]
    random.shuffle(r16_unseeded)
    r16_winners_ids = []
    num_r16_ties = min(len(r16_seeded), len(r16_unseeded))
    for i in range(num_r16_ties):
        winner = simulate_knockout_tie(r16_seeded[i], r16_unseeded[i], teams_by_id, all_teams_flat_players)
        r16_winners_ids.append(winner)
    for wid in r16_winners_ids: print(f"    Winner: {teams_by_id[wid]['name']}")
    apply_tournament_stage_bonus(r16_winners_ids, 3.0, all_teams_flat_players, teams_by_id)

    current_qualifiers = r16_winners_ids
    
    # Quarter-Finals
    if len(current_qualifiers) >= 2:
        print(f"\n--- Simulating Quarter-Finals ---")
        random.shuffle(current_qualifiers)
        qf_winners = []
        for i in range(0, len(current_qualifiers) - (len(current_qualifiers) % 2), 2):
            winner = simulate_knockout_tie(current_qualifiers[i], current_qualifiers[i+1], teams_by_id, all_teams_flat_players)
            qf_winners.append(winner)
            print(f"    Winner: {teams_by_id[winner]['name']}")
        current_qualifiers = qf_winners
        apply_tournament_stage_bonus(qf_winners, 4.0, all_teams_flat_players, teams_by_id)
    else:
        print("\nNot enough teams for Quarter-Finals.")
        current_qualifiers = []

    # Semi-Finals
    if len(current_qualifiers) >= 2:
        print(f"\n--- Simulating Semi-Finals ---")
        random.shuffle(current_qualifiers)
        sf_winners = []
        for i in range(0, len(current_qualifiers) - (len(current_qualifiers) % 2), 2):
            winner = simulate_knockout_tie(current_qualifiers[i], current_qualifiers[i+1], teams_by_id, all_teams_flat_players)
            sf_winners.append(winner)
            print(f"    Winner: {teams_by_id[winner]['name']}")
        current_qualifiers = sf_winners
        apply_tournament_stage_bonus(sf_winners, 5.0, all_teams_flat_players, teams_by_id)
    else:
        print("\nNot enough teams for Semi-Finals.")
        current_qualifiers = []

    # Final
    if len(current_qualifiers) == 2:
        print(f"\n--- Simulating Final ---")
        finalist1_id, finalist2_id = current_qualifiers[0], current_qualifiers[1]
        champion_id = simulate_knockout_tie(finalist1_id, finalist2_id, teams_by_id, all_teams_flat_players, neutral_venue=True)
        
        runner_up_id = finalist1_id if champion_id == finalist2_id else finalist2_id
        # The 5.0 "Reached Final" bonus was already applied to both. Now add champion-specific on top.
        apply_tournament_stage_bonus([champion_id], 6.0, all_teams_flat_players, teams_by_id) # Additional Champion Bonus        print(f"\n*** UEFA Champions League Winner: {teams_by_id[champion_id]['name']} ({teams_by_id[champion_id]['country']}) ***")
        print(f"     Runner-up: {teams_by_id[runner_up_id]['name']} ({teams_by_id[runner_up_id]['country']})")

    elif len(current_qualifiers) == 1: # Should not happen if logic is correct
         print(f"\n*** UEFA Champions League Winner (by default): {teams_by_id[current_qualifiers[0]]['name']} ({teams_by_id[current_qualifiers[0]]['country']}) ***")
    else:
        print("\nError: No finalists or too many finalists.")
        
    # Display Player Stats
    print("\n\n--- Overall Player Statistics ---")
    display_player_stats(all_teams_flat_players, teams_by_id, min_matches_for_avg_rating=3)

    # Display Manager Awards
    manager_stats = track_manager_performance(all_teams, final_table)
    display_manager_awards(manager_stats)

if __name__ == "__main__":
    run_ucl_simulation()
