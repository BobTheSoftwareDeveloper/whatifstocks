"""Helper utilities and decorators."""
from flask import current_app as app
from flask_mail import Message

from whatifstocks.extensions import mail, mailgun


def send_mail(
        sender=None, recipients=None, subject=None, body=None,
        is_log_msg=True):
    """Send mail using either Flask-Mail or Flask-Mailgun."""
    if is_log_msg:
        log_msg = 'Email sent by site\n'
        log_msg += 'From: <{0}>\n'.format(sender)
        log_msg += 'To: {0}\n'.format(recipients)
        log_msg += 'Subject: {0}\n'.format(subject)
        log_msg += body

        app.logger.info(log_msg)

    if app.debug:
        return

    if (
            app.config.get('MAILGUN_DOMAIN') and
            app.config.get('MAILGUN_KEY')):
        msg = dict(
            from_=sender,
            to=recipients,
            subject=subject,
            text=body)

        mailgun.send(**msg)
    else:
        msg = Message(
            subject,
            sender=sender,
            recipients=recipients)
        msg.body = body

        mail.send(msg)
