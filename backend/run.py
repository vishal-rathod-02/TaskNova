import os
import click
from app import create_app
from app.extensions import db
from app.models import User

app = create_app()


@app.cli.command("seed")
@click.option("--name", default=None, help="Admin Full Name")
@click.option("--email", default=None, help="Admin Email Address")
@click.option("--password", default=None, help="Admin Password")
def seed(name, email, password):
    admin_name = name or os.getenv("ADMIN_NAME", "System Admin")
    admin_email = (email or os.getenv("ADMIN_EMAIL", "admin@tasknova.com")).lower().strip()
    admin_password = password or os.getenv("ADMIN_PASSWORD", "admin123")

    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(full_name=admin_name, email=admin_email, role="admin")
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created: {admin_email} ({admin_name})")
    else:
        admin.full_name = admin_name
        admin.set_password(admin_password)
        admin.role = "admin"
        db.session.commit()
        print(f"Admin user updated: {admin_email} ({admin_name})")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
