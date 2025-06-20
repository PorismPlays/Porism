
import json
import os
import logging
from database import db_manager

logger = logging.getLogger('discord_bot.migration')

async def migrate_json_to_database():
    """Migrate existing JSON data to database"""
    try:
        # Check if migration has already been done
        migration_done = await db_manager.get_config("migration_completed", False)
        if migration_done:
            logger.info("Migration already completed, skipping...")
            return
        
        logger.info("Starting data migration from JSON to database...")
        
        # Migrate member stats
        if os.path.exists("member_stats.json"):
            with open("member_stats.json", "r") as f:
                member_stats = json.load(f)
            
            for user_id, stats in member_stats.items():
                await db_manager.update_member_stats(user_id, stats)
            
            logger.info(f"Migrated {len(member_stats)} member stats")
        
        # Migrate balances
        if os.path.exists("balances.json"):
            with open("balances.json", "r") as f:
                balances = json.load(f)
            
            for user_id, balance in balances.items():
                await db_manager.update_user_balance(user_id, balance)
            
            logger.info(f"Migrated {len(balances)} user balances")
        
        # Migrate inventories
        if os.path.exists("inventories.json"):
            with open("inventories.json", "r") as f:
                inventories = json.load(f)
            
            for user_id, inventory in inventories.items():
                for item_name, quantity in inventory.items():
                    await db_manager.update_user_inventory(user_id, item_name, quantity)
            
            logger.info(f"Migrated inventories for {len(inventories)} users")
        
        # Migrate tier list
        if os.path.exists("tierlist.json"):
            with open("tierlist.json", "r") as f:
                tier_data = json.load(f)
            
            for tier, items in tier_data.items():
                for item in items:
                    await db_manager.add_tier_item(tier, item)
            
            logger.info(f"Migrated tier list with {sum(len(items) for items in tier_data.values())} items")
        
        # Migrate bot configuration
        if os.path.exists("bot_config.json"):
            with open("bot_config.json", "r") as f:
                config = json.load(f)
            
            for key, value in config.items():
                await db_manager.set_config(key, value)
            
            logger.info(f"Migrated {len(config)} configuration items")
        
        # Mark migration as completed
        await db_manager.set_config("migration_completed", True)
        await db_manager.log_action("migration_completed", None, "JSON to database migration completed")
        
        logger.info("Data migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

async def backup_json_files():
    """Create backup of JSON files before migration"""
    import shutil
    from datetime import datetime
    
    backup_dir = f"json_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    json_files = [
        "member_stats.json", "balances.json", "inventories.json",
        "tierlist.json", "bot_config.json", "shops.json",
        "auctions.json", "giveaways.json", "premium_slots.json"
    ]
    
    for file_name in json_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, backup_dir)
    
    logger.info(f"JSON files backed up to {backup_dir}")
