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
            menu TEXT NOT NULL,
            text TEXT NOT NULL,
            rating INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    return conn

conn = init_db()

st.title("리뷰 앱")
st.write("오늘의 메뉴 이름과 리뷰 내용을 남기고 별점을 주세요!")

# 리뷰 입력 폼
with st.form("review_form", clear_on_submit=True):
    # "오늘의 메뉴 이름" 입력란 추가
    menu_name = st.text_input("오늘의 메뉴 이름을 입력하세요")
    review_text = st.text_area("리뷰 내용 입력", height=150)
    rating = st.slider("별점 선택 (1~5)", 1, 5, 3)
    submitted = st.form_submit_button("리뷰 제출")
    
    if submitted:
        if menu_name.strip() == "":
            st.error("오늘의 메뉴 이름을 입력해주세요!")
        elif review_text.strip() == "":
            st.error("리뷰 내용을 입력해주세요!")
        else:
            # 메뉴 이름, 리뷰, 별점을 데이터베이스에 저장
            conn.execute(
                "INSERT INTO reviews (menu, text, rating) VALUES (?, ?, ?)",
                (menu_name, review_text, rating)
            )
            conn.commit()
            st.success("리뷰가 제출되었습니다!")
            # experimental_rerun 사용 여부 체크
            if hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            else:
                st.info("리뷰가 추가되었습니다. 페이지를 수동으로 새로고침해주세요.")

st.write("## 제출된 리뷰")

# 데이터베이스에 저장된 리뷰 출력
cur = conn.cursor()
cur.execute("SELECT id, menu, text, rating FROM reviews ORDER BY id DESC")
rows = cur.fetchall()

if rows:
    for review in rows:
        review_id, menu, text, rating = review
        st.markdown(f"**오늘의 메뉴:** {menu}")
        st.markdown(f"**리뷰:** {text}")
        st.markdown(f"**별점:** {rating}")
        # 각 리뷰마다 고유한 키를 가진 삭제 버튼 생성
        if st.button("리뷰 삭제", key=f"delete_{review_id}"):
            conn.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
            conn.commit()
            st.success("리뷰가 삭제되었습니다!")
            if hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            else:
                st.info("리뷰가 삭제되었습니다. 페이지를 수동으로 새로고침해주세요.")
        st.markdown("---")
else:
    st.write("아직 제출된 리뷰가 없습니다.")
