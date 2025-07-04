from datetime import datetime, timezone, timedelta
from flask import render_template, flash, redirect, url_for, request, g, \
    current_app,jsonify,abort
from flask_login import current_user, login_required
import sqlalchemy as sa
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, CommentForm, MessageForm
from app.models import User, Post , Reaction , Comment, Message
from app.main import bp
from werkzeug.utils import secure_filename
import uuid, os
from sqlalchemy import func
from functools import wraps
from app.utility.greetings import get_dynamic_greeting

# Update user's last_seen timestamp on every request if logged in
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()

def admin_required(f): # Decorator to protect admin-only routes (like admin-dashboard). Returns 403 if unauthorized.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    
    greeting = get_dynamic_greeting(current_user.username)
    form = PostForm()
    if form.validate_on_submit():

        post = Post(body=form.body.data, author=current_user,tag=form.tag.data)
       
        if form.pic.data:
            filename = secure_filename(form.pic.data.filename)
            unique = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER_POST'], unique)
            form.pic.data.save(save_path)

            post.pic = unique

        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!','success')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts()
            .join(User, Post.user_id == User.id) .filter(Post.is_deleted == False, User.is_banned == False),
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    
    # AJAX request: returns only post list partial if called from infinite scroll
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
        return render_template('partials/_post_list.html', posts=posts.items, next_url=next_url)
        


    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html',greeting=greeting, title=('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)



@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).join(User, Post.user_id == User.id).filter(Post.is_deleted == False, User.is_banned == False).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
        return render_template('partials/_post_list.html', posts=posts.items, next_url=next_url)


    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Explore',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = Post.query.join(User, Post.user_id == User.id).filter(Post.user_id == user.id,Post.is_deleted == False,User.is_banned == False).order_by(Post.timestamp.desc())

    posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)

    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
        return render_template('partials/_post_list.html', posts=posts.items, next_url=next_url)

   
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(original_username=current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data

        if form.profile_image.data:
            filename = secure_filename(form.profile_image.data.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            form.profile_image.data.save(save_path)

            current_user.profile_image = unique_name

        db.session.commit()
        flash('Your changes have been saved.','success')
        return redirect(url_for('main.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',form=form)


@bp.route('/search')
@login_required
def search():  # Post.search() is an abstraction over Elasticsearch or full-text logic
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
        return render_template('partials/_post_list.html', posts=posts, next_url=next_url)

 
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash('User {username} not found.','warning')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(('You cannot follow yourself!','warning'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!','success')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.','warning')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(('You cannot unfollow yourself!','warning'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.','info')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/tag/<tag>')
@login_required
def posts_by_tag(tag):
    page = request.args.get('page', 1, type=int)
    query = (sa.select(Post).join(User, Post.user_id == User.id).where(
            Post.is_deleted == False,
            User.is_banned == False,
            Post.tag == tag
        )
        .order_by(Post.timestamp.desc())
    )

    posts = db.paginate(
        query,
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        next_url = url_for('main.posts_by_tag', tag=tag, page=posts.next_num) if posts.has_next else None
        return render_template('partials/_post_list.html', posts=posts.items, next_url=next_url)

    next_url = url_for('main.posts_by_tag', tag=tag, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.posts_by_tag', tag=tag, page=posts.prev_num) if posts.has_prev else None

    return render_template('tag_posts.html', posts=posts.items, tag=tag,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
    post=Post.query.get_or_404(id)

    if post.author != current_user:
        return
    
    form=PostForm()

    if request.method == 'GET':
        # manually prepopulating rather than obj
        form.process(obj=post)

    if form.validate_on_submit():
        post.body = form.body.data
        post.tag = form.tag.data

        if form.pic.data:
            filename = secure_filename(form.pic.data.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER_POST'], unique_name)
            form.pic.data.save(save_path)

            post.pic = unique_name

        db.session.commit()
        flash('Post Updated Successfully','success')
        return redirect(url_for('main.index'))
    
    return render_template('edit_post.html',form=form)


@bp.route('/react', methods=['POST'])
@login_required
def react():
    data = request.get_json()
    post_id = data.get('post_id')
    action = data.get('action')

    post = db.session.get(Post, post_id)

    if not post:
        return jsonify({'error': 'Post not found'}), 404

    existing = db.session.scalar(
        sa.select(Reaction)
        .where(Reaction.user_id == current_user.id, Reaction.post_id == post.id)
    )

    # Toggle reaction:
    #  - If same reaction exists, remove it (unreact)
    #  - If different reaction exists, update it
    #  - Else, create new reaction

    if existing:
        if existing.action == action:
            db.session.delete(existing)   
        else:
            existing.action = action
    else:
        new_reaction = Reaction(user_id=current_user.id, post_id=post.id, action=action)
        db.session.add(new_reaction)

    db.session.commit()

    

    cheers = db.session.scalar(
        sa.select(sa.func.count()).select_from(Reaction).where(
            Reaction.post_id == post.id,
            Reaction.action == 'cheer'
        )
    )
    boos = db.session.scalar(
        sa.select(sa.func.count()).select_from(Reaction).where(
            Reaction.post_id == post.id,
            Reaction.action == 'boo'
        )
    )

    return jsonify({'cheers': cheers, 'boos': boos})


@bp.route('/delete_post/<int:id>', methods=['POST'])
@login_required
def delete_post(id): # Soft delete: mark post as deleted instead of removing from DB
    post = Post.query.get_or_404(id)

   
    if post.author.id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    post.is_deleted = True
    db.session.commit()
    return jsonify({'success': True}), 200


@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_view(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        abort(404)

    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(comment_body=form.comment_body.data, comment_author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!','success')
        return redirect(url_for('main.post_view', post_id=post_id))

  
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(post_id=post_id) \
        .order_by(Comment.timestamp.desc()) \
        .paginate(page=page, per_page=5, error_out=False)

 
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        next_url = url_for('main.post_view', post_id=post_id, page=comments.next_num) \
            if comments.has_next else None
        return render_template('partials/_comments.html', comments=comments.items, next_url=next_url)

   
    next_url = url_for('main.post_view', post_id=post_id, page=comments.next_num) \
        if comments.has_next else None
    prev_url = url_for('main.post_view', post_id=post_id, page=comments.prev_num) \
        if comments.has_prev else None

    return render_template('post_view.html', post=post, form=form,
                           comments=comments, next_url=next_url, prev_url=prev_url)



@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = db.first_or_404(sa.select(User).where(User.username == recipient))
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,body=form.message.data)


        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent.','success')
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=('Send Message'),
                           form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.now(timezone.utc)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    query = current_user.messages_received.select().order_by(
        Message.timestamp.desc())
    messages = db.paginate(query, page=page,
                           per_page=current_app.config['POSTS_PER_PAGE'],
                           error_out=False)
    
    
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        next_url = url_for('main.messages', page=messages.next_num) if messages.has_next else None
        return render_template('partials/_messages.html', messages=messages.items, next_url=next_url)


    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    

    return render_template('messages.html', messages=messages.items,next_url=next_url, prev_url=prev_url)


@bp.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin():
        abort(403)

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You can't demote yourself.", "danger")
        return redirect(url_for('main.user', username=user.username))

    user.role = 'admin' if user.role != 'admin' else 'user'
    db.session.commit()

    flash(f"{user.username}'s role updated to {user.role}.", "success")
    return redirect(url_for('main.user', username=user.username))


@bp.route('/admin/toggle_ban/<int:user_id>', methods=['POST'])
@login_required
def toggle_ban(user_id):
    if not current_user.is_admin():
        abort(403)

    user = User.query.get_or_404(user_id)

    # Admin toggle logic:
    #  - Prevents self-demotion and admin banning for safety
    #  - Only 'user' and 'admin' roles are toggled

    if user.id == current_user.id:
        flash("You can't ban yourself.", "danger")
        return redirect(url_for('main.user', username=user.username))
    
    if user.role=='admin':
        flash("You can't ban an ADMIN.", "danger")
        return redirect(url_for('main.user', username=user.username))

    user.is_banned = not user.is_banned
    db.session.commit()

    flash(
        f"User '{user.username}' has been {'banned' if user.is_banned else 'unbanned'}.",
        "warning"
    )

    return redirect(url_for('main.user', username=user.username))


@bp.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():

    # Dashboard metrics:
    #  - Total users by role (admin/user)
    #  - Active users seen within the last 7 days
    # Paginated user table supports AJAX-based loading

    if not current_user.is_admin():
        abort(403)
   
    total_users = db.session.query(User.role, func.count(User.id)).group_by(User.role).all()

   
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    active_users = (
        db.session.query(func.count(User.id))
        .filter(User.last_seen != None)
        .filter(User.last_seen >= one_week_ago)
        .scalar() 
    )

   
    page = request.args.get('page', 1, type=int)
    
    users = User.query.order_by(User.last_seen.desc()).paginate(page=page, per_page=5, error_out=False)

    

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        next_url = url_for('main.admin_dashboard', page=users.next_num) if users.has_next else None
        return render_template('partials/_admin_table.html', users=users.items, next_url=next_url)
    
    next_url = url_for('main.admin_dashboard', page=users.next_num) if users.has_next else None
    prev_url = url_for('main.admin_dashboard', page=users.prev_num) if users.has_prev else None

    return render_template(
        'admin_dashboard.html',
        users=users.items,
        pagination=users,
        total_users=total_users,
        active_users=active_users,
        next_url=next_url,
        prev_url=prev_url
    )

