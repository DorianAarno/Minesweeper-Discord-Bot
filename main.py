import os

import disnake
from disnake.ext import commands

from config import TOKEN


intents = disnake.Intents.default()

bot = commands.InteractionBot(intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} is connected.")


# Load all cogs
for filename in os.listdir("./minesweeper"):
    if filename.endswith(".py"):
        bot.load_extension(f"minesweeper.{filename[:-3]}")

# Run the client
bot.run(TOKEN)
