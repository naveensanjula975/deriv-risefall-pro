"""
Deriv Rise/Fall Bot Pro - Telegram Notification Helper
======================================================

This module provides Telegram notification functionality for the trading bot.
It can be used standalone for testing or integrated with the bot.

Usage:
    1. Set your BOT_TOKEN and CHAT_ID in the configuration
    2. Import and use the send_message function
    3. Or run this file directly to test notifications

Setup:
    1. Create a bot via @BotFather on Telegram
    2. Get your Chat ID via @userinfobot or @RawDataBot
    3. Configure the credentials below or use environment variables
"""

import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any
import os


class TelegramNotifier:
    """Telegram notification handler for Deriv Trading Bot."""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """
        Initialize the Telegram notifier.
        
        Args:
            bot_token: Telegram Bot API token from @BotFather
            chat_id: Your Telegram Chat ID
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.enabled = self.bot_token != 'YOUR_BOT_TOKEN' and self.chat_id != 'YOUR_CHAT_ID'
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> Dict[str, Any]:
        """
        Send a message to Telegram.
        
        Args:
            message: The message text to send
            parse_mode: Message format (HTML or Markdown)
        
        Returns:
            API response as dictionary
        """
        if not self.enabled:
            print(f"[TELEGRAM DISABLED] {message}")
            return {"ok": False, "error": "Telegram not configured"}
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}
    
    def send_win_alert(self, profit: float, total_profit: float, balance: float, 
                       trade_number: int = 0) -> Dict[str, Any]:
        """Send a win notification."""
        message = f"""
✅ <b>WIN TRADE #{trade_number}</b>

💰 Profit: <code>+${profit:.2f}</code>
📊 Total P/L: <code>${total_profit:.2f}</code>
💵 Balance: <code>${balance:.2f}</code>
🕐 Time: {datetime.now().strftime('%H:%M:%S')}
"""
        return self.send_message(message)
    
    def send_loss_alert(self, loss: float, total_profit: float, balance: float,
                        next_stake: float, martingale_step: int, 
                        trade_number: int = 0) -> Dict[str, Any]:
        """Send a loss notification."""
        message = f"""
❌ <b>LOSS TRADE #{trade_number}</b>

💸 Loss: <code>-${abs(loss):.2f}</code>
📊 Total P/L: <code>${total_profit:.2f}</code>
💵 Balance: <code>${balance:.2f}</code>
📈 Next Stake: <code>${next_stake:.2f}</code>
🔄 Martingale Step: {martingale_step}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}
"""
        return self.send_message(message)
    
    def send_bot_started(self, initial_balance: float, settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send bot started notification."""
        settings = settings or {}
        message = f"""
🤖 <b>BOT STARTED</b>

📍 Rise/Fall Bot Pro v1.0
💵 Initial Balance: <code>${initial_balance:.2f}</code>
💰 Base Stake: <code>${settings.get('base_stake', 1):.2f}</code>
🎯 Take Profit: <code>${settings.get('take_profit', 50):.2f}</code>
🛑 Stop Loss: <code>${settings.get('stop_loss', 25):.2f}</code>
📊 Martingale: {settings.get('multiplier', 2)}x (Max {settings.get('max_steps', 5)} steps)
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>Good luck! 🍀</i>
"""
        return self.send_message(message)
    
    def send_bot_stopped(self, reason: str, final_balance: float, 
                         total_profit: float, stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send bot stopped notification."""
        stats = stats or {}
        total_trades = stats.get('total_trades', 0)
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        emoji = "🎯" if "profit" in reason.lower() else "🛑" if "loss" in reason.lower() else "⚠️"
        
        message = f"""
{emoji} <b>BOT STOPPED</b>

📍 Reason: <code>{reason}</code>

📊 <b>SESSION SUMMARY</b>
━━━━━━━━━━━━━━━━━━
📈 Total Trades: {total_trades}
✅ Wins: {wins}
❌ Losses: {losses}
📊 Win Rate: {win_rate:.1f}%
━━━━━━━━━━━━━━━━━━
💵 Final Balance: <code>${final_balance:.2f}</code>
💰 Net P/L: <code>${total_profit:+.2f}</code>
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)
    
    def send_take_profit_reached(self, target: float, actual: float, 
                                  balance: float, stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send take profit reached notification."""
        stats = stats or {}
        message = f"""
🎯 <b>TAKE PROFIT REACHED!</b>

🏆 Target: <code>${target:.2f}</code>
💰 Achieved: <code>${actual:.2f}</code>
💵 Balance: <code>${balance:.2f}</code>
📈 Total Trades: {stats.get('total_trades', 0)}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

<i>Congratulations! 🎉</i>
"""
        return self.send_message(message)
    
    def send_stop_loss_triggered(self, limit: float, actual: float,
                                  balance: float, stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send stop loss triggered notification."""
        stats = stats or {}
        message = f"""
🛑 <b>STOP LOSS TRIGGERED!</b>

⚠️ Limit: <code>-${limit:.2f}</code>
💸 Actual Loss: <code>${actual:.2f}</code>
💵 Balance: <code>${balance:.2f}</code>
📉 Total Trades: {stats.get('total_trades', 0)}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

<i>Better luck next time! 💪</i>
"""
        return self.send_message(message)
    
    def send_max_losses_reached(self, consecutive: int, max_allowed: int,
                                 balance: float) -> Dict[str, Any]:
        """Send max consecutive losses notification."""
        message = f"""
⚠️ <b>MAX CONSECUTIVE LOSSES!</b>

🔴 Consecutive Losses: {consecutive}
📊 Max Allowed: {max_allowed}
💵 Balance: <code>${balance:.2f}</code>
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

<i>Bot stopped for safety.</i>
"""
        return self.send_message(message)
    
    def send_low_balance_alert(self, current: float, minimum: float) -> Dict[str, Any]:
        """Send low balance alert."""
        message = f"""
💰 <b>LOW BALANCE ALERT!</b>

💵 Current: <code>${current:.2f}</code>
⚠️ Minimum: <code>${minimum:.2f}</code>
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

<i>Bot stopped - insufficient balance.</i>
"""
        return self.send_message(message)
    
    def send_session_summary(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Send periodic session summary."""
        total_trades = stats.get('total_trades', 0)
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        profit_emoji = "📈" if stats.get('total_profit', 0) >= 0 else "📉"
        
        message = f"""
📊 <b>SESSION UPDATE</b>

{profit_emoji} P/L: <code>${stats.get('total_profit', 0):+.2f}</code>
💵 Balance: <code>${stats.get('balance', 0):.2f}</code>

📈 Trades: {total_trades}
✅ Wins: {wins} | ❌ Losses: {losses}
📊 Win Rate: {win_rate:.1f}%
🔄 Current Stake: <code>${stats.get('current_stake', 1):.2f}</code>

🕐 {datetime.now().strftime('%H:%M:%S')}
"""
        return self.send_message(message)
    
    def send_error_alert(self, error_type: str, details: str) -> Dict[str, Any]:
        """Send error notification."""
        message = f"""
🚨 <b>ERROR ALERT</b>

❌ Type: <code>{error_type}</code>
📝 Details: {details}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

<i>Please check the bot.</i>
"""
        return self.send_message(message)
    
    def test_connection(self) -> bool:
        """Test the Telegram connection."""
        if not self.enabled:
            print("Telegram is not configured. Please set BOT_TOKEN and CHAT_ID.")
            return False
        
        result = self.send_message("🔔 Test notification from Deriv Rise/Fall Bot Pro")
        if result.get("ok"):
            print("✅ Telegram connection successful!")
            return True
        else:
            print(f"❌ Telegram connection failed: {result.get('error', 'Unknown error')}")
            return False


# Standalone functions for simple usage
_default_notifier = None

def get_notifier(bot_token: str = None, chat_id: str = None) -> TelegramNotifier:
    """Get or create the default notifier instance."""
    global _default_notifier
    if _default_notifier is None or bot_token or chat_id:
        _default_notifier = TelegramNotifier(bot_token, chat_id)
    return _default_notifier

def send_telegram_message(message: str, bot_token: str = None, chat_id: str = None) -> Dict[str, Any]:
    """Quick function to send a Telegram message."""
    notifier = get_notifier(bot_token, chat_id)
    return notifier.send_message(message)


# URL Builder for Deriv DBot (for use in XML bot)
def build_telegram_url(bot_token: str, chat_id: str, message: str) -> str:
    """
    Build a Telegram API URL for use in Deriv DBot's Request block.
    
    This is useful for constructing the URL to use in the XML bot's
    HTTP request functionality.
    """
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    return f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={encoded_message}"


if __name__ == "__main__":
    print("=" * 50)
    print("Deriv Rise/Fall Bot Pro - Telegram Tester")
    print("=" * 50)
    print()
    
    # Configuration - Replace with your actual values
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN' or CHAT_ID == 'YOUR_CHAT_ID':
        print("⚠️  Please configure your Telegram credentials!")
        print()
        print("Options:")
        print("1. Set environment variables:")
        print("   TELEGRAM_BOT_TOKEN=your_token")
        print("   TELEGRAM_CHAT_ID=your_chat_id")
        print()
        print("2. Or edit this file and replace:")
        print("   'YOUR_BOT_TOKEN' with your actual bot token")
        print("   'YOUR_CHAT_ID' with your actual chat ID")
        print()
        print("How to get credentials:")
        print("1. Bot Token: Message @BotFather on Telegram")
        print("2. Chat ID: Message @userinfobot on Telegram")
        print()
    else:
        notifier = TelegramNotifier(BOT_TOKEN, CHAT_ID)
        
        print("Testing Telegram connection...")
        print()
        
        if notifier.test_connection():
            print()
            print("Sending sample notifications...")
            
            # Test bot started
            notifier.send_bot_started(1000.00, {
                'base_stake': 1.00,
                'take_profit': 50.00,
                'stop_loss': 25.00,
                'multiplier': 2,
                'max_steps': 5
            })
            
            print("✅ All test notifications sent!")
            print()
            print("Check your Telegram for the messages.")
