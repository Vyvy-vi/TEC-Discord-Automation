# Discord Automation tools for the TEC

This project consists of tools that might be useful for the [TokenEngineeringCommons'](https://tecommons.org/) discord server. The goal is to serve a variety of server issues ad manage different functionalities needed for the better functioning of using discord as a tool. Some of the tools in here are:
- Call Reminder scripts(currently running off of scheduled Github Actions)
- Discord Forms(A command group for building and filling forms on a discord bot and MongoDB, from discord itself)
- Discord Bot(for some automations that the TEC needs, like `ban`, `role-assignment` etc.)

## Contributing
If you have any feature requests, bug reports or feedback, please feel free to open a GitHub issue! If you would like to contribute, feel free to make changes(after mentioning what changes, in an issues) and open a Pull Request containing the proposed changes. The Pull Request would be reviewed as soon as we are able to do so!
#### Before contributing, please do read our [Contribution Guide](./CONTRIBUTING.md) first.

## How to edit the configs for the Call Reminder?
- Go to the [workflows folder](./.github/workflows) and select the respective github workflow(they are named in - `<working-group-name>.yml` format).
- Now, you can edit the respective env variable(the `env` field is near the bottom of the file) to edit the generated message by the Call Reminder.
```yml
env:
  IMG: 'Banner_ama.png'
  TITLE: 'TEC AMA - Welcome!'
  TEXT: "Join the AMA call in 1hour.\nWe meet at the TEC Community Hall voice channel:\n[https://discord.gg/fNPx3a2h9R](https://discord.gg/fNPx3a2h9R)\nIf you're new to the TEC, join us for a quick intro and Q&A! Everyone is welcome 🥳"
  KEY: ${{ secrets.ENCRYPTION_KEY }}
  URL: '8ef910a95622fa2e7b9cc64f172e58e1f7dc9f10817caa43cfb322ae61b211df5f9e536463fa1dc23bef9708442240b0eceb2d02c1e33325f5d7a0f28e34ce74d6d6ccc94a06a3f2fea1441b257195e92adcded2639bbb12df97ecb51ada44df560497c349951f3ed2ddc029f32c4df468295783c516ad869c8bee8f829a78e606a3c709f7e69b94792860265bbf7c13b9d73f888b96ce66d618c3e88a225e7b'
  TIME: 'Wednesday, 4pm CET'
```
- The respective fields do the following:
  - The `IMG` variable is the name of the image(located in the [resources folder](./.github/resources)). You could update the image by uploading a new image with the same name and deleting the old one.
  - The `TITLE` variable holds the Text in the title of the message
  - The `TEXT` variable is the body of the message sent by the reminder. This can be edited using the [Markdown](https://birdie0.github.io/discord-webhooks-guide/other/discord_markdown.html) format. **NOTE- Add links in hyperlink only, rather than raw text. That is- `[Link title or just the link](link)`**
  - The `TIME` variable shows the exact time of the call, and that can be edited. (**NOTE- However, this would not edit the time the Reminder message is sent**)
- Editing the **ACTUAL** time, when the message is sent in the server.
  You would have to edit the `cron` field in the file:
  - The [`cron` expression](https://en.wikipedia.org/wiki/Cron) is string describing individual timing details(each of the 5-6 letters means something). You could get a desirable cron expression using a software like [Crontab.guru](https://crontab.guru/). Put that expression in the cron field(near top of the file). If there are any problems, feel free to open an issues or dming `Vyvy-vi#5040` about this.
    ```yml
    name: TEC AMA - Welcome!
    on:
    schedule:
      - cron:  '0 13 * * 3'
    workflow_dispatch:
    ```
  - For new biweekly reminders, open an issue, and the reminder would be built in about a week or so. :D
- Editing the `URL`(that is, editing the channel in which the message is sent)- You could copy the respective long hex string from the [hexes file](./actions/hexes.txt) and paste it in this field. If the channel you're looking for isn't listed, open an issue or DM `Vyvy-vi#5040` for adding the channel to the list and to set the reminder for that channel.

## How to run your own instance?
For now, docs for making the Call reminders compatible for other repositories haven't been set up. (More on this, _soon_) For reproducing the discord bot locally, you can follow the steps below:
- Clone this repository
  ```bash
  git clone https://github.com/Vyvy-vi/TEC-Discord-Automation
  ```
- Navigate to the folder
  ```bash
  cd TEC-Discord-Automation
  ```
- Ensure that you have Python and pip installed(atleat of python version 3.7):
  ```bash
  python -V
  pip --version
  ```
  If not, you can install them from - https://www.python.org/downloads/
- This project relies on pipenv for dependency management. Install Pipenv - 
  ```bash
  pip install pipenv
  ```
- Install dependencies-
  ```bash
  pipenv sync
  ```
- Set up configs- Copy the `.env.example` file to a new file `.env` and put your discord bot token into the `DISCORD_BOT_TOKEN` variable(ref: To get the bot token follow [these](https://discordjs.guide/preparations/setting-up-a-bot-application.html#creating-your-bot)). You would also need a MongoDB Atlas instance(free tier cloud instance works for testing) and fetch the URI credential from that and put that in the `MONGO_URI` variable(here's more info on [how to get a mongodb URI](https://docs.mongodb.com/guides/server/drivers/#obtain-your-mongodb-connection-string)). NOTE- The db seed data hasn't been set yet.
- Run the Bot-
  ```bash
  pipenv run start
  ```
