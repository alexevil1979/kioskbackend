from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
KIOSK_W = 1080
KIOSK_H = 1920


@dataclass
class AppConfig:
    title: str = "Сады Коломны — киоск"
    # kolomna | katusha
    ui_theme: str = "kolomna"
    fullscreen: bool = True
    # portrait: вертикальный киоск (32" 1080×1920)
    orientation: str = "portrait"
    screen_width: int = 1080
    screen_height: int = 1920
    # Тест на ПК: рабочая область 1:1 с референсом screen_katusha.png
    dev_mode: bool = False
    viewport_width: int = 499
    viewport_height: int = 913
    # primary | left | right | 0..N (индекс слева направо)
    screen_position: str = "primary"
    screen_index: int | None = None

    @property
    def kiosk_scale(self) -> float:
        """Масштаб по ширине viewport (как offline-референс / scale() в kolomna_tokens)."""
        if not self.dev_mode:
            return 1.0
        return self.viewport_width / KIOSK_W

    @property
    def content_width(self) -> int:
        if self.dev_mode:
            return self.viewport_width
        return self.screen_width

    @property
    def content_height(self) -> int:
        if self.dev_mode:
            return self.viewport_height
        return self.screen_height

    @property
    def phone_layout(self) -> bool:
        """Вёрстка mini app (499×913), не масштаб киоска 1080."""
        return self.dev_mode


@dataclass
class IdleConfig:
    warning_seconds: int = 50
    reset_seconds: int = 60


@dataclass
class SuccessConfig:
    auto_return_min_sec: int = 5
    auto_return_max_sec: int = 8


@dataclass
class CatalogConfig:
    poll_interval_sec: int = 30
    media_dir: str = "media/products"
    # Тест покупок: игнор API-доступности и остатков, все товары продаваемы.
    purchase_test_mode: bool = False
    test_stock_qty: int = 5


@dataclass
class CrmConfig:
    base_url: str = ""
    api_key: str = ""
    kiosk_id: str = ""
    timeout_sec: int = 10
    use_mock: bool = True
    # split — GET /categories + GET /products; combined — GET /kiosk/catalog
    catalog_mode: str = "split"
    order_poll_interval_sec: int = 2


@dataclass
class SbpConfig:
    terminal_key: str = ""
    password: str = ""
    api_url: str = "https://securepay.tinkoff.ru/v2"
    use_mock: bool = True


@dataclass
class PaymentConfig:
    sbp_timeout_sec: int = 120
    card_terminal_path: str = ""
    sbp: SbpConfig = field(default_factory=SbpConfig)
    # Сырой лог запросов/ответов API при оплате СБП (QR)
    qr_api_trace_enabled: bool = True
    qr_api_trace_file: str = "logs/payment_qr_api.log"


@dataclass
class FiscalConfig:
    enabled: bool = False
    # umka | cloudkassir | tbusiness | none
    provider: str = "none"
    use_mock: bool = True
    # УМКА (только legacy_umka)
    host: str = "192.168.1.100"
    port: int = 58088
    use_https: bool = False
    cashier_login: str = "1"
    cashier_password: str = "1"
    use_test_server: bool = False
    test_host: str = "office.armax.ru"
    test_port: int = 58088
    # Облако (tbank_pos_printer)
    cloud_public_id: str = ""
    cloud_api_secret: str = ""


@dataclass
class HardwareNetworkConfig:
    lan_subnet: str = "192.168.1.0/24"
    gateway: str = "192.168.1.1"


@dataclass
class HardwareNucConfig:
    lan_ip: str = "192.168.1.10"


@dataclass
class HardwareUmkaConfig:
    host: str = "192.168.1.100"
    port: int = 58088


@dataclass
class HardwarePrinterConfig:
    enabled: bool = False
    host: str = "192.168.1.101"
    port: int = 9100
    connection: str = "usb"  # usb | ethernet
    # Имя очереди в Windows («Устройства и принтеры»). Пусто — принтер по умолчанию.
    windows_name: str = ""
    # RAW — ESC/POS байты напрямую (CP866, как на самотесте HS-K33); TEXT — только латиница
    windows_datatype: str = "RAW"
    windows_encoding: str = "cp866"
    # HSPOS code page id для ESC t n: 7=CP866, 6=WCP1251 (-1 = авто из windows_encoding)
    windows_codepage_id: int = -1
    # USB: spooler (драйвер POS80L/HSPOS RAW) | direct (USB001) | direct_first
    windows_usb_transport: str = "spooler"
    # Устарело: true → direct_first. Лучше windows_usb_transport.
    windows_use_direct_port: bool = False
    # Вручную: USB001, COM3 — если пусто, берётся из свойств принтера в Windows
    windows_port: str = ""
    # Отправлять ESC t n перед текстом
    windows_escpos_table: bool = True
    # True: добавить ESC @ перед ESC t (обычно не нужен на HS-K33)
    windows_escpos_codepage: bool = False
    # Оплаченный заказ для тестовой печати чека из API (админка)
    sample_paid_order_id: int = 2680
    # Ширина QR-растра для 80 мм (точек); 0 — не масштабировать
    qr_raster_width: int = 384


@dataclass
class HardwareTbankTerminalConfig:
    host: str = "192.168.1.102"
    port: int = 27015
    smart_sale_enabled: bool = False
    use_mock: bool = True


@dataclass
class HardwareAqsiConfig:
    api_base: str = "https://api.aqsi.ru"
    api_key: str = ""
    use_mock: bool = True
    timeout_sec: int = 30
    poll_interval_sec: int = 2
    poll_max_sec: int = 180


@dataclass
class HardwareConfig:
    # tbank_aqsi | tbank_pos_printer | tbank_pos_sbp | legacy_umka
    integration_mode: str = "tbank_aqsi"
    network: HardwareNetworkConfig = field(default_factory=HardwareNetworkConfig)
    nuc: HardwareNucConfig = field(default_factory=HardwareNucConfig)
    umka: HardwareUmkaConfig = field(default_factory=HardwareUmkaConfig)
    printer: HardwarePrinterConfig = field(default_factory=HardwarePrinterConfig)
    tbank_terminal: HardwareTbankTerminalConfig = field(default_factory=HardwareTbankTerminalConfig)
    aqsi: HardwareAqsiConfig = field(default_factory=HardwareAqsiConfig)

    @property
    def uses_umka(self) -> bool:
        return self.integration_mode == "legacy_umka"

    @property
    def uses_aqsi(self) -> bool:
        return self.integration_mode == "tbank_aqsi"

    @property
    def uses_pos_printer(self) -> bool:
        return self.integration_mode == "tbank_pos_printer"

    @property
    def uses_external_printer(self) -> bool:
        return self.uses_pos_printer and self.printer.enabled


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "logs/kiosk.log"
    max_bytes: int = 5_242_880
    backup_count: int = 3


@dataclass
class KioskConfig:
    block_keys: bool = True
    admin_pin: str = "1111"
    # Телефон поддержки на экране ошибки оплаты
    support_phone: str = ""
    show_support_phone_on_payment_error: bool = True


@dataclass
class Settings:
    app: AppConfig = field(default_factory=AppConfig)
    idle: IdleConfig = field(default_factory=IdleConfig)
    success: SuccessConfig = field(default_factory=SuccessConfig)
    catalog: CatalogConfig = field(default_factory=CatalogConfig)
    crm: CrmConfig = field(default_factory=CrmConfig)
    payment: PaymentConfig = field(default_factory=PaymentConfig)
    fiscal: FiscalConfig = field(default_factory=FiscalConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    kiosk: KioskConfig = field(default_factory=KioskConfig)

    @property
    def media_path(self) -> Path:
        p = ROOT / self.catalog.media_dir
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def log_path(self) -> Path:
        p = ROOT / self.logging.file
        p.parent.mkdir(parents=True, exist_ok=True)
        return p


def _merge_dataclass(dc_instance: Any, data: dict[str, Any]) -> None:
    for key, value in data.items():
        if not hasattr(dc_instance, key):
            continue
        current = getattr(dc_instance, key)
        if hasattr(current, "__dataclass_fields__") and isinstance(value, dict):
            _merge_dataclass(current, value)
        else:
            setattr(dc_instance, key, value)


def load_settings(path: Path | None = None) -> Settings:
    from src.core.env import apply_env_overrides, load_dotenv_file

    load_dotenv_file(ROOT)

    settings = Settings()
    cfg_path = path or ROOT / "config" / "settings.yaml"
    example = ROOT / "config" / "settings.yaml.example"
    if not cfg_path.exists() and example.exists():
        cfg_path = example
    if cfg_path.exists():
        with cfg_path.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        for section, values in raw.items():
            if hasattr(settings, section) and isinstance(values, dict):
                _merge_dataclass(getattr(settings, section), values)

    apply_env_overrides(settings)
    return settings
