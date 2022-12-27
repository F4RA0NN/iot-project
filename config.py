from configparser import ConfigParser

class Config:
  def __init__(self):
    self.config = ConfigParser()
    self.config.read('./config.ini')

  def put(self, section, key=None):
    if key is None:
      if self.config.has_option("MAIN", section):
        value = self.config["MAIN"][section]
      else:
        value = str(input(f"Provide {section}: "))
        self.config["MAIN"] = {section: value}
        with open('./config.ini', 'w') as f:
          self.config.write(f)
    else:
      if self.config.has_option(key, section):
        value = self.config[key][section]
      else:
        value = str(input(f"Provide {section} for {key}: "))
        self.config[key]={section: value}
        with open('./config.ini', 'w') as f:
          self.config.write(f)
    
    return value