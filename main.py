import logging
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix='!', intents=intents)
client.author_id = 538808063122079744


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))
    logging.info('Bot is ready')
    # creates muted role if it doesnt exist
    guild = client.get_guild(804313983594004521)
    muted_role = discord.utils.get(guild.roles, name='muted')
    if not muted_role:
        muted_role = await guild.create_role(name='muted')
    for channel in guild.text_channels:
        await channel.set_permissions(muted_role, send_messages=False)
    for channel in guild.voice_channels:
        await channel.set_permissions(muted_role, speak=False)


@client.event
async def on_command_error(ctx, error):
    await ctx.send(f'`〉{error}`')


@client.command()
async def load(ctx, extension):
    if ctx.message.author.id == client.author_id:
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f'Module **{extension}** is loaded.')


@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    if ctx.message.author.id == client.author_id:
        client.unload_extension(f'cogs.{extension}')
        await ctx.send(f'Module **{extension}** is unloaded.')


@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    if ctx.message.author.id == client.author_id:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f'Module **{extension}** was reloaded.')


@client.command()
async def ping(ctx):
    await ctx.send(f'`〉Pong: {round(client.latency * 1000)} ms`')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[: -3]}')

load_dotenv('.env')
client.run(os.getenv('DISCORD_BOT_SECRET'))
