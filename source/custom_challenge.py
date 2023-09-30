#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from source.game_settings import (
    config,
    LIST_OF_NEGATIVE_TRAITS,
    LIST_OF_POSITIVE_TRAITS,
)

from source.constants import (
    END_THR_TRAIT_VALUE,
    TRAIT_DIFFERENCE_MIN_THR,
)


async def check_limit_value_reached(trait_value: int, end_trait_value: int) -> bool:
    sum_trait_value = end_trait_value - trait_value
    if abs(sum_trait_value) <= END_THR_TRAIT_VALUE:
        return True
    else:
        return False


async def finish_trait_value(trait_value: int, game_settings: dict) -> None:
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


async def check_trait_possible(trait: str, game_settings: dict) -> bool:
    if not trait in config:
        return True
    return not any(
        True
        for element in config[trait]
        if element
        in (game_settings["positive_traits"] + game_settings["negative_traits"])
    )


async def check_difference_small_enough(trait: str, game_settings: dict) -> bool:
    if game_settings["difficulty"] == "Impossible":
        return True
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


async def create_custom_challenge(
    trait_value: int, end_trait_value: int, game_settings: dict
) -> None:
    time_out = 25
    min_run_trait_loops = game_settings["min_traits"]

    while (trait_value != end_trait_value) or (min_run_trait_loops <= 0):
        print(
            f"Trait-Value: {trait_value} End-Trait-Value: {end_trait_value} "
            f"timeout: {time_out} min loop: {min_run_trait_loops}"
        )
        if trait_value < end_trait_value:
            # negativen trait hinzufügen
            if await check_limit_value_reached(trait_value, end_trait_value) and (
                min_run_trait_loops <= 0
            ):
                await finish_trait_value(end_trait_value - trait_value, game_settings)
                break
            negative_trait = random.choice(LIST_OF_NEGATIVE_TRAITS)
            print(f"Negativer Trait: {negative_trait}")
            if negative_trait in game_settings["negative_traits"]:
                time_out -= 1
                print(f"Trait: {negative_trait} schon vorhanden.")
                continue
            if not await check_trait_possible(negative_trait, game_settings):
                time_out -= 1
                print(f"Trait: {negative_trait} nicht möglich.")
                continue
            if not await check_difference_small_enough(negative_trait, game_settings):
                time_out -= 1
                trait_difference_thr = game_settings["trait_difference_thr"]
                print(
                    f"Wert von Trait: {negative_trait} zu groß mit "
                    f"Vergleichswert: {trait_difference_thr}"
                )
                continue
            trait_value += config["NegativePropertiesValue"][negative_trait]
            game_settings["negative_traits"].append(negative_trait)
            min_run_trait_loops -= 1
        elif trait_value > end_trait_value:
            # positiven trait hinzufügen
            if await check_limit_value_reached(trait_value, end_trait_value) and (
                min_run_trait_loops <= 0
            ):
                await finish_trait_value(end_trait_value - trait_value, game_settings)
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
            if await check_limit_value_reached(trait_value, end_trait_value) and (
                min_run_trait_loops <= 0
            ):
                await finish_trait_value(end_trait_value - trait_value, game_settings)
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
        if time_out <= 0:
            print(f"Fehler bei {game_settings}")
            game_settings["successful_generated"] = False
            break


def main() -> None:
    pass


if __name__ == "__main__":
    main()
