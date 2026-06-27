"""Локализация UI киоска «Сады Коломны» (RU/EN по offline-референсу)."""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

_HUB_KEYS = ("strawberry", "blueberry", "raspberry", "tours")

_RU = {
    "ATTRACT_CTA": "Коснитесь, чтобы начать",
    "ATTRACT_TAGLINE": "Такой должна быть ягода",
    "ATTRACT_FOOT": "Самовывоз с фермы · оплата картой и СБП",
    "MENU_EYEBROW": "Меню",
    "CHOOSE_CATEGORY": "Что соберём?",
    "BACK": "Назад",
    "CART": "Корзина",
    "CART_TITLE": "Ваш заказ",
    "CART_EMPTY": "Корзина пуста",
    "CART_EMPTY_SUB": "Добавьте ягоды из меню",
    "TO_MENU": "В меню",
    "REMOVE": "Удалить",
    "TOTAL": "Итого",
    "CHECKOUT": "Перейти к оплате",
    "KEEP_SHOPPING": "Добавить ещё",
    "PAY_TITLE": "Оплата",
    "PAY_METHOD": "Выберите способ оплаты",
    "PAY_SBP": "СБП · по QR-коду",
    "PAY_SBP_SUB": "Сканируйте код в приложении банка",
    "PAY_CARD": "Банковская карта",
    "PAY_CARD_SUB": "Приложите или вставьте карту в терминал",
    "PAY": "Оплатить",
    "PAY_SBP_SCAN": "Отсканируйте QR-код для оплаты",
    "PAY_DUE": "К оплате",
    "PAY_CANCEL": "Отмена",
    "PAY_ERROR_TITLE": "Оплата не прошла",
    "PAY_ERROR_CONTACT": "Свяжитесь, пожалуйста, с нами и сообщите об ошибке.",
    "PAY_ERROR_RETRY": "Попробовать снова",
    "PAY_ERROR_MENU": "В главное меню",
    "DONE_TITLE": "Готово!",
    "DONE_SUB": "Заберите чек у киоска",
    "DONE_COUNTDOWN": "Возврат на главный экран через {n} сек…",
    "CUR": "₽",
    "INFO": "Инфо",
    "INFO_TITLE": "Сады Коломны",
    "INFO_LEAD": "Реквизиты хозяйства",
    "INFO_HOURS_LABEL": "Часы работы",
    "INFO_PHONE_LABEL": "Телефон",
    "INFO_PHONE": "+7 901 518-33-33",
    "INFO_SITE_LABEL": "Сайт",
    "INFO_SITE": "sadkolomna.ru",
    "INFO_CLOSE": "Закрыть",
    "QR_SITE": "Сайт",
    "QR_TG": "Telegram",
    "QR_VK": "ВКонтакте",
    "QR_MAX": "MAX",
    "DEV_TITLE": "Разработано",
    "DEV_PHONE": "+7 997 9-901-901",
    "DEV_SITE": "buro901.ru",
    "ADMIN_ACCESS": "Режим администратора",
    "ADMIN_PIN_PROMPT": "Введите PIN",
    "ADMIN_WRONG_PIN": "Неверный PIN",
    "ADMIN_TITLE": "Настройки терминала",
    "ADMIN_LAYOUT_SECTION": "Раскладка меню",
    "ADMIN_LAYOUT_HINT": "Как показывать сорта внутри категории",
    "ADMIN_LAYOUT_LIST": "Список",
    "ADMIN_LAYOUT_LIST_DESC": "Крупные строки на всю ширину",
    "ADMIN_LAYOUT_GRID": "Плитка 2×2",
    "ADMIN_LAYOUT_GRID_DESC": "Карточки по две в ряд",
    "ADMIN_START_SECTION": "Стартовый экран",
    "ADMIN_START_TOGGLE": "Показывать экран приветствия",
    "ADMIN_START_HINT": "Заставка с логотипом перед каталогом",
    "ADMIN_SKIP_SECTION": "Карточка товара",
    "ADMIN_SKIP_TOGGLE": "Скрывать экран товара",
    "ADMIN_SKIP_HINT": "Без экрана товара — в корзину только по кнопке «+»",
    "ADMIN_DESC_SECTION": "Описание в карточке",
    "ADMIN_DESC_HINT": "Текст описания под названием в списке товаров",
    "ADMIN_DESC_TOGGLE": "Показывать описание",
    "ADMIN_IMAGES_SECTION": "Фото товаров",
    "ADMIN_IMAGES_TOGGLE": "Загружать фото с сервера",
    "ADMIN_IMAGES_HINT": "Если выключено — в каталоге показываются заглушки ягод",
    "ADMIN_BREATHE_SECTION": "Кнопки",
    "ADMIN_BREATHE_TOGGLE": "Дыхание текста в кнопках",
    "ADMIN_BREATHE_HINT": "Если выключено — пульсирует только форма кнопки, текст остаётся ровным",
    "ADMIN_PAY_SECTION": "Способы оплаты",
    "ADMIN_PAY_HINT": "Какие варианты показывать на экране оплаты",
    "ADMIN_PAY_SBP_TOGGLE": "СБП по QR-коду",
    "ADMIN_PAY_CARD_TOGGLE": "Банковская карта",
    "ADMIN_HOURS_SECTION": "Режим работы",
    "ADMIN_HOURS_HINT": "Отображается в информационном окне",
    "ADMIN_RUNTIME_SECTION": "Режим работы",
    "ADMIN_RUNTIME_HINT": "Тестовый — без сервера; API — каталог и оплата через Катюшу",
    "ADMIN_API_MODE_TOGGLE": "Работа с API Катюша",
    "ADMIN_RUNTIME_CATALOG": "Каталог",
    "ADMIN_RUNTIME_PAYMENT": "Оплата СБП",
    "ADMIN_RUNTIME_INTEGRATION": "Интеграция",
    "ADMIN_MODE_TEST": "Тестовый",
    "ADMIN_MODE_API": "API Катюша",
    "ADMIN_INTEGRATION_AQSI": "Т-Банк aQsi",
    "ADMIN_INTEGRATION_POS_SBP": "Терминал + СБП на экране",
    "ADMIN_INTEGRATION_POS_PRINTER": "Терминал + принтер",
    "ADMIN_INTEGRATION_LEGACY": "УМКА + принтер",
    "ADMIN_COLOR_SECTION": "Цвет кнопок",
    "ADMIN_COLOR_HINT": "Акцент основных кнопок",
    "ADMIN_COLOR_GREEN": "Зелёный",
    "ADMIN_COLOR_STRAWBERRY": "Клубничный",
    "ADMIN_COLOR_YELLOW": "Жёлтый",
    "ADMIN_CANCEL": "Отмена",
    "ADMIN_DONE": "Готово",
    "ADMIN_QUIT_APP": "Закрыть приложение",
    "ADMIN_PRINTER_SECTION": "Принтер HS-K33",
    "ADMIN_PRINTER_HINT_USB": "USB через очередь Windows (Generic / Text Only). Проверка без оплаты.",
    "ADMIN_PRINTER_HINT_ETHERNET": "Ethernet RAW TCP, порт 9100. Проверка связи без оплаты.",
    "ADMIN_PRINTER_ADDR": "Адрес: {host}:{port}",
    "ADMIN_PRINTER_USB": "Принтер Windows: {name}",
    "ADMIN_PRINTER_TEST": "Тестовая печать",
    "ADMIN_PRINTER_TESTING": "Подключение к принтеру…",
    "ADMIN_PRINTER_OK": "Тестовый чек отправлен на принтер.",
    "ADMIN_PRINTER_FAIL": "Не удалось напечатать. Проверьте IP, порт 9100 и кабель.",
    "ADD_SHORT": "В корзину",
    "PER_PACK": "за лоток",
    "PER_TICKET": "за билет",
    "PER_PERSON": "с человека",
    "PACKS_WORD": "лотков",
    "TICKETS_WORD": "билетов",
    "PEOPLE_WORD": "человек",
    "ADDED_TOAST": "Добавлено в корзину",
    "GRADE_PREMIUM": "Премиум",
    "GRADE_STANDARD": "Стандарт",
    "GRADE_JAM": "На варенье",
    "GRADE_DESC_PREMIUM": "Крупная отборная ягода, ручной сбор",
    "GRADE_DESC_STANDARD": "Свежий сбор сегодня утром",
    "GRADE_DESC_JAM": "Для варенья и домашних заготовок",
    "GRADE_TOUR_WALK": "Экскурсия по ферме",
    "GRADE_TOUR_TASTE": "Экскурсия + дегустация",
    "EST_PRICE": "ориентир. цена",
    "PAY_SBP_GEN": "Формируем QR-код…",
    "PAY_SBP_GEN_SUB": "Подождите несколько секунд",
    "PAY_CARD_HOLD": "Поднесите карту к терминалу и произведите оплату",
    "DONE_THANKS": "Спасибо за заказ",
    "ORDER_NO": "Заказ",
    "COLLECT": "Заберите заказ на стойке выдачи",
    "COLLECT_SUB": "Назовите номер заказа сотруднику фермы",
    "NEW_ORDER": "Новый заказ",
    "AUTO_RETURN": "Возврат на главный экран через",
    "SEC": "сек",
    "QTY_LABEL": "Количество",
    "CAT_TOURS": "Экскурсии",
    "TOUR_DATES_TITLE": "Доступные даты",
    "TOUR_GUEST_ADULTS": "Взрослые",
    "TOUR_GUEST_KIDS": "Дети до 15 лет",
    "TOUR_GUEST_FREE": "Бесплатно",
    "TOUR_ADD": "В корзину",
    "CART_TOUR_PHOTO": "фото • экскурсия",
    "CART_TOUR_GUESTS": "Взрослые ×{adults} · дети ×{kids} ({free})",
    "CART_TOUR_GUESTS_ADULTS": "Взрослые ×{adults}",
    "CART_TOUR_DATE": "Дата: {date}",
    "TOUR_PICK_DATE": "Выберите дату экскурсии",
    "ADD_TO_CART": "Добавить",
    "TOUR_STEPS_TITLE": "Что входит в экскурсию",
    "TOUR_GIFT_TITLE": "Подарок на финал",
    "TOUR_GIFT_DESC": "Каждая семья уезжает с килограммом свежесобранной клубники и фото на поле.",
    "HUB_PROMO_LINE1": "Всей",
    "HUB_PROMO_LINE2": "семьёй",
    "HUB_PROMO_SUB": "Час на грядках, дегустация и ягода в подарок",
    "CAT": {
        "strawberry": "Клубника",
        "blueberry": "Голубика",
        "raspberry": "Малина",
        "tours": "Экскурсии",
    },
    "MONTHS_NOM": {6: "Июнь", 7: "Июль", 8: "Август"},
    "TOUR_DATES": ((6, (20, 27)), (7, (4,)), (8, (15, 22))),
    "TOUR_STEPS": (
        (
            "Встреча у шатра",
            "Каждая семья получает холщовую сумку «Сады Коломны», а дети — наклейку «Юный агроном».",
        ),
        (
            "Обход фермы и плантаций",
            "Знакомство с тремя культурами — клубникой, голубикой и малиной. Узнаете, чем отличаются "
            "сорта клубники Азия, Ания, Мара де Буа, Флорида Бьюти, Мурано и другие, и почему магазинная "
            "ягода уступает собранной в поле в полной зрелости.",
        ),
        (
            "Дегустация клубники",
            "Сорта, что в плодоношении в этот день — в полной зрелости, только что с куста.",
        ),
        (
            "Закулисье фермы",
            "Пруд с осетрами, капельный полив, пасека и плёночные туннели изнутри. Рефрижератор «Катюша» — "
            "машина, в которой ягода едет в Москву в день сбора.",
        ),
    ),
    "DEFAULT_HOURS": "Ежедневно 10:00–19:00",
}

_EN = {
    "ATTRACT_CTA": "Touch to start",
    "ATTRACT_TAGLINE": "This is how a berry should be",
    "ATTRACT_FOOT": "Farm pickup · card & SBP payment",
    "MENU_EYEBROW": "Menu",
    "CHOOSE_CATEGORY": "What shall we pick?",
    "BACK": "Back",
    "CART": "Cart",
    "CART_TITLE": "Your order",
    "CART_EMPTY": "Your cart is empty",
    "CART_EMPTY_SUB": "Add some berries from the menu",
    "TO_MENU": "Go to menu",
    "REMOVE": "Remove",
    "TOTAL": "Total",
    "CHECKOUT": "Checkout",
    "KEEP_SHOPPING": "Add more",
    "PAY_TITLE": "Payment",
    "PAY_METHOD": "Choose a payment method",
    "PAY_SBP": "SBP · by QR code",
    "PAY_SBP_SUB": "Scan the code in your bank app",
    "PAY_CARD": "Bank card",
    "PAY_CARD_SUB": "Tap or insert your card in the terminal",
    "PAY": "Pay",
    "PAY_SBP_SCAN": "Scan the QR code to pay",
    "PAY_DUE": "To pay",
    "PAY_CANCEL": "Cancel",
    "PAY_ERROR_TITLE": "Payment failed",
    "PAY_ERROR_CONTACT": "Please contact us and report the error.",
    "PAY_ERROR_RETRY": "Try again",
    "PAY_ERROR_MENU": "Main menu",
    "DONE_TITLE": "All set!",
    "DONE_SUB": "Collect your receipt at the kiosk",
    "DONE_COUNTDOWN": "Returning to home screen in {n} s…",
    "CUR": "₽",
    "INFO": "Info",
    "INFO_TITLE": "Sady Kolomny",
    "INFO_LEAD": "Company details",
    "INFO_HOURS_LABEL": "Working hours",
    "INFO_PHONE_LABEL": "Phone",
    "INFO_PHONE": "+7 901 518-33-33",
    "INFO_SITE_LABEL": "Website",
    "INFO_SITE": "sadkolomna.ru",
    "INFO_CLOSE": "Close",
    "QR_SITE": "Website",
    "QR_TG": "Telegram",
    "QR_VK": "VK",
    "QR_MAX": "MAX",
    "DEV_TITLE": "Developed by",
    "DEV_PHONE": "+7 997 9-901-901",
    "DEV_SITE": "buro901.ru",
    "ADMIN_ACCESS": "Administrator mode",
    "ADMIN_PIN_PROMPT": "Enter PIN",
    "ADMIN_WRONG_PIN": "Wrong PIN",
    "ADMIN_TITLE": "Terminal settings",
    "ADMIN_LAYOUT_SECTION": "Menu layout",
    "ADMIN_LAYOUT_HINT": "How grades appear inside a category",
    "ADMIN_LAYOUT_LIST": "List",
    "ADMIN_LAYOUT_LIST_DESC": "Large full-width rows",
    "ADMIN_LAYOUT_GRID": "Grid 2×2",
    "ADMIN_LAYOUT_GRID_DESC": "Two cards per row",
    "ADMIN_START_SECTION": "Start screen",
    "ADMIN_START_TOGGLE": "Show welcome screen",
    "ADMIN_START_HINT": "Logo splash before the catalog",
    "ADMIN_SKIP_SECTION": "Product card",
    "ADMIN_SKIP_TOGGLE": "Skip product screen",
    "ADMIN_SKIP_HINT": "No product screen — add to cart only via the «+» button",
    "ADMIN_DESC_SECTION": "Description on card",
    "ADMIN_DESC_HINT": "Product description below the title in the product list",
    "ADMIN_DESC_TOGGLE": "Show description",
    "ADMIN_IMAGES_SECTION": "Product photos",
    "ADMIN_IMAGES_TOGGLE": "Load photos from server",
    "ADMIN_IMAGES_HINT": "When off — berry placeholder images are shown in the catalog",
    "ADMIN_BREATHE_SECTION": "Buttons",
    "ADMIN_BREATHE_TOGGLE": "Button text breathing",
    "ADMIN_BREATHE_HINT": "When off — only the button shape pulses, text stays fixed",
    "ADMIN_PAY_SECTION": "Payment methods",
    "ADMIN_PAY_HINT": "Which options appear on the payment screen",
    "ADMIN_PAY_SBP_TOGGLE": "SBP via QR code",
    "ADMIN_PAY_CARD_TOGGLE": "Bank card",
    "ADMIN_HOURS_SECTION": "Working hours",
    "ADMIN_HOURS_HINT": "Shown in the information window",
    "ADMIN_RUNTIME_SECTION": "Operating mode",
    "ADMIN_RUNTIME_HINT": "Test — no server; API — catalog and payment via Katusha",
    "ADMIN_API_MODE_TOGGLE": "Katusha API",
    "ADMIN_RUNTIME_CATALOG": "Catalog",
    "ADMIN_RUNTIME_PAYMENT": "SBP payment",
    "ADMIN_RUNTIME_INTEGRATION": "Integration",
    "ADMIN_MODE_TEST": "Test",
    "ADMIN_MODE_API": "Katusha API",
    "ADMIN_INTEGRATION_AQSI": "T-Bank aQsi",
    "ADMIN_INTEGRATION_POS_SBP": "Terminal + on-screen SBP",
    "ADMIN_INTEGRATION_POS_PRINTER": "Terminal + printer",
    "ADMIN_INTEGRATION_LEGACY": "UMKA + printer",
    "ADMIN_COLOR_SECTION": "Button colour",
    "ADMIN_COLOR_HINT": "Accent of the primary buttons",
    "ADMIN_COLOR_GREEN": "Green",
    "ADMIN_COLOR_STRAWBERRY": "Strawberry",
    "ADMIN_COLOR_YELLOW": "Yellow",
    "ADMIN_CANCEL": "Cancel",
    "ADMIN_DONE": "Done",
    "ADMIN_QUIT_APP": "Close application",
    "ADMIN_PRINTER_SECTION": "HS-K33 printer",
    "ADMIN_PRINTER_HINT_USB": "USB via Windows spooler (Generic / Text Only). Test without payment.",
    "ADMIN_PRINTER_HINT_ETHERNET": "Ethernet RAW TCP, port 9100. Connectivity check without payment.",
    "ADMIN_PRINTER_ADDR": "Address: {host}:{port}",
    "ADMIN_PRINTER_USB": "Windows printer: {name}",
    "ADMIN_PRINTER_TEST": "Test print",
    "ADMIN_PRINTER_TESTING": "Connecting to printer…",
    "ADMIN_PRINTER_OK": "Test receipt sent to the printer.",
    "ADMIN_PRINTER_FAIL": "Print failed. Check IP, port 9100 and cable.",
    "ADD_SHORT": "Add",
    "PER_PACK": "per tray",
    "PER_TICKET": "per ticket",
    "PER_PERSON": "per person",
    "PACKS_WORD": "trays",
    "TICKETS_WORD": "tickets",
    "PEOPLE_WORD": "people",
    "ADDED_TOAST": "Added to cart",
    "GRADE_PREMIUM": "Premium",
    "GRADE_STANDARD": "Standard",
    "GRADE_JAM": "For jam",
    "GRADE_DESC_PREMIUM": "Large, hand-picked select berries",
    "GRADE_DESC_STANDARD": "Fresh-picked this morning",
    "GRADE_DESC_JAM": "For jam and home preserves",
    "GRADE_TOUR_WALK": "Farm tour",
    "GRADE_TOUR_TASTE": "Tour + tasting",
    "EST_PRICE": "est. price",
    "PAY_SBP_GEN": "Generating QR code…",
    "PAY_SBP_GEN_SUB": "Please wait a few seconds",
    "PAY_CARD_HOLD": "Tap your card on the terminal and complete the payment",
    "DONE_THANKS": "Thank you for your order",
    "ORDER_NO": "Order",
    "COLLECT": "Collect your order at the pickup counter",
    "COLLECT_SUB": "Tell the farm staff your order number",
    "NEW_ORDER": "New order",
    "AUTO_RETURN": "Returning to home screen in",
    "SEC": "s",
    "QTY_LABEL": "Quantity",
    "CAT_TOURS": "Farm tours",
    "TOUR_DATES_TITLE": "Available dates",
    "TOUR_GUEST_ADULTS": "Adults",
    "TOUR_GUEST_KIDS": "Children under 15",
    "TOUR_GUEST_FREE": "Free",
    "TOUR_ADD": "Add to cart",
    "CART_TOUR_PHOTO": "photo • tour",
    "CART_TOUR_GUESTS": "Adults ×{adults} · children ×{kids} ({free})",
    "CART_TOUR_GUESTS_ADULTS": "Adults ×{adults}",
    "CART_TOUR_DATE": "Date: {date}",
    "TOUR_PICK_DATE": "Choose a tour date",
    "ADD_TO_CART": "Add",
    "TOUR_STEPS_TITLE": "What's included in the tour",
    "TOUR_GIFT_TITLE": "Gift at the end",
    "TOUR_GIFT_DESC": "Each family leaves with a kilo of freshly picked strawberries and a photo in the field.",
    "HUB_PROMO_LINE1": "All",
    "HUB_PROMO_LINE2": "together",
    "HUB_PROMO_SUB": "An hour in the beds, tasting and berries to take home",
    "CAT": {
        "strawberry": "Strawberry",
        "blueberry": "Blueberry",
        "raspberry": "Raspberry",
        "tours": "Farm tours",
    },
    "MONTHS_NOM": {6: "June", 7: "July", 8: "August"},
    "TOUR_DATES": ((6, (20, 27)), (7, (4,)), (8, (15, 22))),
    "TOUR_STEPS": (
        (
            "Welcome at the tent",
            "Each family receives a Sady Kolomny canvas bag; children get a «Young Agronomist» sticker.",
        ),
        (
            "Farm and plantation walk",
            "Meet three crops — strawberry, blueberry and raspberry. Learn how varieties like Asia, Ania, "
            "Mara des Bois, Florida Beauty and Murano differ, and why store berries can't match "
            "field-ripe fruit.",
        ),
        (
            "Strawberry tasting",
            "Varieties in season that day — fully ripe, straight from the bush.",
        ),
        (
            "Behind the scenes",
            "Sturgeon pond, drip irrigation, apiary and polytunnels from the inside. The «Katyusha» "
            "refrigerator truck that takes berries to Moscow on harvest day.",
        ),
    ),
    "DEFAULT_HOURS": "Daily 10:00–19:00",
}

STRINGS: dict[str, dict] = {"ru": _RU, "en": _EN}


class KolomnaLocale(QObject):
    changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._lang = "ru"

    def lang(self) -> str:
        return self._lang

    def set_lang(self, lang: str) -> None:
        lang = "en" if lang == "en" else "ru"
        if lang == self._lang:
            return
        self._lang = lang
        self.changed.emit(lang)


_locale = KolomnaLocale()


def locale() -> KolomnaLocale:
    return _locale


def get_lang() -> str:
    return _locale.lang()


def set_lang(lang: str) -> None:
    _locale.set_lang(lang)


def locale_changed():
    return _locale.changed


def strings() -> dict:
    return STRINGS[get_lang()]


def hub_label_for_slot(index: int) -> str:
    key = _HUB_KEYS[min(max(index, 0), len(_HUB_KEYS) - 1)]
    return STRINGS[get_lang()]["CAT"][key]


def n_items_label(count: int) -> str:
    if get_lang() == "en":
        return f"{count} item" if count == 1 else f"{count} items"
    n = abs(count) % 100
    b = n % 10
    if 11 <= n <= 14:
        word = "позиций"
    elif b == 1:
        word = "позиция"
    elif 2 <= b <= 4:
        word = "позиции"
    else:
        word = "позиций"
    return f"{count} {word}"
