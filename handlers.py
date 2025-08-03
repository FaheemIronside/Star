# handlers.py
"""
Message and callback handlers for RajxStars Bot
"""

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from datetime import datetime
from database import db
from keyboards import kb
from utils import utils
import config

# User state storage
user_states = {}

class Handlers:
    def __init__(self, app):
        self.app = app
        self.register_handlers()
    
    def register_handlers(self):
        """Register all handlers"""
        # Message handlers
        self.app.on_message(filters.command("start") & filters.private)(self.start_command)
        self.app.on_message(filters.command("start") & filters.group)(self.group_start)
        self.app.on_message(filters.text & filters.private)(self.handle_text)
        
        # Admin commands
        self.app.on_message(filters.command("adminhelp") & filters.user(config.ADMIN_ID))(self.admin_help)
        self.app.on_message(filters.command("stats") & filters.user(config.ADMIN_ID))(self.bot_stats)
        
        # Callback handlers
        self.app.on_callback_query(filters.regex("verify_join"))(self.verify_join)
        self.app.on_callback_query(filters.regex("main_menu"))(self.main_menu)
        self.app.on_callback_query(filters.regex("bonus"))(self.bonus_menu)
        self.app.on_callback_query(filters.regex("claim_bonus"))(self.claim_bonus)
        self.app.on_callback_query(filters.regex("balance"))(self.balance_menu)
        self.app.on_callback_query(filters.regex("refer"))(self.refer_menu)
        self.app.on_callback_query(filters.regex("withdraw"))(self.withdraw_menu)
        
        # Admin callbacks
        self.app.on_callback_query(filters.regex("admin_") & filters.user(config.ADMIN_ID))(self.admin_callbacks)
        self.app.on_callback_query(filters.regex(r"approve_|reject_"))(self.handle_withdrawal)
        self.app.on_callback_query(filters.regex(r"remove_"))(self.remove_channel)
    
    async def start_command(self, client, message: Message):
        """Handle /start command"""
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        username = message.from_user.username
        
        # Get or create user
        user = await db.get_user(user_id)
        
        # Handle referral
        if len(message.command) > 1 and not user:
            try:
                ref_id = int(message.command[1])
                if ref_id != user_id:
                    await db.inc_user(ref_id, {
                        "balance": config.REFERRAL_BONUS,
                        "total_referrals": 1
                    })
            except:
                pass
        
        # Create new user if doesn't exist
        if not user:
            user_data = utils.create_user_data(user_id, first_name, username)
            await db.create_user(user_data)
        
        # Check channels and membership
        channels = await db.get_channels()
        
        if channels and not await utils.check_membership(client, user_id, channels):
            # Show join channels message
            caption = config.START_MESSAGE.format(first_name=first_name)
            keyboard = await kb.join_channels(channels)
            
            await message.reply_text(
                caption,
                reply_markup=keyboard,
                parse_mode="markdown"
            )
        else:
            # Show main menu
            welcome = config.WELCOME_MESSAGE.format(first_name=first_name)
            await message.reply_text(
                welcome,
                reply_markup=kb.main_menu(),
                parse_mode="markdown"
            )
    
    async def group_start(self, client, message: Message):
        """Handle /start in groups"""
        await message.reply_text(
            "**🤖 I work in private messages only!**",
            reply_markup=kb.start_private(),
            parse_mode="markdown"
        )
    
    async def verify_join(self, client, callback_query: CallbackQuery):
        """Verify channel membership"""
        user_id = callback_query.from_user.id
        channels = await db.get_channels()
        
        if await utils.check_membership(client, user_id, channels):
            first_name = callback_query.from_user.first_name
            welcome = config.WELCOME_MESSAGE.format(first_name=first_name)
            
            await callback_query.edit_message_text(
                welcome,
                reply_markup=kb.main_menu(),
                parse_mode="markdown"
            )
        else:
            await callback_query.answer(
                "❌ Please join all channels first!",
                show_alert=True
            )
    
    async def main_menu(self, client, callback_query: CallbackQuery):
        """Show main menu"""
        first_name = callback_query.from_user.first_name
        welcome = config.WELCOME_MESSAGE.format(first_name=first_name)
        
        await callback_query.edit_message_text(
            welcome,
            reply_markup=kb.main_menu(),
            parse_mode="markdown"
        )
    
    async def bonus_menu(self, client, callback_query: CallbackQuery):
        """Show bonus menu"""
        user_id = callback_query.from_user.id
        user = await db.get_user(user_id)
        
        last_claim = user.get('last_bonus')
        
        if utils.can_claim_bonus(last_claim):
            text = """**🔥 Claim Your Bonus**

**🕑 Claim Again In 24 Hours**

**🎁 Ready to claim!**"""
        else:
            remaining = utils.get_bonus_remaining_time(last_claim)
            time_left = utils.format_time(remaining)
            
            text = f"""**🔥 Claim Your Bonus**

**🕑 Claim Again In 24 Hours**

**⏰ Next: {time_left}**"""
        
        await callback_query.edit_message_text(
            text,
            reply_markup=kb.bonus_menu(),
            parse_mode="markdown"
        )
    
    async def claim_bonus(self, client, callback_query: CallbackQuery):
        """Claim daily bonus"""
        user_id = callback_query.from_user.id
        user = await db.get_user(user_id)
        
        last_claim = user.get('last_bonus')
        
        if utils.can_claim_bonus(last_claim):
            # Grant bonus
            await db.inc_user(user_id, {"balance": config.DAILY_BONUS})
            await db.update_user(user_id, {"last_bonus": datetime.utcnow()})
            
            text = f"""**🎉 Congratulations!**

**⭐ You received {config.DAILY_BONUS}⭐ as Daily Bonus!**

**⏳ Come back after 24 hours!**"""
            
            await callback_query.edit_message_text(
                text,
                reply_markup=kb.bonus_back(),
                parse_mode="markdown"
            )
        else:
            remaining = utils.get_bonus_remaining_time(last_claim)
            time_left = utils.format_time(remaining)
            
            await callback_query.answer(
                f"⏳ Already claimed!\n⏱️ Wait: {time_left}",
                show_alert=True
            )
    
    async def balance_menu(self, client, callback_query: CallbackQuery):
        """Show balance"""
        user_id = callback_query.from_user.id
        user = await db.get_user(user_id)
        first_name = callback_query.from_user.first_name
        
        text = f"""**👤 Name:** {first_name}
**🆔 User ID:** {user_id}

**💵 Balance:** {user['balance']}⭐ Stars

**⌚️ Update:** {utils.get_current_time()}
**📆 Date:** {utils.get_current_date()}"""
        
        await callback_query.edit_message_text(
            text,
            reply_markup=kb.back_menu(),
            parse_mode="markdown"
        )
    
    async def refer_menu(self, client, callback_query: CallbackQuery):
        """Show referral info"""
        user_id = callback_query.from_user.id
        user = await db.get_user(user_id)
        
        referral_link = utils.format_referral_link(user_id)
        
        text = f"""**🔥 Refer and Earn 🔥**

**✅ Per Refer:** {config.REFERRAL_BONUS}⭐ Star
**👥 Total Referrals:** {user.get('total_referrals', 0)}

**🔗 Your Link:**
`{referral_link}`"""
        
        await callback_query.edit_message_text(
            text,
            reply_markup=kb.back_menu(),
            parse_mode="markdown"
        )
    
    async def withdraw_menu(self, client, callback_query: CallbackQuery):
        """Show withdrawal menu"""
        user_id = callback_query.from_user.id
        user = await db.get_user(user_id)
        balance = user.get('balance', 0)
        
        if balance < config.MINIMUM_WITHDRAWAL:
            text = f"""**❌ Insufficient Balance**

**💰 Your balance:** {balance}⭐ stars

**📋 Need at least {config.MINIMUM_WITHDRAWAL}⭐ stars**

**💡 Earn more through daily bonus & referrals!**"""
            
            await callback_query.edit_message_text(
                text,
                reply_markup=kb.back_menu(),
                parse_mode="markdown"
            )
        else:
            text = f"""**💸 Withdrawal Request**

**⚡ Send Stars To Real Username**

**📋 Minimum: {config.MINIMUM_WITHDRAWAL}⭐ Stars**

**Please enter username 👇**"""
            
            user_states[user_id] = {"state": "waiting_username", "data": {}}
            await callback_query.edit_message_text(text, parse_mode="markdown")
    
    async def handle_text(self, client, message: Message):
        """Handle text messages for withdrawal and admin operations"""
        user_id = message.from_user.id
        
        if user_id not in user_states:
            return
        
        state_data = user_states[user_id]
        state = state_data.get("state")
        
        if state == "waiting_username":
            username = utils.clean_username(message.text.strip())
            
            if utils.validate_username(username):
                user_states[user_id]["data"]["username"] = username
                user_states[user_id]["state"] = "waiting_amount"
                await message.reply_text("**⭐ Enter Stars amount:**", parse_mode="markdown")
            else:
                await message.reply_text("**❌ Invalid username format**", parse_mode="markdown")
        
        elif state == "waiting_amount":
            try:
                amount = int(message.text.strip())
                user = await db.get_user(user_id)
                balance = user.get('balance', 0)
                
                if amount < config.MINIMUM_WITHDRAWAL:
                    await message.reply_text(f"**❌ Minimum {config.MINIMUM_WITHDRAWAL}⭐ stars**", parse_mode="markdown")
                elif amount > balance:
                    await message.reply_text(f"**❌ Insufficient balance: {balance}⭐**", parse_mode="markdown")
                else:
                    # Process withdrawal
                    withdrawal_id = utils.generate_id()
                    username = user_states[user_id]["data"]["username"]
                    
                    # Deduct balance
                    await db.inc_user(user_id, {"balance": -amount})
                    
                    # Create withdrawal record
                    withdrawal_data = utils.create_withdrawal_data(withdrawal_id, user_id, username, amount)
                    await db.create_withdrawal(withdrawal_data)
                    
                    # Notify user
                    text = f"""**✅ Order Placed!**

**🆔 Order ID:** {withdrawal_id}
**🎉 Submitted to admin**

**📧 You'll be notified!**"""
                    
                    await message.reply_text(text, parse_mode="markdown")
                    
                    # Notify admin
                    await self.notify_admin_withdrawal(client, message, withdrawal_id, username, amount)
                    
                    del user_states[user_id]
            except ValueError:
                await message.reply_text("**❌ Enter valid number**", parse_mode="markdown")
        
        # Admin states
        elif user_id == config.ADMIN_ID:
            await self.handle_admin_text(client, message, state)
    
    async def notify_admin_withdrawal(self, client, message, withdrawal_id, username, amount):
        """Notify admin about new withdrawal"""
        user_id = message.from_user.id
        admin_text = f"""**📥 New Withdrawal**

**👤 User:** @{message.from_user.username or 'N/A'}
**🆔 ID:** {user_id}
**📝 Username:** @{username}
**⭐ Amount:** {amount} Stars
**🆔 Order:** {withdrawal_id}"""
        
        try:
            await client.send_message(
                config.ADMIN_ID,
                admin_text,
                reply_markup=kb.withdrawal_action(withdrawal_id),
                parse_mode="markdown"
            )
        except:
            pass
    
    async def handle_admin_text(self, client, message, state):
        """Handle admin text messages"""
        user_id = message.from_user.id
        
        if state == "waiting_channel_link":
            link = message.text.strip()
            if utils.is_valid_telegram_link(link):
                user_states[user_id]["data"]["link"] = link
                channel_username = utils.extract_channel_username(link)
                user_states[user_id]["data"]["channel_id"] = f"@{channel_username}"
                user_states[user_id]["state"] = "waiting_button_name"
                await message.reply_text("**📝 Button Name:**", parse_mode="markdown")
            else:
                await message.reply_text("**❌ Invalid link**", parse_mode="markdown")
        
        elif state == "waiting_button_name":
            name = message.text.strip()
            channel_data = user_states[user_id]["data"]
            channel_data["name"] = name
            
            if await db.add_channel(channel_data):
                await message.reply_text("**✅ Button Added!**", parse_mode="markdown")
            else:
                await message.reply_text("**❌ Failed to add**", parse_mode="markdown")
            
            del user_states[user_id]
        
        elif state == "waiting_broadcast":
            broadcast_msg = message.text.strip()
            
            users = await db.get_all_users()
            success = 0
            failed = 0
            
            status_msg = await message.reply_text("**📢 Broadcasting...**", parse_mode="markdown")
            
            for user in users:
                try:
                    await client.send_message(user["user_id"], broadcast_msg, parse_mode="markdown")
                    success += 1
                except:
                    failed += 1
            
            await status_msg.edit_text(
                f"**📢 Complete!**\n\n**✅ Sent:** {success}\n**❌ Failed:** {failed}",
                parse_mode="markdown"
            )
            
            del user_states[user_id]
    
    async def handle_withdrawal(self, client, callback_query: CallbackQuery):
        """Handle withdrawal approval/rejection"""
        if callback_query.from_user.id != config.ADMIN_ID:
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
        
        action, withdrawal_id = callback_query.data.split('_', 1)
        withdrawal = await db.get_withdrawal(withdrawal_id)
        
        if not withdrawal:
            await callback_query.answer("❌ Not found!", show_alert=True)
            return
        
        if action == "approve":
            await db.update_withdrawal(withdrawal_id, {
                "status": "completed",
                "completed_at": datetime.utcnow()
            })
            
            # Notify user
            try:
                await client.send_message(
                    withdrawal["user_id"],
                    f"**🎉 Withdrawal Success!**\n\n**Amount:** {withdrawal['amount']}⭐ Stars",
                    parse_mode="markdown"
                )
            except:
                pass
            
            await callback_query.edit_message_text(
                f"**✅ Approved**\n\n{callback_query.message.text}",
                parse_mode="markdown"
            )
        
        else:  # reject
            # Refund balance
            await db.inc_user(withdrawal["user_id"], {"balance": withdrawal["amount"]})
            await db.update_withdrawal(withdrawal_id, {
                "status": "rejected",
                "rejected_at": datetime.utcnow()
            })
            
            # Notify user
            try:
                await client.send_message(
                    withdrawal["user_id"],
                    "**❌ Withdrawal rejected. Stars refunded.**",
                    parse_mode="markdown"
                )
            except:
                pass
            
            await callback_query.edit_message_text(
                f"**❌ Rejected**\n\n{callback_query.message.text}",
                parse_mode="markdown"
            )
    
    async def admin_help(self, client, message: Message):
        """Show admin help"""
        text = """**🔐 Welcome Boss!**

**👥 Manage Users • 💸 Withdrawals**
**➕ Add Channels • 📢 Broadcast**"""
        
        await message.reply_text(
            text,
            reply_markup=kb.admin_menu(),
            parse_mode="markdown"
        )
    
    async def bot_stats(self, client, message: Message):
        """Show bot statistics"""
        user_count = await db.get_user_count()
        withdrawal_stats = await db.get_withdrawal_stats()
        channels = await db.get_channels()
        
        text = f"""**📊 Bot Statistics**

**👥 Total Users:** {user_count}
**📢 Total Channels:** {len(channels)}

**💸 Withdrawal Stats:**
**⏳ Pending:** {withdrawal_stats['pending']}
**✅ Completed:** {withdrawal_stats['completed']}
**❌ Rejected:** {withdrawal_stats['rejected']}

**🚀 Bot is running smoothly!**"""
        
        await message.reply_text(text, parse_mode="markdown")
    
    async def admin_callbacks(self, client, callback_query: CallbackQuery):
        """Handle admin callback queries"""
        data = callback_query.data
        
        if data == "admin_users":
            user_count = await db.get_user_count()
            text = f"""**👥 User Statistics**

**📊 Total Users:** {user_count}"""
            
            await callback_query.edit_message_text(
                text,
                reply_markup=kb.admin_back(),
                parse_mode="markdown"
            )
        
        elif data == "admin_withdrawals":
            stats = await db.get_withdrawal_stats()
            text = f"""**💸 Withdrawal Stats**

**⏳ Pending:** {stats['pending']}
**✅ Completed:** {stats['completed']}
**❌ Rejected:** {stats['rejected']}"""
            
            await callback_query.edit_message_text(
                text,
                reply_markup=kb.admin_back(),
                parse_mode="markdown"
            )
        
        elif data == "admin_add":
            user_states[callback_query.from_user.id] = {
                "state": "waiting_channel_link",
                "data": {}
            }
            await callback_query.edit_message_text(
                "**📝 Send channel link:**",
                parse_mode="markdown"
            )
        
        elif data == "admin_remove":
            channels = await db.get_channels()
            if not channels:
                await callback_query.edit_message_text(
                    "**❌ No channels found**",
                    parse_mode="markdown"
                )
            else:
                await callback_query.edit_message_text(
                    "**➖ Remove Channel**",
                    reply_markup=kb.remove_channels(channels),
                    parse_mode="markdown"
                )
        
        elif data == "admin_broadcast":
            user_states[callback_query.from_user.id] = {"state": "waiting_broadcast"}
            await callback_query.edit_message_text(
                "**📢 Send broadcast message:**",
                parse_mode="markdown"
            )
        
        elif data == "admin_channels":
            channels = await db.get_channels()
            if not channels:
                text = "**📄 Channel List**\n\n**❌ No channels added yet.**"
            else:
                text = "**📄 Channel List**\n\n"
                for i, ch in enumerate(channels, 1):
                    text += f"**{i}.** {ch['name']}\n**🔗** {ch['link']}\n\n"
            
            await callback_query.edit_message_text(
                text.strip(),
                reply_markup=kb.admin_back(),
                parse_mode="markdown"
            )
        
        elif data == "admin_back":
            text = """**🔐 Welcome Boss!**

**👥 Manage Users • 💸 Withdrawals**
**➕ Add Channels • 📢 Broadcast**"""
            
            await callback_query.edit_message_text(
                text,
                reply_markup=kb.admin_menu(),
                parse_mode="markdown"
            )
    
    async def remove_channel(self, client, callback_query: CallbackQuery):
        """Remove channel"""
        if callback_query.from_user.id != config.ADMIN_ID:
            return
        
        channel_username = callback_query.data.split("remove_")[1]
        channel_id = f"@{channel_username}"
        
        if await db.remove_channel(channel_id):
            await callback_query.edit_message_text(
                "**✅ Channel Removed!**",
                parse_mode="markdown"
            )
        else:
            await callback_query.edit_message_text(
                "**❌ Failed to remove**",
                parse_mode="markdown"
            )