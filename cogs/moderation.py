import asyncio
import logging
from datetime import datetime

import discord
from discord.ext import commands
from pytimeparse import parse


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('〉Moderation module ready')

    async def log_event(self, event_name, event_description):
        embed = discord.Embed(
            title=event_name,
            description=f'{event_description}'
        )
        embed.timestamp = datetime.now()
        guild = self.client.get_guild(804313983594004521)
        logging_channel = guild.get_channel(804345250675294219)
        await logging_channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        clear_message = await ctx.send(f'`〉{amount} messages were deleted.`')
        await self.log_event('Bulk Deletion',
                             f'{ctx.message.author} has deleted {amount} messages in {ctx.channel.mention}')
        await asyncio.sleep(5)
        await clear_message.delete()

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, reason=None):
        await member.send(f'`〉You were kicked from {ctx.guild.name}.`')
        await member.kick(reason=reason)
        await ctx.send(f'`〉{member} was kicked.`')
        await self.log_event('Kick', f'{ctx.message.author} kicked {member}. Reason: {reason}')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason=None):
        await member.send(f'`〉You were banned from {ctx.guild.name}.`')
        await member.ban(reason=reason)
        await ctx.send(f'`〉{member} was banned.`')
        await self.log_event('Ban', f'{ctx.message.author} banned {member}. Reason: {reason}')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, member: discord.Member, duration: str, reason=None):
        await member.send(f'`〉You were banned from {ctx.guild.name} for {duration}.`')
        await member.ban(reason=reason)
        await ctx.send(f'`〉{member} was banned for {duration}.`')
        await self.log_event('Tempban', f'{ctx.message.author} banned {member} for {duration}. Reason: {reason}')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'〉{user.name} was unbanned.')
                await self.log_event('Unban', f'{ctx.message.author} unbanned {member}.')

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, reason=None):
        muted_role = discord.utils.get(ctx.guild.roles, name='muted')
        await member.send(f'`〉You were muted in {ctx.guild.name}. Duration: {duration}.`')
        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f'`〉{member} was muted. Duration: {duration}.`')
        await self.log_event('Mute', f'{ctx.message.author} muted {member}. Duration: {duration}. Reason: {reason}')

        if duration is not None:
            await asyncio.sleep(parse(duration))
            await member.remove_roles(muted_role)
            await member.send(f'`〉You are now unmuted in {ctx.guild.name}.`')


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name='muted')
        await member.remove_roles(muted_role)
        await member.send(f'`〉You are now unmuted in {ctx.guild.name}.`')
        await ctx.send(f'`〉{member} is unmmuted.`')
        await self.log_event('Unmute', f'{ctx.message.author} unmuted {member}.')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, warning: str):
        await member.send(f'`〉Warning: {warning}.`')
        await ctx.send(f'`〉{member} was warned.`')
        await self.log_event('Warn', f'{ctx.message.author} warned {member}. Warning: {warning}')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel, duration: str = None):
        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f'`〉{channel} is locked.`')
        await self.log_event('Channel Lock', f'{ctx.message.author} locked {channel}. Duration: {duration}')
        if duration is not None:
            await asyncio.sleep(parse(duration))
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send(f'`〉{channel} is unlocked.`')


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f'`〉{channel} is unlocked.`')
        await self.log_event('Channel Unlock', f'{ctx.message.author} unlocked {channel}.')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx):
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)

        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(ctx.guild.default_role, speak=False)

        await ctx.send('`〉All channels are locked.`')
        await self.log_event('Lockdown', f'{ctx.message.author} started lockdown.')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def endlockdown(self, ctx):
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)

        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(ctx.guild.default_role, speak=True)

        await ctx.send('`〉All channels are unlocked.`')
        await self.log_event('Lockdown End', f'{ctx.message.author} ended lockdown.')
        # todo fix so it doesnt unlock staff channels


def setup(client):
    client.add_cog(Moderation(client=client))
