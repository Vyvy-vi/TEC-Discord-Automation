import re
import csv

from asyncio import sleep
from datetime import datetime, timedelta

from discord import utils, File
from discord.ext import commands
from discord.ext.commands import Context
from discord.errors import Forbidden, HTTPException


def get_answers(text, is_old = False):
    text = text.split('\n\n')
    if (is_old):
        try:
            if len(text) > 2:
                if '**2' in text[1]:
                    answers = [line.strip().split('\n')[1] for line in text[:2]]
                    answers[1] += ' '.join(text[2:])
                else:
                    answers = [
                        text[0].split('\n')[1] + text[1],
                        text[2].split('\n')[1]
                    ]
            else:
                answers = [line.strip().split('\n')[1] for line in text[:2]]
        except IndexError:
            print("aaa")
            print([text])
    else:
        answers = [line.strip().split('\n')[1] for line in text]
    for i in range(len(answers)):
        answers[i].replace('\n', ' ')
    return answers


class OnboardingDataScrape(commands.Cog):
    """Commands for scraping onboarding-data"""
    def __init__(self, bot):
        self.bot = bot

    def in_bot_setup_channel(ctx):
        return ctx.channel.id == 810180622017757185

    @commands.command()
    @commands.guild_only()
    @commands.check(in_bot_setup_channel)
    @commands.has_any_role('Admin', 873234054449881198)
    @commands.max_concurrency(2)
    @commands.cooldown(1, 20, commands.BucketType.member)
    async def get_onboarding_data(self, ctx: Context, after: str = None):
        await ctx.send(f'Fetching Onboarding data from {ctx.guild.name}...')

        if after:
            dates = [int(char) for char in after.split('-')]
            after = datetime(dates[2], dates[1], dates[0])
        else:
            # data from 7 days ago from now
            after = datetime.now() - timedelta(days=7)

        old_data = [[
            "username",
            "How would you like to be addressed?",
            "Where did you hear about the TEC? What brings you here?",
            "datetime"
        ]]

        new_data = [[
            "username",
            "How would you like to be addressed? - What name(s) and pronouns would you like us to use?",
            "Why did you come to the TEC?",
            "How familiar are you with web3?",
            "How did you find out about the TEC?",
            "Which timezone are you in?",
            "datetime"
        ]]

        channel = ctx.guild.get_channel(887679444867756032)
        msgs = await channel.history(after=after, limit=None).flatten()
        for msg in msgs:
            for embed in msg.embeds:
                if msg.created_at > datetime.fromtimestamp(1638416654):
                    new_data.append(
                        [embed.title[:-19]] + get_answers(embed.description) + [
                            msg.created_at.strftime("%d/%m/%Y - %I:%M: %p")
                        ]
                    )
                else:
                    old_data.append(
                        [embed.title[:-19]] + get_answers(embed.description, True) + [
                            msg.created_at.strftime("%d/%m/%Y - %I:%M %p")
                        ]
                    )

        with open(f"old_onboarding_data_{ctx.guild.id}.csv", "w") as f:
            try:
                writer = csv.writer(f)
                print("Writing Data...")
                writer.writerows(old_data)
            except Exception as e:
                print(f"Error in Writing Data: {e}")

        with open(f"new_onboarding_data_{ctx.guild.id}.csv", 'w') as f:
            try:
                writer = csv.writer(f)
                print('Writing Data...')
                writer.writerows(new_data)
            except Exception as e:
                print(f"Error in Writing Data: {e}")

            print("Data successfully written!")

        await ctx.send(
            f"Here's all of the Data since {(datetime.now() - after).days} days ago",
            files=[
                File(f"old_onboarding_data_{ctx.guild.id}.csv", f'OLD DATA {ctx.guild.name}.csv'),
                File(f'new_onboarding_data_{ctx.guild.id}.csv', f'NEW DATA {ctx.guild.name}.csv')]
        )

    @get_onboarding_data.error
    async def get_data_error(self, ctx: Context, error):
        if isinstance(error.original, HTTPException):
            await ctx.send("An error occured, the date format might be wrong.")
        print(f"An error occured\n{error}")

def setup(bot):
    bot.add_cog(OnboardingDataScrape(bot))
