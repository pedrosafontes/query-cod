from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import BaseUserManager


if TYPE_CHECKING:
    from users.models import User


class UserManager(BaseUserManager['User']):
    def create_user(self, email: str, password: str | None = None, **kwargs: Any) -> 'User':
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs: Any) -> 'User':
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user
