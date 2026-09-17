import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr
from pathlib import Path

logger = logging.getLogger(__name__)

# Absolute paths so loading works regardless of the process working directory.
_BACKEND_DIR = Path(__file__).resolve().parents[2]


def _load_env_files():
    """Load .env.local then .env from the backend dir. Real host env vars win."""
    try:
        from dotenv import load_dotenv

        load_dotenv(_BACKEND_DIR / ".env.local", override=False)
        load_dotenv(_BACKEND_DIR / ".env", override=False)
    except Exception:
        pass


def _as_bool(value):
    if value is None:
        return False
    return value.strip().lower() in ("1", "true", "yes", "on")


def _get_mail_config():
    """Read mail configuration from the environment only (no hardcoded defaults)."""
    _load_env_files()
    port_raw = (os.getenv("MAIL_PORT") or "").strip()
    try:
        port = int(port_raw) if port_raw else 0
    except ValueError:
        port = 0
    return {
        "enabled": _as_bool(os.getenv("MAIL_ENABLED")),
        "server": (os.getenv("MAIL_SERVER") or "").strip(),
        "port": port,
        "use_tls": _as_bool(os.getenv("MAIL_USE_TLS")),
        "use_ssl": _as_bool(os.getenv("MAIL_USE_SSL")),
        "username": (os.getenv("MAIL_USERNAME") or "").strip(),
        "password": (os.getenv("MAIL_PASSWORD") or "").strip().replace(" ", ""),
        "sender": (os.getenv("MAIL_DEFAULT_SENDER") or "").strip(),
        "frontend_url": (os.getenv("APP_FRONTEND_URL") or "").strip(),
    }


def send_email(to_email, subject, html_content, text_content=None):
    """
    Send an email via standard / Gmail SMTP.
    Gracefully handles disabled email and exceptions without blocking caller.
    """
    cfg = _get_mail_config()
    if not cfg["enabled"]:
        logger.info("Email service disabled (MAIL_ENABLED=False). Skipping dispatch to %s.", to_email)
        return False, "Email service is disabled in configuration."

    if not cfg["username"] or not cfg["password"]:
        logger.warning("Email credentials missing (MAIL_USERNAME/MAIL_PASSWORD). Skipping dispatch to %s.", to_email)
        return False, "Missing SMTP username or password."

    if not cfg["server"] or not cfg["port"] or not cfg["sender"]:
        logger.warning("Incomplete SMTP configuration (MAIL_SERVER/MAIL_PORT/MAIL_DEFAULT_SENDER). Skipping dispatch to %s.", to_email)
        return False, "Incomplete SMTP configuration: set MAIL_SERVER, MAIL_PORT and MAIL_DEFAULT_SENDER."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = cfg["sender"]
        msg["To"] = to_email

        # Attach plain-text fallback
        if text_content:
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
        else:
            msg.attach(MIMEText("Please view this email in an HTML-compatible email client.", "plain", "utf-8"))

        # Attach styled HTML body
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        if cfg["use_ssl"]:
            server = smtplib.SMTP_SSL(cfg["server"], cfg["port"], timeout=15)
        else:
            server = smtplib.SMTP(cfg["server"], cfg["port"], timeout=15)
            if cfg["use_tls"]:
                server.starttls()

        server.login(cfg["username"], cfg["password"])
        # Envelope-from must be a bare address (SPF/DKIM align on it).
        # The display name stays only in the MIME From header above.
        _, envelope_from = parseaddr(cfg["sender"])
        if not envelope_from:
            envelope_from = cfg["username"]
        server.sendmail(envelope_from, [to_email], msg.as_string())
        server.quit()

        logger.info("Email successfully dispatched to %s with subject: '%s'", to_email, subject)
        return True, "Email sent successfully."
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to_email, str(e))
        return False, str(e)


def send_deadline_email(user_email, user_name, task_title, project_name, due_date_str, is_overdue=False):
    """
    Render and dispatch a branded deadline warning or overdue alert email.
    """
    cfg = _get_mail_config()
    app_url = cfg["frontend_url"]
    inbox_url = f"{app_url}/notifications"
    tasks_url = f"{app_url}/tasks"

    greeting_name = user_name or "Student"
    alert_badge = "OVERDUE ASSIGNMENT" if is_overdue else "DEADLINE WARNING"
    badge_bg = "#dc2626" if is_overdue else "#d97706"
    title_prefix = "🚨 Overdue" if is_overdue else "⏰ Due Soon"
    subject = f"{title_prefix}: {task_title} [{project_name}] - TaskNova"

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #0f172a; padding: 32px 16px;">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 580px; background-color: #1e293b; border: 1px solid #334155; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5);">
          <!-- Header Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%); padding: 28px 28px; text-align: left;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td>
                    <span style="display: inline-block; background-color: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; color: #ffffff; letter-spacing: 0.05em; text-transform: uppercase;">
                      TaskNova Academic Alert
                    </span>
                    <h1 style="margin: 8px 0 0 0; font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                      {title_prefix}
                    </h1>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Content Body -->
          <tr>
            <td style="padding: 28px;">
              <p style="margin: 0 0 16px 0; font-size: 15px; line-height: 1.5; color: #cbd5e1;">
                Hello <strong>{greeting_name}</strong>,
              </p>
              <p style="margin: 0 0 20px 0; font-size: 14px; line-height: 1.6; color: #94a3b8;">
                This is an automated academic deadline notification for your active coursework in <strong>TaskNova</strong>:
              </p>

              <!-- Task Card Pill -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #0f172a; border: 1px solid #334155; border-radius: 14px; padding: 18px; margin-bottom: 24px;">
                <tr>
                  <td>
                    <span style="display: inline-block; background-color: {badge_bg}; color: #ffffff; padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 800; text-transform: uppercase; margin-bottom: 8px;">
                      {alert_badge}
                    </span>
                    <h3 style="margin: 0 0 8px 0; font-size: 17px; font-weight: 700; color: #f8fafc;">
                      {task_title}
                    </h3>
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="font-size: 12px; color: #94a3b8;">
                      <tr>
                        <td style="padding: 4px 0;">📚 <strong>Course:</strong> {project_name}</td>
                      </tr>
                      <tr>
                        <td style="padding: 4px 0;">⏰ <strong>Target Due:</strong> <span style="color: {'#f87171' if is_overdue else '#fbbf24'}; font-weight: 700;">{due_date_str}</span></td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- Action Buttons -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 24px;">
                <tr>
                  <td align="center">
                    <a href="{tasks_url}" style="display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%); color: #ffffff; text-decoration: none; font-size: 14px; font-weight: 700; padding: 12px 24px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.4);">
                      Open Task Ledger & Checkpoints &rarr;
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin: 0; font-size: 12px; line-height: 1.5; color: #64748b; text-align: center;">
                You can manage your notification preferences anytime inside your <a href="{inbox_url}" style="color: #818cf8; text-decoration: underline;">TaskNova Inbox</a>.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #0f172a; padding: 16px 28px; border-top: 1px solid #334155; text-align: center; font-size: 11px; color: #64748b;">
              &copy; TaskNova Academic Workplace &bull; Empowering Focused Student Productivity
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    plain = f"""TaskNova Academic Alert: {title_prefix}

Hello {greeting_name},

{task_title} in {project_name} is due {due_date_str}.

Open TaskNova to update or complete your task:
{tasks_url}
"""
    return send_email(user_email, subject, html, plain)


def send_daily_digest_email(user_email, user_name, digest_data):
    """
    Render and dispatch a rich Daily Productivity Digest HTML email.
    """
    cfg = _get_mail_config()
    app_url = cfg["frontend_url"]
    inbox_url = f"{app_url}/notifications"

    greeting_name = user_name or "Student"
    date_str = digest_data.get("report_date") or "Today"
    total = digest_data.get("total_tasks", 0)
    completed = digest_data.get("completed_tasks", 0)
    in_prog = digest_data.get("in_progress_tasks", 0)
    overdue = digest_data.get("overdue_tasks", 0)
    rate = digest_data.get("completion_rate", 0)
    grade = digest_data.get("grade", "A")
    momentum = digest_data.get("momentum", "Active Progress")
    quote = digest_data.get("quote", "Consistent daily study sprints build unstoppable academic momentum.")

    subject = f"📊 Daily Productivity Digest - {date_str} (Grade {grade}) - TaskNova"

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #0b0f19; padding: 32px 16px;">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #131b2e; border: 1px solid #1e293b; border-radius: 24px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.6);">
          
          <!-- Top Gradient Accent -->
          <tr>
            <td style="background: linear-gradient(135deg, #4f46e5 0%, #6366f1 40%, #a855f7 75%, #ec4899 100%); padding: 32px 28px; text-align: left;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td>
                    <div style="display: inline-block; background-color: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700; color: #ffffff; letter-spacing: 0.05em; text-transform: uppercase;">
                      ✨ Daily Productivity Snapshot
                    </div>
                    <h1 style="margin: 10px 0 4px 0; font-size: 24px; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                      {date_str} Digest
                    </h1>
                    <p style="margin: 0; font-size: 13px; color: rgba(255,255,255,0.85); font-weight: 500;">
                      Prepared for {greeting_name} &bull; Academic Grade: <strong>{grade}</strong>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Main Content Area -->
          <tr>
            <td style="padding: 28px;">
              <!-- Momentum Banner -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background: linear-gradient(135deg, rgba(79, 70, 229, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 14px; padding: 16px; margin-bottom: 24px;">
                <tr>
                  <td>
                    <span style="font-size: 11px; font-weight: 700; color: #a5b4fc; text-transform: uppercase; letter-spacing: 0.05em;">
                      ⚡ Study Velocity: {momentum}
                    </span>
                    <p style="margin: 6px 0 0 0; font-size: 13px; font-style: italic; color: #e2e8f0; line-height: 1.5;">
                      "{quote}"
                    </p>
                  </td>
                </tr>
              </table>

              <!-- 4 KPI Metrics Grid (2x2 table) -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 24px;">
                <tr>
                  <!-- Metric 1: Total -->
                  <td width="48%" style="background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 14px; text-align: center;">
                    <div style="font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Total Workload</div>
                    <div style="font-size: 24px; font-weight: 800; color: #f8fafc; margin-top: 4px;">{total}</div>
                    <div style="font-size: 11px; color: #64748b;">tasks</div>
                  </td>
                  <td width="4%">&nbsp;</td>
                  <!-- Metric 2: Completed -->
                  <td width="48%" style="background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 14px; text-align: center;">
                    <div style="font-size: 10px; font-weight: 700; color: #34d399; text-transform: uppercase;">Completed</div>
                    <div style="font-size: 24px; font-weight: 800; color: #10b981; margin-top: 4px;">{completed}</div>
                    <div style="font-size: 11px; font-weight: 700; color: #34d399;">{rate}% achieved</div>
                  </td>
                </tr>
                <tr><td height="12" colspan="3"></td></tr>
                <tr>
                  <!-- Metric 3: In Progress -->
                  <td width="48%" style="background-color: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px; padding: 14px; text-align: center;">
                    <div style="font-size: 10px; font-weight: 700; color: #818cf8; text-transform: uppercase;">In Progress</div>
                    <div style="font-size: 24px; font-weight: 800; color: #6366f1; margin-top: 4px;">{in_prog}</div>
                    <div style="font-size: 11px; color: #818cf8;">active assignments</div>
                  </td>
                  <td width="4%">&nbsp;</td>
                  <!-- Metric 4: Overdue -->
                  <td width="48%" style="background-color: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 12px; padding: 14px; text-align: center;">
                    <div style="font-size: 10px; font-weight: 700; color: #fb7185; text-transform: uppercase;">Overdue</div>
                    <div style="font-size: 24px; font-weight: 800; color: #f43f5e; margin-top: 4px;">{overdue}</div>
                    <div style="font-size: 11px; color: #fb7185;">urgent action</div>
                  </td>
                </tr>
              </table>

              <!-- Progress Bar -->
              <div style="margin-bottom: 28px;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 6px; font-size: 11px; color: #94a3b8;">
                  <tr>
                    <td>Completion Progress</td>
                    <td align="right" style="font-weight: 700; color: #f8fafc;">{rate}%</td>
                  </tr>
                </table>
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #1e293b; border-radius: 9999px; height: 8px; overflow: hidden;">
                  <tr>
                    <td width="{min(100, max(0, rate))}%" style="background: linear-gradient(90deg, #6366f1, #10b981); height: 8px; border-radius: 9999px;"></td>
                    <td width="{max(0, 100 - min(100, max(0, rate)))}%"></td>
                  </tr>
                </table>
              </div>

              <!-- CTA Button -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 16px;">
                <tr>
                  <td align="center">
                    <a href="{inbox_url}" style="display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: #ffffff; text-decoration: none; font-size: 14px; font-weight: 700; padding: 14px 28px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);">
                      View Interactive Digest & Course Breakdown &rarr;
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #0b0f19; padding: 18px 28px; border-top: 1px solid #1e293b; text-align: center; font-size: 11px; color: #64748b;">
              &copy; TaskNova Academic Workplace &bull; Sent to {user_email}
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    plain = f"""TaskNova Daily Productivity Digest - {date_str} (Grade {grade})

Hello {greeting_name},

Here is your daily study workload summary:
- Total Workload: {total} tasks
- Completed: {completed} tasks ({rate}%)
- In Progress: {in_prog} tasks
- Overdue: {overdue} tasks
- Momentum: {momentum}

"{quote}"

View your interactive digest and course breakdown:
{inbox_url}
"""
    return send_email(user_email, subject, html, plain)
