import discord
from discord import app_commands
from chatbots import traduzir
import asyncio
import logging

logger = logging.getLogger("izza-study")

# ─── CONFIGURAÇÕES DE TEMPO (em segundos) ────────────────────────────────────────
PREVIEW_TIMEOUT = 15  # Tempo total até a pré-visualização expirar
WARNING_DURATION = 10  # Quantos segundos de aviso queremos no final
DELETE_DELAY_AFTER_SEND = 3  # Quanto tempo após o envio pelo botão até deletar
# ────────────────────────────────────────────────────────────────────────────────


def _log_command_interaction(interaction: discord.Interaction):
    """Logs the detalhes de cada comando invocado."""
    command_name = interaction.command.name if interaction.command else "N/A"
    user = interaction.user
    guild = interaction.guild
    channel = interaction.channel

    guild_info = f"'{guild.name}' (ID: {guild.id})" if guild else "Direct Message"
    channel_info = f"'{channel.name}' (ID: {channel.id})" if channel else "N/A"

    logger.info(f"CMD: /{command_name} | User: {user} ({user.id}) | " f"Guild: {guild_info} | Channel: {channel_info}")


class PingEmbedFactory:
    def __init__(self, usuario: discord.User, latency: int | str):
        self.usuario = usuario
        self.latency = latency

    def build(self) -> discord.Embed:
        embed = discord.Embed(title="🏓 Pong!", description=f"Latência: {self.latency}ms", color=discord.Color.orange())
        embed.set_footer(text=f"Solicitado por {self.usuario}", icon_url=self.usuario.display_avatar.url)
        return embed


class PingView(discord.ui.View):
    def __init__(self, bot_client: discord.Client):
        super().__init__(timeout=120)
        self.bot_client = bot_client

    @discord.ui.button(label="Ping", style=discord.ButtonStyle.primary, emoji="🏓")
    async def ping_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        _log_command_interaction(interaction)
        latency = round(self.bot_client.latency * 1000) if hasattr(self.bot_client, "latency") else "N/A"
        embed = PingEmbedFactory(interaction.user, latency).build()
        await interaction.response.send_message(embed=embed, ephemeral=True, view=PingView(self.bot_client))


# Cache de webhooks para evitar chamadas de API repetidas
webhook_cache: dict[int, discord.Webhook] = {}


async def get_or_create_webhook(channel: discord.TextChannel) -> discord.Webhook:
    """Obtém um webhook ou cria um novo para o comando /traduza."""
    if channel.id in webhook_cache:
        return webhook_cache[channel.id]

    for wh in await channel.webhooks():
        if wh.user == channel.guild.me and wh.name == "IzzaBot Webhook":
            webhook_cache[channel.id] = wh
            return wh

    new_webhook = await channel.create_webhook(name="IzzaBot Webhook", reason="Webhook para o comando /traduza")
    webhook_cache[channel.id] = new_webhook
    return new_webhook


class TranslateView(discord.ui.View):
    def __init__(self_1,
        translated_text: str,
        author: discord.User,
        interaction: discord.Interaction
    ):
        super().__init__(timeout=PREVIEW_TIMEOUT)
        self_1.translated_text = translated_text
        self_1.author = author
        self_1.interaction = interaction
        self_1.message: discord.InteractionMessage | None = None
        self_1.countdown_task: asyncio.Task | None = None

    def start_countdown(self_1):
        """Inicia a tarefa de contagem regressiva."""
        self_1.countdown_task = asyncio.create_task(self_1._countdown_worker())

    async def _countdown_worker(self_1):
        """Mostra o aviso nos últimos WARNING_DURATION segundos e deleta ao final."""
        try:
            # 1) Espera até faltar WARNING_DURATION segundos
            await asyncio.sleep(PREVIEW_TIMEOUT - WARNING_DURATION)
            if self_1.is_finished() or not self_1.message:
                return

            # 2) Exibe contagem regressiva
            for remaining in range(WARNING_DURATION, 0, -1):
                if self_1.is_finished() or not self_1.message:
                    return

                try:
                    embed = self_1.message.embeds[0]
                    embed.color = discord.Color.red()
                    embed.set_footer(text=f"Esta tradução será descartada em {remaining} segundos...")
                    await self_1.message.edit(embed=embed, view=self_1)
                except discord.NotFound:
                    return  # Usuário já ignorou a mensagem

                await asyncio.sleep(1)

            # 3) Ao chegar a zero, deleta a mensagem efêmera
            try:
                await self_1.interaction.delete_original_response()
                logger.info(f"Tradução expirada e mensagem efêmera removida para o autor {self_1.author.id}.")
            except Exception as e:
                logger.error(f"Erro ao excluir mensagem no fim da contagem: {e}")
            finally:
                self_1.stop()

        except asyncio.CancelledError:
            # Quando o botão é clicado, a tarefa é cancelada
            pass
        except Exception as e:
            logger.error(f"Erro na contagem regressiva da TranslateView: {e}")

    @discord.ui.button(label="Enviar Tradução", style=discord.ButtonStyle.success, emoji="📤")
    async def enviar(self_1, interaction_button: discord.Interaction, button: discord.ui.Button):
        if interaction_button.user.id != self_1.author.id:
            await interaction_button.response.send_message(
                "Só quem usou o comando pode usar este botão.", ephemeral=True
            )
            return

        try:
            webhook = await get_or_create_webhook(interaction_button.channel)
            await webhook.send(
                content=self_1.translated_text,
                username=interaction_button.user.display_name,
                avatar_url=interaction_button.user.display_avatar.url,
            )
            logger.info(
                f"BTN: Enviar Tradução | User: {interaction_button.user} ({interaction_button.user.id}) | "
                f"Guild: '{interaction_button.guild.name}' ({interaction_button.guild.id}) | "
                f"Content: '{self_1.translated_text}'"
            )

            # Feedback visual e cancelamento da contagem
            button.disabled = True
            button.label = "Enviado!"
            await interaction_button.response.edit_message(view=self_1)
            self_1.stop()

            # Deleta a pré-visualização após um breve intervalo
            await asyncio.sleep(DELETE_DELAY_AFTER_SEND)
            await interaction_button.delete_original_response()

        except Exception as e:
            logger.error(f"Falha ao enviar mensagem via webhook: {e}")
            await interaction_button.response.send_message(
                "Ocorreu um erro ao tentar enviar a tradução.", ephemeral=True
            )


def setup_comandos(bot: discord.Client):
    @bot.tree.command(name="ajuda", description="Mostra os comandos disponíveis")
    async def ajuda(interaction: discord.Interaction):
        _log_command_interaction(interaction)
        embed = discord.Embed(
            title="Comandos Disponíveis",
            description="Aqui estão alguns comandos que você pode usar:",
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.add_field(name="`/ajuda`", value="Mostra esta mensagem de ajuda", inline=False)
        embed.add_field(name="`/ping`", value="Verifica a latência do bot", inline=False)
        embed.add_field(name="`/info`", value="Mostra informações sobre o bot", inline=False)
        embed.add_field(name="`/server`", value="Mostra informações sobre o servidor", inline=False)
        embed.add_field(name="`/traduza`", value="Traduz frase entre PT-BR e EN", inline=False)
        embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="ping", description="Responde com a latência do bot")
    async def ping(interaction: discord.Interaction):
        _log_command_interaction(interaction)
        latency = round(bot.latency * 1000) if hasattr(bot, "latency") else "N/A"
        embed = PingEmbedFactory(interaction.user, latency).build()
        await interaction.response.send_message(embed=embed, ephemeral=True, view=PingView(bot))

    @bot.tree.command(name="info", description="Mostra informações sobre o bot")
    async def info(interaction: discord.Interaction):
        _log_command_interaction(interaction)
        embed = discord.Embed(
            title="Informações do Bot", description="Detalhes sobre o bot Izza Study", color=discord.Color.green()
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.add_field(name="Nome", value=bot.user.name, inline=True)
        embed.add_field(name="ID", value=bot.user.id, inline=True)
        embed.add_field(name="Latência", value=f"{round(bot.latency * 1000)}ms", inline=True)
        embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="server", description="Mostra informações sobre o servidor")
    async def server_info(interaction: discord.Interaction):
        _log_command_interaction(interaction)
        guild = interaction.guild
        embed = discord.Embed(
            title=f"Informações do Servidor: {guild.name}",
            description=guild.description or "Sem descrição.",
            color=discord.Color.blurple(),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="ID do Servidor", value=guild.id, inline=True)
        embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
        embed.add_field(name="Criado em", value=discord.utils.format_dt(guild.created_at, style="F"), inline=False)
        embed.add_field(name="Membros", value=guild.member_count, inline=True)
        embed.add_field(name="Cargos", value=len(guild.roles), inline=True)
        embed.add_field(name="Canais de Texto", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Canais de Voz", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="Nível de Verificação", value=str(guild.verification_level).capitalize(), inline=True)
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="traduza", description="Traduz frase entre PT-BR <--> EN")
    @app_commands.describe(frase="Frase em português ou inglês para tradução")
    async def traduza(interaction: discord.Interaction, frase: str):
        _log_command_interaction(interaction)
        await interaction.response.defer(ephemeral=True)
        try:
            traducao = traduzir(frase)
            logger.info(f"Translation success for '{interaction.user}': '{frase}' -> '{traducao}'")

            embed = discord.Embed(
                title="Tradução",
                description=(f"**Original:**\n```" f"{frase}```\n" f"**Tradução:**\n```" f"{traducao}```"),
                color=discord.Color.gold(),
            )
            embed.set_footer(text="Clique no botão abaixo para enviar a tradução para o canal.")

            view = TranslateView(traducao, interaction.user, interaction)
            message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            view.message = message
            view.start_countdown()

        except Exception as e:
            logger.error(f"Erro na API de tradução para a frase '{frase}': {e}")
            await interaction.followup.send(
                "Desculpe, ocorreu um erro ao tentar traduzir. Tente novamente mais tarde.", ephemeral=True
            )
