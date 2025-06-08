#!/usr/bin/env python3
"""
English Premier League Season Simulation
Focus on just EPL first to understand the data structures
"""

import json
import random
import os
import csv
from datetime import datetime
from collections import defaultdict


class EPLSeasonSimulator:
    def __init__(self):
        """Initialize the EPL season simulator"""
        self.league_id = "league_epl"
        self.league_name = "English Premier League"
        self.clubs = []
        self.players = {}
        self.managers = {}
        self.season_number = 1
        self.load_data()
        self.determine_season_number()
    
    def load_data(self):
        """Load EPL specific data"""
        print("📂 Loading EPL data...")
        
        # Load EPL clubs
        print("  Loading clubs...")
        try:
            with open('data/leagues_clubs/00_1_clubs.json', 'r', encoding='utf-8') as f:
                self.clubs = json.load(f)
            print(f"  ✅ Loaded {len(self.clubs)} EPL clubs")
        except Exception as e:
            print(f"  ❌ Error loading clubs: {e}")
            return
        
        # Load EPL managers
        print("  Loading managers...")
        try:
            with open('data/managers/1.json', 'r', encoding='utf-8') as f:
                managers_data = json.load(f)
                # Handle the wrapper structure
                if isinstance(managers_data, dict) and 'managers' in managers_data:
                    manager_list = managers_data['managers']
                else:
                    manager_list = managers_data
                
                # Create lookup by club_id
                for manager in manager_list:
                    club_id = manager.get('current_club_id')
                    if club_id:
                        self.managers[club_id] = manager
            print(f"  ✅ Loaded {len(self.managers)} EPL managers")
        except Exception as e:
            print(f"  ❌ Error loading managers: {e}")
        
        # Load EPL players
        print("  Loading players...")
        players_loaded = 0
        for club in self.clubs:
            club_id = club.get('id')
            if club_id:
                players_file = f'data/00_1_clubs_players/{club_id}_players.json'
                try:
                    if os.path.exists(players_file):
                        with open(players_file, 'r', encoding='utf-8') as f:
                            club_players = json.load(f)
                        
                        for player in club_players:
                            player_id = player.get('id')
                            if player_id:
                                player['club_id'] = club_id
                                self.players[player_id] = player
                                players_loaded += 1
                except Exception as e:
                    print(f"    ⚠️  Error loading players for {club.get('name', club_id)}: {e}")
        
        print(f"  ✅ Loaded {players_loaded} EPL players")
        print(f"✅ EPL data loading complete!")
    
    def determine_season_number(self):
        """Determine current season number based on existing CSV files"""
        csv_filename = "epl_season_results.csv"
        if os.path.exists(csv_filename):
            try:
                with open(csv_filename, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    seasons = set()
                    for row in reader:
                        if 'Season' in row:
                            seasons.add(int(row['Season']))
                    
                    if seasons:
                        self.season_number = max(seasons) + 1
                    else:
                        self.season_number = 1
            except:
                self.season_number = 1
        else:
            self.season_number = 1
        
        print(f"🏆 Starting EPL Season {self.season_number}")
    
    def get_club_strength(self, club):
        """Calculate club strength based on available data"""
        # Base strength from club reputation
        strength = club.get('reputation', 70)
        
        # Add player strength if available
        club_id = club.get('id')
        if club_id:
            club_players = [p for p in self.players.values() if p.get('club_id') == club_id]
            if club_players:
                # Use overall ratings if available, otherwise calculate from attributes
                overalls = []
                for player in club_players:
                    overall = player.get('overall')
                    if overall:
                        overalls.append(overall)
                    else:
                        # Calculate from technical attributes if available
                        tech_attrs = player.get('technical_attributes', {})
                        if tech_attrs:
                            avg_tech = sum(tech_attrs.values()) / len(tech_attrs)
                            overalls.append(avg_tech)
                
                if overalls:
                    avg_overall = sum(overalls) / len(overalls)
                    strength = (strength + avg_overall) / 2
        
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
        
        # Add randomness using normal distribution to avoid negative goals
        home_goals = max(0, int(random.normalvariate(max(0.5, home_base_goals), 1.0)))
        away_goals = max(0, int(random.normalvariate(max(0.5, away_base_goals), 1.0)))
        
        return {
            'home_team': home_club.get('name', 'Unknown'),
            'away_team': away_club.get('name', 'Unknown'),
            'home_goals': home_goals,
            'away_goals': away_goals,
            'home_club_id': home_club.get('id'),
            'away_club_id': away_club.get('id')
        }
    
    def generate_fixtures(self):
        """Generate EPL season fixtures (each team plays each other twice - home and away)"""
        fixtures = []
        clubs = self.clubs.copy()
        n = len(clubs)
        
        # Create fixtures where each team plays each other twice (home and away)
        for i in range(n):
            for j in range(n):
                if i != j:
                    fixtures.append((clubs[i], clubs[j]))
        
        # Shuffle for randomness
        random.shuffle(fixtures)
        return fixtures
    
    def simulate_season(self):
        """Simulate a full EPL season"""
        print(f"\n🏟️  Simulating {self.league_name} Season {self.season_number}")
        print("=" * 60)
        
        if len(self.clubs) < 2:
            print(f"⚠️  Not enough clubs found ({len(self.clubs)})")
            return None
        
        # Generate fixtures
        fixtures = self.generate_fixtures()
        print(f"📅 Generated {len(fixtures)} fixtures")
        
        # Initialize league table
        table = {}
        for club in self.clubs:
            club_id = club.get('id')
            table[club_id] = {
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
            if i % 50 == 0:  # Progress indicator
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
        
        # Display results
        self.display_table(sorted_table)
        
        # Export to CSV
        self.export_to_csv(sorted_table, match_results)
        
        return {
            'table': sorted_table,
            'matches': match_results,
            'season': self.season_number
        }
    
    def display_table(self, table):
        """Display the final EPL table"""
        print(f"\n📊 {self.league_name} Season {self.season_number} Final Table:")
        print("=" * 80)
        print(f"{'Pos':<3} {'Club':<25} {'P':<3} {'W':<3} {'D':<3} {'L':<3} {'GF':<3} {'GA':<3} {'GD':<4} {'Pts':<3}")
        print("=" * 80)
        
        for club in table:
            # Add qualification info
            position = club['position']
            if position <= 4:
                qual = "🏆 UCL"
            elif position == 5:
                qual = "🥉 UEL"
            elif position >= 18:
                qual = "⬇️ REL"
            else:
                qual = ""
            
            print(f"{club['position']:<3} {club['club_name'][:25]:<25} "
                  f"{club['matches']:<3} {club['wins']:<3} {club['draws']:<3} {club['losses']:<3} "
                  f"{club['goals_for']:<3} {club['goals_against']:<3} {club['goal_difference']:>+4} {club['points']:<3} {qual}")
        
        print("=" * 80)
        print("🏆 UCL = Champions League, 🥉 UEL = Europa League, ⬇️ REL = Relegation")
        
        # Show top performers
        winner = table[0]
        print(f"\n🏆 EPL CHAMPION: {winner['club_name']} ({winner['points']} points)")
        
        if len(table) >= 4:
            ucl_teams = [club['club_name'] for club in table[:4]]
            print(f"🏆 Champions League: {', '.join(ucl_teams)}")
        
        if len(table) >= 5:
            print(f"🥉 Europa League: {table[4]['club_name']}")
        
        if len(table) >= 18:
            relegated = [club['club_name'] for club in table[-3:]]
            print(f"⬇️ Relegated: {', '.join(relegated)}")
    
    def export_to_csv(self, table, matches):
        """Export results to CSV files"""
        # Main results file
        csv_filename = "epl_season_results.csv"
        
        # Determine if we're appending or creating new
        file_exists = os.path.exists(csv_filename)
        mode = 'a' if file_exists else 'w'
        
        with open(csv_filename, mode, newline='', encoding='utf-8') as f:
            fieldnames = ['Season', 'Position', 'Club', 'Matches', 'Wins', 'Draws', 'Losses', 
                         'Goals_For', 'Goals_Against', 'Goal_Difference', 'Points']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for club in table:
                writer.writerow({
                    'Season': self.season_number,
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
        
        # Matches file for this season
        matches_filename = f"epl_season_{self.season_number}_matches.csv"
        with open(matches_filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Home_Team', 'Away_Team', 'Home_Goals', 'Away_Goals']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for match in matches:
                writer.writerow({
                    'Home_Team': match['home_team'],
                    'Away_Team': match['away_team'],
                    'Home_Goals': match['home_goals'],
                    'Away_Goals': match['away_goals']
                })
        
        print(f"\n✅ Results exported to {csv_filename}")
        print(f"✅ Matches exported to {matches_filename}")
    
    def display_manager_info(self):
        """Display manager information"""
        print(f"\n👔 EPL Manager Information:")
        print("-" * 60)
        
        manager_stats = []
        for club in self.clubs:
            club_id = club.get('id')
            club_name = club.get('name', 'Unknown')
            manager = self.managers.get(club_id)
            
            if manager:
                manager_stats.append({
                    'club': club_name,
                    'manager': manager.get('name', 'Unknown'),
                    'nationality': manager.get('nationality_code', 'Unknown'),
                    'ability': manager.get('manager_ability', 0),
                    'formation': manager.get('preferred_formation', 'Unknown')
                })
            else:
                manager_stats.append({
                    'club': club_name,
                    'manager': 'No manager assigned',
                    'nationality': 'N/A',
                    'ability': 0,
                    'formation': 'N/A'
                })
        
        # Sort by manager ability
        manager_stats.sort(key=lambda x: x['ability'], reverse=True)
        
        for i, stats in enumerate(manager_stats, 1):
            print(f"{i:2}. {stats['club'][:20]:<20} | {stats['manager'][:15]:<15} | "
                  f"{stats['nationality']} | {stats['ability']:2} | {stats['formation']}")


def main():
    """Main function to run the EPL simulation"""
    try:
        simulator = EPLSeasonSimulator()
        
        print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League Simulator")
        print("=" * 50)
        print("1. Simulate full season")
        print("2. Show manager info")
        print("3. Show data summary")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            result = simulator.simulate_season()
            if result:
                print(f"\n🎉 Season {result['season']} simulation complete!")
        elif choice == "2":
            simulator.display_manager_info()
        elif choice == "3":
            print(f"\n📊 EPL Data Summary:")
            print(f"  Clubs: {len(simulator.clubs)}")
            print(f"  Players: {len(simulator.players)}")
            print(f"  Managers: {len(simulator.managers)}")
            print(f"  Season: {simulator.season_number}")
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
