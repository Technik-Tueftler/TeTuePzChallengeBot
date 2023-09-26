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
from source.constants import (
    CONFIGURATION_FILE,
    GENERIC_IMAGE_PATH,
    OFFSET_TRAIT_VALUE,
    END_THR_TRAIT_VALUE,
    TRAIT_DIFFERENCE_THR,
    TRAIT_DIFFERENCE_MIN_THR
)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", None)
CHANNEL_CUSTOM_CHALLENGE_NAME = os.getenv("CHANNEL_CUSTOM_CHALLENGE_NAME", None)

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
    text = (
        f"Einfache Challenge, {user.user_display_name.translate(substitution_dictionary)}, "
        f"{zeitstempel}"
    )
    draw.text(pos, text, fill=color, font=font)
    # Location
    location = game_settings["location"]
    profession = game_settings["profession"]
    pos = (10, 100)
    text = f"Starte in: {location} als {profession}"
    draw.text(pos, text, fill=color, font=font)
    # positiv Traits
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
    # negativ Traits
    if len(game_settings["positive_traits"]) == 0:
        pos_y += 25
    text = "Mit den negativen Traits:"
    pos = (10, pos_y)
    draw.text(pos, text, fill=color, font=font)
    pos_x = 350
    for element in game_settings["negative_traits"]:
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


def get_location(difficulty: str) -> list[str, int]:
    location_settings = ["Location", 0]
    if difficulty == "Easy":
        location_settings[0] = random.choice(list(config["EasyStartLocation"].keys()))
        location_settings[1] = config["EasyStartLocation"][location_settings[0]]
    elif difficulty == "Hard":
        location_settings[0] = random.choice(list(config["HardStartLocation"].keys()))
        location_settings[1] = config["HardStartLocation"][location_settings[0]]
    elif difficulty == "Impossible":
        location_settings[0] = random.choice(
            list(config["ImpossibleStartLocation"].keys())
        )
        location_settings[1] = config["ImpossibleStartLocation"][location_settings[0]]
    return location_settings


def get_profession(difficulty: str) -> list[str, int]:
    profession_settings = ["Profession", 0]
    if difficulty == "Easy":
        profession_settings[0] = random.choice(list(config["EasyProfessions"].keys()))
        profession_settings[1] = config["EasyProfessions"][profession_settings[0]]
    elif difficulty == "Hard":
        profession_settings[0] = random.choice(list(config["HardProfessions"].keys()))
        profession_settings[1] = config["HardProfessions"][profession_settings[0]]
    elif difficulty == "Impossible":
        profession_settings[0] = random.choice(
            list(config["ImpossibleProfessions"].keys())
        )
        profession_settings[1] = config["ImpossibleProfessions"][profession_settings[0]]
    return profession_settings


def get_mission(difficulty: str) -> list[str, int]:
    mission_settings = ["Mission", 0]
    if difficulty == "Easy":
        mission_settings[0] = random.choice(config["EasyMission"])
    elif difficulty == "Hard":
        mission_settings[0] = random.choice(config["HardMission"])
    elif difficulty == "Impossible":
        mission_settings[0] = random.choice(config["ImpossibleMission"])
    return mission_settings


def get_end_trait_value(difficulty: str) -> int:
    return config["EndTraitValue"][difficulty]


def finish_trait_value(trait_value: int, game_settings: dict) -> None:
    if trait_value == -1:
        game_settings["positive_traits"].append("Geschwindigkeitsdämon")
        return
    if trait_value == -2:
        game_settings["positive_traits"].append("Gewandt")
        return
    if trait_value == -3:
        game_settings["positive_traits"].append("Geschwindigkeitsdämon")
        game_settings["positive_traits"].append("Gewandt")
        return
    if trait_value == 1:
        game_settings["positive_traits"].append("Sonntagsfahrer")
        return
    if trait_value == 2:
        game_settings["positive_traits"].append("Feige")
        return
    if trait_value == 3:
        game_settings["positive_traits"].append("Sonntagsfahrer")
        game_settings["positive_traits"].append("Feige")
        return


async def create_easy_custom_challenge2(
        trait_value: int, end_trait_value: int, game_settings: dict
) -> None:
    time_out = 25
    min_run_trait_loops = game_settings["min_traits"]
    while trait_value != end_trait_value:
        print(
            f"Trait-Value: {trait_value} timeout: {time_out} min loop: {min_run_trait_loops}"
        )
        if trait_value > end_trait_value:
            if trait_value - end_trait_value <= END_THR_TRAIT_VALUE:
                finish_trait_value(trait_value - end_trait_value, game_settings)
                break
            positive_trait = random.choice(LIST_OF_POSITIVE_TRAITS)
            print(f"Positiver Trait: {positive_trait}")
            if positive_trait in game_settings["positive_traits"]:
                time_out -= 1
                continue
            if min_run_trait_loops > 0:
                trait_value += config["PositivePropertiesValue"][positive_trait]
                game_settings["positive_traits"].append(positive_trait)
                min_run_trait_loops -= 1
            else:
                if (
                        trait_value + config["PositivePropertiesValue"][positive_trait]
                ) < end_trait_value:
                    time_out -= 1
                    continue
                else:
                    trait_value += config["PositivePropertiesValue"][positive_trait]
                    game_settings["positive_traits"].append(positive_trait)
                    min_run_trait_loops -= 1
            print(game_settings)
        elif trait_value < end_trait_value:
            if trait_value >= 0:
                if end_trait_value - trait_value <= END_THR_TRAIT_VALUE:
                    finish_trait_value(-(end_trait_value - trait_value), game_settings)
                    break
            negative_trait = random.choice(LIST_OF_NEGATIVE_TRAITS)
            print(f"Negativer Trait: {negative_trait}")
            if negative_trait in game_settings["negative_traits"]:
                time_out -= 1
                continue
            if min_run_trait_loops > 0:
                trait_value += config["NegativePropertiesValue"][negative_trait]
                game_settings["negative_traits"].append(negative_trait)
                min_run_trait_loops -= 1
            else:
                if (
                        trait_value - config["NegativePropertiesValue"][negative_trait]
                ) < end_trait_value:
                    time_out -= 1
                    continue
                else:
                    trait_value += config["NegativePropertiesValue"][negative_trait]
                    game_settings["negative_traits"].append(negative_trait)
                    min_run_trait_loops -= 1
            print(game_settings)
        else:
            print("Fehler")
            break


def check_limit_value_reached(trait_value: int, end_trait_value: int) -> bool:
    sum_trait_value = end_trait_value - trait_value
    if abs(sum_trait_value) <= END_THR_TRAIT_VALUE:
        return True
    else:
        return False


async def check_trait_possible(trait: str, game_settings: dict) -> bool:
    if not trait in config:
        return True
    return not any(True for element in config[trait] if element in game_settings["positive_traits"])


async def check_difference_small_enough(trait: str, game_settings: dict) -> bool:
    trait_difference_thr = game_settings["trait_difference_thr"]
    if trait in config["NegativePropertiesValue"]:
        if abs(config["NegativePropertiesValue"][trait]) <= trait_difference_thr:
            if trait_difference_thr > TRAIT_DIFFERENCE_MIN_THR:
                game_settings["trait_difference_thr"] = trait_difference_thr // 2
            return True
        return False
    if trait in config["PositivePropertiesValue"]:
        if abs(config["PositivePropertiesValue"][trait]) <= trait_difference_thr:
            game_settings["trait_difference_thr"] = trait_difference_thr // 2
            if trait_difference_thr > TRAIT_DIFFERENCE_MIN_THR:
                game_settings["trait_difference_thr"] = trait_difference_thr // 2
            return True
        return False


async def add_positive_trait() -> None:
    ...


async def create_easy_custom_challenge(
        trait_value: int, end_trait_value: int, game_settings: dict
) -> None:
    time_out = 25
    min_run_trait_loops = game_settings["min_traits"]

    while (trait_value != end_trait_value) or (min_run_trait_loops <= 0):
        print(
            f"Trait-Value: {trait_value} timeout: {time_out} min loop: {min_run_trait_loops}"
        )
        if trait_value < end_trait_value:
            # negativen trait hinzufügen
            if check_limit_value_reached(trait_value, end_trait_value) and (min_run_trait_loops <= 0):
                finish_trait_value(end_trait_value - trait_value, game_settings)
                break
            negative_trait = random.choice(LIST_OF_NEGATIVE_TRAITS)
            print(f"Negativer Trait: {negative_trait}")
            if negative_trait in game_settings["negative_traits"]:
                time_out -= 1
                continue
            if not await check_trait_possible(negative_trait, game_settings):
                time_out -= 1
                continue
            if not await check_difference_small_enough(negative_trait, game_settings):
                time_out -= 1
                continue
            trait_value += config["NegativePropertiesValue"][negative_trait]
            game_settings["negative_traits"].append(negative_trait)
            min_run_trait_loops -= 1
        elif trait_value > end_trait_value:
            # positiven trait hinzufügen
            if check_limit_value_reached(trait_value, end_trait_value) and (min_run_trait_loops <= 0):
                finish_trait_value(end_trait_value - trait_value, game_settings)
                break
            positive_trait = random.choice(LIST_OF_POSITIVE_TRAITS)
            print(f"Positiver Trait: {positive_trait}")
            if positive_trait in game_settings["positive_traits"]:
                time_out -= 1
                continue
            if not await check_trait_possible(positive_trait, game_settings):
                time_out -= 1
                continue
            if not await check_difference_small_enough(positive_trait, game_settings):
                time_out -= 1
                continue
            trait_value += config["PositivePropertiesValue"][positive_trait]
            game_settings["positive_traits"].append(positive_trait)
            min_run_trait_loops -= 1
        else:
            if check_limit_value_reached(trait_value, end_trait_value) and (min_run_trait_loops <= 0):
                finish_trait_value(end_trait_value - trait_value, game_settings)
                break
            positive_trait = random.choice(LIST_OF_POSITIVE_TRAITS)
            print(f"Positiver Trait: {positive_trait}")
            if positive_trait in game_settings["positive_traits"]:
                time_out -= 1
                continue
            if not await check_trait_possible(positive_trait, game_settings):
                time_out -= 1
                continue
            if not await check_difference_small_enough(positive_trait, game_settings):
                time_out -= 1
                continue
            trait_value += config["PositivePropertiesValue"][positive_trait]
            game_settings["positive_traits"].append(positive_trait)
            min_run_trait_loops -= 1


async def create_custom_challenge(difficulty: str) -> dict:
    """
    Create a custom challenge for requester based on selected difficulty.
    :param difficulty: level of difficulty
    :return: game settings for challenge
    """
    game_settings = {
        "location": None,
        "profession": None,
        "negative_traits": [],
        "positive_traits": [],
        "mission": None,
        "min_traits": config["MinTraits"][difficulty],
        "settings": None,
        "trait_difference_thr": TRAIT_DIFFERENCE_THR
    }
    game_settings["location"], location_value = get_location(difficulty)
    game_settings["profession"], profession_value = get_profession(difficulty)
    game_settings["mission"], _ = get_mission(difficulty)
    print(game_settings)
    trait_value = profession_value
    end_trait_value = (
            get_end_trait_value(difficulty) + location_value + OFFSET_TRAIT_VALUE
    )
    if difficulty == "Easy":
        await create_easy_custom_challenge(trait_value, end_trait_value, game_settings)
    elif difficulty == "Hard":
        await create_easy_custom_challenge(trait_value, end_trait_value, game_settings)
    elif difficulty == "Impossible":
        await create_easy_custom_challenge(trait_value, end_trait_value, game_settings)
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
