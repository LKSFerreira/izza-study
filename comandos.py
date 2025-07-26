import discord


def setup_comandos(bot: discord.Client):
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

        embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed, ephemeral=True)

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
                # Responde com um novo embed e uma nova view, mantendo o botão sempre disponível
                await interaction.response.send_message(embed=embed, ephemeral=True, view=PingView())

        latency = round(bot.latency * 1000) if hasattr(bot, 'latency') else 'N/A'
        embed = PingEmbedFactory(interaction.user, latency).build()
        await interaction.response.send_message(embed=embed, ephemeral=True, view=PingView())

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
