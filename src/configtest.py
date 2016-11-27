import os
from yaml import load
baseconfig = r'''general:
  serve-dir: "."
  port: 80
  server-address: "localhost"
  php-cgi-exec: "/PHP/php-cgi.exe"
  allow-post: True
  https: False
  logging: "%H:%M:%S [%T] %A: %i"
cgi:
  regex-is-cgi: ".*\\.php"
  server-admin: "support@gmail.com"
  external-ip:
    use-internet: True
    override: ""


# logging:
#  %T: type - enum - INFO, ERROR, WARN
#  %A: client IP address
#  %H: hour - 24, 0 padded
#  %h: hour - 24, non 0 padded
#  %G: hour - 12, 0 padded
#  %g: hour - 12, non 0 padded
#  %M: minute - 0 padded
#  %m: minute - non 0 padded
#  %S: second - 0 padded
#  %s: second - non 0 padded
#  %t: time - enum - PM, AM
#  %L: month - 0 padded
#  %l: month - non 0 padded
#  %D: day - 0 padded
#  %d: day - non 0 padded
#  %Y: year - 4 digits
#  %y: year - 2 digits: 16 = 2016
#  %i: message
#  %%: literal % sign
'''
def test():
    if not os.path.exists('config.yml'):
        create()
        return True
    try:
        return True
    except Exception:
        return False
def create():
    f = open('config.yml','w')
    f.write(baseconfig)
    f.close()

class config():
    def __init__(self):
        x = open('config.yml')
        config = x.read()
        x.close()
        self.config = load(config)

        self._general = self.config['general']
        self.serve_dir = self._general['serve-dir']
        self.https = self._general['https']
        self.port = self._general['port']
        self.server_address = self._general['server-address']
        self.php_dir = os.path.abspath(self._general['php-cgi-exec'])
        self.allow_post = self._general['allow-post']
        self.logging = self._general['logging']

        self._cgi = self.config['cgi']
        self.use_internet_for_ip = self._cgi['external-ip']['use-internet']
        self.external_ip = self._cgi['external-ip']['override']
        self.server_admin = self._cgi['server-admin']
        self.cgi_check_regex = self._cgi['regex-is-cgi']
