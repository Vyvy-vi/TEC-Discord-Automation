from discord import Embed, Color, Member
from discord.ext import commands
from discord.ext.commands import Context

from datetime import datetime
from typing import Union, Optional


def UserEmbed(user):
    embed = Embed(
      title="Member Info",
      description=f"Here's what I could find  on {user.mention}",
      color=user.color.value
    )
    fields = [
        {"name": "Name", "value": user, "inline": True },
        {"name": "ID", "value": user.id, "inline": True },
        {"name": "Highest Role", "value": user.top_role.mention, "inline": True },
        {"name": "Joined", "value": f"{(datetime.now() - user.joined_at).days} days ago...", "inline": True},
        {"name": "Account Created", "value": f"{(datetime.now() - user.created_at).days} days ago...", "inline": True}]
    for field in fields:
        embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
    embed.set_thumbnail(url=user.avatar_url)
    return embed

class IceBreakers(commands.Cog):
    """Commands for running icebreakers"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['profile'])
    @commands.guild_only()
    async def user(self, ctx: Context, *, member: Member = None):
        """Pulls up some user info"""
        if not member:
            member = ctx.message.author
        await ctx.send(embed=UserEmbed(member))

def setup(bot):
    bot.add_cog(IceBreakers(bot))
