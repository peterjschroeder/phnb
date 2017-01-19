# TODO: initialize all of them at the beginning, so you're not creating new ones each time a button is pressed
# TODO: move the actual logic out into a configuration file?
class Mode:
  def __str__(self):
    return str(self.__class__)

  def __getitem__(self, key):
    func = self._mapping.get(key)
    if func == None:
      default_action = self.default_action(key)
      if not default_action:
        raise KeyError("Key %s not bound in '%s'" % (key, self.__class__))
      return default_action
    else:
      return func

class MainMode(Mode):
  _mapping = {
    "a": lambda: print(lawl),
  }
  def default_action(self, key):
    if key == 'f':
      return False
    def_action = lambda: print("LAWL ACTION", key)
    return def_action

class InputMode(Mode):
  pass
     
class QuitSaveMode(Mode):
  pass

#TODO: others

lawl = MainMode()
