from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_welcome_email(user):
    msg_html = render_to_string(
        'emails/welcome.html',
        {'user': user, 'BASE_URL': settings.BASE_URL}
    )

    send_mail(
        'Welcome to Dots',
        msg_html,
        settings.SENDER_EMAIL,
        [user.email],
        html_message=msg_html,
    )
