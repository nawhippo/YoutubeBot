import time

from discord.ext import commands
from discord import FFmpegPCMAudio
import discord
import yt_dlp as youtube_dl

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

BOT_TOKEN = "MTIwMTk2MjcxODU3MjA2MDczMg.GMoZjf.2p1r6keE7KT_fv8GZn6IXU1ShxnZJeeWfEVrWA"
CHANNEL_ID = 1201970181794955335
VOICE_CHANNEL_ID = 697982161671684180
songPlaying = False
songlist = []


def notify(e):
    global songPlaying;
    if e['status'] == 'finished':
        songPlaying = False
    else:
        songPlaying = True


@bot.event
async def on_ready():
    print("Music bot ready to rock in the free world!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Music bot ready to rock in the free world!")


@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@bot.command()
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()


@bot.command()
async def queue(ctx):
    if songlist:
        await ctx.send("Queue:\n" + "\n".join(songlist))
    else:
        await ctx.send("The queue is currently empty.")


@bot.command()
async def play(ctx, url):
    global songPlaying
    channel = bot.get_channel(VOICE_CHANNEL_ID)

    await channel.send("Now playing: " + url)
    if ctx.voice_client is None:
        await join(ctx)

    voice_client = ctx.voice_client
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [notify]
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            await ctx.send(f'Now playing: {info["title"]}')
            songPlaying = True
            voice_client.play(FFmpegPCMAudio(url2))
        songlist.append(url)
    except youtube_dl.utils.DownloadError as e:
        await ctx.send("An error occurred while processing the song, but I'll try to continue.")
    songPlaying = False


def addsong(url):
    songlist.append(url)


def check_condition():
    return songPlaying == True


async def check():
    print("Polling song")
    while not check_condition():
        play(VOICE_CHANNEL_ID, songlist[0])
        time.sleep(1)


bot.run(BOT_TOKEN)
