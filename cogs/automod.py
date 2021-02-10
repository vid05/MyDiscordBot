import asyncio
import logging
import re
from datetime import datetime

import discord
from discord.ext import commands
from database_setup import db


class Automod(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('〉Automod module ready')
        while True:
            await asyncio.sleep(6)
            with open('spam_detection.txt', 'r+') as file:
                file.truncate(0)

    async def log_event(self, event_name, event_description):
        guild = self.client.get_guild(804313983594004521)
        logging_channel = guild.get_channel(804345250675294219)
        embed = discord.Embed(
            title=event_name,
            description=event_description
        )
        embed.timestamp = datetime.now()
        await logging_channel.send(embed=embed)

    async def add_strike(self, client, member):
        guild = client.get_guild(804313983594004521)
        muted_role = discord.utils.get(guild.roles, name='muted')
        strikes = db.collection('members').document(str(member.id)).get().to_dict().get('strikes')
        db.collection('members').document(str(member.id)).update({'strikes': strikes + 1})
        strikes = db.collection('members').document(str(member.id)).get().to_dict().get('strikes')
        if strikes >= 5:
            await member.add_roles(muted_role)
            await member.send(f'`You are muted in {guild.name} for 6 hours.`')
            await self.log_event('Automod Mute', f'`{member.display_name}` was muted by automod')
            await asyncio.sleep(6)
            # todo make this 6 hours
            await member.remove_roles(muted_role)
            db.collection('members').document(str(member.id)).update({'strikes': 0})
            await self.log_event('Automod Mute', f'`{member.display_name}` was unmuted by automod')

    async def spam_detection(self, member: discord.Member, message):
        counter = 0
        with open('spam_detection.txt', 'r+') as file:
            for lines in file:
                if lines.strip('\n') == str(member.id):
                    counter += 1

            file.writelines(f'{str(member.id)}\n')
            if counter >= 5 and not member.permissions_in(message.channel).manage_messages:
                await member.send(f'`{member.mention} stop spamming!`')
                await self.add_strike(self.client, member)

    async def invite_links(self, member: discord.Member, message):
        if 'discord.gg' in message.content.lower() and not member.permissions_in(
                message.channel).manage_messages:
            await message.delete()
            await self.add_strike(client=self.client, member=member)
            await member.send(f'`Dont post server invites in {message.channel.name}!`')
            await self.log_event('Server Invite Deleted',
                                 f'Invite sent by `{member.display_name}` deleted in {message.channel.mention} by Automod.')

    async def links(self, member: discord.Member, message):
        urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', message.content)
        if len(urls) > 0 and not message.author.permissions_in(message.channel).embed_links:
            await message.delete()
            await message.author.send(f'`You dont have a permission to send links in {message.channel.name}`')
            await self.add_strike(client=self.client, member=member)
            await self.log_event('Link Deleted',
                                 f'Link sent by `{member.display_name}` deleted in {message.channel.mention} by Automod.')

    async def message_walls(self, member: discord.Member, message):
        message_letters = [char for char in message.content]
        if len(message_letters) > 200 and not message.author.permissions_in(message.channel).manage_messages:
            await message.author.send('`Dont send such long messages`')
            await message.delete()
            await self.add_strike(client=self.client, member=member)
            await self.log_event('Message Deleted',
                                 f'Message sent by `{member.display_name}` deleted in {message.channel.mention} by Automod.')

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.spam_detection(member=message.author, message=message)
        await self.invite_links(member=message.author, message=message)
        await self.links(member=message.author, message=message)
        await self.message_walls(member=message.author, message=message)


def setup(client):
    client.add_cog(Automod(client=client))
