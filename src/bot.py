import os
import yaml
import discord
import asyncio
import logging

from dotenv import load_dotenv
from discord.ext import commands
intents = discord.Intents.all()

load_dotenv()
TOKEN = os.environ['DISCORD_BOT_TOKEN']
MONGO = os.environ['MONGO_URI']

logging.basicConfig(level=logging.INFO)


class Bot(commands.Bot):
    """Main Bot class"""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True

        super().__init__(command_prefix='TESTEC!',
                         case_insensitive=True,
                         intents=intents)

    def load_cogs(self) -> None:
        """Loads all the cogs for the bot"""
        cogs = ['src.cogs.ban',
                'src.cogs.sourcecred',
                'src.cogs.forms',
                'src.cogs.icebreakers',
                'src.cogs.help',
                'src.cogs.users',
                'src.cogs.trustedseed',
                'src.exts.scrape_praise',
                'src.listeners.onboarding']
        self.MONGO = MONGO
        for extension in cogs:
            self.load_extension(extension)
            logging.info(f'Loaded cog - {extension}')

    def run(self) -> None:
        """Runs the bot"""
        if TOKEN is None:
            raise EnvironmentError("Token value not found in .env")
        self.load_yaml()
        self.load_cogs()
        super().run(TOKEN)

    def load_yaml(self) -> None:
        """Loads yaml files"""
        logging.info("Loading YAML files")
        with open("src/sources/trusted_seed_form.yml") as file:
            ts_form = yaml.safe_load(file)
        self.SEED_FORM = ts_form

        with open("src/sources/responses.yml") as file:
            self.RESPONSES = yaml.safe_load(file)

    async def on_ready(self):
        logging.info('Starting...')
