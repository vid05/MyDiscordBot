import discord
from discord.ext import commands
from database_setup import db
import logging


class Welcome(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('〉Welcome module ready')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = self.client.get_guild(804313983594004521)
        member_role = discord.utils.get(guild.roles, name='Member')
        data = {
            'name': str(member),
            'strikes': 0
        }
        db.collection('members').document(str(member.id)).set(data)
        await member.add_roles(member_role)
        embed = discord.Embed(
            title='WELCOME',
            description=member.mention,
            colour=discord.Colour.blurple())

        embed.add_field(name=f'Welcome {member.display_name}', value='Hello')
        channel = self.client.get_channel(804347217330176002)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        db.collection('members').document(str(member.id)).delete()


def setup(client):
    client.add_cog(Welcome(client=client))
