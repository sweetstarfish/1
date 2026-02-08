from flask import Blueprint, jsonify, request, render_template
from models import db, News

public_bp = Blueprint('public', __name__)

# 协会简介
@public_bp.route('/about', methods=['GET'])
def about():
    return jsonify({'title': '某大学某协会', 'intro': '这里是协会简介内容，可自定义。'})

# 协会活动（示例）
@public_bp.route('/activities', methods=['GET'])
def activities():
    return jsonify({'activities': [
        {'title': '迎新晚会', 'date': '2024-09-01', 'desc': '欢迎新同学加入协会！'},
        {'title': '学术讲座', 'date': '2024-10-15', 'desc': '邀请知名学者分享前沿知识。'}
    ]})

# 资讯/新闻分页（API）
@public_bp.route('/news', methods=['GET'])
def news():
    if request.accept_mimetypes.accept_html:
        # 浏览器访问时渲染页面
        try:
            # 尝试查询新闻，如果失败则返回空列表
            news_list = News.query.order_by(News.created_at.desc()).limit(20).all()
        except Exception as e:
            print(f"查询新闻时出错: {e}")
            news_list = []
        return render_template('news.html', news=news_list)
    # API返回JSON
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    try:
        pagination = News.query.order_by(News.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        news_list = [{'id': n.id, 'title': n.title, 'content': n.content, 'created_at': n.created_at} for n in pagination.items]
    except Exception as e:
        print(f"API查询新闻时出错: {e}")
        news_list = []
        pagination = None
    return jsonify({'news': news_list, 'total': pagination.total if pagination else 0, 'page': page, 'per_page': per_page})

# 新闻详情
@public_bp.route('/news/<int:news_id>', methods=['GET'])
def news_detail(news_id):
    try:
        n = News.query.get(news_id)
        if not n:
            return jsonify({'msg': '未找到新闻'}), 404
        return jsonify({'id': n.id, 'title': n.title, 'content': n.content, 'created_at': n.created_at})
    except Exception as e:
        print(f"查询新闻详情时出错: {e}")
        return jsonify({'msg': '查询失败'}), 500 