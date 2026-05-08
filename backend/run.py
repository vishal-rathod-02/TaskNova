from app import create_app
from app.extensions import db
from app.models import User

app = create_app()


@app.cli.command("seed")
def seed():
    admin_email = "admin@tasknova.com"
    if not User.query.filter_by(email=admin_email).first():
        admin = User(full_name="System Admin", email=admin_email, role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@tasknova.com / admin123")
    else:
        print("Admin user already exists")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
