#!/usr/bin/env python3

import discord
from discord import player
from discord import guild
from discord.ext import commands
from discord import FFmpegPCMAudio
import youtube_dl

client = commands.Bot(command_prefix="?")

intents = discord.Intents.default()
intents.members = True

queues = []

def check_queue(ctx):
    if queues:
        voice = ctx.guild.voice_client
        source = queues.pop(0)
        player = voice.play(source)

@client.event
async def on_ready():
    print("The Bot is online!")

@client.command()
async def hello(ctx):
    await ctx.send("Hello!")

@client.command(pass_context = True)
async def play(ctx, arg):

    voice = ctx.guild.voice_client

    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

    guild_id = ctx.message.guild.id

    if not voice_client:
        if ctx.author.voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        else:
            await ctx.send("You are not in a voice channel!")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(arg, download=False)
        url = info['formats'][0]['url']
        source = FFmpegPCMAudio(url)
        
        try:
            player = voice.play(source, after=lambda x=None: check_queue(ctx))
        except:
            queues.append(source)
            await ctx.send("Added to queue!")

@client.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("I am not playing!")

@client.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("I am already playing!")

@client.command(pass_context = True)
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    await ctx.send("Skipped!")

@client.command(pass_context = True)
async def leave(ctx):
    if(ctx.voice_client):
        queues.clear()
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("I am not on a voice channel!")

client.run("BOT_TOKEN")
