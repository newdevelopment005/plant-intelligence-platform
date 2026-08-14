import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable

import structlog

from app.config import settings

logger = structlog.get_logger()


def is_email_enabled(smtp: dict | None = None) -> bool:
    if smtp:
        return bool(smtp.get("host") and smtp.get("user") and smtp.get("password"))
    return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD)


def _smtp_from(smtp: dict | None = None) -> str:
    if smtp and smtp.get("from"):
        return smtp["from"]
    if smtp and smtp.get("user"):
        return smtp["user"]
    if settings.SMTP_FROM and settings.SMTP_FROM != "noreply@pip-platform.org":
        return settings.SMTP_FROM
    if settings.SMTP_USER:
        return settings.SMTP_USER
    return "noreply@pip-platform.org"


def _smtp_config(smtp: dict | None = None) -> dict | None:
    """Return the effective SMTP config dict, or None when nothing is usable."""
    if smtp:
        return smtp
    if is_email_enabled():
        return {
            "host": settings.SMTP_HOST,
            "port": int(settings.SMTP_PORT or 587),
            "user": settings.SMTP_USER,
            "password": settings.SMTP_PASSWORD,
            "from": _smtp_from(),
        }
    return None


async def resolve_smtp_for_user(db, user_id: str | None) -> dict | None:
    """Resolve a user's department SMTP settings, or None to fall back to the
    platform-wide (admin) SMTP config."""
    if not user_id:
        return None
    from app.modules.auth.infrastructure.repositories import UserRepository
    from app.modules.department.infrastructure.repositories import DepartmentRepository

    user = await UserRepository(db).get_by_id(user_id)
    if not user or not user.department_id:
        return None
    dept = await DepartmentRepository(db).get_by_id(str(user.department_id))
    if not dept or not (dept.smtp_host and dept.smtp_user and dept.smtp_password):
        return None
    return {
        "host": dept.smtp_host,
        "port": int(dept.smtp_port or 587),
        "user": dept.smtp_user,
        "password": dept.smtp_password,
        "from": dept.smtp_from or dept.smtp_user,
    }


def send_email(
    to_emails: str | Iterable[str],
    subject: str,
    html: str | None = None,
    text: str | None = None,
    smtp: dict | None = None,
) -> bool:
    """Best-effort email delivery.

    When ``smtp`` is provided (per-department config) it overrides the global
    SMTP settings. When no usable SMTP config exists the message is logged and
    ``False`` is returned so callers can surface the problem.
    """
    if isinstance(to_emails, str):
        to_emails = [to_emails]
    to_emails = [e.strip() for e in to_emails if e and e.strip()]
    if not to_emails:
        logger.warning("send_email called without recipients; skipping")
        return False

    config = _smtp_config(smtp)
    if not config:
        logger.warning(
            "smtp_not_configured",
            subject=subject,
            to=to_emails,
            hint="Add SMTP_USER/SMTP_PASSWORD to .env or configure department SMTP settings",
        )
        return False

    sender = config.get("from") or config.get("user") or "noreply@pip-platform.org"
    host = config["host"]
    port = int(config.get("port") or 587)
    user = config["user"]
    password = config["password"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(to_emails)
    if text:
        msg.attach(MIMEText(text, "plain"))
    if html:
        msg.attach(MIMEText(html, "html"))

    try:
        context = ssl.create_default_context()
        if port == 465:
            # Implicit TLS (e.g. Gmail SMTP_SSL)
            with smtplib.SMTP_SSL(host, port, timeout=15, context=context) as server:
                server.login(user, password)
                server.sendmail(sender, to_emails, msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.ehlo()
                if port == 587:
                    server.starttls(context=context)
                    server.ehlo()
                server.login(user, password)
                server.sendmail(sender, to_emails, msg.as_string())
        logger.info("email_sent", subject=subject, to=to_emails, smtp_host=host)
        return True
    except Exception:
        logger.exception("email_failed", subject=subject, to=to_emails, smtp_host=host)
        return False


def send_share_notification(
    to_email: str,
    sharer_name: str,
    item_type: str,
    item_id: str,
    permission: str,
    base_url: str,
    smtp: dict | None = None,
) -> bool:
    return send_email(
        to_email,
        subject=f"{sharer_name} shared a {item_type} with you",
        html=(
            "<p>Hi,</p>"
            f"<p><strong>{sharer_name}</strong> shared a {item_type} "
            f"(<code>{item_id}</code>) with you "
            f"with <strong>{permission}</strong> access.</p>"
            f'<p><a href="{base_url}/shared">View shared items</a></p>'
        ),
        text=(
            f"{sharer_name} shared a {item_type} ({item_id}) with you "
            f"with {permission} access."
        ),
        smtp=smtp,
    )


def send_team_invite_email(
    to_email: str,
    inviter_name: str,
    team_name: str,
    role: str,
    base_url: str,
    smtp: dict | None = None,
) -> bool:
    return send_email(
        to_email,
        subject=f"Invitation to join team {team_name}",
        html=(
            "<p>Hi,</p>"
            f"<p><strong>{inviter_name}</strong> has invited you to join the team "
            f"<strong>{team_name}</strong> as {role} on the Plant Intelligence Platform.</p>"
            f'<p>If you don\'t yet have an account, '
            f'<a href="{base_url}/register?email={to_email}">register here</a>.</p>'
            f'<p><a href="{base_url}/teams">View your teams</a></p>'
        ),
        text=(
            f"{inviter_name} has invited you to join the team {team_name} as {role}. "
            f"Visit {base_url}/teams to respond."
        ),
        smtp=smtp,
    )


def send_verification_email(
    to_email: str,
    user_name: str,
    verify_token: str,
    base_url: str,
    smtp: dict | None = None,
) -> bool:
    verify_url = f"{base_url}/verify?token={verify_token}"
    return send_email(
        to_email,
        subject="Verify your email",
        html=(
            "<p>Hi,</p>"
            f"<p>Welcome to the Plant Intelligence Platform{', ' + user_name if user_name else ''}!</p>"
            "<p>Please confirm your email address by clicking the link below. "
            "The link expires in 24 hours.</p>"
            f'<p><a href="{verify_url}">Verify your email</a></p>'
            f"<p>If the button doesn't work, copy and paste this URL into your browser:</p>"
            f"<p>{verify_url}</p>"
        ),
        text=(
            f"Welcome to the Plant Intelligence Platform{', ' + user_name if user_name else ''}! "
            f"Verify your email by visiting: {verify_url} (expires in 24 hours)."
        ),
        smtp=smtp,
    )


def send_share_invite_to_unresolved(
    to_email: str,
    sharer_name: str,
    item_type: str,
    base_url: str,
    smtp: dict | None = None,
) -> bool:
    """Notify a person who does not have an account yet that something was shared with them."""
    return send_email(
        to_email,
        subject=f"{sharer_name} shared a {item_type} with you",
        html=(
            "<p>Hi,</p>"
            f"<p><strong>{sharer_name}</strong> shared a {item_type} with you on the "
            "Plant Intelligence Platform, but you don't have an account yet.</p>"
            f'<p>Register with this email address to claim the shared {item_type}: '
            f'<a href="{base_url}/register?email={to_email}">register here</a>.</p>'
            f'<p><a href="{base_url}/shared">View shared items</a></p>'
        ),
        text=(
            f"{sharer_name} shared a {item_type} with you on the Plant Intelligence Platform. "
            f"Register at {base_url}/register to claim it."
        ),
        smtp=smtp,
    )


def send_password_reset(
    to_email: str,
    reset_token: str,
    base_url: str,
    smtp: dict | None = None,
) -> bool:
    reset_url = f"{base_url}/reset-password?token={reset_token}"
    return send_email(
        to_email,
        subject="Reset your password",
        html=(
            "<p>Hi,</p>"
            "<p>We received a request to reset your password for the "
            "Plant Intelligence Platform. Click the link below to set a new one. "
            "The link expires in 1 hour.</p>"
            f'<p><a href="{reset_url}">Reset your password</a></p>'
            f"<p>If the button doesn't work, copy and paste this URL into your browser:</p>"
            f"<p>{reset_url}</p>"
            "<p>If you didn't request this, you can safely ignore this email.</p>"
        ),
        text=(
            f"Reset your password by visiting: {reset_url} "
            "(expires in 1 hour). If you didn't request this, ignore this email."
        ),
        smtp=smtp,
    )


def send_meeting_reminder(
    to_email: str,
    meeting_title: str,
    starts_at_iso: str,
    location: str | None,
    base_url: str,
    smtp: dict | None = None,
) -> bool:
    where = f"<p><strong>Where:</strong> {location}</p>" if location else ""
    return send_email(
        to_email,
        subject=f"Reminder: {meeting_title}",
        html=(
            "<p>Hi,</p>"
            f"<p>A reminder for your upcoming meeting <strong>{meeting_title}</strong> "
            f"scheduled for <strong>{starts_at_iso}</strong>.</p>"
            f"{where}"
            f'<p><a href="{base_url}/meetings">Open meetings</a></p>'
        ),
        text=(
            f"Reminder: {meeting_title} scheduled for {starts_at_iso}."
        ),
        smtp=smtp,
    )


def send_meeting_invite(
    to_email: str,
    inviter_name: str,
    meeting_title: str,
    starts_at_iso: str,
    location: str | None,
    base_url: str,
    smtp: dict | None = None,
) -> bool:
    where = f"<p><strong>Where:</strong> {location}</p>" if location else ""
    return send_email(
        to_email,
        subject=f"Invitation: {meeting_title}",
        html=(
            "<p>Hi,</p>"
            f"<p><strong>{inviter_name}</strong> invited you to the meeting "
            f"<strong>{meeting_title}</strong> scheduled for <strong>{starts_at_iso}</strong>.</p>"
            f"{where}"
            f'<p><a href="{base_url}/meetings">View meetings</a></p>'
        ),
        text=(
            f"{inviter_name} invited you to the meeting {meeting_title} scheduled for {starts_at_iso}."
        ),
        smtp=smtp,
    )
