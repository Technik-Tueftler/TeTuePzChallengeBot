#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random

import discord
import asyncio
import yaml

from PIL import Image, ImageFont, ImageDraw

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

with open('../files/config.yml', encoding="utf-8") as f:
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


async def create_Challenge_picture(game_settings: dict) -> None:
    img = Image.open("../files/post_apocalypse_city.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("../files/CrotahFreeVersionItalic-z8Ev3.ttf", 18)
    pos = (0, 0)
    color = (255, 255, 255)
    draw.text(pos, "TEXT", fill=color, font=font)
    img.save("../created_challenges/test.png")


async def create_custom_challenge(difficulty: str) -> dict:
    game_settings = {"location": None, "negative_traits": [], "positive_traits": [],
                     "mission": None}
    start_trait_value = 8
    if difficulty == "Easy":
        start_location = random.choice(list(config["EasyStartLocation"].keys()))
        game_settings["location"] = start_location
        start_trait_value += config["EasyStartLocation"][start_location]
        game_settings["mission"] = random.choice(config["EasyMission"])
        time_out = 25
        while start_trait_value != 0:
            positive_trait = random.choice(LIST_OF_POSITIVE_TRAITS)
            print(positive_trait)
            if positive_trait in game_settings["positive_traits"]:
                continue
            if (start_trait_value + config["PositivePropertiesValue"][positive_trait]) >= 0:
                start_trait_value += config["PositivePropertiesValue"][positive_trait]
                game_settings["positive_traits"].append(positive_trait)
            time_out -= 1
            if positive_trait == 0:
                break
            if time_out == 0:
                if start_trait_value == 1:
                    game_settings["positive_traits"].append("Geschwindigkeitsdämon")
                    break
                elif start_trait_value == 2:
                    game_settings["positive_traits"].append("Gewandt")
                    break
                elif start_trait_value == 3:
                    game_settings["positive_traits"].append("Geschwindigkeitsdämon")
                    game_settings["positive_traits"].append("Gewandt")
                    break
                else:
                    print(f"Fehler bei {game_settings} mit Endwert: {start_trait_value}")
                    break
    elif difficulty == "Hard":
        ...
    elif difficulty == "Impossible":
        ...
    return game_settings


class CustomChallenge(discord.ui.View):
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
            discord.SelectOption(label="Easy", description="Easy challenge with random elements",
                                 emoji="😃"),
            discord.SelectOption(label="Hard", description="Difficult only for professionals",
                                 emoji="🤕"),
            discord.SelectOption(label="Impossible",
                                 description="Impossible to finish this challenge.", emoji="😰"),
        ],
        min_values=1,
        max_values=1
    )
    async def select_difficulty_level(self, interaction: discord.Interaction,
                                      select_item: discord.ui.Select):
        if interaction.user.id != self.user_id:
            return
        self.response = select_item.values
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()


class User:
    def __init__(self, user_id, user_name, user_display_name):
        self.user_id = user_id
        self.user_name = user_name
        self.user_display_name = user_display_name


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    print(message)
    if message.author == client.user:
        return
    if message.content.startswith('!Challenge'):
        user = User(user_id=message.author.id, user_name=message.author.name, user_display_name=message.author.global_name)
        view = CustomChallenge(user=user)
        await message.channel.send(view=view)
        await view.wait()
        result = view.response
        if result is not None:
            print(result)
            if result[0] in ("Hard", "Impossible"):
                await message.channel.send(f"Es tut mir leid, den Schwierigkeitsgrad {result[0]} kann ich noch nicht ausgeben.")
            else:
                task_create_custom_challenge = asyncio.create_task(create_custom_challenge(result[0]))
                return_value = await task_create_custom_challenge
                await message.channel.send(f"{return_value}")


def main() -> None:
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
