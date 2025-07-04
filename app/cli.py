import click
import subprocess
from flask.cli import with_appcontext

def register_cli(app):
    @app.cli.command("seed-admin")
    @with_appcontext
    def seed_admin():
      
        from app import db
        from app.models import User
        
        try:
           
            click.echo(" Running migrations...")
            subprocess.run(["flask", "db", "upgrade"], check=True)
            click.echo(" Migrations completed!")
            
            
            email = "admin@feelog.ac.in"
            if User.query.filter_by(email=email).first():
                click.echo(" Admin already exists. Skipping...")
                return

            # Create admin user
            click.echo(" Creating admin user...")
            admin = User(username="admin", email=email, role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

            click.echo(" Admin created: admin / admin123")
            
        except subprocess.CalledProcessError as e:
            click.echo(f" Migration failed: {e}")
        except Exception as e:
            click.echo(f" Error creating admin: {e}")
            db.session.rollback()