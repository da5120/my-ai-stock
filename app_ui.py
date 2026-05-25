import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai

# --- 1. 設定網頁標題與外觀 ---
st.set_page_config(page_title="AI 股票分析助手", layout="centered")
st.title("📈 閒閒的鹹魚股市分析助手")

# --- 2. 設定 API Key ---
# 安全寫法：教程式去 Streamlit 的 Secrets 保險箱裡面拿鑰匙
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])  # ✅ 換成這行
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 3. 建立使用者介面 (輸入框與按鈕) ---
st.write("請輸入你想查詢的台灣股票代號，AI 將為您進行技術面分析。")
user_input = st.text_input("股票代號 (例如：2330, 2317, 2603)：", "2330")

if st.button("🚀 開始分析"):
    if user_input:
        stock_symbol = f"{user_input}.TW"
        
        # 顯示載入中的動畫圈圈
        with st.spinner(f"正在抓取 {stock_symbol} 的數據並請 AI 分析中...請稍候！"):
            try:
                # 抓取數據
                stock = yf.Ticker(stock_symbol)
                df = stock.history(period="3mo")
                
                if df.empty:
                    st.error(f"找不到 {stock_symbol} 的資料，請確認代號是否正確。")
                else:
                    # 計算指標
                    df['20MA'] = df['Close'].rolling(window=20).mean()
                    df['Std_dev'] = df['Close'].rolling(window=20).std()
                    df['Bollinger_Upper'] = df['20MA'] + (df['Std_dev'] * 2)
                    df['Bollinger_Lower'] = df['20MA'] - (df['Std_dev'] * 2)
                    support_level = df['Low'].min()
                    resistance_level = df['High'].max()
                    latest_data = df.iloc[-1]
                    
                    # 在畫面上顯示漂亮的三個數據卡片
                    st.subheader(f"📊 {stock_symbol} 最新數據")
                    # 畫出收盤價的折線圖
                    st.line_chart(df['Close'])
                    col1, col2, col3 = st.columns(3)
                    col1.metric("收盤價", f"{latest_data['Close']:.2f}")
                    col2.metric("20日均線", f"{latest_data['20MA']:.2f}")
                    col3.metric("成交量 (千股)", f"{latest_data['Volume']/1000:.0f}")

                    # 準備給 AI 的提示詞
                    analysis_prompt = f"""
                    你是一位資深的技術分析交易員。請根據以下 {stock_symbol} 的最新技術面數據，判斷現在是否為適合買進的時機，並給出具體的理由與風險提示。

                    * 收盤價：{latest_data['Close']:.2f} 
                    * 20日均線：{latest_data['20MA']:.2f} 
                    * 布林通道上軌：{latest_data['Bollinger_Upper']:.2f} / 下軌：{latest_data['Bollinger_Lower']:.2f}
                    * 近期重要支撐位：{support_level:.2f} / 壓力位：{resistance_level:.2f}
                    """
                    
                    # 呼叫 AI
                    response = model.generate_content(analysis_prompt)
                    
                    # 顯示 AI 的分析結果
                    st.divider() # 畫一條分隔線
                    st.subheader("🤖 AI 分析報告")
                    st.write(response.text)
                    
            except Exception as e:
                st.error(f"發生錯誤：{e}")
    else:
        st.warning("請先輸入股票代號喔！")