#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import discord
from source.game_settings import config, stream_challenge_config


def stream_challenge_location() -> str:
    return [
        discord.SelectOption(
            label=area,
            description=f"Points weighting: {value}",
        )
        for area, value in stream_challenge_config["StartingArea"].items()
    ]


def negative_trait_one(game_settings: dict) -> list:
    all_neg_traits_one = stream_challenge_config["NegativePropertiesValueOptionOne"]
    traits_option_one = []

    for key in all_neg_traits_one:
        if key in config["NegativePropertiesValueSubstitute"]:
            value = config["NegativePropertiesValueSubstitute"][key]
        elif key in config["NegativePropertiesValue"]:
            value = config["NegativePropertiesValue"][key]
        else:
            value = 0
        if value <= game_settings["challenge_points"]:
            traits_option_one.append(discord.SelectOption(label=key, description=f"Points weighting: {value}"))
    return traits_option_one


def stream_challenge_stage(option: str):
    option_one = [
        "Nichts auswählen",
        "Langsam-Leser",
        "Tollpatschig",
        "Magenleiden",
        "Agoraphobisch",
        "Gesunder Appetit",
        "Pechvogel",
        "Schwaches Immunsystem",
        "Feige",
        "Schwerhörig",
        "Hämatophobie",
        "Außer Form",
        "Langsam-Lerner",
        "Schlaf-gestört",
        "Untergewichtig",
    ]
    option_two = [

    ]
    option_three = [
        "Nichts auswählen",
        "Durstig",
        "Langsam-Heiler",
        "Fettleibig",
        "Dünnhäutig",
        "Raucher",
        "Gebrechlich",
        "Schlafmütze",
        "Auffällig",
    ]
    cleaned_options = []
    if option == "one":
        for element in option_one:
            if element == "Nichts auswählen":
                description = "Keiner dieser Möglichkeiten und zum nächsten Schritt."
            else:
                description = config["NegativePropertiesDescription"][element]
            cleaned_options.append(
                discord.SelectOption(
                    label=element,
                    description=description,
                )
            )
    elif option == "two":
        for element in option_two:
            if element == "Nichts auswählen":
                description = "Keiner dieser Möglichkeiten und zum nächsten Schritt."
            else:
                description = config["NegativePropertiesDescription"][element]
            cleaned_options.append(
                discord.SelectOption(
                    label=element,
                    description=description,
                )
            )

    return cleaned_options


def main() -> None:
    pass


if __name__ == "__main__":
    main()
