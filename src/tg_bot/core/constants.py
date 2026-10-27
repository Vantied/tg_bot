# Модели: порядок колонок
# Колонки с меньшим значением идут в таблице раньше остальных (по умолчанию 0).
PRIMARY_KEY_SORT_ORDER = -1

# Пользователь
USER_FULL_NAME_MAX_LENGTH = 255

# Расписание
SCHEDULE_TITLE_MAX_LENGTH = 64
TIMEZONE_MAX_LENGTH = 64
DEFAULT_TIMEZONE = 'Europe/Moscow'
FIRST_WEEK = 1
SECOND_WEEK = 2

# Занятие
LESSON_SUBJECT_MAX_LENGTH = 128
LESSON_ROOM_MAX_LENGTH = 32
LESSON_TEACHER_MAX_LENGTH = 128
# Дни недели в формате date.weekday(): 0 - понедельник, 6 - воскресенье.
MONDAY = 0
SUNDAY = 6

# Чат
CHAT_TITLE_MAX_LENGTH = 255

# Команды бота: (команда, описание).
# Отсюда же собирается меню команд для bot.set_my_commands.
BOT_COMMANDS = (
    ('start', 'Приветствие и список команд'),
    ('help', 'Справка по командам'),
    ('new', 'Создать расписание'),
    ('template', 'Скачать шаблон таблицы расписания'),
    ('today', 'Расписание на сегодня'),
    ('tomorrow', 'Расписание на завтра'),
    ('week', 'Расписание на неделю'),
    ('switch_week', 'Поменять чётную и нечётную неделю'),
    ('group', 'Показать id группы (в группе)'),
    ('bind', 'Привязать расписание к группе'),
    ('unbind', 'Отвязать расписание от группы'),
    ('weather', 'Погода'),
    ('cat', 'Случайный котик'),
    ('cancel', 'Отменить текущее действие'),
)

COMMANDS_LIST = '\n'.join(
    f'/{command} — {description}' for command, description in BOT_COMMANDS
)

# Подставлять имя: START_MESSAGE.format(name=html.quote(full_name)).
START_MESSAGE = (
    'Привет, <b>{name}</b>! 👋\n\n'
    'Я бот с расписанием занятий. Умею:\n'
    '📅 хранить расписание, в том числе по чётным и нечётным неделям;\n'
    '📥 загружать расписание из таблицы Excel;\n'
    '👥 присылать расписание в группу;\n'
    '🌤 показывать погоду;\n'
    '🐱 присылать котиков.\n\n'
    '<b>Команды:</b>\n'
    f'{COMMANDS_LIST}\n\n'
    'Начни с /new, чтобы создать своё расписание.'
)

UNKNOWN_USER = 'Неизвестный пользователь'

# Команды, которые работают в группах.
GROUP_COMMANDS = (
    ('start', 'Как подключить расписание'),
    ('today', 'Расписание на сегодня'),
    ('tomorrow', 'Расписание на завтра'),
    ('week', 'Расписание на неделю'),
    ('group', 'Показать id группы'),
    ('weather', 'Погода'),
    ('cat', 'Случайный котик'),
)

GROUP_COMMANDS_LIST = '\n'.join(
    f'/{command} — {description}' for command, description in GROUP_COMMANDS
)

# Подставлять id: GROUP_START_MESSAGE.format(chat_id=message.chat.id).
GROUP_START_MESSAGE = (
    'Привет! Я бот с расписанием занятий 📅\n\n'
    '<b>Чтобы подключить расписание к этой группе:</b>\n'
    '1. Создай расписание у меня в личке: /new\n'
    '2. Там же отправь /bind и укажи id этой группы:\n'
    '<code>{chat_id}</code>\n\n'
    'Привязать расписание может только администратор группы.\n\n'
    '<b>Команды в группе:</b>\n'
    f'{GROUP_COMMANDS_LIST}'
)
