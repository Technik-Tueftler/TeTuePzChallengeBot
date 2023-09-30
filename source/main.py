#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main functions for discord bot and general implementations for challenge generator.
"""
import os
import asyncio
import discord
from source.game_settings import (
    config,
    User,
    get_location,
    get_profession,
    get_mission,
    get_settings,
    get_end_trait_value,
)
from source.custom_challenge import create_custom_challenge
from source.stream_challenge import stream_challenge_stage_one
from source.picture import create_challenge_picture
from source.constants import (
    OFFSET_TRAIT_VALUE,
    TRAIT_DIFFERENCE_THR,
)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", None)
CHANNEL_CUSTOM_CHALLENGE_NAME = os.getenv("CHANNEL_CUSTOM_CHALLENGE_NAME", None)


async def custom_challenge_handler(difficulty: str) -> dict:
    """
    Create a custom challenge for requester based on selected difficulty.
    :param difficulty: level of difficulty
    :return: game settings for challenge
    """
    game_settings = {
        "successful_generated": True,
        "location": None,
        "profession": None,
        "difficulty": difficulty,
        "negative_traits": [],
        "positive_traits": [],
        "mission": None,
        "min_traits": config["MinTraits"][difficulty],
        "settings": None,
        "trait_difference_thr": TRAIT_DIFFERENCE_THR,
    }
    game_settings["location"], location_value = get_location(difficulty)
    game_settings["profession"], profession_value = get_profession(difficulty)
    game_settings["mission"], _ = get_mission(difficulty)
    game_settings["settings"] = get_settings(difficulty)
    print(game_settings)
    trait_value = profession_value
    end_trait_value = (
        get_end_trait_value(difficulty) + location_value + OFFSET_TRAIT_VALUE
    )
    await create_custom_challenge(trait_value, end_trait_value, game_settings)
    return game_settings


class CustomChallenge(discord.ui.View):
    """
    Class to create dropdown menu for selecting the difficulty level of the
    custom challenge.
    """

    def __init__(self, user, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user.user_id
        self.response = None

    async def on_timeout(self):
        self.children[0].disabled = True
        self.clear_items()

    @discord.ui.select(
        placeholder="What difficulty should the challenge have?",
        options=[
            discord.SelectOption(
                label="Easy",
                description="Easy challenge with random elements",
                emoji="😃",
            ),
            discord.SelectOption(
                label="Hard", description="Difficult only for professionals", emoji="🤕"
            ),
            discord.SelectOption(
                label="Impossible",
                description="Impossible to finish this challenge.",
                emoji="😰",
            ),
        ],
        min_values=1,
        max_values=1,
    )
    async def select_difficulty_level(
        self, interaction: discord.Interaction, select_item: discord.ui.Select
    ) -> None:
        """
        Callback function if user interact with the dropdown menu.
        :param interaction: Interaction from requester
        :param select_item: Selected items by the user
        :return: None
        """
        if interaction.user.id != self.user_id:
            return
        self.response = select_item.values
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()


class StreamChallengeStageOne(discord.ui.View):
    def __init__(self, user, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user.user_id
        self.response = None

    async def on_timeout(self):
        self.children[0].disabled = True
        self.clear_items()

    @discord.ui.select(
        placeholder="What difficulty should the challenge have?",
        options=stream_challenge_stage_one(),
        min_values=0,
        max_values=15,
    )
    async def select_difficulty_level(
        self, interaction: discord.Interaction, select_item: discord.ui.Select
    ) -> None:
        if interaction.user.id != self.user_id:
            return
        self.response = select_item.values
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()


@client.event
async def on_ready() -> None:
    """
    Function to be called when the bot is ready.
    :return: None
    """
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message) -> None:
    """
    Function to be called when user sends a message.
    :param message: Message object
    :return: None
    """
    print(message)
    print(message.content)
    if message.author == client.user:
        return
    clean_message = message.content.lower()
    if clean_message.startswith("!challenge"):
        if message.channel.name != CHANNEL_CUSTOM_CHALLENGE_NAME:
            return
        user = User(
            user_id=message.author.id,
            user_name=message.author.name,
            user_display_name=message.author.global_name,
        )
        view = CustomChallenge(user=user)
        await message.channel.send(view=view)
        await view.wait()
        result = view.response
        if result is not None:
            task_create_custom_challenge = asyncio.create_task(
                custom_challenge_handler(result[0])
            )
            game_settings = await task_create_custom_challenge
            if game_settings["successful_generated"]:
                picture_path = await create_challenge_picture(game_settings, user)
                with open(picture_path, "rb") as file:
                    image = discord.File(file)
                    await message.channel.send(
                        f"{user.user_display_name} das ist deine Challenge:"
                    )
                    await message.channel.send(file=image)
            else:
                await message.channel.send(
                    f"{user.user_display_name}, es ist ein Fehler aufgetreten. Bitte erstelle "
                    f"nochmal eine Challenge. Ein Fehler-Report ist gespeichert."
                )
    # if clean_message.startswith("!streamchallenge"):
    #     if message.channel.name != CHANNEL_CUSTOM_CHALLENGE_NAME:
    #         return
    #     user = User(
    #         user_id=message.author.id,
    #         user_name=message.author.name,
    #         user_display_name=message.author.global_name,
    #     )
    #     view = StreamChallengeStageOne(user=user)
    #     await message.channel.send(view=view)
    #     await view.wait()
    #     result = view.response
    #     print(result)


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
