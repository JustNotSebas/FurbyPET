### 🩷 FurbyPET
Ever wanted to pet someone into oblivion?
Then you are in the right place and time!

## current functionality
* pet your friends!
* bonk your (stupid) friends!
* explode your enemies!
* get confused at all the logic the bot has behind in this repository!

## how to run locally
1. clone this repository with
`git clone https://www.github.com/JustNotSebas/FurbyPET.git` or download and unzip the repository.

2. rename .env.example to .env and set your variables

| variable            | description                                                                        | default                 | 
| ------------        | -----------                                                                        | -----------             | 
| PYTHONPYCACHEPREFIX | Removes Python's ``__pycache__`` folder generation. Set to 0 to reenable.            | 1                       | 
| TOKEN               | Sets the token used by py-cord to start the bot. Required.                         | ADD_YOUR_BOT_TOKEN_HERE | 
| TIMEZONE            | Sets the timezone used for time-related purposes. Uses PYTZ format. | UTC | UTC                     |

3. run with ``python3 main.py`` or ``py main.py`` if you're on windows. no extra arguments required, as long as you have set all your variables correctly.

## acknowledgements
the code is not prepared for some scenarios (example: not setting up .env or deleting the file structure) nor is it specifically designed with ease of use in mind, so be aware if cloning or working on it separately. if you don't want to host it yourself, [you can add to your server the public instance by clicking here](https://discord.com/oauth2/authorize?client_id=1367634461633544202), hosted by me.

no bot intents are required, and the bot runs by default with ``discord.Intents.default()``, so you only need to create a bot application in the [discord developer portal](https://discord.dev) to be able to use this bot.

since this is my first 'big' project gone open source, i dont expect contributions but i will review and appreciate any one available.

## license
this program is released under the GNU General Public License v3.0 (GPL-3.0). you are free to use, modify or distribute it as long as your changes remain open source (if distributing) and licensed under GPL. [click here to read the full license hosted in this repository.](LICENSE)
