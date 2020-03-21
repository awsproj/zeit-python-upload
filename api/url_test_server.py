#!/usr/bin/env python
#   url_test_server.py

from url_test_paths import HTTPHandler

import sys
if sys.hexversion < 0x03050000:
    sys.exit("Python 3.5 or newer is required to run this program.")

from http.server import HTTPServer
from urllib.parse import urlparse
import datetime
import os

port = 8000

url_base_path = '/storage'
local_base_path = 'url_www'
local_tmp_prefix = '/tmp' # only used on zeit server-less

def url_server_paths_set(svr): # only set on zeit server-less
    svr.local_base_path = local_tmp_prefix + '/' + local_base_path  # d:\\zeit_proj\\src\\url_www
    svr.url_base_path = local_base_path  # url_www

class urlTestHandler(HTTPHandler):

    # variables to reduce request logs
    cls_poll_demo_content_count = 0
    cls_poll_live_count = 0
    cls_disable_log_request = False

    # override BaseHTTPRequestHandler of BaseHTTPServer
    def log_request(self, code='-', size='-'):
        if urlTestHandler.cls_disable_log_request:
            urlTestHandler.cls_disable_log_request = False
        else:
            HTTPHandler.log_request(self, code=code, size=size)

    def __do_path_mapping_inject(self):
        # inject self.server.url_content on zeit-now server-less:
        if not hasattr(self.server, 'url_content'):
            try:
                from url_test_pub import urlTestPublisher
            except:
                sys.path.insert(0, 'api')
                from url_test_pub import urlTestPublisher
                del sys.path[0]
            self.server.url_content = urlTestPublisher(local_tmp_prefix)
            url_server_paths_set(self.server)

    def do_GET(self):
        def send_err(errc, msg):
            self.send_response(errc)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-control', 'no-cache')
            self.end_headers()
            # Send the html message
            self.wfile.write( ("<b> %s !</b>" % msg).encode() )
        path = self.path
        if path.startswith('/api'):
            urlobj = urlparse(path)
            query = urlobj.query

            self.__do_path_mapping_inject()

            if query == 'time':
                self.do_time()
            elif query.startswith('upload/'):
                # -------------------------------
                # /api/upload
                # -------------------------------
                self.do_command_upload()
            elif query.startswith('live/'):
                # -------------------------------
                # /api/live
                # -------------------------------
                urlTestHandler.cls_poll_live_count += 1
                if (urlTestHandler.cls_poll_live_count % 12) != 1:
                    urlTestHandler.cls_disable_log_request = True
                self.do_command_live()
            elif query.startswith('check/demo_content'):
                # -------------------------------
                # /api/check/demo_content
                # -------------------------------
                urlTestHandler.cls_poll_demo_content_count += 1
                if (urlTestHandler.cls_poll_demo_content_count % 12) != 1:
                    urlTestHandler.cls_disable_log_request = True
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                html_cont = self.server.url_content.updateContent()
                self.send_header('Content-length', "%d" % len(html_cont))
                self.send_header('Cache-control', 'private, max-age=0, no-cache')
                self.end_headers()
                # Send the html message
                self.wfile.write(html_cont.encode())
            elif query.startswith('check/'):
                # -------------------------------
                # /api/check
                # -------------------------------
                send_err(416, "/api/check: Range Not Satisfiable")
            elif query.startswith('media/askvcap/'):
                # ------------------------------
                # /api/media/askvcap/<seq>
                # -------------------------------
                arg_idx = query[len('media/askvcap/'):]
                rv = self.server.url_content.askvcap(arg_idx)

                if rv:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Cache-control', 'no-cache')
                    self.end_headers()
                    # Send the html message
                    self.wfile.write("server received ok")
                else:
                    send_err(416, "/api/media/askvcap/: Range Not Satisfiable")
            elif query.startswith('media/asklive/'):
                # -------------------------------
                # /api/media/asklive/<seq>
                # -------------------------------
                arg_idx = query[len('media/asklive/'):]
                rv = self.server.url_content.asklive(arg_idx)

                if rv:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Cache-control', 'no-cache')
                    self.end_headers()
                    # Send the html message
                    self.wfile.write("server received ok")
                else:
                    send_err(416, "/api/media/asklive/: Range Not Satisfiable")
            elif query.startswith('media/snapshot/'):
                # -------------------------------
                # /api/media/snapshot/<seq>/<snap_num>
                # -------------------------------
                arg_idx = query[len('media/snapshot/'):]
                rv = self.server.url_content.snapshot(arg_idx)

                if type(rv) is list and len(rv) == 2:
                    if type(rv[0]) is bool:
                        if rv[0]:
                            html_cont = rv[1]
                            self.send_response(200)
                            self.send_header('Content-type', 'image/jpeg')
                            self.send_header('Content-length', "%d" % len(html_cont))
                            self.send_header('Cache-control', 'no-cache')
                            self.end_headers()
                            # Send the html message
                            self.wfile.write(html_cont)
                        else:
                            send_err(416,
                                     "/api/media/snapshot/: Range Not Satisfiable 1 %s" % (
                                         rv[1]
                                     ))
                    else:
                        send_err(416, "/api/media/snapshot/: Range Not Satisfiable 2")
                else:
                    send_err(416, "/api/media/snapshot/: Range Not Satisfiable 3")
            elif query.startswith('storage'):
                # -------------------------------
                # /storage  1 of 3 handling paths
                # -------------------------------
                # list directory and file
                self.path = '/' + query
                return HTTPHandler.do_GET(self)
            elif query.startswith('test'):
                # -------------------------------
                # /test
                # -------------------------------
                send_err(200, "Test: Hellow World")
            else:
                send_err(416, "%s: Range Not Satisfiable" % path)

        ##elif path.startswith(self.server.url_base_path):
            # -------------------------------
            # /storage  2 of 3 handling paths
            # -------------------------------
            # list directory and file
            ##return HTTPHandler.do_GET(self)
        elif path.startswith('/' + local_base_path): # /url_www
            # -------------------------------
            # /storage  3 of 3 handling paths
            # -------------------------------
            # list directory and file
            self.path = self.server.url_base_path + path[len('/' + local_base_path):]
            return HTTPHandler.do_GET(self)
        else:
            # -------------------------------
            # /<any_other>
            # -------------------------------
            send_err(410, "Error code: 410 gone")

    def do_time(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.send_header('Cache-control', 'no-cache')
        self.end_headers()
        # Send the html message
        msg = "<b> Hello World !</b>\n" + \
                "<br /><br />\n<p>Current time: " + str(datetime.datetime.now()) + "</p>\n"
        self.wfile.write(msg.encode())

    def do_command_upload(self):
        psegs = self.path.split('/')
        if len(psegs) >= 4 and psegs[1] == 'api' and psegs[2] == 'upload' and psegs[3].isdigit():
            seqn = int(psegs[3])
            seqpath = "%s/upload/%d" % (self.server.local_base_path,seqn)
            if os.path.isdir(seqpath):
                missingfile = not os.path.isfile("%s/data_info" % seqpath)
                missingfile = not os.path.isfile("%s/data_chn0" % seqpath) or missingfile
                if os.path.isfile("%s/upload_req" % seqpath) and missingfile:
                    self.send_response(200) # ok
                else:
                    self.send_response(404)  # not found
            else:
                self.send_response(403) # forbidden
        else:
            self.send_response(400)  # bad request

    def do_command_live(self):
        psegs = self.path.split('/')
        if len(psegs) >= 4 and psegs[1] == 'api' and psegs[2] == 'live' and psegs[3].isdigit():
            seqn = int(psegs[3])
            seqpath = "%s/upload/%d" % (self.server.local_base_path,seqn)
            if os.path.isdir(seqpath):
                if not os.path.isfile("%s/live_stop" % seqpath):
                    self.send_response(200) # ok
                else:
                    self.send_response(404)  # not found
            else:
                self.send_response(403) # forbidden
        else:
            self.send_response(400)  # bad request

    def do_POST(self):
        path = self.path
        query = ""
        if path.startswith('/api'):
            urlobj = urlparse(path)
            query = urlobj.query

            self.__do_path_mapping_inject()

        if query.startswith('upload/'):
            # -------------------------------
            # /api/upload/<seq>/<file_name>
            # curl --data-binary "@filename" http://<ip>:<port>/api?upload/1/chn0 -v -i
            # -------------------------------
            length = self.headers['content-length']
            data = self.rfile.read(int(length))
            dlen = len(data)

            path_segs = query.split('/')
            if dlen != int(length):
                self.send_response(406)  # not acceptable
                self.end_headers()
            elif len(path_segs) >= 3 and path_segs[0] == 'upload' and path_segs[1].isdigit():
                seqn = int(path_segs[1])
                fn = path_segs[2]
                fpth = "%s/upload/%s/%s" % (self.server.local_base_path,
                                            seqn, fn)

                print("received dlen %d fn %s" % (dlen, fn))

                if not os.path.isdir(self.server.local_base_path):
                    os.mkdir(self.server.local_base_path)
                if not os.path.isdir("%s/upload" % self.server.local_base_path):
                    os.mkdir("%s/upload" % self.server.local_base_path)
                if not os.path.isdir("%s/upload/%d" % (self.server.local_base_path, seqn)):
                    os.mkdir("%s/upload/%d" % (self.server.local_base_path, seqn))

                with open(fpth, 'wb') as fh:
                    fh.write(data)
                    fh.close()

                print(" debug send_response 200 ")
                self.send_response(200) # ok
                self.send_header('Content-type', 'text/html')
                self.send_header('Cache-control', 'no-cache')
                self.end_headers()
                # Send the html message
                msg = "<b> Hello World !</b>" + \
                      "<br /><br /><p>Current time: " + str(datetime.datetime.now()) + "</p>"
                self.wfile.write(msg.encode())
            else:
                self.send_response(404) # not found
                self.end_headers()
        else:
            # -------------------------------
            # /<any_other>
            # -------------------------------
            self.send_response(400)  # bad request
            self.end_headers()


class urlTestServer(HTTPServer): # not invoked on zeit server-less
    def __init__(self, local_path, url_path, server_address,
                                            RequestHandlerClass=urlTestHandler):
        self.local_base_path = local_path  # d:\\zeit_proj\\src\\url_www
        self.url_base_path = url_path      # url_www
        import url_test_pub
        self.url_content = url_test_pub.urlTestPublisher()
        HTTPServer.__init__(self, server_address, RequestHandlerClass)


if __name__ == '__main__':
    # translate 'storage' in url to local 'url_www'
    prog_dir = os.path.dirname(__file__)
    topdir = os.path.abspath(prog_dir + "/../")
    www_dir = os.path.join(topdir, local_base_path)
    server = urlTestServer(www_dir, url_base_path, ("", port))

    print('Started httpserver on port %d' % port)

    #Wait forever for incoming http requests
    server.serve_forever()

