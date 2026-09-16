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

    @app.cli.command("send-test-email")
    @click.option("--to", required=True, help="Recipient email address")
    def send_test_email_command(to):
        """Send a test email to verify SMTP configuration."""
        from .services.email_service import send_email

        subject = "🧪 TaskNova Test Email Notification"
        html = f"""
        <div style="font-family:sans-serif;background:#0f172a;color:#f8fafc;padding:24px;border-radius:12px;">
            <h2 style="color:#6366f1;">TaskNova SMTP Service Verification</h2>
            <p>Congratulations! Your email service is properly configured and communicating with TaskNova.</p>
            <p>Recipient: <strong>{to}</strong></p>
        </div>
        """
        plain = f"TaskNova SMTP Service Verification\n\nYour email service is properly configured. Recipient: {to}"
        print(f"Attempting to send test email to {to}...")
        success, msg = send_email(to, subject, html, plain)
        if success:
            print(f"✅ Success: {msg}")
        else:
            print(f"❌ Failed: {msg}")

    @app.cli.command("test-digest-email")
    @click.option("--to", required=True, help="Recipient email address")
    @click.option("--name", default="Academic Scholar", help="Recipient full name")
    def test_digest_email_command(to, name):
        """Send a sample Daily Productivity Digest email to test formatting."""
        from .models.notification import _compute_digest_stats
        from .services.email_service import send_daily_digest_email

        from datetime import date
        sample_stats = _compute_digest_stats(12, 9, 1, date.today().isoformat())
        print(f"Sending sample Daily Digest email to {to} ({name})...")
        success, msg = send_daily_digest_email(to, name, sample_stats)
        if success:
            print(f"✅ Success: {msg}")
        else:
            print(f"❌ Failed: {msg}")


