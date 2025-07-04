from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

db.drop_all()
db.create_all()

admin = User(
    username='admin',
    email='admin@feelog.ac.in',
    role='admin' 
)
admin.set_password('your_password')

db.session.add(admin)
db.session.commit()

print("Admin user created: admin@feelog.ac.in / your_password")
