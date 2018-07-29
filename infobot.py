import asyncio
import logging

import yaboli
from yaboli.utils import *
from join_rooms import join_rooms # List of rooms kept in separate file, which is .gitignore'd

# Turn all debugging on
asyncio.get_event_loop().set_debug(True)
logging.getLogger("asyncio").setLevel(logging.INFO)
logging.getLogger("yaboli").setLevel(logging.DEBUG)


class InfoBot(yaboli.Bot):
	"""
	Display information about the clients connected to a room in its nick.
	"""

	async def send(self, room, message):
		await self.botrulez_ping_general(room, message)
		await self.botrulez_ping_specific(room, message)
		await self.botrulez_help_general(room, message, text="I count the types of clients in my nick")
		await self.botrulez_uptime(room, message)
		await self.botrulez_kill(room, message)
		await self.botrulez_restart(room, message)

		await self.command_help(room, message)
		await self.command_recount(room, message)
		await self.command_detail(room, message)
		await self.command_hosts(room, message)

	forward = send

	@yaboli.command("help", specific=True, args=True)
	async def command_help(self, room, message, argstr):
		nick = mention(room.session.nick)
		args = self.parse_args(argstr)
		if not args:
			text = (
				"Displays information about the clients in a room in its nick:\n"
				"(<people>P <bots>B <lurkers>L <bot-lurkers>N)\n"
				"\n"
				"!recount @{nick} - Recount people in the room\n"
				"!detail @{nick} - Detailed list of clients in this room\n"
				"!hosts @{nick} [--mention] - Lists all hosts currently in this room\n"
				"\n"
				"Created by @Garmy using https://github.com/Garmelon/yaboli.\n"
				"For additional info, try \"!help @{nick} <topic>\". Topics:\n"
				"    count, lurkers, changelog"
			).format(nick=nick)
			await room.send(text, message.mid)
		else:
			for topic in args:
				if topic == "count":
					text = (
						"This bot counts the number of clients connected to a room. If you"
						" open a room in two different tabs, the bot counts you twice.\n"
						"The euphoria client, on the other hand, usually displays all"
						" connections of an account as one nick in the nick list. Because of"
						" that, this bot's count is always as high as, or higher than, the"
						" number of nicks on the nick list, similar to the number on the"
						" button to toggle the nick list.\n"
						"\n"
						"If the bot's count is off, try a !recount or a !restart @{nick}."
					).format(nick=nick)
				elif topic == "lurkers":
					text = (
						"People or bots who are connected to the room but haven't chosen a"
						" nick are lurkers. The euphoria client doesn't display them in the"
						" nick list.\n"
						"This bot differentiates between people (L) and bots (N) who are"
						" lurking."
					)
				elif topic == "changelog":
					text = (
						"- add !recount command\n"
						"- fix bot counting incorrectly\n"
						"- port to rewrite-4 of yaboli\n"
						"- add !detail and !manager commands\n"
					)
				else:
					text = f"Topic {topic!r} does not exist."

				await room.send(text, message.mid)

	async def update_nick(self, room):
		p = len(room.listing.get(types=["account", "agent"], lurker=False))
		b = len(room.listing.get(types=["bot"], lurker=False))
		l = len(room.listing.get(types=["account", "agent"], lurker=True))
		n = len(room.listing.get(types=["bot"], lurker=True))

		name = []
		if p > 0: name.append(f"{p}P")
		if b > 0: name.append(f"{b}B")
		if l > 0: name.append(f"{l}L")
		if n > 0: name.append(f"{n}N")
		name = "\u0001(" + " ".join(name) + ")"

		await room.nick(name)

	async def connected(self, room, log):
		await self.update_nick(room)

	async def join(self, room, session):
		await self.update_nick(room)
		await room.who()
		await self.update_nick(room)

	async def part(self, room, session):
		await self.update_nick(room)
		await room.who()
		await self.update_nick(room)

	async def nick(self, room, sid, uid, from_nick, to_nick):
		await self.update_nick(room)
		await room.who()
		await self.update_nick(room)

	@yaboli.command("recount", specific=True, args=False)
	async def command_recount(self, room, message):
		await room.who()
		await self.update_nick(room)
		await room.send("Recalibrated.", message.mid)

	@yaboli.command("detail", specific=True, args=False)
	async def command_detail(self, room, message):
		sessions = room.listing.get()
		sessions = sorted(sessions, key=lambda s: s.uid)
		sessions = [self.format_session(s) for s in sessions]
		text = "\n".join(sessions)
		await room.send(text, message.mid)

	@staticmethod
	def format_session(s):
		is_staff = "yes" if s.is_staff else "no"
		is_manager = "yes" if s.is_manager else "no"
		return f"UID: {s.uid}\t| SID: {s.sid}\t| staff: {is_staff}\t| host: {is_manager}\t| nick: {s.nick!r}"

	@yaboli.command("hosts", specific=True, args=True)
	async def command_hosts(self, room, message, argstr):
		flags, args, kwargs = self.parse_flags(self.parse_args(argstr))
		sessions = room.listing.get()
		sessions = sorted(set(s.nick for s in sessions if s.is_manager))
		if "ping" in kwargs:
			sessions = ["@" + mention(s) for s in sessions]
		else:
			sessions = [s for s in sessions]
		text = "Hosts that are currently in this room:\n" + "\n".join(sessions)
		await room.send(text, message.mid)

def main():
	bot = InfoBot("()", "infobot.cookie")
	join_rooms(bot)
	asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
	main()
