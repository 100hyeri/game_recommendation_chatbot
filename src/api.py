import requests

def get_steam_games():
    STEAM_API_URL = 'https://api.steampowered.com/ISteamApps/GetAppList/v2'
    response = requests.get(STEAM_API_URL)

    if response.status_code == 200:
        return response.json()['applist']['apps']
    return []

def get_game_details(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch game details from Steam API")
