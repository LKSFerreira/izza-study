import discord
from discord import app_commands
from chatbots import translate_auto
import datetime
import logging

def _log_command_interaction(interaction: discord.Interaction):
    """Logs the details of a command interaction in a structured format."""
    command_name = interaction.command.name if interaction.command else "N/A"
    user = interaction.user
    guild = interaction.guild
    channel = interaction.channel

    guild_info = f"'{guild.name}' (ID: {guild.id})" if guild else "Direct Message"
    channel_info = f"'{channel.name}' (ID: {channel.id})" if channel else "N/A"

    logging.info(
        f"CMD: /{command_name} | User: {user} ({user.id}) | Guild: {guild_info} | Channel: {channel_info}"
    )

class PingEmbedFactory:
    def __init__(self, usuario: discord.User, latency: int | str):
        self.usuario = usuario
        self.latency = latency

    def build(self) -> discord.Embed:
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: {self.latency}ms",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Solicitado por {self.usuario}", icon_url=self.usuario.display_avatar.url)
        return embed

class PingView(discord.ui.View):
    def __init__(self, bot_client: discord.Client):
        super().__init__(timeout=120)
        self.bot_client = bot_client

    @discord.ui.button(label="Ping", style=discord.ButtonStyle.primary, emoji="🏓")
    async def ping_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        guild = interaction.guild
        guild_info = f"'{guild.name}' (ID: {guild.id})" if guild else "Direct Message"
        logging.info(f"BTN: Ping | User: {user} ({user.id}) | Guild: {guild_info}")

        latency = round(self.bot_client.latency * 1000) if hasattr(self.bot_client, 'latency') else 'N/A'
        embed = PingEmbedFactory(interaction.user, latency).build()
        # Passa uma nova instância da View para que o botão continue funcionando
        await interaction.response.send_message(embed=embed, ephemeral=True, view=PingView(self.bot_client))

# Cache de webhooks para evitar chamadas de API repetidas
webhook_cache = {}

async def get_or_create_webhook(channel: discord.TextChannel) -> discord.Webhook:
    """Obtém um webhook existente ou cria um novo se necessário."""
    if channel.id in webhook_cache:
        return webhook_cache[channel.id]

    webhooks = await channel.webhooks()
    for wh in webhooks:
        # Reutiliza um webhook criado pelo bot para evitar criar múltiplos
        if wh.user == channel.guild.me and wh.name == "IzzaBot Webhook":
            webhook_cache[channel.id] = wh
            return wh
    
    new_webhook = await channel.create_webhook(name="IzzaBot Webhook", reason="Webhook para o comando /traduza")
    webhook_cache[channel.id] = new_webhook
    return new_webhook

class TranslateView(discord.ui.View):
    def __init__(self, translated_text: str, author: discord.User):
        super().__init__(timeout=60)
        self.translated_text = translated_text
        self.author = author
        self.message: discord.InteractionMessage | None = None

    @discord.ui.button(label="Enviar Tradução", style=discord.ButtonStyle.success, emoji="📤")
    async def enviar(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        if interaction_button.user.id != self.author.id:
            await interaction_button.response.send_message("Só quem usou o comando pode usar este botão.", ephemeral=True)
            return

        try:
            webhook = await get_or_create_webhook(interaction_button.channel)
            await webhook.send(
                content=self.translated_text,
                username=interaction_button.user.display_name,
                avatar_url=interaction_button.user.display_avatar.url
            )
            user = interaction_button.user
            guild = interaction_button.guild
            logging.info(
                f"BTN: Enviar Tradução | User: {user} ({user.id}) | "
                f"Guild: '{guild.name}' ({guild.id}) | Content: '{self.translated_text}'"
            )

            button.disabled = True
            button.label = "Enviado!"
            await interaction_button.response.edit_message(view=self)

        except Exception as e:
            logging.error(f"Falha ao enviar mensagem via webhook: {e}")
            await interaction_button.response.send_message("Ocorreu um erro ao tentar enviar a tradução.", ephemeral=True)

    async def on_timeout(self) -> None:
        """Desativa os botões e atualiza a mensagem quando a view expira."""
        if not self.message:
            return

        # Desativa todos os botões na view
        for item in self.children:
            item.disabled = True

        # Pega o embed original e o modifica para indicar que expirou
        original_embed = self.message.embeds[0]
        original_embed.color = discord.Color.dark_grey()
        original_embed.set_footer(text="Esta tradução expirou.")
        await self.message.edit(embed=original_embed, view=self)

def setup_comandos(bot: discord.Client):
    @bot.tree.command(name="ajuda", description="Mostra os comandos disponíveis")
    async def ajuda(interaction: discord.Interaction):
        _log_command_interaction(interaction)
        embed = discord.Embed(
            title="Comandos Disponíveis",
            description="Aqui estão alguns comandos que você pode usar:",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.add_field(name="`/ajuda`", value="Mostra esta mensagem de ajuda", inline=False)
        embed.add_field(name="`/ping`", value="Verifica a latência do bot", inline=False)
        embed.add_field(name="`/info`", value="Mostra informações sobre o bot", inline=False)
        embed.add_field(name="`/server`", value="Mostra informações sobre o servidor", inline=False)
        embed.add_field(name="`/traduza`", value="Traduz uma frase entre PT-BR e EN", inline=False)
        embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="ping", description="Responde com a latência do bot")
    async def ping(interaction: discord.Interaction):
        _log_command_interaction(interaction)
        latency = round(bot.latency * 1000) if hasattr(bot, 'latency') else 'N/A'
        embed = PingEmbedFactory(interaction.user, latency).build()
        await interaction.response.send_message(embed=embed, ephemeral=True, view=PingView(bot))

    @bot.tree.command(name="info", description="Mostra informações sobre o bot")
    async def info(interaction: discord.Interaction):
        _log_command_interaction(interaction)
        embed = discord.Embed(
            title="Informações do Bot",
            description="Detalhes sobre o bot Izza Study",
            color=discord.Color.green()
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
            description=guild.description if guild.description else "Sem descrição.",
            color=discord.Color.blurple()
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="ID do Servidor", value=guild.id, inline=True)
        embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
        embed.add_field(name="Criado em", value=discord.utils.format_dt(guild.created_at, style='F'), inline=False)
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
        # Resposta inicial efêmera para que só o usuário veja
        await interaction.response.defer(ephemeral=True)
        try:
            traducao = translate_auto(frase)
            # Log específico da ação de tradução
            logging.info(f"Translation success for '{interaction.user}': '{frase}' -> '{traducao}'")
            
            embed = discord.Embed(
                title="Tradução",
                description=f"**Original:**\n```{frase}```\n**Tradução:**\n```{traducao}```",
                color=discord.Color.gold()
            )
            embed.set_footer(text="Clique no botão abaixo para enviar a tradução para o canal.")
            
            view = TranslateView(traducao, interaction.user)
            # Envia a mensagem e armazena a referência na view para poder editá-la no on_timeout
            message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            view.message = message

        except Exception as e:
            logging.error(f"Erro na API de tradução para a frase '{frase}': {e}")
            await interaction.followup.send(f"Desculpe, ocorreu um erro ao tentar traduzir. Tente novamente mais tarde.", ephemeral=True)
