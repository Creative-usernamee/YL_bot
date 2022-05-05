import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button
from cfg import TOKEN
import sys
import youtube_dl
import asyncio
import requests
import random
import sqlite3

with open('cfg.txt') as f:
    cfg = eval(f.read())

client = commands.Bot(command_prefix=cfg['PREFIX'], intents=discord.Intents.all(), help_command=None)
DiscordComponents(client)


@client.event
async def on_ready():
    con = sqlite3.connect('cfg.db')
    cur = con.cursor()
    members = cur.execute('SELECT member, points FROM scores').fetchall()
    members_names = [i[0] for i in members]
    for member in client.get_guild(481084805820448779).members:
        if not member.bot:
            if str(member.name) not in members_names:
                cur.execute("INSERT INTO scores VALUES(?, 0)", (member.name))
    con.commit()
    print('Работает')


@client.command(name='help')
async def help(ctx):
    p = cfg['PREFIX']
    embed = discord.Embed(title='Help',
                          color=0xff9900)
    embed.add_field(name='Управление ботом', value='_', inline=False)
    embed.add_field(name=f'{p}prefix <префикс>', value='Сменить префикс', inline=False)
    embed.add_field(name=f'{p}off', value='Выключает бота', inline=False)
    embed.add_field(name=f'{p}ping', value='Возвращает задержку\n_', inline=False)

    embed.add_field(name='Управление участниками', value='_', inline=False)
    embed.add_field(name=f'{p}mute', value='Замутит участника', inline=False)
    embed.add_field(name=f'{p}unmute', value='Размутит участника', inline=False)
    embed.add_field(name=f'{p}kick <@ник> <причина>', value='Кикает участника с сервера по причине...', inline=False)
    embed.add_field(name=f'{p}ban <@ник> <причина>', value='Банит участника по причине...\n_', inline=False)

    embed.add_field(name='Управление музыкой', value='_', inline=False)
    embed.add_field(name=f'{p}play <ссылка на YouTube>', value='Проигрывает музыку с видео по ссылке', inline=False)
    embed.add_field(name=f'{p}stop', value='Останавливает, что играет сейчас', inline=False)
    embed.add_field(name=f'{p}resume', value='Продолжает\n_', inline=False)

    embed.add_field(name='Другие команды', value='_', inline=False)
    embed.add_field(name=f'{p}map <шир, дол, зум от 1 до 15>', value='Возвращает карту заданных координат',
                    inline=False)
    embed.add_field(name=f'{p}rps', value='Сыграйте с ботом в игру', inline=False)
    embed.add_field(name=f'{p}roulette', value='Попытайте совю удачу (не повезет - получите бан)', inline=False)

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


# ----------  Команды для юзеров  ----------
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
async def kick(ctx, member: discord.Member = None, *, reason='не указана'):
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
async def ban(ctx, member: discord.Member = None, reason='не указана'):
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


@client.event
async def on_button_click(interaction):
    if interaction.component.label.startswith("Камень") or \
            interaction.component.label.startswith("Ножницы") or \
            interaction.component.label.startswith("Бумага"):
        choice = random.choice(['Камень', 'Ножницы', 'Бумага'])
        if interaction.component.label.startswith("Камень"):
            user = 'Камень'
        elif interaction.component.label.startswith("Ножницы"):
            user = 'Ножницы'
        else:
            user = 'Бумага'
        res = 0
        if user:
            if choice == user:
                res = 0
            elif choice == 'Камень' and user == 'Бумага' or \
                    choice == 'Ножницы' and user == 'Камень' or \
                    choice == 'Бумага' and user == 'Ножницы':
                res = 1
            else:
                res = 2
        if res == 0:
            emb = discord.Embed(title='Ничья!',
                                description=f'Вы выбрали {user}\n'
                                            f'Бот выбрал {choice}',
                                colour=discord.Color.dark_grey())
            await interaction.send(embed=emb)
        elif res == 1:
            emb = discord.Embed(title='Вы победили!',
                                description=f'Вы выбрали {user}\n'
                                            f'Бот выбрал {choice}',
                                colour=discord.Color.dark_green())
            await interaction.send(embed=emb)
        else:
            emb = discord.Embed(title='Бот победил!',
                                description=f'Вы выбрали {user}\n'
                                            f'Бот выбрал {choice}',
                                colour=discord.Color.dark_red())
            await interaction.send(embed=emb)
    elif interaction.component.label.startswith("Очки"):
        con = sqlite3.connect('cfg.db')
        cur = con.cursor()
        cur_points = cur.execute(f'SELECT points FROM scores WHERE member = ?',
                                 (interaction.author.name,)).fetchone()[0]
        emb = discord.Embed(title=f'Ваше кол-во очков: {cur_points}',
                            color=discord.Color.dark_gold())
        await interaction.send(embed=emb)
    else:
        bullets = int(interaction.component.label)
        label = [1] * bullets
        while len(label) != 6:
            label.append(0)
        row = ''
        for place in label:
            if place == 1:
                row += ':red_circle:'
            else:
                row += ':white_circle:'
        if bullets == 1:
            end = 'ю'
        elif 2 <= bullets <= 4:
            end = 'и'
        else:
            end = 'ь'
        emb = discord.Embed(color=discord.Color.dark_grey())
        emb.add_field(name='Ну, поехали!',
                      value=f'Итак, заряжаем {bullets} {"пул" + end} \n\n'
                            f'{row}',
                      inline=False)

        choice = random.choice(label)

        if choice == 1:
            emb.add_field(name='\nВы уверенно спустили урок и... раздался громкий выстрел',
                          value='...',
                          inline=False)
            con = sqlite3.connect('cfg.db')
            cur = con.cursor()
            cur.execute(f'UPDATE scores SET points = ? WHERE member = ?',
                        (0, interaction.author.name,)).fetchall()
            con.commit()
            await interaction.send(embed=emb)
            await interaction.author.ban(reason="Повезет в следующий р... А, нет, вы же мертвы...",
                                         delete_message_days=0)

        else:
            points = 10 * bullets
            emb.add_field(name='\nВы уверенно спустили урок и... разадался тихий щелчок',
                          value=f'Сегодня удача улыбнулась вам... Очков получено: {points}',
                          inline=False)
            await interaction.send(embed=emb)
            con = sqlite3.connect('cfg.db')
            cur = con.cursor()
            cur_points = cur.execute(f'SELECT points FROM scores WHERE member = ?',
                                     (interaction.author.name,)).fetchone()[0]
            cur_points += points
            cur.execute(f'UPDATE scores SET points = ? WHERE member = ?',
                        (cur_points, interaction.author.name,)).fetchall()
            con.commit()


@client.command(name='rps')
async def rps(ctx):
    emb = discord.Embed(title='Выберите свой вариант',
                        colour=discord.Color.blurple())
    await ctx.send(embed=emb)
    await ctx.send(components=[
        [Button(label='Камень 👊', custom_id="button1"),
         Button(label='Ножницы ✌️', custom_id="button2"),
         Button(label='Бумага ✋', custom_id="button3")]
    ]
    )


@client.command(name='roulette')
async def roulette(ctx):
    emb = discord.Embed(title='Сколько пуль зарядить?',
                        description='Кол-во полученных очков будет равно <кол-во пуль> * 10',
                        colour=discord.Color.blurple())
    await ctx.send(embed=emb)
    await ctx.send(components=[
        [Button(label='1', custom_id="button1", style=1),
         Button(label='2', custom_id="button2", style=1),
         Button(label='3', custom_id="button3", style=1),
         Button(label='4', custom_id="button4", style=1),
         Button(label='5', custom_id="button5", style=1),
         ], Button(label='Очки', custom_id="button6", style=3)
    ]
    )


client.run(TOKEN)
