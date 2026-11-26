import asyncio
from collections.abc import Callable
from datetime import timedelta
from functools import wraps
from os import environ
from subprocess import run as system
from traceback import format_exc

import discord
from discord.ext import commands

bot = commands.Bot(
    command_prefix="plu!", intents=discord.Intents.all(), help_command=None
)
helptext = """```
Help for plubot:
plu!help - Shows this message
plu!echo <message> - Echoes the message back to you
plu!warn <user> <reason> - Warns a user with a reason
plu!mute <user> <seconds> <reason> - Mutes a user for a specified duration with a reason
plu!unmute <user> - Unmutes a user
plu!kick <user> <reason> - Kicks a user with a reason
plu!ban <user> <reason> - Bans a user with a reason
plu!unban <user> - Unbans a user
plu!purge <number> - Deletes a specified number of messages from the channel
plu!userinfo <user> - Shows information about a user
plu!serverinfo - Shows information about the server
plu!channelinfo <channel> - Shows information about a channel
plu!role create <name> - Creates a new role
plu!role delete <role> - Deletes a role
plu!role colour <role> <hex> - Changes the color of a role
plu!role hoist <role> <true|false> - Sets whether a role is displayed separately in the member list
plu!role mentionable <role> <true|false> - Sets whether a role can be mentioned by everyone
plu!role add <user> <role> - Adds a role to a user
plu!role remove <user> <role> - Removes a role from a user
plu!role info <role> - Shows information about a role
plu!role move up <role> <amount> - Moves a role up in the role hierarchy by a specified amount
plu!role move down <role> <amount> - Moves a role down in the role hierarchy by a specified amount
plu!role move to <role> <position> - Moves a role to a specific position in the role hierarchy, with 1 being the highest position
plu!role permissions set <role> <permissions> - Sets the permissions integer for a role
plu!role permissions get <role> <permissions> - Get the role permissions integer for a role
```"""


def error_handling(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(ctx: commands.Context, *args, **kwargs):
        try:
            await func(ctx, *args, **kwargs)
        except Exception:  # noqa: BLE001
            await ctx.send("```\n" + format_exc() + "\n```")

    return wrapper


@bot.event
async def on_ready():
    print(f"Logged in as{bot.user}")
    await bot.tree.sync()


@bot.hybrid_command(name="help")
@error_handling
async def _(ctx: commands.Context):
    await ctx.reply(helptext, mention_author=False)


@bot.hybrid_command(name="echo")
@error_handling
async def _(ctx: commands.Context, message: str):
    await ctx.send(message)


@bot.hybrid_command(name="warn")
@error_handling
@commands.has_permissions(moderate_members=True)
async def _(ctx: commands.Context, user: discord.Member, reason: str):
    guild = ctx.guild
    if guild is None:
        await ctx.send("This command can only be used in a server.")
        return
    await user.send(
        f"You have been warned in{guild.name} for the following reason:{reason!r}"
    )
    await ctx.send(f"{user.mention} successfully warned!")


@bot.hybrid_command(name="mute")
@error_handling
@commands.has_permissions(moderate_members=True)
async def _(ctx: commands.Context, user: discord.Member, seconds: int, reason: str):
    await user.timeout(timedelta(seconds=seconds), reason=reason)
    await ctx.send(f"{user.mention} successfully muted for{seconds} seconds!")


@bot.hybrid_command(name="unmute")
@error_handling
@commands.has_permissions(moderate_members=True)
async def _(ctx: commands.Context, user: discord.Member):
    await user.timeout(None)
    await ctx.send(f"{user.mention} successfully unmuted!")


@bot.hybrid_command(name="kick")
@error_handling
@commands.has_permissions(kick_members=True)
async def _(ctx: commands.Context, user: discord.Member, reason: str):
    await user.kick(reason=reason)
    await ctx.send(f"{user.mention} successfully kicked!")


@bot.hybrid_command(name="ban")
@error_handling
@commands.has_permissions(ban_members=True)
async def _(ctx: commands.Context, user: discord.Member, reason: str):
    await user.ban(reason=reason)
    await ctx.send(f"{user.mention} successfully banned!")


@bot.hybrid_command(name="unban")
@error_handling
@commands.has_permissions(ban_members=True)
async def _(ctx: commands.Context, user: discord.User):
    guild = ctx.guild
    if guild is None:
        await ctx.send("This command can only be used in a server.")
        return
    await guild.unban(user)
    await ctx.send(f"{user.mention} successfully unbanned!")


@bot.hybrid_command(name="purge")
@error_handling
@commands.has_permissions(manage_messages=True)
async def _(ctx: commands.Context, number: int):
    channel = ctx.channel
    if not isinstance(channel, discord.TextChannel):
        await ctx.send("This command can only be used in a text channel.")
        return
    await channel.purge(limit=number + 1)
    await ctx.send(f"Successfully deleted{number} messages!")


@bot.hybrid_command(name="userinfo")
@error_handling
async def _(ctx: commands.Context, user: discord.Member):
    await ctx.send(f"""```
    User Info:
    Name:{user.name}
    Discriminator:{user.discriminator}
    ID:{user.id}
    Status:{user.status}
    Top Role:{user.top_role}
    Joined At:{user.joined_at}
    Created At:{user.created_at}
    ```""")


@bot.hybrid_command(name="serverinfo")
@error_handling
async def _(ctx: commands.Context):
    guild = ctx.guild
    if guild is None:
        await ctx.send("This command can only be used in a server.")
        return
    await ctx.send(f"""```
    Server Info:
    Name:{guild.name}
    ID:{guild.id}
    Owner:{guild.owner}
    Member Count:{guild.member_count}
    Created At:{guild.created_at}
    ```""")


@bot.hybrid_command(name="channelinfo")
@error_handling
async def _(ctx: commands.Context, channel: discord.TextChannel):
    await ctx.send(f"""```
    Channel Info:
    Name:{channel.name}
    ID:{channel.id}
    Type:{channel.type}
    Topic:{channel.topic}
    NSFW:{channel.is_nsfw()}
    Created At:{channel.created_at}
    ```""")


@bot.hybrid_group(name="role")
@error_handling
async def role(ctx: commands.Context):
    if ctx.invoked_subcommand is None:
        await ctx.send(
            "Invalid role command passed. Use `plu!help` for more information."
        )


@role.command(name="create")
@error_handling
@commands.has_permissions(manage_roles=True)
async def role_create(ctx: commands.Context, name: str):
    guild = ctx.guild
    if guild is None:
        await ctx.send("This command can only be used in a server.")
        return
    await guild.create_role(name=name)
    await ctx.send(f"Role `{name}` successfully created!")


@role.command(name="delete")
@error_handling
@commands.has_permissions(manage_roles=True)
async def role_delete(ctx: commands.Context, role: discord.Role):
    await role.delete()
    await ctx.send(f"Role `{role.name}` successfully deleted!")


@role.command(name="colour")
@error_handling
@commands.has_permissions(manage_roles=True)
async def role_colour(ctx: commands.Context, role: discord.Role, hex: str):
    assert len(hex) == 6 and all(c in "0123456789abcdefABCDEF" for c in hex), (
        "Invalid hex color code"
    )
    color = discord.Color(int(hex, 16))
    await role.edit(color=color)
    await ctx.send(f"Role `{role.name}` color successfully changed to `#{hex}`!")


@role.command(name="hoist")
@error_handling
@commands.has_permissions(manage_roles=True)
async def role_hoist(ctx: commands.Context, role: discord.Role, hoist: bool):
    await role.edit(hoist=hoist)
    await ctx.send(f"Role `{role.name}` hoist successfully set to `{hoist}`!")


@role.command(name="mentionable")
@error_handling
@commands.has_permissions(manage_roles=True)
async def role_mentionable(
    ctx: commands.Context, role: discord.Role, mentionable: bool
):
    await role.edit(mentionable=mentionable)
    await ctx.send(
        f"Role `{role.name}` mentionable successfully set to `{mentionable}`!"
    )


@role.command(name="add")
@error_handling
@commands.has_permissions(manage_roles=True)
async def role_add(ctx: commands.Context, user: discord.Member, role: discord.Role):
    await user.add_roles(role)
    await ctx.send(f"Role `{role.name}` successfully added to{user.mention}!")


@role.command(name="remove")
@error_handling
@commands.has_permissions(manage_roles=True)
async def role_remove(ctx: commands.Context, user: discord.Member, role: discord.Role):
    await user.remove_roles(role)
    await ctx.send(f"Role `{role.name}` successfully removed from{user.mention}!")


@role.command(name="info")
@error_handling
async def role_info(ctx: commands.Context, role: discord.Role):
    await ctx.send(f"""```
    Role Info:
    Name:{role.name}
    ID:{role.id}
    Color:{role.color}
    Hoist:{role.hoist}
    Mentionable:{role.mentionable}
    Position:{role.position}
    Permissions:{role.permissions.value}
    Created At:{role.created_at}
    ```""")


@role.group(name="move")
@error_handling
@commands.has_permissions(manage_roles=True)
async def role_move(ctx: commands.Context):
    if ctx.invoked_subcommand is None:
        await ctx.send(
            "Invalid role move command passed. Use `plu!help` for more information."
        )


@role_move.command(name="up")
@error_handling
async def role_move_up(ctx: commands.Context, role: discord.Role, amount: int):
    new_position = role.position + amount
    await role.edit(position=new_position)
    await ctx.send(f"Role `{role.name}` successfully moved up by{amount} positions!")


@role_move.command(name="down")
@error_handling
async def role_move_down(ctx: commands.Context, role: discord.Role, amount: int):
    new_position = role.position - amount
    await role.edit(position=new_position)
    await ctx.send(f"Role `{role.name}` successfully moved down by{amount} positions!")


@role_move.command(name="to")
@error_handling
async def role_move_to(ctx: commands.Context, role: discord.Role, position: int):
    guild = ctx.guild
    if guild is None:
        await ctx.send("This command can only be used in a server.")
        return
    await role.edit(position=(guild.roles.index(role) - position))
    await ctx.send(f"Role `{role.name}` successfully moved to position{position}!")


@role.group(name="permissions")
@error_handling
@commands.has_permissions(manage_roles=True)
async def role_permissions(ctx: commands.Context):
    if ctx.invoked_subcommand is None:
        await ctx.send(
            "Invalid role permissions command passed. Use `plu!help` for more information."
        )


@role_permissions.command(name="set")
@error_handling
async def role_permissions_set(
    ctx: commands.Context, role: discord.Role, permissions: int
):
    await role.edit(permissions=discord.Permissions(permissions))
    await ctx.send(
        f"Role `{role.name}` permissions successfully set to `{permissions}`!"
    )


@role_permissions.command(name="get")
@error_handling
async def role_permissions_get(ctx: commands.Context, role: discord.Role):
    await ctx.send(
        f"Role `{role.name}` permissions integer is `{role.permissions.value}`!"
    )
    await ctx.send(
        "For help with permissions integers, visit [this link](https://botdesignerdiscord.com/tools/permission-calculator)."
    )


@bot.hybrid_command(name="reboot")
@error_handling
async def _(ctx: commands.Context):
    assert ctx.author.name == "pludunn", (
        "You do not have permissions to run hidden commands."
    )
    await ctx.send("Rebooting...")
    await asyncio.to_thread(system, "/home/pludunn/plubot/reboot.sh", check=False)
    await bot.close()


token = environ.get("PLUBOT_TOKEN")
if token is None:
    raise RuntimeError("PLUBOT_TOKEN environment variable is not set")
bot.run(token)
