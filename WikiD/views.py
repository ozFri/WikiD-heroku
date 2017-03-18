from .models import INode, get_todays_recent_posts, get_iNode, create_new_schema_relationship
from flask import Flask, request, session, redirect, url_for, render_template, flash
from .user import User

app = Flask(__name__)

#Render Index Page
@app.route('/index')
@app.route('/')
def index():
    inodes = get_todays_recent_posts()
    return render_template('index.html', inodes=inodes)

def init_rest_interface(cfg, flask_webapp):
    """
    Initialize REST interface
    """

    def rest_entry(path, f, flask_args={'methods': ['POST']}):
        return (path, f, flask_args)

    def redirect_entry(path, path_to, flask_args):
        def redirector():
            return redirect(path_to, code=302)
        redirector.func_name = 'redirector_%s' % path.replace('/', '_')
        assert 'endpoint' not in flask_args
        flask_args['endpoint'] = redirector.func_name
        return (path, redirector, flask_args)

    def login_decorator(f):
        """
        security boundary: assert logged-in user before executing REST api call
        """
        @wraps(f)
        def wrapped_function(*args, **kw):
            if None == session.get('username'):
                return redirect('/login')
            return f(*args, **kw)

        return wrapped_function


    def localhost_access_decorator__ipv4(f):
        @wraps(f)
        def wrapped_function(*args, **kw):
            rmt_addr, _ = request.peer_sock_addr
            if '127.0.0.1' != rmt_addr:
                log.warning('unauthorized attempt to access localhost restricted path: %s' % (request.path))
                return make_response__http__empty(stauts=403)
            return f(*args, **kw)
        return wrapped_function

    rest_entry_set = [
                      # REST endpoints
                      rest_entry('/feedback', wd_feedback.rest__send_user_feedback__email),
                      rest_entry('/index', wd_api.index, {'methods': ['GET']}),
                      rest_entry('/login', wd_user.rest__login, {'methods': ['GET', 'POST']}),
                      rest_entry('/logout', wd_user.rest__logout, {'methods': ['GET', 'POST']}),
                      # redirects
                      redirect_entry('/', '/index', {'methods': ['GET']}),
                      redirect_entry('/index.html', '/index', {'methods': ['GET']}),
                      rest_entry('/signup', rz_user.rest__user_signup, {'methods': ['GET', 'POST']})
                      #requires login
                  ]

    for re_entry in rest_entry_set:
        rest_path, f, flask_args = re_entry

        if cfg.access_control and rest_path not in no_login_paths:
            # currently require login on all but /login paths
            f = login_decorator(f)

        # apply local host access restriction
        if rest_path.startswith('/monitor'):
            f = localhost_access_decorator__ipv4(f)

        # [!] order seems important - apply route decorator last
        route_dec = flask_webapp.route(rest_path, **flask_args)
        f = route_dec(f)

        flask_webapp.f = f  # assign decorated function

@app.route('/<inode_id>/add-Snode/<inode_name>', methods=['GET', 'POST'])
def add_S_node(inode_id,inode_name):
    inode=inode_name
    #the type of the schema
    schema = request.form['schema']
    #the title of the target node 
    target = request.form.get('target',None)
    #the title of the source node
    source = request.form.get('source',None)
    newTarget = request.form.getlist('new-target',None)
    newSource = request.form.getlist('new-source',None)
    schemaID=User(session['username']).add_S_Node(schema)
    if target is not None:
        target = request.form['target']
        source = inode
    elif source is not None:    
        source = request.form['source']
        target = inode
    #elif newTarget is not None:    
    #    User(session['username']).add_I_Node(newTarget)
    #    target = newTarget = request.form['new-target']
    #    source = inode
    #elif newSource is not None:    
    #    User(session['username']).add_I_Node(newSource)
    #    source = newSource = request.form['new-source']
    #    target = inode
    if (target or source or newTarget or newSource) is not None:
        create_new_schema_relationship(source,schemaID,target)  
    return redirect(request.referrer)

@app.route('/event')
def event():
    session['eventname'] = "General"
    flash(session['eventname'])
    return render_template('index.html')

@app.route('/inodes/<inode_id>')
def inode(inode_id):
    inode = INode(inode_id)
    inodes = inode.inodes
    agree_votes = inode.agreeing
    disagree_votes = inode.disagreeing
    undecided_votes = inode.undecided
    supporting_inodes = inode.supporting
    opposing_inodes = inode.opposing
    supported_inodes = inode.supported
    opposed_inodes = inode.opposed
    user_vote = inode.user_vote
    return render_template('inode.html', inode=inode,supporting_inodes=supporting_inodes,supported_inodes=supported_inodes,opposing_inodes=opposing_inodes,opposed_inodes=opposed_inodes,agree_votes=agree_votes,disagree_votes=disagree_votes,undecided_votes=undecided_votes,user_vote=user_vote)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.register_validation(flash, username, password):
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
    session.pop('eventname', None)
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/change_event', methods=['POST'])
def change_event():
    session["eventname"] = request.form['event']
    return redirect(request.referrer)

@app.route('/add_iNode', methods=['POST'])
def add_I_Node():
    title = request.form['title']

    if not title:
        flash('You must give your post a title.')
    else:
        User(session['username']).add_I_Node(title)

    return redirect(request.referrer)

@app.route('/agree_with_inode/<inode_id>')
def agree_with_inode(inode_id):
    username = session.get('username')
    eventname = session.get('eventname')
    if not username:
        flash('You must be logged in to agree with a post.')
        return redirect(url_for('login'))

    User(username).agree_with_inode(inode_id, eventname)

    flash('Agreed with inode in event "' + eventname + '"')
    return redirect(request.referrer)

@app.route('/disagree_with_inode/<inode_id>')
def disagree_with_inode(inode_id):
    username = session.get('username')
    eventname = session.get('eventname')

    if not username:
        flash('You must be logged in to disagree with a post.')
        return redirect(url_for('login'))

    User(username).disagree_with_inode(inode_id, eventname)

    flash('Disagreed with inode in event "' + eventname + '"')
    return redirect(request.referrer)

@app.route('/undecided_on_inode/<inode_id>')
def undecided_on_inode(inode_id):
    username = session.get('username')
    eventname = session.get('eventname')
    if not username:
        flash('You must be logged in to follow a post.')
        return redirect(url_for('login'))

    User(username).undecided_on_inode(inode_id, eventname)

    flash('Undecided on post in event "' + eventname + '"')
    return redirect(request.referrer)

@app.route('/profile/<username>')
def profile(username):
    logged_in_username = session.get('username')
    user_being_viewed_username = username

    user_being_viewed = User(user_being_viewed_username)
    inodes = user_being_viewed.get_recent_posts()

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
        inodes=inodes,
        similar=similar,
        common=common
    )
