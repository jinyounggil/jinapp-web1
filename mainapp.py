import streamlit as st
import streamlit.components.v1 as components
import random
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import base64
from io import BytesIO, StringIO
import requests
import urllib.parse
try:
    import cv2
    cv2_available = True
except ImportError:
    cv2_available = False
import numpy as np
import re
from bs4 import BeautifulSoup
import platform
import uuid

# 페이지 설정 (가장 먼저 호출)
st.set_page_config(layout="wide", page_title="로또킹 분석", initial_sidebar_state="collapsed")

# Query-Parameter를 이용한 탭 관리
if 'show_tab' not in st.session_state:
    try:
        st.session_state['show_tab'] = st.query_params.get('tab')
    except:
        st.session_state['show_tab'] = None

# 세션 상태 초기화
if 'subscribe_count' not in st.session_state:
    st.session_state['subscribe_count'] = 0
if 'like_count' not in st.session_state:
    st.session_state['like_count'] = 0
if 'is_subscribed' not in st.session_state:
    st.session_state['is_subscribed'] = False
if 'update_dismissed' not in st.session_state:
    st.session_state['update_dismissed'] = False

# '좋아요' 및 '구독' 클릭 처리 (인터랙티브 효과 추가)
try:
    action = st.query_params.get("action")
    
    if action == "restore_subscribe":
        st.session_state['is_subscribed'] = True
        if "action" in st.query_params:
            del st.query_params["action"]
        st.rerun()

    elif action == "restore_update_dismissed":
        st.session_state['update_dismissed'] = True
        if "action" in st.query_params:
            del st.query_params["action"]
        st.rerun()

    elif action == "dismiss_update":
        st.session_state['update_dismissed'] = True
        st.markdown("<script>localStorage.setItem('lotto_update_dismissed', 'true');</script>", unsafe_allow_html=True)
        if "action" in st.query_params:
            del st.query_params["action"]
        st.rerun()
        
    elif action == "like":
        st.session_state.like_count += 1
        try:
            st.balloons() # 좋아요 클릭 시 풍선 효과
        except:
            pass # 효과 실패해도 로직은 계속 진행
        
        if "action" in st.query_params:
            del st.query_params["action"]
    
    elif action == "subscribe":
        st.session_state['is_subscribed'] = not st.session_state['is_subscribed']
        if st.session_state['is_subscribed']:
            try:
                st.snow() # 구독 클릭 시 눈내림 효과
                st.toast("🎉 구독 감사합니다! 매주 행운의 번호를 받아보세요! 🎁")
                st.markdown("<script>localStorage.setItem('lotto_subscribed', 'true');</script>", unsafe_allow_html=True)
            except:
                pass
        else:
            try:
                st.toast("구독이 취소되었습니다. 다음에 또 만나요! 👋")
                st.markdown("<script>localStorage.removeItem('lotto_subscribed');</script>", unsafe_allow_html=True)
            except:
                pass
        
        if "action" in st.query_params:
            del st.query_params["action"]

except Exception:
    # st.query_params가 지원되지 않는 환경 등 예외 처리
    pass

# 브라우저 로컬 스토리지 확인 및 상태 복원 스크립트
if not st.session_state['is_subscribed']:
    st.markdown("""
    <script>
        if (localStorage.getItem('lotto_subscribed') === 'true') {
            const params = new URLSearchParams(window.location.search);
            if (!params.has('action')) {
                window.location.href = "?action=restore_subscribe";
            }
        }
    </script>
    """, unsafe_allow_html=True)

# 알림창 즉시 숨김을 위한 CSS 가드 (깜빡임 방지)
st.markdown("""
<script>
    if (localStorage.getItem('lotto_update_dismissed') === 'true') {
        document.write('<style>.update-card { display: none !important; }</style>');
    }
</script>
""", unsafe_allow_html=True)

# 알림창 닫기 상태 복원 스크립트
if not st.session_state['update_dismissed']:
    st.markdown("""
    <script>
        if (localStorage.getItem('lotto_update_dismissed') === 'true') {
            const params = new URLSearchParams(window.location.search);
            if (!params.has('action')) {
                window.location.href = "?action=restore_update_dismissed";
            }
        }
    </script>
    """, unsafe_allow_html=True)


# ----- tab1~tab4 UI 함수 직접 정의 -----
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

def generate_lotto_balls_html(numbers, size, font_size, margin="2px", use_flex=False, extra_css="", opacity_map=None, highlight_nums=None):
    """로또 공 목록에 대한 HTML을 생성합니다. (3D 입체 효과 + 내부 흰색 원 적용)"""
    html_output = []
    for n in numbers:
        color = get_color(n)
        # 텍스트는 내부 흰색 원 안에 들어가므로 항상 검정색
        text_color = "black" 
        opacity = opacity_map.get(n, 1.0) if opacity_map else 1.0
        
        # 반짝이는 애니메이션 효과 (일치하는 번호일 경우)
        animation_style = ""
        if highlight_nums and n in highlight_nums:
            animation_style = "animation: blink-effect 0.8s infinite alternate; border: 2px solid #fff700;"
        
        # 입체적인 외부 공 스타일 (그라데이션 + 그림자)
        outer_style = f"""
            background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.8), {color} 40%, rgba(0,0,0,0.6) 120%);
            box-shadow: 2px 3px 5px rgba(0,0,0,0.4), inset -2px -2px 5px rgba(0,0,0,0.2);
            border-radius: 50%; width:{size}px; height:{size}px;
            display:inline-flex; align-items:center; justify-content:center;
            margin:{margin}; opacity:{opacity}; {extra_css} {animation_style}
        """
        
        # 내부 흰색 원 스타일
        inner_size = int(size * 0.65) # 공 크기의 65%
        inner_style = f"""
            background: white; width:{inner_size}px; height:{inner_size}px; border-radius:50%;
            display:flex; align-items:center; justify-content:center;
            color:black; font-weight:bold; font-size:{font_size}px;
            box-shadow: inset 1px 1px 2px rgba(0,0,0,0.3);
        """
        
        html_output.append(f"<div style='{outer_style}'><div style='{inner_style}'>{n}</div></div>")
        
    return "".join(html_output)


@st.cache_data
def load_lotto_data():
    """
    과거 로또 당첨 데이터를 CSV 파일에서 로드하고 전처리합니다. 오류 발생 시 None을 반환합니다.
    '추천회차.csv'와 'past_results.csv' 중 더 최신 회차가 있는 데이터를 자동으로 선택합니다.
    """
    try:
        # 파일 경로를 절대 경로로 설정하여 서버 환경에서의 경로 오류 방지
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 확인해볼 파일 후보군
        candidate_files = ["추천회차.csv", "past_results.csv"]
        
        # 인코딩 호환성을 위해 여러 인코딩 시도
        encodings = ['utf-8-sig', 'cp949', 'euc-kr']
        
        best_df = None
        max_round = -1
        
        for fname in candidate_files:
            csv_path = os.path.join(base_dir, fname)
            if not os.path.exists(csv_path):
                continue
            
            current_df = None
            for enc in encodings:
                try:
                    # CSV 읽기 (헤더 없음)
                    temp_df = pd.read_csv(csv_path, header=None, encoding=enc)
                    
                    # 열 개수 체크 (최소 7개: 회차 + 번호 6개)
                    if temp_df.shape[1] < 7:
                        continue
                        
                    # 8열(보너스 포함)이어도 앞의 7열만 사용
                    temp_df = temp_df.iloc[:, :7]
                    temp_df.columns = ["회차", "번호1", "번호2", "번호3", "번호4", "번호5", "번호6"]
                    
                    # 회차에서 숫자만 추출 (예: '1216회차' -> 1216)
                    try:
                        temp_df["회차_int"] = temp_df["회차"].astype(str).str.replace(r'\D+', '', regex=True).astype(int)
                    except:
                        continue
                        
                    current_df = temp_df
                    break
                except Exception:
                    continue
            
            # 로드 성공 시, 가장 높은 회차인지 비교
            if current_df is not None and not current_df.empty:
                current_max = current_df["회차_int"].max()
                if current_max > max_round:
                    max_round = current_max
                    best_df = current_df

        if best_df is not None:
            return best_df.sort_values("회차_int", ascending=False)
        else:
            return None

    except (FileNotFoundError, Exception) as e:
        # st.error() 호출을 제거하여 앱 시작 시 레이아웃이 깨지는 것을 방지합니다.
        # 오류 처리는 이 함수를 호출하는 각 UI 섹션에서 담당합니다.
        print(f"데이터 로드 중 오류 발생: {e}") # 서버 로그용
        return None

def display_combinations_result(show_result_key, combinations_key):
    """Streamlit 세션 상태를 기반으로 로또 조합 목록을 표시합니다."""
    result_placeholder = st.empty()
    with result_placeholder.container():
        if st.session_state.get(show_result_key) and st.session_state.get(combinations_key):
            html_output = "<div style='display:flex;flex-direction:column;align-items:center; margin-top:20px;'>"
            for comb in st.session_state[combinations_key]:
                html_output += f"<div style='margin:10px 0;'>{generate_lotto_balls_html(comb, size=60, font_size=22)}</div>"
            html_output += "</div>"
            st.markdown(html_output, unsafe_allow_html=True)

def update_lotto_data_online():
    """
    온라인에서 최신 로또 당첨 데이터를 다운로드하여 past_results.csv 파일을 업데이트합니다.
    """
    url = "https://www.dhlottery.co.kr/common.do?method=allWinExel&gubun=byWin"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Host': 'www.dhlottery.co.kr',
        'Origin': 'https://www.dhlottery.co.kr',
        'Connection': 'keep-alive',
        'Referer': 'https://www.dhlottery.co.kr/gameResult.do?method=byWin',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }
    try:
        response = requests.get(url, timeout=15, headers=headers, verify=False) # SSL 검증 우회
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return False, f"데이터 다운로드에 실패했습니다: {e}"

    try:
        # header=1로 하면 '회차별 당첨번호' 행을 헤더로 사용
        # BeautifulSoup를 사용하여 불안정한 HTML에서도 테이블을 안정적으로 찾습니다.
        # 1. 'cp949'로 디코딩하되, 오류가 나는 문자는 깨짐 문자로 대체(replace)합니다.
        html_text = response.content.decode('cp949', errors='replace')
        
        # 2. BeautifulSoup으로 HTML을 파싱합니다.
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # 3. 파싱된 문서에서 'table' 태그를 찾습니다.
        table = soup.find('table')
        if not table:
            raise ValueError("HTML에서 테이블 구조를 찾지 못했습니다. (서버 응답 변경 가능성)")

        # 4. 찾은 테이블 부분만 pandas로 읽어들여 안정성을 높입니다.
        dfs = pd.read_html(StringIO(str(table)), header=1)
        if not dfs:
            raise ValueError("테이블 데이터를 데이터프레임으로 변환하지 못했습니다.")
        df_new = dfs[0]
        
        # '당첨번호'로 시작하는 열들을 찾음
        win_num_cols = [col for col in df_new.columns if str(col).startswith('당첨번호')]
        if len(win_num_cols) != 6:
             raise ValueError("당첨번호 열(6개)을 정확히 찾을 수 없습니다.")
        
        # 필요한 열만 선택하고 이름 변경
        required_cols = ['회차'] + win_num_cols
        df_new = df_new[required_cols].copy()
        df_new.columns = ["회차", "번호1", "번호2", "번호3", "번호4", "번호5", "번호6"]
        
        # 데이터 클리닝
        df_new = df_new.dropna(subset=['회차'])
        df_new = df_new[pd.to_numeric(df_new['회차'], errors='coerce').notna()]
        df_new['회차'] = df_new['회차'].astype(int)
        
        latest_new_round = df_new['회차'].max()

    except Exception as e:
        return False, f"다운로드한 파일 처리 중 오류가 발생했습니다: {e}"

    # 기존 데이터와 비교
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "past_results.csv")
    
    latest_old_round = 0
    if os.path.exists(file_path):
        try:
            for enc in ['utf-8-sig', 'cp949', 'euc-kr']:
                try:
                    df_old = pd.read_csv(file_path, header=None, encoding=enc)
                    break
                except UnicodeDecodeError:
                    continue
            df_old_int = df_old[0].str.replace("회차", "").astype(int)
            latest_old_round = df_old_int.max()
        except Exception:
            latest_old_round = 0

    if latest_new_round <= latest_old_round:
        return True, f"이미 최신 데이터입니다. (현재 {latest_old_round}회차)"

    df_new['회차'] = df_new['회차'].astype(str) + "회차"
    df_to_save = df_new.sort_values(by='회차', key=lambda x: x.str.replace('회차','').astype(int), ascending=True)

    try:
        df_to_save.to_csv(file_path, index=False, header=False, encoding='utf-8-sig')
        st.cache_data.clear()
        return True, f"업데이트 완료! {latest_new_round}회차까지 업데이트되었습니다."
    except Exception as e:
        return False, f"파일 저장 중 오류가 발생했습니다: {e}"

# --- 회차 및 날짜 계산 공통 함수 ---
def get_next_round_info():
    """
    현재 시간(KST)을 기준으로 다음 로또 회차와 추첨일을 정확히 계산합니다.
    1회차 기준: 2002년 12월 7일(토) 20:40
    """
    base_date = datetime.datetime(2002, 12, 7, 20, 40, 0)
    # DeprecationWarning 해결: timezone-aware 객체 생성 후 계산을 위해 naive로 변환
    utc_now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    kst_now = utc_now + datetime.timedelta(hours=9)
    
    # 기준일로부터 경과한 시간
    time_diff = kst_now - base_date
    weeks_passed = time_diff.days // 7
    
    # 이번 주 토요일 추첨 기준 시간 (계산된 주차의 토요일)
    upcoming_draw_date = base_date + datetime.timedelta(days=weeks_passed * 7)
    
    # 현재 시간이 이번 주 추첨 시간을 지났으면 다음 회차(weeks_passed + 2), 아니면 이번 회차(weeks_passed + 1)
    # 1회차부터 시작하므로 인덱스 보정 필요
    if kst_now > upcoming_draw_date:
        next_round = weeks_passed + 2
    else:
        next_round = weeks_passed + 1
        
    next_date = base_date + datetime.timedelta(days=(next_round - 1) * 7)
    return next_round, next_date.strftime("%Y-%m-%d")

def tab1_content():
  # session_state 초기화
  if 'tab1_combinations' not in st.session_state:
    st.session_state['tab1_combinations'] = []
  if 'tab1_show_result' not in st.session_state:
    st.session_state['tab1_show_result'] = False
  
  st.markdown("""
  <div style='background-color:#111; border-radius:20px; padding:10px; text-align:center;'>
    <h2 style='color:gold; font-size:42px;'>🎵 띠별추천번호 생성기</h2>
    <p style='color:white; font-size:20px;'>본인 띠와 출생 년도로 10조합을 확인하세요</p>
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
  
  if st.button("행운의 10조합 🎲", key="btn_zodiac5"):
    base = selected_year
    all_combinations = []
    for i in range(10):
      numbers = []
      while len(numbers) < 10:
        num = (base + random.randint(1,999) + i*1000) % 45 + 1
        if num not in numbers:
          numbers.append(num)
      numbers.sort()
      all_combinations.append(numbers)
    
    st.session_state['tab1_combinations'] = all_combinations
    st.session_state['tab1_show_result'] = True
  
  # 결과 표시 영역 (placeholder 사용)
  display_combinations_result('tab1_show_result', 'tab1_combinations')


def tab2_content():
  # session_state 초기화
  if 'tab2_combinations' not in st.session_state:
    st.session_state['tab2_combinations'] = []
  if 'tab2_show_result' not in st.session_state:
    st.session_state['tab2_show_result'] = False
  
  st.markdown("""
  <div style='background-color:#222; border-radius:20px; padding:10px; text-align:center;'>
    <h2 style='color:deepskyblue; font-size:42px;'>🔮 주역 지역 추천</h2>
    <p style='color:white; font-size:20px;'>방위 기반 추천을 자동 또는 수동으로 선택하세요 (10조합)</p>
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
  
  if mode == "자동":
    if st.button("오늘의 방위 10조합 추천 🎲", key="jx_auto_btn2"):
      now = datetime.datetime.now()
      seed_val = int(now.strftime("%Y%m%d")) # 오늘 날짜를 시드로 고정하여 하루 동안 같은 결과 유지
      all_combinations = []
      for i in range(10):
        rng = random.Random(seed_val + i * 1000) # 게임별로 시드 간격을 두어 고유한 조합 생성
        numbers = [rng.choice(region) for region in regions.values()]
        while len(numbers) < 10:
          # 중복 방지: 랜덤 추가
          n = rng.randint(1, 45)
          if n not in numbers:
            numbers.append(n)
        numbers = numbers[:10]
        numbers.sort()
        all_combinations.append(numbers)
      
      st.session_state['tab2_combinations'] = all_combinations
      st.session_state['tab2_show_result'] = True
      st.success(f"📅 {now.year}년 {now.month}월 {now.day}일의 운세로 생성된 오늘의 고정 번호입니다.")
  else:
    cols = st.columns(4)
    year = cols[0].number_input("년",1900,2100,2025,key="jx_year2")
    month = cols[1].number_input("월",1,12,12,key="jx_month2")
    day = cols[2].number_input("일",1,31,28,key="jx_day2")
    hour = cols[3].number_input("시",0,23,16,key="jx_hour2")
    
    if st.button("수동 방위 10조합 추천 🎲", key="jx_manual_btn2"):
      all_combinations = []
      for i in range(10):
        seed = year+month+day+hour+i*1000
        rng = random.Random(seed)
        numbers = [rng.choice(region) for region in regions.values()]
        while len(numbers) < 10:
          n = rng.randint(1, 45)
          if n not in numbers:
            numbers.append(n)
        numbers = numbers[:10]
        numbers.sort()
        all_combinations.append(numbers)
      
      st.session_state['tab2_combinations'] = all_combinations
      st.session_state['tab2_show_result'] = True
  
  # 결과 표시 영역 (placeholder 사용)
  display_combinations_result('tab2_show_result', 'tab2_combinations')


def tab3_content():
  next_round, next_date = get_next_round_info()
  
  import matplotlib
  import matplotlib.font_manager as fm

  # OS별 한글 폰트 설정
  system_name = platform.system()
  if system_name == 'Windows':
      plt.rc('font', family='Malgun Gothic')
  elif system_name == 'Darwin': # Mac
      plt.rc('font', family='AppleGothic')
  else: # Linux (Streamlit Cloud)
      path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
      if os.path.exists(path):
          font_name = fm.FontProperties(fname=path).get_name()
          plt.rc('font', family=font_name)
      else:
          plt.rc('font', family='DejaVu Sans') # 폰트 없을 시 기본값
  
  # 그래프 텍스트 및 라인 흰색 설정 (다크 모드 대응)
  plt.rcParams.update({
      "text.color": "white",
      "axes.labelcolor": "white",
      "xtick.color": "white",
      "ytick.color": "white",
      "axes.edgecolor": "white",
      "axes.unicode_minus": False # 마이너스 깨짐 방지
  })

  past_results = load_lotto_data()
  if past_results is None:
      st.error("`past_results.csv` 파일을 찾을 수 없거나 데이터가 손상되었습니다. 앱을 재시작하거나 데이터를 확인해주세요.")
      return
  latest_round = past_results["회차_int"].max()
  
  # 현재 분석 중인 회차 정보 배너 표시
  st.info(f"📢 **현재 분석 대상:** 제 {next_round}회차 예측 ({next_date} 추첨) | **최신 데이터:** {latest_round}회까지 반영됨")

  st.markdown("<h2 style='color:orange;'>📊 통계 추천</h2>", unsafe_allow_html=True)
  st.markdown(f"""
  <div style='text-align:right; color:#ccc; font-size:14px; margin-bottom:10px;'>
      🎯 목표: <b>제 {next_round}회 당첨</b> 도전
  </div>
  """, unsafe_allow_html=True)

  # 회차 범위 옵션 및 실제 범위 계산
  ranges = [300, 150, 75, 45, 30, 15, 5]
  options = [f"최근 {r}회" for r in ranges]
  mode = st.selectbox("회차 범위 선택", options)
  n = int(mode.replace("최근 ", "").replace("회", ""))
  min_round = max(latest_round - n + 1, 1)
  data = past_results[(past_results["회차_int"] >= min_round) & (past_results["회차_int"] <= latest_round)]
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
  
  # 그래프 배경 투명화
  fig.patch.set_alpha(0)
  ax.patch.set_alpha(0)
  
  st.pyplot(fig)

  # hot/mid/cold num 표시
  freq_sorted = freq.sort_values(ascending=False)
  hot_nums = freq_sorted.head(10).index.tolist()
  hot_nums_10 = freq_sorted.head(10).index.tolist()
  cold_nums = freq_sorted.tail(10).index.tolist()
  mid_start = max(0, len(freq_sorted)//2 - 5)
  mid_nums = freq_sorted.iloc[mid_start:mid_start+10].index.tolist() if len(freq_sorted) >= 10 else []
  def balls(nums):
    return generate_lotto_balls_html(nums, size=40, font_size=18, margin="4px")
  
  st.markdown(f"<div style='color:white; margin-bottom:5px;'><b>Hot Num</b> (최다 출현): {balls(sorted(hot_nums))}</div>", unsafe_allow_html=True)
  if mid_nums:
    st.markdown(f"<div style='color:white; margin-bottom:5px;'><b>Mid Num</b> (중간 출현): {balls(sorted(mid_nums))}</div>", unsafe_allow_html=True)
  st.markdown(f"<div style='color:white; margin-bottom:5px;'><b>Cold Num</b> (최소 출현): {balls(sorted(cold_nums))}</div>", unsafe_allow_html=True)

  # 미출현 번호 표시 (선택 범위 내 한 번도 안 나온 번호)
  all_numbers = set(range(1, 46))
  appeared_numbers = set(numbers.unique())
  not_appeared = sorted(list(all_numbers - appeared_numbers))
  if not_appeared:
    st.markdown(f"<div style='color:white; margin-top:10px;'><b>미출현 번호</b>: {balls(not_appeared)}</div>", unsafe_allow_html=True)

  # 최다 빈도 10수 추천 기능
  st.markdown("---")
  if st.button("🏆 최다 빈도 10수 조합 추천", key="btn_stat_rec"):
      if len(hot_nums_10) >= 10:
          rec_nums = sorted(hot_nums_10)
          st.markdown(f"""
          <div style='background-color:rgba(255,255,255,0.1); border-radius:15px; padding:20px; text-align:center; margin-top:15px; border:1px solid rgba(255,255,255,0.2);'>
              <h3 style='color:#ffd700; margin-bottom:15px;'>👑 통계 기반 강력 추천 (Top 10)</h3>
              <div style='display:flex; justify-content:center; gap:10px; flex-wrap:wrap;'>
                  {generate_lotto_balls_html(rec_nums, size=60, font_size=24, use_flex=True)}
              </div>
              <p style='color:#ddd; margin-top:15px; font-size:14px;'>
                  선택하신 기간 동안 가장 많이 당첨된 번호 10개입니다.
              </p>
          </div>
          """, unsafe_allow_html=True)
      else:
          st.warning("데이터가 부족하여 추천할 수 없습니다.")

def tab4_content():
  next_round, next_date = get_next_round_info()
  # session_state 초기화
  if 'ai_combinations' not in st.session_state:
    st.session_state['ai_combinations'] = []
  if 'ai_show_result' not in st.session_state:
    st.session_state['ai_show_result'] = False
  
  st.markdown("<h2 style='color:lime;'>🧠 AI 통합 추천</h2>", unsafe_allow_html=True)
  
  # AI 분석 목표 회차 표시
  st.markdown(f"""
  <div style='background:rgba(0,255,0,0.1); padding:10px; border-radius:10px; border:1px solid lime; text-align:center; margin-bottom:20px;'>
      🚀 <b>제 {next_round}회 ({next_date})</b> 당첨번호 AI 예측 분석 중
  </div>
  """, unsafe_allow_html=True)

  past_results = load_lotto_data()
  if past_results is None:
      st.error("`past_results.csv` 파일을 찾을 수 없거나 데이터가 손상되었습니다. 앱을 재시작하거나 데이터를 확인해주세요.")
      return
    
  # 과거 데이터 로드 및 고급 분석
  try:
    # 최근 300회 데이터 분석
    recent_data = past_results.head(300)
    all_numbers = pd.concat([
      recent_data["번호1"], recent_data["번호2"], recent_data["번호3"],
      recent_data["번호4"], recent_data["번호5"], recent_data["번호6"]
    ])
    
    # 1. 빈도 분석
    freq = all_numbers.value_counts()
    freq_sorted = freq.sort_values(ascending=False)
    
    # 2. 최근 추세 분석 (최근 50회 vs 전체)
    recent_50 = past_results.head(50)
    recent_numbers = pd.concat([
      recent_50["번호1"], recent_50["번호2"], recent_50["번호3"],
      recent_50["번호4"], recent_50["번호5"], recent_50["번호6"]
    ])
    recent_freq = recent_numbers.value_counts()
    
    # 3. 미출현 기간 분석 (오래 안 나온 번호)
    last_appearance = {}
    for num in range(1, 46):
      last_appearance[num] = 999
    
    # recent_data는 최신순으로 정렬되어 있음
    for i, (idx, row) in enumerate(recent_data.iterrows()):
      round_gap = i + 1
      for col in ["번호1", "번호2", "번호3", "번호4", "번호5", "번호6"]:
        num = row[col]
        if last_appearance[num] == 999:
          last_appearance[num] = round_gap
    
    # 당첨 패턴 분석 (홀짝 비율, 구간 분포)
    odd_ratios = []
    for idx, row in recent_data.iterrows():
      nums = [row["번호1"], row["번호2"], row["번호3"], row["번호4"], row["번호5"], row["번호6"]]
      odd_count = sum(1 for n in nums if n % 2 == 1)
      odd_ratios.append(odd_count)
    
    avg_odd = sum(odd_ratios) / len(odd_ratios)
    
    has_data = True
  except Exception:
    # 데이터 없을 경우 균등 가중치
    has_data = False
    freq, recent_freq, last_appearance = pd.Series(), pd.Series(), {}
    avg_odd = 3

  # AI 가중치 조절 UI
  with st.expander("⚖️ AI 가중치 조절", expanded=True):
      col1, col2, col3 = st.columns(3)
      with col1:
          weight_freq_user = st.slider("빈도 분석 (%)", 0, 100, 50, key="w_freq")
      with col2:
          weight_trend_user = st.slider("최근 추세 (%)", 0, 100, 30, key="w_trend")
      with col3:
          weight_gap_user = st.slider("미출현 패턴 (%)", 0, 100, 20, key="w_gap")

      total_weight_val = weight_freq_user + weight_trend_user + weight_gap_user
      if total_weight_val == 0:
          st.warning("가중치 총합이 0이 될 수 없습니다. 기본값(50:30:20)을 사용합니다.")
          w_f, w_t, w_g = 0.5, 0.3, 0.2
      else:
          w_f = weight_freq_user / total_weight_val
          w_t = weight_trend_user / total_weight_val
          w_g = weight_gap_user / total_weight_val
      
      st.info(f"적용 가중치: 빈도 {w_f:.0%} | 최근 추세 {w_t:.0%} | 미출현 {w_g:.0%}")

  # 통합 가중치 계산
  weights = {}
  if not has_data:
      weights = {i: 1.0 for i in range(1, 46)}
  else:
      freq_max = freq.max() if not freq.empty and freq.max() > 0 else 1
      recent_freq_max = recent_freq.max() if not recent_freq.empty and recent_freq.max() > 0 else 1
      
      for i in range(1, 46):
          freq_weight = freq.get(i, 0) / freq_max
          recent_weight = recent_freq.get(i, 0) / recent_freq_max
          gap = last_appearance.get(i, 0)
          gap_weight = min(gap / 100, 1.0) if gap > 30 else 0.3
          
          weights[i] = (freq_weight * w_f + recent_weight * w_t + gap_weight * w_g) * 2.0
          weights[i] = max(0.3, min(weights[i], 2.5))
  
  st.markdown("""
  <p style='color:white; font-size:15px; margin-bottom:20px;'>
  ✨ <b>AI 고급 분석:</b> 사용자 설정 가중치와 다양한 필터를 결합하여 최적의 조합을 추천합니다.
  </p>
  """, unsafe_allow_html=True)
  
  # 고급 설정 (제외수, 고정수)
  with st.expander("⚙️ 고급 설정 (제외수 / 고정수)"):
    col_ex, col_fix = st.columns(2)
    with col_ex:
      excluded_numbers = st.multiselect("🚫 제외할 번호", list(range(1, 46)), key="ai_exclude_nums")
    with col_fix:
      fixed_numbers = st.multiselect("📌 고정할 번호 (최대 5개)", list(range(1, 46)), key="ai_fixed_nums")
      if len(fixed_numbers) > 5:
        st.warning("고정수는 최대 5개까지만 선택 가능합니다.")

  # 번호 생성 함수 (고도화)
  def generate_combinations():
    combinations = []
    attempt = 0
    max_attempts = 100  # 고정수 사용 시 조건 만족이 어려울 수 있어 시도 횟수 증가
    
    # 고정수 처리 (제외수와 겹치면 제외수가 우선 -> 제외수에 있으면 고정수에서 제거)
    real_fixed = [n for n in fixed_numbers if n not in excluded_numbers]
    if len(real_fixed) > 5:
        real_fixed = real_fixed[:5]
        
    # 고정수 자체의 연속성 위반 여부 확인 (이미 위반 시 연속성 체크 패스)
    fixed_consecutive_violation = False
    if len(real_fixed) >= 3:
        nums_sorted = sorted(real_fixed)
        cnt = 0
        for j in range(len(nums_sorted)-1):
            if nums_sorted[j+1] - nums_sorted[j] == 1:
                cnt += 1
        if cnt > 2:
            fixed_consecutive_violation = True
    
    while len(combinations) < 10 and attempt < max_attempts:
      attempt += 1
      numbers = list(real_fixed)
      available = [n for n in range(1, 46) if n not in excluded_numbers and n not in numbers]
      
      if len(numbers) + len(available) < 10:
        break
      
      inner_attempt = 0
      while len(numbers) < 10:
        inner_attempt += 1
        if inner_attempt > 50: # 무한 루프 방지 안전장치
            break
            
        if not available:
            break
            
        remaining_weights = [weights[n] for n in available]
        total_weight = sum(remaining_weights)
        if total_weight == 0:
            if len(available) > 0:
                probabilities = [1/len(available)] * len(available)
            else:
                break
        else:
            probabilities = [w/total_weight for w in remaining_weights]
        
        selected = random.choices(available, weights=probabilities, k=1)[0]
        numbers.append(selected)
        available.remove(selected)
        
        # 연속번호 3개 초과 방지 (고정수가 이미 위반했으면 체크 건너뜀)
        if not fixed_consecutive_violation and len(numbers) >= 3:
          numbers_sorted = sorted(numbers)
          consecutive_count = 0
          for j in range(len(numbers_sorted)-1):
            if numbers_sorted[j+1] - numbers_sorted[j] == 1:
              consecutive_count += 1
          if consecutive_count > 2:
            available.append(numbers[-1])
            numbers.pop()
            continue
      
      if len(numbers) < 10:
        continue
      
      # 홀짝 비율 검증 (10개 중 3~7개가 홀수)
      odd_count = sum(1 for n in numbers if n % 2 == 1)
      if odd_count < 3 or odd_count > 7:
        continue
      
      # 구간 분포 검증 (5개 구간에 골고루 분포)
      zones = [0,0,0,0,0]
      for n in numbers:
        if n <= 10: zones[0] += 1
        elif n <= 20: zones[1] += 1
        elif n <= 30: zones[2] += 1
        elif n <= 40: zones[3] += 1
        else: zones[4] += 1
      
      # 특정 구간에 5개 이상 몰리면 제외 (10개 기준 완화)
      if max(zones) > 4:
        continue
      
      # 번호 합계 검증 (10개 합계 평균 약 230, 범위 150~310)
      total_sum = sum(numbers)
      if total_sum < 150 or total_sum > 310:
        continue
      
      numbers.sort()
      
      # 중복 조합 방지
      if numbers not in combinations:
        combinations.append(numbers)
    
    # 10개 미만이면 부족한 만큼 무작위 추가
    while len(combinations) < 10:
      available_fallback = [n for n in range(1, 46) if n not in excluded_numbers and n not in real_fixed]
      if len(available_fallback) + len(real_fixed) < 10:
        break
      
      needed = 10 - len(real_fixed)
      nums = sorted(real_fixed + random.sample(available_fallback, needed))
      if nums not in combinations:
        combinations.append(nums)
    
    return combinations
  
  # 버튼
  col1, col2 = st.columns([1, 1])
  
  with col1:
    if st.button("🎲 AI 추천 번호 생성", key="ai_gen_btn", width="stretch"):
      try:
        st.session_state['ai_combinations'] = generate_combinations()
        st.session_state['ai_show_result'] = True
        st.session_state['like_count'] += 1
      except Exception as e:
        st.error(f"번호 생성 중 오류가 발생했습니다: {e}")
  
  with col2:
    if st.button("🗑️ 초기화", key="ai_clear_btn", width="stretch"):
      st.session_state['ai_combinations'] = []
      st.session_state['ai_show_result'] = False
  
  # 결과 표시 영역 (placeholder 사용)
  result_placeholder = st.empty()
  
  with result_placeholder.container():
    if st.session_state['ai_show_result'] and len(st.session_state['ai_combinations']) > 0:
      st.markdown("---")
      
      # 전체 HTML을 한 번에 생성
      html_output = ""
      for i, comb in enumerate(st.session_state['ai_combinations']):
        # AI 예측 점수 계산 (가중치 + 패턴 점수)
        score = 0
        # 1. 가중치 점수 (0~50점) - weights 딕셔너리 활용
        w_sum = sum(weights.get(n, 1.0) for n in comb)
        w_score = min(50, int((w_sum / 10.0) * 50)) 
        
        # 2. 패턴 점수 (합계, 홀짝) (0~40점)
        s = sum(comb)
        if 120 <= s <= 140: score += 20
        elif 100 <= s <= 160: score += 10
        if 200 <= s <= 260: score += 20 # 10개 합계 기준
        elif 180 <= s <= 280: score += 10
        
        odd = sum(1 for n in comb if n % 2 == 1)
        if odd == 3: score += 20
        elif odd in [2, 4]: score += 15
        if odd == 5: score += 20 # 10개 중 절반
        elif odd in [4, 6]: score += 15
        else: score += 5
        
        # 최종 점수 (최대 99점, 최소 60점 보정)
        total_score = min(99, max(60, w_score + score + (s % 5)))
        
        html_output += f"<p style='color:white; font-weight:bold; margin:15px 0 5px 0;'>🎯 AI 조합 {i+1} <span style='font-size:12px; color:#aaa; font-weight:normal;'>(제 {next_round}회 예상)</span></p>"
        balls_html = generate_lotto_balls_html(comb, size=45, font_size=18, use_flex=True, extra_css="font-weight:bold; box-shadow:0 2px 4px rgba(0,0,0,0.2);")
        
        # 점수 표시 바 (색상 구분: 초록-높음, 주황-중간, 빨강-낮음)
        color = "#00c853" if total_score >= 85 else "#ffa500" if total_score >= 75 else "#ff4b4b"
        
        html_output += f"""
        <div style='display:flex; flex-direction:column; gap:5px; margin-bottom:20px;'>
            <div style='display:flex; gap:8px;'>{balls_html}</div>
            <div style='background-color:rgba(255,255,255,0.1); border-radius:8px; padding:8px 12px; margin-top:5px; display:flex; align-items:center; justify-content:space-between;'>
                <span style='color:white; font-size:14px;'>🤖 AI 당첨 예측지수</span>
                <div style='display:flex; align-items:center; gap:10px;'>
                    <div style='width:100px; height:8px; background:#444; border-radius:4px; overflow:hidden;'>
                        <div style='width:{total_score}%; height:100%; background:{color};'></div>
                    </div>
                    <span style='color:{color}; font-weight:bold; font-size:16px;'>{total_score}%</span>
                </div>
            </div>
        </div>
        """
      
      st.markdown(html_output, unsafe_allow_html=True)
      
      # --- 이미지 생성 및 다운로드 기능 ---
      def create_combinations_image(combinations, target_round):
          ball_size = 45 # 10개 배치 위해 사이즈 축소
          padding = 25
          h_spacing = 10
          v_spacing = 25
          title_v_offset = 30

          row_height = ball_size + v_spacing + title_v_offset
          img_width = padding * 2 + 10 * ball_size + 9 * h_spacing
          img_height = padding * 2 + len(combinations) * row_height - v_spacing

          image = Image.new('RGB', (img_width, img_height), (255, 255, 255))
          draw = ImageDraw.Draw(image)

          try:
              # OS별 폰트 경로 설정
              if platform.system() == 'Windows':
                  font_path = "malgun.ttf"
              elif platform.system() == 'Darwin':
                  font_path = "AppleGothic"
              else:
                  font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
              
              title_font = ImageFont.truetype(font_path, 20)
              ball_font = ImageFont.truetype(font_path, 26)
          except IOError:
              title_font = ImageFont.load_default()
              ball_font = ImageFont.load_default()

          color_map = {
              "gold": (255, 215, 0), "dodgerblue": (30, 144, 255),
              "red": (255, 0, 0), "black": (80, 80, 80), "green": (46, 139, 87)
          }

          for i, comb in enumerate(combinations):
              y_pos = padding + i * row_height
              draw.text((padding, y_pos), f"🎯 AI 조합 {i+1} (제 {target_round}회)", fill=(50, 50, 50), font=title_font)

              for j, num in enumerate(comb):
                  x_pos = padding + j * (ball_size + h_spacing)
                  box = [x_pos, y_pos + title_v_offset, x_pos + ball_size, y_pos + title_v_offset + ball_size]
                  
                  ball_color_name = get_color(num)
                  pillow_ball_color = color_map.get(ball_color_name, (128, 128, 128))
                  
                  # 1. 외부 색상 원 그리기
                  draw.ellipse(box, fill=pillow_ball_color, outline=(180,180,180), width=1)

                  # 2. 내부 흰색 원 그리기 (공 크기의 약 65%)
                  inner_ratio = 0.65
                  cx = x_pos + ball_size / 2
                  cy = y_pos + title_v_offset + ball_size / 2
                  r = (ball_size * inner_ratio) / 2
                  inner_box = [cx - r, cy - r, cx + r, cy + r]
                  draw.ellipse(inner_box, fill=(255, 255, 255), outline=(220, 220, 220), width=1)
                  
                  # 3. 숫자 그리기 (항상 검정색)
                  text_color = (0, 0, 0)
                  num_str = str(num)
                  bbox = draw.textbbox((0, 0), num_str, font=ball_font)
                  text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                  text_x = x_pos + (ball_size - text_width) / 2
                  text_y = y_pos + title_v_offset + (ball_size - text_height) / 2 - 4
                  draw.text((text_x, text_y), num_str, fill=text_color, font=ball_font)

          buf = BytesIO()
          image.save(buf, format='PNG')
          return buf.getvalue()
      
      image_bytes = create_combinations_image(st.session_state['ai_combinations'], next_round)
      st.download_button(
          label="🖼️ 이미지로 저장",
          data=image_bytes,
          file_name=f"lotto_ai_recommendations_{datetime.date.today()}.png",
          mime="image/png"
      )
      
      # 카카오톡/공유하기 기능 (JS 주입)
      share_text = "[👑 로또킹 AI 추천 번호]\\n"
      for idx, comb in enumerate(st.session_state['ai_combinations']):
          share_text += f"{idx+1}게임: {', '.join(map(str, comb))} (제 {next_round}회)\\n"
      share_text += "\\n당첨을 기원합니다! 🍀"
      
      components.html(f"""
      <style>
        .kakao-btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 40px;
            padding: 0.5rem;
            background-color: #FEE500;
            color: #3C1E1E;
            border: none;
            border-radius: 4px;
            font-family: "Source Sans Pro", sans-serif;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            text-decoration: none;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            transition: background-color 0.2s;
        }}
        .kakao-btn:hover {{
            background-color: #FADA0A;
        }}
      </style>
      <button class="kakao-btn" onclick="shareToKakao()">
        💬 카카오톡으로 공유 / 복사
      </button>
      <script>
        function shareToKakao() {{
            const text = `{share_text}`;
            if (navigator.share) {{
                navigator.share({{
                    title: '로또킹 추천 번호',
                    text: text
                }}).then(() => console.log('Shared successfully'))
                .catch((error) => console.log('Error sharing', error));
            }} else {{
                navigator.clipboard.writeText(text).then(function() {{
                    alert('📋 번호가 복사되었습니다!\\n카카오톡을 열고 붙여넣기(Ctrl+V) 하세요.');
                }}, function(err) {{
                    prompt('Ctrl+C를 눌러 복사하세요:', text);
                }});
            }}
        }}
      </script>
      """, height=50)

      if has_data:
        st.success("🎯 **10/10 AI 분석 완료:** 빈도·추세·미출현 패턴 + 구간균형 + 홀짝비율 + 번호합계 + 연속번호 제어 적용")
        
        # 분석 상세 정보 표시
        with st.expander("📊 AI 분석 세부 정보 보기"):
          st.markdown(f"""
          - **빈도 분석**: 최근 300회 데이터 기반 출현 빈도 (현재 가중치: {w_f:.0%})
          - **최근 추세**: 최근 50회 핫 번호 우선 선택 (현재 가중치: {w_t:.0%})
          - **미출현 패턴**: 30회 이상 미출현 번호 우대 (현재 가중치: {w_g:.0%})
          - **구간 균형**: 5개 구간(1-10, 11-20, 21-30, 31-40, 41-45) 균등 분포
          - **홀짝 비율**: 홀수 3~7개 유지 (10개 번호 기준)
          - **연속 번호**: 연속 3개 이상 제외
          - **번호 합계**: 150~310 범위 (10개 번호 기준)
          - **중복 방지**: 동일 조합 제외
          """)
    else:
      st.info("👆 위의 버튼을 눌러 AI가 분석한 추천 번호를 생성하세요!")


def tab5_content():
  st.markdown("""
  <div style='background-color:#333; border-radius:20px; padding:10px; text-align:center;'>
    <h2 style='color:gold; font-size:36px;'>🏆 당첨 확인</h2>
    <p style='color:white; font-size:18px;'>회차별 당첨 번호와 나의 번호를 맞춰보세요</p>
  </div>
  """, unsafe_allow_html=True)

  # 반짝이는 애니메이션 CSS 정의
  st.markdown("""
  <style>
  @keyframes blink-effect {
      0% { transform: scale(1); box-shadow: 0 0 5px gold; }
      100% { transform: scale(1.15); box-shadow: 0 0 20px #ffd700, 0 0 10px white; }
  }
  </style>
  """, unsafe_allow_html=True)

  past_results = load_lotto_data()
  if past_results is None:
      st.error("`past_results.csv` 파일을 찾을 수 없거나 데이터가 손상되었습니다. 앱을 재시작하거나 데이터를 확인해주세요.")
      return

  try:
    valid_rounds = past_results["회차_int"].tolist()
    auto_check = False
    
    # QR 코드 스캔 기능 추가
    with st.expander("📷 QR코드로 번호 스캔 (카메라)"):
      if not cv2_available:
        st.warning("⚠️ QR코드 스캔 기능을 사용하려면 'opencv-python' 라이브러리가 필요합니다.\n터미널에 `pip install opencv-python`을 입력하여 설치해주세요.")
      else:
        img_file = st.camera_input("로또 용지의 QR코드를 비춰주세요")
        if img_file:
          try:
            bytes_data = img_file.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            if cv2_img is None:
                st.warning("이미지를 인식할 수 없습니다.")
            else:
                detector = cv2.QRCodeDetector()
                data, bbox, _ = detector.detectAndDecode(cv2_img)
                
                if data and "dhlottery.co.kr" in data:
                   if "v=" in data:
                     q_str = data.split("v=")[1]
                     round_part = q_str[:4]
                     try:
                       scanned_round = int(round_part)
                       if scanned_round in valid_rounds:
                         st.session_state["check_round_select"] = scanned_round
                         auto_check = True
                       else:
                         st.warning(f"스캔된 {scanned_round}회차 데이터가 아직 없습니다.")
                     except:
                       pass
                     
                     # 게임 번호 추출 (알파벳 + 숫자12자리)
                     # QR코드 포맷: 회차(4자리) + 구분자(알파벳) + 번호(12자리) + 구분자 + ...
                     parts = re.split(r'[a-z]+', q_str)
                     raw_games = parts[1:] if len(parts) > 1 else []
                     games = [g for g in raw_games if len(g) >= 12]
                     
                     for i, g in enumerate(games):
                       if i < 5:
                         nums = [int(g[j:j+2]) for j in range(0, 12, 2)]
                         st.session_state[f"check_g{i}"] = ", ".join(map(str, nums))
                     
                     # 나머지 칸 비우기
                     for i in range(min(len(games), 5), 5):
                       st.session_state[f"check_g{i}"] = ""
                       
                     st.success(f"✅ QR코드 인식 성공! {len(games)}게임이 입력되었습니다.")
                     st.balloons()
                elif data:
                   st.warning("로또 복권 QR코드가 아닙니다.")
          except Exception as e:
            st.error(f"QR 스캔 오류: {e}")

    # 텍스트 일괄 붙여넣기 기능 추가
    with st.expander("📋 텍스트로 한 번에 붙여넣기 (여러 게임)"):
      st.info("메모장, 카톡 등에서 복사한 번호를 붙여넣고 '적용하기'를 누르세요.\n(예: 1, 2, 3, 4, 5, 6 또는 1 2 3 4 5 6)")
      paste_text = st.text_area("번호 입력 (여러 줄 가능)", height=100)
      if st.button("번호 적용하기", key="btn_apply_paste"):
        if paste_text:
          # 줄 단위로 분리
          lines = paste_text.strip().split('\n')
          game_count = 0
          for line in lines:
            # 숫자만 추출
            nums = re.findall(r'\d+', line)
            # 6개 이상인 경우만 유효한 게임으로 간주
            if len(nums) >= 6:
              # 1~45 사이의 숫자인지 확인하고 6개만 취함
              valid_nums = []
              for n in nums:
                if 1 <= int(n) <= 45:
                  valid_nums.append(n)
                if len(valid_nums) == 6:
                  break
              
              if len(valid_nums) == 6:
                st.session_state[f"check_g{game_count}"] = ", ".join(valid_nums)
                game_count += 1
                if game_count >= 5:
                  break
          
          # 남은 슬롯 초기화
          for i in range(game_count, 5):
            st.session_state[f"check_g{i}"] = ""
          
          if game_count > 0:
            st.success(f"✅ {game_count}개 게임이 입력되었습니다.")
          else:
            st.warning("유효한 로또 번호를 찾을 수 없습니다.")

    col1, col2 = st.columns([1, 2])
    with col1:
      selected_round = st.selectbox("회차 선택", valid_rounds, key="check_round_select")
    
    target_row = past_results[past_results["회차_int"] == selected_round].iloc[0]
    winning_numbers = [int(target_row[f"번호{i}"]) for i in range(1, 7)]
    winning_numbers.sort()
    
    with col2:
      st.write(f"**제 {selected_round}회 당첨번호**")
      html_nums = generate_lotto_balls_html(winning_numbers, size=30, font_size=14)
      st.markdown(html_nums, unsafe_allow_html=True)
      
    st.markdown("---")
    st.write("### 📝 나의 번호 입력 (쉼표 또는 띄어쓰기로 구분)")
    
    user_inputs = []
    for i in range(5):
      val = st.text_input(f"게임 {i+1}", placeholder="예: 1, 2, 3, 4, 5, 6", key=f"check_g{i}")
      user_inputs.append(val)
    
    if st.button("결과 확인", key="btn_check_win", type="primary") or auto_check:
      st.markdown("### 🕵️‍♂️ 확인 결과")
      for idx, val in enumerate(user_inputs):
        if not val.strip():
          continue
        
        try:
          nums_str = val.replace(",", " ").split()
          my_nums = [int(n) for n in nums_str]
          
          if len(my_nums) != 6:
            st.warning(f"게임 {idx+1}: 6개의 숫자를 입력해주세요.")
          if len(my_nums) < 6:
            st.warning(f"게임 {idx+1}: 6개 이상의 숫자를 입력해주세요.")
            continue
            
          my_nums.sort()
          matched = set(my_nums) & set(winning_numbers)
          match_count = len(matched)
          
          rank_str = "낙첨 😅"
          bg_color = "#f0f0f0"
          border_color = "#ddd"
          
          if match_count == 6:
            rank_str = "🥇 1등 당첨!!"
            bg_color = "#fff5e6"
            border_color = "gold"
            st.balloons() # 1등 축하 효과
          elif match_count == 5:
            rank_str = "🥉 3등 당첨!! (보너스 제외)"
            bg_color = "#e6f7ff"
            border_color = "dodgerblue"
            st.snow() # 3등 축하 효과
          elif match_count == 4:
            rank_str = "💵 4등 당첨"
            bg_color = "#e6ffe6"
            border_color = "limegreen"
          elif match_count == 3:
            rank_str = "🪙 5등 당첨"
            bg_color = "#fff0f0"
            border_color = "salmon"
          
          opacity_map = {n: (1.0 if n in winning_numbers else 0.2) for n in my_nums}
          my_nums_html = generate_lotto_balls_html(my_nums, size=30, font_size=14, opacity_map=opacity_map, highlight_nums=matched)
          
          st.markdown(f"""
          <div style='border:2px solid {border_color}; background-color:{bg_color}; border-radius:10px; padding:10px; margin-bottom:10px; display:flex; align-items:center; justify-content:space-between;'>
            <div style='display:flex; align-items:center;'>
              <span style='font-weight:bold; margin-right:10px; width:60px;'>게임 {idx+1}</span>
              <div>{my_nums_html}</div>
            </div>
            <div style='font-weight:bold; font-size:16px; min-width:100px; text-align:right;'>{rank_str}</div>
          </div>
          """, unsafe_allow_html=True)
            
        except ValueError:
          st.error(f"게임 {idx+1}: 숫자만 입력해주세요.")
  except Exception as e:
    st.error(f"데이터 로드 오류: {e}")

def play_bgm():
    
    """
    은은한 클래식 배경음악을 재생합니다. (Playlist)
    """
    # 유튜브 임베드 Playlist (클래식 명곡 모음)
    # 1. Erik Satie - Gymnopédie No.1 (S-Xm7s9eGxU)
    # 2. Debussy - Clair de Lune (CvFH_6DNRCY)
    # 3. Chopin - Nocturne Op.9 No.2 (9E6b3swbnWg)
    video_ids = "S-Xm7s9eGxU,CvFH_6DNRCY,9E6b3swbnWg"
    youtube_src = f"https://www.youtube.com/embed/S-Xm7s9eGxU?autoplay=1&loop=1&playlist={video_ids}&controls=1"
    
    st.markdown(
        f"""
        <div style="margin-top: 10px; opacity: 0.9;">
            <iframe width="280" height="157" 
                    src="{youtube_src}" 
                    frameborder="0" 
                    allow="autoplay; encrypted-media" 
                    allowfullscreen
                    style="border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            </iframe>
            <div style="font-size: 12px; color: #ccc; margin-top: 4px;">⚠️ 재생 버튼을 누르면 클래식 명곡들이 연속 재생됩니다.</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_header():
    """ Renders the custom top header for the app. """
    # 공통 함수 사용
    next_draw_round, next_date_str = get_next_round_info()

    # '좋아요' 링크 생성
    try:
        current_params = st.query_params.to_dict()
        like_params = current_params.copy()
        like_params['action'] = 'like'
        like_url = f"?{urllib.parse.urlencode(like_params)}"
    except Exception:
        like_url = "?action=like" # Fallback

    # '구독' 링크 생성
    try:
        current_params = st.query_params.to_dict()
        sub_params = current_params.copy()
        sub_params['action'] = 'subscribe'
        subscribe_url = f"?{urllib.parse.urlencode(sub_params)}"
    except Exception:
        subscribe_url = "?action=subscribe"

    sub_label = "🔔 구독중" if st.session_state.get('is_subscribed') else "🔔 구독"
    sub_style = "color: #ffd700; font-weight:bold;" if st.session_state.get('is_subscribed') else "color: white;"

    st.markdown(f"""
        <div class="top-header">
            <div class="header-left">
                <span>🔗 공유</span>
                <a href="{like_url}" target="_self">❤️ 좋아요 {st.session_state.like_count}</a>
                <a href="{subscribe_url}" target="_self" style="{sub_style}">{sub_label}</a>
            </div>
            <div class="header-center">
                ✨ 로또킹 PRO 2.0 (10조합 업데이트) 🚀
            </div>
            <div class="header-right">
                🔜 이번주 추첨: 제 {next_draw_round}회 ({next_date_str})
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.checkbox("🎵 배경음악 (Classic)", value=False, key="bgm_toggle", help="배경음악: 클래식 명곡 모음 (YouTube)"):
        play_bgm()

def render_sidebar():
    """ Renders the content for the left sidebar. """
    st.markdown("""
        <div class="logo">👑 로또킹</div>
        <div class="nav-cards-container">
            <div class="nav-card">
                <a href="/?tab=tab1" target="_self">
                    <span class="emoji">🐉</span>
                    띠별 추천번호
                </a>
            </div>
            <div class="nav-card">
                <a href="/?tab=tab2" target="_self">
                    <span class="emoji">☯️</span>
                    주역 추천번호
                </a>
            </div>
            <div class="nav-card">
                <a href="/?tab=tab3" target="_self">
                    <span class="emoji">📈</span>
                    통계 추천
                </a>
            </div>
            <div class="nav-card">
                <a href="/?tab=tab4" target="_self">
                    <span class="emoji">🧠</span>
                    AI 통합 추천 <span style='background:#ff4b4b; color:white; font-size:10px; padding:2px 5px; border-radius:5px; vertical-align:middle;'>UP</span>
                </a>
            </div>
            <div class="nav-card">
                <a href="/?tab=tab5" target="_self">
                    <span class="emoji">🔎</span>
                    당첨 확인
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)



def render_main_content():
    """ Renders the content for the right main area. """
    show_tab = st.session_state.get('show_tab')

    # 닫기 버튼을 위한 URL 생성
    try:
        current_params = st.query_params.to_dict()
        dismiss_params = current_params.copy()
        dismiss_params['action'] = 'dismiss_update'
        dismiss_url = f"?{urllib.parse.urlencode(dismiss_params)}"
    except Exception:
        dismiss_url = "?action=dismiss_update"

    if show_tab:
        if st.button("🏠 메인 화면으로", key="btn_return_home"):
            st.query_params.clear()
            st.session_state['show_tab'] = None
            st.rerun()
        if show_tab == 'tab1': tab1_content()
        elif show_tab == 'tab2': tab2_content()
        elif show_tab == 'tab3': tab3_content()
        elif show_tab == 'tab4': tab4_content()
        elif show_tab == 'tab5': tab5_content()
    else:
        st.markdown(f"""
        <div style='text-align:center; color:white; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); min-height:60vh; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
            <h2 class="typing-text" style='color:white; margin-bottom: 10px;'>로또킹 AI 분석</h2>
            <p style='color:white; font-size: 18px;'>왼쪽 메뉴에서 원하시는 번호 생성 방식을 선택하세요.</p>
            
            <!-- 업데이트 알림 카드 -->
            {f'''
            <div class="update-card" style="text-align: left;">
                <a href="{dismiss_url}" 
                   onclick="localStorage.setItem('lotto_update_dismissed', 'true');" 
                   style="position: absolute; top: 10px; right: 15px; color: #ff4b4b !important; text-decoration: none; font-size: 28px; font-weight: bold; cursor: pointer; z-index: 9999; line-height: 1;">×</a>
                <h3>🎉 업데이트 소식 (Ver 2.0)</h3>
                <ul>
                    <li>💎 <b>10조합 확장:</b> 당첨 확률 UP! (6개 → 10개)</li>
                    <li>🎱 <b>3D 리얼 볼:</b> 입체감 있는 프리미엄 디자인</li>
                    <li>✨ <b>시각 효과:</b> 당첨 번호 반짝임 & 축하 효과</li>
                    <li>📷 <b>QR 스캔:</b> 지난 회차 자동 결과 확인</li>
                </ul>
            </div>
            ''' if not st.session_state.get('update_dismissed') else ""}
            
            <p class='pointing-finger'>👈</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'update_toast_shown' not in st.session_state:
            st.toast("🚀 로또킹 PRO 2.0 업데이트 완료! 새로운 10조합 기능을 확인하세요!", icon="🎉")
            st.session_state['update_toast_shown'] = True

def get_image_as_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_footer():
    """ Renders the bottom cards and disclaimer using Streamlit's columns for robust layout. """
    thumb_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    # QR 코드 이미지 데이터 가져오기
    qr_image_path = None
    qr_image_name = '1YTkg'
    for ext in ['.png', '.jpg', '.jpeg', '.gif']:
        path = os.path.join(thumb_dir, qr_image_name + ext)
        if os.path.exists(path):
            qr_image_path = path
            break
    qr_image_b64 = get_image_as_base64(qr_image_path) if qr_image_path else None

    # 카드 데이터 준비
    cards_data = [
        {"title": "🎯 통계 분석", "text": "과거 데이터를 분석하여 스노우보드<br>의 순위를 추천합니다."},
        {"title": "🧠 AI 스마트 추천", "text": "AI 수리로<br>수리를 제공합니다."},
        {"title": "🔮 다양한 생성", "text": "밴드별, 주역 등<br>다양한 방식으로 생성합니다."},
    ]
    if qr_image_b64:
        cards_data.append({
            "title": "📱 앱 공유하기",
            "image_html": f'<img src="data:image/png;base64,{qr_image_b64}" width="60" alt="QR Code" style="margin-top:5px;">'
        })

    # CSS Grid를 사용한 반응형 카드 레이아웃 (모바일 2열, PC 자동)
    # HTML 구조를 명확하게 다시 작성하여 태그 닫힘 오류 방지
    cards_html = ""
    for card in cards_data:
        cards_html += f"<div class='bottom-card'><h3>{card['title']}</h3>"
        if 'text' in card:
            cards_html += f"<p>{card['text']}</p>"
        if 'image_html' in card:
            cards_html += card['image_html']
        cards_html += "</div>"
    
    st.markdown(f'<div class="footer-grid">{cards_html}</div>', unsafe_allow_html=True)

    # 공통 하단 경고 메시지
    st.markdown("""
    <div style='margin-top:20px; padding:10px; text-align:center; color:#ccc; font-size:12px; background: rgba(0,0,0,0.5); border-radius:10px;'>
      ⚠️ 로또 번호 예측은 통계적 참고 자료이며 당첨을 보장하지 않습니다. 모든 투자의 책임은 본인에게 있습니다.
    </div>
    """, unsafe_allow_html=True)

# ===== 전체 레이아웃 설정 =====

# 1. 배경 이미지 가져오기
thumb_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
bg_image_b64 = None
# README에 명시된 lottoking1.jpg를 우선적으로 찾도록 수정
image_path = os.path.join(thumb_dir, 'lottoking2.jpeg')
if not os.path.exists(image_path):
    # 대체 이미지 검색
    thumb_candidates = [f for f in os.listdir(thumb_dir) if f.startswith('lottoking') and f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if thumb_candidates:
        image_path = os.path.join(thumb_dir, random.choice(thumb_candidates))
    else:
        image_path = None

if image_path:
    bg_image_b64 = get_image_as_base64(image_path)

# 2. CSS 스타일 주입
st_app_style = ""
card_bg_style = """
        background: #f0f3f6; /* 배경이미지 없을 시 불투명 회색 */
        """
if bg_image_b64:
    st_app_style = f"""
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_image_b64}");
        background-size: cover; /* 전체 화면을 채우도록 수정 */
        background-position: 0% 0%; /* Initial position */
        background-repeat: no-repeat;
        background-attachment: fixed;
        animation: pan-background 60s infinite alternate linear; /* Slow, continuous pan */
    }}
    """
    card_bg_style = """
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(8px);
    """

st.markdown(f"""
<style>
    /* --- 전체 배경 및 기본 설정 --- */
    @keyframes pan-background {{
        0% {{
            background-position: 0% 0%;
        }}
        100% {{
            background-position: 100% 100%;
        }}
    }}

    @keyframes point-left {{
        0%, 100% {{ transform: translateX(0); }}
        50% {{ transform: translateX(-20px); }}
    }}

    .pointing-finger {{
        font-size: 5rem;
        animation: point-left 1.5s infinite ease-in-out;
        display: inline-block;
    }}

    /* --- 타이핑 애니메이션 --- */
    @keyframes typing {{
      from {{ width: 0 }}
      to {{ width: 100% }}
    }}
    @keyframes blink-caret {{
      from, to {{ border-color: transparent }}
      50% {{ border-color: #ffd700; }}
    }}
    .typing-text {{
        display: inline-block;
        overflow: hidden;
        border-right: .1em solid #ffd700;
        white-space: nowrap;
        margin: 0 auto;
        letter-spacing: 0.1em;
        animation:
            typing 2s steps(20, end),
            blink-caret .75s step-end 3 forwards;
        max-width: fit-content;
    }}

    /* --- 업데이트 소식 카드 --- */
    .update-card {{
        background: rgba(0,0,0,0.6);
        padding: 20px;
        border-radius: 15px;
        margin-top: 30px;
        border: 1px solid gold;
        max-width: 500px;
        position: relative;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
    }}
    .update-card h3 {{
        color: gold;
        margin: 0 0 15px 0;
        font-size: 22px;
    }}
    .update-card ul {{
        text-align: left;
        color: #eee;
        font-size: 16px;
        line-height: 1.8;
        list-style-type: none;
        padding: 0;
        margin: 0;
    }}

    {st_app_style}

    /* --- 상단 헤더 --- */
    .top-header {{
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 10px 20px;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    .header-left {{
        font-size: 14px;
        position: relative; /* 클릭 가능하도록 레이어 순서 조정 */
        z-index: 10;
    }}
    .header-center {{
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        font-size: 30px;
        font-weight: bold;
        color: white;
        white-space: nowrap;
    }}
    .header-right {{
        font-size: 14px;
        font-weight: bold;
        color: white;
        position: relative; /* 레이어 순서 조정 */
        z-index: 10;
    }}
    .header-left span, .header-left a {{
        margin-right: 15px;
        cursor: pointer;
        opacity: 0.9;
        transition: opacity 0.2s;
        color: white;
        text-decoration: none;
        display: inline-block; /* transform 적용을 위해 추가 */
    }}
    .header-left span:hover, .header-left a:hover {{ opacity: 1; transform: scale(1.1); }}
    
    /* --- 사이드바 스타일 (네이티브) --- */
    section[data-testid="stSidebar"] {{
        width: 200px !important;
        min-width: 200px !important;
        max-width: 200px !important;
    }}
    section[data-testid="stSidebar"] > div {{
        background-color: rgba(20, 20, 20, 0.85); /* 더 진한 배경으로 가독성 확보 */
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px !important;
        margin-top: 70px !important; /* 상단 여백 확보 */
        margin-bottom: 20px !important;
        margin-left: 10px !important;
        margin-right: 10px !important;
        height: calc(100vh - 90px) !important; /* 높이 조정 */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        padding-top: 10px;
    }}
    /* 사이드바 내부 텍스트 색상 강제 지정 */
    section[data-testid="stSidebar"] .logo, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {{
        color: white !important;
    }}

    /* --- 메인 콘텐츠 카드 스타일 --- */
    /* 메인 영역 전체에 카드 스타일 적용 */
    .main .block-container {{
        {card_bg_style}
        border-radius: 15px;
        padding: 30px !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        color: white;
        max-width: 1200px; /* 폭 넓힘 */
        min-height: 100vh;
    }}

    /* 사이드바 내부 콘텐츠 스타일 */
    .logo {{
        text-align: center;
        font-size: 24px;
        font-weight: 900;
        color: white;
        margin-bottom: 15px;
    }}
    .nav-cards-container {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
    }}
    .nav-card {{
        background: #fc5c7d;
        background: -webkit-linear-gradient(to right, #6a82fb, #fc5c7d);
        background: linear-gradient(to right, #6a82fb, #fc5c7d);
        border-radius: 8px;
        padding: 6px 2px;
        text-align: center;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    .nav-card:last-child {{
        grid-column: span 2;
    }}
    .nav-card:hover {{
        transform: scale(1.05) translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        filter: brightness(1.15);
    }}
    .nav-card a {{
        text-decoration: none;
        color: white;
        font-size: 12px;
        font-weight: 600;
        line-height: 1.2;
    }}
    .nav-card .emoji {{
        font-size: 18px;
        display: block;
        margin-bottom: 2px;
    }}

    /* Streamlit 위젯 스타일 오버라이드 */
    [data-testid="stWidgetLabel"] > label {{
        color: #f0f0f0 !important; /* 라벨 색상 */
    }}
    [data-testid="stRadio"] label span {{
        color: white !important; /* 라디오 버튼 텍스트 */
    }}

    /* --- 하단 기능 카드 --- */
    .footer-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 10px;
        margin-top: 100px;
        perspective: 1000px;
    }}
    .bottom-card {{
        background: rgba(0, 0, 0, 0.6);
        color: white;
        padding: 10px 5px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100%;
        transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
        transform-style: preserve-3d;
    }}
    .bottom-card:hover {{
        transform: translateY(-10px) rotateX(10deg);
        background: linear-gradient(135deg, rgba(106, 130, 251, 0.9), rgba(252, 92, 125, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 15px 30px rgba(0,0,0,0.5);
    }}
    .bottom-card h3 {{
        color: #ffd700;
        font-size: 14px;
        margin: 0 0 8px 0;
        font-weight: bold;
    }}
    .bottom-card p {{
        font-size: 12px;
        color: #ddd;
        margin: 0;
        line-height: 1.4;
    }}
    
    /* 모바일 최적화 */
    @media (max-width: 600px) {{
        .footer-grid {{
            grid-template-columns: 1fr 1fr; /* 모바일에서 2열 배치 */
        }}
        .bottom-card {{
            padding: 10px 5px;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# --- 2단 레이아웃 생성 ---

# 앱 시작 시 최신 데이터 자동 업데이트 (세션당 1회 실행)
if 'data_updated' not in st.session_state:
    # 화면 로딩 중에 스피너 표시
    with st.spinner('최신 로또 당첨 정보를 동기화 중입니다...'):
        success, msg = update_lotto_data_online()
        if success:
             st.toast(msg, icon="✅")
        # 실패하더라도 기존 csv 파일로 구동되므로 에러는 toast로만 알림
    st.session_state['data_updated'] = True

render_header()

# --- 왼쪽 사이드바 구성 ---
with st.sidebar:
    render_sidebar()

# --- 오른쪽 메인 컨텐츠 구성 ---
render_main_content()

# --- 하단 카드 및 QR 코드 구성 ---
render_footer()
