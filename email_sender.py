from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import get_config


def send_email(subject: str, html_body: str, to: str | None = None) -> str:
    cfg = get_config()
    cfg.validate_email()
    recipient = to or cfg.email_to
    if not recipient:
        raise ValueError("수신 이메일 주소가 없습니다.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = cfg.email_from
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as server:
        server.starttls()
        server.login(cfg.smtp_user, cfg.smtp_password)
        server.sendmail(cfg.email_from, [recipient], msg.as_string())

    return recipient
