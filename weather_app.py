import streamlit as st
import os
import requests
from streamlit_js_eval import streamlit_js_eval
from streamlit import components
API_KEY = st.secrets["API_KEY"]
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"



# 날씨 설명에 따른 배경 이미지 경로 매핑
weather_bg_map = {
    "비": "비/rain-6243559_1280.jpg",
    "먹구름": "먹구름/sea-9714469.jpg",
    "눈": "눈/snow.jpg", # 눈 폴더에 snow.jpg 없으면 맑음 이미지 사용
    "맑음": "맑은날/clouds-7060045_1280.jpg",
    "비온뒤갬": "비온뒤갬/rainbow-4047523_1280.jpg"
}

def get_bg_image(desc):
    if "비" in desc and "후" in desc:
        img = weather_bg_map["비온뒤갬"]
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), img))
        return abs_path
    if "비" in desc:
        img = weather_bg_map["비"]
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), img))
        return abs_path
    if "구름" in desc or "흐림" in desc:
        img = weather_bg_map["먹구름"]
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), img))
        return abs_path
    if "눈" in desc:
        img = weather_bg_map["눈"]
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), img))
        if not os.path.exists(abs_path):
            img = weather_bg_map["맑음"]
            abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), img))
        return abs_path
    if "맑음" in desc or "맑은" in desc or "clear" in desc:
        img = weather_bg_map["맑음"]
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), img))
        return abs_path
    # default
    img = weather_bg_map["맑음"]
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), img))
    return abs_path

def show_weather_image(img_path):
    st.image(img_path, use_container_width=True)

st.markdown("<h1 style='text-align:center; color:#0077b6; font-weight:700;'>🌤️ 날씨 웹앱</h1>", unsafe_allow_html=True)
st.write("<div style='text-align:center;'>현재 위치 기준 날씨를 확인하려면 아래 버튼을 누르세요.</div>", unsafe_allow_html=True)

# 위치 기반 날씨 정보
loc_button = st.button("내 위치 날씨 보기", use_container_width=True)
if loc_button:
    loc = None
    try:
        loc = streamlit_js_eval(js_expressions="geo", key="get_location")
    except Exception:
        loc = None
    lat, lon = None, None
    if loc and "coords" in loc:
        lat = loc["coords"]["latitude"]
        lon = loc["coords"]["longitude"]
    else:
        st.warning("자동 위치 감지에 실패했습니다. 직접 입력해 주세요.")
        lat = st.number_input("위도(latitude)", format="%f")
        lon = st.number_input("경도(longitude)", format="%f")
    if lat and lon:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",
            "lang": "kr"
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            icon_url = f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
            st.markdown("""
                <div class='weather-card'>
                    <img src='{}' class='weather-icon'>
                    <div class='main-temp'>{}°C</div>
                    <div class='desc'>{}</div>
                    <div class='sub-info'>습도: {}% | 풍속: {} m/s</div>
                </div>
            """.format(icon_url, data['main']['temp'], data['weather'][0]['description'], data['main']['humidity'], data['wind']['speed']), unsafe_allow_html=True)
        else:
            pass  # 위치 감지 실패시 경고 후 직접 입력

# 한글 도시명과 영문 도시명 매핑
gyeonggi_cities = {
    "수원시": "Suwon",
    "성남시": "Seongnam",
    "고양시": "Goyang",
    "용인시": "Yongin",
    "부천시": "Bucheon",
    "안산시": "Ansan",
    "안양시": "Anyang",
    "평택시": "Pyeongtaek",
    "의정부시": "Uijeongbu",
    "시흥시": "Siheung",
    "파주시": "Paju",
    "김포시": "Gimpo",
    "광명시": "Gwangmyeong",
    "군포시": "Gunpo",
    "이천시": "Icheon",
    "오산시": "Osan",
    "하남시": "Hanam",
    "여주시": "Yeoju",
    "동두천시": "Dongducheon",
    "과천시": "Gwacheon",
    "구리시": "Guri",
    "남양주시": "Namyangju",
    "양주시": "Yangju",
    "포천시": "Pocheon",
    "의왕시": "Uiwang",
    "가평군": "Gapyeong",
    "양평군": "Yangpyeong"
}

korean_city_map = {
    "서울": "Seoul",
    "부산": "Busan",
    "대구": "Daegu",
    "인천": "Incheon",
    "광주": "Gwangju",
    "대전": "Daejeon",
    "울산": "Ulsan",
    "세종": "Sejong",
    "강원도": "Chuncheon",
    "충청북도": "Cheongju",
    "충청남도": "Hongseong",
    "경상북도": "Andong",
    "경상남도": "Changwon",
    "전라북도": "Jeonju",
    "전라남도": "Muan",
    "제주도": "Jeju"
}
# 경기도 도시 추가

# 도/광역시별 시/군/구 카테고리 구조
region_city_map = {
    "서울": {
        "강남구": "Gangnam-gu,Seoul",
        "종로구": "Jongno-gu,Seoul",
        "송파구": "Songpa-gu,Seoul",
        "서초구": "Seocho-gu,Seoul",
        "마포구": "Mapo-gu,Seoul",
        "영등포구": "Yeongdeungpo-gu,Seoul"
    },
    "인천": {
        "남동구": "Namdong-gu,Incheon",
        "연수구": "Yeonsu-gu,Incheon",
        "부평구": "Bupyeong-gu,Incheon",
        "서구": "Seo-gu,Incheon"
    },
    "부산": {
        "해운대구": {"name": "Haeundae-gu,Busan", "lat": 35.1631, "lon": 129.1635},
        "수영구": {"name": "Suyeong-gu,Busan", "lat": 35.1458, "lon": 129.1134},
        "동래구": {"name": "Dongnae-gu,Busan", "lat": 35.2052, "lon": 129.0836},
        "부산진구": {"name": "Busanjin-gu,Busan", "lat": 35.1625, "lon": 129.0530}
    },
    "대전": {
        "서구": "Seo-gu,Daejeon",
        "유성구": "Yuseong-gu,Daejeon",
        "동구": "Dong-gu,Daejeon"
    },
    "대구": {
        "수성구": {"name": "Suseong-gu,Daegu", "lat": 35.8574, "lon": 128.6306},
        "달서구": {"name": "Dalseo-gu,Daegu", "lat": 35.8222, "lon": 128.5326},
        "중구": {"name": "Jung-gu,Daegu", "lat": 35.8700, "lon": 128.6064}
    },
    "광주": {
        "동구": {"name": "Dong-gu,Gwangju", "lat": 35.1461, "lon": 126.9237},
        "서구": {"name": "Seo-gu,Gwangju", "lat": 35.1547, "lon": 126.8836},
        "남구": {"name": "Nam-gu,Gwangju", "lat": 35.1338, "lon": 126.9021},
        "북구": {"name": "Buk-gu,Gwangju", "lat": 35.1741, "lon": 126.9111},
        "광산구": {"name": "Gwangsan-gu,Gwangju", "lat": 35.1397, "lon": 126.7930}
    },
    "울산": {
        "중구": {"name": "Jung-gu,Ulsan", "lat": 35.5663, "lon": 129.3386},
        "남구": {"name": "Nam-gu,Ulsan", "lat": 35.5436, "lon": 129.3302},
        "동구": {"name": "Dong-gu,Ulsan", "lat": 35.5043, "lon": 129.4207},
        "북구": {"name": "Buk-gu,Ulsan", "lat": 35.5820, "lon": 129.3607},
        "울주군": {"name": "Ulju-gun,Ulsan", "lat": 35.5600, "lon": 129.1275}
    },
    "세종": {"세종": "Sejong"},
    "경기도": gyeonggi_cities,
    "강원도": {"춘천시": "Chuncheon"},
    "충청북도": {"청주시": "Cheongju"},
    "충청남도": {"홍성군": "Hongseong"},
    "경상북도": {"안동시": "Andong"},
    "경상남도": {"창원시": "Changwon"},
    "전라북도": {"전주시": "Jeonju"},
    "전라남도": {"무안군": "Muan"},
    "제주도": {"제주시": "Jeju"}
}

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#0077b6;'>도/광역시별 날씨 정보</h3>", unsafe_allow_html=True)
region = st.selectbox("도/광역시를 선택하세요:", list(region_city_map.keys()))

city_list = list(region_city_map[region].keys())
city_kor = st.selectbox("시/군/구를 선택하세요:", city_list)

# 부산 구별은 lat/lon 사용, 그 외는 기존 방식
if region in ["부산", "대구", "광주", "울산"]:
    city_info = region_city_map[region][city_kor]
    city_eng = city_info["name"]
    city_lat = city_info["lat"]
    city_lon = city_info["lon"]
else:
    city_eng = region_city_map[region][city_kor]
    city_lat = None
    city_lon = None

def get_weather(city_name, lat=None, lon=None):
    if lat is not None and lon is not None:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",
            "lang": "kr"
        }
    else:
        params = {
            "q": city_name,
            "appid": API_KEY,
            "units": "metric",
            "lang": "kr"
        }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json(), None
    else:
        try:
            error_msg = response.json().get("message", "알 수 없는 오류")
        except Exception:
            error_msg = "API 응답 오류"
        return None, error_msg

def get_forecast(city_name, lat=None, lon=None):
    if lat is not None and lon is not None:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",
            "lang": "kr"
        }
    else:
        params = {
            "q": city_name,
            "appid": API_KEY,
            "units": "metric",
            "lang": "kr"
        }
    response = requests.get(FORECAST_URL, params=params)
    if response.status_code == 200:
        return response.json(), None
    else:
        try:
            error_msg = response.json().get("message", "알 수 없는 오류")
        except Exception:
            error_msg = "API 응답 오류"
        return None, error_msg





# 오늘 날씨
data, error = get_weather(city_eng, city_lat, city_lon)
if data:
    desc = data['weather'][0]['description']
    img_path = get_bg_image(desc)
    st.markdown("<div class='weather-card'>", unsafe_allow_html=True)
    show_weather_image(img_path)
    icon_url = f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
    st.markdown(f"<img src='{icon_url}' class='weather-icon'>", unsafe_allow_html=True)
    st.markdown(f"<div class='main-temp'>{data['main']['temp']}°C</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='desc'>{desc}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-info'>습도: {data['main']['humidity']}% | 풍속: {data['wind']['speed']} m/s</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
elif error:
    st.error(f"날씨 정보를 가져올 수 없습니다: {error}")




# 5일간 예보 (시간대별 온도)
st.markdown("<h4 style='color:#0077b6;'>5일간 시간대별 날씨 예보</h4>", unsafe_allow_html=True)
forecast, error_f = get_forecast(city_eng, city_lat, city_lon)
if forecast:
    from collections import defaultdict
    import datetime
    week_names = ["월", "화", "수", "목", "금", "토", "일"]
    daily_times = defaultdict(list)
    for item in forecast["list"]:
        dt_txt = item["dt_txt"]
        date, time = dt_txt.split(" ")
        daily_times[date].append(item)

    weather_color_map = {
        "비": "#4a90e2",
        "먹구름": "#7b8fa1",
        "눈": "#b3e0ff",
        "맑음": "#ffe066",
        "비온뒤갬": "#a3d977"
    }
    def get_row_color(desc):
        if "비" in desc and "후" in desc:
            return weather_color_map["비온뒤갬"]
        elif "비" in desc:
            return weather_color_map["비"]
        elif "구름" in desc or "흐림" in desc:
            return weather_color_map["먹구름"]
        elif "눈" in desc:
            return weather_color_map["눈"]
        elif "맑음" in desc or "맑은" in desc or "clear" in desc:
            return weather_color_map["맑음"]
        else:
            return "#f0f0f0"

    for date, items in daily_times.items():
        y, m, d = map(int, date.split("-"))
        weekday = week_names[datetime.date(y, m, d).weekday()]
        # 대표 날씨(첫 시간대)로 이미지 선택
        main_desc = items[0]["weather"][0]["description"]
        img_path = get_bg_image(main_desc)
        st.markdown(f"""
        <div style="margin-bottom:8px;">
            <div style="background-image:url('file://{img_path}');background-size:cover;background-position:center center;border-radius:12px;padding:16px 0;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.18);">
                <span style="font-size:1.3em;color:#fff;text-shadow:0 2px 8px #000;font-weight:700;">{date} ({weekday}요일)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        table_html = [
            f"<div style=\"overflow-x:auto;background-image:url('file://{img_path}');background-size:cover;background-repeat:no-repeat;background-position:center center;padding:32px;\">",
            "<table style='width:100%;border-collapse:collapse;color:#fff;text-shadow:0 1px 4px #000;font-weight:600;border:2px solid #fff;border-radius:18px;box-shadow:0 4px 24px rgba(0,0,0,0.25);background:transparent !important;padding:24px;'>",
            "<thead><tr>",
            "<th style='border-bottom:2px solid #fff;padding:8px 0;'>시간</th>",
            "<th style='border-bottom:2px solid #fff;padding:8px 0;'>온도(°C)</th>",
            "<th style='border-bottom:2px solid #fff;padding:8px 0;'>날씨</th>",
            "<th style='border-bottom:2px solid #fff;padding:8px 0;'>습도(%)</th>",
            "<th style='border-bottom:2px solid #fff;padding:8px 0;'>풍속(m/s)</th>",
            "</tr></thead><tbody>"
        ]
        for item in items:
            time = item["dt_txt"].split(" ")[1][:5]
            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"]
            humidity = item["main"]["humidity"]
            wind = item["wind"]["speed"]
            table_html.append(
                f"<tr>"
                f"<td style='border-bottom:1px solid #fff;padding:8px 0;'>{time}</td>"
                f"<td style='border-bottom:1px solid #fff;padding:8px 0;'>{temp}</td>"
                f"<td style='border-bottom:1px solid #fff;padding:8px 0;'>{desc}</td>"
                f"<td style='border-bottom:1px solid #fff;padding:8px 0;'>{humidity}</td>"
                f"<td style='border-bottom:1px solid #fff;padding:8px 0;'>{wind}</td>"
                "</tr>"
            )
        table_html.append("</tbody></table></div>")
        st.markdown("\n".join(table_html), unsafe_allow_html=True)
elif error_f:
    st.error(f"5일 예보 정보를 가져올 수 없습니다: {error_f}")
