# coding=utf-8
import discord
import json
import re

client = discord.Client()
with open('config.json') as f:
    jsdata = json.load(f)
token = jsdata['token']


@client.event
async def on_ready():
    print("Amana: On ready.")


@client.event
async def on_message(message):
    # メッセージの受信時に呼び出される
    if message.author.bot:
        return

    cmds = message.content.split()
    print(cmds)
    print(client.user in cmds)
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
    reply = "甜花ちゃんどこ？"
    if cmds[0] == "room":
        if len(cmds) == 2:
            await make_channel(cmds[1])
            reply = f"{cmds[1]}を作成しました!"
    await msg.channel.send(f"{msg.author.mention} " + reply)


async def make_channel(name):
    global jsdata
    guild = client.get_guild(jsdata["target-guild"])
    cate = client.get_channel(jsdata["target-category"])
    await guild.create_voice_channel(name, category=cate)


@client.event
async def on_voice_state_update(member, before, after):
    # Voiceの状況が変わったときに呼び出される
    # チャンネル移動やミュートの解除など
    pass

client.run(token)
