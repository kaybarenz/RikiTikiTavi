"""
    Routes
    ~~~~~~
"""
import os

from flask import Blueprint, current_app, Response, jsonify
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from werkzeug.utils import secure_filename

from wiki.core import Processor
from wiki.web.forms import EditorForm, ChangePasswordForm, UserEditorForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki, get_users, get_pictures
from wiki.web import current_users
from wiki.web.user import protect, admin_protect, UserManager, User

bp = Blueprint('wiki', __name__)


@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    return render_template('page.html', page=page)


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    images = get_pictures()
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        page.save()
        flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page, images=images)


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    return data['html']


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        current_wiki.move(url, newurl)
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.name.data)
        login_user(user)
        user.set('authenticated', True)
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route('/user/change_password/', methods=['GET', 'POST'])
def user_change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.confirm_password.data)
        current_user.set('authenticated', True)
        flash('Password Change Successful.', 'success')
        return render_template('change_password.html', form=form)
    return render_template('change_password.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.user_login'))


@bp.route('/user/create/', methods=['GET', 'POST'])
def user_create():
    form = UserEditorForm()
    if form.validate_on_submit():
        get_users().add_user(form.name.data, form.password.data, form.active.data)
        return redirect(url_for('wiki.admin'))
    return render_template('User/addEdit.html', form=form, create=True)


@bp.route('/user/edit/<string:user_id>/', methods=['GET', 'POST'])
def user_edit(user_id):
    user_manager = get_users()
    user = user_manager.get_user(user_id)
    form = UserEditorForm(name=user.name, password=user.get("password"), active=user.get("active"))

    if form.validate_on_submit():
        if user.name != form.name.data:
            temp = user_manager.add_user(form.name.data, user.data['password'], user.data['password'],
                                         user.data['roles'], user.data['authentication_method'])
            user_manager.delete_user(user.name)
            user = temp
        user.set_password(form.password.data)
        user.set("active", form.active.data)
        return redirect(url_for('wiki.admin'))
    return render_template('User/addEdit.html', form=form, create=False)


@bp.route('/user/delete/<string:user_id>/')
def user_delete(user_id):
    get_users().delete_user(user_id)
    return redirect(url_for('wiki.admin'))


@bp.route('/admin/')
@admin_protect
def admin():
    users = current_users
    return render_template('admin.html', users=users.read())


@bp.route('/profile/')
def profile():
    users = current_users
    return render_template('profile.html', users=users.read())


@bp.route('/pictures/', methods=['POST'])
def pictures():
    if request.method == "POST":
        file = request.files['file']
        filename = secure_filename(file.filename)
        if file:
            file.save(os.path.join(current_app.config['PIC_BASE'], filename))

        resp = jsonify({'message': 'success', 'filename': filename})
        resp.status_code = 201
        return resp


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
