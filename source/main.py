#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main functions for discord bot and general implementations for challenge generator.
"""
import os
import asyncio
import discord
from discord import app_commands

from source.game_settings import (
    User,
    get_location,
    get_profession,
    get_mission,
    get_settings,
    get_end_trait_value,
    send_user_info_message_with_points,
)
from source.game_settings import (
    custom_config,
    stream_challenge_config,
    total_sum_of_neg_traits,
    send_user_info_message_for_approval,
)
from source.custom_challenge import create_custom_challenge
from source.stream_challenge import (
    stream_challenge_location,
    negative_trait_one,
    negative_trait_two,
    negative_trait_three,
    mission,
    mission_value,
)
from source.picture import create_challenge_picture, herr_apfelring
from source.constants import (
    OFFSET_TRAIT_VALUE,
    TRAIT_DIFFERENCE_THR,
)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# client = commands.Bot(command_prefix="-", intents=discord.Intents.all())
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", None)
CHANNEL_CUSTOM_CHALLENGE_NAME = os.getenv("CHANNEL_CUSTOM_CHALLENGE_NAME", None)
CHANNEL_CUSTOM_CHALLENGE_ID = os.getenv("CHANNEL_CUSTOM_CHALLENGE_ID", None)
CHANNEL_STREAM_CHALLENGE_ID = os.getenv("CHANNEL_STREAM_CHALLENGE_ID", None)
SERVER_ID = os.getenv("SERVER_ID", None)
STREAM_CHALLENGE_CREATOR_ROLE_ID = os.getenv("STREAM_CHALLENGE_CREATOR_ROLE_ID", None)


async def failed_choice_explanation_option_one(
    challenge_settings: dict, interaction: discord.Interaction
) -> None:
    trait_points = abs(challenge_settings["challenge_points"])
    info_text = (
        f"Du hast die maximale Anzahl an Eigenschaftspunkten um {trait_points} Punkten "
        f"überschritten. Bitte starte mit dem Befehl neu und wähle weniger Eigenschaften "
        f"aus oder lass die Challenge in einer anderen Stadt mit weniger Punkten starten."
    )
    await interaction.message.channel.send(info_text)


async def custom_challenge_handler(difficulty: str) -> dict:
    """
    Create a custom challenge for requester based on selected difficulty.
    :param difficulty: level of difficulty
    :return: game settings for challenge
    """
    game_settings = {
        "successful_generated": True,
        "location": None,
        "profession": None,
        "difficulty": difficulty,
        "negative_traits": [],
        "positive_traits": [],
        "mission": None,
        "min_traits": custom_config["MinTraits"][difficulty],
        "settings": None,
        "trait_difference_thr": TRAIT_DIFFERENCE_THR,
    }
    game_settings["location"], location_value = get_location(difficulty)
    game_settings["profession"], profession_value = get_profession(difficulty)
    game_settings["mission"], _ = get_mission(difficulty)
    game_settings["settings"] = get_settings(difficulty)
    # print(game_settings)
    trait_value = profession_value
    end_trait_value = (
        get_end_trait_value(difficulty) + location_value + OFFSET_TRAIT_VALUE
    )
    await create_custom_challenge(trait_value, end_trait_value, game_settings)
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


class SteamChallengeApproval(discord.ui.View):
    def __init__(self, user, timeout=180):
        super().__init__(timeout=timeout)
        self.user_id = user.user_id
        self.response = None

    async def on_timeout(self):
        self.children[0].disabled = True
        self.clear_items()

    @discord.ui.select(
        placeholder="Do you want to enter this challenge like this?",
        options=[
            discord.SelectOption(
                label="Yes / Ja",
                description="Create a stream challenge for TeTü",
                emoji="😃",
            ),
            discord.SelectOption(
                label="No / Nein",
                description="Cancel the created stream challenge for TeTü",
                emoji="🤕",
            ),
        ],
        min_values=1,
        max_values=1,
    )
    async def select_difficulty_level(
        self, interaction: discord.Interaction, select_item: discord.ui.Select
    ) -> None:
        if interaction.user.id != self.user_id:
            return
        self.response = select_item.values
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()


class MissionOption(discord.ui.Select):
    def __init__(self, game_settings: dict):
        mission_options = mission(game_settings)
        super().__init__(
            options=mission_options,
            placeholder="Select the mission for the challenge",
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_mission_option(interaction, self.values)


class NegativeTraitThree(discord.ui.Select):
    def __init__(self, game_settings: dict):
        trait_options = negative_trait_three(game_settings)
        super().__init__(
            options=trait_options,
            placeholder="Select the 3rd negative traits",
            min_values=1,
            max_values=len(trait_options),
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_option_three(interaction, self.values)


class NegativeTraitTwo(discord.ui.Select):
    def __init__(self, game_settings: dict):
        trait_options = negative_trait_two(game_settings)
        super().__init__(
            options=trait_options,
            placeholder="Select the 2nd negative traits",
            min_values=1,
            max_values=len(trait_options),
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_option_two(interaction, self.values)


class NegativeTraitOne(discord.ui.Select):
    def __init__(self, game_settings: dict):
        trait_options = negative_trait_one(game_settings)
        super().__init__(
            options=trait_options,
            placeholder="Select the 1st negative traits",
            min_values=1,
            max_values=len(trait_options),
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.respond_to_option_one(interaction, self.values)


class StreamChallengeStage(discord.ui.View):
    game_settings = {
        "challenge_points": stream_challenge_config["TotalPoints"],
        "start_location": None,
        "negative_trait_1": None,
        "negative_trait_2": None,
        "negative_trait_3": None,
        "prohibitions": None,
        "mission": None,
        "choices_valid": False,
    }
    options = stream_challenge_location()

    def __init__(self, user, interaction, timeout=300):
        super().__init__(timeout=timeout)
        self.user_id = user.user_id
        self.start_interaction = interaction

    @discord.ui.select(
        placeholder="Select the starting area",
        options=options,
        # options=[discord.SelectOption(label="Test",description=f"Points weighting"),
        #          discord.SelectOption(label="Test2",description=f"Points weighting"),
        #         ],
        min_values=1,
        max_values=1,
    )
    async def select_starting_area(
        self, interaction: discord.Interaction, select_item: discord.ui.Select
    ) -> None:
        if interaction.user.id != self.user_id:
            return
        self.game_settings["start_location"] = select_item.values[0]
        self.game_settings["challenge_points"] -= stream_challenge_config[
            "StartingArea"
        ][self.game_settings["start_location"]]
        self.children[0].disabled = True
        user_message = send_user_info_message_with_points(
            self.game_settings["challenge_points"]
        )
        await self.start_interaction.edit_original_response(content=user_message)
        call_option_one = NegativeTraitOne(self.game_settings)
        self.add_item(call_option_one)
        await interaction.message.edit(view=self)
        await interaction.response.defer()

    async def respond_to_option_one(self, interaction: discord.Interaction, choices):
        if interaction.user.id != self.user_id:
            return
        self.game_settings["challenge_points"] -= total_sum_of_neg_traits(choices)
        self.game_settings["negative_trait_1"] = choices
        self.children[1].disabled = True
        if self.game_settings["challenge_points"] >= 0:
            self.game_settings["choices_valid"] = True
            user_message = send_user_info_message_with_points(
                self.game_settings["challenge_points"]
            )
            await self.start_interaction.edit_original_response(content=user_message)
            call_option_two = NegativeTraitTwo(self.game_settings)
            self.add_item(call_option_two)
            await interaction.message.edit(view=self)
            await interaction.response.defer()
        else:
            await failed_choice_explanation_option_one(self.game_settings, interaction)
            await interaction.message.edit(view=self)
            await interaction.response.defer()
            self.stop()

    async def respond_to_option_two(self, interaction: discord.Interaction, choices):
        if interaction.user.id != self.user_id:
            return
        self.game_settings["challenge_points"] -= total_sum_of_neg_traits(choices)
        self.game_settings["negative_trait_2"] = choices
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.children[2].disabled = True
        if self.game_settings["challenge_points"] >= 0:
            self.game_settings["choices_valid"] = True
            user_message = send_user_info_message_with_points(
                self.game_settings["challenge_points"]
            )
            await self.start_interaction.edit_original_response(content=user_message)
            call_option_three = NegativeTraitThree(self.game_settings)
            self.add_item(call_option_three)
            await interaction.message.edit(view=self)
        else:
            await failed_choice_explanation_option_one(self.game_settings, interaction)
            await interaction.message.edit(view=self)
            self.stop()

    async def respond_to_option_three(self, interaction: discord.Interaction, choices):
        if interaction.user.id != self.user_id:
            return
        self.game_settings["challenge_points"] -= total_sum_of_neg_traits(choices)
        self.game_settings["negative_trait_3"] = choices
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.children[3].disabled = True
        if self.game_settings["challenge_points"] >= 0:
            self.game_settings["choices_valid"] = True
            user_message = send_user_info_message_with_points(
                self.game_settings["challenge_points"]
            )
            await self.start_interaction.edit_original_response(content=user_message)
            call_option_mission = MissionOption(self.game_settings)
            # call_option_mission = SteamChallengeApproval()
            self.add_item(call_option_mission)
            await interaction.message.edit(view=self)
        else:
            await failed_choice_explanation_option_one(self.game_settings, interaction)
            await interaction.message.edit(view=self)
            self.stop()

    async def respond_to_mission_option(
        self, interaction: discord.Interaction, choices
    ):
        if interaction.user.id != self.user_id:
            return
        self.game_settings["challenge_points"] -= mission_value(choices)
        self.game_settings["mission"] = choices
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.children[4].disabled = True
        if self.game_settings["challenge_points"] >= 0:
            self.game_settings["choices_valid"] = True
            await interaction.message.edit(view=self)
            self.stop()
        else:
            await failed_choice_explanation_option_one(self.game_settings, interaction)
            await interaction.message.edit(view=self)
            self.stop()

    async def reset_settings(self):
        self.game_settings["challenge_points"] = stream_challenge_config["TotalPoints"]
        self.game_settings["start_location"] = None
        self.game_settings["negative_trait_1"] = None
        self.game_settings["negative_trait_2"] = None
        self.game_settings["negative_trait_3"] = None
        self.game_settings["prohibitions"] = None
        self.game_settings["mission"] = None
        self.game_settings["choices_valid"] = None


@client.event
async def on_ready() -> None:
    """
    Function to be called when the bot is ready.
    :return: None
    """
    await tree.sync(guild=discord.Object(id=SERVER_ID))
    print(f"We have logged in as {client.user}")


@tree.command(name="challenge", description="Create a random Project Zomboid challenge for your game.", guild=discord.Object(id=SERVER_ID))
async def custom_challenge(interaction):
    # ToDo: env verifizieren mit verfügbarkeit und type
    if interaction.channel.id != int(CHANNEL_CUSTOM_CHALLENGE_ID):
        # ToDo: Text in config
        await interaction.response.send_message("Falscher Channel", ephemeral=True, delete_after=60)
        return
    user = User(
        user_id=interaction.user.id,
        user_name=interaction.user.display_name,
        user_display_name=interaction.user.global_name,
    )
    view = CustomChallenge(user=user)
    await interaction.response.send_message(view=view)
    await view.wait()
    result = view.response
    if result is not None:
        task_create_custom_challenge = asyncio.create_task(
            custom_challenge_handler(result[0])
        )
        game_settings = await task_create_custom_challenge
        if game_settings["successful_generated"]:
            picture_path = await create_challenge_picture(game_settings, user)
            with open(picture_path, "rb") as file:
                image = discord.File(file)
                await interaction.channel.send(
                    f"{user.user_display_name} das ist deine Challenge:"
                )
                await interaction.channel.send(file=image)
        else:
            await interaction.channel.send(
                f"{user.user_display_name}, es ist ein Fehler aufgetreten. Bitte erstelle "
                f"nochmal eine Challenge. Ein Fehler-Report ist gespeichert."
            )


@tree.command(name="streamchallenge", description="Create a Project Zomboid challenge for TeTü.", guild=discord.Object(id=SERVER_ID))
async def stream_challenge(interaction):
    if interaction.channel.id != int(CHANNEL_STREAM_CHALLENGE_ID):
        # ToDo: Text in config
        await interaction.response.send_message("Falscher Channel", ephemeral=True, delete_after=60)
        return
    if int(STREAM_CHALLENGE_CREATOR_ROLE_ID) not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("Du hast keine Berechtigung, löse dazu Kanalpunkte ein.", ephemeral=True, delete_after=60)
        return
    user = User(
        user_id=interaction.user.id,
        user_name=interaction.user.display_name,
        user_display_name=interaction.user.global_name,
    )
    user_message = send_user_info_message_with_points(
        stream_challenge_config["TotalPoints"]
    )
    await interaction.response.send_message(user_message)
    view = StreamChallengeStage(user=user, interaction=interaction)
    await interaction.channel.send(view=view)
    await view.wait()
    result = view.game_settings
    # await view.reset_settings()
    approval_message = send_user_info_message_for_approval(result)
    await interaction.channel.send(approval_message)
    approval_view = SteamChallengeApproval(user)
    await interaction.channel.send(view=approval_view)
    await approval_view.wait()
    approval_result = approval_view.response
    if "yes" in approval_result[0].lower():
        await herr_apfelring(result, user)
        role = interaction.guild.get_role(int(STREAM_CHALLENGE_CREATOR_ROLE_ID))
        await interaction.user.remove_roles(role, reason="Finish stream challenge creation.")
    print(approval_result)
    print(result)


@client.event
async def on_message(message) -> None:
    """
    Function to be called when user sends a message.
    :param message: Message object
    :return: None
    """
    # print(message)
    # print(message.content)
    # print(message.channel.name)
    # print(message.channel.id)
    if message.author == client.user:
        return
    clean_message = message.content.lower()
    if clean_message.startswith("!challenge"):
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
                custom_challenge_handler(result[0])
            )
            game_settings = await task_create_custom_challenge
            if game_settings["successful_generated"]:
                picture_path = await create_challenge_picture(game_settings, user)
                with open(picture_path, "rb") as file:
                    image = discord.File(file)
                    await message.channel.send(
                        f"{user.user_display_name} das ist deine Challenge:"
                    )
                    await message.channel.send(file=image)
            else:
                await message.channel.send(
                    f"{user.user_display_name}, es ist ein Fehler aufgetreten. Bitte erstelle "
                    f"nochmal eine Challenge. Ein Fehler-Report ist gespeichert."
                )
    if clean_message.startswith("!streamchallenge"):
        if str(message.channel.id) != CHANNEL_STREAM_CHALLENGE_ID:
            return
        user = User(
            user_id=message.author.id,
            user_name=message.author.name,
            user_display_name=message.author.global_name,
        )
        user_message = send_user_info_message_with_points(
            stream_challenge_config["TotalPoints"]
        )
        user_info_message = await message.channel.send(user_message)
        view = StreamChallengeStage(user=user, info_message=user_info_message)
        await message.channel.send(view=view)
        await view.wait()
        result = view.game_settings
        # await view.reset_settings()
        approval_message = send_user_info_message_for_approval(result)
        await message.channel.send(approval_message)
        approval_view = SteamChallengeApproval(user)
        await message.channel.send(view=approval_view)
        await approval_view.wait()
        approval_result = approval_view.response
        if "yes" in approval_result[0].lower():
            herr_apfelring(result, user)
        print(approval_result)
        print(result)


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
