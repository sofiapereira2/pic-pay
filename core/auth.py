from django.http import HttpRequest
from ninja.security import HttpBearer
import jwt
from django.conf import settings
from users.models import User


class InvalidToken(Exception):
    pass


class JWTAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        try:
            data = jwt.decode(token, settings.SECRET_KEY_JWT,
                              algorithms='HS256')
        except jwt.exceptions.ExpiredSignatureError:
            raise InvalidToken('Token is expired.')
        except Exception:
            raise InvalidToken('Token is not valid.')

        user = User.objects.filter(username=data['user']).first()
        if user:
            return user.id

        raise InvalidToken('Invalid Token')
