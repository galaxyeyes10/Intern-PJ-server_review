from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from model import ReviewTable, UserTable, StoreTable
from db import session
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
import uvicorn

review = FastAPI()

review.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

review.add_middleware(SessionMiddleware, secret_key="your-secret-key")

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

#로그인 상태 확인, 로그인 중인 유저 아이디 반환
@review.get("/check_login/")
async def check_login(request: Request):
    # 세션에서 사용자 정보 확인
    if "user_id" not in request.session:
        return False
    
    return {"user_id": f"{request.session['user_id']}"}

#유저 아이디로 모든 리뷰 아이디 반환
@review.get("/review_ids/{user_id}")
async def get_review_ids(user_id: str, db: Session = Depends(get_db)):
    review_ids = db.query(ReviewTable.review_id).filter(ReviewTable.user_id == user_id).all()
    
    return {"review_ids": [review_id[0] for review_id in review_ids]}

#유저 이름 반환
@review.get("/username/{user_id}")
async def read_username(user_id: str, db: Session = Depends(get_db)):
    reviewer = db.query(ReviewTable).join(UserTable).filter(ReviewTable.user_id == user_id).first()
    
    return reviewer.user.username

#리뷰 갯수 반환
@review.get("/review_counting/{user_id}")
async def read_review_count(user_id: str, db: Session = Depends(get_db)):
    reviews = db.query(ReviewTable).filter(ReviewTable.user_id == user_id).all()
    return len(reviews)

#유저의 평균 별점 반환
@review.get("/average_rating/{user_id}")
async def average_rating(user_id: str, db: Session = Depends(get_db)):
    reviews = db.query(ReviewTable).filter(ReviewTable.user_id == user_id).all()
    ratings = [row.rating for row in reviews]
    average = sum(ratings) / len(ratings)
    return round(average, 1)

#리뷰 제목, 별점, 내용 딕셔너리 반환
@review.get("/review/{user_id}")
async def read_review_history(user_id: str, db: Session = Depends(get_db)):
    reviews = db.query(ReviewTable.title,
                        ReviewTable.rating,
                        ReviewTable.content).join(StoreTable, ReviewTable.store_id == StoreTable.store_id).filter(ReviewTable.user_id == user_id).all()
    
    review = [
        {
            "title": review.title,
            "rating": "{:.1f}".format(review.rating),
            "content": review.content
        }
        for review in reviews
    ]

    return review

#삭제 버튼 처리
@review.delete("/delete/{review_id}")
async def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(ReviewTable).filter(ReviewTable.review_id == review_id).first()
    
    db.delete(review)
    db.commit()

if __name__ == "__review__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
