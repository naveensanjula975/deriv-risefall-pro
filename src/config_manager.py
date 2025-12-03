"""
Deriv Rise/Fall Bot Pro - Configuration Manager
===============================================

This module handles bot configuration, validation, and preset management.
It provides a clean interface for managing trading bot settings.

Features:
    - Configuration validation
    - Preset management (Conservative, Moderate, Aggressive)
    - Settings import/export
    - Runtime configuration updates
"""

import json
import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum


class RiskLevel(Enum):
    """Risk level presets."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"


@dataclass
class TradingConfig:
    """Trading configuration settings."""
    base_stake: float = 1.00
    contract_type: str = "rise_fall"
    contract_duration: int = 1
    duration_unit: str = "ticks"  # ticks, seconds, minutes
    trading_asset: str = "R_100"
    trade_direction: str = "random"  # random, rise, fall


@dataclass
class MartingaleConfig:
    """Martingale system configuration."""
    enabled: bool = True
    multiplier: float = 2.0
    max_steps: int = 5
    reset_on_win: bool = True


@dataclass
class RiskManagementConfig:
    """Risk management configuration."""
    take_profit: float = 50.00
    stop_loss: float = 25.00
    max_consecutive_losses: int = 5
    min_balance_threshold: float = 10.00
    max_daily_trades: int = 0  # 0 = unlimited


@dataclass
class TelegramConfig:
    """Telegram notification configuration."""
    enabled: bool = False
    bot_token: str = "YOUR_BOT_TOKEN"
    chat_id: str = "YOUR_CHAT_ID"
    notify_on_win: bool = True
    notify_on_loss: bool = True
    notify_on_start: bool = True
    notify_on_stop: bool = True
    notify_on_take_profit: bool = True
    notify_on_stop_loss: bool = True
    send_session_summary: bool = True


@dataclass
class BotConfig:
    """Complete bot configuration."""
    trading: TradingConfig = field(default_factory=TradingConfig)
    martingale: MartingaleConfig = field(default_factory=MartingaleConfig)
    risk_management: RiskManagementConfig = field(default_factory=RiskManagementConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    risk_level: RiskLevel = RiskLevel.MODERATE


class ConfigValidator:
    """Validates bot configuration settings."""
    
    @staticmethod
    def validate_positive(value: float, field_name: str) -> Tuple[bool, str]:
        """Validate that a value is positive."""
        if value <= 0:
            return False, f"{field_name} must be positive (got {value})"
        return True, ""
    
    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float, 
                       field_name: str) -> Tuple[bool, str]:
        """Validate that a value is within a range."""
        if value < min_val or value > max_val:
            return False, f"{field_name} must be between {min_val} and {max_val} (got {value})"
        return True, ""
    
    @staticmethod
    def validate_trading_config(config: TradingConfig) -> List[str]:
        """Validate trading configuration."""
        errors = []
        
        # Base stake validation
        valid, msg = ConfigValidator.validate_positive(config.base_stake, "Base stake")
        if not valid:
            errors.append(msg)
        
        # Stake range check (reasonable limits)
        valid, msg = ConfigValidator.validate_range(config.base_stake, 0.01, 10000, "Base stake")
        if not valid:
            errors.append(msg)
        
        # Duration validation
        if config.contract_duration < 1:
            errors.append(f"Contract duration must be at least 1 (got {config.contract_duration})")
        
        # Duration unit validation
        valid_units = ["ticks", "seconds", "minutes", "t", "s", "m"]
        if config.duration_unit.lower() not in valid_units:
            errors.append(f"Duration unit must be one of {valid_units} (got {config.duration_unit})")
        
        # Trade direction validation
        valid_directions = ["random", "rise", "fall", "call", "put"]
        if config.trade_direction.lower() not in valid_directions:
            errors.append(f"Trade direction must be one of {valid_directions}")
        
        return errors
    
    @staticmethod
    def validate_martingale_config(config: MartingaleConfig) -> List[str]:
        """Validate martingale configuration."""
        errors = []
        
        if config.enabled:
            # Multiplier validation
            valid, msg = ConfigValidator.validate_range(config.multiplier, 1.1, 10.0, "Multiplier")
            if not valid:
                errors.append(msg)
            
            # Max steps validation
            if config.max_steps < 1 or config.max_steps > 20:
                errors.append(f"Max martingale steps must be between 1 and 20 (got {config.max_steps})")
        
        return errors
    
    @staticmethod
    def validate_risk_config(config: RiskManagementConfig) -> List[str]:
        """Validate risk management configuration."""
        errors = []
        
        # Take profit validation
        valid, msg = ConfigValidator.validate_positive(config.take_profit, "Take profit")
        if not valid:
            errors.append(msg)
        
        # Stop loss validation
        valid, msg = ConfigValidator.validate_positive(config.stop_loss, "Stop loss")
        if not valid:
            errors.append(msg)
        
        # Max consecutive losses validation
        if config.max_consecutive_losses < 1:
            errors.append("Max consecutive losses must be at least 1")
        
        # Min balance validation
        valid, msg = ConfigValidator.validate_positive(config.min_balance_threshold, "Min balance threshold")
        if not valid:
            errors.append(msg)
        
        # Max daily trades validation (0 = unlimited)
        if config.max_daily_trades < 0:
            errors.append("Max daily trades cannot be negative")
        
        return errors
    
    @staticmethod
    def validate_telegram_config(config: TelegramConfig) -> List[str]:
        """Validate Telegram configuration."""
        errors = []
        
        if config.enabled:
            if not config.bot_token or config.bot_token == "YOUR_BOT_TOKEN":
                errors.append("Telegram bot token is not configured")
            
            if not config.chat_id or config.chat_id == "YOUR_CHAT_ID":
                errors.append("Telegram chat ID is not configured")
            
            # Basic token format validation
            if config.bot_token and ":" not in config.bot_token:
                errors.append("Telegram bot token format appears invalid (should contain ':')")
        
        return errors
    
    @staticmethod
    def validate_all(config: BotConfig) -> Tuple[bool, List[str]]:
        """Validate complete bot configuration."""
        errors = []
        
        errors.extend(ConfigValidator.validate_trading_config(config.trading))
        errors.extend(ConfigValidator.validate_martingale_config(config.martingale))
        errors.extend(ConfigValidator.validate_risk_config(config.risk_management))
        errors.extend(ConfigValidator.validate_telegram_config(config.telegram))
        
        return len(errors) == 0, errors


class PresetManager:
    """Manages preset configurations."""
    
    PRESETS = {
        RiskLevel.CONSERVATIVE: {
            "trading": {"base_stake": 0.50},
            "martingale": {"multiplier": 1.5, "max_steps": 3},
            "risk_management": {
                "take_profit": 25.00,
                "stop_loss": 15.00,
                "max_consecutive_losses": 3
            }
        },
        RiskLevel.MODERATE: {
            "trading": {"base_stake": 1.00},
            "martingale": {"multiplier": 2.0, "max_steps": 5},
            "risk_management": {
                "take_profit": 50.00,
                "stop_loss": 25.00,
                "max_consecutive_losses": 5
            }
        },
        RiskLevel.AGGRESSIVE: {
            "trading": {"base_stake": 2.00},
            "martingale": {"multiplier": 2.5, "max_steps": 7},
            "risk_management": {
                "take_profit": 100.00,
                "stop_loss": 50.00,
                "max_consecutive_losses": 7
            }
        }
    }
    
    @classmethod
    def get_preset(cls, level: RiskLevel) -> Dict[str, Any]:
        """Get preset configuration for a risk level."""
        return cls.PRESETS.get(level, cls.PRESETS[RiskLevel.MODERATE])
    
    @classmethod
    def apply_preset(cls, config: BotConfig, level: RiskLevel) -> BotConfig:
        """Apply a preset to a configuration."""
        preset = cls.get_preset(level)
        
        # Apply trading settings
        if "trading" in preset:
            for key, value in preset["trading"].items():
                setattr(config.trading, key, value)
        
        # Apply martingale settings
        if "martingale" in preset:
            for key, value in preset["martingale"].items():
                setattr(config.martingale, key, value)
        
        # Apply risk management settings
        if "risk_management" in preset:
            for key, value in preset["risk_management"].items():
                setattr(config.risk_management, key, value)
        
        config.risk_level = level
        return config
    
    @classmethod
    def get_preset_description(cls, level: RiskLevel) -> str:
        """Get a description of a preset."""
        descriptions = {
            RiskLevel.CONSERVATIVE: """
🟢 CONSERVATIVE (Low Risk)
━━━━━━━━━━━━━━━━━━━━━━━━
• Base Stake: $0.50
• Multiplier: 1.5x
• Max Steps: 3
• Take Profit: $25
• Stop Loss: $15
• Best for: Beginners, small accounts
• Risk: Low | Reward: Low
""",
            RiskLevel.MODERATE: """
🟡 MODERATE (Balanced)
━━━━━━━━━━━━━━━━━━━━━━━━
• Base Stake: $1.00
• Multiplier: 2.0x
• Max Steps: 5
• Take Profit: $50
• Stop Loss: $25
• Best for: Most traders
• Risk: Medium | Reward: Medium
""",
            RiskLevel.AGGRESSIVE: """
🔴 AGGRESSIVE (High Risk)
━━━━━━━━━━━━━━━━━━━━━━━━
• Base Stake: $2.00
• Multiplier: 2.5x
• Max Steps: 7
• Take Profit: $100
• Stop Loss: $50
• Best for: Experienced, large accounts
• Risk: High | Reward: High
"""
        }
        return descriptions.get(level, "Custom configuration")
    
    @classmethod
    def calculate_max_loss(cls, config: BotConfig) -> float:
        """Calculate maximum possible loss for current settings."""
        if not config.martingale.enabled:
            return config.trading.base_stake
        
        total = 0
        stake = config.trading.base_stake
        for _ in range(config.martingale.max_steps):
            total += stake
            stake *= config.martingale.multiplier
        
        return total
    
    @classmethod
    def get_recommended_balance(cls, config: BotConfig, safety_factor: float = 2.0) -> float:
        """Calculate recommended minimum balance."""
        max_loss = cls.calculate_max_loss(config)
        return max_loss * safety_factor


class ConfigManager:
    """Main configuration manager for the bot."""
    
    def __init__(self, config_path: str = None):
        """Initialize the configuration manager."""
        self.config_path = config_path
        self.config = BotConfig()
        self.validator = ConfigValidator()
        self.preset_manager = PresetManager()
    
    def load(self, path: str = None) -> BotConfig:
        """Load configuration from a JSON file."""
        path = path or self.config_path
        
        if not path or not os.path.exists(path):
            return self.config
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            self.config = self._dict_to_config(data)
            return self.config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            return self.config
    
    def save(self, path: str = None) -> bool:
        """Save configuration to a JSON file."""
        path = path or self.config_path
        
        if not path:
            return False
        
        try:
            data = self._config_to_dict(self.config)
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate current configuration."""
        return self.validator.validate_all(self.config)
    
    def apply_preset(self, level: RiskLevel) -> None:
        """Apply a risk level preset."""
        self.config = self.preset_manager.apply_preset(self.config, level)
    
    def get_summary(self) -> str:
        """Get a summary of current configuration."""
        max_loss = self.preset_manager.calculate_max_loss(self.config)
        rec_balance = self.preset_manager.get_recommended_balance(self.config)
        
        return f"""
╔══════════════════════════════════════════════════════╗
║         DERIV RISE/FALL BOT PRO - CONFIG             ║
╠══════════════════════════════════════════════════════╣
║  TRADING SETTINGS                                    ║
║  ─────────────────                                   ║
║  Base Stake:      ${self.config.trading.base_stake:.2f}
║  Asset:           {self.config.trading.trading_asset}
║  Duration:        {self.config.trading.contract_duration} {self.config.trading.duration_unit}
║  Direction:       {self.config.trading.trade_direction}
╠══════════════════════════════════════════════════════╣
║  MARTINGALE SETTINGS                                 ║
║  ───────────────────                                 ║
║  Enabled:         {'Yes' if self.config.martingale.enabled else 'No'}
║  Multiplier:      {self.config.martingale.multiplier}x
║  Max Steps:       {self.config.martingale.max_steps}
╠══════════════════════════════════════════════════════╣
║  RISK MANAGEMENT                                     ║
║  ────────────────                                    ║
║  Take Profit:     ${self.config.risk_management.take_profit:.2f}
║  Stop Loss:       ${self.config.risk_management.stop_loss:.2f}
║  Max Consec Loss: {self.config.risk_management.max_consecutive_losses}
║  Min Balance:     ${self.config.risk_management.min_balance_threshold:.2f}
╠══════════════════════════════════════════════════════╣
║  RISK ANALYSIS                                       ║
║  ─────────────                                       ║
║  Max Possible Loss: ${max_loss:.2f}
║  Recommended Bal:   ${rec_balance:.2f}
║  Risk Level:        {self.config.risk_level.value.upper()}
╠══════════════════════════════════════════════════════╣
║  TELEGRAM                                            ║
║  ────────                                            ║
║  Enabled:         {'Yes' if self.config.telegram.enabled else 'No'}
╚══════════════════════════════════════════════════════╝
"""
    
    def _config_to_dict(self, config: BotConfig) -> Dict[str, Any]:
        """Convert config object to dictionary."""
        return {
            "trading": asdict(config.trading),
            "martingale": asdict(config.martingale),
            "risk_management": asdict(config.risk_management),
            "telegram": asdict(config.telegram),
            "risk_level": config.risk_level.value
        }
    
    def _dict_to_config(self, data: Dict[str, Any]) -> BotConfig:
        """Convert dictionary to config object."""
        config = BotConfig()
        
        if "trading" in data:
            config.trading = TradingConfig(**data["trading"])
        if "martingale" in data:
            config.martingale = MartingaleConfig(**data["martingale"])
        if "risk_management" in data:
            config.risk_management = RiskManagementConfig(**data["risk_management"])
        if "telegram" in data:
            config.telegram = TelegramConfig(**data["telegram"])
        if "risk_level" in data:
            config.risk_level = RiskLevel(data["risk_level"])
        
        return config
    
    def export_for_xml(self) -> Dict[str, Any]:
        """Export configuration in a format suitable for XML bot."""
        return {
            "base_stake": self.config.trading.base_stake,
            "duration_value": self.config.trading.contract_duration,
            "duration_type": self.config.trading.duration_unit[0],  # First letter
            "symbol": self.config.trading.trading_asset,
            "martingale_enabled": self.config.martingale.enabled,
            "martingale_multiplier": self.config.martingale.multiplier,
            "max_martingale_steps": self.config.martingale.max_steps,
            "take_profit": self.config.risk_management.take_profit,
            "stop_loss": self.config.risk_management.stop_loss,
            "max_consecutive_losses": self.config.risk_management.max_consecutive_losses,
            "min_balance": self.config.risk_management.min_balance_threshold,
            "telegram_enabled": self.config.telegram.enabled,
            "telegram_token": self.config.telegram.bot_token,
            "telegram_chat_id": self.config.telegram.chat_id
        }


# Available trading assets
AVAILABLE_ASSETS = {
    "volatility_indices": [
        {"id": "R_10", "name": "Volatility 10 Index", "min_stake": 0.35},
        {"id": "R_25", "name": "Volatility 25 Index", "min_stake": 0.35},
        {"id": "R_50", "name": "Volatility 50 Index", "min_stake": 0.35},
        {"id": "R_75", "name": "Volatility 75 Index", "min_stake": 0.35},
        {"id": "R_100", "name": "Volatility 100 Index", "min_stake": 0.35},
        {"id": "1HZ10V", "name": "Volatility 10 (1s) Index", "min_stake": 0.35},
        {"id": "1HZ25V", "name": "Volatility 25 (1s) Index", "min_stake": 0.35},
        {"id": "1HZ50V", "name": "Volatility 50 (1s) Index", "min_stake": 0.35},
        {"id": "1HZ75V", "name": "Volatility 75 (1s) Index", "min_stake": 0.35},
        {"id": "1HZ100V", "name": "Volatility 100 (1s) Index", "min_stake": 0.35},
    ],
    "crash_boom": [
        {"id": "BOOM300N", "name": "Boom 300 Index", "min_stake": 0.35},
        {"id": "BOOM500", "name": "Boom 500 Index", "min_stake": 0.35},
        {"id": "BOOM1000", "name": "Boom 1000 Index", "min_stake": 0.35},
        {"id": "CRASH300N", "name": "Crash 300 Index", "min_stake": 0.35},
        {"id": "CRASH500", "name": "Crash 500 Index", "min_stake": 0.35},
        {"id": "CRASH1000", "name": "Crash 1000 Index", "min_stake": 0.35},
    ],
    "step_indices": [
        {"id": "stpRNG", "name": "Step Index", "min_stake": 0.35},
    ],
    "jump_indices": [
        {"id": "JD10", "name": "Jump 10 Index", "min_stake": 0.35},
        {"id": "JD25", "name": "Jump 25 Index", "min_stake": 0.35},
        {"id": "JD50", "name": "Jump 50 Index", "min_stake": 0.35},
        {"id": "JD75", "name": "Jump 75 Index", "min_stake": 0.35},
        {"id": "JD100", "name": "Jump 100 Index", "min_stake": 0.35},
    ]
}


def create_default_config() -> BotConfig:
    """Create a default configuration."""
    return BotConfig()


def create_config_from_preset(level: RiskLevel) -> BotConfig:
    """Create a configuration from a preset."""
    config = BotConfig()
    return PresetManager.apply_preset(config, level)


if __name__ == "__main__":
    print("=" * 60)
    print("Deriv Rise/Fall Bot Pro - Configuration Manager")
    print("=" * 60)
    print()
    
    # Create and display configurations
    manager = ConfigManager()
    
    # Show all presets
    print("Available Risk Presets:")
    print("-" * 40)
    
    for level in [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]:
        print(PresetManager.get_preset_description(level))
    
    # Apply moderate preset and show summary
    print("\n" + "=" * 60)
    print("Current Configuration (Moderate Preset)")
    print("=" * 60)
    
    manager.apply_preset(RiskLevel.MODERATE)
    print(manager.get_summary())
    
    # Validate configuration
    is_valid, errors = manager.validate()
    print(f"\nConfiguration Valid: {'✅ Yes' if is_valid else '❌ No'}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
