import asyncpraw


discord_token = "token-here"

reddit_clientid = "clientid"
reddit_clientsecret = "client-secret"
reddit_useragent = "cool-useragent"

openai_api_key = "openai-api-key"

aw_domain = "https://absurdismworld.cc/" #don't change this
aw_tnadne = "https://absurdismworld.cc/TNADNE/" #don't change this

inspirobot = "https://inspirobot.me/api?generate=true" #don't change this

www_dir = "http://127.0.0.1/my-cool-directory"

reddit = asyncpraw.Reddit( #don't change this
    client_id=reddit_clientid,
    client_secret=reddit_clientsecret,
    user_agent=reddit_useragent,
)
