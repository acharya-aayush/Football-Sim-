#!/usr/bin/env python3
"""
Champions League Simulator
A working simulation of the UEFA Champions League
"""

import json
import random
import os

def load_leagues():
    """Load league data"""
    with open('data/leagues.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_all_clubs():
    """Load all clubs from all leagues"""
    clubs = {}
    clubs_by_league = {}
    
    clubs_dir = 'data/leagues_clubs'
    for filename in os.listdir(clubs_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(clubs_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            club_data = json.load(f)
        
        # Handle different file formats
        if isinstance(club_data, list):
            club_list = club_data
        else:
            club_list = club_data.get('clubs', [])
        
        for club in club_list:
            club_id = club.get('id', club.get('club_id'))
            league_id = club.get('league_id')
            
            if club_id and league_id:
                clubs[club_id] = club
                if league_id not in clubs_by_league:
                    clubs_by_league[league_id] = []
                clubs_by_league[league_id].append(club)
    
    return clubs, clubs_by_league

def calculate_club_rating(club):
    """Calculate a club's overall rating"""
    # Base rating from reputation
    reputation = club.get('attributes', {}).get('reputation', 60)
    
    # Financial strength
    financials = club.get('financials', {})
    budget = financials.get('transfer_budget_initial', 1000000)
    wages = financials.get('wage_budget_weekly_total', 50000)
    
    # Financial score (0-20 range)
    financial_score = min(20, (budget / 1000000) + (wages / 50000))
    
    # Historical success
    history = club.get('history', {})
    titles = history.get('league_titles_domestic', 0)
    continental = history.get('continental_cup_wins', 0)
    
    # Historical score (0-20 range)
    historical_score = min(20, titles + continental * 3)
    
    return min(100, reputation + financial_score + historical_score)

def get_ucl_qualifiers(clubs_by_league):
    """Get Champions League qualified teams"""
    # UCL qualification spots
    ucl_spots = {
        'league_epl': 4,
        'league_laliga': 4, 
        'league_ger_bundesliga': 4,
        'league_ita_seriea': 4,
        'league_fra_ligue1': 3,
        'league_eredivisie': 1,
        'league_primeira': 1,
        'league_russian': 1,
        'league_scottish': 1,
        'league_austrian': 1,
        'league_greek': 1,
        'league_turkish': 1,
        'league_belgian': 1,
        'league_swiss': 1,
        'league_ukrainian': 1
    }
    
    qualified = []
    
    for league_id, spots in ucl_spots.items():
        if league_id in clubs_by_league:
            league_clubs = clubs_by_league[league_id]
            
            # Sort by rating and take top clubs
            rated_clubs = [(club, calculate_club_rating(club)) for club in league_clubs]
            rated_clubs.sort(key=lambda x: x[1], reverse=True)
            
            for i in range(min(spots, len(rated_clubs))):
                club, rating = rated_clubs[i]
                qualified.append({
                    'id': club.get('id', club.get('club_id')),
                    'name': club['name'],
                    'league': league_id,
                    'rating': rating,
                    'position': i + 1
                })
    
    return qualified[:36]  # UEFA allows 36 teams maximum

def simulate_match(team1, team2):
    """Simulate a match between two teams"""
    # Strength difference affects goal probability
    strength_diff = team1['rating'] - team2['rating']
    
    # Base goal expectation
    team1_goals_expected = 1.5 + (strength_diff / 100)
    team2_goals_expected = 1.5 - (strength_diff / 100)
    
    # Add randomness and ensure minimum
    team1_goals_expected = max(0.2, team1_goals_expected + random.uniform(-0.5, 0.5))
    team2_goals_expected = max(0.2, team2_goals_expected + random.uniform(-0.5, 0.5))
    
    # Generate goals (simplified Poisson)
    team1_goals = max(0, int(random.normalvariate(team1_goals_expected, 1.0)))
    team2_goals = max(0, int(random.normalvariate(team2_goals_expected, 1.0)))
    
    return team1_goals, team2_goals

def simulate_group_stage(teams):
    """Simulate the Champions League group stage"""
    print("🏆 UEFA CHAMPIONS LEAGUE - GROUP STAGE")
    print("=" * 50)
    
    # Create 9 groups of 4 teams each (simplified from new 36-team format)
    groups = []
    team_list = teams.copy()
    random.shuffle(team_list)
    
    for group_num in range(9):
        group_teams = team_list[group_num*4:(group_num+1)*4]
        if len(group_teams) == 4:
            groups.append(group_teams)
    
    qualified_teams = []
    
    for group_idx, group in enumerate(groups):
        print(f"\nGroup {chr(65 + group_idx)}:")
        
        # Initialize records
        records = {}
        for team in group:
            records[team['id']] = {
                'team': team,
                'points': 0,
                'goals_for': 0,
                'goals_against': 0,
                'matches': 0
            }
        
        # Play round-robin (each team plays each other twice)
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                team1, team2 = group[i], group[j]
                
                # First match
                goals1, goals2 = simulate_match(team1, team2)
                
                # Update records
                records[team1['id']]['goals_for'] += goals1
                records[team1['id']]['goals_against'] += goals2
                records[team2['id']]['goals_for'] += goals2
                records[team2['id']]['goals_against'] += goals1
                records[team1['id']]['matches'] += 1
                records[team2['id']]['matches'] += 1
                
                if goals1 > goals2:
                    records[team1['id']]['points'] += 3
                elif goals2 > goals1:
                    records[team2['id']]['points'] += 3
                else:
                    records[team1['id']]['points'] += 1
                    records[team2['id']]['points'] += 1
                
                # Second match (home/away reversed)
                goals2_return, goals1_return = simulate_match(team2, team1)
                
                records[team1['id']]['goals_for'] += goals1_return
                records[team1['id']]['goals_against'] += goals2_return
                records[team2['id']]['goals_for'] += goals2_return
                records[team2['id']]['goals_against'] += goals1_return
                records[team1['id']]['matches'] += 1
                records[team2['id']]['matches'] += 1
                
                if goals1_return > goals2_return:
                    records[team1['id']]['points'] += 3
                elif goals2_return > goals1_return:
                    records[team2['id']]['points'] += 3
                else:
                    records[team1['id']]['points'] += 1
                    records[team2['id']]['points'] += 1
        
        # Sort group and get top 2
        group_table = sorted(records.values(), 
                           key=lambda x: (x['points'], x['goals_for'] - x['goals_against']), 
                           reverse=True)
        
        # Display group table
        for pos, record in enumerate(group_table, 1):
            gd = record['goals_for'] - record['goals_against']
            print(f"  {pos}. {record['team']['name'][:20]:20} {record['points']:2}pts {gd:+3}gd")
        
        # Top 2 advance
        qualified_teams.extend([record['team'] for record in group_table[:2]])
    
    print(f"\n✅ {len(qualified_teams)} teams advance to Round of 16")
    return qualified_teams

def simulate_knockout_round(teams, round_name):
    """Simulate a knockout round"""
    print(f"\n{round_name.upper()}:")
    print("-" * 30)
    
    random.shuffle(teams)
    winners = []
    
    for i in range(0, len(teams), 2):
        if i + 1 < len(teams):
            team1, team2 = teams[i], teams[i + 1]
            
            # First leg
            goals1_home, goals2_away = simulate_match(team1, team2)
            
            # Second leg
            goals2_home, goals1_away = simulate_match(team2, team1)
            
            # Calculate aggregate
            team1_total = goals1_home + goals1_away
            team2_total = goals2_away + goals2_home
            
            print(f"  {team1['name']} vs {team2['name']}")
            print(f"    First leg:  {team1['name']} {goals1_home}-{goals2_away} {team2['name']}")
            print(f"    Second leg: {team2['name']} {goals2_home}-{goals1_away} {team1['name']}")
            print(f"    Aggregate:  {team1['name']} {team1_total}-{team2_total} {team2['name']}")
            
            if team1_total > team2_total:
                winner = team1
                print(f"    Winner: {team1['name']} ✓")
            elif team2_total > team1_total:
                winner = team2
                print(f"    Winner: {team2['name']} ✓")
            else:
                # Away goals or penalties (simplified to random)
                winner = random.choice([team1, team2])
                print(f"    Winner: {winner['name']} (penalties) ✓")
            
            winners.append(winner)
            print()
    
    return winners

def main():
    """Main Champions League simulation"""
    print("🏆 UEFA CHAMPIONS LEAGUE SIMULATOR 🏆")
    print("=" * 50)
    
    try:
        # Load data
        print("Loading data...")
        leagues = load_leagues()
        clubs, clubs_by_league = load_all_clubs()
        
        print(f"✅ Loaded {len(clubs)} clubs from {len(clubs_by_league)} leagues")
        
        # Get UCL qualifiers
        qualified_teams = get_ucl_qualifiers(clubs_by_league)
        print(f"✅ {len(qualified_teams)} teams qualified for Champions League")
        
        # Show qualified teams by league
        print(f"\nQualified teams by league:")
        current_league = None
        for team in sorted(qualified_teams, key=lambda x: x['league']):
            if team['league'] != current_league:
                current_league = team['league']
                league_name = next((l['name'] for l in leagues if l['id'] == current_league), current_league)
                print(f"\n{league_name}:")
            print(f"  {team['position']}. {team['name']} (Rating: {team['rating']:.1f})")
        
        # Run tournament
        print(f"\n🚀 Starting Champions League simulation...")
        
        # Group stage
        round_of_16_teams = simulate_group_stage(qualified_teams)
        
        # Knockout rounds
        quarter_finalists = simulate_knockout_round(round_of_16_teams, "Round of 16")
        semi_finalists = simulate_knockout_round(quarter_finalists, "Quarter-Finals")
        finalists = simulate_knockout_round(semi_finalists, "Semi-Finals")
        
        # Final
        if len(finalists) >= 2:
            print(f"\nFINAL:")
            print("=" * 20)
            team1, team2 = finalists[0], finalists[1]
            goals1, goals2 = simulate_match(team1, team2)
            
            print(f"{team1['name']} {goals1}-{goals2} {team2['name']}")
            
            if goals1 > goals2:
                champion = team1
            elif goals2 > goals1:
                champion = team2
            else:
                # Extra time/penalties
                champion = random.choice([team1, team2])
                print("(After extra time and penalties)")
            
            print(f"\n🎉 CHAMPIONS LEAGUE WINNER: {champion['name']} 🎉")
            print(f"🏆 {champion['name']} are the Champions of Europe! 🏆")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
