import discord
import os
import logging
import sys
from dotenv import load_dotenv
from comandos import setup_comandos

# --- Configuração Inicial ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

# --- MODO DE OPERAÇÃO ---
# Mude para False para sincronizar comandos globalmente (produção).
# Para o modo de desenvolvimento (True), GUILD_ID deve estar definido no .env.
DEVELOPMENT_MODE = True

# Configuração das intenções do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# --- Configuração de Logging Colorido ---
class ColoredFormatter(logging.Formatter):
    """Formatter que adiciona cores e alinhamento ao nível do log."""

    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    PINK = "\x1b[38;5;206m"
    RESET = "\x1b[0m"

    def __init__(self, fmt, datefmt=None):
        super().__init__(fmt, datefmt)
        self.COLORS = {
            logging.DEBUG: self.GREY,
            logging.INFO: self.GREEN,
            logging.WARNING: self.YELLOW,
            logging.ERROR: self.RED,
            logging.CRITICAL: self.BOLD_RED,
        }

    def format(self, record):
        original_levelname = record.levelname

        # Verifica se o log é do discord e aplica a cor rosa
        if 'discord' in record.name:
            color = self.PINK
        else:
            color = self.COLORS.get(record.levelno)

        padded_levelname = f"{original_levelname:<8}"

        if color:
            record.levelname = f"{color}{padded_levelname}{self.RESET}"
        else:
            record.levelname = padded_levelname

        result = super().format(record)

        record.levelname = original_levelname

        return result


# Configura o logger principal com nome 'izza-study'
logger = logging.getLogger("izza-study")
logger.setLevel(logging.INFO)

# Handler para o arquivo (sem cores)
file_handler = logging.FileHandler("izza_study.log", encoding='utf-8')
file_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

# Handler para o console (com cores)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter(
    '[%(asctime)s] %(levelname)s %(name)-20s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

class IzzaBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        setup_comandos(self)

        if DEVELOPMENT_MODE:
            if not GUILD_ID:
                raise ValueError(
                    "❌ GUILD_ID não foi definido no arquivo .env. Ele é necessário para o modo de desenvolvimento.")
            guild = discord.Object(id=GUILD_ID)
            await self.tree.sync(guild=guild)
            logger.info(
                f"✅ [MODO DEV] Comandos sincronizados para a guilda de desenvolvimento: {GUILD_ID}.")
        else:
            await self.tree.sync()
            logger.info(
                "🌐 [MODO PROD] Comandos sincronizados globalmente (pode levar até 1h).")

    async def on_ready(self):
        logger.info(
            f'✅ {self.user.name} conectado com sucesso! ID: {self.user.id}')
        await self.change_presence(activity=discord.Game(name="/ajuda"))


bot = IzzaBot(intents=intents)
# Passamos log_handler=None para desativar a configuração de log padrão do discord.py,
# evitando logs duplicados e não padronizados no terminal.
bot.run(DISCORD_TOKEN, log_handler=None)
