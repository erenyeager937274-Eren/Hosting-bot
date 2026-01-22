import os
import subprocess
import shutil
import psutil
from pyrogram import Client, filters
from dotenv import load_dotenv

load_dotenv()

# Config
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))

app = Client("UniversalHoster", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Sabhi hosted bots ke liye ek folder
BASE_DIR = "all_bots"
if not os.path.exists(BASE_DIR):
    os.mkdir(BASE_DIR)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("🚀 **Universal Hosting Bot Tyar Hai!**\n\nKoshish karein: `/deploy link | token | session` (agar session chahiye)")

@app.on_message(filters.command("deploy") & filters.user(OWNER_ID))
async def deploy_any_bot(client, message):
    try:
        # Format: /deploy repo_link | bot_token | (optional variables)
        args = message.text.split(" ", 1)[1]
        parts = [p.strip() for p in args.split("|")]
        repo_url = parts[0]
        bot_token = parts[1]
    except:
        return await message.reply("❌ **Format Galat Hai!**\nUse: `/deploy link | token`")

    # Bot ka unique naam (Repo ke naam se)
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    path = f"{BASE_DIR}/{repo_name}"

    m = await message.reply(f"🔍 **{repo_name}** ko check kar raha hoon...")

    # Purana version delete karein agar hai toh
    if os.path.exists(path):
        shutil.rmtree(path)

    await m.edit("📥 **GitHub se Clone kar raha hoon...**")
    os.system(f"git clone {repo_url} {path}")

    await m.edit("📝 **Environment Variables (Vars) set kar raha hoon...**")
    # Har bot ke liye alag .env file banana
    with open(f"{path}/.env", "w") as f:
        f.write(f"API_ID={API_ID}\nAPI_HASH={API_HASH}\nBOT_TOKEN={bot_token}\n")
        # Agar user ne aur vars diye hain toh yahan add ho sakte hain

    await m.edit("📦 **Requirements install kar raha hoon... (Isme time lag sakta hai)**")
    subprocess.run(["pip", "install", "-r", f"{path}/requirements.txt"])

    await m.edit("🚀 **Bot ko Background mein Start kar raha hoon...**")
    
    # Ye command bot ke main file ko dhund kar chala degi (main.py ya bot.py)
    # Sabse aacha tarika hai 'python3 -m bot' ya direct file run karna
    log_file = open(f"{path}/logs.txt", "w")
    process = subprocess.Popen(
        ["python3", "-m", "bot"], # Ya fir "python3", "main.py"
        cwd=path,
        stdout=log_file,
        stderr=log_file
    )

    await m.edit(f"✅ **{repo_name} Deploy Ho Gaya!**\n\n**PID:** `{process.pid}`\n**Status:** Running 🟢")

@app.on_message(filters.command("stop_all") & filters.user(OWNER_ID))
async def stop_all(client, message):
    # Sabhi background processes ko band karne ka logic
    os.system("pkill python3")
    await message.reply("🛑 Sabhi hosted bots band kar diye gaye hain.")

app.run()
