import smtplib
import ssl
from email.message import EmailMessage


class SmtpEmailSender:
    def __init__(self, host: str, port: int, username: str, password: str,
                 from_name: str = "Christmas Gift Shuffle"):
        self._host, self._port = host, port
        self._username, self._password = username, password
        self._from_name = from_name

    def _connect(self) -> smtplib.SMTP:
        context = ssl.create_default_context()
        if self._port == 465:
            return smtplib.SMTP_SSL(self._host, self._port, context=context, timeout=20)
        smtp = smtplib.SMTP(self._host, self._port, timeout=20)
        smtp.starttls(context=context)
        return smtp

    def send(self, to: str, subject: str, text: str, html: str | None = None) -> None:
        msg = EmailMessage()
        msg["From"] = f"{self._from_name} <{self._username}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(text)
        if html:
            msg.add_alternative(html, subtype="html")
        with self._connect() as smtp:
            smtp.login(self._username, self._password)
            smtp.send_message(msg)