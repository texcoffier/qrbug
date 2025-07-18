"""
Defines a user of the app.
"""
from typing import TypeAlias
import html
import qrbug

UserId: TypeAlias = str

CHECK_VALID_LOGIN = True

class User(qrbug.Tree):
    """
    A user of the app.
    """
    instances: dict[UserId, "User"] = {}

    def _local_dump(self) -> str:
        return '()'

    @classmethod
    async def try_create_user(cls, request, login):
        if CHECK_VALID_LOGIN and (await qrbug.get_mail_from_login(login)) == qrbug.DEFAULT_EMAIL_TO:
            return f"<b>ERREUR :</b> L'utilisateur «{html.escape(login)}» n'a pas d'adresse mail valide, et ne sera donc pas créé."
        request.update_configuration(f'user_update({repr(login)})')


qrbug.User = User
qrbug.UserId = UserId
qrbug.user_update = User.update_attributes
qrbug.user_add = User.add_parenting_link
qrbug.user_remove = User.remove_parenting_link
