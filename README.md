# AbsurdBot
A bot.

## Installation
This project uses UV as a package manager.
```bash
uv sync
```

### Webserver
This project includes a fastapi webserver, in order to serve files too large to upload normally. Please ensure that the environment variable `PUBLIC_BASE_PATH` is set to the public-facing URL (e.g. https://example.com/api).

### Token
You need a Discord bot token. Store this token in the `DISCORD_TOKEN` environment variable.

### Prefix
Set the bot prefix with the `BOT_PREFIX` environment variable.