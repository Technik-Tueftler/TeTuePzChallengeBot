#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import uuid
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
from source.game_settings import User, substitution_dictionary, write_config, config
from source.constants import (
    GENERIC_IMAGE_PATH,
    MAX_CHARS_PRINT,
)


async def get_background_image() -> str:
    files = os.listdir(GENERIC_IMAGE_PATH)
    pictures = [element for element in files if element.endswith(".png")]
    if len(pictures) == 0:
        return None
    return GENERIC_IMAGE_PATH + random.choice(pictures)


async def sort_text_for_print(text: str) -> list:
    sort_strings = text.split(" ")
    temp_len = 0
    temp_text = ""
    return_strings = []
    for element in sort_strings:
        if (temp_len + len(element)) <= MAX_CHARS_PRINT:
            temp_text = " ".join([temp_text, element])
            temp_len += len(element)
        else:
            return_strings.append(temp_text)
            temp_len = len(element)
            temp_text = element
    return_strings.append(temp_text)
    return return_strings


async def herr_apfelring(game_settings: dict, user: User) -> str:
    """

    :param game_settings:
    :param user:
    :return:
    """
    background_image = await get_background_image()
    img = Image.open(background_image)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("../files/CrotahFreeVersionItalic-z8Ev3.ttf", 25)
    color = (255, 255, 255)
    x, y = 10, 10
    zeitstempel = datetime.now().strftime("%Y-%m-%d")
    challenge_id = config["challenge_id"] +1
    write_config("challenge_id", challenge_id)
    text = (
        f"#{challenge_id} "
        f"{user.user_display_name.translate(substitution_dictionary)}, "
        f"{zeitstempel}"
    )
    draw.text((x, y), text, fill=color, font=font)


async def create_challenge_picture(game_settings: dict, user: User) -> str:
    """
    Function to create the pictures with the challenge based on game settings.
    :param game_settings: Game settings with map, traits and mission.
    :param user: User information
    :return: picture name and path
    """
    background_image = await get_background_image()
    img = Image.open(background_image)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("../files/CrotahFreeVersionItalic-z8Ev3.ttf", 25)
    color = (255, 255, 255)
    # Ersteller
    pos = (10, 10)
    zeitstempel = datetime.now().strftime("%Y-%m-%d")
    challenge_difficulty = game_settings["difficulty"]
    text = (
        f"Challenge: {challenge_difficulty}, "
        f"{user.user_display_name.translate(substitution_dictionary)}, "
        f"{zeitstempel}"
    )
    draw.text(pos, text, fill=color, font=font)
    # Location and profession
    location = game_settings["location"]
    profession = game_settings["profession"].translate(substitution_dictionary)
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
    else:
        pos_y += 5
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
    pos_y += 50
    pos = (10, pos_y)
    draw.text(
        pos,
        "Deine Mission:",
        fill=color,
        font=font,
    )
    text_list = await sort_text_for_print(mission.translate(substitution_dictionary))
    pos = (200, pos_y)
    for element in text_list:
        draw.text(
            pos,
            element,
            fill=color,
            font=font,
        )
        pos_y += 20
        pos = (200, pos_y)
    # Einstellungen
    einstellungen = game_settings["settings"]
    text_list = await sort_text_for_print(
        einstellungen.translate(substitution_dictionary)
    )
    pos_y += 50
    pos = (10, pos_y)
    draw.text(
        pos,
        "Einstellungen:",
        fill=color,
        font=font,
    )
    pos = (200, pos_y)
    for element in text_list:
        draw.text(
            pos,
            element,
            fill=color,
            font=font,
        )
        pos_y += 20
        pos = (200, pos_y)
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


def main() -> None:
    pass


if __name__ == "__main__":
    main()
