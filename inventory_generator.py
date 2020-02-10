from GroupWorks import *;
import yaml;
import json;
import argparse;


def main(hosts, template, out_format):

  # parse the template into YAML
  input_string = "";
  with open(template) as file_template:
    for line in file_template:
      input_string += line;
  template = yaml.load(input_string);#, Loader=yaml.CLoader);


  # parse hosts file
  # hostnames: valid DNS names (i.e. valid inventory records)
  # process: line comments ignored; first word is kept; \ is replaced

  hostnames = []

  for lf_line in open(hosts):
    line = lf_line[:-1]
    trimmed = line.strip()
    if (not trimmed.startswith("#") and len(trimmed) > 0):
      tokens = trimmed.split(" ")
      try:
        word = tokens[0]
        if (is_dns_name(word)):
          hostnames.append(word)
      except:
        pass #design choice (pass or raise Exception)


  hostname_set = {host: None for host in hostnames};

  group_set = build_group(template, hostname_set);


  # print
  if (out_format is None):
    print(group_set);

  else:
    format = out_format.lower();
    if (format in ["ini", ".ini"]):
      print(to_ini(group_set));
    elif (format in ["yaml", "yml", ".yaml", ".yml"]):
      print(yaml.dump(group_set, indent=2));
    elif (format in ["json", ".json"]):
      print(json.dumps(group_set, indent=2));

  pass



def is_dns_name(line):
  for chr in line:
    #if chr is none of
    if (not (chr.isalnum() or chr == "." or chr == "-")):
      return False
  return True



if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Generate an Ansible inventory file using a list of hosts and a YAML and regexp template')
  parser.add_argument("--hosts", "-i", type=str, help="file where each line is a DNS name");
  parser.add_argument("--template", "-t", type=str, help="YAML file that defines how to parse the hosts");
  parser.add_argument("--out-format", "-f", type=str, help="output format of inventory; one of ini, yaml, json");
  args = parser.parse_args()

  missing_option = False

  if (args.hosts is None):
    print("specify a file of hosts to parse")
    missing_option = True
  if (args.template is None):
    print("specify a template file to parse the hosts")
    missing_option = True

  if (missing_option):
    print("-h for help")
    exit(1)

  main(args.hosts, args.template, args.out_format);
