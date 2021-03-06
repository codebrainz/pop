#!/usr/bin/env python3

import jinja2
import optparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

class Operator:
  def __init__(self, id, name, token, arity, suffix):
    self.id = id
    self.name = name
    self.token = token
    self.arity = arity
    self.suffix = suffix

class Node:
  def __init__(self, name, fields=[], is_atom=False):
    self.name = name
    self.fields = fields
    self.is_atom = is_atom
  @property
  def child_fields(self):
    return [ field for field in self.fields if field.child ]
  @property
  def construct_fields(self):
    return [ field for field in self.fields if field.construct ]
  @property
  def has_scope(self):
    return any(field.name == "scope" and field.type == "SymbolTable"
      for field in self.fields)
  @property
  def first_child(self):
    return self.child_fields[0]
  @property
  def last_child(self):
    return self.child_fields[-1]

class Field:
  def __init__(self, name, type, construct, child, default):
    self.name = name
    self.type = type
    self.construct = construct
    self.child = child
    self.default = default

class Instruction:
  def __init__(self, name, mnemonic, fields=[], size=1):
    self.name = name
    self.mnemonic = mnemonic
    self.fields = fields
    self.size = size
  @property
  def node_fields(self):
    return [ f for f in self.fields if f.type == "Node*" ]
  @property
  def construct_fields(self):
    return [ f for f in self.fields if f.construct ]

class InstructionField:
    def __init__(self, name, type, construct=True, default=None):
      self.name = name
      self.type = type
      self.construct = construct
      self.default = default

def parse_operators(root):
  operators = []
  for elem in root.iterfind('operators/operator'):
    operators.append(Operator(
      elem.attrib['id'],
      elem.attrib['name'],
      elem.attrib['token'],
      int(elem.attrib['arity']),
      True if elem.attrib.get('suffix', 'no') in [ 'yes', 'true' ] else False
    ))
  return operators

def parse_nodes(root):
  nodes = []
  for node_elem in root.iterfind('nodes/node'):
    name = node_elem.attrib['name']
    fields = []
    for field_elem in node_elem.iterfind('field'):
      fields.append(Field(
        field_elem.attrib['name'],
        field_elem.attrib.get('type', 'Node*'),
        False if field_elem.attrib.get('construct', 'yes') in [ 'no', 'false' ] else True,
        True if field_elem.attrib.get('child', 'no') in [ 'yes', 'true']
          else field_elem.attrib.get('type', 'Node*') == 'Node*',
        field_elem.attrib.get('default', None)
      ))
    nodes.append(Node(name, fields,
      True if node_elem.attrib.get('atom', 'false')
        in [ 'yes', 'true' ] else False))
  return nodes

def parse_instructions(root):
  instructions = []
  for node_elem in root.iterfind('instructions/node'):
    name = node_elem.attrib['name']
    mnemonic = node_elem.attrib.get('mnemonic', None)
    size = int(node_elem.attrib.get('size', '1'))
    fields = []
    for field_elem in node_elem.iterfind('field'):
      fields.append(InstructionField(
        field_elem.attrib['name'],
        field_elem.attrib['type'],
        True if field_elem.attrib.get('construct', "true") in [ "yes", "true" ] else False,
        field_elem.attrib.get('default', None)
      ))
    instructions.append(Instruction(name, mnemonic, fields, size))
  return instructions

def do_format(fn):
  def can_format():
    if fn == '-':
      return False
    try:
      with open(os.devnull) as nulfile:
        subprocess.call([ "clang-format", "--version"], stdout=nulfile, stderr=nulfile)
      return os.path.exists(os.path.join(os.path.dirname(__file__), "..", ".clang-format"))
    except FileNotFoundError as e:
      return False
  if can_format():
    subprocess.call([ "clang-format", "-i", "-style=file", fn ])

def main(args):
  par = optparse.OptionParser()

  par.add_option('-d', '--data', metavar='FILE', dest='data_fn',
    help='the xml data file')
  par.add_option('-o', '--output', metavar='FILE', dest='out_fn',
    default='-', help="the file to write (default '-' for stdout)")

  opts, args = par.parse_args(args[1:])

  data_fn = opts.data_fn
  out_fn = opts.out_fn
  in_fns = args

  xml_root = ET.ElementTree(file=data_fn)
  out_file = open(out_fn, 'w') if out_fn != '-' else sys.stdout

  operators = parse_operators(xml_root)
  nodes = parse_nodes(xml_root)
  instructions = parse_instructions(xml_root)

  in_files = []
  if len(in_fns) == 0:
    in_files.append( ('<stdin>', sys.stdin) )
  else:
    in_files.extend( (fn, open(fn)) for fn in in_fns )

  for fn, f in in_files:
    t = jinja2.Template(f.read())
    s = t.render(fn=fn, operators=operators, nodes=nodes, instructions=instructions)
    com = '// This file is auto-generated from %s, do not edit.\n' % fn
    out_file.write(com + s.rstrip() + '\n')

  if out_fn != '-':
    out_file.close()

  do_format(out_fn)

  return 0

if __name__ == "__main__":
  sys.exit(main(sys.argv))
