#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package to provide all necessary information and functions for the game settings
"""
import random
from collections import namedtuple
import yaml
from source.constants import (
    CONFIG_FILE,
    CONFIG_CUSTOM_CHALLENGE_FILE,
    CONFIG_STREAM_CHALLENGE_FILE,
    USER_INFO_MESSAGE_1,
    USER_INFO_MESSAGE_2,
    USER_INFO_MESSAGE_APPROVAL_1,
    USER_INFO_MESSAGE_APPROVAL_2,
    USER_INFO_MESSAGE_APPROVAL_3,
    USER_INFO_MESSAGE_APPROVAL_4,
    USER_INFO_MESSAGE_APPROVAL_5,
    DEFAULT_SKIP_SELECTION,
)

with open(CONFIG_FILE, encoding="utf-8") as f:
    config = yaml.safe_load(f)

with open(CONFIG_CUSTOM_CHALLENGE_FILE, encoding="utf-8") as f:
    custom_config = yaml.safe_load(f)

with open(CONFIG_STREAM_CHALLENGE_FILE, encoding="utf-8") as f:
    stream_challenge_config = yaml.safe_load(f)

LIST_OF_POSITIVE_TRAITS = list(custom_config["PositivePropertiesValue"].keys())
LIST_OF_NEGATIVE_TRAITS = list(custom_config["NegativePropertiesValue"].keys())

substitution_dictionary = {
    ord("Ü"): "Ue",
    ord("Ä"): "Ae",
    ord("Ö"): "Oe",
    ord("ü"): "ue",
    ord("ä"): "ae",
    ord("ö"): "oe",
    ord("ß"): "ss",
}

User = namedtuple("User", ["user_id", "user_name", "user_display_name"])


def write_config(key: str, value) -> None:
    """
    Function to write statistic data in a configuration file
    :param key: Key of the date field
    :param value: Value of the date field
    :return: None
    """
    config[key] = value
    with open(CONFIG_FILE, "w", encoding="utf-8") as datei:
        yaml.dump(config, datei, default_flow_style=False)


def get_location(difficulty: str) -> list[str, int]:
    """
    Get the location for the challenge based on difficulty level
    :param difficulty: difficulty level
    :return: List of the location with the trait value
    """
    location_settings = ["Location", 0]
    if difficulty == "Easy":
        location_settings[0] = random.choice(
            list(custom_config["EasyStartLocation"].keys())
        )
        location_settings[1] = custom_config["EasyStartLocation"][location_settings[0]]
    elif difficulty == "Hard":
        location_settings[0] = random.choice(
            list(custom_config["HardStartLocation"].keys())
        )
        location_settings[1] = custom_config["HardStartLocation"][location_settings[0]]
    elif difficulty == "Impossible":
        location_settings[0] = random.choice(
            list(custom_config["ImpossibleStartLocation"].keys())
        )
        location_settings[1] = custom_config["ImpossibleStartLocation"][
            location_settings[0]
        ]
    return location_settings


def get_profession(difficulty: str) -> list[str, int]:
    """
    Get the profession for the challenge based on difficulty level
    :param difficulty: difficulty level
    :return: List of the profession with the trait value
    """
    profession_settings = ["Profession", 0]
    if difficulty == "Easy":
        profession_settings[0] = random.choice(
            list(custom_config["EasyProfessions"].keys())
        )
        profession_settings[1] = custom_config["EasyProfessions"][
            profession_settings[0]
        ]
    elif difficulty == "Hard":
        profession_settings[0] = random.choice(
            list(custom_config["HardProfessions"].keys())
        )
        profession_settings[1] = custom_config["HardProfessions"][
            profession_settings[0]
        ]
    elif difficulty == "Impossible":
        profession_settings[0] = random.choice(
            list(custom_config["ImpossibleProfessions"].keys())
        )
        profession_settings[1] = custom_config["ImpossibleProfessions"][
            profession_settings[0]
        ]
    return profession_settings


def get_mission(difficulty: str) -> list[str, int]:
    """
    Get the mission for the challenge based on difficulty level
    :param difficulty: difficulty level
    :return: List of the mission with the trait value
    """
    mission_settings = ["Mission", 0]
    if difficulty == "Easy":
        mission_settings[0] = random.choice(custom_config["EasyMission"])
    elif difficulty == "Hard":
        mission_settings[0] = random.choice(custom_config["HardMission"])
    elif difficulty == "Impossible":
        mission_settings[0] = random.choice(custom_config["ImpossibleMission"])
    return mission_settings


def get_settings(difficulty: str) -> str:
    """
    Get the settings for the challenge based on difficulty level
    :param difficulty: difficulty level
    :return: Settings as string
    """
    if difficulty == "Easy":
        return random.choice(custom_config["EasySettings"])
    if difficulty == "Hard":
        return random.choice(custom_config["HardSettings"])
    if difficulty == "Impossible":
        return random.choice(custom_config["ImpossibleSettings"])
    return "No settings"


def get_end_trait_value(difficulty: str) -> int:
    """
    Get the end trait value from configuration file
    :param difficulty: difficulty level
    :return: end trait value as integer
    """
    return custom_config["EndTraitValue"][difficulty]


def total_sum_of_neg_traits(traits: list) -> int:
    """
    Calculate the trait points for all selected traits
    :param traits: Selected traits
    :return: Calculated traits as integer
    """
    trait_sum = 0
    for element in traits:
        if element in custom_config["NegativePropertiesValueSubstitute"]:
            trait_sum += custom_config["NegativePropertiesValueSubstitute"][element]
        elif element in custom_config["NegativePropertiesValue"]:
            trait_sum += custom_config["NegativePropertiesValue"][element]
        else:
            pass
            # print(f"Fehler bei trait: {element}")
    return trait_sum


def send_user_info_message_with_points(points: int) -> str:
    """
    User message to inform the rest trait points
    :param points: Current trait points
    :return: Information as string
    """
    return USER_INFO_MESSAGE_1 + str(points) + USER_INFO_MESSAGE_2


def get_all_negative_traits(game_settings: dict) -> list:
    """
    Combine all the negative traits from game settings and delete process created
    and not used traits.
    :param game_settings: Current game settings
    :return: List of all negative traits
    """
    negative_traits = (
        game_settings["negative_trait_1"]
        + game_settings["negative_trait_2"]
        + game_settings["negative_trait_3"]
    )
    if "Nichts auswählen" in negative_traits:
        negative_traits.remove("Nichts auswählen")
    return negative_traits


def send_user_info_message_for_approval(game_settings: dict) -> str:
    """
    Send user information message with all selected game settings
    :param game_settings: Current game settings
    :return: Information as string
    """
    negative_traits = get_all_negative_traits(game_settings)
    info_message = (
        USER_INFO_MESSAGE_APPROVAL_1
        + game_settings["start_location"]
        + "\n"
        + USER_INFO_MESSAGE_APPROVAL_2
        + ", ".join(negative_traits)
        + "\n"
        + USER_INFO_MESSAGE_APPROVAL_3
        + game_settings["mission"][0]
        + "\n"
        + USER_INFO_MESSAGE_APPROVAL_4
        + str(game_settings["challenge_points"])
        + "\n"
        + USER_INFO_MESSAGE_APPROVAL_5
    )
    return info_message


def remove_wildcard_selection(traits: list) -> None:
    """
    Remote the wildcard from a trait list
    :param traits: List of traits
    :return: None
    """
    selection = DEFAULT_SKIP_SELECTION
    if "wildcard_skip_selection" in config:
        selection = config["wildcard_skip_selection"]
    traits.remove(selection)


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
