"""
Deriv Rise/Fall Bot Pro - Source Package
========================================

This package contains utility modules for the Deriv trading bot.

Modules:
    - telegram_notifier: Telegram notification functionality
    - config_manager: Configuration and preset management
"""

__version__ = "1.0.0"
__author__ = "Deriv Rise/Fall Bot Pro Team"

from .telegram_notifier import TelegramNotifier, send_telegram_message, get_notifier
from .config_manager import (
    ConfigManager,
    ConfigValidator,
    PresetManager,
    BotConfig,
    TradingConfig,
    MartingaleConfig,
    RiskManagementConfig,
    TelegramConfig,
    RiskLevel,
    create_default_config,
    create_config_from_preset,
    AVAILABLE_ASSETS
)

__all__ = [
    # Telegram
    'TelegramNotifier',
    'send_telegram_message', 
    'get_notifier',
    # Config
    'ConfigManager',
    'ConfigValidator',
    'PresetManager',
    'BotConfig',
    'TradingConfig',
    'MartingaleConfig',
    'RiskManagementConfig',
    'TelegramConfig',
    'RiskLevel',
    'create_default_config',
    'create_config_from_preset',
    'AVAILABLE_ASSETS',
    # Meta
    '__version__'
]
