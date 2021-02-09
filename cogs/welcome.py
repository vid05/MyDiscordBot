import discord
from discord.ext import commands
from database_setup import db


class Welcome(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.welcome_channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        print('Welcome module ready')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        data = {
            'name': str(member),
            'strikes': 0
        }
        db.collection('members').document(str(member.id)).set(data)
        embed = discord.Embed(
            title='WELCOME',
            description=member.mention,
            colour=discord.Colour.blurple())

        embed.add_field(name=f'Welcome {member.display_name}', value='Hello')
        channel = self.client.get_channel(804347217330176002)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        pass
    # todo on leave delete users data from database


def setup(client):
    client.add_cog(Welcome(client=client))
