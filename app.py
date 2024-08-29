from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///topics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a random secret key
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    sort_order = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))  # New field

    def __repr__(self):
        return f'<Topic {self.name}>'

# Remove the following lines as we'll use Flask-Migrate instead
# with app.app_context():
#     db.create_all()

@app.route('/')
def index():
    return render_template('index.html', active_page='home')

@app.route('/knowledge-base')
def knowledge_base():
    topics = Topic.query.order_by(Topic.sort_order).all()
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
                elif Topic.query.count() >= 10:
                    flash('Maximum number of topics (10) reached.', 'error')
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
                db.session.delete(topic)
                db.session.commit()
                flash('Topic deleted successfully.', 'success')
            else:
                flash('Topic not found.', 'error')
        return redirect(url_for('admin'))

    topics = Topic.query.order_by(Topic.sort_order).all()
    topic_count = Topic.query.count()
    return render_template('admin.html', active_page='admin', topics=topics, topic_count=topic_count)

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

if __name__ == '__main__':
    app.run(debug=True)
