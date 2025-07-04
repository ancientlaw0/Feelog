import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))




class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this_is_the_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/profile_pics')
    UPLOAD_FOLDER_POST = os.path.join(basedir, 'app/static/post')
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024
    POSTS_PER_PAGE=3
    COMMENTS_PER_PAGE=3
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL') or  "http://localhost:9200"
   
    TAG_CHOICES = [ # Tag choices to be added in a post - default is uncategorized (if not chosen)
    ('', 'Uncategorized'),
    ('AI', 'AI'),
    ('Art', 'Art'),
    ('Blog Post', 'Blog Post'),
    ('Creative', 'Creative'),
    ('Cybersecurity', 'Cybersecurity'),
    ('Design', 'Design'),
    ('Entrepreneurship', 'Entrepreneurship'),
    ('Fashion', 'Fashion'),
    ('Fitness', 'Fitness'),
    ('Food', 'Food'),
    ('Gadgets', 'Gadgets'),
    ('Health', 'Health'),
    ('Leadership', 'Leadership'),
    ('Management', 'Management'),
    ('Music', 'Music'),
    ('News', 'News'),
    ('Photography', 'Photography'),
    ('Random', 'Random'),
    ('Sports', 'Sports'),
    ('Startup', 'Startup'),
    ('Technology', 'Technology'),
    ('Travel', 'Travel'),
    ('Writing', 'Writing')]



    ALLOWED_DOMAINS = {
    'gmail.com', 'outlook.com', 'hotmail.com', 'live.com', 'protonmail.com',
    'yahoo.com', 'icloud.com', 'mail.com',
    'lnmiit.ac.in', 'rediffmail.com'
    }


    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = os.environ.get('ADMINS', 'feelog.project@gmail.com').split(',') 