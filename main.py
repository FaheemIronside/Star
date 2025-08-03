# main.py
"""
RajxStars Bot - Main Entry Point
Multi-file structure for better organization
"""

import asyncio
import logging
from pyrogram import Client
from handlers import Handlers
import config

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING  # Minimal logging for low RAM
)

# Initialize bot
app = Client(
    "rajxstars_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    sleep_threshold=30  # Reduce flood wait
)

async def main():
    """Main function to start the bot"""
    print("🚀 Starting RajxStars Bot...")
    print(f"📱 Bot Username: @{config.BOT_USERNAME}")
    print(f"👑 Admin ID: {config.ADMIN_ID}")
    
    # Initialize handlers
    handlers = Handlers(app)
    print("✅ Handlers registered")
    
    # Start the bot
    try:
        await app.start()
        print("✅ Bot started successfully!")
        print("📢 Bot is now running and ready to serve users")
        print("💡 Use /adminhelp to access admin panel")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
    finally:
        print("⏹️ Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        print("🔚 Bot shutdown complete")