import sublime
import sublime_plugin

from Expression import expression
from Method import method
from Statement import statement
import re

def set(view, edit):
  methods = method.extract_methods(view)
  edit_point = None
  view_size = view.size()
  for current_method in reversed(methods):
    _, region, _ = method.get_regions(view, current_method)

    region_value = view.substr(region)

    if (edit_point == None or region.b < edit_point):
      _set_following_spaces(view, edit, view_size, region, region_value)

    _set_method_endings(view, edit, current_method)
    _set_method_starts(view, edit, current_method)

    if 'python' not in view.scope_name(region.a):
      edit_point = _set_preceding_spaces(view, edit, region, region_value)

def _set_preceding_spaces(view, edit, region, region_value):
  before_match = re.search(r'^(\s*\n)?[ \t]*\S', region_value)
  if before_match.group(1) == "\n":
    return

  if before_match.end(1) == -1:
    view.insert(edit, region.a, "\n")
  else:
    before = sublime.Region(region.a, region.a + before_match.end(1))
    view.replace(edit, before, "\n")

  return region.a

def _set_following_spaces(view, edit, view_size, region, region_value):
  after_match = re.search(r'(\s*)$', region_value)
  if after_match.group(1) == "\n\n":
    return

  end = region.a + after_match.end(1)
  if end >= view_size:
    return end

  after = sublime.Region(region.a + after_match.start(1), end)
  view.replace(edit, after, "\n\n")

def _set_method_starts(view, edit, current_method):
  header = [current_method['start'], current_method['body_start']]

  match = expression.find_match(view, current_method['body_start'], r'(\s*)$',
    {'range': header, 'backward': True})

  if match == None:
    return match

  shift = match.start(1) + current_method['start']
  header[1] = shift

  match = expression.find_match(view, shift, r'^(\s+)\n[ \t]*\S', {'nesting': True,
    'range': [shift, current_method['end']]})

  if match == None:
    return

  replacement = ''
  if "\n" in view.substr(sublime.Region(*header)):
    replacement = "\n"

  region = sublime.Region(match.start(1) + shift, match.end(1) + shift)
  print(match.start(1) + shift, match.end(1) + shift)
  if match.group(1) == replacement:
    return

  view.replace(edit, region, replacement)

def _set_method_endings(view, edit, current_method):
  if current_method['end'] == current_method['body_end']:
    return

  shift = current_method['body_start']
  options = {'nesting': True, 'range': [shift, current_method['end']]}
  match = expression.find_match(view, shift, r'(\s+)\n\s*\S+$', options)
  if match == None:
    return

  region = sublime.Region(match.start(1) + shift, match.end(1) + shift)
  view.replace(edit, region, "")

class RemoveExcessLines(sublime_plugin.TextCommand):
  def run(self, edit):
    remove_excess_lines(self.view, edit)