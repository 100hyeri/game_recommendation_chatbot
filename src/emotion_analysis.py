import openai

def analyze_emotion_with_gpt(user_input, api_key):
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "다음 문장에서 사용자의 감정을 자연스럽게 해석하고, 그 감정을 기쁨, 슬픔, 분노, 놀람, 공포 중 하나로 판단해 주세요."},
                {"role": "user", "content": f"문장: '{user_input}'"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error analyzing emotion: {e}")
        return None