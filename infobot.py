import logging

import yaboli
from yaboli.util import *


class InfoBot(yaboli.Bot):
    """
    Displays information about the clients connected to a room in its nick.
    """

    ALIASES = ["InfoBot", "PBL", "(PBL)", "PBLN", "(PBLN)"]
    HELP_GENERAL = "/me counts the types of clients in its nick"

    HELP_SPECIFIC = [
            "Displays information about the clients in a room in its nick:"
            " (<people>P\u00A0<bots>B\u00A0<lurkers>L\u00A0<bot-lurkers>N)",
            "You can also use @InfoBot, @PBL or @(PBL) for bot commands.",
            "",
            "!recount {atmention} - Recount people in the room",
            #"!detail {atmention} - Detailed list of clients in this room",
            #"!detail {atmention} @person - Detailed info regarding @person",
            "!hosts [--ping] - Lists all hosts currently in this room",
            "",
            "Created by @Garmy using https://github.com/Garmelon/yaboli.",
            "For additional info, try \"!help {atmention} <topic>\". Topics:",
            "\tcount, lurkers, changelog",
    ]

    HELP_COUNT = [
            "This bot counts the number of clients connected to a room. If you"
            " open a room in two different tabs, the bot counts you twice.",
            "The euphoria client, on the other hand, usually displays all"
            " connections of an account with the same nick as one in the nick"
            " list. Because of that, this bot's count is always at least as high"
            " as the number of nicks on the nick list, similar to the number on"
            " the button to toggle the nick list.",
            "",
            #"If the bot's count is off, try a !recount or a !restart {atmention}.",
            "If the bot's count is off, try a !recount.",
    ]

    HELP_LURKERS = [
            "People or bots who are connected to the room but haven't chosen a"
            " nick are lurkers. The euphoria client doesn't display them in the"
            " nick list.",
            "This bot differentiates between people (L) and bots (N) who are"
            " lurking.",
    ]

    HELP_CHANGELOG = [
            "(2019-04-13) re-add !hosts command",
            "(2019-04-12) update to yaboli rewrite 5",
    ]

    HELP_TOPICS = {
            "count": HELP_COUNT,
            "lurkers": HELP_LURKERS,
            "changelog": HELP_CHANGELOG,
    }

    def __init__(self, config_file):
        super().__init__(config_file)
        self.register_botrulez(help_=False, kill=True) # using our own help functions
        self.register_general("help", self.cmd_help_general, args=False)
        self.register_specific("help", self.cmd_help_specific)
        self.register_specific("recount", self.cmd_recount, args=False)
        self.register_general("hosts", self.cmd_hosts)

    async def cmd_help_specific(self, room, message, args):
        if not args.has_args():
            await message.reply(self.format_help(room, self.HELP_SPECIFIC))
            return

        if len(args.basic()) > 5:
            await message.reply("A maximum of 5 help topics is allowed.")
            return

        for topic in args.basic():
            help_lines = self.HELP_TOPICS.get(topic.lower())
            if help_lines is None:
                await message.reply(f"Module {topic!r} not found.")
            else:
                await message.reply(self.format_help(room, help_lines))

    async def cmd_recount(self, room, message, args):
        await self.update_nick(room)
        await message.reply("Recalibrated.")

    async def cmd_hosts(self, room, message, args):
        fancy = args.fancy()
        ping = "mention" in fancy.optional or "ping" in fancy.optional

        hosts = sorted(set(user.nick for user in room.users if user.is_manager))

        lines = []
        for host in hosts:
            if ping:
                lines.append(atmention(host))
            else:
                lines.append(host)

        if lines:
            lines = ["Hosts that are currently in this room:"] + lines
        else:
            lines = ["No hosts currently in this room."]

        await message.reply("\n".join(lines))

    # Updating the nick

    def format_nick(self, users):
        people = 0
        bots = 1 # room.who() doesn't include the bot itself.
        lurkers = 0
        nurkers = 0

        for user in users:
            if user.is_bot:
                if user.nick:
                    bots += 1
                else:
                    nurkers += 1
            else: # user is person or something else
                if user.nick:
                    people += 1
                else:
                    lurkers += 1

        info = []

        if people > 0:
            info.append(f"{people}P")

        info.append(f"{bots}B")

        if lurkers > 0:
            info.append(f"{lurkers}L")

        if nurkers > 0:
            info.append(f"{nurkers}N")

        return "\u0001(" + " ".join(info) + ")"

    async def update_nick(self, room):
        users = await room.who()
        new_nick = self.format_nick(users)
        await room.nick(new_nick)

    async def on_connected(self, room):
        await self.update_nick(room)

    async def on_join(self, room, user):
        await self.update_nick(room)

    async def on_part(self, room, user):
        await self.update_nick(room)

    async def on_nick(self, room, user, from_nick, to_nick):
        await self.update_nick(room)

#	@yaboli.command("detail")
#	async def command_detail(self, room, message, argstr):
#		sessions = room.listing.get()
#		args = self.parse_args(argstr)
#
#		if args:
#			lines = []
#			for arg in args:
#				if arg.startswith("@") and arg[1:]:
#					nick = arg[1:]
#				else:
#					nick = arg
#
#				for ses in sessions:
#					if similar(ses.nick, nick):
#							lines.append(self.format_session(ses))
#
#			if lines:
#				text = "\n".join(lines)
#			else:
#				text = "No sessions found that match any of the nicks."
#			await room.send(text, message.mid)
#
#		else:
#			sessions = sorted(sessions, key=lambda s: s.uid)
#			lines = [self.format_session(s) for s in sessions]
#			text = "\n".join(lines)
#			await room.send(text, message.mid)
#
#	@staticmethod
#	def format_session(s):
#		is_staff = "yes" if s.is_staff else "no"
#		is_manager = "yes" if s.is_manager else "no"
#		return f"UID: {s.uid}\t| SID: {s.sid}\t| staff: {is_staff}\t| host: {is_manager}\t| nick: {s.nick!r}"
#

if __name__ == "__main__":
    yaboli.enable_logging(level=logging.DEBUG)
    yaboli.run(InfoBot)
