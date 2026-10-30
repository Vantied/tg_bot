from tg_bot.models.users import User
from tg_bot.crud.base import CRUDBase


class CRUDUser(CRUDBase[User]):
    """КРУД операции для user."""


user_crud = CRUDUser(User)
