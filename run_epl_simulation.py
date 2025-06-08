#!/usr/bin/env python3
"""
Run a complete EPL season simulation using the MultiLeagueSimulator
"""
from multi_league_simulator import MultiLeagueSimulator

print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Running EPL Season Simulation")

# Create EPL-only simulator
simulator = MultiLeagueSimulator(['league_epl'])

# Simulate EPL season
league_id = 'league_epl'
result = simulator.simulate_league_season(league_id)

if result:
    print(f"\n✅ Successfully simulated {result['league_name']} Season {simulator.season_number}")
    
    # Top teams summary
    top_teams = result['table'][:4]
    print("\n🏆 Champions League Qualifiers:")
    for i, team in enumerate(top_teams, 1):
        print(f"{i}. {team['club_name']} ({team['points']} points, GD: {team['goal_difference']})")
    
    # Relegated teams
    bottom_teams = result['table'][-3:]
    print("\n⬇️ Relegated Teams:")
    for i, team in enumerate(bottom_teams, 18):
        print(f"{i}. {team['club_name']} ({team['points']} points, GD: {team['goal_difference']})")
    
    # Export to CSV
    csv_filename = f"epl_simulation_season_{simulator.season_number}.csv"
    simulator.export_to_csv([result], [], {})
    print(f"\n📊 Results exported to CSV files")
