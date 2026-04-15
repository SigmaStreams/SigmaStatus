import logging

import discord
from discord.ext import commands

from bot.config import load_config
from bot.db import ReportDB

DEFAULT_GUILD_ID_FOR_SYNC = 1457559352717086917
logger = logging.getLogger(__name__)


class SigmaReportsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.cfg = load_config()
        self.db = ReportDB(self.cfg.db_path)

    async def setup_hook(self) -> None:
        for ext in ("bot.cogs.plex_liveboard",):
            try:
                await self.load_extension(ext)
            except Exception as e:
                logger.exception("Skipping extension %s: %r", ext, e)

        # Sync to a single guild for fast iteration
        guild_id = getattr(self.cfg, "guild_id", None) or DEFAULT_GUILD_ID_FOR_SYNC
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            try:
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                logger.info("Synced %s commands to guild %s", len(synced), guild_id)
            except Exception as e:
                logger.exception("Command sync failed for guild %s: %r", guild_id, e)
        else:
            logger.warning("No guild_id configured; skipping guild sync.")

    async def on_ready(self):
        logger.info("Logged in as %s (ID: %s)", self.user, self.user.id)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    bot = SigmaReportsBot()
    bot.run(bot.cfg.token)


if __name__ == "__main__":
    main()
