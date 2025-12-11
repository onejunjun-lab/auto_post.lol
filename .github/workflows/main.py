import os
import requests
import tweepy
from datetime import datetime
import google.generativeai as genai

# === APIキー（GitHub Secretsから取得）===
GEMINI_API_KEY = os.getenv('AIzaSyDcTzliAbBT022tZQFQilJ7rHH8UPEwKzU')
X_CONSUMER_KEY = os.getenv('KqqGOWPH7C2NZNbBueh9RnXBf')
X_CONSUMER_SECRET = os.getenv('xnX1XzfsKAqhO6atccRV1vpTTj06fnX9e7Ll1NDoJgonZQQmLB')
X_ACCESS_TOKEN = os.getenv('1141352675037995008-hvIpt75VXyC8uhkRDu0sSERnakSNhF')
X_ACCESS_TOKEN_SECRET = os.getenv('vCe001mD6EHGrzwjbxAl1h9AWQmLhOjAm7EvNn84jd9c8')

# Gemini設定
genai.configure(api_key=GEMINI_API_KEY)
text_model = genai.GenerativeModel('gemini-1.5-flash')
image_model = genai.GenerativeModel('gemini-1.5-flash')  # 画像も同じモデルでOK

# 1. 今日のLoLトレンドをGeminiに聞く
def get_lol_trends():
    response = text_model.generate_content(
        "2025年12月現在のLeague of Legendsで今一番熱いトレンドを3つ以内で日本語で教えて。"
        "パッチ、スキン、メタ、esports、ミーム、なんでもOK！"
    )
    return response.text.strip()

# 2. DEEPLOL風の投稿文を作る
def generate_post_text(trends):
    prompt = f"""
    以下のトレンドをDEEPLOL風に超可愛くユーモアたっぷりで140文字以内で投稿文にしてください：
    {trends}
    語尾は「だお」「なんだお」「だぞ」「にゃ」など可愛く！絵文字もたくさん！
    """
    response = text_model.generate_content(prompt)
    return response.text.strip()

# 3. 画像を生成（Geminiは直接画像を返す！）
def generate_image(text):
    response = image_model.generate_content([
        f"League of Legendsの可愛いアニメ風イラストを作成して：{text}、トレンド感満載、キラキラ、チャンピオン中心、Twitter映え"
    ])
    response.resolve()  # 画像生成完了まで待つ
    return response.parts[0].inline_data.data  # バイナリ画像データ

# 4. Xに投稿
def post_to_x(text, image_bytes):
    img_path = "/tmp/lol_image.png"
    with open(img_path, "wb") as f:
        f.write(image_bytes)

    auth = tweepy.OAuth1UserHandler(
        X_CONSUMER_KEY, X_CONSUMER_SECRET,
        X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)
    api.update_with_media(img_path, status=text)

# 5. 今日もう投稿したかチェック（重複防止）
def already_posted_today():
    flag = "/tmp/last_post_date.txt"
    if os.path.exists(flag):
        with open(flag, "r") as f:
            last = f.read().strip()
            if last == datetime.now().strftime("%Y-%m-%d"):
                return True
    return False

def mark_posted_today():
    with open("/tmp/last_post_date.txt", "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d"))

# === メイン ===
def main():
    if already_posted_today():
        print("今日はもう投稿済み！スキップします～")
        return

    print("LoLトレンド取得中...")
    trends = get_lol_trends()
    print("投稿文生成中...")
    post_text = generate_post_text(trends)
    full_text = f"{post_text}\n#LoL #LeagueOfLegends #LoLトレンド"

    print("画像生成中...")
    image_bytes = generate_image(post_text)

    print("Xに投稿中...")
    post_to_x(full_text, image_bytes)
    mark_posted_today()
    print("投稿完了だお！")

if __name__ == "__main__":
    main()
