import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix='!', intents=intents)
client.author_id = 538808063122079744
db = firestore.client()


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))
    print('Bot is ready')


@client.event
async def on_command_error(ctx, error):
    await ctx.send(f'`{error}`')


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
        await ctx.send(f'Module *{extension}* is unloaded.')


@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    if ctx.message.author.id == client.author_id:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f'Module *{extension}* was reloaded.')


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong {round(client.latency * 1000)} ms')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[: -3]}')

load_dotenv('.env')
client.run(os.getenv('DISCORD_BOT_SECRET'))
