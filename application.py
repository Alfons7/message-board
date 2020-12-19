import os
from flask import Flask, request, render_template, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, exc
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from helpers import time_ago, not_login_required, get_next_page

app = Flask(__name__)

#
# configuration
# 
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if app.config['SECRET_KEY'] is None:
    raise ValueError('Secret Key Missing')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# TODO: set SQLALCHEMY_ECHO to False when done with development
# app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
# Ensure FOREIGN KEY constraints are enforced when using sqlite 
# https://gist.github.com/asyd/a7aadcf07a66035ac15d284aef10d458
if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    def _fk_pragma_on_connect(dbapi_con, con_record):  # noqa
        dbapi_con.execute('pragma foreign_keys=ON;')
    with app.app_context():
        from sqlalchemy import event
        event.listen(db.engine, 'connect', _fk_pragma_on_connect)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
app.jinja_env.filters["time_ago"] = time_ago

from models import User, Post
from forms import LoginForm, RegisterForm, PostForm, ConfirmDelete

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

#
# Custom error handler
#

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='Not found'), 404


#
# view functions for log in, log out and registration
#

@app.route('/login', methods=['GET', 'POST'])
@not_login_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        flash('You are logged in.', 'info')
        return redirect(get_next_page(request))
    return render_template('login.html', title='Log in', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You logged out.', 'warning')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@not_login_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome to our message board! Now you can log in and add your own messages.', 'info')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


#
# view functions to display and handle messages
#

@app.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', 
        title="MessageBoard", heading="All messages", posts=posts)

@app.route('/favorites')
@login_required
def favorites():
    posts = current_user.favorites
    return render_template('index.html', 
        title="My favorites", heading="My favorite messages", posts=posts)

@app.route('/my_posts')
@login_required
def my_posts():
    posts = current_user.posts
    return render_template('index.html', 
        title="My messages", heading="My messages", posts=posts)


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    next_page = get_next_page(request)
    if form.validate_on_submit():
        post = Post(text=form.text.data, user=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your message is now online.', 'info')
        return redirect(next_page)
    return render_template('post.html', title='New message', form=form, next_page=next_page)

# helper function for the edit and delelete views below
def get_post(id):
    """
    Return the post with the given id or abort with an http error message 
      404 if no such post exists or if the post exists but it does not belong 
      to the loged in user
    Assumes the request comes from a logged in user.
    """
    post = Post.query.filter(
        and_(Post.id == id, Post.user_id == current_user.id)).first_or_404()
    return post


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = get_post(id)
    next_page = get_next_page(request)    
    if request.method == 'GET':
        form = PostForm(obj=post)
    else:
        form = PostForm()
        if form.validate_on_submit():
            post.text = form.text.data
            db.session.commit()
            flash('Your message has been updated.', 'success')
            return redirect(next_page)
    return render_template('post.html', 
        title='Update message', form=form, next_page=next_page)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = get_post(id)
    next_page = get_next_page(request)
    form = ConfirmDelete()
    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash('Your message is gone!', 'success')
        return redirect(next_page)
    return render_template('confirm_delete.html', 
            title='Delete message', post=post, form=form, next_page=next_page)

#
# favorites feature
#
@app.route('/fav', methods=["POST"])
@login_required
def fav():
    post_id = request.form.get('post_id')
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return jsonify(success=False)
    current_user.fav(post)
    try:
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
    return jsonify(
        success=True, action="fav", post_id=post.id, likes=post.likers.count())


@app.route('/unfav', methods=["POST"])
@login_required
def unfav():
    post_id = request.form.get('post_id')
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return jsonify(success=False)
    current_user.unfav(post)
    try:
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
    return jsonify(
        success=True, action="unfav", post_id=post.id, likes=post.likers.count())