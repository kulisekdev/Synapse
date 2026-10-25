<!-- Synapse README -->

<div align="center">

# ⚡ Synapse

**A Discord bot built with Python, made to keep a community connected.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-bot-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-database-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)

[**📦 View Repository**](https://github.com/kulisekdev/Synapse) · [**🐛 Report a Bug**](https://github.com/kulisekdev/Synapse/issues) · [**✨ Request a Feature**](https://github.com/kulisekdev/Synapse/issues)

</div>

---

## 🌌 About

Synapse is a Python Discord bot with community features, server moderation tools, member logging, and a few fun commands. It uses **discord.py** and **MongoDB** to handle bot events and store user stats.

## ✨ Features

| Feature | What it does |
| --- | --- |
| 📈 **Levels & XP** | Track user XP and levels, check stats with `/level`, and view the leaderboard with `/levelleaderboard`. |
| 👋 **Welcome & leave logs** | Posts embeds when members join or leave. |
| 🛡️ **Moderation** | Includes owner-restricted `/ban` and `/purge` commands. |
| ✅ **Verification** | Provides a `/verify` command for member access. |
| 🔗 **Link filtering** | Removes messages containing configured unwanted links. |
| 🎱 **Question command** | Ask a question with `!question` and get a random answer. |
| 🔊 **Flashdance** | The anthem. Use `!flashdance` while in a voice channel. |

> Features and commands may evolve as Synapse is developed.

## 🚀 Getting Started

### Requirements

- Python 3.11 or newer
- A Discord bot application and bot token
- A MongoDB connection string
- FFmpeg available on your system for voice playback

### 1. Clone the project

```bash
git clone https://github.com/kulisekdev/Synapse.git
cd Synapse
```

### 2. Install dependencies

Install the packages used by the project:

```bash
pip install discord.py pymongo python-dotenv requests
```

Voice playback may also require an appropriate FFmpeg installation and voice dependencies for your platform.

### 3. Configure environment variables

Create a local `.env` file in the project root. **Never commit this file or share its contents.**

```env
mongodb=your_mongodb_connection_string
tkn=your_production_bot_token
testing=your_test_bot_token
webhook=your_error_reporting_webhook_url
```

The bot reads these environment variable names when starting. Keep production credentials private, and use a separate test bot while developing.

### 4. Check bot settings

Review `BotSettings.json` and configure the command prefix, owner ID, reconnect behavior, testing mode, and unwanted-link list for your own setup.

### 5. Run the bot

```bash
python main.py
```

Make sure your Discord bot has the permissions it needs for the features you enable. Server-specific channel and role IDs in the code must also be updated to match your server.

## 💬 Commands

| Command | Type | Description |
| --- | --- | --- |
| `/level` | Slash | View your level and XP, or another member's stats. |
| `/levelleaderboard` | Slash | Show the top five users by level. |
| `/verify` | Slash | Assign the configured member role. |
| `/purge <amount>` | Slash | Remove recent messages; restricted by the bot's owner check. |
| `/ban <user> [reason]` | Slash | Ban a member; restricted by the bot's owner check. |
| `!question <question>` | Prefix | Get a random answer. |
| `!flashdance` | Prefix | Play the anthem in your voice channel. |

The prefix is configurable in `BotSettings.json`; `!` is shown above as the example/default used in the code.

## 🧰 Built With

- [Python](https://www.python.org/)
- [discord.py](https://discordpy.readthedocs.io/)
- [MongoDB](https://www.mongodb.com/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [Requests](https://requests.readthedocs.io/)

## 🔒 Security Notes

- Keep `.env`, bot tokens, database credentials, and webhook URLs private.
- If a webhook URL is exposed, regenerate it.
- Check that your bot's role permissions and command access rules match your server's needs.
- Do not commit local secrets or downloaded files containing private data.

## 🤝 Contributing

Suggestions and bug reports are welcome! Open an [issue](https://github.com/kulisekdev/Synapse/issues) to discuss an idea or report a problem before making larger changes.

---

<div align="center">

**Made with Python, Discord, and a little chaos.** ⚡

*Synapse — connect the community.*

</div>
