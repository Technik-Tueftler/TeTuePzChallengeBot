#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main functions for discord bot and general implementations for challenge generator.
"""
import os
import random
import asyncio
import uuid
from datetime import datetime
from collections import namedtuple
import yaml
import discord
from PIL import Image, ImageFont, ImageDraw
from source.constants import CONFIGURATION_FILE, GENERIC_IMAGE_PATH

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_CUSTOM_CHALLENGE_NAME = os.getenv("CHANNEL_CUSTOM_CHALLENGE_NAME")

with open(CONFIGURATION_FILE, encoding="utf-8") as f:
    config = yaml.safe_load(f)

LIST_OF_POSITIVE_TRAITS = list(config["PositivePropertiesValue"].keys())
LIST_OF_NEGATIVE_TRAITS = list(config["NegativePropertiesValue"].keys())

# Jobs are not included. Unemployed is always taken first, -8 Points.
FINISH_POINTS_FOR_EASY = 0
FINISH_POINTS_FOR_HARD = 5
FINISH_POINTS_FOR_IMPOSSIBLE = 10

TOTAL_NUMBER_OF_POSITIVE_TRAITS_EASY = 3
TOTAL_NUMBER_OF_POSITIVE_TRAITS_HARD = 2
TOTAL_NUMBER_OF_POSITIVE_TRAITS_IMPOSSIBLE = 1

substitution_dictionary = {
    ord("Ü"): "Ue",
    ord("Ä"): "Ae",
    ord("Ö"): "Oe",
    ord("ü"): "ue",
    ord("ä"): "ae",
    ord("ö"): "oe",
}

User = namedtuple("User", ["user_id", "user_name", "user_display_name"])


async def create_challenge_picture(game_settings: dict, user: User) -> str:
    """
    Function to create the pictures with the challenge based on game settings.
    :param game_settings: Game settings with map, traits and mission.
    :param user: User information
    :return: picture name and path
    """
    img = Image.open(GENERIC_IMAGE_PATH)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("../files/CrotahFreeVersionItalic-z8Ev3.ttf", 25)
    color = (255, 255, 255)
    # Ersteller
    pos = (10, 10)
    zeitstempel = datetime.now().strftime("%Y-%m-%d")
    text = (f"Einfache Challenge, {user.user_display_name.translate(substitution_dictionary)}, "
            f"{zeitstempel}")
    draw.text(pos, text, fill=color, font=font)
    # Location
    location = game_settings["location"]
    pos = (10, 100)
    text = f"Starte in: {location} als Arbeitsloser"
    draw.text(pos, text, fill=color, font=font)
    # Traits
    text = "Mit den positiven Traits:"
    pos = (10, 140)
    draw.text(pos, text, fill=color, font=font)
    pos_x = 350
    pos_y = 140
    for element in game_settings["positive_traits"]:
        pos = (pos_x, pos_y)
        draw.text(
            pos, element.translate(substitution_dictionary), fill=color, font=font
        )
        pos_y += 20
    # Mission
    mission = game_settings["mission"]
    pos = (10, pos_y + 50)
    draw.text(
        pos,
        f"Deine Mission: {mission.translate(substitution_dictionary)}",
        fill=color,
        font=font,
    )
    # Bildname und Pfad
    bildname_und_pfad = (
        "../created_challenges/"
        + zeitstempel
        + "_"
        + user.user_display_name.translate(substitution_dictionary).replace(" ", "")
        + "_"
        + str(uuid.uuid4()).replace("-", "")
        + ".png"
    )
    img.save(bildname_und_pfad)
    return bildname_und_pfad


async def create_custom_challenge(difficulty: str) -> dict:
    """
    Create a custom challenge for requester based on selected difficulty.
    :param difficulty: level of difficulty
    :return: game settings for challenge
    """
    game_settings = {
        "location": None,
        "negative_traits": [],
        "positive_traits": [],
        "mission": None,
    }
    start_trait_value = 8
    if difficulty == "Easy":
        start_location = random.choice(list(config["EasyStartLocation"].keys()))
        game_settings["location"] = start_location
        start_trait_value += config["EasyStartLocation"][start_location]
        game_settings["mission"] = random.choice(config["EasyMission"])
        time_out = 25
        while start_trait_value != 0:
            positive_trait = random.choice(LIST_OF_POSITIVE_TRAITS)
            if positive_trait in game_settings["positive_traits"]:
                continue
            if (
                start_trait_value + config["PositivePropertiesValue"][positive_trait]
            ) >= 0:
                start_trait_value += config["PositivePropertiesValue"][positive_trait]
                game_settings["positive_traits"].append(positive_trait)
            time_out -= 1
            if positive_trait == 0:
                break
            if time_out == 0:
                if start_trait_value == 1:
                    game_settings["positive_traits"].append("Geschwindigkeitsdämon")
                    break
                if start_trait_value == 2:
                    game_settings["positive_traits"].append("Gewandt")
                    break
                if start_trait_value == 3:
                    game_settings["positive_traits"].append("Geschwindigkeitsdämon")
                    game_settings["positive_traits"].append("Gewandt")
                    break
                print(f"Fehler bei {game_settings} mit Endwert: {start_trait_value}")
                break
    elif difficulty == "Hard":
        ...
    elif difficulty == "Impossible":
        ...
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
    if message.author == client.user:
        return
    if message.content.startswith("!Challenge"):
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
            if result[0] in ("Hard", "Impossible"):
                await message.channel.send(f"Es tut mir leid, den Schwierigkeitsgrad {result[0]} "
                                           f"kann ich noch nicht ausgeben.")
            else:
                task_create_custom_challenge = asyncio.create_task(
                    create_custom_challenge(result[0])
                )
                return_value = await task_create_custom_challenge
                picture_path = await create_challenge_picture(return_value, user)
                with open(picture_path, "rb") as file:
                    image = discord.File(file)
                    await message.channel.send(
                        f"{user.user_display_name} das ist deine Challenge:"
                    )
                    await message.channel.send(file=image)


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
