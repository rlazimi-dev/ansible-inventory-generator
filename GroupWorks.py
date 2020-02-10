import re;


'''
(TODO) remove avoidable loops (e.g. the match_to_* loops)

@group_temp:

<group>:
  hosts:
    <dnsname>:
    ...

  children:
    <child name>:
      <nested child name>:
      ...
...

@potential_hosts: dict; become hosts of group based on the group template's hosts <regexp>
!return: JSON such that all hosts satisfy the host <regexp> and children such that all children were defined by recursive calls
'''

def build_group(group_temp, potential_hosts):

  # recursive formulation:
  # when calling on children, return a JSON object where each key maps to a valid group definition;
  # what's left is to define the hosts for each of the current groups in group_temp (before recursion);
  # what's left is to define the current JSON represented by the template

  template_as_json = {};

  for group_name in group_temp:
    group = group_temp[group_name]; 

    host_regexps = group.get("hosts",{});
    children = group.get("children",{});
    vars = group.get("vars",{});

    #---parse current hosts---
    # capture any potential host that matches any of the regexps

    current_hosts = {};

    for host_regexp in host_regexps:
      for host in potential_hosts:
        if (re.search(host_regexp, host)):
          current_hosts[host] = potential_hosts[host];


    #---expand child regexp into valid templates---
    # handle both literally defined children and regexp children
    # literal child is any template that has a "hosts" key
    # note: no regexp expansion for a group if hosts defined

    expanded_children = {};

    for child_name in children:
      is_literal_child = children[child_name] is not None and children[child_name].get("hosts",None) is not None;
      is_regexp = not is_literal_child;

      if (is_literal_child):
        expanded_children[child_name] = children[child_name];

      elif (is_regexp):
        child_regexp = child_name;

        is_nested_regexp = children[child_regexp] is not None and (children[child_regexp].get("children",None) is not None and children[child_regexp].get("hosts",None) is None);
    
        nth_match = 0;
        if (children[child_regexp] is not None):
          nth_match = children[child_regexp].get("nth_match",0);
    
        for host in current_hosts:
          match_list = re.findall(child_regexp, host)
          if (nth_match < len(match_list)):
            match_name = match_list[nth_match];
            try:
              expanded_children[match_name]["hosts"][host] = current_hosts[host];
            except:
              expanded_children[match_name] = {
                "hosts":  { host: current_hosts[host] },
                "children": children[child_name]["children"] if is_nested_regexp else {}
              };



    #---parse children (recursively)---
    parsed_children = build_group(expanded_children, current_hosts);

    template_as_json[group_name] = {};

    if (len(current_hosts) > 0):
      template_as_json[group_name]["hosts"] = current_hosts;
    if (len(parsed_children) > 0):
      template_as_json[group_name]["children"] = parsed_children;
    if (len(vars) > 0):
      template_as_json[group_name]["vars"] = vars;

  return template_as_json;





"""
@inv_json:
{
  <group_name>: {
    "hosts": {...},
    "children": {...},
  }
}
!return: string in ini format
"""

def to_ini(inv_json):
    # when calling "children", return children as ini string
    # what's left is to append "hosts" to [<group_name>] and to append child string to [<group_name>:children]

    group_string = "";

    for group_name in inv_json:
      group = inv_json[group_name];
      group_string += "[" + group_name + "]";

      for host_key in group["hosts"]:
        group_string += "\n" + host_key;

      children = group.get("children",{});
      group_string += "\n";
      group_string += "\n";
      group_string += "[" + group_name + ":children]" if len(children) > 0 else "";
      for child_name in children:
        group_string += "\n" + child_name;

      group_string += "\n";
      group_string += "\n";
      group_string += to_ini(children);

    return group_string;
