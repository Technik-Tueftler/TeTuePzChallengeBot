#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random

import discord
import asyncio
import yaml

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

with open('../files/config.yml', encoding="utf-8") as f:
    config = yaml.safe_load(f)

LIST_OF_POSITIVE_TRAITS = list(config["PositivePropertiesValue"].keys())

# Jobs are not included. Unemployed is always taken first, -8 Points.
FINISH_POINTS_FOR_EASY = 0
FINISH_POINTS_FOR_HARD = 5
FINISH_POINTS_FOR_IMPOSSIBLE = 10

TOTAL_NUMBER_OF_POSITIVE_TRAITS_EASY = 3
TOTAL_NUMBER_OF_POSITIVE_TRAITS_HARD = 2
TOTAL_NUMBER_OF_POSITIVE_TRAITS_IMPOSSIBLE = 1


async def create_custom_challenge(difficulty: str) -> dict:
    game_settings = {"location": None, "negative_traits":[], "positive_traits":[], "mission": None}
    start_trait_value = -8
    if difficulty == "Easy":
        positive_traits = random.choices(LIST_OF_POSITIVE_TRAITS, k=TOTAL_NUMBER_OF_POSITIVE_TRAITS_EASY)
    elif difficulty == "Hard":
        ...
    elif difficulty == "Impossible":
        ...
    return game_settings


class CustomChallenge(discord.ui.View):
    def __init__(self, user_id, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.response = None

    async def on_timeout(self):
        self.children[0].disabled = True
        self.clear_items()

    @discord.ui.select(
        placeholder="What difficulty should the challenge have?",
        options=[
            discord.SelectOption(label="Easy", description="Easy challenge with random elements", emoji="😃"),
            discord.SelectOption(label="Hard", description="Difficult only for professionals", emoji="🤕"),
            discord.SelectOption(label="Impossible", description="Impossible to finish this challenge.", emoji="😰"),
        ],
        min_values=1,
        max_values=1
    )
    async def select_difficulty_level(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        if interaction.user.id != self.user_id:
            return
        self.response = select_item.values
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    print(message)
    if message.author == client.user:
        return
    if message.content.startswith('!Challenge'):
        view = CustomChallenge(user_id=message.author.id)
        await message.channel.send(view=view)
        await view.wait()
        result = view.response
        if result is not None:
            task_create_custom_challenge = asyncio.create_task(create_custom_challenge(result[0]))
            return_value = await task_create_custom_challenge
            await message.channel.send(f"{return_value}")



def main() -> None:
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
