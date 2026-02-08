from flask import Blueprint, request, jsonify, session, render_template
from models import db, User, MemberApplication, Movie, MovieEvent
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# 管理员首页
@admin_bp.route('/dashboard', methods=['GET'])
def admin_dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    
    # 获取统计数据
    pending_applications = MemberApplication.query.filter_by(status='pending').count()
    total_users = User.query.count()
    total_movies = Movie.query.count()
    total_events = MovieEvent.query.count()
    
    return render_template('admin_dashboard.html', 
                         user=user,
                         pending_applications=pending_applications,
                         total_users=total_users,
                         total_movies=total_movies,
                         total_events=total_events)

# 获取所有用户（仅管理员）
@admin_bp.route('/users', methods=['GET'])
def get_users():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    users = User.query.all()
    return jsonify({'users': [{'id': u.id, 'username': u.username, 'role': u.role, 'nickname': u.nickname} for u in users]})

# 设置用户角色（仅管理员）
@admin_bp.route('/set_role', methods=['POST'])
def set_role():
    user_id = session.get('user_id')
    admin = User.query.get(user_id)
    if not admin or admin.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    data = request.json
    uid = data.get('user_id')
    role = data.get('role')
    user = User.query.get(uid)
    if not user:
        return jsonify({'msg': '用户不存在'}), 404
    user.role = role
    db.session.commit()
    return jsonify({'msg': '角色已更新'})

# 入会申请列表
@admin_bp.route('/applications', methods=['GET'])
def get_applications():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    
    applications = MemberApplication.query.order_by(MemberApplication.created_at.desc()).all()
    return render_template('admin_applications.html', applications=applications, user=user)

# 审核入会申请
@admin_bp.route('/approve_application', methods=['POST'])
def approve_application():
    user_id = session.get('user_id')
    admin = User.query.get(user_id)
    if not admin or admin.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    
    data = request.json
    app_id = data.get('application_id')
    action = data.get('action')  # 'approve' or 'reject'
    
    application = MemberApplication.query.get(app_id)
    if not application:
        return jsonify({'msg': '申请不存在'}), 404
    
    if action == 'approve':
        application.status = 'approved'
        # 创建用户账号
        new_user = User(
            username=application.username,
            password='123456',  # 默认密码
            role='member',
            nickname=application.realname,
            join_date=datetime.utcnow()
        )
        db.session.add(new_user)
    else:
        application.status = 'rejected'
    
    db.session.commit()
    return jsonify({'msg': f'申请已{action}'})

# 电影管理
@admin_bp.route('/movies', methods=['GET'])
def manage_movies():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    return render_template('admin_movies.html', movies=movies, user=user)

# 添加电影
@admin_bp.route('/add_movie', methods=['POST'])
def add_movie():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    data = request.form
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

# 活动管理
@admin_bp.route('/events', methods=['GET'])
def manage_events():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    
    events = MovieEvent.query.order_by(MovieEvent.event_date.desc()).all()
    movies = Movie.query.all()
    return render_template('admin_events.html', events=events, movies=movies, user=user)

# 添加活动
@admin_bp.route('/add_event', methods=['POST'])
def add_event():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    
    data = request.json
    event = MovieEvent(
        title=data.get('title'),
        description=data.get('description'),
        movie_id=data.get('movie_id'),
        event_type=data.get('event_type'),
        event_date=datetime.fromisoformat(data.get('event_date')),
        location=data.get('location'),
        max_participants=data.get('max_participants')
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'msg': '活动添加成功', 'id': event.id})

# 会员管理页面
@admin_bp.route('/members', methods=['GET'])
def manage_members():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'msg': '无权限'}), 403
    
    # 获取所有会员，按加入时间排序
    members = User.query.filter(User.role.in_(['member', 'admin'])).order_by(User.join_date.desc()).all()
    
    # 计算统计数据
    total_members = len(members)
    admin_count = len([m for m in members if m.role == 'admin'])
    member_count = len([m for m in members if m.role == 'member'])
    
    return render_template('admin_members.html', 
                         members=members, 
                         user=user,
                         total_members=total_members,
                         admin_count=admin_count,
                         member_count=member_count) 