from flask import Blueprint, render_template, request, redirect, session, flash, jsonify
from models import db, Movie, MovieReview, MovieEvent, EventRegistration, User
from datetime import datetime

movie_bp = Blueprint('movie', __name__)

# 电影列表与添加
@movie_bp.route('/movies', methods=['GET', 'POST'])
def movie_list():
    if request.method == 'POST':
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            flash('无权限')
            return redirect('/movie/movies')
        title = request.form.get('title')
        director = request.form.get('director')
        genre = request.form.get('genre')
        release_year = request.form.get('release_year')
        if title:
            movie = Movie(title=title, director=director, genre=genre, release_year=release_year)
            db.session.add(movie)
            db.session.commit()
            flash('添加电影成功！')
        return redirect('/movie/movies')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    movies = Movie.query.paginate(page=page, per_page=per_page, error_out=False)
    user = None
    if session.get('user_id'):
        user = User.query.get(session.get('user_id'))
    return render_template('movies.html', movies=movies, user=user)

# 管理员仪表板API：添加电影
@movie_bp.route('/api/add_movie', methods=['POST'])
def api_add_movie():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    data = request.json or request.form
    movie = Movie(
        title=data.get('title'),
        original_title=data.get('original_title'),
        director=data.get('director'),
        actors=data.get('actors'),
        genre=data.get('genre'),
        release_year=data.get('release_year'),
        country=data.get('country'),
        duration=data.get('duration'),
        rating=data.get('rating', 0.0),
        poster_url=data.get('poster_url'),
        description=data.get('description'),
        trailer_url=data.get('trailer_url')
    )
    db.session.add(movie)
    db.session.commit()
    return jsonify({'msg': '电影添加成功', 'id': movie.id})

# 删除电影（仅管理员）
@movie_bp.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        flash('无权限')
        return redirect('/movie/movies')
    movie = Movie.query.get(movie_id)
    if movie:
        db.session.delete(movie)
        db.session.commit()
        flash('删除电影成功！')
    return redirect('/movie/movies')

# 电影详情与评论
@movie_bp.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    reviews = MovieReview.query.filter_by(movie_id=movie_id).order_by(MovieReview.created_at.desc()).all()
    user = None
    if session.get('user_id'):
        user = User.query.get(session.get('user_id'))
    if request.method == 'POST':
        if not user:
            flash('请先登录')
            return redirect('/login')
        rating = request.form.get('rating', type=int)
        review_text = request.form.get('review_text')
        if not rating or not review_text:
            flash('请填写完整的评论信息')
            return redirect(f'/movie/movie/{movie_id}')
        existing_review = MovieReview.query.filter_by(user_id=user.id, movie_id=movie_id).first()
        if existing_review:
            flash('您已经评论过这部电影了')
            return redirect(f'/movie/movie/{movie_id}')
        review = MovieReview(user_id=user.id, movie_id=movie_id, rating=rating, review_text=review_text)
        db.session.add(review)
        all_reviews = MovieReview.query.filter_by(movie_id=movie_id).all()
        if all_reviews:
            avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
            movie.rating = round(avg_rating, 1)
        db.session.commit()
        flash('评论提交成功！')
        return redirect(f'/movie/movie/{movie_id}')
    return render_template('movie_detail.html', movie=movie, reviews=reviews, user=user)

# 活动列表与添加
@movie_bp.route('/events', methods=['GET', 'POST'])
def event_list():
    if request.method == 'POST':
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            flash('无权限')
            return redirect('/movie/events')
        title = request.form.get('title')
        event_date_str = request.form.get('event_date')
        location = request.form.get('location')
        event_date = None
        if event_date_str:
            try:
                event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
            except Exception:
                event_date = None
        if title:
            event = MovieEvent(title=title, event_date=event_date, location=location)
            db.session.add(event)
            db.session.commit()
            flash('添加活动成功！')
        return redirect('/movie/events')
    events = MovieEvent.query.filter_by(status='upcoming').order_by(MovieEvent.event_date).all()
    user = None
    if session.get('user_id'):
        user = User.query.get(session.get('user_id'))
    return render_template('events.html', events=events, user=user)

# 管理员仪表板API：添加活动
@movie_bp.route('/api/add_event', methods=['POST'])
def api_add_event():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    data = request.json or request.form
    event = MovieEvent(
        title=data.get('title'),
        description=data.get('description'),
        movie_id=data.get('movie_id'),
        event_type=data.get('event_type'),
        event_date=datetime.fromisoformat(data.get('event_date')) if data.get('event_date') else None,
        location=data.get('location'),
        max_participants=data.get('max_participants')
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'msg': '活动添加成功', 'id': event.id})

# 删除活动（仅管理员）
@movie_bp.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        flash('无权限')
        return redirect('/movie/events')
    event = MovieEvent.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        flash('删除活动成功！')
    return redirect('/movie/events')

# 活动详情与报名
@movie_bp.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event_detail(event_id):
    event = MovieEvent.query.get_or_404(event_id)
    movie = Movie.query.get(event.movie_id) if event.movie_id else None
    registrations = EventRegistration.query.filter_by(event_id=event_id).all()
    participants = [User.query.get(r.user_id) for r in registrations]
    user = None
    if session.get('user_id'):
        user = User.query.get(session.get('user_id'))
    if request.method == 'POST':
        if not user:
            flash('请先登录')
            return redirect('/login')
        existing_registration = EventRegistration.query.filter_by(user_id=user.id, event_id=event_id).first()
        if existing_registration:
            flash('您已经报名参加这个活动了')
            return redirect(f'/movie/event/{event_id}')
        if event.current_participants >= event.max_participants:
            flash('活动报名已满')
            return redirect(f'/movie/event/{event_id}')
        registration = EventRegistration(user_id=user.id, event_id=event_id)
        db.session.add(registration)
        event.current_participants += 1
        db.session.commit()
        flash('活动报名成功！')
        return redirect(f'/movie/event/{event_id}')
    return render_template('event_detail.html', event=event, movie=movie, participants=participants, user=user)

# 电影搜索
@movie_bp.route('/search')
def search():
    query = request.args.get('q', '')
    genre = request.args.get('genre', '')
    year = request.args.get('year', '')
    movies = Movie.query
    if query:
        movies = movies.filter(Movie.title.contains(query) | Movie.director.contains(query))
    if genre:
        movies = movies.filter(Movie.genre == genre)
    if year:
        movies = movies.filter(Movie.release_year == int(year))
    movies = movies.order_by(Movie.rating.desc()).all()
    return render_template('search_results.html', movies=movies, query=query, genre=genre, year=year) 