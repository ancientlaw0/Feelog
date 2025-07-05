from typing import Optional
from app import login,db
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from app.search import add_to_index, remove_from_index, query_index
import jwt
from time import time
from flask import current_app
from elasticsearch.exceptions import NotFoundError

# Reorder results based on Elasticsearch match order using CASE WHEN.
class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        cls.check_and_reindex_if_needed()  # Ensures index exists before querying
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        return db.session.scalars(query), total
    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

        # Store object changes before commit so we can sync them to the search index after DB commit.
        # Required because SQLAlchemy's 'after_commit' doesn't have access to new objects directly.

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls): # Re-index all existing records into Elasticsearch, e.g. after index deletion or schema changes.
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(cls.__tablename__, obj)

    @classmethod # solving not indexed error by auto reindexing
    def check_and_reindex_if_needed(cls):
        if not current_app.elasticsearch:
            current_app.logger.warning("Elasticsearch not configured.")
            return

        index_name = cls.__tablename__
        try:
            current_app.elasticsearch.indices.get(index=index_name)
        except NotFoundError:
            current_app.logger.warning(f"Index '{index_name}' not found. Reindexing...")
            cls.reindex()
        except Exception as e:
            current_app.logger.warning(f"Could not verify index '{index_name}': {e}")


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

followers = sa.Table('followers',db.metadata,sa.Column('follower_id',sa.Integer,sa.ForeignKey('user.id'),primary_key=True),
                                            sa.Column('followed_id',sa.Integer,sa.ForeignKey('user.id'),primary_key=True))

class User(UserMixin,db.Model): 
    id:so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(50), index=True,unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(125),index=True,unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    last_message_read_time: so.Mapped[Optional[datetime]]

    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    
    profile_image: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128), nullable=True)

    role = db.Column(db.String(10), default='user')
    is_banned = db.Column(db.Boolean, default=False, nullable=False)


    
    posts:so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    reactions: so.WriteOnlyMapped['Reaction'] = so.relationship(back_populates='user')
    comments: so.WriteOnlyMapped['Comment'] = so.relationship(back_populates='comment_author',lazy='dynamic')
    
    messages_sent: so.WriteOnlyMapped['Message'] = so.relationship(
        foreign_keys='Message.sender_id', back_populates='author')
    
    messages_received: so.WriteOnlyMapped['Message'] = so.relationship(
        foreign_keys='Message.recipient_id', back_populates='recipient')
    
   
    def is_admin(self):
        return self.role == 'admin'

    
    def set_password(self,password):
            self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
         return check_password_hash(self.password_hash,password)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    following: so.WriteOnlyMapped['User'] = so.relationship(secondary=followers, primaryjoin=(followers.c.follower_id == id),secondaryjoin=(followers.c.followed_id == id),back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(secondary=followers, primaryjoin=(followers.c.followed_id == id),secondaryjoin=(followers.c.follower_id == id),back_populates='following')


    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        return db.session.scalar(
            sa.select(sa.func.count()).select_from(followers).where(
                followers.c.followed_id == self.id
            )
        )

    def following_count(self):
        return db.session.scalar(
            sa.select(sa.func.count()).select_from(followers).where(
                followers.c.follower_id == self.id
            )
        )
    
    def following_posts(self): # Returns a query of posts from users this user follows (including their own),
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
                sa.select(Post)
               
                .join(Post.author.of_type(Author))
                .join(Author.followers.of_type(Follower), isouter=True)
                .where(sa.or_(
                    Follower.id == self.id,
                    Author.id == self.id
                ))
                .group_by(Post)
                .order_by(Post.timestamp.desc())
                )
    

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    def unread_message_count(self): # Counts messages received after the last read time to show unread badge .
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        query = sa.select(Message).where(Message.recipient == self, Message.timestamp > last_read_time)
        return db.session.scalar(sa.select(sa.func.count()).select_from(
            query.subquery()))
    

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return db.session.get(User, id)

class Post(SearchableMixin,db.Model):
    __searchable__ = ['body']   
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(200))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True,default=lambda:datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),index=True)
    author: so.Mapped[User] = so.relationship(back_populates='posts')
    tag: so.Mapped[Optional[str]] = so.mapped_column(db.String(30), index=True, default=None)
    is_deleted: so.Mapped[bool] = so.mapped_column(default=False,server_default=sa.text("0"),nullable=False)
    pic: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255), nullable=True)
    
    reactions: so.WriteOnlyMapped['Reaction'] = so.relationship(back_populates='post',lazy='dynamic')
    comments: so.WriteOnlyMapped['Comment'] = so.relationship(back_populates='post',lazy='dynamic')

    @property 
    def cheer_count(self):
        return db.session.scalar(
            sa.select(sa.func.count()).select_from(Reaction).where(
                Reaction.post_id == self.id, Reaction.action == 'cheer'
            )
        )

    @property
    def boo_count(self):
        return db.session.scalar(
            sa.select(sa.func.count()).select_from(Reaction).where(
                Reaction.post_id == self.id, Reaction.action == 'boo'
            )
        )

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
class Reaction(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    post_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('post.id'), nullable=False) 
    action: so.Mapped[str] = so.mapped_column(sa.String(10))

    user: so.Mapped['User'] = so.relationship(back_populates='reactions')
    post: so.Mapped['Post'] = so.relationship(back_populates='reactions')

    __table_args__ = (
        sa.UniqueConstraint('user_id', 'post_id', name='unique_user_post_reaction'),
    )

    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Comment(db.Model):
    id:so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False) 
    post_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('post.id'), nullable=False)
    comment_body: so.Mapped[str] = so.mapped_column(sa.String(100))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True,default=lambda:datetime.now(timezone.utc))

    comment_author: so.Mapped['User'] = so.relationship(back_populates='comments')
    post: so.Mapped['Post'] = so.relationship(back_populates='comments')

class Message(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    sender_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                                 index=True)
    recipient_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                                    index=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))


    author: so.Mapped[User] = so.relationship(
        foreign_keys='Message.sender_id',
        back_populates='messages_sent')
    

    recipient: so.Mapped[User] = so.relationship(
        foreign_keys='Message.recipient_id',
        back_populates='messages_received')
    
    
    
