"""Backend de autenticación que acepta username o email indistintamente (spec §3.1).

El objetivo es que el mensaje de error sea idéntico en ambos casos para no
permitir enumeración de cuentas (ver spec §8).
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between "user does not exist" and "wrong password".
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Username duplicado shouldn’t happen (username is unique), pero si
            # el email coincide con el username de otro usuario, no adivinamos.
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None