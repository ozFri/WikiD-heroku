from models import User, Post, get_todays_recent_posts, get_post
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/index')
@app.route('/')
def index():
    posts = get_todays_recent_posts()
    return render_template('index.html', posts=posts)

@app.route('/event')
def event():
    session['eventname']="General"
    flash(session['eventname'])
    return render_template('index.html')

@app.route('/add-Snode')
def add_Snode(post_id):
    post=post_id
    schema=request.form['schema']
    target=request.form['target']
    Post.add_Snode(post,schema,target)

@app.route('/posts/<post_id>')
def post(post_id):
    post = Post(post_id)
    posts = post.get_posts
    supporting_posts = post.supporting
    opposing_posts = post.opposing
    supported_posts = post.supported
    opposed_posts = post.opposed
    return render_template('post.html', post=post)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 1:
            flash('Your username must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
        elif not User(username).register(password):
            flash('A user with that username already exists.')
        else:
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            flash('Invalid login.')
        else:
            session['username'] = username
            session['eventname'] = "General"
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('eventname',None)
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/change_event', methods=['POST'])
def change_event():
    session["eventname"]=request.form['event']
    return redirect(request.referrer)

@app.route('/add_post', methods=['POST'])
def add_post():
    title = request.form['title']

    if not title:
        flash('You must give your post a title.')
    else:
        User(session['username']).add_post(title)

    return redirect(url_for('index'))

#@app.route('/like_post/<post_id>')
#def like_post(post_id):
#    username = session.get('username')
#
#    if not username:
#        flash('You must be logged in to like a post.')
#        return redirect(url_for('login'))
#
#    User(username).like_post(post_id)
#
#    flash('Liked post.')
#    return redirect(request.referrer)

@app.route('/agree_with_post/<post_id>')
def agree_with_post(post_id):
    username = session.get('username')
    eventname = session.get('eventname')
    if not username:
        flash('You must be logged in to agree with a post.')
        return redirect(url_for('login'))

    User(username).agree_with_post(post_id, eventname)

    flash('Agreed with post in event "'+ eventname + '"')
    return redirect(request.referrer)

@app.route('/disagree_with_post/<post_id>')
def disagree_with_post(post_id):
    username = session.get('username')
    eventname = session.get('eventname')

    if not username:
        flash('You must be logged in to disagree with a post.')
        return redirect(url_for('login'))

    User(username).disagree_with_post(post_id, eventname)

    flash('Disagreed with post in event "'+ eventname + '"')
    return redirect(request.referrer)

@app.route('/undecided_on_post/<post_id>')
def undecided_on_post(post_id):
    username = session.get('username')
    eventname = session.get('eventname')
    if not username:
        flash('You must be logged in to follow a post.')
        return redirect(url_for('login'))

    User(username).undecided_on_post(post_id, eventname)

    flash('Undecided on post in event "'+ eventname + '"' )
    return redirect(request.referrer)

@app.route('/profile/<username>')
def profile(username):
    logged_in_username = session.get('username')
    user_being_viewed_username = username

    user_being_viewed = User(user_being_viewed_username)
    posts = user_being_viewed.get_recent_posts()

    similar = []
    common = []

    if logged_in_username:
        logged_in_user = User(logged_in_username)

        if logged_in_user.username == user_being_viewed.username:
            similar = logged_in_user.get_similar_users()
        else:
            common = logged_in_user.get_commonality_of_user(user_being_viewed)

    return render_template(
        'profile.html',
        username=username,
        posts=posts,
        similar=similar,
        common=common
    )
