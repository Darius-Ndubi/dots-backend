import random
import string
import hashlib

from core.models import UserActivation, PasswordResetToken


def random_string(string_length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def create_activation_key(user):
    activation = UserActivation.objects.filter(user=user).first()
    if activation:
        return activation

    key = '{}-{}-{}'.format(user.id, user.email, random_string(8))
    hash_object = hashlib.md5(key.encode())
    key = hash_object.hexdigest()
    return UserActivation.objects.create(user=user, key=key)


def create_invitation_key(email, workspace_id):
    key = '{}-{}-{}'.format(workspace_id, email, random_string(8))
    hash_object = hashlib.md5(key.encode())
    return hash_object.hexdigest()


def create_password_reset_key(user):
    reset_token = PasswordResetToken.objects.filter(user=user).first()
    if reset_token:
        return reset_token

    key = '{}-{}-{}'.format(user.id, user.email, random_string(8))
    hash_object = hashlib.md5(key.encode())
    key = hash_object.hexdigest()
    return PasswordResetToken.objects.create(user=user, key=key)
