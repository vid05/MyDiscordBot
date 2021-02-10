import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from database_setup import db
import logging


class BotOrders(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('〉Bot orders module ready')

    @commands.command()
    async def order(self, ctx, plan):
        # todo set plans
        approve_emoji = '✅'
        orders_channel = self.client.get_channel(809020971196481567)
        embed = discord.Embed(
            title='Orded',
            description=f'{ctx.message.author} has ordered plan `{plan}`',
            # todo add colour for embed
        )
        embed.timestamp = datetime.now()
        order_message = await orders_channel.send(embed=embed)
        await order_message.add_reaction(approve_emoji)
        order_data = {
            'member_id': ctx.message.author.id,
            'plan': str(plan),
            'timestamp': datetime.now(),
        }
        db.collection('orders').document(str(order_message.id)).set(order_data)
        await ctx.message.author.send('`Your order has been submitted`')
        await asyncio.sleep(5)
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        orders_channel = self.client.get_channel(809020971196481567)
        guild = self.client.get_guild(804313983594004521)
        if payload.channel_id == orders_channel.id and payload.user_id != 808309381414256650:
            order_message = payload.message_id
            developer = guild.get_member(payload.user_id)
            db.collection('orders').document(str(order_message)).update({'developer_id': str(developer.id)})
            data_dict = db.collection('orders').document(str(order_message)).get().to_dict()
            member_id = data_dict.get('member_id')
            member = guild.get_member(member_id)
            plan = data_dict.get('plan')
            await developer.send(f'`Order accepted. Bot is for {str(member)}. Plan: {plan}`')
            await member.send(f'`Your order has been accepted by {developer}.`')
            timestamp = data_dict.get('timestamp')
            embed = discord.Embed(
                title=f'Order {order_message}',
                description=f'Developer: `{developer}`. Member: `{str(member)}`. Plan: `{plan}`. Order date: `{timestamp}`'
            )
            order_logs = self.client.get_channel(809051264322240563)
            log_message = await order_logs.send(embed=embed)
            db.collection('orders').document(str(order_message)).update({'log_message_id': log_message.id})
            msg = await orders_channel.fetch_message(order_message)
            await msg.delete()

    @commands.command()
    @commands.is_owner()
    async def orderclose(self, ctx, order):
        guild = self.client.get_guild(804313983594004521)
        close_message = await ctx.send(f'Order {order} is closed.')
        await close_message.delete()
        await ctx.message.delete()
        plan = db.collection('orders').document(str(order)).get().to_dict().get('plan')
        timestamp = db.collection('orders').document(str(order)).get().to_dict().get('timestamp')
        developer_id = db.collection('orders').document(str(order)).get().to_dict().get('developer_id')
        developer = guild.get_member(developer_id)
        member_id = db.collection('orders').document(str(order)).get().to_dict().get('member_id')
        member = guild.get_member(member_id)
        log_message_id = db.collection('orders').document(str(order)).get().to_dict().get('log_message_id')
        log_message = await ctx.fetch_message(log_message_id)
        closed_embed = discord.Embed(
            title=f'Order {order}',
            description=f'Developer: `{developer}`. Member: `{str(member)}`. Plan: `{plan}`. Order date: `{timestamp}`',
            colour=0xe74c3c
        )
        await log_message.edit(embed=closed_embed)
        db.collection('orders').document(str(order)).delete()


def setup(client):
    client.add_cog(BotOrders(client=client))
