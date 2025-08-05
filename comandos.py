import discord
from discord import app_commands
from chatbots import translate_auto
import datetime

def setup_comandos(bot: discord.Client):
    # Comando /ajuda
    @bot.tree.command(name="ajuda", description="Mostra os comandos disponíveis")
    async def ajuda(interaction: discord.Interaction):
        embed = discord.Embed(
            title="Comandos Disponíveis",
            description="Aqui estão alguns comandos que você pode usar:",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.add_field(name="`/ajuda`", value="Mostra esta mensagem de ajuda")
        embed.add_field(name="`/ping`", value="Responde com Pong!")
        embed.add_field(name="`/info`", value="Mostra informações sobre o bot")
        embed.add_field(name="`/server`", value="Mostra informações sobre o servidor")
        embed.add_field(name="`/traduzir`", value="Traduz frase entre PT-BR e EN automaticamente")
        embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Comando /ping
    @bot.tree.command(name="ping", description="Responde com Pong!")
    async def ping(interaction: discord.Interaction):
        class PingEmbedFactory:
            def __init__(self, usuario, latency):
                self.usuario = usuario
                self.latency = latency

            def build(self):
                embed = discord.Embed(
                    title="🏓 Pong!",
                    description=f"Latência: {self.latency}ms",
                    color=discord.Color.orange()
                )
                embed.set_footer(text=f"Solicitado por {self.usuario}", icon_url=self.usuario.display_avatar.url)
                return embed

        class PingView(discord.ui.View):
            @discord.ui.button(label="Ping", style=discord.ButtonStyle.primary, emoji="🏓")
            async def ping_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                latency = round(bot.latency * 1000) if hasattr(bot, 'latency') else 'N/A'
                embed = PingEmbedFactory(interaction.user, latency).build()
                await interaction.response.send_message(embed=embed, ephemeral=True, view=PingView())

        latency = round(bot.latency * 1000) if hasattr(bot, 'latency') else 'N/A'
        embed = PingEmbedFactory(interaction.user, latency).build()
        await interaction.response.send_message(embed=embed, ephemeral=True, view=PingView())

    # Comando /info
    @bot.tree.command(name="info", description="Mostra informações sobre o bot")
    async def info(interaction: discord.Interaction):
        embed = discord.Embed(
            title="Informações do Bot",
            description="Detalhes sobre o bot Izza Study",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.add_field(name="Nome", value=bot.user.name, inline=True)
        embed.add_field(name="ID", value=bot.user.id, inline=True)
        embed.add_field(name="Latência", value=f"{round(bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Comando de Ajuda", value="/ajuda", inline=False)
        embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Comando /server
    @bot.tree.command(name="server", description="Mostra informações sobre o servidor")
    async def server_info(interaction: discord.Interaction):
        guild = interaction.guild
        owner = guild.owner
        embed = discord.Embed(
            title=f"Informações do Servidor: {guild.name}",
            description=guild.description if guild.description else "Sem descrição.",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        embed.add_field(name="ID do Servidor", value=guild.id, inline=True)
        embed.add_field(name="Dono", value=f"{owner} (ID: {owner.id})", inline=True)
        embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y %H:%M"), inline=False)
        embed.add_field(name="Membros", value=guild.member_count, inline=True)
        embed.add_field(name="Cargos", value=len(guild.roles), inline=True)
        embed.add_field(name="Canais de Texto", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Canais de Voz", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="Stickers", value=len(getattr(guild, "stickers", [])), inline=True)
        embed.add_field(name="Nível de Verificação", value=str(guild.verification_level), inline=True)
        embed.add_field(name="AFK Timeout", value=f"{guild.afk_timeout // 60} min" if guild.afk_timeout else "Não definido", inline=True)
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Comando /traduzir com botões e logs
    @bot.tree.command(name="traduzir", description="Traduz frase entre PT-BR e EN automaticamente")
    @app_commands.describe(frase="Frase em português ou inglês para tradução")
    async def traduzir(interaction: discord.Interaction, frase: str):

        await interaction.response.defer()

        try:
            traducao = translate_auto(frase)

            # Log do pedido de tradução
            log_line = f"[{datetime.datetime.now()}] {interaction.user} pediu tradução: '{frase}' -> '{traducao}'\n"
            with open("translation_log.txt", "a", encoding="utf-8") as f:
                f.write(log_line)

            # View com botões
            class TranslateView(discord.ui.View):
                def __init__(self, original_text, translated_text, author):
                    super().__init__(timeout=120)
                    self.original_text = original_text
                    self.translated_text = translated_text
                    self.author = author

                @discord.ui.button(label="Copiar Tradução", style=discord.ButtonStyle.primary, emoji="📋")
                async def copiar(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                    if interaction_button.user != self.author:
                        await interaction_button.response.send_message("Só quem usou o comando pode usar este botão.", ephemeral=True)
                        return
                    try:
                        await interaction_button.user.send(f"Tradução copiada:\n{self.translated_text}")
                        await interaction_button.response.send_message("Enviei a tradução no seu DM para você copiar!", ephemeral=True)
                    except discord.Forbidden:
                        await interaction_button.response.send_message("Não consegui enviar DM. Ative suas DMs para receber a tradução.", ephemeral=True)

                @discord.ui.button(label="Enviar Tradução", style=discord.ButtonStyle.success, emoji="📤")
                async def enviar(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                    if interaction_button.user != self.author:
                        await interaction_button.response.send_message("Só quem usou o comando pode usar este botão.", ephemeral=True)
                        return

                    channel = interaction_button.channel
                    webhooks = await channel.webhooks()
                    webhook = None
                    for wh in webhooks:
                        if wh.name == "IzzaBot Webhook":
                            webhook = wh
                            break
                    if webhook is None:
                        webhook = await channel.create_webhook(name="IzzaBot Webhook")

                    await webhook.send(
                        content=self.translated_text,
                        username=interaction_button.user.display_name,
                        avatar_url=interaction_button.user.display_avatar.url
                    )

                    await interaction_button.response.send_message("Mensagem enviada no canal via webhook!", ephemeral=True)

                    # Log do envio via webhook
                    log_line_send = f"[{datetime.datetime.now()}] {interaction_button.user} enviou mensagem via webhook: {self.translated_text}\n"
                    with open("translation_log.txt", "a", encoding="utf-8") as f:
                        f.write(log_line_send)

            view = TranslateView(frase, traducao, interaction.user)
            await interaction.followup.send(f"**Tradução:** {traducao}", view=view)

        except Exception as e:
            await interaction.followup.send(f"Erro na tradução: {e}")
