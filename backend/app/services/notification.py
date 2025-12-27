import requests
from typing import Optional
from app.core.config import settings

class NotificationService:
    @staticmethod
    def send_telegram_message(message: str, chat_id: Optional[str] = None) -> bool:
        """
        Send a message via Telegram Bot.
        """
        token = settings.TELEGRAM_BOT_TOKEN
        # Use provided chat_id or default from settings
        target_chat_id = chat_id
        if not target_chat_id or target_chat_id == 'default':
            target_chat_id = settings.TELEGRAM_CHAT_ID
        
        if not token or not target_chat_id:
            print("⚠️ Telegram not configured. Skipping notification.")
            return False
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": target_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return False

    @staticmethod
    def format_alert_message(product_name: str, current_price: float, target_price: float, url: str) -> str:
        """Format the alert message with HTML."""
        return (
            f"🎯 <b>Price Drop Alert!</b>\n\n"
            f"📦 <b>{product_name}</b>\n"
            f"💰 Price: <b>₹{current_price:,.2f}</b>\n"
            f"🎯 Target: ₹{target_price:,.2f}\n\n"
            f"<a href='{url}'>👉 Buy Now</a>"
        )
