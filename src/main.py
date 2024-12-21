from flask import Flask, request, jsonify
import openai
from api import get_steam_games, get_game_details
from emotion_analysis import analyze_emotion_with_gpt  # 감정 분석 함수
from pymongo import MongoClient
from flask_cors import CORS
import random  # 랜덤 게임 선택을 위해 추가

app = Flask(__name__)
CORS(app)

# OpenAI API 키 설정
openai.api_key = 'api_key'

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017/')
db = client['game_recommendations']  # DB 이름
recommendations_collection = db['recommendations']  # 컬렉션 이름

# 감정-장르 매핑
genre_emotion_mapping = {
    '기쁨': ['Casual', 'Massively Multiplayer', 'Racing'],
    '슬픔': ['Indie', 'Adventure', 'RPG'],
    '놀람': ['Adventure'],
    '분노': ['Racing', 'Action', 'RPG'],
    '공포': ['Indie'],
}

def extract_emotion(emotion_text):
    """ 감정 분석 결과에서 핵심 감정 단어만 추출 """
    for emotion in genre_emotion_mapping.keys():
        if emotion in emotion_text:
            return emotion
    return None

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('input')

    # 감정 분석
    emotion_text = analyze_emotion_with_gpt(user_input, openai.api_key)
    emotion = extract_emotion(emotion_text)  # 감정 텍스트에서 핵심 단어 추출

    print(f"Detected emotion: {emotion}")

    if emotion and emotion in genre_emotion_mapping:
        genre_list = genre_emotion_mapping[emotion]  # 감정에 매핑된 장르 리스트
        
        # Steam API에서 게임 목록 가져오기
        games = get_steam_games()

        # 추천할 게임 필터링 (장르에 따라)
        recommended_games = [
            game for game in games 
            if any(genre.lower() in game['name'].lower() for genre in genre_list)
        ]

        # 기존에 추천된 게임 목록 가져오기
        existing_games = list(recommendations_collection.find({}, {'_id': 0, 'game.name': 1}))
        existing_game_names = [game['game']['name'] for game in existing_games]

        # 기존에 추천된 게임은 제외하고 새로운 게임만 선택
        new_games = [game for game in recommended_games if game['name'] not in existing_game_names]

        if new_games:
            # 랜덤으로 하나의 새로운 게임을 선택
            selected_game = random.choice(new_games)
        elif recommended_games:  # 새로운 게임이 없으면 기존 게임에서도 랜덤으로 선택
            selected_game = random.choice(recommended_games)
        else:
            return jsonify({
                "response": "죄송합니다, 해당 감정에 맞는 추천 게임을 찾을 수 없습니다."
            })

        # MongoDB에 이미 존재하는지 확인 후 없으면 추가
        if not recommendations_collection.find_one({"game.name": selected_game['name']}):
            recommendations_collection.insert_one({"game": selected_game, "emotion": emotion})
            print(f"Stored game in DB: {selected_game['name']}")

        # 추천할 게임을 하나만 반환하도록 수정
        stored_game = recommendations_collection.find_one({"game.name": selected_game['name']}, {'_id': 0, 'game': 1})

        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 사용자에게 친근하고 자연스럽게 대화하는 챗봇입니다."},
                {"role": "user", "content": f"사용자가 '{user_input}'라고 했을 때의 감정은 {emotion}입니다. 이 감정에 맞는 게임을 추천해 주세요."}
            ],
            temperature=0.8,
            max_tokens=500,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )

        ai_message = openai_response.choices[0].message.content

        return jsonify({
            "response": ai_message,
            "game": stored_game['game']  # 추천한 하나의 게임만 반환
        })
    else:
        return jsonify({
            "response": "죄송합니다 감정을 읽지 못했어요. 저에게 감정을 다시한번 표현해주시겠어요?"
        })

@app.route('/api/game/<int:app_id>', methods=['GET'])
def get_game_details(app_id):  
    try:
        game_details = get_game_details(app_id)
        if game_details[str(app_id)]['success']:
            return jsonify(game_details[str(app_id)]['data'])
        else:
            return jsonify({"message": "게임 정보를 찾을 수 없습니다."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    recommendations = list(recommendations_collection.find({}, {'_id': 0, 'game': 1}))
    return jsonify(recommendations)

@app.route('/api/recommendations/<string:game>', methods=['DELETE'])
def delete_recommendation(game):
    result = recommendations_collection.delete_one({"game.name": game})
    if result.deleted_count > 0:
        return jsonify({"message": "추천 게임이 삭제되었습니다."}), 200
    else:
        return jsonify({"message": "게임을 찾을 수 없습니다."}), 404

if __name__ == "__main__":
    app.run(port=5000)
