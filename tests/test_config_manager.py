"""
Deriv Rise/Fall Bot Pro - Test Suite
====================================

Unit tests for the configuration manager module.

Run with: pytest tests/ -v
Or: python -m pytest tests/ -v
"""

import pytest
import json
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_manager import (
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
    create_config_from_preset
)


class TestTradingConfig:
    """Tests for TradingConfig."""
    
    def test_default_values(self):
        """Test default trading configuration values."""
        config = TradingConfig()
        assert config.base_stake == 1.00
        assert config.contract_type == "rise_fall"
        assert config.contract_duration == 1
        assert config.duration_unit == "ticks"
        assert config.trading_asset == "R_100"
        assert config.trade_direction == "random"
    
    def test_custom_values(self):
        """Test custom trading configuration."""
        config = TradingConfig(
            base_stake=2.50,
            contract_duration=5,
            trading_asset="R_50"
        )
        assert config.base_stake == 2.50
        assert config.contract_duration == 5
        assert config.trading_asset == "R_50"


class TestMartingaleConfig:
    """Tests for MartingaleConfig."""
    
    def test_default_values(self):
        """Test default martingale configuration."""
        config = MartingaleConfig()
        assert config.enabled == True
        assert config.multiplier == 2.0
        assert config.max_steps == 5
        assert config.reset_on_win == True
    
    def test_disabled_martingale(self):
        """Test disabled martingale configuration."""
        config = MartingaleConfig(enabled=False)
        assert config.enabled == False


class TestRiskManagementConfig:
    """Tests for RiskManagementConfig."""
    
    def test_default_values(self):
        """Test default risk management configuration."""
        config = RiskManagementConfig()
        assert config.take_profit == 50.00
        assert config.stop_loss == 25.00
        assert config.max_consecutive_losses == 5
        assert config.min_balance_threshold == 10.00
        assert config.max_daily_trades == 0


class TestConfigValidator:
    """Tests for ConfigValidator."""
    
    def test_validate_positive_valid(self):
        """Test positive validation with valid value."""
        valid, msg = ConfigValidator.validate_positive(10.0, "Test")
        assert valid == True
        assert msg == ""
    
    def test_validate_positive_invalid(self):
        """Test positive validation with invalid value."""
        valid, msg = ConfigValidator.validate_positive(-5.0, "Test")
        assert valid == False
        assert "must be positive" in msg
    
    def test_validate_positive_zero(self):
        """Test positive validation with zero."""
        valid, msg = ConfigValidator.validate_positive(0, "Test")
        assert valid == False
    
    def test_validate_range_valid(self):
        """Test range validation with valid value."""
        valid, msg = ConfigValidator.validate_range(5.0, 1.0, 10.0, "Test")
        assert valid == True
    
    def test_validate_range_below(self):
        """Test range validation below minimum."""
        valid, msg = ConfigValidator.validate_range(0.5, 1.0, 10.0, "Test")
        assert valid == False
        assert "must be between" in msg
    
    def test_validate_range_above(self):
        """Test range validation above maximum."""
        valid, msg = ConfigValidator.validate_range(15.0, 1.0, 10.0, "Test")
        assert valid == False
    
    def test_validate_trading_config_valid(self):
        """Test trading config validation with valid config."""
        config = TradingConfig()
        errors = ConfigValidator.validate_trading_config(config)
        assert len(errors) == 0
    
    def test_validate_trading_config_invalid_stake(self):
        """Test trading config validation with invalid stake."""
        config = TradingConfig(base_stake=-1.0)
        errors = ConfigValidator.validate_trading_config(config)
        assert len(errors) > 0
        assert any("stake" in e.lower() for e in errors)
    
    def test_validate_trading_config_invalid_duration(self):
        """Test trading config validation with invalid duration."""
        config = TradingConfig(contract_duration=0)
        errors = ConfigValidator.validate_trading_config(config)
        assert len(errors) > 0
    
    def test_validate_trading_config_invalid_unit(self):
        """Test trading config validation with invalid duration unit."""
        config = TradingConfig(duration_unit="invalid")
        errors = ConfigValidator.validate_trading_config(config)
        assert len(errors) > 0
    
    def test_validate_martingale_config_valid(self):
        """Test martingale config validation with valid config."""
        config = MartingaleConfig()
        errors = ConfigValidator.validate_martingale_config(config)
        assert len(errors) == 0
    
    def test_validate_martingale_config_invalid_multiplier(self):
        """Test martingale config validation with invalid multiplier."""
        config = MartingaleConfig(multiplier=0.5)
        errors = ConfigValidator.validate_martingale_config(config)
        assert len(errors) > 0
    
    def test_validate_martingale_config_invalid_steps(self):
        """Test martingale config validation with invalid steps."""
        config = MartingaleConfig(max_steps=50)
        errors = ConfigValidator.validate_martingale_config(config)
        assert len(errors) > 0
    
    def test_validate_martingale_disabled_skips_validation(self):
        """Test that disabled martingale skips validation."""
        config = MartingaleConfig(enabled=False, multiplier=0.1, max_steps=100)
        errors = ConfigValidator.validate_martingale_config(config)
        assert len(errors) == 0
    
    def test_validate_risk_config_valid(self):
        """Test risk config validation with valid config."""
        config = RiskManagementConfig()
        errors = ConfigValidator.validate_risk_config(config)
        assert len(errors) == 0
    
    def test_validate_risk_config_invalid_take_profit(self):
        """Test risk config validation with invalid take profit."""
        config = RiskManagementConfig(take_profit=-10)
        errors = ConfigValidator.validate_risk_config(config)
        assert len(errors) > 0
    
    def test_validate_risk_config_invalid_stop_loss(self):
        """Test risk config validation with invalid stop loss."""
        config = RiskManagementConfig(stop_loss=0)
        errors = ConfigValidator.validate_risk_config(config)
        assert len(errors) > 0
    
    def test_validate_telegram_config_disabled(self):
        """Test telegram config validation when disabled."""
        config = TelegramConfig(enabled=False)
        errors = ConfigValidator.validate_telegram_config(config)
        assert len(errors) == 0
    
    def test_validate_telegram_config_enabled_no_token(self):
        """Test telegram config validation with missing token."""
        config = TelegramConfig(enabled=True)
        errors = ConfigValidator.validate_telegram_config(config)
        assert len(errors) > 0
        assert any("token" in e.lower() for e in errors)
    
    def test_validate_telegram_config_invalid_token_format(self):
        """Test telegram config validation with invalid token format."""
        config = TelegramConfig(
            enabled=True,
            bot_token="invalid_token_no_colon",
            chat_id="123456"
        )
        errors = ConfigValidator.validate_telegram_config(config)
        assert len(errors) > 0
    
    def test_validate_all_valid(self):
        """Test complete validation with valid config."""
        config = BotConfig()
        valid, errors = ConfigValidator.validate_all(config)
        assert valid == True
        assert len(errors) == 0
    
    def test_validate_all_invalid(self):
        """Test complete validation with invalid config."""
        config = BotConfig()
        config.trading.base_stake = -1
        config.martingale.multiplier = 0.5
        valid, errors = ConfigValidator.validate_all(config)
        assert valid == False
        assert len(errors) > 0


class TestPresetManager:
    """Tests for PresetManager."""
    
    def test_get_conservative_preset(self):
        """Test getting conservative preset."""
        preset = PresetManager.get_preset(RiskLevel.CONSERVATIVE)
        assert preset["trading"]["base_stake"] == 0.50
        assert preset["martingale"]["multiplier"] == 1.5
        assert preset["martingale"]["max_steps"] == 3
    
    def test_get_moderate_preset(self):
        """Test getting moderate preset."""
        preset = PresetManager.get_preset(RiskLevel.MODERATE)
        assert preset["trading"]["base_stake"] == 1.00
        assert preset["martingale"]["multiplier"] == 2.0
        assert preset["martingale"]["max_steps"] == 5
    
    def test_get_aggressive_preset(self):
        """Test getting aggressive preset."""
        preset = PresetManager.get_preset(RiskLevel.AGGRESSIVE)
        assert preset["trading"]["base_stake"] == 2.00
        assert preset["martingale"]["multiplier"] == 2.5
        assert preset["martingale"]["max_steps"] == 7
    
    def test_apply_preset_conservative(self):
        """Test applying conservative preset."""
        config = BotConfig()
        config = PresetManager.apply_preset(config, RiskLevel.CONSERVATIVE)
        assert config.trading.base_stake == 0.50
        assert config.martingale.multiplier == 1.5
        assert config.risk_level == RiskLevel.CONSERVATIVE
    
    def test_apply_preset_moderate(self):
        """Test applying moderate preset."""
        config = BotConfig()
        config = PresetManager.apply_preset(config, RiskLevel.MODERATE)
        assert config.trading.base_stake == 1.00
        assert config.martingale.multiplier == 2.0
        assert config.risk_level == RiskLevel.MODERATE
    
    def test_apply_preset_aggressive(self):
        """Test applying aggressive preset."""
        config = BotConfig()
        config = PresetManager.apply_preset(config, RiskLevel.AGGRESSIVE)
        assert config.trading.base_stake == 2.00
        assert config.martingale.multiplier == 2.5
        assert config.risk_level == RiskLevel.AGGRESSIVE
    
    def test_calculate_max_loss_no_martingale(self):
        """Test max loss calculation without martingale."""
        config = BotConfig()
        config.martingale.enabled = False
        config.trading.base_stake = 5.0
        max_loss = PresetManager.calculate_max_loss(config)
        assert max_loss == 5.0
    
    def test_calculate_max_loss_with_martingale(self):
        """Test max loss calculation with martingale."""
        config = BotConfig()
        config.trading.base_stake = 1.0
        config.martingale.enabled = True
        config.martingale.multiplier = 2.0
        config.martingale.max_steps = 5
        max_loss = PresetManager.calculate_max_loss(config)
        # 1 + 2 + 4 + 8 + 16 = 31
        assert max_loss == 31.0
    
    def test_get_recommended_balance(self):
        """Test recommended balance calculation."""
        config = BotConfig()
        config.trading.base_stake = 1.0
        config.martingale.multiplier = 2.0
        config.martingale.max_steps = 5
        rec_balance = PresetManager.get_recommended_balance(config)
        # 31 * 2 = 62
        assert rec_balance == 62.0
    
    def test_get_preset_description(self):
        """Test preset description retrieval."""
        desc = PresetManager.get_preset_description(RiskLevel.CONSERVATIVE)
        assert "CONSERVATIVE" in desc
        assert "Low" in desc


class TestConfigManager:
    """Tests for ConfigManager."""
    
    def test_init_default(self):
        """Test ConfigManager initialization."""
        manager = ConfigManager()
        assert manager.config is not None
        assert isinstance(manager.config, BotConfig)
    
    def test_apply_preset(self):
        """Test applying preset via manager."""
        manager = ConfigManager()
        manager.apply_preset(RiskLevel.AGGRESSIVE)
        assert manager.config.trading.base_stake == 2.00
        assert manager.config.risk_level == RiskLevel.AGGRESSIVE
    
    def test_validate(self):
        """Test validation via manager."""
        manager = ConfigManager()
        valid, errors = manager.validate()
        assert valid == True
    
    def test_get_summary(self):
        """Test summary generation."""
        manager = ConfigManager()
        summary = manager.get_summary()
        assert "DERIV RISE/FALL BOT PRO" in summary
        assert "Base Stake" in summary
        assert "Martingale" in summary
    
    def test_export_for_xml(self):
        """Test XML export format."""
        manager = ConfigManager()
        manager.config.trading.base_stake = 1.50
        manager.config.telegram.enabled = True
        
        export = manager.export_for_xml()
        
        assert export["base_stake"] == 1.50
        assert export["telegram_enabled"] == True
        assert "martingale_multiplier" in export
        assert "take_profit" in export
    
    def test_save_and_load(self, tmp_path):
        """Test saving and loading configuration."""
        config_path = tmp_path / "test_config.json"
        
        # Save configuration
        manager = ConfigManager(str(config_path))
        manager.apply_preset(RiskLevel.AGGRESSIVE)
        manager.config.trading.base_stake = 3.50
        assert manager.save() == True
        
        # Load configuration
        manager2 = ConfigManager(str(config_path))
        loaded_config = manager2.load()
        assert loaded_config.trading.base_stake == 3.50
        assert loaded_config.risk_level == RiskLevel.AGGRESSIVE
    
    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file."""
        manager = ConfigManager("/nonexistent/path/config.json")
        config = manager.load()
        # Should return default config
        assert config.trading.base_stake == 1.00


class TestHelperFunctions:
    """Tests for helper functions."""
    
    def test_create_default_config(self):
        """Test creating default configuration."""
        config = create_default_config()
        assert isinstance(config, BotConfig)
        assert config.trading.base_stake == 1.00
    
    def test_create_config_from_preset(self):
        """Test creating configuration from preset."""
        config = create_config_from_preset(RiskLevel.CONSERVATIVE)
        assert config.trading.base_stake == 0.50
        assert config.martingale.multiplier == 1.5


class TestMartingaleCalculations:
    """Tests for martingale stake calculations."""
    
    def test_stake_progression_2x(self):
        """Test 2x martingale stake progression."""
        base = 1.0
        multiplier = 2.0
        stakes = []
        stake = base
        for _ in range(5):
            stakes.append(stake)
            stake *= multiplier
        
        assert stakes == [1.0, 2.0, 4.0, 8.0, 16.0]
    
    def test_stake_progression_1_5x(self):
        """Test 1.5x martingale stake progression."""
        base = 1.0
        multiplier = 1.5
        stakes = []
        stake = base
        for _ in range(4):
            stakes.append(round(stake, 2))
            stake *= multiplier
        
        assert stakes == [1.0, 1.5, 2.25, 3.38]
    
    def test_total_loss_calculation(self):
        """Test total loss after consecutive losses."""
        base = 1.0
        multiplier = 2.0
        steps = 5
        
        total = 0
        stake = base
        for _ in range(steps):
            total += stake
            stake *= multiplier
        
        assert total == 31.0  # 1 + 2 + 4 + 8 + 16


class TestRiskAnalysis:
    """Tests for risk analysis calculations."""
    
    def test_win_rate_breakeven(self):
        """Test breakeven win rate calculation."""
        # With 95% payout and martingale, need to calculate
        # how often you need to win to break even
        payout = 0.95
        win_rate_needed = 1 / (1 + payout)
        assert round(win_rate_needed, 2) == 0.51  # ~51% win rate needed
    
    def test_risk_reward_ratio(self):
        """Test risk/reward ratio calculation."""
        take_profit = 50.0
        stop_loss = 25.0
        ratio = take_profit / stop_loss
        assert ratio == 2.0  # 2:1 reward to risk


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
