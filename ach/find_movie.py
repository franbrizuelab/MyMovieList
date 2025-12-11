import requests
import json

# --- 設定區 ---
# 這是你剛才提供的 API Key
API_KEY = '5ca996952123cb47fb3751f95b9d5a97'

# 我們要搜尋的關鍵字
SEARCH_QUERY = 'Star Wars'

# 圖片的基礎網址 (w500 代表寬度 500px，也可以改成 original 取得原圖)
BASE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

def test_search():
    print(f"正在搜尋: {SEARCH_QUERY} ...\n")

    # 1. 設定 API 請求網址與參數
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        'api_key': API_KEY,
        'query': SEARCH_QUERY,
        'language': 'en-US'  
    }

    try:
        # 2. 發送請求
        response = requests.get(url, params=params)
        
        # 檢查連線狀態 (200 代表成功)
        if response.status_code == 200:
            data = response.json()
            
            # 3. 檢查是否有搜尋結果
            if data['results']:
                # 取得第一筆結果 (通常是最符合的)
                first_match = data['results'][0]
                
                print(f"--- 找到電影 ---")
                print(f"電影名稱: {first_match.get('title')}")
                print(f"原始名稱: {first_match.get('original_title')}")
                print(f"上映日期: {first_match.get('release_date')}")
                
                # 4. 組合圖片網址
                poster_path = first_match.get('poster_path')
                if poster_path:
                    full_image_url = f"{BASE_IMAGE_URL}{poster_path}"
                    print(f"\n✅ 成功取得封面連結: {full_image_url}")
                    print(f"你可以點擊上面的連結在瀏覽器中查看圖片。")
                else:
                    print("⚠️ 這部電影雖然找到了，但是 TMDB 資料庫裡沒有封面圖片。")
                
                # (選用) 印出完整資料結構讓你參考，方便你以後想抓別的欄位
                # print("\n--- 完整資料 (Debug用) ---")
                # print(json.dumps(first_match, indent=4, ensure_ascii=False))
                
            else:
                print("找不到任何符合的電影。")
        else:
            print(f"API 请求失敗，狀態碼: {response.status_code}")
            print(f"錯誤訊息: {response.text}")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    test_search()