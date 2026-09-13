import os
import click
from .extensions import db
from .models import User


def register_commands(app):
    @app.cli.command("seed")
    @click.option("--name", default=None, help="Admin Full Name")
    @click.option("--email", default=None, help="Admin Email Address")
    @click.option("--password", default=None, help="Admin Password")
    def seed_command(name, email, password):
        """Seed or update the administrator account."""
        admin_name = name or os.getenv("ADMIN_NAME", "System Admin")
        admin_email = (email or os.getenv("ADMIN_EMAIL", "admin@tasknova.com")).lower().strip()
        admin_password = password or os.getenv("ADMIN_PASSWORD", "admin123")

        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(full_name=admin_name, email=admin_email, role="admin")
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin account created successfully: {admin_email} ({admin_name})")
        else:
            admin.full_name = admin_name
            admin.set_password(admin_password)
            admin.role = "admin"
            db.session.commit()
            print(f"Admin account updated successfully: {admin_email} ({admin_name})")

    @app.cli.command("run-jobs")
    def run_jobs_command():
        """Run deadline reminders and daily productivity digest calculation."""
        from .tasks_jobs.tasks import run_daily_productivity_report, run_deadline_reminders

        print("Checking deadlines and sending reminders...")
        reminders = run_deadline_reminders()
        print(f"Reminders result: {reminders}")

        print("Generating daily productivity reports...")
        reports = run_daily_productivity_report()
        print(f"Daily reports result: {reports}")
        print("Background jobs completed successfully.")

