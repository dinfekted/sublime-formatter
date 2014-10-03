import sublime
import sublime_plugin

from Formatter import methods_lines
from Formatter import common
from Semicolon import semicolon
from WrapStatement import wrap_statement

import time

class FormatEnhanced(sublime_plugin.TextCommand):
  def run(self, edit):
    common.format_view(self.view, edit)
    methods_lines.set(self.view, edit)
    semicolon.add_all(self.view, edit)
    # wrap_statement.rewrap_long_lines(self.view, edit)

class AutoFormat(sublime_plugin.EventListener):
  def __init__(self):
    super().__init__()

  def on_pre_save(self, view):
    settings = sublime.load_settings('FormatEnhanced.sublime-settings')
    if not settings.get('auto', False):
      return

    view_size_limit = settings.get('view_size_limit', None)
    if view_size_limit != None and view.size() > view_size_limit:
      return

    view.run_command('format_enhanced')