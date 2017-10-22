import sys
import yaboli
from yaboli.utils import *



class InfoBot(yaboli.Bot):
	"""
	Display information about the clients connected to a room in its nick.
	"""

	def __init__(self):
		super().__init__("()")

		self.add_help("count", (
			"This bot counts the number of clients connected to a room.\n"
			"If you open a room in two different tabs, the bot counts you "
			"twice.\n"
			"The euphoria client, on the other hand, usually displays all "
			"connections of an account as one nick in the nick list.\n"
			"Because of that, this bot's count is always as high as, or higher "
			"than, the number of nicks on the nick list.\n\n"
			"If the bot's count is off, try a !recount."
		))

		self.add_help("lurkers", (
			"People or bots who are connected to the room but haven't chosen a "
			"nick are lurkers.\n"
			"The euphoria client doesn't display them in the nick list.\n"
			"This bot differentiates between people (L) and bots (N) who are "
			"lurking."
		))

		self.add_help("changelog", (
			"- add !recount command\n"
			"- fix bot counting incorrectly\n"
		))

		self.help_specific = (
			"Displays information about the clients in a room in its nick:\n"
			"(<people>P <bots>B <lurkers>L <bot-lurkers>N)\n\n"
			"!recount @{nick} - Recount people in the room\n\n"
			"Created by @Garmy using yaboli.\n"
			"For additional info, try \"!help @{nick} <topic>\". Topics:\n"
		)
		self.help_specific += self.list_help_topics()

		self.register_command("recount", self.command_recount, specific=False)

	async def update_nick(self):
		p = len(self.room.listing.get(types=["account", "agent"], lurker=False))
		b = 1 + len(self.room.listing.get(types=["bot"], lurker=False))
		l = len(self.room.listing.get(types=["account", "agent"], lurker=True))
		n = len(self.room.listing.get(types=["bot"], lurker=True))

		name = []
		if p > 0: name.append(f"{p}P")
		if b > 0: name.append(f"{b}B")
		if l > 0: name.append(f"{l}L")
		if n > 0: name.append(f"{n}N")
		name = "\u0001(" + " ".join(name) + ")"

		await self.set_nick(name)

	async def on_join(self, session):
		await self.update_nick()
		await self.room.who()
		await self.update_nick()

	async def on_part(self, session):
		await self.update_nick()
		await self.room.who()
		await self.update_nick()

	async def on_nick(self, session_id, user_id, from_nick, to_nick):
		await self.update_nick()
		await self.room.who()
		await self.update_nick()

	async def on_snapshot(self, user_id, session_id, version, sessions,
	                      messages, nick=None, pm_with_nick=None,
	                      pm_with_user_id=None):
		# Not needed because we're updating the nick anyways.
		#super().on_snapshot(user_id, session_id, version, sessions, messages,
		#                    nick, pm_with_nick, pm_with_user_id)
		await self.update_nick()

	async def command_recount(self, message, argstr):
		await self.room.who()
		await self.update_nick()
		await self.room.send("Recalibrated.", message.mid)

def main():
	if len(sys.argv) != 2:
		print("USAGE:")
		print(f"  {sys.argv[0]} <room>")
		return

	run_bot(InfoBot, sys.argv[1])

if __name__ == "__main__":
	main()
