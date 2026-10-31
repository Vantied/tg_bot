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
# Утренняя рассылка в группы: час по часовому поясу расписания.
DAILY_SCHEDULE_HOUR = 7

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
    ('now', 'Какая пара идёт сейчас'),
    ('today', 'Расписание на сегодня'),
    ('tomorrow', 'Расписание на завтра'),
    ('week', 'Расписание на неделю'),
    ('switch_week', 'Поменять чётную и нечётную неделю'),
    ('timezone', 'Часовой пояс: /timezone город'),
    ('delete', 'Удалить расписание'),
    ('bind', 'Привязать расписание к группе'),
    ('unbind', 'Отвязать расписание от группы'),
    ('weather', 'Погода: /weather город'),
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
USER_NOT_DEFINED_MESSAGE = 'Не удалось определить, кто отправил сообщение.'

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
ASK_CITY_FOR_TIMEZONE_MESSAGE = (
    'В каком городе ты учишься? Это нужно, чтобы знать твоё время.\n'
    'Например: Омск'
)
CITY_FOR_TIMEZONE_NOT_FOUND_MESSAGE = (
    'Не нашёл город «{city}». Попробуй написать иначе, например: Омск'
)
TIMEZONE_FALLBACK_MESSAGE = (
    'Не получилось определить часовой пояс, пока ставлю московское время. '
    'Поменять потом: /timezone город'
)
TIMEZONE_SET_MESSAGE = 'Часовой пояс: {timezone}, сейчас у тебя {time}.'
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

# Таблица расписания: колонки шаблона в нужном порядке.
COLUMN_DAY = 'День'
COLUMN_START = 'Начало'
COLUMN_END = 'Конец'
COLUMN_SUBJECT = 'Предмет'
COLUMN_ROOM = 'Кабинет'
COLUMN_TEACHER = 'Преподаватель'
COLUMN_WEEK = 'Неделя'
TEMPLATE_COLUMNS = (
    COLUMN_DAY,
    COLUMN_START,
    COLUMN_END,
    COLUMN_SUBJECT,
    COLUMN_ROOM,
    COLUMN_TEACHER,
    COLUMN_WEEK,
)
# Без этих колонок файл не разобрать.
REQUIRED_COLUMNS = (COLUMN_DAY, COLUMN_START, COLUMN_END, COLUMN_SUBJECT)

# Дни недели по индексу date.weekday() и варианты написания в файле.
WEEKDAY_SHORT_NAMES = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')
WEEKDAY_FULL_NAMES = (
    'понедельник',
    'вторник',
    'среда',
    'четверг',
    'пятница',
    'суббота',
    'воскресенье',
)

# Значения колонки «Неделя». Пустая ячейка = каждую неделю.
WEEK_EVERY_VALUE = 'каждая'
WEEK_FIRST_VALUE = '1'
WEEK_SECOND_VALUE = '2'

# Формат времени в таблице.
TIME_FORMATS = ('%H:%M', '%H:%M:%S')
TIME_OUTPUT_FORMAT = '%H:%M'

# Ограничения на файл.
MAX_SCHEDULE_FILE_SIZE = 1024 * 1024  # 1 МБ
MAX_LESSONS_IN_FILE = 200
MAX_SHOWN_FILE_ERRORS = 10

# Строки-примеры для пустого шаблона.
TEMPLATE_EXAMPLE_ROWS = (
    ('Пн', '08:30', '10:00', 'Матанализ', '305', 'Иванов И.И.', 'каждая'),
    ('Пн', '10:10', '11:40', 'Физика', '112', '', '1'),
    ('Вт', '08:30', '10:00', 'Программирование', '401', '', '2'),
)

# /template и загрузка файла
TEMPLATE_FILENAME = 'raspisanie.xlsx'
TEMPLATE_CAPTION = (
    'Шаблон расписания: одна строка — одно занятие.\n'
    'День: Пн–Вс. Время: ЧЧ:ММ. '
    'Неделя: каждая, 1 или 2 (для расписания на 7 дней не важна).\n\n'
    'Заполни и пришли файл мне.'
)
NOT_XLSX_MESSAGE = 'Пришли таблицу в формате .xlsx. Шаблон: /template'
FILE_TOO_BIG_MESSAGE = 'Файл слишком большой, максимум 1 МБ.'
NO_SCHEDULE_FOR_FILE_MESSAGE = (
    'Сначала создай расписание: /new\nПотом пришли таблицу.'
)
FILE_READ_ERROR_MESSAGE = (
    'Не получилось прочитать файл. Проверь, что это таблица .xlsx, '
    'или возьми шаблон: /template'
)
FILE_EMPTY_MESSAGE = 'В таблице нет ни одного занятия.'
FILE_ERRORS_MESSAGE = (
    'В файле есть ошибки, ничего не сохранено:\n\n{errors}\n\n'
    'Исправь и пришли файл ещё раз.'
)
MORE_FILE_ERRORS = '…и ещё ошибок: {count}'
LESSONS_LOADED_MESSAGE = (
    'Загружено занятий: {count} ✅\nПосмотреть расписание: /week'
)

# Ошибки разбора файла. {row} - номер строки в Excel.
ROW_ERROR = 'Строка {row}: {error}'
MISSING_COLUMNS_ERROR = 'Нет колонок: {columns}. Возьми шаблон: /template'
TOO_MANY_LESSONS_ERROR = (
    f'Слишком много занятий, максимум {MAX_LESSONS_IN_FILE}.'
)
BAD_DAY_ERROR = 'неизвестный день «{value}», нужно Пн–Вс'
BAD_TIME_ERROR = '{column}: «{value}» — нужно время ЧЧ:ММ'
TIME_ORDER_ERROR = 'конец занятия не позже начала'
EMPTY_SUBJECT_ERROR = 'не указан предмет'
TOO_LONG_ERROR = '{column}: длиннее {limit} символов'
BAD_WEEK_ERROR = 'неделя «{value}» — нужно «каждая», 1 или 2'

# Команды, которые работают в группах.
GROUP_COMMANDS = (
    ('start', 'Как подключить расписание'),
    ('help', 'Справка по командам'),
    ('now', 'Какая пара идёт сейчас'),
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
    '/new — создать расписание: название, город, 7 или 14 дней '
    'и какая неделя идёт сейчас\n'
    '/template — скачать шаблон Excel. Заполни его и отправь мне файлом, '
    'я загружу занятия\n'
    '/now — какая пара идёт сейчас и какая следующая\n'
    '/today, /tomorrow, /week — расписание на день или неделю\n'
    '/switch_week — если перепутались чётная и нечётная неделя\n'
    '/timezone Омск — поменять часовой пояс по городу\n'
    '/delete — удалить расписание вместе с занятиями\n\n'
    '<b>👥 Группы</b>\n'
    '1. Добавь меня в группу и отправь там /group — я покажу её id\n'
    '2. Здесь, в личке, отправь /bind и укажи этот id\n'
    '/unbind — отвязать расписание от группы\n'
    'Привязывать может только администратор группы.\n'
    f'Каждое утро в {DAILY_SCHEDULE_HOUR}:00 я присылаю в привязанные группы '
    'расписание на день.\n\n'
    '<b>✨ Прочее</b>\n'
    '/weather Омск — погода в городе\n'
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


CAT_API_URL = 'https://api.thecatapi.com/v1/images/search'
TIMEOUT = 10

CAT_REQUEST_ERROR_MESSAGE = 'Не удалось отправить кота, попробуйте ещё раз'

# Общая ошибка, если в хендлере что-то упало.
UNEXPECTED_ERROR_MESSAGE = 'Что-то пошло не так 😔 Попробуй ещё раз позже.'

# Показ расписания
WEEKDAY_NAMES = (
    'Понедельник',
    'Вторник',
    'Среда',
    'Четверг',
    'Пятница',
    'Суббота',
    'Воскресенье',
)
MONTH_NAMES = (
    'января',
    'февраля',
    'марта',
    'апреля',
    'мая',
    'июня',
    'июля',
    'августа',
    'сентября',
    'октября',
    'ноября',
    'декабря',
)
DAY_HEADER = '<b>{weekday}, {day} {month}</b>'
WEEK_NUMBER_SUFFIX = ' · {week}-я неделя'
LESSON_LINE = '{start}–{end} {subject}'
LESSON_ROOM = ', ауд. {room}'
LESSON_TEACHER = ', {teacher}'
NO_LESSONS_DAY = 'Занятий нет 🎉'
NO_LESSONS_WEEK = 'На этой неделе занятий нет 🎉'
NO_SCHEDULE_PRIVATE_MESSAGE = 'У тебя пока нет расписания. Создать: /new'
NO_SCHEDULE_GROUP_MESSAGE = (
    'К этой группе не привязано расписание. Как подключить: /start'
)

# /switch_week
NOT_TWO_WEEKS_MESSAGE = (
    'Твоё расписание одинаковое каждую неделю, менять нечего.'
)
WEEK_SWITCHED_MESSAGE = 'Готово, сейчас идёт {week}-я неделя.'

# /group
GROUP_ID_MESSAGE = (
    'id этой группы: <code>{chat_id}</code>\n'
    'Отправь мне в личку: /bind {chat_id}'
)

# /bind
ASK_CHAT_ID_MESSAGE = (
    'Пришли id группы. Чтобы его узнать, добавь меня в группу '
    'и отправь там /group.\n\nОтменить: /cancel'
)
BAD_CHAT_ID_MESSAGE = (
    'Это не похоже на id группы. Он выглядит так: -1001234567890'
)
CHAT_NOT_FOUND_MESSAGE = (
    'Не нашёл такую группу. Проверь id и что я добавлен в группу.'
)
NOT_A_GROUP_MESSAGE = 'Это не группа. Привязать можно только группу.'
NOT_CHAT_ADMIN_MESSAGE = (
    'Привязать расписание может только администратор группы.'
)
CHAT_BOUND_MESSAGE = 'Группа «{chat}» привязана к расписанию «{schedule}» ✅'
CHAT_BOUND_GROUP_MESSAGE = (
    'К группе привязано расписание «{schedule}» 📅\n'
    'Расписание на сегодня: /today'
)

# /unbind
NO_BOUND_CHATS_MESSAGE = 'К твоему расписанию не привязана ни одна группа.'
CHOOSE_CHAT_TO_UNBIND_MESSAGE = 'Какую группу отвязать?'
UNBIND_CALLBACK_PREFIX = 'unbind_'
CHAT_UNBOUND_MESSAGE = 'Группа «{chat}» отвязана.'
CHAT_ALREADY_UNBOUND_MESSAGE = 'Эта группа уже отвязана.'

# /weather (Open-Meteo, ключ не нужен)
GEOCODING_API_URL = 'https://geocoding-api.open-meteo.com/v1/search'
WEATHER_API_URL = 'https://api.open-meteo.com/v1/forecast'
WEATHER_CURRENT_FIELDS = (
    'temperature_2m,apparent_temperature,weather_code,wind_speed_10m'
)
ASK_CITY_MESSAGE = 'Напиши город после команды, например: /weather Омск'
CITY_NOT_FOUND_MESSAGE = 'Не нашёл город «{city}».'
WEATHER_REQUEST_ERROR_MESSAGE = 'Не удалось узнать погоду, попробуй позже.'
WEATHER_MESSAGE = (
    '<b>{city}</b>\n'
    '{emoji} {description}\n'
    '🌡 {temperature}°C, ощущается как {feels_like}°C\n'
    '💨 Ветер {wind} м/с'
)
# Коды погоды WMO: код -> (эмодзи, описание).
WEATHER_CODES = {
    0: ('☀️', 'Ясно'),
    1: ('🌤', 'Преимущественно ясно'),
    2: ('⛅', 'Переменная облачность'),
    3: ('☁️', 'Пасмурно'),
    45: ('🌫', 'Туман'),
    48: ('🌫', 'Изморозь'),
    51: ('🌦', 'Слабая морось'),
    53: ('🌦', 'Морось'),
    55: ('🌧', 'Сильная морось'),
    56: ('🌧', 'Ледяная морось'),
    57: ('🌧', 'Сильная ледяная морось'),
    61: ('🌦', 'Небольшой дождь'),
    63: ('🌧', 'Дождь'),
    65: ('🌧', 'Сильный дождь'),
    66: ('🌧', 'Ледяной дождь'),
    67: ('🌧', 'Сильный ледяной дождь'),
    71: ('🌨', 'Небольшой снег'),
    73: ('🌨', 'Снег'),
    75: ('❄️', 'Сильный снег'),
    77: ('🌨', 'Снежные зёрна'),
    80: ('🌦', 'Ливень'),
    81: ('🌧', 'Сильный ливень'),
    82: ('⛈', 'Очень сильный ливень'),
    85: ('🌨', 'Снегопад'),
    86: ('❄️', 'Сильный снегопад'),
    95: ('⛈', 'Гроза'),
    96: ('⛈', 'Гроза с градом'),
    99: ('⛈', 'Сильная гроза с градом'),
}
UNKNOWN_WEATHER = ('🌡', 'Погода')

# Утренняя рассылка в группы (час рассылки - в начале файла).
DAILY_SCHEDULE_HEADER = 'Доброе утро! Расписание на сегодня ☀️'

# /timezone
CURRENT_TIMEZONE_MESSAGE = (
    'Часовой пояс расписания: {timezone}, сейчас там {time}.\n'
    'Поменять: /timezone город, например /timezone Омск'
)
TIMEZONE_REQUEST_ERROR_MESSAGE = (
    'Не получилось определить часовой пояс, попробуй позже.'
)

# /now
NOW_LESSON_MESSAGE = '<b>Сейчас идёт:</b>\n{lesson}\nДо конца: {minutes} мин.'
NEXT_LESSON_MESSAGE = '<b>Следующая:</b>\n{lesson}\nНачнётся через: {wait}'
NO_LESSON_NOW_MESSAGE = 'Сейчас пары нет.'
NO_MORE_LESSONS_TODAY_MESSAGE = 'Сегодня пар больше нет 🎉'
WAIT_MINUTES = '{minutes} мин.'
WAIT_HOURS = '{hours} ч {minutes} мин.'
WAIT_WHOLE_HOURS = '{hours} ч'
MINUTES_IN_HOUR = 60
