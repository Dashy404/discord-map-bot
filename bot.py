import random
import discord
from discord.ext import commands

# -----------------------------
# ⚠️ REPLACE THIS WITH YOUR BOT TOKEN
import os
TOKEN = os.getenv("TOKEN")

# -----------------------------

# Enable intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Map pools
MAP_POOLS = {
    "hardpoint": ["Scar", "Den", "Exposure", "Blackheart", "Colossus"],
    "snd": ["Scar", "Den", "Exposure", "Colossus", "Raid"],
    "overload": ["Scar", "Den", "Exposure"]
}

# Series formats
SERIES_FORMATS = {
    "bo3": ["hardpoint", "hardpoint", "snd"],
    "bo5": ["hardpoint", "snd", "overload", "hardpoint", "snd"]
}

# Track available maps per mode for round-robin
available_per_mode = {mode: MAP_POOLS[mode].copy() for mode in MAP_POOLS}
last_map_played = None  # for back-to-back prevention

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Pick a map using round-robin and avoid back-to-back
def pick_map(mode):
    global available_per_mode, last_map_played

    available = available_per_mode[mode]

    # Avoid back-to-back repeat
    options = [m for m in available if m != last_map_played]

    if not options:  # if only last map is left, allow it
        options = available

    chosen = random.choice(options)

    # Remove chosen from available list
    available.remove(chosen)

    # Reset available list if empty
    if not available:
        available_per_mode[mode] = MAP_POOLS[mode].copy()

    # Track last map for back-to-back prevention
    last_map_played = chosen

    return chosen

# Command: Generate maps
@bot.command()
async def maps(ctx, series: str):
    series = series.lower()
    if series not in SERIES_FORMATS:
        await ctx.send("❌ Use `!maps bo3` or `!maps bo5`")
        return

    result = []
    for i, mode in enumerate(SERIES_FORMATS[series], start=1):
        chosen = pick_map(mode)
        result.append(f"**Game {i}:** {mode.upper()} — {chosen}")

    await ctx.send(f"🎮 **{series.upper()} Map Set** 🎮\n\n" + "\n".join(result))

# Command: Add a map
@bot.command()
async def addmap(ctx, mode: str, *, map_name: str):
    mode = mode.lower()
    if mode not in MAP_POOLS:
        await ctx.send("❌ Invalid mode.")
        return

    if map_name in MAP_POOLS[mode]:
        await ctx.send("⚠️ Map already exists.")
        return

    MAP_POOLS[mode].append(map_name)
    available_per_mode[mode].append(map_name)
    await ctx.send(f"✅ Added **{map_name}** to {mode.upper()}.")

# Command: Remove a map
@bot.command()
async def removemap(ctx, mode: str, *, map_name: str):
    mode = mode.lower()
    if mode not in MAP_POOLS:
        await ctx.send("❌ Invalid mode.")
        return

    if map_name not in MAP_POOLS[mode]:
        await ctx.send("⚠️ Map not found.")
        return

    MAP_POOLS[mode].remove(map_name)
    if map_name in available_per_mode[mode]:
        available_per_mode[mode].remove(map_name)
    await ctx.send(f"🗑️ Removed **{map_name}** from {mode.upper()}.")

# Command: Show map pool
@bot.command()
async def mappool(ctx, mode: str):
    mode = mode.lower()
    if mode not in MAP_POOLS:
        await ctx.send("❌ Invalid mode.")
        return

    maps = ", ".join(MAP_POOLS[mode])
    await ctx.send(f"🗺️ **{mode.upper()} Maps:** {maps}")

# Command: Reset series (resets available maps and back-to-back tracking)
@bot.command()
async def resetseries(ctx):
    global available_per_mode, last_map_played
    available_per_mode = {mode: MAP_POOLS[mode].copy() for mode in MAP_POOLS}
    last_map_played = None
    await ctx.send("🔄 Map series reset! All modes are now fresh and ready for new picks.")

# Run the bot
bot.run(TOKEN)
