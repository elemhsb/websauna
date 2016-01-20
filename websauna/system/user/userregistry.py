"""Default user object generator."""

from sqlalchemy import func
from websauna.system.user.interfaces import IUserRegistry, IUser
from websauna.system.user.usermixin import UserMixin, GroupMixin
from websauna.system.user.utils import get_user_class, get_activation_model

from websauna.compat.typing import Optional
from websauna.compat.typing import List
from websauna.compat.typing import Tuple
from zope.interface import implementer


@implementer(IUserRegistry)
class DefaultEmailBasedUserRegistry:
    """Default user backend which uses SQLAlchemy to store User models.

    Provides default user actions
    """

    def __init__(self, request):
        self.dbsession = request.dbsession
        self.registry = request.registry

    @property
    def User(self):
        """Currently configured User SQLAlchemy model."""
        return get_user_class(self.registry)

    @property
    def Activation(self):
        """Currently configured User SQLAlchemy model."""
        return get_activation_model(self.registry)

    def verify_password(self, user, password):
        """Validate user password."""
        return user.verify_password(password)

    def get_by_username(self, username):
        return self.dbsession.query(self.User).filter(func.lower(self.User.username) == username.lower()).first()

    def get_by_email(self, email):
        return self.dbsession.query(self.User).filter(func.lower(self.User.email) == email.lower()).first()

    def get_by_activation(self, activation):
        pass

    def can_login(self, user):
        return user.can_login()

    def get_groups(self, user) -> List[GroupMixin]:
        return user.groups

    def create_password_reset_token(self, email) -> str:
        """Sets password reset token for user.

        :return: User and his password reset token or ``None`` if user is disabled or is not email login based.
        """
        user = self.get_by_email(email)
        assert user, "Got password reset request for non-existing email".format(email)

        if not self.can_login(user):
            return None

        activation = self.Activation()
        self.dbsession.add(activation)
        self.dbsession.flush()
        user.activation = activation

        assert user.activation.code, "Could not generate the password reset code"

        return user, activation.code

    def get_authenticated_user_by_username(self, username, password) -> Optional[UserMixin]:
        """Authenticate incoming user.

        :return: User instance of none if password does not match
        """
        user = self.get_by_username(username)
        if user and self.verify_password(user, password):
            return user
        return None

    def get_authenticated_user_by_email(self, email, password) -> Optional[UserMixin]:
        user = self.get_by_email(email)
        if user and self.verify_password(user, password):
            return user
        return None

    def get_session_token(self, user):
        """Get marker string we use to store reference to this user in authenticated session."""
        return user.id

    def get_user_by_session_token(self, token: str):
        """Resolve the authenticated user by a session token reference."""
        return self.dbsession.query(self.User).get(token)
