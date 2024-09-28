from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func, or_
import bleach
import os
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
import re
import unicodedata
from faker import Faker
import random
import requests

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
    keywords = db.Column(db.String(200))  # New field for keywords
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Article {self.title}>'

@app.route('/')
def index():
    topics = Topic.query.options(joinedload(Topic.articles)).order_by(Topic.sort_order).all()
    return render_template('knowledge_base.html', active_page='knowledge_base', topics=topics)

@app.route('/knowledge-base')
def knowledge_base():
    topics = Topic.query.options(joinedload(Topic.articles)).order_by(Topic.sort_order).all()
    return render_template('knowledge_base.html', active_page='knowledge_base', topics=topics)

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not is_valid_search_query(query):
        return jsonify({'results': [], 'error': 'Invalid search query'})

    # Search for articles matching the query in title, content, or keywords
    articles = Article.query.filter(
        or_(
            Article.title.ilike(f'%{query}%'),
            Article.content.ilike(f'%{query}%'),
            Article.keywords.ilike(f'%{query}%')
        )
    ).all()

    results = []
    for article in articles:
        snippet = article.content[:200] + '...' if len(article.content) > 200 else article.content
        results.append({
            'id': article.id,
            'title': article.title,
            'snippet': snippet,
            'topic_id': article.topic_id
        })

    return jsonify({'results': results})

def is_valid_search_query(query):
    # Allow letters (including international characters), numbers, and spaces
    return bool(re.match(r'^[\w\s]{3,}$', query, re.UNICODE))

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
            keywords = request.form.get('keywords')
            
            # Process keywords
            keyword_list = [k.strip() for k in keywords.split(',') if len(k.strip()) >= 3]
            processed_keywords = ', '.join(keyword_list)

            # Use a more permissive bleach cleaning
            content = bleach.clean(content, tags=['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'img', 'h1', 'h2', 'h3', 'blockquote', 'pre', 'code'],
                                   attributes={'a': ['href', 'target'], 'img': ['src', 'alt']})
            max_sort_order = db.session.query(func.max(Article.sort_order)).filter_by(topic_id=topic_id).scalar() or 0
            new_article = Article(title=title, content=content, keywords=processed_keywords, topic_id=topic_id, sort_order=max_sort_order + 1)
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
        keywords = request.form.get('keywords')
        
        # Process keywords
        keyword_list = [k.strip() for k in keywords.split(',') if len(k.strip()) >= 3]
        article.keywords = ', '.join(keyword_list)

        # Use a more permissive bleach cleaning
        article.content = bleach.clean(content, tags=['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'img', 'h1', 'h2', 'h3', 'blockquote', 'pre', 'code'],
                                       attributes={'a': ['href', 'target'], 'img': ['src', 'alt', 'style']})
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
    print("Update sort order route hit")
    new_order = request.json['new_order']
    print("Received new order:", new_order)
    for index, topic_id in enumerate(new_order, start=1):
        topic = Topic.query.get(topic_id)
        if topic:
            topic.sort_order = index
            print(f"Updated topic {topic_id} to order {index}")
    db.session.commit()
    print("Sort order update completed")
    return jsonify({'status': 'success'})

@app.route('/login')
def login():
    return render_template('login.html', active_page='login')

@app.route('/admin/topic/<int:topic_id>/update_article_sort_order', methods=['POST'])
def update_article_sort_order(topic_id):
    print(f"Update article sort order route hit for topic {topic_id}")
    new_order = request.json['new_order']
    print("Received new article order:", new_order)
    for index, article_id in enumerate(new_order, start=1):
        article = Article.query.get(article_id)
        if article and article.topic_id == topic_id:
            article.sort_order = index
            print(f"Updated article {article_id} to order {index}")
    db.session.commit()
    print("Article sort order update completed")
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

@app.route('/generate_content', methods=['GET', 'POST'])
def generate_content():
    if request.method == 'POST':
        num_topics = int(request.form.get('num_topics', 1))
        num_articles = int(request.form.get('num_articles', 1))
        image_percentage = int(request.form.get('image_percentage', 0))
        use_foreign_chars = request.form.get('use_foreign_chars') == 'on'
        
        fake = Faker(['en_US', 'ja_JP', 'ru_RU']) if use_foreign_chars else Faker(['en_US'])
        
        for _ in range(num_topics):
            topic_name = fake.word().capitalize()
            max_sort_order = db.session.query(func.max(Topic.sort_order)).scalar() or 0
            new_topic = Topic(name=topic_name, sort_order=max_sort_order + 1)
            db.session.add(new_topic)
            db.session.flush()  # This assigns an ID to the new topic
            
            for _ in range(num_articles):
                title = fake.sentence(nb_words=4)
                content_paragraphs = fake.paragraphs(nb=random.randint(3, 10))
                
                content = '<p>' + '</p><p>'.join(content_paragraphs) + '</p>'
                
                if random.random() < image_percentage / 100:  # Use the specified percentage
                    image_url = add_random_image()
                    if image_url:
                        content += f'<p><img src="{image_url}" alt="Random Image" style="max-width: 100%; height: auto;"></p>'
                
                keywords = ', '.join(fake.words(nb=random.randint(3, 8)))
                
                max_article_sort_order = db.session.query(func.max(Article.sort_order)).filter_by(topic_id=new_topic.id).scalar() or 0
                new_article = Article(
                    title=title[:100],  # Limit title to 100 characters
                    content=content,
                    keywords=keywords,
                    topic_id=new_topic.id,
                    sort_order=max_article_sort_order + 1
                )
                db.session.add(new_article)
        
        db.session.commit()
        flash(f'Generated {num_topics} topics with {num_articles} articles each. {image_percentage}% of articles have images.', 'success')
        return redirect(url_for('generate_content'))
    
    return render_template('generate_content.html', active_page='generate_content')

def add_random_image():
    width = random.randint(300, 800)
    height = random.randint(200, 600)
    image_url = f'https://picsum.photos/{width}/{height}'
    
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            file_extension = response.headers.get('content-type', '').split('/')[-1]
            filename = secure_filename(f'random_image_{random.randint(1000, 9999)}.{file_extension}')
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            
            return url_for('static', filename=f'uploads/{filename}')
    except Exception as e:
        print(f"Error downloading image: {e}")
    
    return None

if __name__ == '__main__':
    app.run(debug=True)