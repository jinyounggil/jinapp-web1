
# ----- tab1~tab4 UI 함수 직접 정의 -----
import random
import pandas as pd
import matplotlib.pyplot as plt

def get_color(n):
  # 실로또공 색상: 1~10 노랑, 11~20 파랑, 21~30 빨강, 31~40 검정, 41~45 초록
  if 1 <= n <= 10:
    return "gold"  # 노랑
  elif 11 <= n <= 20:
    return "dodgerblue"  # 파랑
  elif 21 <= n <= 30:
    return "red"  # 빨강
  elif 31 <= n <= 40:
    return "black"  # 검정
  else:
    return "green"  # 초록


def tab1_content():
  st.markdown("""
  <div style='background-color:#111; border-radius:20px; padding:10px; text-align:center;'>
    <h2 style='color:gold; font-size:42px;'>🎵 밴드추천번호 생성기</h2>
    <p style='color:white; font-size:20px;'>본인 띠와 출생년도로 5조합을 확인하세요</p>
  </div>
  """, unsafe_allow_html=True)
  zodiac_years = {
    "쥐 🐭": [1948,1960,1972,1984,1996,2008,2020],
    "소 🐮": [1949,1961,1973,1985,1997,2009,2021],
    "호랑이 🐯": [1950,1962,1974,1986,1998,2010,2022],
    "토끼 🐰": [1951,1963,1975,1987,1999,2011,2023],
    "용 🐲": [1952,1964,1976,1988,2000,2012,2024],
    "뱀 🐍": [1953,1965,1977,1989,2001,2013,2025],
    "말 🐴": [1954,1966,1978,1990,2002,2014,2026],
    "양 🐑": [1955,1967,1979,1991,2003,2015,2027],
    "원숭이 🐵": [1956,1968,1980,1992,2004,2016,2028],
    "닭 🐔": [1957,1969,1981,1993,2005,2017,2029],
    "개 🐶": [1958,1970,1982,1994,2006,2018,2030],
    "돼지 🐷": [1959,1971,1983,1995,2007,2019,2031]
  }
  selected_zodiac = st.selectbox("띠 선택", list(zodiac_years.keys()), key="zodiac_select")
  selected_year = st.selectbox("출생년도 선택", zodiac_years[selected_zodiac], key="year_select")
  if st.button("행운의 5조합 🎲", key="btn_zodiac5"):
    base = selected_year
    all_combinations = []
    for i in range(5):
      numbers = []
      while len(numbers) < 6:
        num = (base + random.randint(1,999) + i*1000) % 45 + 1
        if num not in numbers:
          numbers.append(num)
      numbers.sort()
      all_combinations.append(numbers)
    # 5행 6열로 출력
    st.markdown("""
    <div style='display:flex;flex-direction:column;align-items:center;'>
    """, unsafe_allow_html=True)
    for comb in all_combinations:
      st.markdown(
        "".join([
          f"<span style='display:inline-block; background:{get_color(n)}; color:white; "
          f"border-radius:50%; width:60px; height:60px; text-align:center; "
          f"line-height:60px; margin:2px; font-size:22px;'>{n}</span>"
          for n in comb
        ]), unsafe_allow_html=True
      )
    st.markdown("</div>", unsafe_allow_html=True)


def tab2_content():
  st.markdown("""
  <div style='background-color:#222; border-radius:20px; padding:10px; text-align:center;'>
    <h2 style='color:deepskyblue; font-size:42px;'>🔮 주역 지역 추천</h2>
    <p style='color:white; font-size:20px;'>방위 기반 추천을 자동 또는 수동으로 선택하세요 (5조합)</p>
  </div>
  """, unsafe_allow_html=True)
  mode = st.radio("선택 모드", ["자동", "수동"], index=0, key="jx_mode2")
  regions = {
    "건(乾, 하늘·북서)": list(range(1,10)),
    "곤(坤, 땅·남서)": list(range(10,19)),
    "감(坎, 물·북)": list(range(19,28)),
    "리(離, 불·남)": list(range(28,37)),
    "중앙(中, 균형)": list(range(37,46))
  }
  def show_combinations(combs):
    st.markdown("""
    <div style='display:flex;flex-direction:column;align-items:center;'>
    """, unsafe_allow_html=True)
    for comb in combs:
      st.markdown(
        "".join([
          f"<span style='display:inline-block; background:{get_color(n)}; color:white; "
          f"border-radius:50%; width:60px; height:60px; text-align:center; "
          f"line-height:60px; margin:2px; font-size:22px;'>{n}</span>"
          for n in comb
        ]), unsafe_allow_html=True
      )
    st.markdown("</div>", unsafe_allow_html=True)
  if mode == "자동":
    if st.button("오늘의 방위 5조합 추천 🎲", key="jx_auto_btn2"):
      all_combinations = []
      for i in range(5):
        numbers = [random.choice(region) for region in regions.values()]
        while len(numbers) < 6:
          # 중복 방지: 랜덤 추가
          n = random.randint(1, 45)
          if n not in numbers:
            numbers.append(n)
        numbers = numbers[:6]
        numbers.sort()
        all_combinations.append(numbers)
      show_combinations(all_combinations)
  else:
    cols = st.columns(4)
    year = cols[0].number_input("년",2000,2100,2025,key="jx_year2")
    month = cols[1].number_input("월",1,12,12,key="jx_month2")
    day = cols[2].number_input("일",1,31,28,key="jx_day2")
    hour = cols[3].number_input("시",0,23,16,key="jx_hour2")
    if st.button("수동 방위 5조합 추천 🎲", key="jx_manual_btn2"):
      all_combinations = []
      for i in range(5):
        seed = year+month+day+hour+i*1000
        rng = random.Random(seed)
        numbers = [rng.choice(region) for region in regions.values()]
        while len(numbers) < 6:
          n = rng.randint(1, 45)
          if n not in numbers:
            numbers.append(n)
        numbers = numbers[:6]
        numbers.sort()
        all_combinations.append(numbers)
      show_combinations(all_combinations)

def tab3_content():
  import matplotlib
  matplotlib.rc('font', family='Malgun Gothic')  # 한글 폰트 설정
  matplotlib.rcParams['axes.unicode_minus'] = False  # 마이너스 깨짐 방지
  past_results = pd.read_csv("past_results.csv", header=None)
  past_results.columns = ["회차", "번호1", "번호2", "번호3", "번호4", "번호5", "번호6"]
  past_results["회차"] = past_results["회차"].str.replace("회차", "").astype(int)
  latest_round = past_results["회차"].max()
  st.markdown("<h2 style='color:orange;'>📊 통계 추천</h2>", unsafe_allow_html=True)
  # 회차 범위 옵션 및 실제 범위 계산
  ranges = [300, 150, 75, 45, 30, 15, 5]
  options = [f"최근 {r}회" for r in ranges]
  mode = st.selectbox("회차 범위 선택", options)
  n = int(mode.replace("최근 ", "").replace("회", ""))
  min_round = max(latest_round - n + 1, 1)
  data = past_results[(past_results["회차"] >= min_round) & (past_results["회차"] <= latest_round)]
  st.write(f"선택된 회차 범위: {min_round} ~ {latest_round}")
  numbers = pd.concat([
    data["번호1"], data["번호2"], data["번호3"],
    data["번호4"], data["번호5"], data["번호6"]
  ])
  freq = numbers.value_counts().sort_index()
  chart_type = st.radio("그래프 타입 선택", ["막대그래프", "꺾은선그래프"])
  fig, ax = plt.subplots(figsize=(8,2.8))  # 그래프 높이 축소
  if chart_type == "막대그래프":
    freq.plot(kind="bar", ax=ax, color="skyblue")
    ax.set_title("번호 빈도 - 막대그래프")
  elif chart_type == "꺾은선그래프":
    freq.plot(kind="line", ax=ax, marker="o", color="orange")
    ax.set_title("번호 빈도 - 꺾은선그래프")
  ax.set_xlabel("번호")
  ax.set_ylabel("출현 빈도")
  st.pyplot(fig)

  # hot/mid/cold num 표시
  freq_sorted = freq.sort_values(ascending=False)
  hot_nums = freq_sorted.head(6).index.tolist()
  cold_nums = freq_sorted.tail(6).index.tolist()
  mid_start = len(freq_sorted)//2 - 3
  mid_nums = freq_sorted.iloc[mid_start:mid_start+6].index.tolist() if len(freq_sorted) >= 12 else []
  def balls(nums):
    return "".join([
      f"<span style='display:inline-block; background:{get_color(n)}; color:white; border-radius:50%; width:40px; height:40px; text-align:center; line-height:40px; margin:4px; font-size:18px;'>{n}</span>"
      for n in nums
    ])
  st.markdown(f"<b>Hot Num</b>: {balls(sorted(hot_nums))}", unsafe_allow_html=True)
  if mid_nums:
    st.markdown(f"<b>Mid Num</b>: {balls(sorted(mid_nums))}", unsafe_allow_html=True)
  st.markdown(f"<b>Cold Num</b>: {balls(sorted(cold_nums))}", unsafe_allow_html=True)

  # 미출현 번호 표시 (선택 범위 내 한 번도 안 나온 번호)
  all_numbers = set(range(1, 46))
  appeared_numbers = set(numbers.unique())
  not_appeared = sorted(list(all_numbers - appeared_numbers))
  if not_appeared:
    st.markdown(f"<b>미출현 번호</b>: {balls(not_appeared)}", unsafe_allow_html=True)

def tab4_content():
  st.markdown("<h2 style='color:lime;'>🧠 AI 통합 추천</h2>", unsafe_allow_html=True)
  sets = [
    sorted([12, 18, 21, 25, 33, 39]),
    sorted([10, 17, 23, 28, 34, 41]),
    sorted([11, 19, 24, 29, 35, 42]),
    sorted([13, 20, 26, 30, 36, 43]),
    sorted([14, 22, 27, 31, 37, 44])
  ]
  def lotto_ball(num):
    color = get_color(num)
    return f"<span style='display:inline-block; background-color:{color}; color:white; border-radius:50%; width:60px; height:60px; line-height:60px; text-align:center; margin:8px; font-size:22px;'>{num}</span>"
  html = "<div style='display:flex;flex-direction:column;align-items:center;'>"
  for comb in sets:
    html += "<div style='display:flex;flex-direction:row;justify-content:center;margin-bottom:8px;'>"
    html += "".join([lotto_ball(n) for n in comb])
    html += "</div>"
  html += "</div>"
  st.markdown(html, unsafe_allow_html=True)


import streamlit as st
st.markdown("""
<style>
body, .stApp {
  background-color: #f4f4f7 !important;
}
</style>
""", unsafe_allow_html=True)
from PIL import Image
import datetime


st.set_page_config(layout="wide", page_title="로또 분석 레이아웃")

# ===== 상단 3분할 레이아웃 =====
col_left, col_center, col_right = st.columns([1.2, 2, 2.2], gap="large")
with col_left:
  st.markdown("""
  <style>
  .fancy-btn2 {
    background:#fff;
    border-radius:10px;
    font-size:16px;
    font-weight:700;
    padding:6px 16px;
    margin-bottom:7px;
    border:2px solid #7f7fd5;
    color:#7f7fd5;
    box-shadow:0 1px 4px rgba(127,127,213,0.08);
    cursor:pointer;
    transition:transform 0.08s, box-shadow 0.18s;
    display:flex; align-items:center; gap:6px;
    min-width:90px;
    min-height:32px;
    max-width:140px;
  }
  .fancy-btn2:active {
    transform:scale(0.95);
    box-shadow:0 1px 2px rgba(127,127,213,0.12);
  }
  .fancy-btn2 .finger {
    font-size:18px; margin-right:2px;
    animation: tap 0.5s infinite alternate;
  }
  @keyframes tap {
    0% { transform: translateY(0); }
    100% { transform: translateY(3px) scale(1.05); }
  }
  </style>
  <div style='display:flex; flex-direction:column; align-items:flex-start; gap:5px; margin-top:6px;'>
    <button class='fancy-btn2'><span class='finger'>👉</span>구독</button>
    <button class='fancy-btn2'><span class='finger'>👍</span>좋아요</button>
    <button class='fancy-btn2'>🔗 공유</button>
  </div>
  """, unsafe_allow_html=True)
with col_center:
  st.markdown("""
  <style>
  .header-row-final {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 18px;
    margin-top: 10px;
    width: 80%;
    min-width: 600px;
    max-width: 950px;
    white-space: nowrap;
  }
  .header-emoji-final {
    font-size: 48px;
    margin: 0 10px 0 0;
    filter: drop-shadow(0 2px 8px #ffd70088);
    display: inline-block;
    vertical-align: middle;
  }
  .header-title-final {
    font-size: 48px;
    font-weight: 900;
    color: #7f7fd5;
    letter-spacing: 0.08em;
    text-shadow: 2px 4px 12px #b3b3e6, 0 2px 0 #fff;
    margin-right: 18px;
    display: inline-block;
    vertical-align: middle;
    line-height: 1;
    white-space: nowrap;
  }
  .header-slogan-final {
    font-size: 38px;
    font-weight: 900;
    color: #ff3c00;
    letter-spacing: 0.04em;
    margin-left: 18px;
    text-shadow: 2px 4px 12px #ffb3b3, 0 2px 0 #fff;
    background: none;
    -webkit-background-clip: unset;
    -webkit-text-fill-color: unset;
    background-clip: unset;
    display: inline-block;
    line-height: 1;
    white-space: nowrap;
    vertical-align: middle;
  }
  </style>
  <div class='header-row-final'>
    <span class='header-emoji-final'>✨</span>
    <span class='header-title-final'>로또킹</span>
    <span class='header-emoji-final'>👑</span>
    <span class='header-slogan-final'>1등을 향하여</span>
  </div>
  """, unsafe_allow_html=True)
with col_right:
  # 회차 및 날짜 계산
  today = datetime.date.today()
  base_round = 1205
  base_date = datetime.date(2026, 1, 3)
  days_diff = (today - base_date).days
  if days_diff >= 0:
    round_num = base_round + (days_diff // 7)
    next_draw = base_date + datetime.timedelta(days=7 * ((days_diff // 7) + 1))
  else:
    round_num = base_round
    next_draw = base_date
  st.markdown(f"""
  <div style='text-align:right; margin-top:10px;'>
    <span style='font-size:22px; font-weight:700; color:#222;'>
      {round_num}회차
    </span><br>
    <span style='font-size:16px; color:#666;'>
      추첨일: {next_draw.strftime('%Y년 %m월 %d일')} 21시까지
    </span>
  </div>
  """, unsafe_allow_html=True)

# CSS 스타일 정의
st.markdown("""
<style>
.aspect-12-9 {
  position: relative;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,.15);
}
.aspect-12-9::before {
  content: "";
  display: block;
  padding-top: 75%;
}
.aspect-12-9 > .content {
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: 1fr 4fr;
  gap: 20px;
  background: #e6e0f8;
  padding: 20px;
  box-sizing: border-box;
}
.left-column {
  display: grid;
  grid-template-rows: repeat(4, 1fr);
  gap: 20px;
}
.frame {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,.1);
  display: flex;
  align-items: center;
  justify-content: center;
}
.button-custom {
  width: 100px;
  height: 40px;
  background-color: #28a745;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.button-custom:hover {
  background-color: #218838;
}
.big-frame {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,.1);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.big-frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)



# Streamlit columns로 레이아웃 분리 (왼쪽 버튼, 오른쪽 big-frame+이미지)

# 왼쪽 밴드추천번호 프레임을 세로로 일정 간격으로 배치
left, right = st.columns([1, 4], gap="large")
with left:
  st.markdown(
    """
    <div style="display: flex; flex-direction: column; gap: 32px; margin-top: 30px;">
    """,
    unsafe_allow_html=True
  )
  # 멋진 버튼 스타일 CSS (st.button에만 적용)
  st.markdown("""
  <style>
  div.stButton > button {
    width: 180px;
    height: 54px;
    margin-bottom: 22px;
    background: linear-gradient(90deg, #7f7fd5 0%, #86a8e7 50%, #91eac9 100%);
    color: #fff;
    border: none;
    border-radius: 18px;
    font-size: 20px;
    font-weight: 700;
    box-shadow: 0 4px 16px rgba(80,80,180,0.13);
    cursor: pointer;
    transition: transform 0.1s, box-shadow 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    letter-spacing: 1px;
  }
  div.stButton > button:hover {
    background: linear-gradient(90deg, #91eac9 0%, #86a8e7 50%, #7f7fd5 100%);
    transform: translateY(-2px) scale(1.04);
    box-shadow: 0 8px 24px rgba(80,80,180,0.18);
  }
  </style>
  """, unsafe_allow_html=True)
  # st.button + 이모지로 멋진 버튼
  if st.button("🎵 밴드추천번호"):
    st.session_state['show_tab'] = 'tab1'
  if st.button("🧭 주역 추천번호"):
    st.session_state['show_tab'] = 'tab2'
  if st.button("📊 통계 추천"):
    st.session_state['show_tab'] = 'tab3'
  if st.button("🧠 AI 통합 추천"):
    st.session_state['show_tab'] = 'tab4'

  st.markdown("</div>", unsafe_allow_html=True)
with right:
  st.markdown('<div class="big-frame">', unsafe_allow_html=True)
  show_tab = st.session_state.get('show_tab')
  if show_tab in ['tab1', 'tab2', 'tab3', 'tab4']:
    col_btn, _ = st.columns([2, 7])
    with col_btn:
      if st.button('메인으로', key='main_back', help='메인 화면으로 이동'):
        st.session_state['show_tab'] = None
    if show_tab == 'tab1':
      tab1_content()
    elif show_tab == 'tab2' or show_tab == 'tab4':
      # 구독/좋아요 버튼 및 카운트 표시
      if 'subscribe_count' not in st.session_state:
          st.session_state['subscribe_count'] = 0
      if 'like_count' not in st.session_state:
          st.session_state['like_count'] = 0
      col1, col2 = st.columns([1, 1])
      with col1:
          if st.button('👍 좋아요'):
              st.session_state['like_count'] += 1
          st.markdown(f"<b>좋아요 수:</b> {st.session_state['like_count']}")
      with col2:
          if st.button('👉 구독'):
              st.session_state['subscribe_count'] += 1
          st.markdown(f"<b>구독자 수:</b> {st.session_state['subscribe_count']}")
      if show_tab == 'tab2':
        tab2_content()
      else:
        tab4_content()
    elif show_tab == 'tab3':
      tab3_content()
  else:
    # 썸네일 업로드 및 자동 교체 기능
    st.markdown("<b>썸네일 이미지 업로드/자동교체</b>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("썸네일 업로드 (jpg/png)", type=["jpg", "jpeg", "png"], key="thumb_upload")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state['main_thumbnail'] = image
        st.success("썸네일이 업로드되었습니다!")
    # 자동 썸네일 교체: 여러 이미지 중 무작위/순차 선택
    import os, random
    thumb_dir = os.path.dirname(os.path.abspath(__file__))
    thumb_candidates = [f for f in os.listdir(thumb_dir) if f.startswith('lottoking') and f.lower().endswith(('.jpg','.jpeg','.png'))]
    # 업로드 썸네일 우선, 없으면 랜덤, 없으면 기본
    if 'main_thumbnail' in st.session_state:
        st.image(st.session_state['main_thumbnail'], width=1280)
    elif thumb_candidates:
        pick = random.choice(thumb_candidates)
        image = Image.open(os.path.join(thumb_dir, pick))
        st.image(image, width=1280)
    else:
        image = Image.open("lottoking1.jpg")
        st.image(image, width=1280)
  st.markdown('</div>', unsafe_allow_html=True)
  # 메인 화면 하단 경고 메시지
  st.markdown("""
  <div style='margin-top:32px; padding:18px 0 0 0; text-align:center; color:#b00; font-size:17px; font-weight:600;'>
    ⚠️ 로또 번호 예측은 불가능합니다. 본 데이터는 분석 참고용일 뿐입니다. 실제 투자, 도박, 구매 등에는 신중을 기하시기 바랍니다.<br>
  </div>
  """, unsafe_allow_html=True)





