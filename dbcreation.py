
import aiosqlite
import json
from utils.variables import DB_FILE


async def setup_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS party_loot (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT,
                type TEXT,
                hands TEXT,
                damage TEXT,
                range TEXT,
                magical BOOLEAN DEFAULT 0,
                crit TEXT,
                damage_type TEXT,
                description TEXT,
                discovery_location TEXT,
                quantity INTEGER DEFAULT 1,
                owner TEXT,
                link TEXT
            )
        """)
        with open("./data/loot.json", "r") as f:
            items = json.load(f)
        for item in items.values():
            await db.execute(
                "INSERT OR IGNORE INTO party_loot (name, category, type, hands, damage, range, magical, crit, damage_type, description, discovery_location, quantity, owner, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    item.get("name"),
                    item.get("category", ""),
                    item.get("type", ""),
                    item.get("hands", ""),
                    item.get("damage", ""),
                    item.get("range", ""),
                    item.get("magical", False),
                    item.get("crit", ""),
                    item.get("damage_type", ""),
                    item.get("description", ""),
                    item.get("discovery_location", ""),
                    item.get("quantity", 1),
                    item.get("owner", ""),
                    item.get("link", "")
                )
            )

        await db.commit()
        print("Database setup complete.")
