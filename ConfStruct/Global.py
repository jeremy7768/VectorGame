# vim:encoding=utf-8:ts=2:sw=2:expandtab
# vim:syntax=python


###############################################################################
# **Global** > Local > Global > User > System > User > Global > Local > OUTPUT


class ID(ProjectIdentifier):
  pass

class DevLevel(Integer):
  Description = 'Development level: 0=Production, 1=Preview, 2=Development'

class Postgres(Postgres):
  pass

class Redis(Redis):
  pass

class Main(Site, SSLSite, SiteProxy, WSGIProcessGroup):
  Description = 'Main Site.'


yield
###############################################################################
# Global > Local > **Global** > User > System > User > Global > Local > OUTPUT

import re

ID = 'VectorGame'

match = re.search('DevLevel\\.([0-9])', Path)
if match:
  DevLevel = int(match.group(1))

yield
###############################################################################
# Global > Local > Global > User > System > User > **Global** > Local > OUTPUT

# --
if Postgres.Database is None and DevLevel is not None:
  Postgres.Database = ID + '_' + str(DevLevel)

if Postgres.Username is None:
  Postgres.Username = ID

# --
if Main.ServerName is None:
  Main.ServerName = DomainConverter.LiveToDev('play.gahooa.com')

if Main.SSLServerName is None:
  Main.SSLServerName = Main.ServerName

if Main.URL is None and Main.ServerName is not None:
  Main.URL = 'http://' + Main.ServerName

if Main.SSLURL is None and Main.SSLServerName is not None:
  Main.SSLURL = 'https://' + Main.SSLServerName


yield
###############################################################################
# Global > Local > Global > User > System > User > Global > Local > **OUTPUT**
# Only called if there were not validation errors

from os.path import join


WriteFile('{0}-{1}-{2}-nginx.conf'.format(ID, User, DevLevel), '''
server
{
  listen ''' + Main.IP + ''':''' + str(Main.Port) + ''';
  listen ''' + Main.SSLIP + ''':''' + str(Main.SSLPort) + ''' ssl;
  server_name ''' + Main.ServerName + ''';
  ''' + ('''
  server_name ''' + Main.SSLServerName + ''';
  ''' if Main.ServerName != Main.SSLServerName else '') + '''

  ssl_certificate     ''' + Main.SSLCrt + ''';
  ssl_certificate_key ''' + Main.SSLKey + ''';

  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header Scheme $scheme;

  client_max_body_size 1000m;

  location ~ \.(py|pyc|pyo|wsgi)$
  {
    return 403;
  }

  location ~ \.([a-zA-Z0-9])+$
  {
    root  ''' + join(Path, 'Web', 'Main') + ''';
    ''' + ('''
    expires max;
    ''' if DevLevel in (0, 1) else '''
    add_header Cache-Control 'no-cache, no-store, max-age=0, must-revalidate';
    add_header Expires 'Thu, 01 Jan 1970 00:00:01 GMT';
    ''') + '''
  }

  location /
  {
    add_header Cache-Control 'no-cache, no-store, max-age=0, must-revalidate';
    add_header Expires 'Thu, 01 Jan 1970 00:00:01 GMT';
    proxy_pass http://''' + Main.ProxyIP + ''':''' + str(Main.ProxyPort) + ''';
  }
}
''', 'nginx') 

# Write the apache file

WriteFile('{0}-{1}-{2}-httpd.conf'.format(ID, User, DevLevel), '''

#================================================================================================
# Main

WSGIDaemonProcess Port''' + str(Main.ProxyPort) + ''' processes=''' + str(Main.Processes) + ''' threads=''' + str(Main.Threads) + ''' python-path=''' + join(Path, 'Python') + '''
Listen ''' + Main.ProxyIP + ''':''' + str(Main.ProxyPort) + '''
NameVirtualHost ''' + Main.ProxyIP + ''':''' + str(Main.ProxyPort) + '''

<VirtualHost ''' + Main.ProxyIP + ''':''' + str(Main.ProxyPort) + '''>
  ServerName _default_
  DocumentRoot ''' + join(Path, 'Web', 'Main') + '''
  AddDefaultCharset UTF-8

  RewriteEngine on
  RewriteOptions inherit

  # Forbid any python source files from being served.
  RewriteRule \.(py|pyc|pyo|wsgi)$  -  [F]

  WSGIScriptAlias / ''' + join(Path, 'Web', 'Main', '__init__.wsgi') + '''
  WSGIProcessGroup Port''' + str(Main.ProxyPort) + '''

  LogLevel info
  ErrorLog ''' + join(Path, 'apache-error.log') + '''
</VirtualHost>


''', 'httpd')

#==================================================================================================
# Write the local settings file
import time

WriteFile('Python-Project-Local.py', '''
# Generated by AutoConf system

DevLevel = ''' + repr(DevLevel) + '''
Identifier = ''' + repr(ID) + '''
Path = ''' + repr(Path) + '''

Postgres = ''' + repr(Postgres) + '''

Redis = ''' + repr(Redis) + '''

Main_HTTP_URL = ''' + repr(Main.URL) + '''
Main_HTTPS_URL = ''' + repr(Main.SSLURL) + '''

CacheTime = ''' + repr(str(int(time.time()))) + '''

''')

