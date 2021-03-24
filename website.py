# https://uptimerobot.com/dashboard#783777145
# tutorial: https://www.freecodecamp.org/news/how-to-build-a-web-application-using-flask-and-deploy-it-to-the-cloud-3551c985e492/
# https://opentechschool.github.io/python-flask/core/hello-world.html

# CURRENT STEP: https://pythonbasics.org/flask-login/#User-Model

from flask import Flask, Markup, render_template, request, redirect, url_for, make_response, g, abort
from functools import wraps
from threading import Thread
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
import json
import re

import authenticate

app = Flask(__name__)
app.secret_key = 'super secret key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(id):
    users = {}
    with open('users.json', 'r+') as file:
        users = json.loads(file.read())

    if id not in users:
        return

    user = User()
    user.id = id
    return user


@login_manager.request_loader
def request_loader(request):
    users = {}
    with open('users.json', 'r+') as file:
        users = json.loads(file.read())

    username = request.form.get('username')
    if username not in users:
        return

    user = User()
    user.id = username

    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html')
    
    # request.method == 'POST'
    error = authenticate.store_account(dict(request.form))
    if error:
        return render_template('create.html', error=error)
    else:
        user = User()
        user.id = request.form.get('username')
        login_user(user)
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # request.method == 'POST'
    username = request.form.get('username')
    password = request.form.get('password')

    verified = authenticate.verify_login(username, password)
    if verified:
        user = User()
        user.id = username
        login_user(user)
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error='Failed login attempt')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'GET':
        user = get_user_info(current_user.id)
        settings = (
            {
                'field': 'Username',
                'value': user['username']
            }, {
                'field': 'Email',
                'value': user['email'],
                'edit': Markup('<input type="email" id="email" name="email" style="width:unset;" placeholder="username@domain.name">')
            }, {
                'field': 'Player URL',
                'value': Markup('<a href="' + user['player_url'] + '">' + re.search('\d*$', user['player_url']).group() + '</a>'),
                'edit': Markup('<input type="url" id="player_url" name="player_url" style="width:unset;" placeholder="https://simulationhockey.com/showthread.php?tid=" pattern="^https:\/\/simulationhockey\.com\/showthread\.php\?tid=\d{1,}$" oninvalid="this.setCustomValidity("URL must be in the form: https://simulationhockey.com/showthread.php?tid={$threadID}")" oninput="this.setCustomValidity("")">')
            }, {
                'field': 'Updates URL',
                'value': Markup('<a href="' + user['updates_url'] + '">' + re.search('\d*$', user['updates_url']).group() + '</a>'),
                'edit': Markup('<input type="url" id="updates_url" name="updates_url" style="width:unset;" placeholder="https://simulationhockey.com/showthread.php?tid=" pattern="^https:\/\/simulationhockey\.com\/showthread\.php\?tid=\d{1,}$" oninvalid="this.setCustomValidity("URL must be in the form: https://simulationhockey.com/showthread.php?tid={$threadID}")" oninput="this.setCustomValidity("")">')
            }
        )
        return render_template('settings.html', settings=settings)
    else:
        user = get_user_info(current_user.id)
        for key, value in dict(request.form).items():
            if value != '':
                user[key] = value
        set_user_info(current_user.id, user)
        return redirect(url_for('settings'))


@app.route('/player')
@login_required
def player():
    user = get_user_info(current_user.id)
    return render_template('player.html', user=user)


@app.route('/updates')
@login_required
def updates():
    user = get_user_info(current_user.id)
    return render_template('updates.html', user=user)


@app.route('/protected')
@login_required
def protected():
    return 'Logged in as ' + current_user.id


def get_user_info(id):
    users = {}
    with open('users.json', 'r+') as file:
        users = json.loads(file.read())
    
    return users[id] or False


def set_user_info(id, info):
    users = {}
    with open('users.json', 'r+') as file:
        users = json.loads(file.read())
    
    users[id] = info;
    with open('users.json', 'w+') as file:
        file.write(json.dumps(users))


def run():
    app.run(host='0.0.0.0', port=8080)


def shutdown():
    raise RuntimeError('Server shutting down...')


def start():
    server = Thread(target=run)
    server.start()
