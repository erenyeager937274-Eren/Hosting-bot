import os
import subprocess
import shutil
import asyncio
from pyrogram import Client, filters
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", 23264133))
API_HASH = os.environ.get("API_HASH", "945e5b76ce8550bebbeeaf5599e7ce58")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8524126181:AAE1MhlELlzui8z3m_9C3vRGCo8CK74l4kY")
OWNER_ID = int(os.environ.get("OWNER_ID", 6883111123))

app = Client("UniversalHoster", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- WEB SERVER FOR RENDER (Port Binding) ---
async def handle(request):
    return web.Response(text="Bot is Running! 🚀")

async def start_web_server():
    server = web.Application()
    server.router.add_get("/", handle)
    runner = web.AppRunner(server)
    await runner.setup()
    # Render khud PORT environment variable deta hai
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"✅ Web Server started on port {port}")

# --- DEPLOY COMMAND ---
@app.on_message(filters.command("deploy") & filters.user(OWNER_ID))
async def deploy_any_bot(client, message):
    try:
        args = message.text.split(" ", 1)[1]
        repo_url, b_token = [p.strip() for p in args.split("|")]
    except:
        return await message.reply("❌ **Format:** `/deploy link | token`")

    repo_name = repo_url.split("/")[-1].replace(".git", "")
    path = f"bots/{repo_name}"

    m = await message.reply(f"🚀 **{repo_name}** ko deploy kar raha hoon...")

    if os.path.exists(path): shutil.rmtree(path)
    os.system(f"git clone {repo_url} {path}")

    with open(f"{path}/.env", "w") as f:
        f.write(f"API_ID={API_ID}\nAPI_HASH={API_HASH}\nBOT_TOKEN={b_token}\n")

    await m.edit("📦 **Installing Requirements...**")
    subprocess.run(["pip", "install", "-r", f"{path}/requirements.txt"])

    await m.edit("✅ **Bot Started in Background!**")
    log_file = open(f"{path}/logs.txt", "w")
    subprocess.Popen(["python3", "-m", "bot"], cwd=path, stdout=log_file, stderr=log_file)

# --- START BOTH ---
async def main():
    await start_web_server() # Render ki requirement
    await app.start()
    print("🔥 Manager Bot is Live!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    
