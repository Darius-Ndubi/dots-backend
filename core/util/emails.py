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


def send_activation_email(user, activation):
    msg_html = render_to_string(
        'emails/activation.html',
        {'user': user, 'BASE_URL': settings.BASE_URL,
         'activation_key': activation.key}
    )

    send_mail(
        'Verify Your Email',
        msg_html,
        settings.SENDER_EMAIL,
        [user.email],
        html_message=msg_html,
    )


def send_invitation_email(invitation):
    msg_html = render_to_string(
        'emails/invitation.html',
        {'BASE_URL': settings.BASE_URL,
         'invitation': invitation}
    )

    send_mail(
        'Dots Workspace Invitation',
        msg_html,
        settings.SENDER_EMAIL,
        [invitation.email],
        html_message=msg_html,
    )


def send_password_reset_email(user, reset_token):
    msg_html = render_to_string(
        'emails/password_reset.html',
        {'user': user, 'BASE_URL': settings.BASE_URL,
         'reset_key': reset_token.key}
    )

    send_mail(
        'Reset Your Password',
        msg_html,
        settings.SENDER_EMAIL,
        [user.email],
        html_message=msg_html,
    )
