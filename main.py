import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, Select, SelectOption
from cfg import TOKEN


client = commands.Bot(command_prefix='!', intents=discord.Intents.all())
DiscordComponents(client)


@client.event
async def on_ready():
    print('Работает')


@client.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Ping: {client.latency}')


@client.command()
async def button(ctx):
    await ctx.send(
        "...",
        components = [
            Button(label = "название кнопочки", custom_id = "button1")
        ]
    )

    interaction = await client.wait_for("button_click", check = lambda i: i.custom_id == "button1")
    await interaction.send(content="ага", components=[
            Button(label = "кнопочка", custom_id = "button1")
        ])


@client.command()
async def select(ctx):
    await ctx.send(
        "текст",
        components = [
            Select(
                placeholder = "выбрать",
                options = [
                    SelectOption(label = "A", value = "A"),
                    SelectOption(label = "B", value = "B")
                ]
            )
        ]
    )

    interaction = await client.wait_for("select_option")
    await interaction.send(content = f"{interaction.values[0]}")


client.run(TOKEN)
