import os
import streamlit as st
import sqlite3

# 데이터베이스 파일 경로 설정 (예: Streamlit Cloud에서는 /tmp 사용)
DB_PATH = os.path.join("/tmp", "reviews.db")

@st.cache_resource
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    # 테이블이 존재하지 않을 경우 새로 생성 (이때는 올바른 스키마로 생성)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu TEXT NOT NULL,
            text TEXT NOT NULL,
            rating INTEGER NOT NULL,
            admin_comment TEXT NOT NULL DEFAULT '',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()

    # 기존 테이블에 저장된 내용은 그대로 유지하면서,
    # 필요한 컬럼이 누락되었을 경우에만 ALTER TABLE 로 컬럼 추가
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(reviews)")
    columns = [col[1] for col in cur.fetchall()]

    # 누락된 경우, 관리자 댓글(admin_comment) 컬럼 추가
    if "admin_comment" not in columns:
        conn.execute("ALTER TABLE reviews ADD COLUMN admin_comment TEXT NOT NULL DEFAULT ''")
        conn.commit()

    # 누락된 경우, 등록일시(created_at) 컬럼 추가  
    if "created_at" not in columns:
        conn.execute("ALTER TABLE reviews ADD COLUMN created_at DATETIME")
        # 기존 행에 대해 created_at 값이 NULL인 경우 현재 시각으로 업데이트
        conn.execute("UPDATE reviews SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        conn.commit()
        
    return conn

conn = init_db()

# 앱 제목 및 설명
st.title("Riley 식당")
st.write("오늘의 메뉴 이름과 리뷰 내용을 남기고 별점을 주세요!")

# ----------------- 고객 리뷰 리스트 (상단) -----------------
st.subheader("고객 리뷰")

cur = conn.cursor()
cur.execute("SELECT id, menu, text, rating, admin_comment, created_at FROM reviews ORDER BY id DESC")
rows = cur.fetchall()

if rows:
    for review in rows:
        review_id, menu, text, rating, admin_comment, created_at = review
        
        st.markdown(f"**오늘의 메뉴:** {menu}")
        st.markdown(f"**리뷰:** {text}")
        st.markdown(f"**별점:** {rating}")
        st.markdown(f"**등록일시:** {created_at}")
        # 관리자 댓글 대신 Riley 댓글로 표시
        if admin_comment != "":
            st.markdown(f"**Riley 댓글:** {admin_comment}")
        
        # --- 관리자 삭제 기능 (토글 형태, 제목: "삭제") ---
        with st.expander("삭제"):
            delete_pass = st.text_input("관리자 비밀번호 (삭제용)", type="password", key=f"delete_password_{review_id}")
            if st.button("리뷰 삭제", key=f"delete_{review_id}"):
                if delete_pass == "0328":
                    conn.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
                    conn.commit()
                    st.success("리뷰가 삭제되었습니다!")
                    if hasattr(st, "experimental_rerun"):
                        st.experimental_rerun()
                    else:
                        st.info("리뷰가 삭제되었습니다. 페이지를 수동으로 새로고침해주세요.")
                else:
                    st.error("비밀번호가 틀렸습니다. 리뷰를 삭제할 수 없습니다.")
        
        # --- 관리자 댓글 기능 (토글 형태, 제목: "Riley 댓글") ---
        with st.expander("Riley 댓글"):
            # 입력 라벨 변경: 관리자 댓글 입력 -> Riley 댓글 입력
            admin_comment_input = st.text_area("Riley 댓글 입력", key=f"admin_comment_input_{review_id}")
            comment_pass = st.text_input("관리자 비밀번호 (댓글 추가용)", type="password", key=f"admin_comment_password_{review_id}")
            if st.button("댓글 추가", key=f"add_comment_{review_id}"):
                if comment_pass == "0328":
                    conn.execute("UPDATE reviews SET admin_comment = ? WHERE id = ?", (admin_comment_input, review_id))
                    conn.commit()
                    st.success("Riley 댓글이 추가되었습니다!")
                    if hasattr(st, "experimental_rerun"):
                        st.experimental_rerun()
                    else:
                        st.info("댓글이 추가되었습니다. 페이지를 수동으로 새로고침해주세요.")
                else:
                    st.error("비밀번호가 틀렸습니다. 댓글을 추가할 수 없습니다.")
        st.markdown("---")
else:
    st.write("아직 제출된 리뷰가 없습니다.")

st.markdown("---")

# ----------------- 리뷰 작성 폼 (하단 배치) -----------------
st.subheader("리뷰 작성")
with st.form("review_form", clear_on_submit=True):
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
            # 새 리뷰 삽입 시, created_at 값을 CURRENT_TIMESTAMP 로 지정
            conn.execute(
                "INSERT INTO reviews (menu, text, rating, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                (menu_name, review_text, rating)
            )
            conn.commit()
            st.success("리뷰가 제출되었습니다!")
            if hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            else:
                st.info("리뷰가 추가되었습니다. 페이지를 수동으로 새로고침해주세요.")
