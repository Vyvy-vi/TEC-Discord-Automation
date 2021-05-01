from discord import Embed
from discord.ext import commands
from discord.ext.commands import Context

HelpDesc = "This bot's prefix is `TEC!`\n\
Use `TEC!help category` for more info on a category\n\
Use `TEC!help command` for more info on a command\n\
For any problems, open an issue on the [Github Repo](https://github.com/Vyvy-vi/TEC-Discord-Automation/issues)"

class CustomHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        return "`%s%s %s`" % (self.clean_prefix, command.qualified_name, command.signature)
    # TEC!help
    async def send_bot_help(self, mapping):
        embed = Embed(title="Help Categories",
                      description=HelpDesc,
                      colour=0xdefb48)
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value=cog.description + "\n" + "\n".join(command_signatures), inline=True)
        embed.set_footer(text='For any more info, dm @Vyvy-vi#5040')
        await self.context.send(embed=embed)

   # TEC!help <command>
    async def send_command_help(self, command):
        await self.context.send("This is help command")

   # TEC!help <group>
    async def send_group_help(self, group):
        await self.context.send("This is help group")

   # TEC!help <cog>
    async def send_cog_help(self, cog):
        await self.context.send("This is help cog")

class Helpers(commands.Cog):
    """Help command and some other helper commands"""
    def __init__(self, bot):
        self._default_help_command = bot.help_command
        bot.help_command = CustomHelp()
        bot.help_command.cog = self
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')


def setup(bot):
    bot.add_cog(Helpers(bot))
