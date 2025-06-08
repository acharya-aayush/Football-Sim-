#!/usr/bin/env python3
"""
Enhanced UEFA Europa League Simulation (New Swiss Model) with Real Player Data and Manager Integration
Based on the successful UCL simulation framework with UEL-specific adaptations
"""
import random
import json
from collections import defaultdict
import uuid
import os

# --- Configuration ---
# UEL teams are generally less prestigious than UCL teams, so different reputation ranges
UEL_TEAMS = [
    # Premier League representatives (usually 5th-7th place teams)
    {'name': 'Tottenham', 'country': 'ENG', 'reputation': 87, 'club_id': 'club_tottenham'},
    {'name': 'Brighton', 'country': 'ENG', 'reputation': 78, 'club_id': 'club_brighton'},
    {'name': 'West Ham', 'country': 'ENG', 'reputation': 76, 'club_id': 'club_west_ham'},
    
    # Bundesliga representatives
    {'name': 'Union Berlin', 'country': 'GER', 'reputation': 73, 'club_id': 'club_union_berlin'},
    {'name': 'Freiburg', 'country': 'GER', 'reputation': 71, 'club_id': 'club_freiburg'},
    {'name': 'Mainz', 'country': 'GER', 'reputation': 69, 'club_id': 'club_mainz'},
    
    # La Liga representatives
    {'name': 'Villarreal', 'country': 'ESP', 'reputation': 82, 'club_id': 'club_villarreal'},
    {'name': 'Real Betis', 'country': 'ESP', 'reputation': 79, 'club_id': 'club_real_betis'},
    {'name': 'Athletic Bilbao', 'country': 'ESP', 'reputation': 77, 'club_id': 'club_athletic_bilbao'},
    {'name': 'Real Sociedad', 'country': 'ESP', 'reputation': 76, 'club_id': 'club_real_sociedad'},
    
    # Serie A representatives
    {'name': 'Roma', 'country': 'ITA', 'reputation': 84, 'club_id': 'club_roma'},
    {'name': 'Lazio', 'country': 'ITA', 'reputation': 80, 'club_id': 'club_lazio'},
    {'name': 'Fiorentina', 'country': 'ITA', 'reputation': 78, 'club_id': 'club_fiorentina'},
    {'name': 'Atalanta', 'country': 'ITA', 'reputation': 81, 'club_id': 'club_atalanta'},
    
    # Ligue 1 representatives
    {'name': 'Marseille', 'country': 'FRA', 'reputation': 81, 'club_id': 'club_marseille'},
    {'name': 'Rennes', 'country': 'FRA', 'reputation': 74, 'club_id': 'club_rennes'},
    {'name': 'Lille', 'country': 'FRA', 'reputation': 77, 'club_id': 'club_lille'},
    {'name': 'Nice', 'country': 'FRA', 'reputation': 75, 'club_id': 'club_nice'},
    
    # Portuguese teams
    {'name': 'Sporting Braga', 'country': 'POR', 'reputation': 75, 'club_id': 'club_sporting_braga'},
    {'name': 'Vitoria Guimaraes', 'country': 'POR', 'reputation': 70, 'club_id': 'club_vitoria_guimaraes'},
    
    # Dutch teams
    {'name': 'AZ Alkmaar', 'country': 'NED', 'reputation': 73, 'club_id': 'club_az_alkmaar'},
    {'name': 'FC Twente', 'country': 'NED', 'reputation': 71, 'club_id': 'club_fc_twente'},
    
    # Scottish teams
    {'name': 'Aberdeen', 'country': 'SCO', 'reputation': 68, 'club_id': 'club_aberdeen'},
    {'name': 'Hearts', 'country': 'SCO', 'reputation': 66, 'club_id': 'club_hearts'},
    
    # Austrian teams
    {'name': 'LASK Linz', 'country': 'AUT', 'reputation': 67, 'club_id': 'club_lask_linz'},
    {'name': 'Austria Vienna', 'country': 'AUT', 'reputation': 65, 'club_id': 'club_austria_vienna'},
    
    # Turkish teams
    {'name': 'Besiktas', 'country': 'TUR', 'reputation': 74, 'club_id': 'club_besiktas'},
    {'name': 'Trabzonspor', 'country': 'TUR', 'reputation': 71, 'club_id': 'club_trabzonspor'},
    
    # Belgian teams
    {'name': 'Union Saint-Gilloise', 'country': 'BEL', 'reputation': 69, 'club_id': 'club_union_saint_gilloise'},
    {'name': 'Antwerp', 'country': 'BEL', 'reputation': 67, 'club_id': 'club_antwerp'},
    
    # Greek teams
    {'name': 'Olympiacos', 'country': 'GRE', 'reputation': 72, 'club_id': 'club_olympiacos'},
    {'name': 'PAOK', 'country': 'GRE', 'reputation': 69, 'club_id': 'club_paok'},
    
    # Swiss teams
    {'name': 'Basel', 'country': 'SUI', 'reputation': 68, 'club_id': 'club_basel'},
    {'name': 'Young Boys', 'country': 'SUI', 'reputation': 66, 'club_id': 'club_young_boys'},
      # Ukrainian teams
    {'name': 'Shakhtar Donetsk', 'country': 'UKR', 'reputation': 76, 'club_id': 'club_shakhtar_donetsk'},
    {'name': 'Dynamo Kyiv', 'country': 'UKR', 'reputation': 73, 'club_id': 'club_dynamo_kyiv'},
]

PLAYER_POSITIONS_ALLOCATION = {'GK': 3, 'DEF': 7, 'MID': 7, 'FWD': 6}  # 23 players total
TOTAL_PLAYERS_PER_TEAM = sum(PLAYER_POSITIONS_ALLOCATION.values())

# Formation templates for tactical variety
FORMATIONS = {
    '4-3-3': {'GK': 1, 'DEF': 4, 'MID': 3, 'FWD': 3},
    '4-4-2': {'GK': 1, 'DEF': 4, 'MID': 4, 'FWD': 2},
    '3-5-2': {'GK': 1, 'DEF': 3, 'MID': 5, 'FWD': 2},
    '4-2-3-1': {'GK': 1, 'DEF': 4, 'MID': 5, 'FWD': 1},
    '5-3-2': {'GK': 1, 'DEF': 5, 'MID': 3, 'FWD': 2}
}

# --- Helper Functions ---
def generate_club_id(name):
    return "club_" + name.lower().replace(" ", "_").replace("-", "_")

def generate_player_id():
    return f"player_{uuid.uuid4()}"

def load_players_from_json(team_name, club_id):
    """Load players for a given team from JSON file."""
    # Try multiple possible file paths based on different league directories
    possible_paths = [
        f'data/00_1_clubs_players/{club_id}_players.json',
        f'data/00_2_clubs_players/{club_id}_players.json',
        f'data/00_3_clubs_players/{club_id}_players.json',
        f'data/00_4_clubs_players/{club_id}_players.json',
        f'data/00_5_clubs_players/{club_id}_players.json',
        f'data/00_12_clubs_players/{club_id}_players.json',
        f'data/00_11_clubs_players/{club_id}_players.json',
        f'data/league_super_lig_clubs_players/{club_id}_players.json',
        f'data/league_scottish_premiership_clubs_players/{club_id}_players.json',
    ]
    
    for file_path in possible_paths:
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    players_data = json.load(f)
                print(f"Successfully loaded {len(players_data)} players for {team_name} from {file_path}")
                return convert_players_to_simulation_format(players_data, team_name, club_id)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            continue
    
    print(f"No player file found for {team_name} in any expected location")
    return []

def convert_players_to_simulation_format(players_data, team_name, club_id):
    """Convert loaded player data to simulation format."""
    converted_players = []
    
    for idx, player in enumerate(players_data):
        # Extract key attributes
        current_ability = player.get('current_ability', 70)
        positions = player.get('positions_primary', ['MID'])
        primary_position = positions[0] if positions else 'MID'
        
        # Map position to simulation categories
        if primary_position in ['GK']:
            sim_position = 'GK'
        elif primary_position in ['CB', 'LB', 'RB', 'LWB', 'RWB', 'SW']:
            sim_position = 'DEF'
        elif primary_position in ['CDM', 'CM', 'CAM', 'LM', 'RM']:
            sim_position = 'MID'
        elif primary_position in ['LW', 'RW', 'ST', 'CF']:
            sim_position = 'FWD'
        else:
            sim_position = 'MID'  # Default fallback
        
        converted_player = {
            'id': player.get('id', f"player_{club_id}_{idx}"),
            'name': player.get('known_as', player.get('name', f'Player_{idx}')),
            'team_id': club_id,
            'team_name': team_name,
            'position': sim_position,
            'skill': min(95, max(50, current_ability)),  # Clamp skill between 50-95
            'goals': 0,
            'assists': 0,
            'matches_played': 0,
            'total_rating_points': 0.0,
            'clean_sheets': 0,
            'avg_rating': 0.0,
            'original_position': primary_position,
            'real_data': True  # Mark as real player data
        }
        converted_players.append(converted_player)
    
    return converted_players

def load_manager_for_team(club_id):
    """Load manager data for a team."""
    # Try multiple manager files to find the team's manager
    possible_manager_files = [
        'data/managers/26.json',  # UEL managers
        'data/managers/1.json',   # EPL managers
        'data/managers/2.json',   # LaLiga managers
        'data/managers/3.json',   # Bundesliga managers
        'data/managers/4.json',   # Serie A managers
        'data/managers/5.json',   # Ligue 1 managers
        'data/managers/11.json',  # Primeira Liga managers
        'data/managers/12.json'   # Eredivisie managers
    ]
    
    for manager_file in possible_manager_files:
        try:
            if os.path.exists(manager_file):
                with open(manager_file, 'r', encoding='utf-8') as f:
                    manager_data = json.load(f)
                # Check if this file contains managers for our club
                if isinstance(manager_data, list):
                    for manager in manager_data:
                        if manager.get('current_club') == club_id or manager.get('current_club_id') == club_id:
                            return manager
                elif isinstance(manager_data, dict) and 'managers' in manager_data:
                    for manager in manager_data['managers']:
                        if manager.get('current_club') == club_id or manager.get('current_club_id') == club_id:
                            return manager
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        pass
    return None

def generate_placeholder_players(team_name, club_id, country):
    """Generate placeholder players for teams without real data."""
    players = []
    
    for position, count in PLAYER_POSITIONS_ALLOCATION.items():
        for i in range(count):
            # Generate country-specific player names and skills based on position
            if country in ['ENG', 'SCO']:
                name_prefix = ['Smith', 'Jones', 'Brown', 'Wilson', 'Taylor'][i % 5]
            elif country in ['GER', 'AUT', 'SUI']:
                name_prefix = ['Müller', 'Schmidt', 'Wagner', 'Weber', 'Fischer'][i % 5]
            elif country in ['ESP']:
                name_prefix = ['García', 'López', 'Martín', 'González', 'Rodríguez'][i % 5]
            elif country in ['ITA']:
                name_prefix = ['Rossi', 'Russo', 'Ferrari', 'Esposito', 'Bianchi'][i % 5]
            elif country in ['FRA']:
                name_prefix = ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert'][i % 5]
            elif country in ['NED']:
                name_prefix = ['de Jong', 'van der Berg', 'Jansen', 'Bakker', 'de Vries'][i % 5]
            elif country in ['POR']:
                name_prefix = ['Silva', 'Santos', 'Ferreira', 'Pereira', 'Costa'][i % 5]
            elif country in ['TUR']:
                name_prefix = ['Yılmaz', 'Kaya', 'Demir', 'Şahin', 'Çelik'][i % 5]
            else:
                name_prefix = ['Player', 'Star', 'Hero', 'Legend', 'Champion'][i % 5]
            
            # Skill varies by position and team reputation
            base_skill = 60
            if position == 'GK':
                skill_range = (base_skill, base_skill + 15)
            elif position == 'DEF':
                skill_range = (base_skill - 5, base_skill + 12)
            elif position == 'MID':
                skill_range = (base_skill - 3, base_skill + 18)
            else:  # FWD
                skill_range = (base_skill - 2, base_skill + 20)
            
            player = {
                'id': generate_player_id(),
                'name': f"{name_prefix}_{position}{i+1}_{country[:3].upper()}",
                'team_id': club_id,
                'team_name': team_name,
                'position': position,
                'skill': random.randint(skill_range[0], skill_range[1]),
                'goals': 0,
                'assists': 0,
                'matches_played': 0,
                'total_rating_points': 0.0,
                'clean_sheets': 0,
                'avg_rating': 0.0,
                'real_data': False  # Mark as generated player
            }
            players.append(player)
    
    return players

def simulate_match(team1, team2, all_players, is_neutral=False):
    """Simulate a match between two teams with detailed player performance tracking."""
    # Get squad for both teams
    team1_players = get_best_starting_xi(team1, all_players)
    team2_players = get_best_starting_xi(team2, all_players)
    
    # Calculate team strengths with formation bonuses
    formation1 = team1.get('manager', {}).get('preferred_formation', '4-3-3')
    formation2 = team2.get('manager', {}).get('preferred_formation', '4-3-3')
    
    team1_strength = calculate_team_strength(team1_players, formation1)
    team2_strength = calculate_team_strength(team2_players, formation2)
    
    # Home advantage (UEL has less pronounced home advantage than domestic leagues)
    if not is_neutral:
        team1_strength *= 1.08  # 8% home advantage
    
    # Simulate match events
    total_strength = team1_strength + team2_strength
    team1_dominance = team1_strength / total_strength
    
    # Expected goals calculation
    expected_goals_1 = 2.5 * team1_dominance
    expected_goals_2 = 2.5 * (1 - team1_dominance)
    
    # Actual goals (Poisson distribution simulation)
    goals_1 = max(0, random.randint(0, int(expected_goals_1 * 2)))
    goals_2 = max(0, random.randint(0, int(expected_goals_2 * 2)))
    
    # Track player performances
    track_player_performances(team1_players + team2_players, goals_1 + goals_2)
    
    # Assign goalscorers and assisters
    assign_goals_and_assists(team1_players, goals_1)
    assign_goals_and_assists(team2_players, goals_2)
    
    return goals_1, goals_2

def get_best_starting_xi(team, all_players):
    """Get the best starting XI for a team based on formation."""
    team_players = [p for p in all_players if p['team_id'] == team['id']]
    formation = team.get('manager', {}).get('preferred_formation', '4-3-3')
    formation_requirements = FORMATIONS[formation]
    
    starting_xi = []
    for position, needed in formation_requirements.items():
        position_players = sorted(
            [p for p in team_players if p['position'] == position],
            key=lambda x: x['skill'], reverse=True
        )
        starting_xi.extend(position_players[:needed])
    
    return starting_xi

def calculate_team_strength(players, formation):
    """Calculate team strength considering formation bonuses."""
    if not players:
        return 50  # Default strength for teams without players
    
    base_strength = sum(p['skill'] for p in players) / len(players)
    
    # Formation bonuses for UEL (smaller than UCL as teams are less tactical)
    formation_bonus = {
        '4-3-3': 1.02,
        '4-4-2': 1.01,
        '3-5-2': 1.015,
        '4-2-3-1': 1.03,
        '5-3-2': 1.0
    }.get(formation, 1.0)
    
    return base_strength * formation_bonus

def track_player_performances(players, total_goals):
    """Track player performances in the match."""
    for player in players:
        player['matches_played'] += 1
        
        # Generate match rating (6.0-9.5 scale)
        base_rating = 6.0
        skill_factor = (player['skill'] - 50) / 45  # Normalize skill to 0-1
        performance_variance = random.uniform(-0.5, 1.5)
        
        match_rating = min(9.5, max(6.0, base_rating + skill_factor + performance_variance))
        player['total_rating_points'] += match_rating

def assign_goals_and_assists(team_players, goals):
    """Assign goals and assists to players."""
    if goals == 0 or not team_players:
        return
    
    # Forwards and attacking midfielders more likely to score
    attacking_players = [p for p in team_players if p['position'] in ['FWD', 'MID']]
    all_outfield = [p for p in team_players if p['position'] != 'GK']
    
    for _ in range(goals):
        # Goal scorer
        if attacking_players:
            weights = []
            for p in attacking_players:
                weight = p['skill']
                if p['position'] == 'FWD':
                    weight *= 2.0  # Forwards twice as likely
                elif p['position'] == 'MID':
                    weight *= 1.3  # Midfielders more likely
                weights.append(weight)
            
            scorer = random.choices(attacking_players, weights=weights)[0]
        else:
            scorer = random.choice(all_outfield)
        
        scorer['goals'] += 1
        
        # Assist (70% chance)
        if random.random() < 0.7 and len(all_outfield) > 1:
            potential_assisters = [p for p in all_outfield if p != scorer]
            weights = [p['skill'] * (1.5 if p['position'] == 'MID' else 1.0) for p in potential_assisters]
            assister = random.choices(potential_assisters, weights=weights)[0]
            assister['assists'] += 1
    
    # Clean sheets for goalkeepers
    if goals == 0:
        for player in team_players:
            if player['position'] == 'GK':
                player['clean_sheets'] += 1

def create_fixtures_swiss_model(teams, rounds=8):
    """Create fixtures for the Swiss model (each team plays 8 matches)."""
    fixtures = []
    team_opponents = {team['id']: set() for team in teams}
    team_home_count = {team['id']: 0 for team in teams}
    
    for round_num in range(1, rounds + 1):
        round_fixtures = []
        available_teams = list(teams)
        random.shuffle(available_teams)
        
        while len(available_teams) >= 2:
            team1 = available_teams.pop(0)
            
            # Find suitable opponent
            suitable_opponents = [
                t for t in available_teams 
                if t['id'] not in team_opponents[team1['id']]
                and team1['id'] not in team_opponents[t['id']]
            ]
            
            if not suitable_opponents:
                # If no suitable opponent, pick randomly from remaining
                suitable_opponents = available_teams
            
            if suitable_opponents:
                team2 = suitable_opponents[0]
                available_teams.remove(team2)
                
                # Determine home/away
                if team_home_count[team1['id']] <= team_home_count[team2['id']]:
                    home_team, away_team = team1, team2
                    team_home_count[team1['id']] += 1
                else:
                    home_team, away_team = team2, team1
                    team_home_count[team2['id']] += 1
                
                fixture = {
                    'round': round_num,
                    'home': home_team,
                    'away': away_team
                }
                round_fixtures.append(fixture)
                
                # Track opponents
                team_opponents[team1['id']].add(team2['id'])
                team_opponents[team2['id']].add(team1['id'])
        
        fixtures.extend(round_fixtures)
    
    return fixtures

def simulate_league_phase(teams, all_players):
    """Simulate the entire league phase of the Europa League."""
    print("--- Simulating League Phase ---")
    
    # Create fixtures
    fixtures = create_fixtures_swiss_model(teams, rounds=8)
    print(f"--- League Phase Fixtures Generated: {len(fixtures)} ---")
    
    # Initialize team stats
    team_stats = {}
    for team in teams:
        team_stats[team['id']] = {
            'team': team,
            'played': 0, 'won': 0, 'drawn': 0, 'lost': 0,
            'goals_for': 0, 'goals_against': 0, 'points': 0
        }
    
    # Simulate all matches
    for fixture in fixtures:
        home_team = fixture['home']
        away_team = fixture['away']
        
        goals_home, goals_away = simulate_match(home_team, away_team, all_players)
        
        # Update stats
        for team_id, goals_for, goals_against in [
            (home_team['id'], goals_home, goals_away),
            (away_team['id'], goals_away, goals_home)
        ]:
            stats = team_stats[team_id]
            stats['played'] += 1
            stats['goals_for'] += goals_for
            stats['goals_against'] += goals_against
            
            if goals_for > goals_against:
                stats['won'] += 1
                stats['points'] += 3
            elif goals_for == goals_against:
                stats['drawn'] += 1
                stats['points'] += 1
            else:
                stats['lost'] += 1
    
    # Create final table
    final_table = []
    for team_id, stats in team_stats.items():
        goal_difference = stats['goals_for'] - stats['goals_against']
        final_table.append((team_id, {
            'Team': stats['team']['name'],
            'Country': stats['team']['country'],
            'P': stats['played'],
            'W': stats['won'],
            'D': stats['drawn'],
            'L': stats['lost'],
            'GF': stats['goals_for'],
            'GA': stats['goals_against'],
            'GD': goal_difference,
            'Pts': stats['points']
        }))
    
    # Sort by points, then goal difference, then goals for
    final_table.sort(key=lambda x: (x[1]['Pts'], x[1]['GD'], x[1]['GF']), reverse=True)
    
    return final_table

def display_league_table(final_table):
    """Display the league phase table."""
    print("--- Final League Phase Table ---")
    for i, (team_id, data) in enumerate(final_table):
        print(f"{i+1:2d}. {data['Team']:<25} ({data['Country']})  "
              f"{data['P']:2d}  {data['W']:2d}  {data['D']:2d}  {data['L']:2d}  "
              f"{data['GF']:2d}-{data['GA']:<2d}  {data['GD']:+3d}  {data['Pts']:2d}")

def determine_knockout_qualification(final_table):
    """Determine knockout stage qualification according to UEL rules."""
    print("\\n--- Knockout Stage Qualifications ---")
    
    # Top 8 go direct to Round of 16
    direct_r16 = [team_id for team_id, _ in final_table[:8]]
    direct_r16_teams = [(team_id, data) for team_id, data in final_table[:8]]
    
    print("Direct to R16 (Top 8): " + ", ".join([data['Team'] for _, data in direct_r16_teams]))
    
    # 9th-24th place go to Knockout Playoff Round
    playoff_teams = final_table[8:24]
    if playoff_teams:
        print("Knockout Playoff Round (9th-24th):")
        # Pair teams: 9th vs 24th, 10th vs 23rd, etc.
        playoff_pairs = []
        for i in range(len(playoff_teams) // 2):
            seeded_team = playoff_teams[i]
            unseeded_team = playoff_teams[-(i+1)]
            playoff_pairs.append((seeded_team, unseeded_team))
            print(f"  - {seeded_team[1]['Team']} (S) vs {unseeded_team[1]['Team']} (U)")
        
        return direct_r16, playoff_pairs
    else:
        return direct_r16, []

def simulate_knockout_match(team1_data, team2_data, all_players, teams_dict, match_name=""):
    """Simulate a knockout match (two legs or single match)."""
    # team1_data and team2_data are tuples from final_table: (team_id, team_stats)
    team1_id = team1_data[0]
    team2_id = team2_data[0]
    
    # Get team objects from teams_dict
    team1 = teams_dict.get(team1_id)
    team2 = teams_dict.get(team2_id)
    
    if not team1 or not team2:
        return None, "0-0", "Team not found"
    
    # Simulate two legs
    # Leg 1 (team1 at home)
    goals1_leg1, goals2_leg1 = simulate_match(team1, team2, all_players)
    
    # Leg 2 (team2 at home)  
    goals1_leg2, goals2_leg2 = simulate_match(team2, team1, all_players)
    
    # Calculate aggregate
    aggregate1 = goals1_leg1 + goals1_leg2
    aggregate2 = goals2_leg1 + goals2_leg2
    
    print(f"  Tie: {team1['name']} vs {team2['name']}")
    print(f"    Leg 1: {team1['name']} {goals1_leg1} - {goals2_leg1} {team2['name']}")
    print(f"    Leg 2: {team2['name']} {goals2_leg2} - {goals1_leg2} {team1['name']}")
    print(f"    Aggregate: {team1['name']} {aggregate1} - {aggregate2} {team2['name']}")
    
    # Determine winner
    if aggregate1 > aggregate2:
        winner = team1_data
        print(f"    Winner: {team1['name']}")
    elif aggregate2 > aggregate1:
        winner = team2_data
        print(f"    Winner: {team2['name']}")
    else:
        # Away goals rule or penalties
        print(f"    Aggregate tied! Coin flip winner (simplified for no extra time/pens simulation)...")
        winner = random.choice([team1_data, team2_data])
        winner_team = team1 if winner == team1_data else team2
        print(f"    Winner: {winner_team['name']}")
    
    return winner

def simulate_knockout_phase(direct_r16, playoff_pairs, all_players, all_teams):
    """Simulate the knockout phase of the Europa League."""
    print("\\n--- Simulating Knockout Playoff Round ---")
      # Create teams dictionary for lookup
    teams_dict = {team['id']: team for team in all_teams}
    
    # Simulate playoff round
    playoff_winners = []
    for seeded, unseeded in playoff_pairs:
        winner = simulate_knockout_match(seeded, unseeded, all_players, teams_dict, "Playoff")
        if winner:
            playoff_winners.append(winner)    # Round of 16 participants
    r16_teams = []
    for team_id in direct_r16:
        for team_data in all_teams:
            if team_data['id'] == team_id:
                r16_teams.append((team_id, {'Team': team_data['name']}))
                break
    
    r16_teams.extend(playoff_winners)
    random.shuffle(r16_teams)
    
    print("\\n--- Simulating Round of 16 ---")
    qf_teams = []
    for i in range(0, len(r16_teams), 2):
        if i + 1 < len(r16_teams):
            winner = simulate_knockout_match(r16_teams[i], r16_teams[i+1], all_players, teams_dict, "R16")
            if winner:
                qf_teams.append(winner)
    
    print("\\n--- Simulating Quarter-Finals ---")
    sf_teams = []
    for i in range(0, len(qf_teams), 2):
        if i + 1 < len(qf_teams):
            winner = simulate_knockout_match(qf_teams[i], qf_teams[i+1], all_players, teams_dict, "QF")
            if winner:
                sf_teams.append(winner)
    
    print("\\n--- Simulating Semi-Finals ---")
    final_teams = []
    for i in range(0, len(sf_teams), 2):
        if i + 1 < len(sf_teams):
            winner = simulate_knockout_match(sf_teams[i], sf_teams[i+1], all_players, teams_dict, "SF")
            if winner:
                final_teams.append(winner)
    
    if len(final_teams) >= 2:
        print("\\n--- Simulating Final ---")
          # Find team objects for final
        team1 = team2 = None
        for team in all_teams:
            if team['id'] == final_teams[0][0]:
                team1 = team
            elif team['id'] == final_teams[1][0]:
                team2 = team
        
        if team1 and team2:
            # Single match final
            goals1, goals2 = simulate_match(team1, team2, all_players, is_neutral=True)
            print(f"  Final: {team1['name']} vs {team2['name']}")
            
            if goals1 == goals2:
                print(f"    Score: {goals1}-{goals2}. Penalties...")
                winner = random.choice([team1, team2])
                print(f"    {winner['name']} wins on penalties!")
            else:
                winner = team1 if goals1 > goals2 else team2
                print(f"    Score: {goals1}-{goals2}")
                print(f"    Winner: {winner['name']}")
            
            runner_up = team2 if winner == team1 else team1
            print(f"     Runner-up: {runner_up['name']} ({runner_up['country']})")
            
            return winner, runner_up
    
    return None, None

def display_player_stats(all_players, min_matches_for_avg_rating=3):
    """Display comprehensive player statistics."""
    print("\\n--- Overall Player Statistics ---")
    
    # Filter out players who haven't played
    players_list = [p for p in all_players if p['matches_played'] > 0]
    
    # Top Scorers
    print("--- Top Scorers ---")
    top_scorers = sorted(players_list, key=lambda x: (x['goals'], x['matches_played']), reverse=True)[:10]
    for i, p in enumerate(top_scorers, 1):
        real_tag = " *** Real Player Data" if p.get('real_data') else ""
        print(f"{i}. {p['name']} ({p['team_name']}) - {p['goals']} goals ({p['matches_played']} matches){real_tag}")
    
    # Top Assisters
    print("--- Top Assisters ---")
    top_assisters = sorted(players_list, key=lambda x: (x['assists'], x['matches_played']), reverse=True)[:10]
    for i, p in enumerate(top_assisters, 1):
        real_tag = " *** Real Player Data" if p.get('real_data') else ""
        print(f"{i}. {p['name']} ({p['team_name']}) - {p['assists']} assists ({p['matches_played']} matches){real_tag}")
    
    # Goals + Assists
    print("--- Top Goals + Assists ---")
    for p in players_list:
        p['goals_assists'] = p['goals'] + p['assists']
    
    top_ga = sorted(players_list, key=lambda x: (x['goals_assists'], x['matches_played']), reverse=True)[:10]
    for i, p in enumerate(top_ga, 1):
        real_tag = " *** Real Player Data" if p.get('real_data') else ""
        print(f"{i}. {p['name']} ({p['team_name']}) - {p['goals_assists']} (G:{p['goals']}, A:{p['assists']}) [{p['matches_played']} matches]{real_tag}")
    
    # Clean Sheets (Goalkeepers)
    print("--- Goalkeeper Clean Sheets ---")
    gk_players = [p for p in players_list if p['position'] == 'GK' and p['matches_played'] >= 3]
    top_cs = sorted(gk_players, key=lambda x: (x['clean_sheets'], x['matches_played']), reverse=True)[:5]
    for i, p in enumerate(top_cs, 1):
        real_tag = " *** Real Player Data" if p.get('real_data') else ""
        print(f"{i}. {p['name']} ({p['team_name']}) - {p['clean_sheets']} clean sheets ({p['matches_played']} matches){real_tag}")
    
    # Average Match Rating
    print("--- Highest Average Match Rating (Min 3 Matches) ---")
    for player in players_list:
        if player['matches_played'] >= min_matches_for_avg_rating:
            player['avg_rating'] = round(player['total_rating_points'] / player['matches_played'], 2)

    rated_players = sorted([p for p in players_list if p['matches_played'] >= min_matches_for_avg_rating], 
                           key=lambda x: x['avg_rating'], reverse=True)
    for i, p in enumerate(rated_players[:10]):
        real_tag = " *** Real Player Data" if p.get('real_data') else ""
        print(f"{i+1}. {p['name']} ({p['team_name']}) - {p['avg_rating']:.2f} avg rating ({p['matches_played']} matches){real_tag}")

    # Tournament Best Player (considering total rating points, goals+assists, and match participation)
    print("\\n--- Tournament Best Player Analysis ---")
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
    print("\\n--- Tournament Best XI (4-3-3 Formation) ---")
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
        print(f"\\n   Best XI Average Rating: {average_rating:.2f}")
        
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
                'table_position': table_positions.get(team['id'], 99),
                'qualified_ko': table_positions.get(team['id'], 99) <= 24,
                'direct_r16': table_positions.get(team['id'], 99) <= 8
            }
    
    return manager_stats

def calculate_manager_score(manager_data):
    """Calculate a score for manager performance."""
    score = 0
    
    # Points earned (most important factor)
    score += manager_data['points'] * 10
    
    # Table position bonus (higher = better)
    position_bonus = max(0, 37 - manager_data['table_position']) * 5
    score += position_bonus
    
    # Goal difference
    score += manager_data['goal_difference'] * 2
    
    # Qualification bonuses
    if manager_data['direct_r16']:
        score += 100  # Direct qualification bonus
    elif manager_data['qualified_ko']:
        score += 50   # Knockout qualification bonus
    
    # Win percentage bonus
    total_matches = manager_data['wins'] + manager_data['draws'] + manager_data['losses']
    if total_matches > 0:
        win_rate = manager_data['wins'] / total_matches
        score += win_rate * 50
    
    return score

def display_manager_awards(teams, final_table):
    """Display manager performance awards."""
    print("\\n--- Manager Performance Awards ---")
    
    manager_stats = track_manager_performance(teams, final_table)
    
    if not manager_stats:
        print("   No manager data available")
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
    
    # Top 5 managers
    print("   Top 5 Managers:")
    for i, (score, manager) in enumerate(manager_scores[:5], 1):
        ko_status = "Direct R16" if manager['direct_r16'] else ("Qualified" if manager['qualified_ko'] else "Eliminated")
        print(f"   {i}. {manager['name']} ({manager['team_name']}) - Pos: {manager['table_position']}, Score: {score:.0f} ({ko_status})")

def setup_teams_with_data():
    """Set up all teams with real player data and managers where available."""
    all_teams = []
    all_players = []
    
    print("*** Starting UEFA Europa League Simulation (Swiss Model with Player Stats) ***")
    
    for team_info in UEL_TEAMS:
        team = {
            'id': team_info['club_id'],
            'name': team_info['name'],
            'country': team_info['country'],
            'reputation': team_info['reputation']
        }
        
        # Load players
        players = load_players_from_json(team['name'], team['id'])
        if not players:
            players = generate_placeholder_players(team['name'], team['id'], team['country'])
        
        all_players.extend(players)
        
        # Load manager
        manager = load_manager_for_team(team['id'])
        if manager:
            team['manager'] = manager
            print(f"Found manager {manager.get('name', 'Unknown')} for {team['name']}")
        else:
            print(f"Manager not found for {team['name']} (club_id: {team['id']})")
        
        all_teams.append(team)
    
    return all_teams, all_players

def run_uel_simulation():
    """Run the complete Europa League simulation."""
    # Setup teams and players
    all_teams, all_players = setup_teams_with_data()
    
    # Simulate league phase
    final_table = simulate_league_phase(all_teams, all_players)
    display_league_table(final_table)
    
    # Knockout qualification
    direct_r16, playoff_pairs = determine_knockout_qualification(final_table)
      # Simulate knockout phase
    champion, runner_up = simulate_knockout_phase(direct_r16, playoff_pairs, all_players, all_teams)
    
    if champion:
        print(f"\\n*** EUROPA LEAGUE CHAMPION: {champion['name']} ({champion['country']}) ***")
    if runner_up:
        print(f"   Runner-up: {runner_up['name']} ({runner_up['country']})")
    
    # Display comprehensive statistics
    display_player_stats(all_players)
    display_manager_awards(all_teams, final_table)

if __name__ == "__main__":
    run_uel_simulation()
