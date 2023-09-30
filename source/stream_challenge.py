#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import discord
from source.game_settings import config


def stream_challenge_stage_one():
    option_one = ["Nichts auswählen", "Langsam-Leser", "Tollpatschig",
                  "Magenleiden", "Agoraphobisch", "Gesunder Appetit",
                  "Pechvogel", "Schwaches Immunsystem", "Feige",
                  "Schwerhörig","Hämatophobie", "Außer Form",
                  "Langsam-Lerner", "Schlaf-gestört", "Untergewichtig"]
    option_two = ["Nichts auswählen", "Analphabet", "Klaustrophobisch",
                  "Taub", "Couch-Kartoffel", "Schwach",
                  "Messie", "Übergewichtig", "Schusslig",
                  "Pazifist", "Asthmatiker", "Sonntagsfahrer"]
    option_three = ["Nichts auswählen", "Durstig", "Langsam-Heiler",
                    "Fettleibig", "Dünnhäutig", "Raucher",
                    "Gebrechlich", "Schlafmütze", "Auffällig"]
    cleaned_options = []
    for element in option_one:
        if element == "Nichts auswählen":
            description = "Keiner dieser Möglichkeiten und zum nächsten Schritt."
        else:
            description = config["NegativePropertiesDescription"][element]
        cleaned_options.append(discord.SelectOption(
        label=element,
        description=description,
    ))
    return cleaned_options


def main() -> None:
    pass


if __name__ == "__main__":
    main()
