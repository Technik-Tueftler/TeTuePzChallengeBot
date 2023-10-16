#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import yaml
from collections import namedtuple
from source.constants import (
    CONFIGURATION_FILE,
    CONFI_STREAM_CHALLENGE_FILE,
    USER_INFO_MESSAGE_1,
    USER_INFO_MESSAGE_2,
    USER_INFO_MESSAGE_APPROVAL_1,
    USER_INFO_MESSAGE_APPROVAL_2,
    USER_INFO_MESSAGE_APPROVAL_3,
    USER_INFO_MESSAGE_APPROVAL_4,
    USER_INFO_MESSAGE_APPROVAL_5,
)

with open(CONFIGURATION_FILE, encoding="utf-8") as f:
    config = yaml.safe_load(f)

with open(CONFI_STREAM_CHALLENGE_FILE, encoding="utf-8") as f:
    stream_challenge_config = yaml.safe_load(f)

LIST_OF_POSITIVE_TRAITS = list(config["PositivePropertiesValue"].keys())
LIST_OF_NEGATIVE_TRAITS = list(config["NegativePropertiesValue"].keys())

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


def get_settings(difficulty: str) -> str:
    if difficulty == "Easy":
        return random.choice(config["EasySettings"])
    elif difficulty == "Hard":
        return random.choice(config["HardSettings"])
    elif difficulty == "Impossible":
        return random.choice(config["ImpossibleSettings"])


def get_end_trait_value(difficulty: str) -> int:
    return config["EndTraitValue"][difficulty]


def total_sum_of_neg_traits(traits: list) -> int:
    trait_sum = 0
    for element in traits:
        if element in config["NegativePropertiesValueSubstitute"]:
            trait_sum += config["NegativePropertiesValueSubstitute"][element]
        elif element in config["NegativePropertiesValue"]:
            trait_sum += config["NegativePropertiesValue"][element]
        else:
            print(f"Fehler bei trait: {element}")
    return trait_sum


def send_user_info_message_with_points(points: int) -> str:
    return USER_INFO_MESSAGE_1 + str(points) + USER_INFO_MESSAGE_2


def send_user_info_message_for_approval(game_settings: dict) -> str:
    negative_traits = (
        game_settings["negative_trait_1"]
        + game_settings["negative_trait_2"]
        + game_settings["negative_trait_3"]
    )
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


def main() -> None:
    pass


if __name__ == "__main__":
    main()
