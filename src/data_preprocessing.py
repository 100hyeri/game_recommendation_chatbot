import json

def pre_training_data(games, genre_emotion_mapping):
    training_data = []
    for game in games:
        for genre in genre_emotion_mapping.keys():
            if genre in game['name'].lower():
                training_data.append({
                    'game_name': game['name'],
                    'genre': genre,
                    'emotion': genre_emotion_mapping[genre]
                })
    return training_data

def save_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)
