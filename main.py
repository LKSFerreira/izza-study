import discord
import os
from dotenv import load_dotenv
from comandos import setup_comandos

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Configuração das intenções do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True


class IzzaBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        setup_comandos(self)
        await self.tree.sync()

    async def on_ready(self):
        print(f'{self.user.name} conectado com sucesso! ID: {self.user.id}')
        print('------')
        await self.change_presence(activity=discord.Game(name="/ajuda"))


bot = IzzaBot(intents=intents)

bot.run(DISCORD_TOKEN)
