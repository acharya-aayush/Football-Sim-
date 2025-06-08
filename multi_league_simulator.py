#!/usr/bin/env python3
"""
Multi-League Season Simulator
Simulate domestic football leagues with all available league data
"""

import json
import random
import os
import csv
from datetime import datetime
from collections import defaultdict


class MultiLeagueSimulator:
    def __init__(self, specific_leagues=None):
        """Initialize the multi-league simulator
        
        Args:
            specific_leagues (list): Optional list of league IDs to simulate (defaults to all)
        """
        self.leagues = {}
        self.clubs_by_league = {}
        self.all_clubs = {}
        self.players_by_club = {}
        self.managers = {}
        self.season_number = 1
        
        # Filter for specific leagues if provided
        self.specific_leagues = specific_leagues
        
        self.load_data()
        self.determine_season_number()
    
    def load_data(self):
        """Load all required data (leagues, clubs, players, managers)"""
        print("📂 Loading simulation data...")
        
        # Load leagues configuration
        print("  Loading leagues...")
        try:
            with open('data/leagues.json', 'r', encoding='utf-8') as f:
                content = f.read()
                if content.startswith('//'):
                    lines = content.split('\n')
                    content = '\n'.join(line for line in lines if not line.strip().startswith('//'))
                leagues_data = json.loads(content)
            
            for league in leagues_data:
                league_id = league.get('id') or league.get('league_id')
                # Only include domestic leagues (not competitions) and filter if specific_leagues provided
                if league_id and not league_id.startswith('competition_'):
                    if not self.specific_leagues or league_id in self.specific_leagues:
                        self.leagues[league_id] = league
            
            print(f"  ✅ Loaded {len(self.leagues)} leagues")
            
            # Show which leagues were loaded
            for league_id, league in self.leagues.items():
                print(f"    - {league.get('name', league_id)}")
        except Exception as e:
            print(f"  ❌ Error loading leagues: {e}")
            return
        
        # Load clubs for each league
        self.load_clubs_data()
        
        # Load managers data (comprehensive approach to find all manager files)
        self.load_managers_data()
        
        # Load players for all clubs that have been loaded
        self.load_players_data()
        
        print(f"\n✅ Loaded {len(self.leagues)} leagues")
        club_count = sum(len(clubs) for clubs in self.clubs_by_league.values())
        print(f"✅ Loaded {club_count} clubs")
        print(f"✅ Loaded {len(self.managers)} managers")
        player_count = sum(len(players) for players in self.players_by_club.values())
        print(f"✅ Loaded {player_count} players")
    
    def load_clubs_data(self):
        """Load club data for all leagues"""
        print("\n  Loading clubs...")
        leagues_clubs_dir = 'data/leagues_clubs'
        
        if not os.path.exists(leagues_clubs_dir):
            print(f"  ❌ Clubs directory not found: {leagues_clubs_dir}")
            return
        
        for filename in os.listdir(leagues_clubs_dir):
            if filename.endswith('_clubs.json') or filename.endswith('clubs.json'):
                file_path = os.path.join(leagues_clubs_dir, filename)
                
                league_id = None
                # Extract league ID from filename
                if filename.startswith('league_'):
                    # Handle league_{name}_clubs.json format
                    league_id = 'league_' + filename.replace('league_', '').replace('_clubs.json', '')
                elif filename == 'epl_clubs.json':
                    league_id = 'league_epl'
                elif filename == 'laliga_clubs.json':
                    league_id = 'league_laliga'
                
                # Skip if this league wasn't selected
                if league_id not in self.leagues:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        clubs = json.load(f)
                    
                    # Handle different file structures
                    if isinstance(clubs, list):
                        club_list = clubs
                    else:
                        club_list = clubs.get('clubs', [])
                    
                    # Store clubs by league
                    self.clubs_by_league[league_id] = club_list
                    
                    # Add to overall club dictionary
                    for club in club_list:
                        club_id = club.get('id') or club.get('club_id')
                        if club_id:
                            self.all_clubs[club_id] = club
                    
                    print(f"    ✅ Loaded {len(club_list)} clubs for {self.leagues[league_id].get('name', league_id)}")
                except Exception as e:
                    print(f"    ⚠️  Error loading clubs from {filename}: {e}")
    
    def load_managers_data(self):
        """Load managers data from all available sources"""
        print("\n  Loading managers...")
          manager_sources = [
            # First try consolidated managers file
            'data/managers.json', 
            
            # Try simple integer manager files based on league mapping
            'data/managers/1.json',  # EPL
            'data/managers/2.json',  # LaLiga
            'data/managers/3.json',  # Bundesliga
            'data/managers/4.json',  # Serie A
            'data/managers/5.json',  # Ligue 1
            'data/managers/6.json',  # LaLiga2
            'data/managers/7.json',  # Championship
            'data/managers/8.json',  # Bundesliga 2
            'data/managers/9.json',  # Serie B
            'data/managers/10.json', # Ligue 2
            'data/managers/11.json', # Primeira Liga
            'data/managers/12.json', # Eredivisie
            'data/managers/13.json', # Scottish Premiership
            'data/managers/14.json', # Belgian Pro League
            'data/managers/15.json', # Austrian Bundesliga
            'data/managers/16.json', # Swiss Super League
            'data/managers/17.json', # Turkish Super Lig
            'data/managers/18.json', # Russian Premier League
            'data/managers/19.json', # Ukrainian Premier League
            'data/managers/20.json', # Polish Ekstraklasa
            'data/managers/21.json', # Argentina Primera
            'data/managers/22.json', # Argentina Primera Division
            'data/managers/23.json', # Austrian League
            'data/managers/24.json', # Brasileirao
            'data/managers/25.json', # UCL
            'data/managers/26.json', # UEL
            'data/managers/27.json', # Serie A Brazil
            'data/managers/28.json', # Danish
            'data/managers/29.json', # Danish Superliga
            'data/managers/30.json', # Greek
            'data/managers/31.json', # Liga MX
            'data/managers/32.json', # Liga MX (alt)
            'data/managers/33.json', # MLS
            'data/managers/34.json', # Norwegian Eliteserien
            'data/managers/35.json', # Swedish Allsvenskan
        ]
        
        managers_loaded = 0
        
        for source in manager_sources:
            if os.path.exists(source):
                try:
                    with open(source, 'r', encoding='utf-8') as f:
                        manager_data = json.load(f)
                    
                    # Handle different file structures
                    if isinstance(manager_data, dict) and 'managers' in manager_data:
                        manager_list = manager_data['managers']
                    else:
                        manager_list = manager_data
                    
                    # Add managers to dictionary
                    for manager in manager_list:
                        manager_id = manager.get('manager_id') or manager.get('id')
                        club_id = manager.get('current_club_id') or manager.get('club_id')
                        
                        if manager_id and club_id:
                            self.managers[club_id] = manager
                            managers_loaded += 1
                    
                    print(f"    ✅ Loaded managers from {source}")
                except Exception as e:
                    print(f"    ⚠️  Error loading managers from {source}: {e}")
        
        print(f"    Total: {managers_loaded} managers loaded")
    
    def load_players_data(self):
        """Load players data for all clubs"""
        print("\n  Loading players...")
        
        for league_id in self.leagues.keys():
            base_name = league_id.replace('league_', '')
            
            # Try different directory patterns for player data
            player_dirs = [
                f'data/league_{base_name}_clubs_players',
                f'data/{league_id}_clubs_players'
            ]
            
            for player_dir in player_dirs:
                if os.path.exists(player_dir):
                    league_name = self.leagues[league_id].get('name', league_id)
                    print(f"    Loading {league_name} players from {player_dir}...")
                    
                    club_count = 0
                    player_count = 0
                    
                    # Handle direct club folders with players.json inside
                    if any(os.path.isdir(os.path.join(player_dir, d)) for d in os.listdir(player_dir)):
                        # Structure: player_dir/club_id/players.json
                        for club_folder in os.listdir(player_dir):
                            club_path = os.path.join(player_dir, club_folder)
                            if os.path.isdir(club_path):
                                players_file = os.path.join(club_path, 'players.json')
                                if os.path.exists(players_file):
                                    try:
                                        with open(players_file, 'r', encoding='utf-8') as f:
                                            club_players = json.load(f)
                                        
                                        self.players_by_club[club_folder] = club_players
                                        club_count += 1
                                        player_count += len(club_players)
                                    except Exception as e:
                                        print(f"      ⚠️  Error loading {players_file}: {e}")
                    # Handle club_id_players.json files
                    else:
                        for filename in os.listdir(player_dir):
                            if filename.endswith('_players.json'):
                                club_id = filename.replace('_players.json', '')
                                players_file = os.path.join(player_dir, filename)
                                
                                try:
                                    with open(players_file, 'r', encoding='utf-8') as f:
                                        club_players = json.load(f)
                                    
                                    self.players_by_club[club_id] = club_players
                                    club_count += 1
                                    player_count += len(club_players)
                                except Exception as e:
                                    print(f"      ⚠️  Error loading {players_file}: {e}")
                    
                    print(f"      ✅ Loaded {player_count} players for {club_count} {league_name} clubs")
    
    def determine_season_number(self):
        """Determine current season number based on existing CSV files"""
        csv_filename = "multi_league_results.csv"
        if os.path.exists(csv_filename):
            try:
                with open(csv_filename, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    seasons = set()
                    for row in reader:
                        if 'Season' in row:
                            try:
                                seasons.add(int(row['Season']))
                            except:
                                pass
                    
                    if seasons:
                        self.season_number = max(seasons) + 1
                    else:
                        self.season_number = 1
            except:
                self.season_number = 1
        else:
            self.season_number = 1
        
        print(f"🏆 Starting Season {self.season_number}")
    
    def get_club_strength(self, club):
        """Calculate club strength based on available data"""
        # Base strength from club reputation or league reputation
        club_id = club.get('id') or club.get('club_id')
        club_rep = club.get('reputation')
        
        if club_rep:
            strength = club_rep
        else:
            # If no club reputation, use league reputation as baseline
            league_id = club.get('league_id')
            if league_id in self.leagues:
                league_rep = self.leagues[league_id].get('reputation', 70)
                strength = league_rep
            else:
                strength = 70  # Default
        
        # Add player strength if available
        if club_id in self.players_by_club:
            club_players = self.players_by_club[club_id]
            if club_players:
                # Use overall ratings if available, otherwise calculate from attributes
                overalls = []
                for player in club_players:
                    if 'overall' in player:
                        overalls.append(player['overall'])
                    elif 'technical_attributes' in player:
                        tech_attrs = player['technical_attributes']
                        if tech_attrs:
                            avg_tech = sum(tech_attrs.values()) / len(tech_attrs)
                            overalls.append(min(avg_tech, 95))  # Cap at 95
                
                if overalls:
                    avg_overall = sum(overalls) / len(overalls)
                    strength = (strength + avg_overall) / 2
        
        # Add manager strength if available
        manager = self.managers.get(club_id)
        if manager:
            manager_ability = manager.get('manager_ability')
            if manager_ability:
                strength = (strength * 0.8) + (manager_ability * 0.2)  # 80% club, 20% manager
        
        # Apply some small randomness for season-to-season variation
        strength += random.uniform(-3, 3)
        
        return min(max(strength, 50), 95)  # Clamp between 50-95
    
    def simulate_match(self, home_club, away_club):
        """Simulate a match between two clubs"""
        home_strength = self.get_club_strength(home_club)
        away_strength = self.get_club_strength(away_club)
        
        # Home advantage
        home_strength += 3
        
        # Calculate goal probabilities based on strength difference
        strength_diff = home_strength - away_strength
        
        # Base goals with some randomness
        home_base_goals = 1.5 + (strength_diff / 30)
        away_base_goals = 1.5 - (strength_diff / 30)
          # Add randomness using normal distribution (more reliable than Poisson for Python's random)
        home_goals = max(0, int(random.normalvariate(max(0.5, home_base_goals), 1.0)))
        away_goals = max(0, int(random.normalvariate(max(0.5, away_base_goals), 1.0)))
        
        return {
            'home_team': home_club.get('name', 'Unknown'),
            'away_team': away_club.get('name', 'Unknown'),
            'home_goals': home_goals,
            'away_goals': away_goals,
            'home_club_id': home_club.get('id') or home_club.get('club_id'),
            'away_club_id': away_club.get('id') or away_club.get('club_id')
        }
    
    def generate_fixtures(self, clubs):
        """Generate round-robin fixtures (home and away)"""
        fixtures = []
        n = len(clubs)
        
        # Create fixtures where each team plays each other twice (home and away)
        for i in range(n):
            for j in range(n):
                if i != j:
                    fixtures.append((clubs[i], clubs[j]))
        
        return fixtures
    
    def simulate_league_season(self, league_id):
        """Simulate a full season for a league"""
        league_name = self.leagues[league_id].get('name', league_id)
        print(f"\n🏟️  Simulating {league_name} Season {self.season_number}")
        print("-" * 60)
        
        clubs = self.clubs_by_league.get(league_id, [])
        if len(clubs) < 2:
            print(f"⚠️  Not enough clubs in {league_name} (found {len(clubs)})")
            return None
        
        # Generate fixtures
        fixtures = self.generate_fixtures(clubs)
        print(f"📅 Generated {len(fixtures)} fixtures ({len(clubs)} clubs)")
        
        # Initialize league table
        table = {}
        for club in clubs:
            club_id = club.get('id') or club.get('club_id')
            table[club_id] = {
                'club_id': club_id,
                'club_name': club.get('name', 'Unknown'),
                'matches': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0,
                'points': 0
            }
        
        # Simulate all matches
        print(f"⚽ Simulating {len(fixtures)} matches...")
        match_results = []
        for i, (home_club, away_club) in enumerate(fixtures):
            if i % 100 == 0 and i > 0:  # Progress indicator
                print(f"  Progress: {i}/{len(fixtures)} matches")
            
            result = self.simulate_match(home_club, away_club)
            match_results.append(result)
            
            # Update table
            home_id = result['home_club_id']
            away_id = result['away_club_id']
            
            if home_id in table and away_id in table:
                # Update matches played
                table[home_id]['matches'] += 1
                table[away_id]['matches'] += 1
                
                # Update goals
                table[home_id]['goals_for'] += result['home_goals']
                table[home_id]['goals_against'] += result['away_goals']
                table[away_id]['goals_for'] += result['away_goals']
                table[away_id]['goals_against'] += result['home_goals']
                
                # Determine winner and update points
                if result['home_goals'] > result['away_goals']:
                    table[home_id]['wins'] += 1
                    table[home_id]['points'] += 3
                    table[away_id]['losses'] += 1
                elif result['home_goals'] < result['away_goals']:
                    table[away_id]['wins'] += 1
                    table[away_id]['points'] += 3
                    table[home_id]['losses'] += 1
                else:
                    table[home_id]['draws'] += 1
                    table[away_id]['draws'] += 1
                    table[home_id]['points'] += 1
                    table[away_id]['points'] += 1
        
        # Calculate goal difference
        for club_id in table:
            table[club_id]['goal_difference'] = table[club_id]['goals_for'] - table[club_id]['goals_against']
        
        # Sort table by points, then goal difference, then goals for
        sorted_table = sorted(table.values(), 
                            key=lambda x: (-x['points'], -x['goal_difference'], -x['goals_for']))
        
        # Add positions
        for i, club in enumerate(sorted_table):
            club['position'] = i + 1
            club['league_id'] = league_id  # Add league_id for CSV export
            club['league_name'] = league_name  # Add league_name for CSV export
        
        # Display table
        self.display_league_table(sorted_table, league_id, league_name)
        
        return {
            'league_id': league_id,
            'league_name': league_name,
            'table': sorted_table,
            'matches': match_results
        }
    
    def display_league_table(self, table, league_id, league_name):
        """Display a formatted league table"""
        print(f"\n📊 {league_name} Final Table:")
        print("-" * 80)
        print(f"{'Pos':<3} {'Club':<25} {'P':<3} {'W':<3} {'D':<3} {'L':<3} {'GF':<3} {'GA':<3} {'GD':<4} {'Pts':<3}")
        print("-" * 80)
        
        # Get the promotion/relegation spots from league configuration
        league_config = self.leagues.get(league_id, {})
        ucl_spots = league_config.get('ucl_qualification_spots', 4) if league_config.get('is_top_five') else 1
        uel_spots = league_config.get('uel_qualification_spots', 1)
        relegation_spots = league_config.get('relegation_spots', 3)
        
        for club in table:
            # Add qualification info
            position = club['position']
            qual = ""
            if position <= ucl_spots:
                qual = "🏆 UCL"
            elif position <= ucl_spots + uel_spots:
                qual = "🥉 UEL"
            elif position > len(table) - relegation_spots:
                qual = "⬇️ REL"
            
            print(f"{club['position']:<3} {club['club_name'][:25]:<25} "
                  f"{club['matches']:<3} {club['wins']:<3} {club['draws']:<3} {club['losses']:<3} "
                  f"{club['goals_for']:<3} {club['goals_against']:<3} {club['goal_difference']:>+4} {club['points']:<3} {qual}")
        
        print("-" * 80)
        print("🏆 UCL = Champions League, 🥉 UEL = Europa League, ⬇️ REL = Relegation")
    
    def run_all_leagues(self):
        """Run simulation for all loaded leagues"""
        print(f"\n🌍 Starting Season {self.season_number} Simulation")
        print("=" * 60)
        
        all_results = []
        manager_stats = defaultdict(lambda: {'points': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'position': 0})
        winners = []
        
        # Simulate each league
        for league_id in self.leagues.keys():
            result = self.simulate_league_season(league_id)
            
            if result:
                all_results.append(result)
                
                # Track winner
                if result['table']:
                    winner = result['table'][0]
                    winners.append({
                        'league': result['league_name'],
                        'champion': winner['club_name'],
                        'points': winner['points'],
                        'goal_difference': winner['goal_difference']
                    })
                
                # Track manager stats
                for club in result['table']:
                    club_id = club['club_id']
                    if club_id in self.managers:
                        manager_id = self.managers[club_id].get('manager_id') or self.managers[club_id].get('id')
                        if manager_id:
                            manager_stats[manager_id]['name'] = self.managers[club_id].get('name', 'Unknown')
                            manager_stats[manager_id]['club'] = club['club_name']
                            manager_stats[manager_id]['league'] = result['league_name']
                            manager_stats[manager_id]['points'] += club['points']
                            manager_stats[manager_id]['wins'] += club['wins']
                            manager_stats[manager_id]['draws'] += club['draws']
                            manager_stats[manager_id]['losses'] += club['losses']
                            manager_stats[manager_id]['position'] = club['position']
                            manager_stats[manager_id]['position_points'] = (len(result['table']) - club['position'] + 1) * 2
        
        # Export results
        self.export_to_csv(all_results, winners, manager_stats)
        
        print(f"\n🎉 Season {self.season_number} Complete!")
        print(f"📊 Results exported to CSV files")
        
        return all_results
    
    def export_to_csv(self, all_results, winners, manager_stats):
        """Export results to CSV files"""
        # Main results file
        csv_filename = "multi_league_results.csv"
        
        # Determine if we're appending or creating new
        file_exists = os.path.exists(csv_filename)
        mode = 'a' if file_exists else 'w'
        
        with open(csv_filename, mode, newline='', encoding='utf-8') as f:
            fieldnames = ['Season', 'League', 'Position', 'Club', 'Matches', 'Wins', 'Draws', 'Losses', 
                         'Goals_For', 'Goals_Against', 'Goal_Difference', 'Points']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for result in all_results:
                for club in result['table']:
                    writer.writerow({
                        'Season': self.season_number,
                        'League': result['league_name'],
                        'Position': club['position'],
                        'Club': club['club_name'],
                        'Matches': club['matches'],
                        'Wins': club['wins'],
                        'Draws': club['draws'],
                        'Losses': club['losses'],
                        'Goals_For': club['goals_for'],
                        'Goals_Against': club['goals_against'],
                        'Goal_Difference': club['goal_difference'],
                        'Points': club['points']
                    })
        
        # Winners file for this season
        winners_filename = f"league_winners_season_{self.season_number}.csv"
        with open(winners_filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['League', 'Champion', 'Points', 'Goal_Difference']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for winner in winners:
                writer.writerow(winner)
        
        # Manager rankings file
        manager_filename = f"manager_rankings_season_{self.season_number}.csv"
        with open(manager_filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Name', 'Club', 'League', 'Position', 'Wins', 'Draws', 'Losses', 'Points', 'Position_Points']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Sort managers by position points (higher is better)
            sorted_managers = sorted(manager_stats.values(), key=lambda x: x['position_points'], reverse=True)
            
            for manager in sorted_managers:
                writer.writerow({
                    'Name': manager['name'],
                    'Club': manager['club'],
                    'League': manager['league'],
                    'Position': manager['position'],
                    'Wins': manager['wins'],
                    'Draws': manager['draws'],
                    'Losses': manager['losses'],
                    'Points': manager['points'],
                    'Position_Points': manager['position_points']
                })
        
        print(f"✅ Exported results to {csv_filename}")
        print(f"✅ Exported winners to {winners_filename}")
        print(f"✅ Exported manager rankings to {manager_filename}")
    
    def display_league_selection(self):
        """Display available leagues for selection"""
        print("\n📋 Available leagues:")
        print("-" * 60)
        
        # Sort leagues alphabetically by name
        sorted_leagues = sorted(self.leagues.items(), key=lambda x: x[1].get('name', x[0]))
        
        # Display as a compact grid with numbers
        for i, (league_id, league) in enumerate(sorted_leagues, 1):
            print(f"{i:2}. {league.get('name', league_id):<25}", end=" ")
            if i % 3 == 0:  # 3 columns
                print()
        
        # Add final newline if needed
        if len(sorted_leagues) % 3 != 0:
            print()
        
        print("-" * 60)
        return sorted_leagues
    
    def simulate_specific_league(self):
        """Simulate a specific league selected by the user"""
        sorted_leagues = self.display_league_selection()
        
        try:
            selection = input("\nEnter league number to simulate (or 0 to return): ")
            if selection == "0":
                return
            
            index = int(selection) - 1
            if 0 <= index < len(sorted_leagues):
                league_id, league = sorted_leagues[index]
                result = self.simulate_league_season(league_id)
                
                if result:
                    # Export just this league to a specific CSV
                    with open(f"{league_id}_season_{self.season_number}.csv", 'w', newline='', encoding='utf-8') as f:
                        fieldnames = ['Position', 'Club', 'Matches', 'Wins', 'Draws', 'Losses', 
                                    'Goals_For', 'Goals_Against', 'Goal_Difference', 'Points']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        for club in result['table']:
                            writer.writerow({
                                'Position': club['position'],
                                'Club': club['club_name'],
                                'Matches': club['matches'],
                                'Wins': club['wins'],
                                'Draws': club['draws'],
                                'Losses': club['losses'],
                                'Goals_For': club['goals_for'],
                                'Goals_Against': club['goals_against'],
                                'Goal_Difference': club['goal_difference'],
                                'Points': club['points']
                            })
                    
                    print(f"\n✅ League table exported to {league_id}_season_{self.season_number}.csv")
            else:
                print("❌ Invalid selection")
        except (ValueError, IndexError):
            print("❌ Invalid selection")
    
    def display_data_summary(self):
        """Display summary of loaded data"""
        print("\n📊 Simulation Data Summary:")
        print("-" * 60)
        
        print(f"Leagues: {len(self.leagues)}")
        for league_id, league in self.leagues.items():
            club_count = len(self.clubs_by_league.get(league_id, []))
            print(f"  - {league.get('name', league_id):<25}: {club_count} clubs")
        
        club_count = sum(len(clubs) for clubs in self.clubs_by_league.values())
        print(f"\nTotal Clubs: {club_count}")
        
        print(f"Total Managers: {len(self.managers)}")
        
        player_count = sum(len(players) for players in self.players_by_club.values())
        print(f"Total Players: {player_count}")
        
        print(f"\nCurrent Season: {self.season_number}")
        print("-" * 60)


def main():
    """Main function to run the multi-league simulation"""
    try:
        # Default to all leagues
        specific_leagues = None
        
        # Check for command-line arguments for specific leagues
        import sys
        if len(sys.argv) > 1:
            if sys.argv[1] == "--epl-only":
                specific_leagues = ["league_epl"]
                print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 EPL Only Mode")
            elif sys.argv[1] == "--top5":
                specific_leagues = ["league_epl", "league_laliga", "league_ger_bundesliga", 
                                  "league_ita_seriea", "league_fra_ligue1"]
                print("🌟 Top 5 Leagues Mode")
        
        simulator = MultiLeagueSimulator(specific_leagues)
        
        print("\n🌍 Multi-League Football Simulator")
        print("=" * 50)
        print("1. Simulate all leagues")
        print("2. Simulate specific league")
        print("3. Show data summary")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            simulator.run_all_leagues()
        elif choice == "2":
            simulator.simulate_specific_league()
        elif choice == "3":
            simulator.display_data_summary()
        elif choice == "4":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n👋 Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
