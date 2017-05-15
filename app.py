#!/usr/bin/env python3
from os import environ
from re import sub
from codecs import encode
from sys import getsizeof

from werkzeug.routing import BuildError

from forms import SignUpForm, PostForm, SignInForm
from models import User, Post, Comment, Relationship, DoesNotExist, DB

from werkzeug.exceptions import BadRequest
from flask import Flask, flash, redirect, url_for, render_template, g, abort, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import check_password_hash
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView


app = Flask(__name__)
app.secret_key = 'gb5;w85uigb4hp89g 5ubg8959gb5g9p891234567gfvhytrdgfjdfgd5c56d566576tyvyfyftfyttytyftf'


class AuthView(ModelView):
    column_exclude_list = ('avatar', 'password')
    form_excluded_columns = ['email']

    def is_accessible(self):
        if 'HEROKU' in environ:
            return current_user.is_authenticated and (g.user.username == environ['admin'])
        else:
            return current_user.is_authenticated

admin = Admin(app, name='TDIC')
admin.add_view(AuthView(User, 'User'))
admin.add_view(AuthView(Post, 'Post'))
admin.add_view(AuthView(Comment, 'Comment'))
admin.add_view(AuthView(Relationship, 'Relationship'))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'sign_in'


@login_manager.user_loader
def load_user(id):
    try:
        return User.get(User.id == id)
    except DoesNotExist:
        return None


@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    posts = None
    if current_user.is_authenticated:
        posts = Post.select().paginate(page, 20)
    return render_template('index.html', posts=posts, page=page)


@app.route('/comment/<int:id>', methods=['POST'])
@login_required
def comment(id):
    form = PostForm()
    if form.validate_on_submit():
        if request.files['content']:
            if 'image' in request.files['content'].content_type:
                file_u = request.files['content'].read()
                if getsizeof(file_u) <= 3000000:
                    file_a = 'data:{};base64,{}'.format(request.files['content'].content_type,
                                                        encode(file_u, 'base64').decode('utf-8'))
                                                        post_create = Post.create(user=g.user.id, data=file_a)
                                                        flash('Posted!')
                                                        return redirect(url_for('index'))
                else:
                    flash('Image is bigger than 3 mb.')
    else:
        flash('The upload is not an image. ')
    return render_template('post.html', form=form)
        return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        User.create_user(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=form.password.data
        )
        flash('You signed up! Remember to login!')
        return redirect(url_for('index'))

    return render_template('signup.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
@app.route('/signin/<action>', methods=['GET', 'POST'])
def sign_in(action=None):
    form = SignInForm()
    other_text = action
    if form.validate_on_submit():
        try:
            user = User.get(User.username ** form.name_email.data)
        except DoesNotExist:
            try:
                user = User.get(User.email ** form.name_email.data)
            except DoesNotExist:
                flash('Could not find a user with that username/email and password combination')
                return render_template('signin.html', form=form)
            else:
                user_exists = True
        else:
            user_exists = True
        if user_exists:
            if check_password_hash(user.password, form.password.data):
                if action:
                    try:
                        return redirect(url_for(action))
                    except BuildError:
                        flash('Could not find the action to verify')
                        return redirect(url_for('index')), 404
                login_user(user, remember=form.remember.data)
                flash('You have been logged in! Go ahead, explore!')
                return redirect(url_for('index'))
            else:
                flash('Could not find a user with that username/email and password combination')
    return render_template('signin.html', form=form, text=other_text)


@app.route('/signout')
@login_required
def sign_out():
    logout_user()
    flash('You have been signed out. Make sure to come back! Your friends will be waiting!')
    return redirect(url_for('index'))


@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        if request.files['content']:
            if 'image' in request.files['content'].content_type:
                file_u = request.files['content'].read()
                if getsizeof(file_u) <= 5000000:
                    file_a = 'data:{};base64,{}'.format(request.files['content'].content_type,
                                                        encode(file_u, 'base64').decode('utf-8'))
                    post_create = Post.create(user=g.user.id, data=file_a)
                    flash('Posted!')
                    return redirect(url_for('index'))
                else:
                    flash('Image is bigger than 5 mb.')
        else:
            flash('The upload is not an image. ')
    return render_template('post.html', form=form)


@app.route('/user')
@app.route('/user/<username>')
@login_required
def user_view(username=None):
    try:
        if username:
            user = User.get(User.username ** username)
        else:
            user = User.get(User.username ** request.values['user'])
    except DoesNotExist:
        abort(406)
    except KeyError:
        abort(400)
    else:
        posts = Post.select().where(Post.user == user)
        return render_template('index.html', user=user, posts=posts)


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        user = User.get(User.username ** username)
    except DoesNotExist:
        abort(406)
    else:
        try:
            Relationship.get(Relationship.from_user == g.user, Relationship.to_user == user)
        except DoesNotExist:
            Relationship.create(from_user=g.user, to_user=user)
            flash('Followed {}!'.format(user.username))
            return redirect(url_for('user_view', username=user.username))
        else:
            flash('You already followed {}.'.format(user.username))
            return redirect(url_for('user_view', username=user.username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        user = User.get(User.username ** username)
    except DoesNotExist:
        abort(406)
    else:
        try:
            relation = Relationship.get(Relationship.from_user == g.user,
                                        Relationship.to_user == user)
        except DoesNotExist:
            flash('You haven\'t followed {} yet.'.format(user.username))
            return redirect(url_for('user_view', username=user.username))
        else:
            relation.delete_instance()
            flash('Unfollowed {}.'.format(user.username))
            return redirect(url_for('user_view', username=user.username))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        user = g.user
        if request.form['bio'] != '':
            if len(request.form['bio']) <= 255:
                user.bio = request.form['bio']
                user.save()
                flash('Bio set!')
            else:
                flash('Bio is too long.')
        if request.files['avatar']:
            if 'image' in request.files['avatar'].content_type:
                file_u = request.files['avatar'].read()
                if getsizeof(file_u) <= 3000000:
                    file_a = 'data:{};base64,{}'.format(request.files['avatar'].content_type,
                                                        encode(file_u, 'base64').decode('utf-8'))
                    g.user.avatar = file_a
                    g.user.save()
                    flash('Avatar set!')
                else:
                    flash('Avatar is bigger than 3 mb.')
            else:
                flash('Avatar is not an image.')
        if 'email' not in request.form:
            if user.default_view != 'noemail':
                user.default_view = 'noemail'
                user.save()
                flash('Email turned off.')
        elif 'email' in request.form:
            if user.default_view == 'noemail':
                user.default_view = 'email'
                user.save()
                flash('Email enabled.')
    return render_template('settings.html')


@app.route('/delete_account')
@login_required
def delete_account():
    g.user.delete_instance()
    logout_user()
    flash('User deleted. We are sorry to see you go!')
    return redirect(url_for('index'))


@app.route('/view_post/<int:id>')
@login_required
def view_post(id):
    try:
        viewed_post = Post.get(Post.id == id)
    except DoesNotExist:
        abort(404)
    else:
        return render_template('index.html', posts=[viewed_post])


@app.errorhandler(404)
def e404(error):
    print(error)
    return render_template('layout.html', error_head='404',
                           error_message='You have landed in the wrong spot.',
                           error_link='/', error_link_m='Return to homepage'), 404


@app.errorhandler(406)
def e406(error):
    print(error)
    return render_template('layout.html', error_head='406',
                           error_message='Dude, that user does not exist.',
                           error_link='/', error_link_m='Back to safety'), 406


@app.errorhandler(500)
def e500(error):
    print(error)
    return render_template('layout.html', error_head='500',
                           error_message='Holy smokes! You just crashed the server!',
                           error_link='https://i.ytimg.com/vi/tntOCGkgt98/maxresdefault.jpg',
                           error_link_m='Cat picture'), 500


@app.before_request
def before():
    g.user = current_user
    g.db = DB
    g.db.connect()
    g.db.create_tables([User, Post, Comment, Relationship], safe=True)

    url = sub('http://', 'https://', request.url)
    if 'http://' in request.url and 'HEROKU' in environ:
        return redirect(url)


@app.after_request
def after(response):
    g.db.close()
    return response


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
