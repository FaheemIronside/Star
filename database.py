# database.py
"""
Database operations for RajxStars Bot
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Dict, List, Optional
import config

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(config.MONGO_URI, maxPoolSize=5)
        self.db = self.client[config.DB_NAME]
        self.users = self.db.users
        self.channels = self.db.channels
        self.withdrawals = self.db.withdrawals
    
    # User Operations
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user from database"""
        try:
            return await self.users.find_one({"user_id": user_id})
        except:
            return None
    
    async def create_user(self, user_data: Dict) -> bool:
        """Create new user"""
        try:
            await self.users.insert_one(user_data)
            return True
        except:
            return False
    
    async def update_user(self, user_id: int, data: Dict) -> bool:
        """Update user data"""
        try:
            await self.users.update_one({"user_id": user_id}, {"$set": data})
            return True
        except:
            return False
    
    async def inc_user(self, user_id: int, data: Dict) -> bool:
        """Increment user fields"""
        try:
            await self.users.update_one({"user_id": user_id}, {"$inc": data})
            return True
        except:
            return False
    
    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        try:
            return await self.users.find({}).to_list(None)
        except:
            return []
    
    async def get_user_count(self) -> int:
        """Get total user count"""
        try:
            return await self.users.count_documents({})
        except:
            return 0
    
    # Channel Operations
    async def get_channels(self) -> List[Dict]:
        """Get all channels"""
        try:
            return await self.channels.find({}).to_list(None)
        except:
            return []
    
    async def add_channel(self, channel_data: Dict) -> bool:
        """Add new channel"""
        try:
            await self.channels.insert_one(channel_data)
            return True
        except:
            return False
    
    async def remove_channel(self, channel_id: str) -> bool:
        """Remove channel"""
        try:
            await self.channels.delete_one({"channel_id": channel_id})
            return True
        except:
            return False
    
    # Withdrawal Operations
    async def create_withdrawal(self, withdrawal_data: Dict) -> bool:
        """Create withdrawal request"""
        try:
            await self.withdrawals.insert_one(withdrawal_data)
            return True
        except:
            return False
    
    async def get_withdrawal(self, withdrawal_id: str) -> Optional[Dict]:
        """Get withdrawal by ID"""
        try:
            return await self.withdrawals.find_one({"withdrawal_id": withdrawal_id})
        except:
            return None
    
    async def update_withdrawal(self, withdrawal_id: str, data: Dict) -> bool:
        """Update withdrawal status"""
        try:
            await self.withdrawals.update_one(
                {"withdrawal_id": withdrawal_id}, 
                {"$set": data}
            )
            return True
        except:
            return False
    
    async def get_withdrawal_stats(self) -> Dict:
        """Get withdrawal statistics"""
        try:
            pending = await self.withdrawals.count_documents({"status": "pending"})
            completed = await self.withdrawals.count_documents({"status": "completed"})
            rejected = await self.withdrawals.count_documents({"status": "rejected"})
            
            return {
                "pending": pending,
                "completed": completed,
                "rejected": rejected,
                "total": pending + completed + rejected
            }
        except:
            return {"pending": 0, "completed": 0, "rejected": 0, "total": 0}

# Create database instance
db = Database()