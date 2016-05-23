import yaboli
import operator

class InfoBot(yaboli.Bot):
	"""
	Display information about the clients connected to a room in its nick.
	"""
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.bot_description = ("This bot displays information about the clients connected to the\n"
		                        "current room in its nick: (<people>p <bots>b <lurkers>l)\n"
		                        "Created by @Garmy using yaboli (Yet Another Bot Library)")
		
		self.add_command("info", self.info_command, "Show more detailed info.",
		                 ("!info @bot [ --list[=<who>] | --name=<name> ]\n"
		                  "--list=<who> : list user names and client/session ids\n"
		                  "--name=<name> : list info for users with the name specified\n"
		                  "<who> can be: people, bots, lurkers, all\n"
		                  "<name> is the name of the person (without leading '@')\n\n"
		                  "Shows different information about the clients connected to the\n"
		                  "current room."))
		
		self.room.add_callback("sessions", self.update_nick)
		
		self.update_nick()
	
	def update_nick(self):
		"""
		update_nick(self) -> None
		
		Change the name to display the correct values.
		"""
		
		nick = "\001({}p {}b {}l)".format(
			len(self.room.get_people()),
			len(self.room.get_bots()),
			len(self.room.get_lurkers())
		)
		
		self.room.set_nick(nick)
	
	def info_command(self, message, arguments, flags, options):
		"""
		info_command(message, arguments, flags, options) -> None
		
		Send a more verbose message.
		"""
		
		if "name" in options and "list" in options:
			msg = "Sorry, the --list and --name options can't be used simultaneously."
		
		elif ("name" in options and options["name"] is not True) or "list" in options:
			clients = []
			
			if "name" in options:
				name = self.room.mentionable(options["name"]).lower()
				
				clients = [c for c in self.room.get_sessions()
				           if self.room.mentionable(c.name).lower() == name]
			
			elif "list" in options:
				if options["list"] is True or options["list"] == "all":
					clients = self.room.get_sessions()
				elif options["list"] == "people":
					clients = self.room.get_people()
				elif options["list"] == "bots":
					clients = self.room.get_bots()
				elif options["list"] == "lurkers":
					clients = self.room.get_lurkers()
			
			if clients:
				msg = ""
				for client in sorted(clients, key=operator.attrgetter("name")):
					msg += "id={}, session_id={}, name={}\n".format(
						repr(client.id),
						repr(client.session_id),
						repr(client.name)
					)
				
				msg = msg[:-1] # remove trailing newline
			else:
				msg = "No clients"
		
		else:
			people = len(self.room.get_people())
			accounts =  len(self.room.get_accounts())
			bots = len(self.room.get_bots())
			lurkers = len(self.room.get_lurkers())
			
			msg = "people: {}\n  with accounts: {}\nbots: {}\nlurkers: {}\n\ntotal: {}\ntotal visible: {}"
			msg = msg.format(
				people,
				accounts,
				bots,
				lurkers,
				people + bots + lurkers,
				people + bots
			)
		
		self.room.send_message(msg, message.id)

manager = yaboli.BotManager(InfoBot, default_nick="infobot")
manager.create("bots")
