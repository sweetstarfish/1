from flask import Flask, render_template, session, redirect, request, flash
from models import db, User, Friendship, Log, MemberApplication, News, Collection, Movie, MovieEvent, Photo
from views_user import user_bp
from views_admin import admin_bp
from views_public import public_bp
from views_movie import movie_bp
import os

# 创建Flask应用实例
app = Flask(__name__, instance_path=None)

# --- 应用配置 ---
# 数据库文件路径 - 明确指定使用主目录的数据库文件
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'association.db')
# 禁止追踪对象修改，提高性能
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 用于session加密的密钥
app.config['SECRET_KEY'] = 'your_secret_key'
# 文件上传目录
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')


# --- 数据库初始化 ---
# 在应用上下文中初始化数据库并创建所有表
with app.app_context():
    db.init_app(app)
    db.create_all()

# --- 蓝图注册 ---
# 将用户、管理员、公共、电影等视图蓝图注册到应用中，实现模块化
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(public_bp, url_prefix='/public')
app.register_blueprint(movie_bp, url_prefix='/movie')


# --- 核心路由 ---
@app.route('/')
def index():
    """首页"""
    return render_template('index.html', session=session)

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """会员空间"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    user = User.query.get(user_id)
    friends = [User.query.get(f.friend_id) for f in Friendship.query.filter_by(user_id=user_id).all()]
    logs = Log.query.filter_by(user_id=user_id).order_by(Log.created_at.desc()).all()
    photos = Photo.query.filter_by(user_id=user_id).order_by(Photo.uploaded_at.desc()).all()
    return render_template('dashboard.html', user=user, friends=friends, logs=logs, photos=photos)

@app.route('/friend_space/<int:friend_id>')
def friend_space(friend_id):
    """好友空间"""
    friend = User.query.get(friend_id)
    logs = Log.query.filter_by(user_id=friend_id, visible=True).order_by(Log.created_at.desc()).all()
    return render_template('friend_space.html', friend=friend, logs=logs)

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    """会员申请"""
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        realname = request.form.get('realname')
        reason = request.form.get('reason')
        favorite_movies = request.form.get('favorite_movies')
        movie_experience = request.form.get('movie_experience')
        if not username or not reason:
            msg = '请填写完整信息'
        else:
            app_obj = MemberApplication(
                username=username, 
                realname=realname, 
                reason=reason,
                favorite_movies=favorite_movies,
                movie_experience=movie_experience
            )
            db.session.add(app_obj)
            db.session.commit()
            msg = '申请已提交，等待审核'
    return render_template('apply.html', msg=msg)

@app.route('/admin/apply_admin', methods=['GET'])
def apply_admin():
    """管理员审核页面"""
    apps = MemberApplication.query.order_by(MemberApplication.created_at.desc()).all()
    return render_template('apply_admin.html', apps=apps)

@app.route('/admin/apply_approve', methods=['POST'])
def apply_approve():
    """处理会员申请（通过/拒绝）"""
    app_id = request.form.get('id')
    action = request.form.get('action')
    app_obj = MemberApplication.query.get(app_id)
    if app_obj and app_obj.status == 'pending':
        if action == 'approve':
            app_obj.status = 'approved'
        elif action == 'reject':
            app_obj.status = 'rejected'
        db.session.commit()
    return redirect('/admin/apply_admin')

# --- 应用启动 ---
if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True) 