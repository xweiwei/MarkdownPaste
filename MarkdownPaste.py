import os
import datetime
import subprocess

import sublime
import sublime_plugin

class MarkdownPasteCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    syntax = self.view.settings().get('syntax')
    if 'Markdown' != syntax.split('/')[1]:
      if sublime.ok_cancel_dialog('file is not markdown, continue parse image?', 'Continue') is not True:
        return

    edit_file_name = self.view.file_name()
    if edit_file_name is None:
      sublime.error_message('file does not exist, please save')
      return

    edit_file_dir = os.path.dirname(edit_file_name)
    img_dir = '{}/_images/'.format(edit_file_dir)
    if os.path.isdir(img_dir) is not True:
      os.makedirs(img_dir)

    desc = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = '{}.png'.format(desc)
    if os.name == "posix":
      path = '{}/{}'.format(img_dir, file_name)
      # os.system("pngpaste '{}'".format(path))
      if subprocess.call(["pngpaste", path]) != 0:
        sublime.error_message('save png error')
        return
      img_path = '_images/{}'.format(file_name)
      self.insert_img_tag(edit, desc, img_path)
    

  def insert_img_tag(self, edit, desc, img_path):
    img_tag = '![{desc}]({src})'.format(desc=desc, src=img_path)
    self.view.insert(edit, self.view.sel()[0].begin(), img_tag)

