from discord.ext import commands
from .scripts.embeds import i_webhost
import os
import time
import json
import requests
import pathlib

www_directory = "./data/wwwtest"
www_database = f"{www_directory}/database.json"

default_db = {
    "creation_date": time.time(),
    "users": {}
}

default_user = {
    "storage_used": 0,
    "site_settings": {}
}

settings = {
    "storage": 26214400
}

if not os.path.exists(www_directory):
    os.mkdir(www_directory)

    with open(www_database, "w") as r:
        r.write(json.dumps(default_db))

db = json.loads(open(www_database, "r").read())


class WebsiteMaker:
    def __init__(self, ctx):
        homedir = f"{www_directory}/{str(ctx.author.id)}"
        if ctx.author.id not in db["users"]:
            db["users"][ctx.author.id] = default_user
        if not os.path.exists(homedir):
            os.mkdir(homedir)
        self.home_dir = os.path.realpath(homedir)
        self.ctx = ctx

    def get_own_data(self):
        return f"```python\n{json.dumps(db['users'][self.ctx.author.id])}```"

    def storage_fits(self, target_size):
        current_size = 0
        for path, dirs, files in os.walk(self.home_dir):
            for f in files:
                fp = os.path.join(path, f)
                current_size += os.path.getsize(fp)
        if (int(current_size) + int(target_size)) > settings["storage"]:
            return False
        else:
            return True

    def upload_to_self(self, file_url, location):
        target_size = requests.head(file_url).headers["content-length"]
        if not self.storage_fits(target_size):
            return [False, "Filesize exceeds your home directory size quota!"]
        target_path_clean = os.path.realpath(f"{self.home_dir}/{location}")
        p1 = pathlib.PurePath(self.home_dir)
        p2 = pathlib.PurePath(target_path_clean)
        if not p2.is_relative_to(p1):
            return [False, "Attempted to break out of home dir!"]
        os.makedirs(os.path.dirname(p2), exist_ok=True)
        with open(p2, "wb") as f:
            f.write(requests.get(file_url).content)
        return [True, True]


class WebsiteMakerCommands(commands.Cog, name="Static Website Hoster"):
    def __init__(self):
        pass

    @commands.group()
    async def web(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=i_webhost)

    @web.command(brief="Info/stats about your own subdomain")
    async def me(self, ctx):
        me = WebsiteMaker(ctx)
        await ctx.send(me.get_own_data())

    @web.command(brief="Upload a file to your subdomain")
    async def upload(self, ctx, url, loc):
        me = WebsiteMaker(ctx)
        res = me.upload_to_self(url, loc)
        if not res[0] is True:
            await ctx.send(res[1])
