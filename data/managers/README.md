# Manager Data Structure

## Overview
The manager data has been restructured from a single large `managers.json` file into league-specific files for better organization and performance.

## New Structure
```
data/
├── managers/
│   ├── league_epl_managers.json
│   ├── league_laliga_managers.json
│   ├── league_league_ger_bundeslig_managers.json
│   ├── league_league_ita_seriea_managers.json
│   ├── league_league_fra_ligue1_managers.json
│   ├── league_league_championship_managers.json
│   └── ... (other league manager files)
└── leagues_clubs/
    ├── epl_clubs.json (updated with new manager_id references)
    ├── laliga_clubs.json (updated with new manager_id references)
    └── ... (other club files)
```

## Key Changes

### 1. League-Specific Manager Files
- Each league now has its own manager file
- Format: `league_[league_name]_managers.json`
- Contains only managers for clubs in that specific league

### 2. Flexible Manager IDs
- Old format: `manager_[league]_club_[club_name]_[hash]`
- New format: `mgr_[lastname]_[firstname]`
- Examples:
  - `mgr_guardiola_pep` (Pep Guardiola)
  - `mgr_conte_antonio` (Antonio Conte)
  - `mgr_slot_arne` (Arne Slot)

### 3. Realistic Star Manager Trait Distribution
- **5-star managers**: Elite managers (Guardiola, Ancelotti, Conte, Slot, etc.) - 1.3%
- **4-star managers**: Top tier managers - 6.3%
- **3-star managers**: Good managers - 24.2%
- **2-star managers**: Average managers - 46.8%
- **1-star managers**: Below average managers - 21.3%

### 4. Updated Club References
- All club files updated to reference new flexible manager IDs
- Manager contracts can now be more easily transferred between clubs
- No more club-specific manager ID constraints

## Elite Managers (5-star)
Based on 2024/2025 real-world rankings:
- Pep Guardiola (Manchester City)
- Antonio Conte (Napoli)
- Arne Slot (Liverpool)
- Xabi Alonso (Bayer Leverkusen)
- Simone Inzaghi (Inter Milan)

## Files Processed
- **Total managers**: 380
- **Total leagues**: 21
- **Club files updated**: 83 clubs across 5 major leagues (EPL, La Liga, Bundesliga, Serie A, Ligue 1)

## Benefits
1. **Performance**: Smaller files load faster
2. **Organization**: Easier to find and manage league-specific managers
3. **Flexibility**: Manager IDs no longer tied to specific clubs
4. **Realism**: Star ratings reflect real-world manager quality
5. **Scalability**: Easy to add new leagues and managers

## Backup
- Original `managers.json` backed up to `_backups/managers_original.json`
- Full restructuring summary available in `manager_restructuring_summary.txt`
