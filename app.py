from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
import bleach
import os
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///topics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a random secret key
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define maximum number of topics and articles
MAX_TOPICS = 10
MAX_ARTICLES_PER_TOPIC = 25

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    sort_order = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    articles = db.relationship('Article', backref='topic', lazy=True)

    def __repr__(self):
        return f'<Topic {self.name}>'

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Article {self.title}>'

@app.route('/')
def index():
    return render_template('index.html', active_page='home')

@app.route('/knowledge-base')
def knowledge_base():
    topics = Topic.query.options(joinedload(Topic.articles)).order_by(Topic.sort_order).all()
    return render_template('knowledge_base.html', active_page='knowledge_base', topics=topics)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            topic_name = request.form.get('topic_name').strip()
            if topic_name and len(topic_name) <= 25:
                existing_topic = Topic.query.filter(func.lower(Topic.name) == func.lower(topic_name)).first()
                if existing_topic:
                    flash('Topic already exists.', 'error')
                elif Topic.query.count() >= MAX_TOPICS:
                    flash(f'Maximum number of topics ({MAX_TOPICS}) reached.', 'error')
                else:
                    max_sort_order = db.session.query(func.max(Topic.sort_order)).scalar() or 0
                    new_topic = Topic(name=topic_name, sort_order=max_sort_order + 1)
                    db.session.add(new_topic)
                    db.session.commit()
                    flash('Topic created successfully.', 'success')
            else:
                flash('Invalid topic name. Must be between 1 and 25 characters.', 'error')
        elif action == 'edit':
            topic_id = request.form.get('topic_id')
            new_name = request.form.get('new_name').strip()
            if new_name and len(new_name) <= 25:
                topic = Topic.query.get(topic_id)
                if topic:
                    existing_topic = Topic.query.filter(func.lower(Topic.name) == func.lower(new_name)).first()
                    if existing_topic and existing_topic.id != int(topic_id):
                        flash('Topic name already exists.', 'error')
                    else:
                        topic.name = new_name
                        db.session.commit()
                        flash('Topic updated successfully.', 'success')
                else:
                    flash('Topic not found.', 'error')
            else:
                flash('Invalid topic name. Must be between 1 and 25 characters.', 'error')
        elif action == 'delete':
            topic_id = request.form.get('topic_id')
            topic = Topic.query.get(topic_id)
            if topic:
                # Check if the topic has articles
                if topic.articles:
                    # Check if the user typed "delete" (case-insensitive)
                    confirmation = request.form.get('confirmation', '').strip().lower()
                    if confirmation != 'delete':
                        return jsonify({'status': 'error', 'message': 'You must type "delete" to confirm deletion of a topic with articles.'})
                # Delete all articles associated with the topic
                for article in topic.articles:
                    db.session.delete(article)
                db.session.delete(topic)
                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Topic and associated articles deleted successfully.'})
            else:
                return jsonify({'status': 'error', 'message': 'Topic not found.'})
        return redirect(url_for('admin'))

    topics = Topic.query.order_by(Topic.sort_order).all()
    topic_count = Topic.query.count()
    return render_template('admin.html', active_page='admin', topics=topics, topic_count=topic_count, max_topics=MAX_TOPICS, max_articles=MAX_ARTICLES_PER_TOPIC)

@app.route('/admin/topic/<int:topic_id>')
def admin_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    articles = Article.query.filter_by(topic_id=topic_id).order_by(Article.sort_order).all()
    return render_template('admin_topic.html', active_page='admin', topic=topic, articles=articles, max_articles=MAX_ARTICLES_PER_TOPIC)

@app.route('/admin/topic/<int:topic_id>/article/new', methods=['GET', 'POST'])
def new_article(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if request.method == 'POST':
        if Article.query.filter_by(topic_id=topic_id).count() >= MAX_ARTICLES_PER_TOPIC:
            flash(f'Maximum number of articles ({MAX_ARTICLES_PER_TOPIC}) reached for this topic.', 'error')
        else:
            title = request.form.get('title')
            content = request.form.get('content')
            # Use a more permissive bleach cleaning
            content = bleach.clean(content, tags=['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'img', 'h1', 'h2', 'h3', 'blockquote', 'pre', 'code'],
                                   attributes={'a': ['href', 'target'], 'img': ['src', 'alt']})
            max_sort_order = db.session.query(func.max(Article.sort_order)).filter_by(topic_id=topic_id).scalar() or 0
            new_article = Article(title=title, content=content, topic_id=topic_id, sort_order=max_sort_order + 1)
            db.session.add(new_article)
            db.session.commit()
            flash('Article created successfully.', 'success')
        return redirect(url_for('admin_topic', topic_id=topic_id))
    return render_template('new_article.html', active_page='admin', topic=topic)

@app.route('/admin/topic/<int:topic_id>/article/<int:article_id>/edit', methods=['GET', 'POST'])
def edit_article(topic_id, article_id):
    topic = Topic.query.get_or_404(topic_id)
    article = Article.query.get_or_404(article_id)
    if request.method == 'POST':
        article.title = request.form.get('title')
        content = request.form.get('content')
        # Use a more permissive bleach cleaning
        article.content = bleach.clean(content, tags=['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'img', 'h1', 'h2', 'h3', 'blockquote', 'pre', 'code'],
                                       attributes={'a': ['href', 'target'], 'img': ['src', 'alt']})
        db.session.commit()
        flash('Article updated successfully.', 'success')
        return redirect(url_for('admin_topic', topic_id=topic_id))
    return render_template('edit_article.html', active_page='admin', topic=topic, article=article)

@app.route('/admin/topic/<int:topic_id>/article/<int:article_id>/delete', methods=['POST'])
def delete_article(topic_id, article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted successfully.', 'success')
    return redirect(url_for('admin_topic', topic_id=topic_id))

@app.route('/update_sort_order', methods=['POST'])
def update_sort_order():
    new_order = request.json['new_order']
    for index, topic_id in enumerate(new_order, start=1):
        topic = Topic.query.get(topic_id)
        if topic:
            topic.sort_order = index
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/login')
def login():
    return render_template('login.html', active_page='login')

@app.route('/admin/topic/<int:topic_id>/update_article_sort_order', methods=['POST'])
def update_article_sort_order(topic_id):
    new_order = request.json['new_order']
    for index, article_id in enumerate(new_order, start=1):
        article = Article.query.get(article_id)
        if article and article.topic_id == topic_id:
            article.sort_order = index
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'success': True, 'url': url_for('uploaded_file', filename=filename)})
    return jsonify({'success': False, 'message': 'File type not allowed'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/knowledge-base/topic/<int:topic_id>/article/<int:article_id>')
def view_article(topic_id, article_id):
    topic = Topic.query.get_or_404(topic_id)
    article = Article.query.get_or_404(article_id)
    return render_template('view_article.html', topic=topic, article=article)

if __name__ == '__main__':
    app.run(debug=True)
