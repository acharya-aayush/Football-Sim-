"""
Complete European Competition System
Integrates Champions League and Europa League simulations
"""

import json
import random
import os
from collections import defaultdict

class CompleteEuropeanSystem:
    def __init__(self):
        """Initialize the complete European competition system"""
        self.load_data()
        
    def load_data(self):
        """Load leagues, clubs, and manager data"""
        # Load leagues configuration
        with open('data/leagues.json', 'r', encoding='utf-8') as f:
            leagues_data = json.load(f)
        
        self.leagues = {league['id']: league for league in leagues_data}
        self.clubs_by_league = {}
        self.all_clubs = {}
        
        # Load all clubs data
        leagues_clubs_dir = 'data/leagues_clubs'
        for filename in os.listdir(leagues_clubs_dir):
            if filename.endswith('_clubs.json'):
                league_name = filename.replace('_clubs.json', '').replace('league_', '')
                file_path = os.path.join(leagues_clubs_dir, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    clubs = json.load(f)
                
                # Handle different file structures
                if isinstance(clubs, list):
                    club_list = clubs
                else:
                    club_list = clubs.get('clubs', [])
                
                for club in club_list:
                    club_id = club.get('id') or club.get('club_id')
                    league_id = club.get('league_id', f'league_{league_name}')
                    
                    if club_id:
                        self.all_clubs[club_id] = club
                        if league_id not in self.clubs_by_league:
                            self.clubs_by_league[league_id] = []
                        self.clubs_by_league[league_id].append(club)

    def get_ucl_qualified_teams(self, season_results=None):
        """Get teams qualified for Champions League"""
        ucl_config = self.leagues.get('competition_ucl')
        if not ucl_config:
            return []
        
        qualified_teams = []
        
        # Get teams from domestic leagues based on qualification criteria
        for league_id, criteria in ucl_config['qualification_criteria']['domestic_leagues'].items():
            if league_id not in self.clubs_by_league:
                continue
                
            league_clubs = self.clubs_by_league[league_id]
            spots = criteria['spots']
            
            if season_results and league_id in season_results:
                # Use actual season results
                top_clubs = season_results[league_id][:spots]
            else:
                # Simulate based on club reputation
                sorted_clubs = sorted(league_clubs, 
                                    key=lambda x: self.get_club_strength(x), 
                                    reverse=True)
                top_clubs = sorted_clubs[:spots]
            
            for club in top_clubs:
                qualified_teams.append({
                    'club_id': club.get('id') or club.get('club_id'),
                    'club_name': club['name'],
                    'league_id': league_id,
                    'qualification_type': 'league_position',
                    'strength': self.get_club_strength(club)
                })
        
        return qualified_teams[:ucl_config['qualification_criteria']['total_teams']]

    def get_uel_qualified_teams(self, season_results=None, ucl_teams=None):
        """Get teams qualified for Europa League"""
        uel_config = self.leagues.get('competition_uel')
        if not uel_config:
            return []
        
        qualified_teams = []
        ucl_club_ids = set()
        
        # Get UCL team IDs to exclude them
        if ucl_teams:
            ucl_club_ids = {team['club_id'] for team in ucl_teams}
        
        # Get teams from domestic leagues
        for league_id, criteria in uel_config['qualification_criteria']['domestic_leagues'].items():
            if league_id not in self.clubs_by_league:
                continue
                
            league_clubs = self.clubs_by_league[league_id]
            spots = criteria['spots']
            
            if season_results and league_id in season_results:
                # Use actual season results, skip UCL qualified teams
                available_clubs = [club for club in season_results[league_id] 
                                 if club.get('id', club.get('club_id')) not in ucl_club_ids]
                top_clubs = available_clubs[:spots]
            else:
                # Simulate based on club reputation, skip UCL teams
                available_clubs = [club for club in league_clubs 
                                 if club.get('id', club.get('club_id')) not in ucl_club_ids]
                sorted_clubs = sorted(available_clubs, 
                                    key=lambda x: self.get_club_strength(x), 
                                    reverse=True)
                top_clubs = sorted_clubs[:spots]
            
            for club in top_clubs:
                qualified_teams.append({
                    'club_id': club.get('id') or club.get('club_id'),
                    'club_name': club['name'],
                    'league_id': league_id,
                    'qualification_type': 'league_position',
                    'strength': self.get_club_strength(club)
                })
        
        # Add UCL dropouts (simulated)
        if ucl_teams and len(ucl_teams) >= 8:
            ucl_dropouts = random.sample(ucl_teams, 8)
            for team in ucl_dropouts:
                qualified_teams.append({
                    'club_id': team['club_id'],
                    'club_name': team['club_name'],
                    'league_id': team['league_id'],
                    'qualification_type': 'ucl_dropout',
                    'strength': team['strength']
                })
        
        return qualified_teams[:uel_config['qualification_criteria']['total_teams']]

    def get_club_strength(self, club):
        """Calculate club strength based on a more comprehensive model."""
        
        # Default values
        squad_overall_rating = 0  # Placeholder: Ideally average of player ratings
        manager_impact_score = 0  # Placeholder: Ideally from manager-specific stats
        european_pedigree_score = 0
        star_player_factor = 0    # Placeholder: Ideally count of 5-star players * bonus
        financial_clout = 0

        # 1. Squad Overall Rating (Conceptual - requires player data access)
        # For now, we can use a proxy or a default. Let's use training facilities + youth academy as a rough proxy.
        # Ideally: Iterate through club's players, get their overall rating, and average them.
        # squad_overall_rating = average_player_ratings_for_club(club_id) # This function would need to be implemented
        attributes = club.get('attributes', {})
        squad_overall_rating_proxy = (attributes.get('youth_academy_rating', 10) + attributes.get('training_facilities_rating', 10)) * 2.5 # Scale to ~50-100
        squad_overall_rating = squad_overall_rating_proxy # Using proxy for now

        # 2. Manager Impact Score (Conceptual - requires manager data access)
        # Ideally: Fetch manager data using manager_id and use their tactical ratings, experience, etc.
        # manager_data = self.managers.get(club.get('manager_details', {}).get('manager_id'))
        # if manager_data:
        #     manager_impact_score = manager_data.get('tactical_ability', 60) + manager_data.get('experience', 0) / 2
        # For now, using a default or a simple proxy if some manager info is in club object.
        # The current club object only has manager_name and manager_id in 'manager_details'.
        # Let's assume a base value or a small bonus if a manager is listed.
        if club.get('manager_details', {}).get('manager_id'):
            manager_impact_score = 60 # Base score for having a manager, ideally fetch detailed stats
        else:
            manager_impact_score = 40 # Lower score if no manager listed

        # 3. European Pedigree Score
        history = club.get('history', {})
        # continental_cup_wins is a direct field in some club data structures.
        # Or sum specific cups if available.
        european_titles = history.get('continental_cup_wins', 0)
        if european_titles == 0: # If 'continental_cup_wins' is not present or zero, try summing individual cups
            european_titles = (history.get('european_cup_wins', 0) + # UCL/European Cup
                               history.get('uefa_cup_wins', 0) +     # UEL/UEFA Cup
                               history.get('cup_winners_cup_wins', 0)) # Defunct Cup Winners' Cup
        
        # European_Pedigree_Score: Combines historical titles and recent UCL/UEL performance.
        # Recent performance is hard to track without season-by-season data.
        # For now, titles * a multiplier.
        european_pedigree_score = european_titles * 5 # Each title adds 5 points to this component

        # 4. Star Player Factor (Conceptual - requires player data access)
        # Ideally: Count players with overall_rating > X (e.g., > 85 for 5-star)
        # num_star_players = count_star_players_in_club(club_id) # This function would need to be implemented
        # star_player_factor = num_star_players * 2 # Each star player adds 2 points
        # Using key_player_ids as a proxy if available
        key_players = club.get('squad_meta', {}).get('key_player_ids', [])
        star_player_factor = len(key_players) * 1.5 # Each key player adds 1.5 points as a proxy

        # 5. Financial Clout
        financials = club.get('financials', {})
        transfer_budget = financials.get('transfer_budget_initial', 0)
        wage_budget = financials.get('wage_budget_weekly_total', 0) * 52 / 1000000 # Annualized wage budget in millions
        revenue = financials.get('annual_revenue_approx', 0) / 1000000 # Revenue in millions

        # Normalize and combine financial metrics. Max score around 100 for this component.
        # Example: (Transfer Budget / 2M) + (Annual Wage Budget / 1M) + (Revenue / 5M)
        # Cap each part to avoid extreme values from dominating.
        financial_clout_raw = (min(transfer_budget / 2000000, 40) + 
                               min(wage_budget / 1, 30) +            
                               min(revenue / 5, 30))
        financial_clout = min(financial_clout_raw, 100) # Cap at 100

        # Calculate weighted total_strength
        total_strength = (squad_overall_rating * 0.35) + \
                         (manager_impact_score * 0.25) + \
                         (european_pedigree_score * 0.20) + \
                         (star_player_factor * 0.10) + \
                         (financial_clout * 0.10)
        
        # Ensure strength is within a reasonable range (e.g., 30-100)
        return max(30, min(100, total_strength))

    def simulate_match(self, home_team, away_team):
        """Simulate a single match between two teams"""
        home_strength = home_team['strength']
        away_strength = away_team['strength']
        
        # Home advantage
        home_strength *= 1.1
        
        # Calculate goal probabilities based on strength difference
        strength_diff = home_strength - away_strength
        
        # Base goals expectation
        home_goals_expected = 1.3 + (strength_diff / 100)
        away_goals_expected = 1.1 - (strength_diff / 100)
        
        # Ensure minimum goals expectation
        home_goals_expected = max(0.3, home_goals_expected)
        away_goals_expected = max(0.3, away_goals_expected)
        
        # Generate goals using Poisson-like distribution
        home_goals = max(0, int(random.gauss(home_goals_expected, 1.2)))
        away_goals = max(0, int(random.gauss(away_goals_expected, 1.2)))
        
        return {
            'home_goals': home_goals,
            'away_goals': away_goals,
            'home_team_name': home_team['club_name'],
            'away_team_name': away_team['club_name']
        }

    def update_team_record(self, record, match_result, home_away):
        """Update team record based on match result"""
        record['matches'] += 1
        
        if home_away == 'home':
            goals_for = match_result['home_goals']
            goals_against = match_result['away_goals']
        else:
            goals_for = match_result['away_goals']
            goals_against = match_result['home_goals']
        
        record['goals_for'] += goals_for
        record['goals_against'] += goals_against
        record['goal_difference'] = record['goals_for'] - record['goals_against']
        
        if goals_for > goals_against:
            record['wins'] += 1
            record['points'] += 3
        elif goals_for == goals_against:
            record['draws'] += 1
            record['points'] += 1
        else:
            record['losses'] += 1

    def simulate_league_phase(self, teams, competition_name):
        """Simulate the league phase (Swiss system) for UCL or UEL"""
        print(f"\n🏆 {competition_name.upper()} - LEAGUE PHASE")
        print("=" * 60)
        print(f"📊 {len(teams)} teams competing in league phase")
        
        # Initialize team records
        team_records = {}
        for team in teams:
            team_records[team['club_id']] = {
                'name': team['club_name'],
                'league_id': team['league_id'],
                'strength': team['strength'],
                'matches': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0,
                'points': 0
            }
        
        # Generate and simulate matches (each team plays 8 matches)
        all_matches = []
        matches_per_team = 8
        
        # Simple fixture generation
        for team in teams:
            team_id = team['club_id']
            current_matches = team_records[team_id]['matches']
            needed_matches = matches_per_team - current_matches
            
            if needed_matches > 0:
                available_opponents = [t for t in teams if t['club_id'] != team_id and 
                                     team_records[t['club_id']]['matches'] < matches_per_team]
                
                if len(available_opponents) >= needed_matches:
                    opponents = random.sample(available_opponents, needed_matches)
                else:
                    opponents = available_opponents
                
                for opponent in opponents:
                    match = {
                        'home_team': team,
                        'away_team': opponent,
                        'matchday': len(all_matches) // (len(teams) // 2) + 1
                    }
                    all_matches.append(match)
                    
                    # Simulate the match
                    match_result = self.simulate_match(team, opponent)
                    match.update(match_result)
                    
                    # Update records
                    self.update_team_record(team_records[team['club_id']], match_result, 'home')
                    self.update_team_record(team_records[opponent['club_id']], match_result, 'away')
        
        # Sort teams by points, goal difference, goals scored
        sorted_teams = sorted(team_records.values(), 
                            key=lambda x: (x['points'], x['goal_difference'], x['goals_for']), 
                            reverse=True)
        
        # Display league phase table
        print(f"\nFinal League Phase Table:")
        print("=" * 80)
        print(f"{'Pos':<4} {'Team':<25} {'P':<3} {'W':<3} {'D':<3} {'L':<3} {'GF':<4} {'GA':<4} {'GD':<5} {'Pts':<4}")
        print("-" * 80)
        
        for i, team in enumerate(sorted_teams, 1):
            print(f"{i:<4} {team['name'][:24]:<25} {team['matches']:<3} {team['wins']:<3} "
                  f"{team['draws']:<3} {team['losses']:<3} {team['goals_for']:<4} "
                  f"{team['goals_against']:<4} {team['goal_difference']:+5} {team['points']:<4}")
        
        # Determine knockout phase qualifiers
        knockout_qualifiers = sorted_teams[:16]  # Top 16 advance
        print(f"\n🏆 TOP 16 ADVANCE TO KNOCKOUT PHASE")
        
        print("\nKnockout Phase Qualifiers:")
        for i, team in enumerate(knockout_qualifiers, 1):
            print(f"{i:2}. {team['name']} ({team['points']} pts)")
        
        return knockout_qualifiers, all_matches

    def simulate_knockout_phase(self, qualified_teams, competition_name):
        """Simulate knockout phase from Round of 16 to Final"""
        print(f"\n🏆 {competition_name.upper()} - KNOCKOUT PHASE")
        print("=" * 60)
        
        current_teams = qualified_teams.copy()
        rounds = ['Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
        
        for round_name in rounds:
            print(f"\n--- {round_name} ---")
            
            if round_name == 'Final':
                # Single match final
                if len(current_teams) == 2:
                    final_result = self.simulate_knockout_match(
                        current_teams[0], current_teams[1], single_leg=True
                    )
                    winner = final_result['winner']
                    
                    print(f"\n🏆 {competition_name.upper()} FINAL")
                    print(f"⚽ {final_result['home_team_name']} {final_result['home_goals']}-{final_result['away_goals']} {final_result['away_team_name']}")
                    
                    if final_result.get('penalties'):
                        print(f"🥅 Penalties: {final_result['home_penalties']}-{final_result['away_penalties']}")
                    
                    print(f"\n🎉 {competition_name.upper()} WINNER: {winner['name']}!")
                    
                    return {
                        'winner': winner,
                        'final_result': final_result,
                        'runner_up': current_teams[1] if winner == current_teams[0] else current_teams[0]
                    }
            else:
                # Two-legged ties
                next_round_teams = []
                
                # Pair teams for matches
                random.shuffle(current_teams)
                for i in range(0, len(current_teams), 2):
                    if i + 1 < len(current_teams):
                        team1 = current_teams[i]
                        team2 = current_teams[i + 1]
                        
                        tie_result = self.simulate_two_legged_tie(team1, team2)
                        winner = tie_result['winner']
                        
                        print(f"⚽ {team1['name']} vs {team2['name']}")
                        print(f"   Leg 1: {tie_result['leg1']['home_team_name']} {tie_result['leg1']['home_goals']}-{tie_result['leg1']['away_goals']} {tie_result['leg1']['away_team_name']}")
                        print(f"   Leg 2: {tie_result['leg2']['home_team_name']} {tie_result['leg2']['home_goals']}-{tie_result['leg2']['away_goals']} {tie_result['leg2']['away_team_name']}")
                        print(f"   Aggregate: {tie_result['aggregate_score']} → {winner['name']} advances")
                        
                        if tie_result.get('away_goals_rule'):
                            print(f"   (Away goals rule)")
                        elif tie_result.get('penalties'):
                            print(f"   (Penalties: {tie_result['penalties']})")
                        
                        next_round_teams.append(winner)
                
                current_teams = next_round_teams
        
        return None

    def simulate_two_legged_tie(self, team1, team2):
        """Simulate a two-legged knockout tie"""
        # First leg (team1 at home)
        leg1 = self.simulate_knockout_match(team1, team2)
        
        # Second leg (team2 at home)
        leg2 = self.simulate_knockout_match(team2, team1)
        
        # Calculate aggregate score
        team1_aggregate = leg1['home_goals'] + leg2['away_goals']
        team2_aggregate = leg1['away_goals'] + leg2['home_goals']
        
        aggregate_score = f"{team1_aggregate}-{team2_aggregate}"
        
        # Determine winner
        if team1_aggregate > team2_aggregate:
            winner = team1
        elif team2_aggregate > team1_aggregate:
            winner = team2
        else:
            # Check away goals rule
            team1_away_goals = leg2['away_goals']
            team2_away_goals = leg1['away_goals']
            
            if team1_away_goals > team2_away_goals:
                winner = team1
                return {
                    'winner': winner,
                    'leg1': leg1,
                    'leg2': leg2,
                    'aggregate_score': aggregate_score,
                    'away_goals_rule': True
                }
            elif team2_away_goals > team1_away_goals:
                winner = team2
                return {
                    'winner': winner,
                    'leg1': leg1,
                    'leg2': leg2,
                    'aggregate_score': aggregate_score,
                    'away_goals_rule': True
                }
            else:
                # Penalty shootout
                penalties = self.simulate_penalty_shootout()
                winner = team1 if penalties[0] > penalties[1] else team2
                
                return {
                    'winner': winner,
                    'leg1': leg1,
                    'leg2': leg2,
                    'aggregate_score': aggregate_score,
                    'penalties': f"{penalties[0]}-{penalties[1]}"
                }
        
        return {
            'winner': winner,
            'leg1': leg1,
            'leg2': leg2,
            'aggregate_score': aggregate_score
        }

    def simulate_knockout_match(self, home_team, away_team, single_leg=False):
        """Simulate a knockout match (can go to extra time/penalties)"""
        match_result = self.simulate_match(home_team, away_team)
        
        if single_leg and match_result['home_goals'] == match_result['away_goals']:
            # Extra time
            extra_time_home = 1 if random.random() < 0.3 else 0
            extra_time_away = 1 if random.random() < 0.3 else 0
            
            match_result['home_goals'] += extra_time_home
            match_result['away_goals'] += extra_time_away
            
            if match_result['home_goals'] == match_result['away_goals']:
                # Penalty shootout
                penalties = self.simulate_penalty_shootout()
                match_result['home_penalties'] = penalties[0]
                match_result['away_penalties'] = penalties[1]
                match_result['penalties'] = True
                
                if penalties[0] > penalties[1]:
                    match_result['winner'] = home_team
                else:
                    match_result['winner'] = away_team
            else:
                if match_result['home_goals'] > match_result['away_goals']:
                    match_result['winner'] = home_team
                else:
                    match_result['winner'] = away_team
        
        return match_result

    def simulate_penalty_shootout(self):
        """Simulate a penalty shootout"""
        home_score = 0
        away_score = 0
        
        # Regular 5 penalties each
        for i in range(5):
            if random.random() < 0.75:  # 75% conversion rate
                home_score += 1
            if random.random() < 0.75:
                away_score += 1
        
        # Sudden death if tied
        while home_score == away_score:
            if random.random() < 0.75:
                home_score += 1
            if random.random() < 0.75:
                away_score += 1
        
        return (home_score, away_score)

    def run_champions_league(self, season_results=None):
        """Run the complete Champions League competition"""
        print("\n" + "="*80)
        print("🏆 UEFA CHAMPIONS LEAGUE SIMULATION")
        print("="*80)
        
        # Get qualified teams
        qualified_teams = self.get_ucl_qualified_teams(season_results)
        
        if len(qualified_teams) < 32:
            print(f"❌ Not enough qualified teams ({len(qualified_teams)}). Need at least 32.")
            return None
        
        print(f"\n✅ {len(qualified_teams)} teams qualified for Champions League")
        
        # Simulate league phase
        league_phase_results, league_matches = self.simulate_league_phase(qualified_teams, "Champions League")
        
        # Simulate knockout phase
        knockout_results = self.simulate_knockout_phase(league_phase_results, "Champions League")
        
        if knockout_results:
            return {
                'competition': 'Champions League',
                'winner': knockout_results['winner'],
                'runner_up': knockout_results['runner_up'],
                'final_result': knockout_results['final_result'],
                'qualified_teams': qualified_teams,
                'league_phase_results': league_phase_results,
                'league_matches': league_matches
            }
        
        return None

    def run_europa_league(self, season_results=None, ucl_teams=None):
        """Run the complete Europa League competition"""
        print("\n" + "="*80)
        print("🏆 UEFA EUROPA LEAGUE SIMULATION")
        print("="*80)
        
        # Get qualified teams
        qualified_teams = self.get_uel_qualified_teams(season_results, ucl_teams)
        
        if len(qualified_teams) < 32:
            print(f"❌ Not enough qualified teams ({len(qualified_teams)}). Need at least 32.")
            return None
        
        print(f"\n✅ {len(qualified_teams)} teams qualified for Europa League")
        
        # Simulate league phase
        league_phase_results, league_matches = self.simulate_league_phase(qualified_teams, "Europa League")
        
        # Simulate knockout phase
        knockout_results = self.simulate_knockout_phase(league_phase_results, "Europa League")
        
        if knockout_results:
            return {
                'competition': 'Europa League',
                'winner': knockout_results['winner'],
                'runner_up': knockout_results['runner_up'],
                'final_result': knockout_results['final_result'],
                'qualified_teams': qualified_teams,
                'league_phase_results': league_phase_results,
                'league_matches': league_matches
            }
        
        return None

    def run_full_european_season(self, season_results=None):
        """Run both UCL and UEL competitions for a complete European season"""
        print("\n" + "="*100)
        print("🌍 COMPLETE EUROPEAN COMPETITIONS SEASON")
        print("="*100)
        
        results = {
            'ucl': None,
            'uel': None,
            'success': False
        }
        
        # Run Champions League first
        ucl_result = self.run_champions_league(season_results)
        results['ucl'] = ucl_result
        
        # Get UCL teams for UEL (for dropouts)
        ucl_teams = ucl_result.get('qualified_teams', []) if ucl_result else []
        
        # Run Europa League
        uel_result = self.run_europa_league(season_results, ucl_teams)
        results['uel'] = uel_result
        
        # Set success flag
        results['success'] = (results['ucl'] is not None and results['uel'] is not None)
        
        # Display summary
        self.display_season_summary(results)
        
        return results

    def display_season_summary(self, results):
        """Display summary of European competition results"""
        print("\n" + "="*100)
        print("🏆 EUROPEAN COMPETITIONS SEASON SUMMARY")
        print("="*100)
        
        if results['ucl']:
            ucl = results['ucl']
            print(f"\n🏆 UEFA CHAMPIONS LEAGUE:")
            print(f"   🥇 Winner: {ucl['winner']['name']}")
            print(f"   🥈 Runner-up: {ucl['runner_up']['name']}")
            print(f"   ⚽ Final: {ucl['final_result']['home_team_name']} {ucl['final_result']['home_goals']}-{ucl['final_result']['away_goals']} {ucl['final_result']['away_team_name']}")
        else:
            print(f"\n❌ Champions League: Not completed")
        
        if results['uel']:
            uel = results['uel']
            print(f"\n🏆 UEFA EUROPA LEAGUE:")
            print(f"   🥇 Winner: {uel['winner']['name']}")
            print(f"   🥈 Runner-up: {uel['runner_up']['name']}")
            print(f"   ⚽ Final: {uel['final_result']['home_team_name']} {uel['final_result']['home_goals']}-{uel['final_result']['away_goals']} {uel['final_result']['away_team_name']}")
        else:
            print(f"\n❌ Europa League: Not completed")
        
        print(f"\n✅ Season Status: {'Successfully Completed' if results['success'] else 'Incomplete'}")
        print("="*100)


def main():
    """Main function to demonstrate the complete European system"""
    print("🌍 Complete European Competition System")
    print("="*60)
    
    # Initialize system
    euro_system = CompleteEuropeanSystem()
    
    # Display system info
    print(f"\n📊 System Information:")
    print(f"   Total Leagues: {len(euro_system.clubs_by_league)}")
    print(f"   Total Clubs: {len(euro_system.all_clubs)}")
    print(f"   UCL Configuration: {'✅' if 'competition_ucl' in euro_system.leagues else '❌'}")
    print(f"   UEL Configuration: {'✅' if 'competition_uel' in euro_system.leagues else '❌'}")
    
    # Run complete European season
    if 'competition_ucl' in euro_system.leagues and 'competition_uel' in euro_system.leagues:
        print(f"\n🚀 Running complete European season...")
        results = euro_system.run_full_european_season()
        
        if results['success']:
            print(f"\n🎉 European season completed successfully!")
        else:
            print(f"\n❌ European season incomplete")
    else:
        print(f"\n❌ Missing competition configurations")


if __name__ == "__main__":
    main()
