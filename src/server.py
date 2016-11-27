from http.server import *
import os, subprocess, socket, urllib.request, re, base64, time, sys, datetime
version = "1.0"
title = "Horse %s"%version
CONFIGURATION, public_ip, cgi_path_match = None, None, None
def setup(CONFIGURATIO):
    global CONFIGURATION, public_ip, cgi_path_match
    CONFIGURATION = CONFIGURATIO
    if CONFIGURATION.use_internet_for_ip:
        public_ip = urllib.request.urlopen('http://ip.42.pl/raw').read().decode()
    else:
        public_ip = CONFIGURATION.external_ip
    authregex = re.compile('(\w+)[:=] ?"?(\w+)"?')
    cgi_path_match = re.compile(CONFIGURATION.cgi_check_regex)
def stop(*toggleserver):
    if 'httpd' in globals():
        global httpd
        try:
            httpd.shutdown()
        except Exception: tprint("Server could not shutdown.")
        try:
            httpd.server_close()
        except Exception: tprint("Server could not close.")
        del httpd
    tprint("Server stopped successfully.")
    if not toggleserver == ():
        toggleserver[0]['text'] = 'Start Server'
        toggleserver[0]['state'] = 'normal'

def format_stderr(stderr):
    if stderr:return '<div id="errors"><pre style="background-color:#eeefff">\n'+stderr.decode()+'\n</pre></div>'
    else: return ''
def tprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#def print_error(typ,)
class CustomServer(HTTPServer):
    pass


class CustomHandler(CGIHTTPRequestHandler):
    def do_POST(self):
        if self.is_cgi():
            #self.cgi_info = path
            self.run_cgi()
        else:
            if CONFIGURATION.allow_post:
                return SimpleHTTPRequestHandler.do_POST(self)
            else:
                self.send_error(501, "Can only POST to CGI scripts")

    def send_head(self):
        if self.is_cgi():
            self.run_cgi()
        else:
            return SimpleHTTPRequestHandler.send_head(self)

    def do_GET(self):
        if self.is_cgi():
            self.run_cgi()
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def is_cgi(self):
        if (cgi_path_match.match(self.path) and os.path.exists(os.getcwd()+self.path)):
            return True
        return False 

    def run_cgi(self):
        t = time.time()
        headers = dict(self.headers)
        #TODO: ADD CONTENT_LENGTH, CONTENT_TYPE, REMOTE_USER/REDIRECT_REMOTE_USER (added but need funtionality)
        env = os.environ.copy()
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        #env['PATH_INFO'] = ''#urllib.parse.unquote(self.path.split('/')[-1])
        env['PATH_TRANSLATED'] = os.path.abspath(self.path[1:])#.replace('\\', '/')
        if '?' not in self.path:
            env['QUERY_STRING'] = ''
        else:
            env['QUERY_STRING'] = self.path.split('?')[-1]
        env['REMOTE_ADDR'] = self.client_address[0]
        env['REMOTE_HOST'] = socket.gethostbyaddr(env['REMOTE_ADDR'])[0]
        env['REMOTE_USER'] = ''
        env['REDIRECT_REMOTE_USER'] = ''
        env['SCRIPT_FILENAME'] = env['PATH_TRANSLATED']
        env['SERVER_ADMIN'] = CONFIGURATION.server_admin #FIX (not needed technically, only Apache sets this using the configuration of it) (email for webmaster)
        env['SERVER_PORT'] = str(self.server.server_port)
        env['SERVER_SIGNATURE'] = '' #use in config.... this is the "footer" for each page
        env['SERVER_ADDR'] = public_ip #gets server's external ip
        env['SERVER_SOFTWARE'] = title
        env['SERVER_PROTOCOL'] = self.protocol_version
        env['REQUEST_METHOD'] = self.command
        env['REQUEST_TIME'] = str(int(t))
        env['REQUEST_TIME_FLOAT'] = str(t)
        env['DOCUMENT_ROOT'] = os.getcwd()
        env['HTTP_ACCEPT'] = headers.get('Accept','')
        env['HTTP_ACCEPT_CHARSET'] = headers.get('Accept-Charset','')
        env['HTTP_ACCEPT_ENCODING'] = headers.get('Accept-Encoding','')
        env['HTTP_ACCEPT_LANGUAGE'] = headers.get('Accept-Language','')
        env['HTTP_CONNECTION'] = headers.get('Connection','')
        env['HTTP_HOST'] = headers.get('Host','')
        env['HTTP_REFERER'] = headers.get('Referer','')
        env['HTTP_USER_AGENT'] = headers.get('User-Agent','')
        env['HTTPS'] = '1' if CONFIGURATION.https else '' #should be empty if through http, and some non-empty value if yes
        env['SCRIPT_NAME'] = "/".join(env['PATH_TRANSLATED'].split('/')[:-1])
        env['REQUEST_URI'] = self.path
        env['REDIRECT_STATUS'] = '1'
        if headers.get('Authorization',''):
            if dict(authregex.findall(headers['Authorization']))['Authorization'] == "Digest":
                env['PHP_AUTH_DIGEST'] = " ".join(headers.get('Authorization').split()[1:])
            elif headers['Authorization'].split() == "Basic":
                env['PHP_AUTH_USER'], env['PHP_AUTH_PW'] = base64.b64decode(headers['Authorization'].split()[1]).split(":")
            env['AUTH_TYPE'] = headers['Authorization'].split()[0]


        cmdline = [CONFIGURATION.php_dir,os.path.abspath(os.getcwd()+self.path)]
        #self.log_message("command: %s", subprocess.list2cmdline(cmdline))
        p = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdout, stderr = p.communicate()

        self.output = stdout.decode()+format_stderr(stderr)

        p.stderr.close()
        p.stdout.close()
        self.wfile.write(self.output.split('\r\n\r\n',1)[1].encode())
            
    def end_headers(self):
        if self.is_cgi():
            self.run_cgi()
            for header in self.output.split('\r\n\r\n',1)[0].split('\r\n'):
                h = header.split(': ',1)
                self.send_header(h[0],h[1])
        SimpleHTTPRequestHandler.end_headers(self)

    def log_request(self, code='', size=''):
        self.log_message(0,'"%s" %s %s'%(self.requestline, code, size),str(code))
    def log_error(self, format, *args):
        if format == 'code %d, message %s' and args[0] == 404: return
        self.log_message(1,format%args)
    def log_message(self, type, message, *args):
        if type == 0:
            if args[0][0] in ['1','2']:
                typ = 'INFO'
            elif args[0][0] == '3':
                typ = 'WARN'
            elif args[0][0] in ['4','5']:
                typ = 'ERROR'
            else:
                typ = 'MISC'
        else: typ = 'ERROR'
        rn = datetime.datetime.now()
        noon = 'PM' if int(rn.hour/12)==1 else 'AM'
        

        ret = CONFIGURATION.logging

        ret = ret.replace(r'%T',typ)
        ret = ret.replace(r'%A',self.address_string())
        ret = ret.replace(r'%H',self.padZero(rn.hour))
        ret = ret.replace(r'%h',str(rn.hour))
        ret = ret.replace(r'%G',self.padZero(rn.hour%12))
        ret = ret.replace(r'%g',str(rn.hour%12))
        ret = ret.replace(r'%M',self.padZero(rn.minute))
        ret = ret.replace(r'%m',str(rn.minute))
        ret = ret.replace(r'%S',self.padZero(rn.second))
        ret = ret.replace(r'%s',str(rn.second))
        ret = ret.replace(r'%t',noon)
        ret = ret.replace(r'%L',self.padZero(rn.month))
        ret = ret.replace(r'%l',str(rn.month))
        ret = ret.replace(r'%D',self.padZero(rn.day))
        ret = ret.replace(r'%d',str(rn.day))
        ret = ret.replace(r'%Y',str(rn.year))
        ret = ret.replace(r'%y',str(rn.year)[2:])
        ret = ret.replace(r'%i',message)
        ret = ret.replace(r'%%',r'%')
        #format = format.replace('%T')
        sys.stderr.write(ret+"\n")
        #self.address_string() = ip adress
        #self.log_date_time_string() = timestring (useless)
    def padZero(self,num):
        return '0'+str(num) if num<10 else str(num)
def run():
    global httpd
    try:
        httpd = CustomServer((CONFIGURATION.server_address, CONFIGURATION.port), CustomHandler)
    except OSError:
        tprint("There was an error in starting the web server. Maybe the port is being used or taken?")
        return
    tprint("Server started successfully.")
    httpd.serve_forever()
