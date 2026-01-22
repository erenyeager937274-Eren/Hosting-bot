import os
import subprocess
import shutil
import asyncio
import signal
from pyrogram import Client, filters
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", 23264133))
API_HASH = os.environ.get("API_HASH", "945e5b76ce8550bebbeeaf5599e7ce58")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_MANAGER_BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", 6883111123))

app = Client(
    "UniversalHoster",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- WEB SERVER (RENDER FIX) ---
async def handle(request):
    return web.Response(text="Bot is Running 🚀")

async def start_web_server():
    server = web.Application()
    server.router.add_get("/", handle)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"✅ Web server on port {port}")

# --- DEPLOY COMMAND ---
@app.on_message(filters.command("deploy") & filters.user(OWNER_ID))
async def deploy_any_bot(client, message):
    try:
        args = message.text.split(" ", 1)[1]
        repo_url, b_token = [x.strip() for x in args.split("|")]
    except:
        return await message.reply("❌ Use:\n`/deploy repo_link | bot_token`")

    repo_name = repo_url.split("/")[-1].replace(".git", "")
    path = f"bots/{repo_name}"

    msg = await message.reply(f"🚀 **Deploying {repo_name}...**")

    if os.path.exists(path):
        shutil.rmtree(path)

    os.system(f"git clone {repo_url} {path}")

    with open(f"{path}/.env", "w") as f:
        f.write(
            f"API_ID={API_ID}\n"
            f"API_HASH={API_HASH}\n"
            f"BOT_TOKEN={b_token}\n"
        )

    await msg.edit("📦 Installing requirements...")
    subprocess.run(["pip", "install", "-r", f"{path}/requirements.txt"])

    log_file = open(f"{path}/logs.txt", "w")

    process = subprocess.Popen(
        ["python3", "-m", "bot"],
        cwd=path,
        stdout=log_file,
        stderr=log_file
    )

    with open(f"{path}/pid.txt", "w") as p:
        p.write(str(process.pid))

    await msg.edit(f"✅ **{repo_name} started successfully!**")

# --- STOP COMMAND ---
@app.on_message(filters.command("stop") & filters.user(OWNER_ID))
async def stop_bot(client, message):
    try:
        repo_name = message.text.split(" ", 1)[1]
        path = f"bots/{repo_name}"
        pid_file = f"{path}/pid.txt"

        if not os.path.exists(pid_file):
            return await message.reply("❌ Bot running nahi hai")

        with open(pid_file) as f:
            pid = int(f.read())

        os.kill(pid, signal.SIGKILL)
        os.remove(pid_file)

        await message.reply(f"🛑 **{repo_name} bot band kar diya**")
    except:
        await message.reply("❌ Use:\n`/stop bot_repo_name`")

# --- START BOTH ---
async def main():
    await start_web_server()
    await app.start()
    print("🔥 Manager Bot is Live!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
