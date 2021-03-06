from .models import AIFNode, get_aifNodes, get_aifNode, rename_iNode,create_new_schema_relationship, get_INodes
from flask import Flask, request, session, redirect, url_for, render_template, flash,jsonify #,Blueprints
from flask_cors import CORS
import logging
from .user import User
import requests
from . import config

# whatever = Blueprint("mold", __name__)
app = Flask(__name__)
logging.getLogger('flask_cors').level = logging.DEBUG
CORS(app)

#Render Index Page
@app.route('/api', methods=[ "GET" ])
def version():
    d = 1;
    return jsonify(d)

@app.route('/index')
@app.route('/')
def index():
    aifNodes = get_aifNodes()
    logged_in_user = User(session.get('username'))
    feed = logged_in_user.get_user_feed()
    return render_template('index.html', aifnodes=aifNodes, feed=feed)

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

# @app.route('/<aifnode_id>/add-tag', methods=['POST','GET'])
# def add_tag(aifnode_id):

@app.route('/<source>/<schema>/<target>', methods=['POST','GET'])
def add_S_node(source,schema,target):
    username = session.get('username')
    discussionname = session.get('discussionname')
    if not username or username == "Guest":
        flash('You must be logged in to agree with a post.','danger')
        return redirect(url_for('login'))
    if (schema and source and target) is not None:
        if target != source:
            source_title=get_aifNode(source).properties["title"]
            target_title=get_aifNode(target).properties["title"]
            schema_id = User(session['username']).add_S_Node(schema,source,target)
            if (target and source and schema) is not None:
                create_new_schema_relationship(source_title,schema_id,target_title)
            flash(source_title +" "+ schema +" "+ target_title,'success')

    return redirect(request.referrer)

@app.route('/discussion')
def discussion():
    session['discussionname'] = "General"
    flash("Viweing discussion: " + session['discussionname'])
    return render_template('index.html')

@app.route('/aifnodes/<aifnode_id>')
def aifNode(aifnode_id):
    aifnode = AIFNode(aifnode_id)
    aifnodes = get_aifNodes()
    agree_votes = aifnode.agreeing
    disagree_votes = aifnode.disagreeing
    undecided_votes = aifnode.undecided
    supporting_nodes = aifnode.supporting
    opposing_nodes = aifnode.opposing
    supported_nodes = aifnode.supported
    opposed_nodes = aifnode.opposed
    user_vote = aifnode.user_vote
    activity_feed = aifnode.activity_feed

    return render_template('aifnode.html',aifnodes=aifnodes,aifnode=aifnode,supporting_nodes=supporting_nodes,supported_nodes=supported_nodes,opposing_nodes=opposing_nodes,opposed_nodes=opposed_nodes,agree_votes=agree_votes,disagree_votes=disagree_votes,undecided_votes=undecided_votes,user_vote=user_vote)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.register_validation(flash, username, password):
            session['username'] = username
            flash('Logged in.','success')
            return redirect(url_for('discussion'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            flash('Invalid login.','danger')
        else:
            session['username'] = username
            session['discussionname'] = "General"
            flash('Logged in.','success')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('discussionname', None)
    flash('Logged out.','primary')
    return redirect(url_for('index'))

@app.route('/change_discussion', methods=['POST'])
def change_discussion():
    session["discussionname"] = request.form['discussion']
    return redirect(request.referrer)

@app.route('/add_iNode', methods=['POST'])
def add_I_Node():
    title = request.form['title']

    if not title:
        flash('You must give your post a title.','primary')
    else:
        User(session['username']).add_I_Node(title)

    return redirect(request.referrer)

@app.route('/<aifnode_id>/vote/<vote_type>')
def vote_on_aifnode(aifnode_id,vote_type):
    username = session.get('username')
    discussionname = session.get('discussionname')
    aifnode = AIFNode(aifnode_id)
    if not username or username == "Guest":
        flash('You must be logged in to vote on a post.','danger')
        return redirect(url_for('login'))

    User(username).vote_on_aifnode(aifnode_id, discussionname, vote_type)

    flash('Voted "' + vote_type + '" on "' + aifnode.title + '" in discussion "' + discussionname + '"','primary')
    return redirect(request.referrer)

@app.route('/<inode_id>/rename')
def rename_I_Node(inode_id):
    username = session.get('username')
    discussionname = session.get('discussionname')
    if not username or username == "Guest":
        flash('You must be logged in to agree with a post.','danger')
        return redirect(url_for('login'))
    newTitle = request.form['new-title']
    rename_iNode(aifnode_id,newTitle)

    return redirect(request.referrer)

@app.route('/<aifnode_id>/delete')
def delete_aifnode(aifnode_id):
    username = session.get('username')
    discussionname = session.get('discussionname')
    if not username or username == "Guest":
        flash('You must be logged in to delete a post.','danger')
        return redirect(url_for('login'))
    aifnode = AIFNode(aifnode_id)
    aifnode.delete()
    flash('Deleted Node','primary')
    return redirect("/index")

@app.route('/profile/<username>')
def profile(username):
    logged_in_username = session.get('username')
    user_being_viewed_username = username

    user_being_viewed = User(user_being_viewed_username)
    aifnodes = user_being_viewed.get_recent_posts()
    feed = user_being_viewed.get_user_feed()

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
        aifnodes=aifnodes,
        similar=similar,
        common=common
    )

@app.route('/search/<searchterm>')
def search(searchterm):

    return searchterm

@app.route('/graphql',methods=['GET'])
def get_graphql():
    query=request.args.get('query')

    #JSON object
    json={"query":query}

    restAPI=requests.post(config.graphql_url,json=json,headers=config.headers)


    return jsonify(restAPI.json()['data']);
