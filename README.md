# Python-White-Bear-Editor

White-bear website editor written in Python 3.

#### Uses:

- wxPython 4.1.1
- GNOME icons under GNU General Public License version 2. https://commons.wikimedia.org/wiki/GNOME_Desktop_icons

### Goals:

- Generate fast static html5 pages from easily written text.
- Generate robots.txt and sitemap.xml.
- CSS3 Styles separated from content.
- Easy page deployment onto server with one button.
- Automatically generate index page.
- Automatically generate menu pages.
- Check common SEO issues.
- Use HTML structure set by the original handwritten white-bear pages.
- Simplify adding/converting various types of text and side images and article icons.
- Simplify article logo management.
- Validate pages against xsd templates.
- Include SFTP client for fast page upload.
- Spell check all texts and perform rule check on all website parts.

#### Fedora development/run requirements:

- sudo yum install python3-wxpython4 gcc gcc-c++ gtk3 gtk3-devel python3-devel python3-html5lib python3-webcolors python3-pendulum python3-paramiko
- sudo pip3 install tinycss
- sudo pip3 install htmlmin

#### Pycharm package requirements (install Fedora development requirements before):
- wxPython