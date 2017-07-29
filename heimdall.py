#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configargparse
import asyncio
import discord
import os
import sys

client = discord.Client()


def get_args():
    if '-cf' not in sys.argv and '--config' not in sys.argv:
        config_files = [os.path.join(os.path.dirname(__file__),
                        './config/config.ini')]
    parser = configargparse.ArgParser(default_config_files=config_files)
    parser.add_argument('-cf', '--config', is_config_file=True,
                        help='Configuration file')
    parser.add_argument('-token', '--token', type=str,
                        help='Token for your bot account', required=True)
    parser.add_argument('-mod', '--mod_logs', type=str,
                        help='The ID of your mod_logs', required=True)
    parser.add_argument('-uses', '--uses', type=int,
                        help='The max number of uses for an invite',
                        required=True)
    parser.add_argument('-exp', '--expires', type=int,
                        help='Time in seconds an invite is set to expire',
                        required=True)

    args = parser.parse_args()

    return args


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.invisible)
    print('Connected! Ready to protect.')
    print('Username: ' + client.user.name)
    print('ID: ' + client.user.id)
    print('--Server List--')
    for server in client.servers:
        print(server.name)
    print('---------------')


@client.event
async def on_message(message):
    if message.content.lower() == '&invite':
        invite = await client.create_invite(destination=message.server,
                                            max_age=args.expires)
        await client.send_message(discord.utils.find(
            lambda u: u.id == message.author.id, client.get_all_members()),
                                  invite)
        await client.send_message(discord.utils.find(
            lambda c: c.id == args.mod_logs, client.get_all_channels()),
            "`{}` created an invite! (`{}`)".format(
                message.author.display_name, invite.code))
        await client.delete_message(message)


@client.event
async def on_member_join(member):
    invites = await client.invites_from(member.server)
    for invite in invites:
        if invite.uses > 0:
            await client.send_message(discord.utils.find(
                lambda c: c.id == args.mod_logs, client.get_all_channels()),
                                      "`{}` used an invite! (`{}`)".format(
                                          member.display_name, invite.code))
            await client.delete_invite(invite)


def heimdall():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.login(args.token))
    try:
        loop.run_until_complete(client.connect())
    except Exception:
        heimdall()

###############################################################################


if __name__ == '__main__':
    args = get_args()
    heimdall()
