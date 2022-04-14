import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, Select, SelectOption
from cfg import TOKEN

with open('cfg.txt') as f:
    cfg = eval(f.read())

client = commands.Bot(command_prefix=cfg['PREFIX'], intents=discord.Intents.all(), help_command=None)
DiscordComponents(client)


@client.event
async def on_ready():
    print('Работает')


@client.command(name='help')
async def help(ctx):
    embed = discord.Embed(title='Help',
                          description='\n```fix\nКоманды для управления участниками```'
                                      '\n**mute <@ник>** - ***мутит участника***\n\n'
                                      '**unmute <@ник>** - ***размутит участника***\n\n'
                                      '**kick <@ник> <причина>** - ***кикает участника с сервера по причине...***\n\n'
                                      '**ban <@ник> <причина>** - ***банит участника по причине...\n\n\n***'
                                      '```fix\nКоманды для управления музыкой```'
                                      '**\nplay <ссылка на YouTube>** - ***проигрывает музыку с видео по ссылке***\n\n'
                                      '**next** - ***включает следующую песню***\n\n'
                                      '**stop** - ***останавливает, что играет сейчас***\n\n'
                                      '**resume** - ***продолжает***\n\n'
                                      '**list** - ***показывает очередь песен***\n\n'
                                      '**clear** - ***очищает всю очередь и перестаёт играть***\n\n',
                          color=0xff9900)
    await ctx.send(embed=embed)


@client.command(name='prefix')
async def prefix(ctx, new_prefix = None):
    if not new_prefix:
        emb = discord.Embed(title=f"Префикс бота - {cfg['PREFIX']}", description='Чтобы сменить префикс, напишите '
                                                                  '<текущий префикс>prefix <новый префикс>',
                            colour=discord.Color.blue())
        await ctx.send(embed=emb)
    else:
        client.command_prefix = new_prefix
        with open('cfg.txt', 'w') as f:
            cfg['PREFIX'] = new_prefix
            f.write(str(cfg))
        emb = discord.Embed(title="Префикс бота изменен", description=f'Префикс бота успешно изменен на {new_prefix}',
                            colour=discord.Color.blue())
        await ctx.send(embed=emb)



@client.command(name='mute')
async def mute(ctx, member: discord.Member):
    emb = discord.Embed(title="Участник был замучен!", colour=discord.Color.blue())
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.set_footer(text="Его замутил {}".format(ctx.author.name), icon_url=ctx.author.avatar_url)
    await ctx.send(embed=emb)
    muted_role = discord.utils.get(ctx.message.guild.roles, name="Muted")
    await member.add_roles(muted_role)


@client.command(name='unmute')
async def unmute(ctx, member: discord.Member):
    emb = discord.Embed(title="Участник был размучен!", colour=discord.Color.blue())
    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.set_footer(text="Его размутил {}".format(ctx.author.name), icon_url=ctx.author.avatar_url)
    await ctx.send(embed=emb)
    muted_role = discord.utils.get(ctx.message.guild.roles, name="Muted")
    await member.remove_roles(muted_role)


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
