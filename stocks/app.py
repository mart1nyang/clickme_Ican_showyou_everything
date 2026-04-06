import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# [페이지 기본 설정]
st.set_page_config(page_title="주식 퀀트 지표 분석기", page_icon="📈", layout="centered")

st.title("📈 퀀트 투자 지표 자동 평가 시스템")
st.markdown("종목의 **CAGR(연환산 수익률)**, **Sharpe Ratio(샤프 지수)**, **MDD(최대 낙폭)**를 계산하고 종합 점수를 산출합니다.")

# [입력 폼 생성]
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        # 한국 주식은 '.KS'(코스피)나 '.KQ'(코스닥)를 붙이고, 미국 주식은 그대로 입력(예: AAPL)
        ticker = st.text_input("종목 코드 (예: 005930.KS, AAPL)", value="005930.KS")
    with col2:
        start_date = st.date_input("분석 시작일", value=pd.to_datetime("2023-01-01"))
    
    submit_button = st.form_submit_button(label="분석 시작")

# [분석 실행]
if submit_button:
    with st.spinner(f"'{ticker}' 데이터를 불러오고 분석하는 중입니다..."):
        try:
            # 1. 데이터 다운로드
            df = yf.download(ticker, start=start_date, progress=False)
            
            if df.empty:
                st.error("데이터를 불러오지 못했습니다. 종목 코드나 날짜를 확인해 주세요.")
            else:
                price = df['Close'].squeeze()

                # 2. 지표 계산 (수정된 완벽한 로직 적용)
                returns = price.pct_change().dropna()
                cum_return = (1 + returns).cumprod()
                years = len(returns) / 252
                
                # CAGR 계산
                cagr = cum_return.iloc[-1] ** (1/years) - 1
                
                # 샤프 지수 계산
                risk_free = 0.03
                volatility = returns.std() * np.sqrt(252)
                sharpe = (cagr - risk_free) / volatility

                # MDD 계산
                cum_max = cum_return.cummax()
                drawdown = (cum_return - cum_max) / cum_max
                mdd = drawdown.min()

                # 3. 점수 계산 시스템
                score = 0
                
                if cagr > 0.20: score += 40
                elif cagr > 0.10: score += 30
                elif cagr > 0.05: score += 20
                else: score += 10

                if sharpe > 2.0: score += 40
                elif sharpe > 1.0: score += 30
                elif sharpe > 0.5: score += 20
                else: score += 10

                if mdd > -0.10: score += 20
                elif mdd > -0.20: score += 15
                elif mdd > -0.30: score += 10
                else: score += 5

                # 등급 산출
                if score >= 90: grade = "최상 🏆"
                elif score >= 75: grade = "우수 🥇"
                elif score >= 60: grade = "보통 🥈"
                else: grade = "위험 🚨"

                # ----------------------------------------
                # [결과 화면 출력 (UI)]
                # ----------------------------------------
                st.divider() # 구분선
                st.subheader(f"📊 {ticker} 분석 결과")
                
                # 핵심 지표를 3칸으로 나누어 예쁘게 표시
                m1, m2, m3 = st.columns(3)
                m1.metric("CAGR (연평균 성장률)", f"{cagr * 100:.2f}%")
                m2.metric("Sharpe Ratio (위험대비 수익)", f"{sharpe:.2f}")
                m3.metric("MDD (최대 낙폭)", f"{mdd * 100:.2f}%")
                
                st.divider()
                
                # 최종 점수와 등급 강조
                col_score, col_grade = st.columns(2)
                with col_score:
                    st.info(f"### 총점: {score} / 100")
                with col_grade:
                    if score >= 75:
                        st.success(f"### 등급: {grade}")
                    elif score >= 60:
                        st.warning(f"### 등급: {grade}")
                    else:
                        st.error(f"### 등급: {grade}")
                
                st.write("") # 여백
                
                # 누적 수익률 차트 추가 (보너스!)
                st.write("📈 **누적 수익률 추이 (기준: 1.0)**")
                st.line_chart(cum_return)

        except Exception as e:
            st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")