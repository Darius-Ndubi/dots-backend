from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class DotsAuthBackend:
    def authenticate(self, request, username=None, password=None):
        user = User.objects.filter(Q(email__iexact=username) | Q(username__iexact=username)).first()
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        return User.objects.filter(pk=user_id).first()
