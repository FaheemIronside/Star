# utils.py
"""
Utility functions for RajxStars Bot
"""

import random
import string
import re
from datetime import datetime
from typing import Dict
from pyrogram.errors import UserNotParticipant
import config

class Utils:
    @staticmethod
    def generate_id(length: int = 8) -> str:
        """Generate random ID"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def format_time(seconds: int) -> str:
        """Format seconds to readable time"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}h {minutes:02d}m {secs:02d}s"
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate Telegram username format"""
        if username.startswith('@'):
            username = username[1:]
        return bool(re.match(r'^[a-zA-Z0-9_]{5,32}$', username))
    
    @staticmethod
    def clean_username(username: str) -> str:
        """Clean and format username"""
        if username.startswith('@'):
            return username[1:]
        return username
    
    @staticmethod
    def get_current_time() -> str:
        """Get current time formatted"""
        return datetime.utcnow().strftime("%I:%M %p")
    
    @staticmethod
    def get_current_date() -> str:
        """Get current date formatted"""
        return datetime.utcnow().strftime("%Y-%m-%d")
    
    @staticmethod
    def create_user_data(user_id: int, first_name: str, username: str, referred_by: int = None) -> Dict:
        """Create user data dictionary"""
        return {
            "user_id": user_id,
            "first_name": first_name,
            "username": username or "N/A",
            "balance": 0,
            "total_referrals": 0,
            "last_bonus": None,
            "joined_at": datetime.utcnow(),
            "referred_by": referred_by
        }
    
    @staticmethod
    def create_withdrawal_data(withdrawal_id: str, user_id: int, username: str, amount: int) -> Dict:
        """Create withdrawal data dictionary"""
        return {
            "withdrawal_id": withdrawal_id,
            "user_id": user_id,
            "username": f"@{username}",
            "amount": amount,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_channel_data(name: str, link: str, channel_id: str) -> Dict:
        """Create channel data dictionary"""
        return {
            "name": name,
            "link": link,
            "channel_id": channel_id
        }
    
    @staticmethod
    async def check_membership(app, user_id: int, channels: list) -> bool:
        """Check if user is member of all channels"""
        for ch in channels:
            try:
                member = await app.get_chat_member(ch['channel_id'], user_id)
                if member.status in ["left", "kicked"]:
                    return False
            except (UserNotParticipant, Exception):
                return False
        return True
    
    @staticmethod
    def can_claim_bonus(last_claim) -> bool:
        """Check if user can claim bonus"""
        if not last_claim:
            return True
        
        now = datetime.utcnow()
        time_diff = (now - last_claim).total_seconds()
        return time_diff >= config.BONUS_COOLDOWN
    
    @staticmethod
    def get_bonus_remaining_time(last_claim) -> int:
        """Get remaining time for next bonus claim"""
        if not last_claim:
            return 0
        
        now = datetime.utcnow()
        elapsed = (now - last_claim).total_seconds()
        remaining = config.BONUS_COOLDOWN - elapsed
        return max(0, int(remaining))
    
    @staticmethod
    def extract_channel_username(link: str) -> str:
        """Extract channel username from link"""
        return link.split('/')[-1]
    
    @staticmethod
    def is_valid_telegram_link(link: str) -> bool:
        """Check if link is valid Telegram link"""
        return link.startswith('https://t.me/')
    
    @staticmethod
    def format_referral_link(user_id: int) -> str:
        """Format referral link"""
        return f"https://t.me/{config.BOT_USERNAME}?start={user_id}"

# Create utils instance
utils = Utils()