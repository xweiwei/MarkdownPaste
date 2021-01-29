import os
import datetime
import subprocess
import re
import urllib

import sublime
import sublime_plugin

class MarkdownPasteCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    syntax = self.view.settings().get('syntax')
    if 'Markdown' != syntax.split('/')[1]:
      if sublime.ok_cancel_dialog('file is not markdown, continue parse?', 'Continue') is not True:
        return

    url = self.get_url()
    if url:
      self.paste_url(edit, url)
    else:
      self.paste_image(edit)


  def get_url(self):
    text = sublime.get_clipboard()
    if re.match(r'^https?:/{2}\w.+$', text):
      return text
    return None

  
  def paste_image(self, edit):
    edit_file_name = self.view.file_name()
    if edit_file_name is None:
      sublime.error_message('file does not exist, please save')
      return

    edit_file_dir = os.path.dirname(edit_file_name)
    img_dir = '{}/imgs/'.format(edit_file_dir)
    img_dir_exist = False
    if os.path.exists(img_dir):
      img_dir_exist = True
    if not os.path.isdir(img_dir) and img_dir_exist:
      sublime.error_message('{} is not dir, image can not to save'.format(img_dir))
      return

    desc = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = '{}.png'.format(desc)
    if os.name == "posix":
      img_path = '{}/{}'.format(img_dir, file_name)
      if img_dir_exist:
        path = img_path
      else:
        path = '{}/{}'.format(edit_file_dir, file_name)
      # os.system("pngpaste '{}'".format(path))
      # print('save img to {}'.format(path))
      if subprocess.call(["pngpaste", path]) != 0:
        sublime.error_message('save png to {} error'.format(path))
        return

      if not img_dir_exist:
        os.mkdir(img_dir)
        if not os.path.isdir(img_dir):
          os.remove(path)
          sublime.error_message('mkdir {} failed'.format(img_dir))
          return

        os.rename(path, img_path)

        if not os.path.exists(img_path):
          os.removedirs(img_dir) 
          sublime.error_message('rename {} to {} error'.fomat(path, img_path))
          return
      img_path = './imgs/{}'.format(file_name)
      self.insert_img_tag(edit, desc, img_path)

  def insert_img_tag(self, edit, desc, img_path):
    img_tag = '![{desc}]({src})'.format(desc=desc, src=img_path)
    self.view.insert(edit, self.view.sel()[0].begin(), img_tag)

  def paste_url(self, edit, url):
    title = self.find_title(url)
    if title is None:
      title = ''
    self.insert_url_tag(edit, title, url)


  def find_title(self, url):
    title = None
    try:
      webpage = urllib.request.urlopen(url, timeout=0.5).read()
      title = webpage.decode('utf8').split('<title>')[1].split('</title>')[0]
      if title:
        import html
        parser = html.parser.HTMLParser()
        title = parser.unescape(title).strip()
    except Exception as e:
      print(e)
    return title

  def insert_url_tag(self, edit, desc, url):
    url_tag = '[{desc}]({src})'.format(desc=desc, src=url)
    self.view.insert(edit, self.view.sel()[0].begin(), url_tag)
