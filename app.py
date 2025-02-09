import streamlit as st
import sqlite3

# SQLite 데이터베이스 연결 및 테이블 생성 (서버 실행 시 단 한 번 생성)
@st.cache_resource
def init_db():
    # check_same_thread=False 옵션은 멀티스레딩 환경에서도 사용하기 위함입니다.
    conn = sqlite3.connect("reviews.db", check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            rating INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    return conn

conn = init_db()

st.title("리뷰 앱")
st.write("리뷰 내용을 남기고 별점을 주세요!")

# 리뷰 입력 폼
with st.form("review_form", clear_on_submit=True):
    review_text = st.text_area("리뷰 내용 입력", height=150)
    rating = st.slider("별점 선택 (1~5)", 1, 5, 3)
    submitted = st.form_submit_button("리뷰 제출")
    
    if submitted:
        if review_text.strip() == "":
            st.error("리뷰 내용을 입력해주세요!")
        else:
            conn.execute("INSERT INTO reviews (text, rating) VALUES (?, ?)", (review_text, rating))
            conn.commit()
            st.success("리뷰가 제출되었습니다!")
            # 제출 후 페이지를 새로 고침하여 최신 리뷰 목록을 보여줍니다.
            st.experimental_rerun()

st.write("## 제출된 리뷰")

# 데이터베이스에 저장된 리뷰를 id, text, rating 컬럼과 함께 불러옵니다.
cur = conn.cursor()
cur.execute("SELECT id, text, rating FROM reviews ORDER BY id DESC")
rows = cur.fetchall()

if rows:
    for review in rows:
        review_id, text, rating = review
        st.write(f"**리뷰:** {text}")
        st.write(f"**별점:** {rating}")
        # 각 리뷰마다 고유한 키를 가진 삭제 버튼을 생성합니다.
        if st.button("리뷰 삭제", key=f"delete_{review_id}"):
            conn.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
            conn.commit()
            st.success("리뷰가 삭제되었습니다!")
            # 삭제 후 페이지를 새로 고침하여 변경된 리뷰 목록을 반영합니다.
            st.experimental_rerun()
else:
    st.write("아직 제출된 리뷰가 없습니다.")
