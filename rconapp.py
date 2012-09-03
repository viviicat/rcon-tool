import rcongui


class RconApp(object):
  def __init__(self):
    self.gui = rcongui.RconGui(self, self.servers)


