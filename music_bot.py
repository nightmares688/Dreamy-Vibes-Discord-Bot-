import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Sync slash commands
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# YT-DLP setup
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

def get_audio(url):
    info = ytdl.extract_info(url, download=False)

    # Fix for playlists
    if 'entries' in info:
        info = info['entries'][0]

    return info['url']

# /join
@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ You must be in a voice channel")
        return

    vc = interaction.guild.voice_client

    if vc is None:
        await interaction.user.voice.channel.connect()
        await interaction.response.send_message("✅ Joined voice channel")
    else:
        await interaction.response.send_message("⚠️ Already connected")

# /leave
@bot.tree.command(name="leave", description="Leave voice channel")
async def leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        await vc.disconnect()
        await interaction.response.send_message("👋 Left voice channel")
    else:
        await interaction.response.send_message("❌ Not in a voice channel")

# /play
@bot.tree.command(name="play", description="Play a song from YouTube URL")
@app_commands.describe(url="YouTube URL")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    if not interaction.user.voice:
        await interaction.followup.send("❌ Join a voice channel first")
        return

    vc = interaction.guild.voice_client

    # Prevent reconnect loop
    if vc is None:
        vc = await interaction.user.voice.channel.connect()
    elif vc.channel != interaction.user.voice.channel:
        await vc.move_to(interaction.user.voice.channel)

    try:
        source = get_audio(url)

        if vc.is_playing():
            vc.stop()

        vc.play(discord.FFmpegPCMAudio(source, **ffmpeg_options))



        await interaction.followup.send("🎶 Playing!")
    except Exception as e:
        print(e)
        await interaction.followup.send(f"❌ Error: {e}")

# /pause
@bot.tree.command(name="pause", description="Pause music")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸ Paused")
    else:
        await interaction.response.send_message("❌ Nothing playing")

# /resume
@bot.tree.command(name="resume", description="Resume music")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶ Resumed")
    else:
        await interaction.response.send_message("❌ Nothing paused")

# /stop
@bot.tree.command(name="stop", description="Stop music")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        vc.stop()
        await interaction.response.send_message("⏹ Stopped")
    else:
        await interaction.response.send_message("❌ Nothing playing")

# RUN BOT
import os
bot.run(os.getenv("TOKEN"))

