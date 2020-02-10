# there are two types of data in an ansible file: host and group
# host is a string that is a dns name
# group is represented by the dictionary data structure in this script, and also has a string name
# group = { hosts: [<string>], children: [<group>] }

import json;
import yaml;


class Host:

  """
  logical structure:
  Host =
  {
    hostname: {
      <vars>,
    }
  }
  """

  class HostMissingValueException(Exception):
    # raised on access of a key that does not exist on host
    pass

  class HostArgumentNotStringException(Exception):
    # raised on arguing a host variable value that is not a string
    pass


  def __init__(self, hostname):
    self.hostname = hostname;
    self.parameters = {};

  def __setitem__(self, key, value):
    if (not isinstance(value, str)):
      raise self.HostArgumentNotStringException("cannot assign non-string to host variable; assignment=" + json.dumps(value));
    self.parameters[key] = value;

  def __getitem__(self, key):
    try:
      return self.parameters[key];
    except:
      raise self.HostMissingValueException("no value in " + self.hostname + "" + " for host: " + key);

  def to_ini(self):
    this_string = self.hostname;
    for param in self.parameters:
      this_string += "\t" + param + "=" + str(self.parameters[param]);
    return this_string;

  def to_yaml(self):
    return yaml.dump({ self.hostname: self.parameters }, indent=4);

  def __repr__(self):
    return self.to_ini();

  pass
