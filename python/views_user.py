from flask import Blueprint, request, jsonify, session, redirect, flash
from models import db, User, Friendship, Log, Photo, News, Collection
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os

user_bp = Blueprint('user', __name__)

# 用户注册
@user_bp.route('/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.json
    else:
        data = request.form
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        if request.is_json:
            return jsonify({'msg': '用户名和密码不能为空'}), 400
        else:
            flash('用户名和密码不能为空')
            return redirect('/register')
    
    if User.query.filter_by(username=username).first():
        if not request.is_json:
            return redirect('/register?userexists=1')
        return jsonify({'msg': '用户名已存在'}), 400
    
    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    
    if not request.is_json:
        flash('注册成功！请登录')
        return redirect('/login')
    return jsonify({'msg': '注册成功'})

# 用户登录
@user_bp.route('/login', methods=['POST'])
def login():
    if request.is_json:
        data = request.json
    else:
        data = request.form
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        if request.is_json:
            return jsonify({'msg': '用户名和密码不能为空'}), 400
        else:
            flash('用户名和密码不能为空')
            return redirect('/login')
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        if request.is_json:
            return jsonify({'msg': '用户名或密码错误'}), 400
        else:
            flash('用户名或密码错误')
            return redirect('/login')
    
    session['user_id'] = user.id
    session['username'] = user.username
    
    if not request.is_json:
        flash(f'欢迎回来，{user.nickname or user.username}！')
        # 根据用户角色跳转到不同页面
        if user.role == 'admin':
            return redirect('/admin/dashboard')
        else:
            return redirect('/dashboard')
    return jsonify({'msg': '登录成功', 'user_id': user.id, 'role': user.role})

# 个人资料
@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'msg': '未登录'}), 401
    user = User.query.get(user_id)
    if request.method == 'GET':
        return jsonify({'username': user.username, 'nickname': user.nickname, 'avatar': user.avatar, 'tags': user.tags})
    else:
        data = request.json
        user.nickname = data.get('nickname', user.nickname)
        user.tags = data.get('tags', user.tags)
        db.session.commit()
        return jsonify({'msg': '资料已更新'})

# 好友管理
@user_bp.route('/friends', methods=['GET', 'POST', 'DELETE'])
def friends():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'msg': '未登录'}), 401
    if request.method == 'GET':
        fs = Friendship.query.filter_by(user_id=user_id).all()
        friend_list = [User.query.get(f.friend_id).username for f in fs]
        return jsonify({'friends': friend_list})
    elif request.method == 'POST':
        data = request.json
        friend_name = data.get('friend_name')
        friend = User.query.filter_by(username=friend_name).first()
        if not friend:
            return jsonify({'msg': '好友不存在'}), 404
        if Friendship.query.filter_by(user_id=user_id, friend_id=friend.id).first():
            return jsonify({'msg': '已添加为好友'})
        db.session.add(Friendship(user_id=user_id, friend_id=friend.id))
        db.session.commit()
        return jsonify({'msg': '添加好友成功'})
    elif request.method == 'DELETE':
        data = request.json
        friend_name = data.get('friend_name')
        friend = User.query.filter_by(username=friend_name).first()
        if not friend:
            return jsonify({'msg': '好友不存在'}), 404
        fs = Friendship.query.filter_by(user_id=user_id, friend_id=friend.id).first()
        if fs:
            db.session.delete(fs)
            db.session.commit()
            return jsonify({'msg': '删除好友成功'})
        return jsonify({'msg': '未找到好友关系'})

# 日志发布
@user_bp.route('/log', methods=['POST'])
def post_log():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'msg': '未登录'}), 401
    data = request.json
    content = data.get('content')
    visible = data.get('visible', True)
    log = Log(user_id=user_id, content=content, visible=visible)
    db.session.add(log)
    db.session.commit()
    return jsonify({'msg': '日志发布成功'})

# 日志列表
@user_bp.route('/logs', methods=['GET'])
def get_logs():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'msg': '未登录'}), 401
    logs = Log.query.filter_by(user_id=user_id).order_by(Log.created_at.desc()).all()
    return jsonify({'logs': [{'content': l.content, 'visible': l.visible, 'created_at': l.created_at} for l in logs]})

# 资料收藏（示例，实际可扩展）
@user_bp.route('/collect', methods=['POST'])
def collect():
    # 这里只做接口示例，具体实现可根据收藏对象扩展
    return jsonify({'msg': '收藏成功（示例）'})

# 上传会员照片
@user_bp.route('/upload_photo', methods=['POST'])
def upload_photo():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'msg': '未登录'}), 401
    file = request.files.get('file')
    contest = request.form.get('contest', 'default')
    if not file:
        return jsonify({'msg': '未选择文件'}), 400
    ext = os.path.splitext(file.filename)[-1]
    rand_name = str(uuid.uuid4()) + ext
    save_dir = os.path.join('static', 'uploads', contest)
    os.makedirs(save_dir, exist_ok=True)
    file.save(os.path.join(save_dir, rand_name))
    photo = Photo(user_id=user_id, filename=rand_name, realname=file.filename, contest=contest)
    db.session.add(photo)
    db.session.commit()
    return jsonify({'msg': '上传成功', 'filename': rand_name})

# 访问好友空间
@user_bp.route('/friend_space/<int:friend_id>', methods=['GET'])
def friend_space(friend_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'msg': '未登录'}), 401
    friend = User.query.get(friend_id)
    if not friend:
        return jsonify({'msg': '好友不存在'}), 404
    logs = Log.query.filter_by(user_id=friend_id, visible=True).order_by(Log.created_at.desc()).all()
    return jsonify({
        'friend': {
            'id': friend.id,
            'username': friend.username,
            'nickname': friend.nickname,
            'avatar': friend.avatar,
            'tags': friend.tags
        },
        'logs': [{'content': l.content, 'created_at': l.created_at} for l in logs]
    })

# 退出登录
@user_bp.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('已成功退出登录')
    return redirect('/')

# 获取用户列表（用于好友搜索）
@user_bp.route('/users', methods=['GET'])
def get_users():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'msg': '未登录'}), 401
    
    # 获取所有用户，排除自己
    users = User.query.filter(User.id != user_id).all()
    user_list = []
    
    for user in users:
        # 检查是否已经是好友
        is_friend = Friendship.query.filter_by(user_id=user_id, friend_id=user.id).first() is not None
        
        user_list.append({
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname or user.username,
            'tags': user.tags,
            'is_friend': is_friend
        })
    
    return jsonify({'users': user_list})

# --- Form-based Endpoints (for Templates) ---

@user_bp.route('/profile/update', methods=['POST'])
def update_profile_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    user = User.query.get(user_id)
    user.nickname = request.form.get('nickname')
    user.tags = request.form.get('tags')
    db.session.commit()
    flash('个人资料已更新')
    return redirect('/dashboard')

@user_bp.route('/friend/add', methods=['POST'])
def add_friend_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    friend_name = request.form.get('friend_name')
    friend = User.query.filter_by(username=friend_name).first()

    if not friend:
        flash('用户不存在')
        return redirect('/dashboard')
    
    if friend.id == user_id:
        flash('不能添加自己为好友')
        return redirect('/dashboard')
    
    existing_friendship = Friendship.query.filter_by(user_id=user_id, friend_id=friend.id).first()
    if existing_friendship:
        flash('已经是好友了')
        return redirect('/dashboard')
    
    friendship = Friendship(user_id=user_id, friend_id=friend.id)
    db.session.add(friendship)
    db.session.commit()
    flash(f'已添加 {friend.nickname or friend.username} 为好友')
    return redirect('/dashboard')

@user_bp.route('/friend/remove', methods=['POST'])
def remove_friend_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    friend_id = request.form.get('friend_id')
    friendship = Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    
    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        flash('已删除好友')
    else:
        flash('未找到好友关系')
    
    return redirect('/dashboard')

@user_bp.route('/log/post_form', methods=['POST'])
def post_log_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    content = request.form.get('content')
    if not content:
        flash('日志内容不能为空')
        return redirect('/dashboard')
    
        log = Log(user_id=user_id, content=content, visible=True)
        db.session.add(log)
        db.session.commit()
    flash('日志发布成功')
    return redirect('/dashboard')

@user_bp.route('/collect/<item_type>/<int:item_id>', methods=['POST'])
def collect_item(item_type, item_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'msg': '未登录'}), 401
    
    # 检查是否已收藏
    existing = Collection.query.filter_by(user_id=user_id, item_type=item_type, item_id=item_id).first()
    if existing:
        return jsonify({'msg': '已收藏'})
    
        collection = Collection(user_id=user_id, item_type=item_type, item_id=item_id)
        db.session.add(collection)
        db.session.commit()
    return jsonify({'msg': '收藏成功'})

# ... existing code ... 