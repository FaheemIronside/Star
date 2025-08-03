# keyboards.py
"""
Keyboard layouts for RajxStars Bot
"""

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict
import config

class Keyboards:
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎁 Bonus", callback_data="bonus"),
                InlineKeyboardButton("💰 Balance", callback_data="balance")
            ],
            [
                InlineKeyboardButton("👥 Refer", callback_data="refer"),
                InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")
            ],
            [
                InlineKeyboardButton("📞 Contact", url=config.CONTACT_ADMIN_URL)
            ]
        ])
    
    @staticmethod
    def back_menu() -> InlineKeyboardMarkup:
        """Back to main menu keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
        ])
    
    @staticmethod
    def bonus_menu() -> InlineKeyboardMarkup:
        """Bonus menu keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Claim", callback_data="claim_bonus")],
            [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
        ])
    
    @staticmethod
    def bonus_back() -> InlineKeyboardMarkup:
        """Back to bonus menu keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="bonus")]
        ])
    
    @staticmethod
    async def join_channels(channels: List[Dict]) -> InlineKeyboardMarkup:
        """Create join channels keyboard with 2x2 layout"""
        if not channels:
            return Keyboards.main_menu()
        
        keyboard = []
        
        # Create channel buttons in pairs (2x2 layout)
        for i in range(0, len(channels), 2):
            row = []
            for j in range(2):
                if i + j < len(channels):
                    ch = channels[i + j]
                    row.append(InlineKeyboardButton(f"📢 {ch['name']}", url=ch['link']))
            keyboard.append(row)
        
        # Add verify button
        keyboard.append([InlineKeyboardButton("✅ Verify Join", callback_data="verify_join")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Admin panel keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👥 Users", callback_data="admin_users"),
                InlineKeyboardButton("💸 Withdrawals", callback_data="admin_withdrawals")
            ],
            [
                InlineKeyboardButton("➕ Add Channel", callback_data="admin_add"),
                InlineKeyboardButton("➖ Remove Channel", callback_data="admin_remove")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton("📋 Channel List", callback_data="admin_channels")
            ]
        ])
    
    @staticmethod
    def admin_back() -> InlineKeyboardMarkup:
        """Back to admin menu keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
        ])
    
    @staticmethod
    def withdrawal_action(withdrawal_id: str) -> InlineKeyboardMarkup:
        """Withdrawal approval/rejection keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{withdrawal_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{withdrawal_id}")
            ]
        ])
    
    @staticmethod
    def remove_channels(channels: List[Dict]) -> InlineKeyboardMarkup:
        """Remove channels keyboard"""
        keyboard = []
        for ch in channels:
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ {ch['name']}", 
                    callback_data=f"remove_{ch['channel_id'][1:]}"  # Remove @ symbol
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_back")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def start_private() -> InlineKeyboardMarkup:
        """Start bot in private keyboard for groups"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Start Bot", url=f"https://t.me/{config.BOT_USERNAME}")]
        ])

# Create keyboards instance
kb = Keyboards()