import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, Select, SelectOption
from cfg import TOKEN
import sys
import youtube_dl
import asyncio
import requests
import random
import _sqlite3

with open('cfg.txt') as f:
    cfg = eval(f.read())

client = commands.Bot(command_prefix=cfg['PREFIX'], intents=discord.Intents.all(), help_command=None)
DiscordComponents(client)


@client.event
async def on_ready():
    members = []
    for member in client.get_guild(963418450611539988).members:
        if not member.bot:
            members.append(member.name)
    print('Работает')


@client.command(name='help')
async def help(ctx):
    embed = discord.Embed(title='Help',
                          description='\n```fix\nКоманды для управления ботом```'
                                      '\n**prefix <новый префикс>** - ***меняет префикс***\n\n'
                                      '**off** - ***выключает бота***\n\n'
                                      '**ping** - ***возвращает задержку***\n\n'
                                      '\n```fix\nКоманды для управления участниками```'
                                      '\n**mute <@ник>** - ***замутит участника***\n\n'
                                      '**unmute <@ник>** - ***размутит участника***\n\n'
                                      '**kick <@ник> <причина>** - ***кикает участника с сервера по причине...***\n\n'
                                      '**ban <@ник> <причина>** - ***банит участника по причине...\n\n***'
                                      '```fix\nКоманды для управления музыкой```'
                                      '**\nplay <ссылка на YouTube>** - ***проигрывает музыку с видео по ссылке***\n\n'
                                      '**next** - ***включает следующую песню***\n\n'
                                      '**stop** - ***останавливает, что играет сейчас***\n\n'
                                      '**resume** - ***продолжает***\n\n'
                                      '**list** - ***показывает очередь песен***\n\n'
                                      '**clear** - ***очищает всю очередь и перестаёт играть***\n\n',
                          color=0xff9900)
    await ctx.send(embed=embed)


# ----------  Команды для бота  ----------
@client.command(name='prefix')
async def prefix(ctx, new_prefix=None):
    if not new_prefix:
        emb = discord.Embed(title=f"Префикс бота - {cfg['PREFIX']}",
                            description='Чтобы сменить префикс, напишите '
                                        '<текущий префикс>prefix <новый префикс>',
                            colour=discord.Color.dark_blue())
        await ctx.send(embed=emb)
    else:
        client.command_prefix = new_prefix
        with open('cfg.txt', 'w') as f:
            cfg['PREFIX'] = new_prefix
            f.write(str(cfg))
        emb = discord.Embed(title="Префикс бота изменен",
                            description=f'Префикс бота успешно изменен на {new_prefix}',
                            colour=discord.Color.dark_blue())
        await ctx.send(embed=emb)


@client.command(name='off')
async def off(ctx):
    if ctx.author.id == 375939678991286282:
        emb = discord.Embed(title="Выключаюсь...",
                            colour=discord.Color.red())
        await ctx.send(embed=emb)

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        await sys.exit(0)
    else:
        emb = discord.Embed(title=f"{ctx.author.name} Нет прав на совершение данной команды!",
                            colour=discord.Color.red())
        await ctx.send(embed=emb)


# ----------  Команды для юзера  ----------
@client.command(name='mute')
async def mute(ctx, member: discord.Member):
    if ctx.author.id == 375939678991286282:
        emb = discord.Embed(title="Участник был замучен!",
                            colour=discord.Color.red())
        emb.set_author(name=member.name,
                       icon_url=member.avatar_url)
        emb.set_footer(text=f"Его замутил {ctx.author.name}",
                       icon_url=ctx.author.avatar_url)
        await ctx.send(embed=emb)
        muted_role = discord.utils.get(ctx.message.guild.roles, name="Muted")
        await member.add_roles(muted_role)
    else:
        emb = discord.Embed(title=f"{ctx.author.name} Нет прав на совершение данной команды!",
                            colour=discord.Color.red())
        await ctx.send(embed=emb)


@client.command(name='unmute')
async def unmute(ctx, member: discord.Member):
    if ctx.author.id == 375939678991286282:
        emb = discord.Embed(title="Участник был размучен!", colour=discord.Color.green())
        emb.set_author(name=member.name,
                       icon_url=member.avatar_url)
        emb.set_footer(text=f"Его размутил {ctx.author.name}",
                       icon_url=ctx.author.avatar_url)
        await ctx.send(embed=emb)
        muted_role = discord.utils.get(ctx.message.guild.roles, name="Muted")
        await member.remove_roles(muted_role)
    else:
        emb = discord.Embed(title=f"{ctx.author.name} Нет прав на совершение данной команды!",
                            colour=discord.Color.red())
        await ctx.send(embed=emb)


@client.command(name='ping')
async def ping(ctx):
    emb = discord.Embed(title=f"Задержка: {client.latency}",
                        colour=discord.Color.gold())
    await ctx.send(embed=emb)


@client.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member=None, *, reason='не указана'):
    if ctx.author.id == 375939678991286282:
        await ctx.guild.kick(member)
        emb = discord.Embed(title="Прощай!",
                            colour=discord.Color.red())
        emb.set_author(name=member.name,
                       icon_url=member.avatar_url)
        emb.set_footer(text=f"{member.name} был кикнут {ctx.author.name} по причине {reason}",
                       icon_url=ctx.author.avatar_url)
        await ctx.send(embed=emb)
    else:
        emb = discord.Embed(title=f"{ctx.author.name} Нет прав на совершение данной команды!",
                            colour=discord.Color.red())
        await ctx.send(embed=emb)


@client.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member=None, reason='не указана'):
    if ctx.author.id == 375939678991286282:
        await member.ban(reason=reason)
        emb = discord.Embed(title="Чтож, возможно, мы больше не встретимся!",
                            colour=discord.Color.red())
        emb.set_author(name=member.name,
                       icon_url=member.avatar_url)
        emb.set_footer(text=f"{member.name} был забанен {ctx.author.name} по причине {reason}",
                       icon_url=ctx.author.avatar_url)
        await ctx.send(embed=emb)
    else:
        emb = discord.Embed(title=f"{ctx.author.name} Нет прав на совершение данной команды!",
                            colour=discord.Color.red())
        await ctx.send(embed=emb)


# ----------  Команды для музыки  ----------
song_list = []

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


@client.command(name='join')
async def join(ctx):
    if not ctx.message.author.voice:
        emb = discord.Embed(title=f'{ctx.message.author.name} вы не подключены к голосовому каналу',
                            colour=discord.Color.red())
        await ctx.send(embed=emb)
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@client.command(name='leave')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        emb = discord.Embed(title='Бот не подключен к голосовому каналу',
                            colour=discord.Color.red())
        await ctx.send(embed=emb)


@client.command(name='play')
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        filename = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        emb = discord.Embed(title=f'**Сейчас играет:** {url}',
                            colour=discord.Color.purple())
        await ctx.send(embed=emb)
    except:
        emb = discord.Embed(title='Бот не подключен к голосовому каналу',
                            colour=discord.Color.red())
        await ctx.send(embed=emb)


@client.command(name='pause')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        emb = discord.Embed(title='Бот сейчас ничего не играет или уже стоит на паузе',
                            colour=discord.Color.red())
        await ctx.send(embed=emb)


@client.command(name='resume')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        emb = discord.Embed(title='Бот ничего не играл или уже играет',
                            colour=discord.Color.red())
        await ctx.send(embed=emb)


@client.command(name='stop')
async def stop(ctx):
    global song_list
    song_list = []
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        emb = discord.Embed(title='Бот не подключен к голосовому каналу',
                            colour=discord.Color.red())
        await ctx.send(embed=emb)


# ----------  Другие команды  ----------
@client.command(name='map')
async def map(ctx, lon, lat, z):
    params = {
        'll': f'{lon},{lat}',
        'z': z,
        'l': 'map'
    }
    api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(api_server, params=params)
    if not response:
        emb = discord.Embed(title='Ошибка выполнения запроса:',
                            description=f'{response}\n'
                            f'Http статус: {response.status_code} ({response.reason})',
                            colour=discord.Color.red())
        await ctx.send(embed=emb)
    else:
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)
        with open('map.png', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)


@client.command(name='rps')
async def rps(ctx):
    for emoji in ctx.guild.emojis:
        print(emoji, emoji.id)
    emb = discord.Embed(title='Выберите свой вариант',
                        colour=discord.Color.blurple())
    await ctx.send(embed=emb)
    await ctx.send(components=[
        [Button(label=f'Камень 👊', custom_id = "button1"),
         Button(label='Ножницы ✋', custom_id = "button2"),
         Button(label='Бумага ✌️', custom_id = "button3")]
        ]
    )
    choice = random.choice([1, 2, 3])
    interaction1 = await client.wait_for("button_click", check=lambda i: i.custom_id == "button1")
    interaction2 = await client.wait_for("button_click", check=lambda i: i.custom_id == "button2")
    interaction3 = await client.wait_for("button_click", check=lambda i: i.custom_id == "button3")
    user = 0
    if interaction1:
        user = 1
    elif interaction2:
        user = 2
    elif interaction3:
        user = 3
    res = 0
    if user:
        if choice == user:
            res = 0
        elif choice == 1 and user == 3 or\
            choice == 2 and user == 1 or\
            choice == 3 and user == 2:
            res = 1
        else:
            res = 2
    if res == 0:
        await interaction1.send('hello')
        emb = discord.Embed(title='Ничья!',
                        colour=discord.Color.dark_grey())
        await ctx.send(embed=emb)
    if res == 1:
        emb = discord.Embed(title='Вы победили!',
                        colour=discord.Color.dark_green())
        await ctx.send(embed=emb)
    else:
        emb = discord.Embed(title='Бот победил!',
                        colour=discord.Color.dark_red())
        await ctx.send(embed=emb)


@client.command(name='roulette')
async def roulette(ctx, bullets):
    try:
        bullets = int(bullets)
        if bullets < 0:
            emb = discord.Embed(title='А как?',
                                colour=discord.Color.greyple())
            await ctx.send(embed=emb)
        elif bullets == 0:
            emb = discord.Embed(title='Нет, ну так уж совсем не честно',
                                colour=discord.Color.greyple())
            await ctx.send(embed=emb)
        elif 0 < bullets < 6:
            li = ['kill']
            li += [0] * bullets
            choice = random.choice(li)
            if choice == 'kill':
                emb = discord.Embed(title=f'{ctx.author.name} смело спустил курок и...',
                                    description='отправился на тот свет...',
                                    colour=discord.Color.dark_red())
                await ctx.send(embed=emb)
                await ctx.author.ban(reason='Удача отвернулась от вас...')
            else:
                emb = discord.Embed(title=f'{ctx.author.name} смело спустил курок и...',
                                    description='ничего не прозошло...',
                                    colour=discord.Color.dark_green())
                await ctx.send(embed=emb)
        elif bullets >= 6:
            emb = discord.Embed(title='Многовато получается',
                                colour=discord.Color.greyple())
            await ctx.send(embed=emb)
    except Exception:
        emb = discord.Embed(title='А как?',
                            colour=discord.Color.greyple())
        await ctx.send(embed=emb)



@client.command()
async def button(ctx):
    await ctx.send(
        "...",
        components = [
            Button(label = "название кнопочки", custom_id = "button1")
        ]
    )

    interaction = await client.wait_for("button_click", check = lambda i: i.custom_id == "button1")
    await interaction.send(content="ага",
                           components=[
                               Button(label="кнопочка", custom_id="button1")
        ])


@client.command()
async def select(ctx):
    await ctx.send(
        "текст",
        components=[
            Select(
                placeholder="выбрать",
                options=[
                    SelectOption(label="A", value="A"),
                    SelectOption(label="B", value="B")
                ]
            )
        ]
    )

    interaction = await client.wait_for("select_option")
    await interaction.send(content = f"{interaction.values[0]}")


client.run(TOKEN)
