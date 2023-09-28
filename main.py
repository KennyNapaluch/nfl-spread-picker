import requests

# Define the base ESPN API endpoint for NFL scores and matchups
base_api_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{}/schedule'

# Define the odds API endpoint template
odds_api_url_template = 'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{}/competitions/{}/odds?lang=en&region=us'

# Define initial Elo ratings for each team
nfl_teams = {
    "ARI": 1500, "ATL": 1500, "BAL": 1500, "BUF": 1500, "CAR": 1500, "CHI": 1500, "CIN": 1500, "CLE": 1500, "DAL": 1500,
    "DEN": 1500, "DET": 1500, "GB": 1500, "HOU": 1500, "IND": 1500, "JAX": 1500, "KC": 1500, "LV": 1500, "LAC": 1500,
    "LAR": 1500, "MIA": 1500, "MIN": 1500, "NE": 1500, "NO": 1500, "NYG": 1500, "NYJ": 1500, "PHI": 1500, "PIT": 1500,
    "SF": 1500, "SEA": 1500, "TB": 1500, "TEN": 1500, "WSH": 1500
}

K = 32


# Function to get odds data for an event
def get_odds_data(event_id, competition_id):
    odds_api_url = odds_api_url_template.format(event_id, competition_id)
    response = requests.get(odds_api_url)

    if response.status_code == 200:
        odds_data = response.json()
        return odds_data
    else:
        return None


# Function to parse the point spread from odds data
def parse_point_spread(odds_data):
    try:
        return float(odds_data['items'][0]['spread'])
    except (KeyError, ValueError) as e:
        print(e)
    return 0.0  # Default to 0 if point spread cannot be parsed


# Create a set to store seen event_ids
seen_event_ids = set()
week = 5
print(f'Week: {week}')

# Loop through team IDs
for team_id in range(1, 35):
    if team_id != 31 and team_id != 32:

        # Create the API URL for the current team to get past game results
        api_url = base_api_url.format(team_id)

        # Send a GET request to the API to get past game results
        response = requests.get(api_url)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            for i in range(week):
                event_id = data['events'][i]['id']
    
                # Check if the event_id has already been processed
                if event_id in seen_event_ids:
                    continue  # Skip this event
                seen_event_ids.add(event_id)
    
                game_status = data['events'][i]['competitions'][0]['status']['type']['state']
    
                if game_status == 'post':
                    home_team = data['events'][i]['competitions'][0]['competitors'][0]['team']['abbreviation']
                    away_team = data['events'][i]['competitions'][0]['competitors'][1]['team']['abbreviation']
                    home_score = data['events'][i]['competitions'][0]['competitors'][0]['score']
                    away_score = data['events'][i]['competitions'][0]['competitors'][1]['score']
    
                    # Get odds data for the current event
                    event_id = data['events'][i]['id']
                    competition_id = data['events'][i]['competitions'][0]['id']
                    odds_data = get_odds_data(event_id, competition_id)
    
                    # Calculate the point spread
                    point_spread = parse_point_spread(odds_data)
    
                    # Calculate expected win probabilities for each team with point spread
                    expected_home_win = 1 / (1 + 10 ** ((nfl_teams[away_team] - nfl_teams[home_team] + point_spread) / 400))
                    expected_away_win = 1 / (1 + 10 ** ((nfl_teams[home_team] - nfl_teams[away_team] - point_spread) / 400))
    
                    # Update Elo ratings based on the game result
                    if home_score['value'] > away_score['value']:
                        nfl_teams[home_team] += K * (1 - expected_home_win)
                        nfl_teams[away_team] += K * (0 - expected_away_win)
                    elif home_score['value'] < away_score['value']:
                        nfl_teams[home_team] += K * (0 - expected_home_win)
                        nfl_teams[away_team] += K * (1 - expected_away_win)
                game_status = data['events'][i]['competitions'][0]['status']['type']['state']
                if game_status == 'pre':
                    home_team = data['events'][i]['competitions'][0]['competitors'][0]['team']['abbreviation']
                    away_team = data['events'][i]['competitions'][0]['competitors'][1]['team']['abbreviation']
    
                    # Calculate the point spread
                    event_id = data['events'][i]['id']
                    competition_id = data['events'][i]['competitions'][0]['id']
                    odds_data = get_odds_data(event_id, competition_id)
                    point_spread = parse_point_spread(odds_data)
    
                    modified_point_spread = point_spread
    
                    # Adjust the impact of point_spread
                    impact_factor = 1 + 0.01 * modified_point_spread
    
                    # Calculate expected win probabilities for each team with the modified point spread
                    expected_home_win = 1 / (
                                1 + 10 ** ((nfl_teams[away_team] - nfl_teams[home_team]) / 400) * impact_factor)
                    expected_away_win = 1 / (
                                1 + 10 ** ((nfl_teams[home_team] - nfl_teams[away_team]) / 400) / impact_factor)
    
                    if expected_home_win > expected_away_win:
                        print(f"Predicted winner: {home_team} ({expected_home_win * 100:.2f}) over {away_team} ({expected_away_win * 100:.2f}). Spread: {point_spread}")
                    elif expected_home_win < expected_away_win:
                        print(f"Predicted winner: {away_team} ({expected_away_win * 100:.2f}) over {home_team} ({expected_home_win * 100:.2f}). Spread: {point_spread}")
                    else:
                        print(f"Predicted match-up: {home_team} and {away_team} are evenly matched. Spread: {point_spread}")
                else:
                    print(f'Is it week {week}?')