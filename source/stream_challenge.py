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


def mission_value(selected_mission: list) -> int:
    trait_sum = 0
    for element in selected_mission:
        trait_sum += stream_challenge_config["Mission"][element]
    return trait_sum


def mission(game_settings: dict) -> list:
    challenge_points = game_settings["challenge_points"]
    all_missions = stream_challenge_config["Mission"]
    all_possible_missions = []
    for key in all_missions:
        mission_value = all_missions[key]
        if mission_value <= challenge_points:
            all_possible_missions.append([mission_value, discord.SelectOption(
                label=key, description=f"Points weighting: {mission_value}"
            )])
    sorted_missions = sorted(all_possible_missions, key=lambda x: x[0])
    return [element[1] for element in sorted_missions]


def negative_trait_three(game_settings: dict) -> list:
    selected_neg_traits_one_two = game_settings["negative_trait_1"] + game_settings["negative_trait_2"]
    all_neg_traits_three = stream_challenge_config["NegativePropertiesValueOptionThree"]
    trait_options_three = []

    for key in all_neg_traits_three:
        if key in config["NegativePropertiesValueSubstitute"]:
            value = config["NegativePropertiesValueSubstitute"][key]
        elif key in config["NegativePropertiesValue"]:
            value = config["NegativePropertiesValue"][key]
        else:
            value = 0
        temp_abort = False
        if key in config:
            for trait in config[key]:
                if trait in selected_neg_traits_one_two:
                    temp_abort = True
                    break
        if value <= game_settings["challenge_points"] and not temp_abort:
            trait_options_three.append([value, discord.SelectOption(
                    label=key, description=f"Points weighting: {value}"
                )])
            # traits_option_three.append(
            #     discord.SelectOption(
            #         label=key, description=f"Points weighting: {value}"
            #     )
            # )
    sorted_traits_option_three = sorted(trait_options_three, key=lambda x: x[0])
    return [element[1] for element in sorted_traits_option_three]


def negative_trait_two(game_settings: dict) -> list:
    selected_neg_traits_one = game_settings["negative_trait_1"]
    all_neg_traits_two = stream_challenge_config["NegativePropertiesValueOptionTwo"]
    trait_options_two = []

    for key in all_neg_traits_two:
        if key in config["NegativePropertiesValueSubstitute"]:
            value = config["NegativePropertiesValueSubstitute"][key]
        elif key in config["NegativePropertiesValue"]:
            value = config["NegativePropertiesValue"][key]
        else:
            value = 0
        temp_abort = False
        if key in config:
            for trait in config[key]:
                if trait in selected_neg_traits_one:
                    temp_abort = True
                    break
        if value <= game_settings["challenge_points"] and not temp_abort:
            trait_options_two.append([value,
                discord.SelectOption(
                    label=key, description=f"Points weighting: {value}"
                )]
            )
    sorted_traits_option_two = sorted(trait_options_two, key=lambda x: x[0])
    return [element[1] for element in sorted_traits_option_two]


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
            traits_option_one.append([value,
                discord.SelectOption(
                    label=key, description=f"Points weighting: {value}"
                )]
            )
    sorted_traits_option_one = sorted(traits_option_one, key=lambda x: x[0])
    return [element[1] for element in sorted_traits_option_one]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
