import cPickle

MAX_CMDS = 25

class RecentCommandManager(object):
  def __init__(self, store):
    self.store = store
    self.commands = {}
    try:
      fcmds = open("recentcommands.pkl", "r")
      cmds = cPickle.load(fcmds)
      for cmd, val in cmds:
        self.commands[cmd] = val
        self.add_to_store(cmd)
      fcmds.close()

    except:
      pass

  def add_to_store(self, cmd):
    self.store.append([cmd])

  def addcmd(self, command):
    command = command.strip()

    if not command in self.commands:
      self.commands[command] = 0
      self.add_to_store(command)
    else:
      self.commands[command] += 1

  def quit(self):
    fcmds = open("recentcommands.pkl", "w")

    best_cmds = [tup for tup in sorted(self.commands.iteritems(), key=lambda(k, v) : (v, k))][:MAX_CMDS]

    cPickle.dump(best_cmds, fcmds)
    fcmds.close()
