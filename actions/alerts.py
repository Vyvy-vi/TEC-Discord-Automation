import os
import nacl.secret

from dhooks import Webhook, Embed
from dotenv import load_dotenv


def main(
        key: int,
        title: str,
        text: str,
        img: str,
        url: str,
        time: str) -> None:
    """Function to send embed with data to discord channel"""
    box = nacl.secret.SecretBox(key)
    url = box.decrypt(
        bytes(
            url,
            'utf-8'),
        encoder=nacl.encoding.HexEncoder).decode('utf-8')
    hook = Webhook(url)
    embed = Embed(
        title=f"**{title}**",
        description=text,
        color=0x0F2EEE)
    embed.add_field(name='Time:', value=time, inline=False)
    embed.set_thumbnail(
        "https://images-ext-1.discordapp.net/external/9wjKKfnz90VR4MCxCu_KYVee6HDO8smJduqtL8dbNCs/%3Fsize%3D128/https/cdn.discordapp.com/icons/776352494992883722/0000b679a3e5f283653a38e138a43f9b.webp")
    embed.set_image(img)
    hook.send(embed=embed)


if __name__ == '__main__':
    load_dotenv()
    KEY = (int(os.environ['KEY'], 16)).to_bytes(32, 'big')
    IMG = "https://raw.githubusercontent.com/Vyvy-vi/TEC-Discord-Automation/main/.github/resources/" + \
        os.environ['IMG']
    TITLE = os.environ['TITLE']
    TEXT = os.environ['TEXT']
    HOOK_URL = os.environ['URL']
    TIME = os.environ['TIME']
    main(KEY, TITLE, TEXT, IMG, HOOK_URL, TIME)
