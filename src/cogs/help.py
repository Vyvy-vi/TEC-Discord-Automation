from discord import Embed, Color
from discord.ext import commands
from discord.ext.commands import Context

HelpDesc = "This bot's prefix is `TEC!`\n\
Use `TEC!help category` for more info on a category\n\
Use `TEC!help command` for more info on a command\n\
For any problems, open an issue on the [Github Repo](https://github.com/Vyvy-vi/TEC-Discord-Automation/issues)"

class CustomHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        cmd = "%s%s %s" % (self.clean_prefix, command.qualified_name, command.signature)
        return f"`{cmd.strip()}`"

    def get_help_text(self, command):
        cmd = self.get_command_signature(command)
        return cmd, command.short_doc

    # TEC!help
    async def send_bot_help(self, mapping):
        embed = Embed(title="Help Categories",
                      description=HelpDesc,
                      colour=0xdefb48)
        for cog, cmds in mapping.items():
            filtered = await self.filter_commands(cmds, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value=cog.description + "\n" + "\n".join(command_signatures), inline=True)
        embed.set_footer(text='For any more info, dm @Vyvy-vi#5040')
        await self.context.send(embed=embed)

   # TEC!help <command>
    async def send_command_help(self, command):
        embed = Embed(title=self.get_command_signature(command),
                      color=0xdefb48)
        embed.add_field(name=f"Help for `{command.name}`",
                        value=command.short_doc)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)
        embed.set_footer(text='For any more info, dm @Vyvy-vi#5040')
        await self.context.send(embed=embed)

   # TEC!help <group>
    async def send_group_help(self, group):
        embed = Embed(title=f"Help for Category: `{cog_name}`",
                      description=HelpDesic + '\nThat group doesn\'t exist',
                      colour=Color.Red())
        await self.context.send(embed=embed)

   # TEC!help <cog>
    async def send_cog_help(self, cog):
        cog_name = getattr(cog, "qualified_name", "No Category")
        embed = Embed(title=f"Help for Category: `{cog_name}`",
                      description="Use TEC!help command for more info on a command"
                      + f'\n\n**{cog.description}**',
                      colour=0xdefb48)
        commands = [self.get_help_text(c) for c in await self.filter_commands(cog.walk_commands(), sort=True)]
        if commands:
            for cmd in commands:
                embed.add_field(name=cmd[0], value=cog.description + cmd[1], inline=False)
        embed.set_footer(text='For any more info, dm @Vyvy-vi#5040')
        await self.context.send(embed=embed)

    # Error Handling
    async def send_error_message(self, error):
        embed = Embed(title="Error",
                      description=error,
                      color=Color.red())
        await self.context.send(embed=embed)



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
