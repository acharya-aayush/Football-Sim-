import json

def load_players(file_path):
    """Load players from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_manager(file_path, club_id):
    """Load manager details for a specific club."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            managers_data = json.load(f)
            
        # Handle different data structures
        if isinstance(managers_data, list):
            managers = managers_data
        elif isinstance(managers_data, dict) and 'managers' in managers_data:
            managers = managers_data['managers']
        else:
            managers = managers_data
            
        for manager in managers:
            current_club = manager.get('current_club_id') or manager.get('club_id')
            if current_club == club_id:
                return manager
        return None
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None

def _calculate_position_effectiveness(player, position):
    """
    Calculate the effectiveness of a player for a given position.
    Considers player's primary, secondary, and general adaptability.
    Returns an effectiveness factor and a string indicating position type.
    """
    primary_positions = player.get('positions_primary', [])
    secondary_positions = player.get('positions_secondary', [])

    # Define base effectiveness factors
    effectiveness_map = {
        'primary': 1.0,    # Player is in their main role
        'secondary': 0.75, # Player is in a familiar secondary role
        'makeshift': 0.5,  # Player is out of position but adaptable
        'unsuitable': 0.25 # Player is in a very unsuitable role (e.g., outfield player in goal)
    }

    # Highly specialized position: Goalkeeper
    if position == 'GK':
        if 'GK' in primary_positions:
            return effectiveness_map['primary'], 'primary'
        else:
            # Any non-GK playing as GK is highly unsuitable
            return effectiveness_map['unsuitable'], 'unsuitable' 
    elif 'GK' in primary_positions and position != 'GK':
        # A GK playing out of goal is also highly unsuitable
        return effectiveness_map['unsuitable'], 'unsuitable'

    if position in primary_positions:
        return effectiveness_map['primary'], 'primary'
    elif position in secondary_positions:
        return effectiveness_map['secondary'], 'secondary'
    else:
        # General adaptability for out-of-position play
        # This could be further nuanced by player attributes like 'versatility' if available
        # For now, a general 'makeshift' factor
        return effectiveness_map['makeshift'], 'makeshift'

def _get_player_candidate_info(player_id, target_position, all_position_candidates):
    """
    Helper to find a player's pre-calculated candidate info for a specific position.
    'all_position_candidates' is the map like: {'GK': [cand1, cand2], 'CB': [...]}
    """
    if target_position not in all_position_candidates:
        return None
    for candidate in all_position_candidates[target_position]:
        if candidate['player']['id'] == player_id:
            return candidate
    return None

def select_starting_11(players, formation):
    """
    Select a starting 11 based on the given formation.
    Chooses the best players for each position based on current_ability,
    considering both primary and secondary positions.
    Includes a refinement step to check for beneficial 2-player swaps within the XI.
    """
    # Define formations with positions in traditional order
    positions_map = {
        # Traditional 4-3-3: GK, RB, CB, CB, LB, CDM, CM, CM, RW, ST, LW
        '4-3-3': ['GK', 'RB', 'CB', 'CB', 'LB', 'CDM', 'CM', 'CM', 'RW', 'ST', 'LW'],
        
        # 4-4-2: GK, RB, CB, CB, LB, RM, CM, CM, LM, ST, ST  
        '4-4-2': ['GK', 'RB', 'CB', 'CB', 'LB', 'RM', 'CM', 'CM', 'LM', 'ST', 'ST'],
        
        # 4-2-3-1: GK, RB, CB, CB, LB, CDM, CDM, CAM, RW, ST, LW
        '4-2-3-1': ['GK', 'RB', 'CB', 'CB', 'LB', 'CDM', 'CDM', 'CAM', 'RW', 'ST', 'LW'],
        
        # 3-5-2: GK, CB, CB, CB, RM, CDM, CM, CM, LM, ST, ST
        '3-5-2': ['GK', 'CB', 'CB', 'CB', 'RM', 'CDM', 'CM', 'CM', 'LM', 'ST', 'ST'],
        
        # 3-4-3: GK, CB, CB, CB, RM, CM, CM, LM, RW, ST, LW
        '3-4-3': ['GK', 'CB', 'CB', 'CB', 'RM', 'CM', 'CM', 'LM', 'RW', 'ST', 'LW'],
        
        # 4-1-4-1: GK, RB, CB, CB, LB, CDM, RM, CM, CM, LM, ST
        '4-1-4-1': ['GK', 'RB', 'CB', 'CB', 'LB', 'CDM', 'RM', 'CM', 'CM', 'LM', 'ST'],
        
        # 5-3-2: GK, RB, CB, CB, CB, LB, CM, CM, CM, ST, ST
        '5-3-2': ['GK', 'RB', 'CB', 'CB', 'CB', 'LB', 'CM', 'CM', 'CM', 'ST', 'ST'],
        
        # 4-3-2-1: GK, RB, CB, CB, LB, CDM, CM, CM, CAM, CAM, ST
        '4-3-2-1': ['GK', 'RB', 'CB', 'CB', 'LB', 'CDM', 'CM', 'CM', 'CAM', 'CAM', 'ST']
    }
    
    available_positions = positions_map.get(formation, positions_map['4-3-3'])
    
    position_candidates = {pos: [] for pos in set(available_positions)}
    
    for player in players:
        for pos_key in set(available_positions): # Use pos_key to avoid conflict with pos var later
            factor, pos_type = _calculate_position_effectiveness(player, pos_key)
            effective_ability = int(player['current_ability'] * factor)
            
            position_candidates[pos_key].append({
                'player': player, # This is a reference to the original player dict
                'effective_ability': effective_ability,
                'position_type': pos_type,
                'factor': factor
            })
    
    for pos_key in position_candidates:
        position_candidates[pos_key].sort(key=lambda x: x['effective_ability'], reverse=True)
    
    # Initial greedy selection
    # selected_11_intermediate will store dicts with more details for refinement
    selected_11_intermediate = []
    used_players_ids_intermediate = set()

    for pos in available_positions: # This is the positional slot in the formation
        candidates_for_slot = [
            c for c in position_candidates.get(pos, []) 
            if c['player']['id'] not in used_players_ids_intermediate
        ]
        
        current_player_selection_details = None
        if candidates_for_slot:
            selection = candidates_for_slot[0] # Best candidate for this slot
            
            current_player_selection_details = {
                'player_original_data': selection['player'], 
                'selected_position': pos,
                'effective_ability': selection['effective_ability'],
                'position_type': selection['position_type'],
                'effectiveness_factor': selection['factor']
            }
            used_players_ids_intermediate.add(selection['player']['id'])
        else:
            # Fallback: if no dedicated player, pick best remaining player overall for this slot
            remaining_players_for_fallback = [p for p in players if p['id'] not in used_players_ids_intermediate]
            if remaining_players_for_fallback:
                # Sort by base current_ability for fallback
                remaining_players_for_fallback.sort(key=lambda p: p['current_ability'], reverse=True)
                
                # Find the original player object from the input 'players' list
                # This is important because 'position_candidates' might have copies or modified versions.
                # However, 'selection['player']' in the above block IS the original player object.
                # For fallback, we need to ensure we get the original player object.
                original_fallback_player_data = next(p_orig for p_orig in players if p_orig['id'] == remaining_players_for_fallback[0]['id'])

                factor, pos_type = _calculate_position_effectiveness(original_fallback_player_data, pos)
                
                current_player_selection_details = {
                    'player_original_data': original_fallback_player_data,
                    'selected_position': pos,
                    'effective_ability': int(original_fallback_player_data['current_ability'] * factor),
                    'position_type': pos_type,
                    'effectiveness_factor': factor
                }
                used_players_ids_intermediate.add(original_fallback_player_data['id'])
        
        if current_player_selection_details:
            selected_11_intermediate.append(current_player_selection_details)

    # Refinement Phase: 2-Player Swaps within the current XI
    max_refinement_iterations = len(selected_11_intermediate) * (len(selected_11_intermediate) -1) // 2 + 1 # Max possible pairs + 1
    for iteration in range(max_refinement_iterations):
        made_swap_in_iteration = False
        if len(selected_11_intermediate) < 2:
            break

        for i in range(len(selected_11_intermediate)):
            p1_sel_details = selected_11_intermediate[i]
            p1_original_data = p1_sel_details['player_original_data']
            p1_id = p1_original_data['id']
            pos1 = p1_sel_details['selected_position']
            p1_ea_at_pos1 = p1_sel_details['effective_ability']

            for j in range(i + 1, len(selected_11_intermediate)):
                p2_sel_details = selected_11_intermediate[j]
                p2_original_data = p2_sel_details['player_original_data']
                p2_id = p2_original_data['id']
                pos2 = p2_sel_details['selected_position']
                p2_ea_at_pos2 = p2_sel_details['effective_ability']

                current_combined_ea = p1_ea_at_pos1 + p2_ea_at_pos2

                # Candidate info for P1 if they were to play Pos2
                p1_cand_at_pos2_info = _get_player_candidate_info(p1_id, pos2, position_candidates)
                # Candidate info for P2 if they were to play Pos1
                p2_cand_at_pos1_info = _get_player_candidate_info(p2_id, pos1, position_candidates)

                if p1_cand_at_pos2_info and p2_cand_at_pos1_info:
                    p1_ea_at_pos2 = p1_cand_at_pos2_info['effective_ability']
                    p2_ea_at_pos1 = p2_cand_at_pos1_info['effective_ability']
                    swapped_combined_ea = p1_ea_at_pos2 + p2_ea_at_pos1

                    if swapped_combined_ea > current_combined_ea:
                        # Perform the swap by creating new selection details dicts
                        
                        new_sel_for_i = {
                            'player_original_data': p2_original_data, # P2 is now at index i
                            'selected_position': pos1, # Playing P1's original position
                            'effective_ability': p2_ea_at_pos1,
                            'position_type': p2_cand_at_pos1_info['position_type'],
                            'effectiveness_factor': p2_cand_at_pos1_info['factor']
                        }
                        
                        new_sel_for_j = {
                            'player_original_data': p1_original_data, # P1 is now at index j
                            'selected_position': pos2, # Playing P2's original position
                            'effective_ability': p1_ea_at_pos2,
                            'position_type': p1_cand_at_pos2_info['position_type'],
                            'effectiveness_factor': p1_cand_at_pos2_info['factor']
                        }
                        
                        selected_11_intermediate[i] = new_sel_for_i
                        selected_11_intermediate[j] = new_sel_for_j
                        
                        made_swap_in_iteration = True
                        break 
            if made_swap_in_iteration:
                break 

        if not made_swap_in_iteration:
            break            
    # Final validation: ensure no player appears twice (fix for swap logic bug)
    final_selected_xi = []
    used_player_ids = set()
    
    for sel_details in selected_11_intermediate:
        player_id = sel_details['player_original_data']['id']
        
        # Skip if player already used (duplicate from swap logic)
        if player_id in used_player_ids:
            # Find a replacement player for this position
            position = sel_details['selected_position']
            replacement_candidates = [
                c for c in position_candidates.get(position, [])
                if c['player']['id'] not in used_player_ids
            ]
            
            if replacement_candidates:
                # Use the best available replacement
                replacement = replacement_candidates[0]
                sel_details = {
                    'player_original_data': replacement['player'],
                    'selected_position': position,
                    'effective_ability': replacement['effective_ability'],
                    'position_type': replacement['position_type'],
                    'effectiveness_factor': replacement['factor']
                }
                player_id = replacement['player']['id']
            else:
                continue  # Skip this position if no replacement available
        
        # Create a copy of the original player data to add selection-specific attributes
        player_for_output = sel_details['player_original_data'].copy()
        player_for_output['selected_position'] = sel_details['selected_position']
        player_for_output['position_type'] = sel_details['position_type']
        player_for_output['effective_ability'] = sel_details['effective_ability']
        player_for_output['effectiveness_factor'] = sel_details['effectiveness_factor']
        
        final_selected_xi.append(player_for_output)
        used_player_ids.add(player_id)
        
    return final_selected_xi

def calculate_ratings(players):
    """Calculate ratings for attack, midfield, defense, and overall squad."""
    attack, midfield, defense, gk = 0, 0, 0, 0
    num_attackers, num_midfielders, num_defenders = 0, 0, 0

    for player in players:
        # Use the player's selected_position in the current lineup for rating calculation
        selected_pos = player.get('selected_position') 
        current_ability = player['current_ability']

        if selected_pos == 'GK':
            gk += current_ability
        elif selected_pos in ['ST', 'LW', 'RW']:
            attack += current_ability
            num_attackers += 1
        elif selected_pos in ['CM', 'CDM', 'CAM', 'RM', 'LM']:
            midfield += current_ability
            num_midfielders += 1
        elif selected_pos in ['CB', 'LB', 'RB']:
            defense += current_ability
            num_defenders += 1

    total_rating = attack + midfield + defense + gk
    return {
        'attack': attack // num_attackers if num_attackers > 0 else 0,
        'midfield': midfield // num_midfielders if num_midfielders > 0 else 0,
        'defense': defense // num_defenders if num_defenders > 0 else 0,
        'goalkeeper': gk,
        'total': total_rating // 11 if len(players) == 11 else (total_rating // len(players) if len(players) > 0 else 0)    }

if __name__ == "__main__":
    # Example usage - only runs when script is executed directly
    barcelona_players = load_players('data/00_2_clubs_players/club_barcelona_players.json')
    manager = load_manager('data/managers/2.json', 'club_barcelona')

    formation = manager.get('preferred_formation', '4-3-3')
    starting_11 = select_starting_11(barcelona_players, formation)
    ratings = calculate_ratings(starting_11)

    # Define a canonical sort order for football positions
    position_display_order = {
        'GK': 0,
        'RB': 1,
        'CB': 2,
        'LB': 3,
        'CDM': 4,
        'RM': 5,
        'CM': 6,
        'LM': 7,
        'CAM': 8,
        'RW': 9,
        'ST': 10,
        'LW': 11
    }

    # Sort the starting_11 for display purposes
    # Use player['selected_position'] which indicates the position they were chosen for in this XI
    # Provide a high default value for any unexpected positions to sort them last
    starting_11_display = sorted(
        starting_11,
        key=lambda p: position_display_order.get(p['selected_position'], 99)
    )

    print("Starting XI:")
    for player in starting_11_display: # Iterate over the sorted list
        # Display the player's name, their selected position in this XI, and their current ability
        print(f"{player['known_as']} ({player['selected_position']}) - Ability: {player['current_ability']}")

    print("\nRatings:")
    print(f"Attack: {ratings['attack']}")
    print(f"Midfield: {ratings['midfield']}")
    print(f"Defense: {ratings['defense']}")
    print(f"Goalkeeper: {ratings['goalkeeper']}")
    print(f"Total Squad Rating: {ratings['total']}")
