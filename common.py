import sublime
import sublime_plugin

import re
from types import LambdaType

try:
  from Expression import expression
except ImportError as error:
  sublime.error_message("Dependency import failed; please read readme for " +
   "Formatter plugin for installation instructions; to disable this " +
   "message remove this plugin; message: " + str(error))
  raise error

# todo inline blocks endings: f() { f() }
# todo inline conditions: a ? b : c
# todo minus and plus operator: f(-a), a / -b

# hope this shit will not work slow on large files...
def format_view(view, edit):
  replacement = [

    # trailing spaces
    r'([ \t]+)(?=\n)',

    # trailing new lines at the end of file
    r'(\s+)$',

    # before commas: a1, a2
    r'([ \t]+)(?=,)',

    # short plus and minus with bracket (slow): f(-a)
    {
      'expression': r'[({\[]([\t ]*)[+\-]([\t ]*)[\w$@({\[\'"]',
      'groups': 2,
      'replacements': ['', ''],
    },

    # short plus and minus with operator (slow): a1 / -a2
    {
      'expression': r'(?<![\w)}\]\s\'"])(?<!\w[!?])([\t ]*)[+-]([\t ]*)' +
        r'[\w$@({\[\'"]',
      'groups': 2,
      'replacements': [' ', ''],
    },

    # brackets start f()
    r'[(\[]([ \t]+)(?=\S(?<!\|))',

    # remove comma at the end of nesting without new line
    r'(,[ \t]*)(?=[)}\];])',

    # brackets end [a, b] and semicolon f();
    r'(?<=\S)([ \t,]+)(?=[)\];])',

    {
      'expression': r'\w(?<![^\w]or)(?<![^\w]and)(?<![^\w]not)(?<![^\w]if)' +
      r'(?<![^\w]while)(?<![^\w]unless)(?<![^\w]return)([ \t]+)(?=\()',
    },

    # block args: { |a1, a2|
    {
      'expression': r'\{\s*\|(\s*)[\w,()\s]+(?<=[\w)])(\s*)\|',
      'groups': 2,
    },

    # double spaces to one space: v1 + v2
    {
      'expression': r'(?<=\S)([ \t]{2,})(?=\S)',
      'replacements': [' '],
    },

    # after commas: a1, a2
    {
      'expression': r',((?!\s))(?!\n)',
      'replacements': [' '],
    },

    # blocks: function f() {
    {
      'expression': r'(?:[)\w]|\w[!?])((?!\s)|\n|\s{2,})(?=\{)',
      'replacements': [' '],
      'scopes': [r'source\.(?!php)'],
    },

    # php: class ... {
    {
      'expression': r'(?:\n|^)\s*(?:class|trait).*?([ \t]|\s{2,})\{(?!\})',
      'replacements': ["\n"],
      'scopes': [r'source\.php'],
    },

    # php: function ... {
    {
      'expression': r'(?:\n|^)([ \t]*)(?:public|private|protected|final).*?\w+\(.*?\)(\s*){',
      'replacements': [None, "\n$0"],
      'groups': 2,
      'scopes': [r'source\.php', r'source\.php'],
    },

    # block args: { |a1, a2|
    {
      'expression': r'\{(\s*)\|[\w,()\s]+\|([ \t]*)',
      'groups': 2,
      'replacements' : [' ', ' '],
    },

    # after colon 'v1': 'v2'
    {
      'expression': r'["\'\w]:((?!\s))(?![\n:])',
      'scopes': [r'source\.(?!css)(?!.*source)'],
    },

    # before operator: a * b
    {
      'expression': r'(?:[\w)}\]]|\w[!?])((?!\s))' +
        r'(?=(?:[+\-*/=><%^&]|&&|\|\||\*\*)[\s\w$@({\[\'"])',
      'replacements': [' '],
      'scopes': [r'^(?!=.*meta)']
    },

    # after operator: a * b
    {
      'expression': r'(?<=[\s\w)}\]!?])' +
        r'(?:[+\-*/=><%^&]|&&|\|\||\*\*)((?!\s))' +
        r'(?=[\w$@{(\[\'"])',
      'replacements': [' '],
      'scopes': [r'^(?!=.*meta)']
    },

    # lines doubles
    {
      'expression': r'(\n\s*\n\s*\n)',
      'replacements': ["\n\n"],
    },

  ]

  _replace_spaces(view, edit, replacement)

def _replace_spaces(view, edit, replacements):
  expressions, scope_lambdas, scopes, replacing = [], [], [], []

  global_index = 1
  for replacement in replacements:
    if not isinstance(replacement, dict):
      replacement = {'expression': replacement}

    expressions.append(replacement['expression'])

    if 'scope_lambdas' in replacement:
      scope_lambdas += replacement['scope_lambdas']
    else:
      scope_lambdas += [None] * replacement.get('groups', 1)

    if 'scopes' in replacement:
      for scope in replacement['scopes']:
        scopes.append(re.compile(scope))
    else:
      scopes += [None] * replacement.get('groups', 1)

    if 'replacements' in replacement:
      for replacement_value in replacement['replacements']:
        has_expression = (
          replacement_value != None and
          re.search(r'\$\d+', replacement_value) != None
        )

        if has_expression:
          replacement_value = {
            'replacement': re.sub(
              r'(\$(\d+))',
              lambda match: '$' + str(int(match.group(2)) + global_index),
              replacement_value
            ),
            'has_expression': True,
          }

        replacing.append(replacement_value)
    else:
      replacing += [''] * replacement.get('groups', 1)

    global_index += replacement.get('groups', 1)

  # "'string': True, 'comment': True" is for lesser view.scope_name requests
  options = {'nesting': True, 'string': True, 'comment': True}
  regexp = r'|'.join(expressions)

  text = view.substr(sublime.Region(0, view.size()))
  matches = re.finditer(regexp, text)

  for match in reversed(list(matches)):
    if match.lastindex == None:
      continue

    for index in reversed(range(0, match.lastindex)):
      if match.group(index + 1) == replacing[index] or replacing[index] == None:
        continue

      match_start = match.start(index + 1)
      if match_start == -1:
        continue

      scope_left = view.scope_name(match_start - 1)
      scope_right = view.scope_name(match_start)
      scope_name_invalid = (
        'source' not in scope_right or
        ('comment' in scope_right and 'comment' in scope_left) or
        ('symbol' in scope_right and 'symbol' in scope_left) or
        ('string' in scope_right and 'string' in scope_left)
      )
      if scope_name_invalid:
        continue

      scope = scopes[index]
      if scope != None and re.search(scope, scope_right) == None:
        continue

      scope_lambda = scope_lambdas[index]
      if scope_lambda != None and not scope_lambda(scope_right):
        continue

      region = sublime.Region(match_start, match.end(index + 1))
      replacement = replacing[index]
      if isinstance(replacement, dict):
        if replacement['has_expression']:
          replacement = re.sub(
            r'(\$(\d+))',
            lambda local_match: match.group(int(local_match.group(2))),
            replacement['replacement']
          )
        else:
          replacement = replacement['replacement']

      view.replace(edit, region, replacement)

class RemoveExcessSpaces(sublime_plugin.TextCommand):
  def run(self, edit):
    remove_excess_spaces(self.view, edit)