import discord
import nacl
import json
from discord import PCMVolumeTransformer
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
import os
import asyncio
import random
from collections import defaultdict
import time
from datetime import timedelta
from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv("TOKEN")

OWNER_ID = 770527988033781770
SECRET_CHANNEL = "private-bot"
WELCOME_CHANNEL = "new-members"
MOD_LOG_CHANNEL = "mod-logs"
LOG_CHANNEL = "bot-logs"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!",help_command=None, intents=intents)
OWNER_ID = 770527988033781770

def is_owner(ctx):


    return (
        ctx.author.id == OWNER_ID
        and
        ctx.channel.name
        == SECRET_CHANNEL
    )
def is_mod(ctx):

    return (

        ctx.author.id
        in MODERATOR_IDS

    )
def is_staff(ctx):

    return (

        is_owner(ctx)

        or

        is_mod(ctx)

    )
def is_staff_member(member):

    return (

        member.id == OWNER_ID

        or

        member.id in MODERATOR_IDS

        or

        member.bot

    )
def is_protected(member):

    return (

        member.id == OWNER_ID

        or

        member.id
        in MODERATOR_IDS

    )
current_volume = 1.0

message_tracker = defaultdict(list)
chat_tracker = []

SPAM_LIMIT = 5
SPAM_TIME = 10

BAD_WORDS = [
    "badword1",
    "badword2",
    "abuse",
    "spamword"
]

autosend_running = False

DM_DELAY = 1

sound_queue = []
loop_enabled = False
current_song = None
ghost_mode = False
slowmode_active = False
MENTION_LIMIT = 5
CHAT_SPAM_LIMIT = 15
CHAT_SPAM_TIME = 10
anti_nuke_tracker = {}
ANTI_NUKE_LIMIT = 3
ANTI_NUKE_TIME = 20
SETTINGS_FILE = "settings.json"
spam_cooldown = {}
user_warnings = {}
sniped_message = {}
join_tracker = []
RAID_JOIN_LIMIT = 5
RAID_TIME = 30
MIN_ACCOUNT_AGE_DAYS = 7
vc_tracker = {}
VC_FOLLOW_LIMIT = 3
VC_FOLLOW_TIME = 60
VC_TIMEOUT_MINUTES = 10
MODERATOR_IDS = [

    1277332965629624411,

    915228950312124456,

    1507075008923566212,

    1361813587831554179

]
SPAM_WHITELIST = [

    OWNER_ID,

    1277332965629624411,

    915228950312124456,

    1507075008923566212,

    1361813587831554179

]
async def send_mod_log(
    guild,
    message
):

    log_channel = discord.utils.get(

        guild.text_channels,

        name=MOD_LOG_CHANNEL
    )

    if log_channel:

        try:

            await log_channel.send(
                message
            )

        except:
            pass
# Save warnings
def save_warnings():

    with open(
        "warnings.json",
        "w"
    ) as file:

        json.dump(
            user_warnings,
            file
        )


# Load warnings
def load_warnings():

    global user_warnings

    try:

        with open(
            "warnings.json",
            "r"
        ) as file:

            user_warnings = json.load(
                file
            )

            user_warnings = {

                int(k): v

                for k, v in
                user_warnings.items()

            }

    except:

        user_warnings = {}
# Save settings
def save_settings():

    settings = {

        "current_volume":
        current_volume,

        "ghost_mode":
        ghost_mode,

        "loop_enabled":
        loop_enabled

    }

    with open(
        SETTINGS_FILE,
        "w"
    ) as file:

        json.dump(
            settings,
            file
        )


# Load settings
def load_settings():

    global current_volume
    global ghost_mode
    global loop_enabled

    try:

        with open(
            SETTINGS_FILE,
            "r"
        ) as file:

            settings = json.load(
                file
            )

            current_volume = settings.get(
                "current_volume",
                1.0
            )

            ghost_mode = settings.get(
                "ghost_mode",
                False
            )

            loop_enabled = settings.get(
                "loop_enabled",
                False
            )

    except:

        current_volume = 1.0
        ghost_mode = False
        loop_enabled = False
async def anti_nuke_check(
    guild,
    user
):

    if user.id == OWNER_ID:
        return False

    current_time = time.time()

    user_id = user.id

    if user_id not in anti_nuke_tracker:

        anti_nuke_tracker[
            user_id
        ] = []

    anti_nuke_tracker[
        user_id
    ].append(current_time)

    anti_nuke_tracker[
        user_id
    ] = [

        t for t in
        anti_nuke_tracker[
            user_id
        ]

        if current_time - t
        < ANTI_NUKE_TIME
    ]

    if len(
        anti_nuke_tracker[
            user_id
        ]
    ) >= ANTI_NUKE_LIMIT:

        try:

            await user.edit(

                roles=[],

                reason=
                "Anti-Nuke Protection"

            )

        except:
            pass

        try:

            await user.timeout(

                timedelta(
                    minutes=30
                ),

                reason=
                "Anti-Nuke Triggered"

            )

        except:
            pass

        await send_mod_log(

            guild,

            f"🚨 ANTI-NUKE "
            f"triggered on "
            f"{user}"

        )

        return True

    return False
def is_protected_vc_user(member):

    return (

        member.id == OWNER_ID

        or

        member.id in MODERATOR_IDS

    )


@bot.event
async def on_ready():
    
    print(f"Logged in as {bot.user}")
    try:

        with open(
            "voice_channel.json",
            "r"
        ) as f:

            data = json.load(f)

        channel_id = data.get(
            "channel_id"
        )

        if channel_id:

            channel = bot.get_channel(
                channel_id
            )

            if channel:

                await channel.connect()

                print(
                    "Rejoined VC"
                )

    except Exception as e:

        print(
            "VC reconnect error:",
            e
        )


# Test command
@bot.command()
async def hello(ctx):

    await send_log(
        ctx,
        f"{ctx.author} used !hello"
    )

    await ctx.send(
        "Bot is working!"
    )

# Join VC
@commands.check(is_owner)
@bot.command()
async def join(ctx):

    try:

        if ctx.author.voice:

            channel = ctx.author.voice.channel

            if ctx.voice_client is None:

                await channel.connect()

            await ctx.send(
                "Joined VC"
            )

        else:

            await ctx.send(
                "Join VC first"
            )

    except Exception as e:

        await ctx.send(

            "❌ Voice system "
            "not supported on host"

        )

        print(e)


# Leave VC
@commands.check(is_owner)
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Left VC")


# Show sounds
@commands.check(is_owner)
@bot.command()
async def sounds(ctx):

    folder = "sounds"

    try:
        files = os.listdir(folder)

        if not files:
            await ctx.send("No sounds found")
            return

        sound_list = "\n".join(files)

        await ctx.send(f"Available sounds:\n{sound_list}")

    except Exception as e:
        await ctx.send(f"Error: {e}")


# Play sound
@commands.check(is_owner)
@bot.command()
async def play(ctx, filename):

    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Join VC first")
            return

    file_path = os.path.join("sounds", filename)

    if not os.path.exists(file_path):
        await ctx.send("File not found")
        return

    vc = ctx.voice_client

    if vc.is_playing():
        vc.stop()

    audio = discord.FFmpegPCMAudio(
        executable="ffmpeg",
        source=file_path
    )

    source = PCMVolumeTransformer(
        audio,
        volume=current_volume
    )

    vc.play(source)

    await ctx.send(f"Playing {filename}")
@commands.check(is_owner)
@bot.command()
async def volume(ctx, percent: int):

    global current_volume

    if percent < 0 or percent > 500:
        await ctx.send("Choose between 0 and 500")
        return

    current_volume = percent / 100

    await ctx.send(f"Volume set to {percent}%")
# Bot sends message
@commands.check(is_owner)
@bot.command()
async def say(ctx, *, message):
    await ctx.send(message)


# Pause audio
@commands.check(is_owner)
@bot.command()
async def pause(ctx):
    if ctx.voice_client:
        ctx.voice_client.pause()
        await ctx.send("Paused audio")


# Resume audio
@commands.check(is_owner)
@bot.command()
async def resume(ctx):
    if ctx.voice_client:
        ctx.voice_client.resume()
        await ctx.send("Resumed audio")


# Stop audio
@commands.check(is_owner)
@bot.command()
async def stopaudio(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("Stopped audio")


# Clear messages
@commands.check(
    lambda ctx: (
        is_owner(ctx)
        or
        is_mod(ctx)
    )
)
@bot.command()
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(f"Deleted {amount} messages")

    import asyncio
    await asyncio.sleep(2)

    await msg.delete()
# DM a mentioned user
@commands.check(is_owner)
@bot.command()
async def dm(ctx, member: discord.Member, *, message):

    try:
        await member.send(message)

        await ctx.send(
            f"DM sent to {member.name}"
        )

    except:
        await ctx.send(
            "Could not send DM"
        )


# DM by user ID
@commands.check(is_owner)
@bot.command()
async def dmid(ctx, userid: int, *, message):

    try:
        user = await bot.fetch_user(userid)

        await user.send(message)

        await ctx.send(
            "DM sent successfully"
        )

    except:
        await ctx.send(
            "Failed to send DM"
        )
def is_owner(ctx):
    return ctx.author.id == OWNER_ID
# Lock channel
@commands.check(is_owner)
@bot.command()
async def lock(ctx):

    overwrite = ctx.channel.overwrites_for(
        ctx.guild.default_role
    )

    overwrite.send_messages = False

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        overwrite=overwrite
    )

    await ctx.send("🔒 Channel locked")


# Unlock channel
@commands.check(is_owner)
@bot.command()
async def unlock(ctx):

    overwrite = ctx.channel.overwrites_for(
        ctx.guild.default_role
    )

    overwrite.send_messages = True

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        overwrite=overwrite
    )

    await ctx.send("🔓 Channel unlocked")


@commands.check(
    lambda ctx: (
        is_owner(ctx)
        or
        is_mod(ctx)
    )
)
@bot.command()
async def mutechat(ctx, minutes: int):

    overwrite = ctx.channel.overwrites_for(
        ctx.guild.default_role
    )

    # Lock only normal users
    overwrite.send_messages = False

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        overwrite=overwrite
    )

    # Bot sends message AFTER locking
    try:
        await ctx.author.send(
            f"Chat locked for {minutes} minute(s)"
        )
    except:
        pass

    await asyncio.sleep(minutes * 60)

    overwrite.send_messages = None

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        overwrite=overwrite
    )

    try:
        await ctx.channel.send(
            "🔓 Chat automatically unlocked"
        )
    except:
        pass
@bot.event
async def on_message(message):
    if message.author.bot:

        await bot.process_commands(
           message
        )

        return

    # Repeated message spam
    recent_messages = message_tracker.get(
        f"msg_{message.author.id}",
        []
    )
    
    recent_messages.append(
        message.content.lower()
    )
    
    message_tracker[
        f"msg_{message.author.id}"
    ] = recent_messages[-5:]
    
    # Same message repeated
    if (
    
        len(recent_messages) >= 3
    
        and
    
        len(
            set(
                recent_messages[-3:]
            )
        ) == 1
    
    ):
    
        try:
    
            await message.channel.purge(
    
                limit=20,
    
                check=lambda m:
                (
                    m.author
                    ==
                    message.author
                )
            )
    
            await message.author.timeout(
    
                timedelta(minutes=5),
    
                reason=
                "Repeated spam"
    
            )
    
            warning = await message.channel.send(
    
                f"⚠️ "
                f"{message.author.mention} "
                f"repeated spam detected"
    
            )
    
            await asyncio.sleep(5)
    
            await warning.delete()
    
        except:
            pass
    
        return
    
    
    # Emoji spam
    emoji_count = sum(
    
        1
    
        for char
        in message.content
    
        if ord(char)
        > 10000
    
    )
    
    if emoji_count >= 8:
    
        try:
    
            await message.delete()
    
        except:
            pass
    
        return
    
    
    # ALL CAPS spam
    if (
    
        len(message.content)
        > 15
    
        and
    
        message.content.isupper()
    
    ):
    
        try:
    
            await message.delete()
    
        except:
            pass
    
        return
    if is_staff_member(
        message.author
    ):

        await bot.process_commands(
            message
        )

        return
    # Mention spam protection
    mention_count = len(
        message.mentions
    )
    
    everyone_ping = (
        "@everyone"
        in message.content
    )
    
    here_ping = (
        "@here"
        in message.content
    )
    
    if (
    
        mention_count
        >= MENTION_LIMIT
    
        or
    
        everyone_ping
    
        or
    
        here_ping
    
    ):
    
        try:
    
            await message.delete()
    
            try:
    
                await message.author.timeout(
    
                    timedelta(minutes=5),
    
                    reason=
                    "Mention spam"
    
                )
    
            except:
                pass
    
            warning = await message.channel.send(
    
                f"🚫 "
                f"{message.author.mention} "
                f"mention spam detected"
    
            )
    
            await asyncio.sleep(5)
    
            await warning.delete()
    
        except:
            pass
    
        return    
    global slowmode_active
    
    current_time = time.time()
    
    chat_tracker.append(
        current_time
    )
    
    chat_tracker[:] = [
    
        t for t in chat_tracker
    
        if current_time - t
        < CHAT_SPAM_TIME
    ]
    
    # Chat explosion detected
    if (
    
        len(chat_tracker)
        >= CHAT_SPAM_LIMIT
    
        and
    
        not slowmode_active
    ):
    
        try:
    
            await message.channel.edit(
    
                slowmode_delay=5
    
            )
    
            slowmode_active = True
    
            await message.channel.send(
    
                "⚠️ High activity detected.\n"
                "Slowmode enabled (5 seconds)."
    
            )
    
            async def remove_slowmode():
    
                global slowmode_active
    
                await asyncio.sleep(60)
    
                await message.channel.edit(
    
                    slowmode_delay=0
    
                )
    
                slowmode_active = False
    
                await message.channel.send(
    
                    "✅ Slowmode disabled"
    
                )
    
            asyncio.create_task(
                remove_slowmode()
            )
    
        except:
            pass
    if ghost_mode:

        if message.author.id != OWNER_ID:
            return

    message_content = message.content.lower()

    for word in BAD_WORDS:

        if word in message_content:

            try:
                await message.delete()

                warning = await message.channel.send(
                    f"{message.author.mention} bad language not allowed!"
                )

                await asyncio.sleep(3)

                await warning.delete()

            except:
                pass

            return

    user_id = message.author.id
    if user_id in SPAM_WHITELIST:
        await bot.process_commands(message)
        return
    current_time = time.time()

    message_tracker[user_id].append(
        current_time
    )

    message_tracker[user_id] = [

        t for t in
        message_tracker[user_id]

        if current_time - t < SPAM_TIME
    ]

    if len(message_tracker[user_id]) >= SPAM_LIMIT:

        if user_id in spam_cooldown:
 
            if current_time - spam_cooldown[user_id] < 300:
                return

        spam_cooldown[user_id] = current_time

        try:

            deleted = await message.channel.purge(
                limit=50,
                check=lambda m:
                m.author == message.author
            )

            try:

                await message.author.timeout(
                    timedelta(minutes=5),
                    reason="Spam detected"
                )

            except:
                pass

            warning = await message.channel.send(

                f"⚠️ "
                f"{message.author.mention} "
                f"NEE AMMA PUKULU SPAMMING"

            )

            await asyncio.sleep(5)

            await warning.delete()

        except:
            pass

        await bot.process_commands(message)
# Auto message sender
@commands.check(is_owner)
@bot.command()
async def autosend(ctx, minutes: int, *, message):

    global autosend_running

    if autosend_running:
        await ctx.send(
            "Autosend already running"
        )
        return

    autosend_running = True

    await ctx.send(
        f"Autosending every {minutes} minute(s)"
    )

    while autosend_running:

        try:
            await ctx.send(message)
        except:
            pass

        await asyncio.sleep(minutes * 1)


# Stop autosend
@commands.check(is_owner)
@bot.command()
async def stopautosend(ctx):

    global autosend_running

    autosend_running = False

    await ctx.send(
        "Autosend stopped"
    )
# Mass DM all members
@commands.check(is_owner)
@bot.command()
async def massdm(ctx, *, message):

    sent = 0
    failed = 0

    await ctx.send(
        "Starting mass DM..."
    )

    for member in ctx.guild.members:

        if member.bot:
            continue

        try:
            await member.send(message)

            sent += 1

            await asyncio.sleep(DM_DELAY)

        except:
            failed += 1

    await ctx.send(
        f"Done! Sent: {sent}, Failed: {failed}"
    )


# Mass DM role
@commands.check(is_owner)
@bot.command()
async def massdmrole(ctx, role_name, *, message):

    role = discord.utils.get(
        ctx.guild.roles,
        name=role_name
    )

    if role is None:
        await ctx.send("Role not found")
        return

    sent = 0
    failed = 0

    await ctx.send(
        f"Sending DMs to {role.name}"
    )

    for member in role.members:

        if member.bot:
            continue

        try:
            await member.send(message)

            sent += 1

            await asyncio.sleep(DM_DELAY)

        except:
            failed += 1

    await ctx.send(
        f"Done! Sent: {sent}, Failed: {failed}"
    )
@bot.command()
async def roles(ctx):

    role_names = []

    for role in ctx.guild.roles:
        role_names.append(role.name)

    await ctx.send(
        "\n".join(role_names)
    )
# DM by username
@commands.check(is_owner)
@bot.command()
async def dmuser(ctx, username, *, message):

    member = discord.utils.get(
        ctx.guild.members,
        name=username
    )

    if member is None:

        member = discord.utils.get(
            ctx.guild.members,
            display_name=username
        )

    if member is None:
        await ctx.send(
            "User not found"
        )
        return

    try:
        await member.send(message)

        await ctx.send(
            f"DM sent to {member.name}"
        )

    except:
        await ctx.send(
            "Could not send DM"
        )
# Play next sound automatically
async def play_next(ctx):

    global current_song

    vc = ctx.voice_client

    if loop_enabled and current_song:

        source = discord.FFmpegPCMAudio(
            executable="ffmpeg",
            source=current_song
        )

        source = PCMVolumeTransformer(
            source,
            volume=current_volume
        )

        vc.play(
            source,
            after=lambda e:
            bot.loop.create_task(
                play_next(ctx)
            )
        )

        return

    if len(sound_queue) > 0:

        next_song = sound_queue.pop(0)

        current_song = next_song

        source = discord.FFmpegPCMAudio(
            executable="ffmpeg",
            source=next_song
        )

        source = PCMVolumeTransformer(
            source,
            volume=current_volume
        )

        vc.play(
            source,
            after=lambda e:
            bot.loop.create_task(
                play_next(ctx)
            )
        )


# Add to queue
@bot.command()
async def queue(ctx, filename):

    path = os.path.join(
        "sounds",
        filename
    )

    if not os.path.exists(path):
        await ctx.send(
            "File not found"
        )
        return

    sound_queue.append(path)

    await ctx.send(
        f"Queued {filename}"
    )

    vc = ctx.voice_client

    if vc and not vc.is_playing():

        await play_next(ctx)


# Show queue
@bot.command()
async def showqueue(ctx):

    if not sound_queue:
        await ctx.send(
            "Queue is empty"
        )
        return

    msg = ""

    for i, song in enumerate(
        sound_queue,
        1
    ):
        msg += f"{i}. {os.path.basename(song)}\n"

    await ctx.send(msg)


# Clear queue
@commands.check(
    lambda ctx: (
        is_owner(ctx)
        or
        is_mod(ctx)
    )
)
@bot.command()
async def clearqueue(ctx):

    sound_queue.clear()

    await ctx.send(
        "Queue cleared"
    )


# Loop on/off
@bot.command()
async def loop(ctx, mode):

    global loop_enabled

    mode = mode.lower()

    if mode == "on":
        loop_enabled = True
        save_settings()

        await ctx.send(
            "Loop enabled"
        )

    elif mode == "off":
        loop_enabled = False
        save_settings()

        await ctx.send(
            "Loop disabled"
        )

    else:
        await ctx.send(
            "Use: !loop on/off"
        )
@commands.check(is_owner)
@bot.command()
async def clearchannel(
    ctx,
    channel_name,
    amount: int
):

    channel = discord.utils.get(
        ctx.guild.channels,
        name=channel_name
    )

    if channel is None:

        await ctx.send(
            "Channel not found"
        )
        return

    await channel.purge(
        limit=amount
    )

    await ctx.send(
        f"Deleted {amount} messages from #{channel_name}"
    )
# Emergency lockdown
@commands.check(is_owner)
@bot.command()
async def panic(ctx):

    locked = 0

    for channel in ctx.guild.text_channels:

        try:

            overwrite = (
                channel.overwrites_for(
                    ctx.guild.default_role
                )
            )

            overwrite.send_messages = False

            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=overwrite
            )

            locked += 1

        except:
            pass

    await ctx.send(
        f"🚨 Panic mode enabled! Locked {locked} channels."
    )


# Unlock all channels
@commands.check(is_owner)
@bot.command()
async def safe(ctx):

    unlocked = 0

    for channel in ctx.guild.text_channels:

        try:

            overwrite = (
                channel.overwrites_for(
                    ctx.guild.default_role
                )
            )

            overwrite.send_messages = None

            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=overwrite
            )

            unlocked += 1

        except:
            pass

    await ctx.send(
        f"✅ Safe mode enabled! Unlocked {unlocked} channels."
    )
@commands.check(is_owner)
@bot.command()
async def ghost(ctx, mode):

    global ghost_mode

    mode = mode.lower()

    if mode == "on":

        ghost_mode = True
        save_settings()

        await ctx.send(
            "👻 Ghost mode enabled"
        )

    elif mode == "off":

        ghost_mode = False
        save_settings()

        await ctx.send(
            "👻 Ghost mode disabled"
        )

    else:

        await ctx.send(
            "Use: !ghost on/off"
        )
async def send_log(ctx, message):

    log_channel = discord.utils.get(
        ctx.guild.text_channels,
        name=LOG_CHANNEL
    )

    if log_channel:

        try:
            await log_channel.send(message)
        except:
            pass
async def send_log(ctx, message):

    log_channel = discord.utils.get(
        ctx.guild.text_channels,
        name=LOG_CHANNEL
    )

    if log_channel:

        try:
            await log_channel.send(message)

        except:
            pass
@bot.event
async def on_command(ctx):

    dangerous_commands = [

        "panic",
        "safe",
        "clear",
        "lock",
        "unlock",
        "mutechat",
        "massdm",
        "autosend",
        "clearchannel"

    ]

    if ctx.command.name in dangerous_commands:

        await send_log(

            ctx,

            f"⚡ {ctx.author} used !{ctx.command.name} in #{ctx.channel.name}"

        )
# Kick member
@commands.check(
    lambda ctx: (
        is_owner(ctx)
        or
        is_mod(ctx)
    )
)
@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if (
        is_protected(member)

        and

        not is_owner(ctx)
    ):

        await ctx.send(
            "❌ Moderators cannot punish staff"
        )

        return

        await ctx.send(
            "❌ You cannot kick the owner"
        )

    return

    try:

        await member.kick(
            reason=reason
        )

        await ctx.send(
            f"👢 {member.name} kicked"
        )

    except:

        await ctx.send(
            "Could not kick user"
        )


# Ban member
@commands.check(
    lambda ctx: (
        is_owner(ctx)
        or
        is_mod(ctx)
    )
)
@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if (
        is_protected(member)

        and

        not is_owner(ctx)
    ):

        await ctx.send(
            "❌ Moderators cannot punish staff"
        )

        return

        await ctx.send(
            "❌ You cannot ban the owner"
        )

        return

    try:

        await member.ban(
            reason=reason
        )

        await ctx.send(
            f"🔨 {member.name} banned"
        )

    except:

        await ctx.send(
            "Could not ban user"
        )


# Timeout member
@commands.check(
    lambda ctx: (
        is_owner(ctx)
        or
        is_mod(ctx)
    )
)
@bot.command()
async def timeout(
    ctx,
    member: discord.Member,
    minutes: int
):
    if (
        is_protected(member)

        and

        not is_owner(ctx)
    ):

        await ctx.send(
            "❌ Moderators cannot punish staff"
        )

        return

        await ctx.send(
            "❌ You cannot timeout the owner"
        )
        await send_mod_log(

            ctx.guild,

            f"⏳ "
            f"{ctx.author} timed out "
            f"{member} for "
            f"{minutes} minutes"

        )

        return
    try:

        await member.timeout(
            timedelta(minutes=minutes),
            reason="Admin timeout"
        )

        await ctx.send(
            f"⏳ {member.name} timed out for {minutes} minute(s)"
        )

    except:

        await ctx.send(
            "Could not timeout user"
        )
# Warn user
@commands.check(
    lambda ctx: (
        is_owner(ctx)
        or
        is_mod(ctx)
    )
)
@bot.command()
async def warn(
    ctx,
    member: discord.Member,
    *,
    reason="No reason"
):

    user_id = member.id
    if (
        is_protected(member)

        and

        not is_owner(ctx)
    ):

        await ctx.send(
            "❌ Moderators cannot punish staff"
        )

        return

        await ctx.send(
            "❌ You cannot warn the owner"
        )

    return

    if user_id not in user_warnings:
        user_warnings[user_id] = 0

    user_warnings[user_id] += 1

    save_warnings()

    warns = user_warnings[user_id]

    await ctx.send(

        f"⚠️ {member.name} warned.\n"
        f"Reason: {reason}\n"
        f"Warnings: {warns}"

    )
    
    await send_mod_log(

        ctx.guild,

        f"⚠️ "
        f"{ctx.author} warned "
        f"{member} | "
        f"Reason: {reason}"

    )
    # 3 warns = timeout
    if warns == 3:

        try:

            await member.timeout(
                timedelta(minutes=5),
                reason="Reached 3 warnings"
            )

            await ctx.send(
                f"⏳ {member.name} timed out for 5 minutes (3 warnings)"
            )

        except:
            pass

    # 5 warns = kick
    elif warns == 5:

        try:

            await member.kick(
                reason="Reached 5 warnings"
            )

            await ctx.send(
                f"👢 {member.name} kicked (5 warnings)"
            )
            await send_mod_log(

                ctx.guild,

                f"👢 "
                f"{ctx.author} kicked "
                f"{member} | "
                f"Reason: {reason}"

            )

        except:
            pass

    # 7 warns = ban
    elif warns >= 7:

        try:

            await member.ban(
                reason="Reached 7 warnings"
            )

            await ctx.send(
                f"🔨 {member.name} banned (7 warnings)"
            )
            await send_mod_log(

                ctx.guild,

                f"🔨 "
                f"{ctx.author} banned "
                f"{member} | "
                f"Reason: {reason}"

            )

        except:
            pass

# Check warnings
@commands.check(is_owner)
@bot.command()
async def warnings(
    ctx,
    member: discord.Member
):

    warns = user_warnings.get(
        member.id,
        0
    )

    await ctx.send(
        f"{member.name} has {warns} warning(s)"
    )


# Clear warnings
@commands.check(is_owner)
@bot.command()
async def clearwarns(
    ctx,
    member: discord.Member
):

    user_warnings[member.id] = 0

    save_warnings()

    await ctx.send(
        f"✅ Cleared warnings for {member.name}"
    )
# Remove timeout
@commands.check(is_owner)
@bot.command()
async def untimeout(
    ctx,
    member: discord.Member
):

    try:

        await member.timeout(
            None,
            reason="Timeout removed by admin"
        )

        await ctx.send(
            f"✅ Removed timeout from {member.name}"
        )

    except:

        await ctx.send(
            "Could not remove timeout"
        )


# Unban user
@commands.check(
    lambda ctx: (
        is_owner(ctx)
        or
        is_mod(ctx)
    )
)
@bot.command()
async def unban(
    ctx,
    *,
    username
):

    banned_users = [
        entry async for entry
        in ctx.guild.bans()
    ]

    for ban_entry in banned_users:

        user = ban_entry.user

        if user.name.lower() == username.lower():

            await ctx.guild.unban(user)

            await ctx.send(
                f"✅ Unbanned {user.name}"
            )

            return

    await ctx.send(
        "User not found in ban list"
    )
@bot.event
async def on_message_delete(message):

    if message.author.bot:
        return

    sniped_message[
        message.channel.id
    ] = {

        "author":
        message.author.name,

        "content":
        message.content
    }
@bot.command()
async def snipe(ctx):

    data = sniped_message.get(
        ctx.channel.id
    )

    if not data:

        await ctx.send(
            "No deleted message found"
        )

        return

    await ctx.send(

        f"🕵️ Deleted by: "
        f"{data['author']}\n"

        f"💬 Message: "
        f"{data['content']}"

    )
# Skip current sound
@bot.command()
async def skipaudio(ctx):

    vc = ctx.voice_client

    if vc and vc.is_playing():

        vc.stop()

        await ctx.send(
            "⏭️ Skipped"
        )

    else:

        await ctx.send(
            "Nothing is playing"
        )


# Stop everything
@bot.command()
async def stop(ctx):

    vc = ctx.voice_client

    if vc:

        sound_queue.clear()

        vc.stop()

        await ctx.send(
            "⏹️ Stopped and cleared queue"
        )

    else:

        await ctx.send(
            "Not connected"
        )


# Pause audio
@bot.command()
async def pauseaudio(ctx):

    vc = ctx.voice_client

    if vc and vc.is_playing():

        vc.pause()

        await ctx.send(
            "⏸️ Paused"
        )

    else:

        await ctx.send(
            "Nothing is playing"
        )


# Resume audio
@bot.command()
async def resumeaudio(ctx):

    vc = ctx.voice_client

    if vc and vc.is_paused():

        vc.resume()

        await ctx.send(
            "▶️ Resumed"
        )

    else:

        await ctx.send(
            "Nothing paused"
        )


# Shuffle queue
@bot.command()
async def shufflequeue(ctx):

    if not sound_queue:

        await ctx.send(
            "Queue empty"
        )

        return

    random.shuffle(
        sound_queue
    )

    await ctx.send(
        "🔀 Queue shuffled"
    )


# Remove item from queue
@bot.command()
async def removequeue(
    ctx,
    index: int
):

    if not sound_queue:

        await ctx.send(
            "Queue empty"
        )

        return

    if index < 1 or index > len(sound_queue):

        await ctx.send(
            "Invalid number"
        )

        return

    removed = sound_queue.pop(
        index - 1
    )

    await ctx.send(
        f"❌ Removed "
        f"{os.path.basename(removed)}"
    )
# Show available sounds
@bot.command()
async def soundlist(ctx):

    try:

        files = os.listdir(
            "sounds"
        )

        sound_files = [

            f for f in files

            if f.endswith(
                (
                    ".mp3",
                    ".wav",
                    ".ogg"
                )
            )
        ]

        if not sound_files:

            await ctx.send(
                "No sounds found"
            )

            return

        msg = (
            "🎵 Available Sounds:\n\n"
        )

        for sound in sound_files:

            msg += (
                f"• {sound}\n"
            )

        await ctx.send(msg)

    except:

        await ctx.send(
            "Sounds folder error"
        )
# Random sound
@bot.command()
async def randomsound(ctx):

    vc = ctx.voice_client

    if not vc:

        await ctx.send(
            "Join voice chat first"
        )

        return

    files = os.listdir(
        "sounds"
    )

    sound_files = [

        f for f in files

        if f.endswith(
            (
                ".mp3",
                ".wav",
                ".ogg"
            )
        )
    ]

    if not sound_files:

        await ctx.send(
            "No sounds found"
        )

        return

    random_file = random.choice(
        sound_files
    )

    path = os.path.join(
        "sounds",
        random_file
    )

    source = discord.FFmpegPCMAudio(
        executable="ffmpeg",
        source=path
    )

    source = PCMVolumeTransformer(
        source,
        volume=current_volume
    )

    vc.play(source)

    await ctx.send(
        f"🎲 Playing {random_file}"
    )
@bot.event
async def on_ready():

    load_warnings()
    load_settings()
    if not health_monitor.is_running():
        health_monitor.start()


    print(
        f"✅ Logged in as "
        f"{bot.user}"
    )

    print(
        "🔥 Bot online and stable"
    )
@bot.event
async def on_command_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.CheckFailure
    ):
        return

    print(
        f"❌ Error: {error}"
    )

    try:

        await ctx.send(
            "⚠️ Command error, "
            "but bot still running."
        )

    except:
        pass
# Background health monitor
@tasks.loop(minutes=5)
async def health_monitor():

    print(
        "💚 Health check OK"
    )

    print(
        f"Ghost Mode: {ghost_mode}"
    )

    print(
        f"Loop Enabled: {loop_enabled}"
    )

    print(
        f"Queue Size: "
        f"{len(sound_queue)}"
    )
@bot.command()
async def health(ctx):

    vc = ctx.voice_client

    voice_status = (
        "✅ Connected"
        if vc
        else "❌ Not Connected"
    )

    ghost_status = (
        "ON"
        if ghost_mode
        else "OFF"
    )

    loop_status = (
        "ON"
        if loop_enabled
        else "OFF"
    )

    await ctx.send(

        f"💚 Bot Health\n\n"

        f"Voice: "
        f"{voice_status}\n"

        f"Ghost Mode: "
        f"{ghost_status}\n"

        f"Loop Mode: "
        f"{loop_status}\n"

        f"Queue Size: "
        f"{len(sound_queue)}"

    )
@bot.event
async def on_member_join(member):

    # Existing raid protection
    current_time = time.time()

    join_tracker.append(
        current_time
    )

    join_tracker[:] = [

        t for t in join_tracker

        if current_time - t
        < RAID_TIME
    ]

    # Welcome channel
    welcome_channel = discord.utils.get(

        member.guild.text_channels,

        name=WELCOME_CHANNEL
    )

    if welcome_channel:

        try:

            await welcome_channel.send(

                f"🎉 Welcome "
                f"{member.mention}!\n\n"

                f"🔓 To unlock the server:\n"

                f"Type:\n"

                f"`!verify`\n\n"

                f"in #verify-here 😄"
            )
            await send_mod_log(

                ctx.guild,

                f"✅ "
                f"{ctx.author} verified"

            )

        except:
            pass

    # Fake account protection
    account_age = (
        datetime.now(
            member.created_at.tzinfo
        )
        -
        member.created_at
    ).days

    if (
        account_age
        < MIN_ACCOUNT_AGE_DAYS
    ):

        try:

            await member.timeout(

                timedelta(
                    minutes=10
                ),

                reason=
                "New account protection"

            )

        except:
            pass

    # Raid detection
    if len(join_tracker) >= RAID_JOIN_LIMIT:

        try:

            for channel in member.guild.text_channels:

                overwrite = (
                    channel.overwrites_for(
                        member.guild.default_role
                    )
                )

                overwrite.send_messages = False

                await channel.set_permissions(

                    member.guild.default_role,

                    overwrite=overwrite

                )

            print(
                "🚨 RAID DETECTED - "
                "SERVER LOCKED"
            )
            await send_mod_log(

                member.guild,

                "🚨 RAID DETECTED - "
                "SERVER LOCKED"

            )

        except:
            pass
    # Keep recent joins only
    join_tracker[:] = [

        t for t in join_tracker

        if current_time - t
        < RAID_TIME
    ]

    # Fake account protection
    account_age = (
        datetime.now(
            member.created_at.tzinfo
        )
        -
        member.created_at
    ).days

    if (
        account_age
        < MIN_ACCOUNT_AGE_DAYS
    ):

        try:

            await member.timeout(

                timedelta(
                    minutes=10
                ),

                reason=
                "New account protection"

            )

        except:
            pass

    # Raid detection
    if len(join_tracker) >= RAID_JOIN_LIMIT:

        try:

            for channel in member.guild.text_channels:

                overwrite = (
                    channel.overwrites_for(
                        member.guild.default_role
                    )
                )

                overwrite.send_messages = False

                await channel.set_permissions(

                    member.guild.default_role,

                    overwrite=overwrite

                )

            print(
                "🚨 RAID DETECTED - "
                "SERVER LOCKED"
            )

        except:
            pass
@bot.command()
async def verify(ctx):

    role = discord.utils.get(
        ctx.guild.roles,
        name="Verified"
    )

    if not role:

        await ctx.send(
            "Verified role not found"
        )

        return

    if role in ctx.author.roles:

        await ctx.send(
            "You are already verified"
        )

        return

    try:

        await ctx.author.add_roles(
            role
        )

        await ctx.send(

            f"✅ "
            f"{ctx.author.mention} "
            f"verified successfully!"

        )

    except:

        await ctx.send(
            "Verification failed"
        )
@bot.event
async def on_guild_channel_delete(
    channel
):

    async for entry in channel.guild.audit_logs(

        limit=1,

        action=
        discord.AuditLogAction.channel_delete
    ):

        await anti_nuke_check(

            channel.guild,

            entry.user
        )
@bot.event
async def on_member_ban(
    guild,
    user
):

    async for entry in guild.audit_logs(

        limit=1,

        action=
        discord.AuditLogAction.ban
    ):

        await anti_nuke_check(

            guild,

            entry.user
        )
@commands.check(is_owner)
@bot.command()
async def rate(
    ctx,
    messages_per_minute: int
):

    global DM_DELAY

    if messages_per_minute <= 0:

        await ctx.send(
            "Enter a valid number"
        )

        return

    DM_DELAY = (
        60
        /
        messages_per_minute
    )

    await ctx.send(

        f"✅ Rate set to "
        f"{messages_per_minute} "
        f"messages per minute\n"

        f"Delay: "
        f"{DM_DELAY:.1f} sec"

    )
@bot.command()
async def help(ctx):

    help_text = """

👑 OWNER COMMANDS

!panic → emergency lockdown
!safe → remove lockdown
!ghost on/off → toggle ghost mode
!massdm username message → send DM
!massdmloop username message → loop DM
!stopautosend → stop autosend
!ban @user reason → ban user
!unban username → unban user
!kick @user reason → kick user
!timeout @user minutes → timeout user
!untimeout @user → remove timeout
!clear number → delete messages


🛡️ MODERATOR COMMANDS

!warn @user reason → warn user
!warnings @user → see warnings
!clearwarns @user → reset warnings
!snipe → see deleted message
!health → bot health status


🎵 MUSIC / VOICE COMMANDS

!join → join voice channel
!leave → leave voice channel
!play filename.mp3 → play sound
!queue → show queue
!loop → toggle loop mode
!skip → skip sound
!stopaudio → stop audio
!pause → pause audio
!resume → resume audio
!shufflequeue → shuffle queue
!removequeue number → remove sound
!soundlist → show sounds
!randomsound → random sound


👥 USER COMMANDS

!verify → verify account
!hello → hello message
!help → show commands

"""

    await ctx.send(help_text)
@commands.check(is_staff)
@bot.command()
async def verifyuser(
    ctx,
    member: discord.Member
):

    role = discord.utils.get(

        ctx.guild.roles,

        name="Verified"
    )

    if not role:

        await ctx.send(

            "❌ Verified role "
            "not found"

        )

        return

    if role in member.roles:

        await ctx.send(

            f"{member.mention} "
            f"is already verified"

        )

        return

    try:

        await member.add_roles(
            role
        )

        await ctx.send(

            f"✅ "
            f"{member.mention} "
            f"verified successfully"

        )

        await send_mod_log(

            ctx.guild,

            f"✅ "
            f"{ctx.author} "
            f"manually verified "
            f"{member}"

        )

    except Exception as e:

        await ctx.send(

            "❌ Verification failed"

        )

        print(e)
@bot.event
async def on_voice_state_update(

    member,
    before,
    after
):

    # Ignore bots
    if member.bot:
        return

    # User joined VC
    if after.channel:

        guild = member.guild

        protected_members = [

            m for m in guild.members

            if (
                is_protected_vc_user(m)

                and

                m.voice

                and

                m.voice.channel
                ==
                after.channel
            )
        ]

        # No staff in VC
        if not protected_members:
            return

        current_time = time.time()

        if member.id not in vc_tracker:

            vc_tracker[
                member.id
            ] = []

        vc_tracker[
            member.id
        ].append(current_time)

        vc_tracker[
            member.id
        ] = [

            t for t in
            vc_tracker[
                member.id
            ]

            if current_time - t
            < VC_FOLLOW_TIME
        ]

        # Suspicious follow detected
        if len(

            vc_tracker[
                member.id
            ]

        ) >= VC_FOLLOW_LIMIT:

            try:

                await member.move_to(
                    None
                )

                await member.timeout(

                    timedelta(
                        minutes=
                        VC_TIMEOUT_MINUTES
                    ),

                    reason=
                    "VC trolling"
                )

                await send_mod_log(

                    guild,

                    f"🚫 "
                    f"{member} "
                    f"removed for "
                    f"VC trolling"

                )

            except:
                pass


while True:

    try:

        bot.run(TOKEN)

    except KeyboardInterrupt:

        print(
            "🛑 Bot stopped manually"
        )

        break

    except Exception as e:

        print(
            f"Reconnect error: {e}"
        )

        print(
            "Reconnecting in 10 seconds..."
        )

        time.sleep(10)
