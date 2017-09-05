import sys
import yaboli
from yaboli.utils import *



class InfoBot(yaboli.Bot):
	"""
	Display information about the clients connected to a room in its nick.
	"""
	
	def __init__(self, name):
		super().__init__(name)
		
		self.help_specific = (
			"Displays information about the clients in a room in its nick:\n"
			"(<people>P <bots>B [<lurkers>L] [<bot-lurkers>N])\n\n"
			"Github: https://github.com/Garmelon/infobot (complies with botrulez, including !kill and !restart)"
			"Created by @Garmy using yaboli (https://github.com/Garmelon/yaboli)\n"
		)
	
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
	
	async def on_part(self, session):
		await self.update_nick()
	
	async def on_snapshot(self, user_id, session_id, version, listing, log, nick=None,
	                      pm_with_nick=None, pm_with_user_id=None):
		await self.update_nick()

def main():
	if len(sys.argv) != 2:
		print("USAGE:")
		print(f"  {sys.argv[0]} <room>")
		return
	
	run_bot(InfoBot, sys.argv[1], "()")

if __name__ == "__main__":
	main()
