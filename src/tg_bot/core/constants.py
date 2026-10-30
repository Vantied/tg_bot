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
    ('delete', 'Удалить расписание'),
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

# /cancel
CANCEL_MESSAGE = 'Действие отменено.'
NOTHING_TO_CANCEL_MESSAGE = 'Нечего отменять.'

# /new: кнопки длины расписания
ONE_WEEK_BUTTON = '7 дней — каждую неделю одинаково'
TWO_WEEKS_BUTTON = '14 дней — чётная и нечётная'
ONE_WEEK_CALLBACK = 'weeks_1'
TWO_WEEKS_CALLBACK = 'weeks_2'

# /new: кнопки текущей недели
FIRST_WEEK_BUTTON = '1-я неделя'
SECOND_WEEK_BUTTON = '2-я неделя'
FIRST_WEEK_CALLBACK = 'current_1'
SECOND_WEEK_CALLBACK = 'current_2'

# /new: тексты диалога. {title} подставлять через html.quote.
SCHEDULE_EXISTS_MESSAGE = (
    'У тебя уже есть расписание «{title}».\n'
    'Чтобы создать новое, сначала удали старое: /delete'
)
ASK_TITLE_MESSAGE = (
    'Как назовём расписание? Например: ИВТ-21\n\nОтменить: /cancel'
)
TITLE_NOT_TEXT_MESSAGE = 'Пришли название текстом.'
TITLE_TOO_LONG_MESSAGE = (
    f'Слишком длинное название, максимум {SCHEDULE_TITLE_MAX_LENGTH} '
    'символов. Попробуй короче.'
)
ASK_LENGTH_MESSAGE = (
    'Расписание одинаковое каждую неделю или чередуются чётная и нечётная?'
)
ASK_CURRENT_WEEK_MESSAGE = 'Какая неделя идёт сейчас?'
PRESS_BUTTON_MESSAGE = 'Выбери вариант кнопкой выше или отмени: /cancel'
SCHEDULE_CREATED_MESSAGE = (
    'Расписание «{title}» создано ✅\n\n'
    'Теперь пришли таблицу с занятиями файлом .xlsx.'
)

# /delete: кнопки подтверждения
YES_BUTTON = 'Да, удалить'
NO_BUTTON = 'Отмена'
DELETE_CONFIRM_CALLBACK = 'delete_yes'
DELETE_CANCEL_CALLBACK = 'delete_no'

# /delete: тексты. {title} подставлять через html.quote.
NOTHING_TO_DELETE_MESSAGE = 'У тебя нет расписания, удалять нечего.'
DELETE_CONFIRM_MESSAGE = (
    'Удалить расписание «{title}»?\n'
    'Все занятия удалятся, а привязанные группы отвяжутся.'
)
SCHEDULE_DELETED_MESSAGE = 'Расписание «{title}» удалено.\nСоздать новое: /new'
DELETE_CANCELLED_MESSAGE = 'Удаление отменено.'

# Команды, которые работают в группах.
GROUP_COMMANDS = (
    ('start', 'Как подключить расписание'),
    ('help', 'Справка по командам'),
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

HELP_MESSAGE = (
    '<b>Справка</b>\n\n'
    '<b>📅 Расписание</b>\n'
    '/new — создать расписание: название, 7 или 14 дней '
    'и какая неделя идёт сейчас\n'
    '/template — скачать шаблон Excel. Заполни его и отправь мне файлом, '
    'я загружу занятия\n'
    '/today, /tomorrow, /week — расписание на день или неделю\n'
    '/switch_week — если перепутались чётная и нечётная неделя\n'
    '/delete — удалить расписание вместе с занятиями\n\n'
    '<b>👥 Группы</b>\n'
    '1. Добавь меня в группу и отправь там /group — я покажу её id\n'
    '2. Здесь, в личке, отправь /bind и укажи этот id\n'
    '/unbind — отвязать расписание от группы\n'
    'Привязывать может только администратор группы.\n\n'
    '<b>✨ Прочее</b>\n'
    '/weather — погода\n'
    '/cat — случайный котик\n'
    '/cancel — отменить текущее действие'
)

GROUP_HELP_MESSAGE = (
    '<b>Справка</b>\n\n'
    '<b>Как подключить расписание</b>\n'
    '1. Отправь /group — я покажу id этой группы\n'
    '2. Напиши мне в личку: /new — создать расписание, '
    'затем /bind и id группы\n'
    'Привязывать может только администратор группы.\n\n'
    '<b>Команды в группе</b>\n'
    f'{GROUP_COMMANDS_LIST}'
)
