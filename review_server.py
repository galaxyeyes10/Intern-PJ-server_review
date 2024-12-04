from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from model import ReviewTable, UserTable, StoreTable
from db import session
from fastapi.middleware.cors import CORSMiddleware
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


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

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
if __name__ == "__review__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
