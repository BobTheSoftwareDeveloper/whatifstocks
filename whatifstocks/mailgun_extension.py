from flask_mailgun import Mailgun as MailgunBase


class Mailgun(MailgunBase):
    def init_app(self, app):
        error_subject_template = app.config[
            'MAIL_ERROR_SUBJECT_TEMPLATE']

        self.error_subject_withexcinfo_template = (
            error_subject_template.format(
                app.config['SITE_NAME'], '{exc_info}'))

        self.error_subject_withoutexcinfo_template = (
            error_subject_template.format(
                app.config['SITE_NAME'],
                '{levelname}: {pathname}:{lineno}'))

        super(Mailgun, self).init_app(app)
