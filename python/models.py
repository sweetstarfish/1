from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(16), default='member')  # sysadmin:系统管理员, admin:一般管理员, member:会员, guest:游客
    nickname = db.Column(db.String(32))
    avatar = db.Column(db.String(128))
    tags = db.Column(db.String(128))
    favorite_genres = db.Column(db.String(256))  # 喜欢的电影类型
    favorite_directors = db.Column(db.String(256))  # 喜欢的导演
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    member_level = db.Column(db.String(16), default='bronze')  # bronze, silver, gold, platinum
    # 其它字段...

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    original_title = db.Column(db.String(128))
    director = db.Column(db.String(64))
    actors = db.Column(db.String(256))
    genre = db.Column(db.String(64))
    release_year = db.Column(db.Integer)
    country = db.Column(db.String(32))
    duration = db.Column(db.Integer)  # 时长（分钟）
    rating = db.Column(db.Float, default=0.0)  # 评分
    poster_url = db.Column(db.String(256))
    description = db.Column(db.Text)
    trailer_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MovieReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    rating = db.Column(db.Integer)  # 1-5星评分
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MovieEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    event_type = db.Column(db.String(32))  # screening, discussion, workshop
    event_date = db.Column(db.DateTime)
    location = db.Column(db.String(128))
    max_participants = db.Column(db.Integer)
    current_participants = db.Column(db.Integer, default=0)
    status = db.Column(db.String(16), default='upcoming')  # upcoming, ongoing, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('movie_event.id'))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(16), default='registered')  # registered, attended, cancelled

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)
    visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    content = db.Column(db.Text)
    category = db.Column(db.String(32))  # announcement, review, industry_news
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(128))
    realname = db.Column(db.String(128))
    contest = db.Column(db.String(64))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_type = db.Column(db.String(32))  # 'news', 'log', 'movie'
    item_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MemberApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    realname = db.Column(db.String(32))
    reason = db.Column(db.String(256))
    favorite_movies = db.Column(db.String(256))  # 喜欢的电影
    movie_experience = db.Column(db.Text)  # 电影相关经历
    status = db.Column(db.String(16), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 