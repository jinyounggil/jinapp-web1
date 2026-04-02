import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
import os

def update_lotto_data():
    print("🔄 로또 데이터 업데이트 시작...")
    url = "https://www.dhlottery.co.kr/common.do?method=allWinExel&gubun=byWin"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.dhlottery.co.kr/gameResult.do?method=byWin',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }
    
    try:
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        # 인코딩 및 파싱
        html_text = response.content.decode('cp949', errors='replace')
        soup = BeautifulSoup(html_text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return False, "데이터 테이블을 찾을 수 없습니다."

        dfs = pd.read_html(StringIO(str(table)), header=1)
        if not dfs:
            return False, "데이터 변환에 실패했습니다."
            
        df_new = dfs[0]
        
        # 필요한 열만 선택 및 전처리
        win_num_cols = [col for col in df_new.columns if str(col).startswith('당첨번호')]
        required_cols = ['회차'] + win_num_cols
        df_new = df_new[required_cols].copy()
        df_new.columns = ["회차", "번호1", "번호2", "번호3", "번호4", "번호5", "번호6"]
        
        df_new = df_new.dropna(subset=['회차'])
        df_new = df_new[pd.to_numeric(df_new['회차'], errors='coerce').notna()]
        df_new['회차'] = df_new['회차'].astype(int)
        
        latest_new_round = df_new['회차'].max()
        print(f"📡 서버 최신 회차: {latest_new_round}회")

    except Exception as e:
        return False, f"데이터 처리 중 오류 발생: {e}"

    # 기존 파일 확인
    file_path = "past_results.csv"
    latest_old_round = 0
    if os.path.exists(file_path):
        try:
            df_old = pd.read_csv(file_path, header=None, encoding='utf-8-sig')
            df_old_int = df_old[0].str.replace("회차", "").astype(int)
            latest_old_round = df_old_int.max()
        except Exception:
            latest_old_round = 0
    
    print(f"📂 로컬 저장 회차: {latest_old_round}회")

    if latest_new_round <= latest_old_round:
        return True, f"이미 최신 상태입니다. ({latest_old_round}회)"

    # 저장 로직
    df_new['회차'] = df_new['회차'].astype(str) + "회차"
    df_to_save = df_new.sort_values(by='회차', key=lambda x: x.str.replace('회차','').astype(int), ascending=True)
    
    try:
        df_to_save.to_csv(file_path, index=False, header=False, encoding='utf-8-sig')
        return True, f"{latest_new_round}회차 업데이트 완료!"
    except Exception as e:
        return False, f"파일 저장 실패: {e}"

if __name__ == "__main__":
    update_lotto_data()