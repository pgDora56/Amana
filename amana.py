# coding=utf-8
import discord
import json
import re
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s- %(name)s - %(levelname)s - %(message)s'
)

remove_check_channel = []
client = discord.Client()
with open('config.json') as f:
    jsdata = json.load(f)
token = jsdata['token']


@client.event
async def on_ready():
    logging.info("On ready.")
    await remove_check()


@client.event
async def on_message(message):
    # メッセージの受信時に呼び出される
    if message.author.bot:
        return

    cmds = message.content.split()
    logging.debug(cmds)
    delete = []
    for c in cmds:
        m = re.fullmatch(r"<@![0-9]+>", c)
        if m is not None:
            delete.append(c)
    for d in delete:
        cmds.remove(d)

    if client.user in message.mentions:
        await reply(message, cmds)


async def reply(msg, cmds):
    reply = "???"
    if cmds[0] == "room":
        if len(cmds) == 2:
            await make_channel(cmds[1])
            reply = f"{cmds[1]}を作成しました!"
    await msg.channel.send(f"{msg.author.mention} " + reply)


async def make_channel(name):
    global jsdata, remove_check_channel
    guild = client.get_guild(jsdata["target-guild"])
    cate = client.get_channel(jsdata["target-category"])
    ch = await guild.create_voice_channel(name, category=cate)
    remove_check_channel.append(TemporaryChannel(ch))


class TemporaryChannel:
    def __init__(self, channel):
        self.ch = channel
        self.remain = 0

    async def check(self):
        global jsdata
        try:
            len_member = len(self.ch.members)
            if len_member == 0:
                self.remain += 1
                if self.remain >= jsdata["wait-remove"]:
                    await self.delete()
                    return True
            else:
                self.remain = 0
            return False
        except Exception as e:
            logging.error(f"Fatal error and ended watching: {e}")
            return True

    async def delete(self):
        d_reason = f"Deleted over time({jsdata['wait-remove']})"
        await self.ch.delete(reason=d_reason)

    def string(self):
        return f"TempCh: {self.ch} {self.remain}"


async def remove_check():
    global jsdata, remove_check_channel
    while True:
        await asyncio.sleep(60)

        logging.info("Remove Check")
        deleted = []
        for idx in range(len(remove_check_channel)):
            isdeleted = await remove_check_channel[idx].check()
            if isdeleted:
                deleted.insert(0, idx)
            logging.debug(remove_check_channel[idx].string())

        for dch in deleted:
            remove_check_channel.pop(dch)

if __name__ == "__main__":
    client.run(token)
