from aiogram import F
from aiogram.enums import ChatType

IS_PRIVATE = F.chat.type == ChatType.PRIVATE
IS_GROUP = F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
