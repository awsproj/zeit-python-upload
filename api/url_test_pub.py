#!/usr/bin/env python
#   url_test_pub.py

import os

url_base_path = '/api?check/req'
local_base_path = 'url_www/upload'
local_tmp_prefix = None # set to non-None on zeit server-less

def local_work_path():
    if local_tmp_prefix is None:
        return local_base_path
    else:
        return local_tmp_prefix + '/' + local_base_path

class urlTestPublisher:
    def __clear(self):
        self._seqs = []
        self._seqmap = {}

    def __init__(self, tmp_prefix=None):
        self.__clear()
        if tmp_prefix is not None:
            global local_tmp_prefix
            local_tmp_prefix = tmp_prefix
            workpth = local_work_path()
            if not os.path.isdir(workpth):
                # create seq 0 dir with dummy.txt
                import pathlib
                pathlib.Path(workpth + '/0').mkdir(parents=True, exist_ok=True)
                with open(workpth + '/0/dummy.txt', 'wb') as f_out:
                    f_out.write(" ".encode())
                    f_out.close()

    def listContent(self):
        if not os.path.isdir(local_work_path()):
            return
        cont1 = os.listdir(local_work_path())
        cont2 = sorted(cont1, key=lambda x: int(x))
        self.__clear()
        self._seqs = [ [int(x), "%s/%s" % (local_work_path(), x)] for x in cont2]
        self._seqmap = { int(x):i for i,x in enumerate(cont2) }

    def __updateContent_createTable(self):
        rets = "<p><table border=\"1\">\r\n"
        for y in self._seqs:
            x = y[0]
            d = y[1]
            retv =  "    <tr>\r\n"
            retv += "        <td> %d </td> " % x

            rawf1 = d + '/data_chn2'
            rawf2 = d + '/data_chn0'
            rawf3 = d + '/data_info'
            rqf   = d + '/upload_req'
            cond1 = os.path.isfile(rawf1)
            cond2 = cond1 and os.path.isfile(rawf2) and os.path.isfile(rawf3)
            cond3 = os.path.isfile(rqf)
            td3 = "&lt; no cap action &gt;"
            td2_jpg = " no jpeg1 jpeg2 "
            td2_cap = " &nbsp; no cap "
            if cond1:
                td2_jpg = " play %s %s " % (
                          "<a href=\"/api?media/snapshot/%d/1\" target=\"_blank\">jpeg1</a> " % x,
                          "<a href=\"/api?media/snapshot/%d/2\" target=\"_blank\">jpeg2</a> " % x)
                if cond2:
                    td2_cap = " cap "
                else:
                    if cond3:
                        td3 = "waiting cap"
                    else:
                        td3_id = "askvcap%d" % x
                        td3_s = "<script type=\"text/javascript\"> %s %s </script>" % (
                            "function askvcap_%d() { " % x,
                            " $(\"#%s\").load(\"/api?media/askvcap/%d\"); return false; }" % (
                                td3_id, x
                            )
                        )
                        td3_1 = "<a href=\"javascript:void(0);\" onclick=\"askvcap_%d()\">" % x
                        td3_2 = "click to request camera upload cap</a>"
                        td3_3 = "<div id=\"%s\"> </div>" % td3_id
                        td3 = "<div> %s %s %s %s </div>" % (td3_s, td3_1, td3_2, td3_3)
            td2 = "<div>%s %s</div>" % (td2_jpg, td2_cap)
            retv += "        <td> %s </td> <td> %s </td>\r\n" % (td2, td3)

            live_on_f   = d + '/live_on'
            live_done_f = d + '/live_done'
            live_stop_f = d + '/live_stop'
            cond4 = os.path.isfile(live_on_f)
            cond5 = os.path.isfile(live_done_f)
            cond6 = not os.path.isfile(live_stop_f)
            td4 = "&lt; no live video &gt;"
            td5 = "&lt; no live action &gt;"
            if cond5:
                td4 = "&lt; live video done &gt;"
            else:
                if cond4:
                    td4 = "play live video"
                if cond6:
                    td5_id = "asklive%d" % x
                    td5_s = "<script type=\"text/javascript\"> %s %s </script>" % (
                        "function asklive_%d() { " % x,
                        " $(\"#%s\").load(\"/api?media/asklive/%d\"); return false; }" % (
                            td5_id, x
                        )
                    )
                    td5_1 = "<a href=\"javascript:void(0);\" onclick=\"asklive_%d()\">" % x
                    td5_2 = "click to stop live video</a>"
                    td5_3 = "<div id=\"%s\"> </div>" % td5_id
                    td5 = "<div> %s %s %s %s </div>" % (td5_s, td5_1, td5_2, td5_3)
            retv += "        <td> %s </td> <td> %s </td>\r\n" % (td4, td5)
            retv += "    </tr>\r\n"
            rets += retv
        rets += "   </table>\r\n"
        rets += "<p>\r\n"
        return rets

    def updateContent(self):
        import time
        tm1 = time.time()
        self.listContent()
        rv1 = self.__updateContent_createTable()
        tm2 = time.time()
        rv = "<p> <p> %s </p> <p> updateContent(): &nbsp; %s &nbsp; &nbsp; %s </p> </p>" % (
            rv1, "%.2f seconds" % (tm2 - tm1), " %d bytes " % len(rv1))
        return rv

    def __snapshot_createJpeg(self, seq, snap_num):
        rets = None
        sidx = self._seqmap.get(seq, None)
        if sidx == None:
            return rets

        filepath = self._seqs[sidx][1] + '/data_chn2'
        data = None
        if not os.path.isfile(filepath):
            return rets

        try:
            with open(filepath, "rb") as f_in:
                data = f_in.read()
        except:
            pass
        if data is None:
            return rets

        total_bytes = len(data)
        import struct

        # top level header
        consumed = 0
        if consumed + 24 >= total_bytes:
            return [False, "Failed top level 1 header no enough data"]

        # 6 * 4 = 24 bytes: packet header
        # h_type, h_len, h_seqn, h_total_len, h_segs, h_working
        h1 = struct.unpack("@IIIIII", data[consumed:consumed+24])
        if h1[3] >= total_bytes:
            return [False, "Failed top level 1 frame size match"]
        if h1[0] != 0xff0f0201:
            return [False, "Failed top level 1 jpeg packet type check"]
        if h1[1] != 24:
            return [False, "Failed top level 1 header size check"]
        if h1[4] != 2:
            return [False, "Failed top level 1 header segs check"]
        consumed += 24

        # seg 1
        if consumed + 48 >= total_bytes:
            return [False, "Failed plen1 header no enough data"]
        # 12 * 4 = 48 bytes: video seg header
        v1 = struct.unpack("@IIIIIIIIIIII", data[consumed:consumed+48])
        #    uint32_t msg_type, hdr_len, seqn;
        #    uint32_t vpss_chn, /* 0:h265, 1:h265, 2:jpeg */
        #             key_frame, /* 1 for I frame */
        #             frame_count, frame_msg_no, frame_data_len;
        #    uint32_t mono_stamp_lo, mono_stamp_hi, wall_stamp_lo, wall_stamp_hi;
        consumed += 48

        d_ext1 = data[0:0]
        d_ext2 = data[0:0]

        plen1 = v1[7]
        if consumed + plen1 >= total_bytes:
            return [False, "Failed plen1 too big"]
        d_ext1 += data[consumed:consumed+plen1]
        consumed += plen1

        # seg 2
        if consumed + 48 >= total_bytes:
            return [False, "Failed plen2 header no enough data"]
        v2 = struct.unpack("@IIIIIIIIIIII", data[consumed:consumed+48])
        consumed += 48

        plen2 = v2[7]
        if consumed + plen2 >= total_bytes:
            return [False, "Failed plen2 too big"]
        d_ext1 += data[consumed:consumed+plen2]
        consumed += plen2

        # top level header 2
        if consumed + 24 >= total_bytes:
            return [False, "Failed top level 2 header no enough data"]

        # h_type, h_len, h_seqn, h_total_len, h_segs, h_working
        h2 = struct.unpack("@IIIIII", data[consumed:consumed + 24])
        if h2[3] + consumed > total_bytes:
            return [False, "Failed top level 2 frame size match"]
        if h2[0] != 0xff0f0201:
            return [False, "Failed top level 2 jpeg packet type check"]
        if h2[1] != 24:
            return [False, "Failed top level 2 header size check"]
        if h2[4] != 2:
            return [False, "Failed top level 2 header segs check"]
        consumed += 24

        # seg 3
        if consumed + 48 >= total_bytes:
            return [False, "Failed plen3 header no enough data"]
        v3 = struct.unpack("@IIIIIIIIIIII", data[consumed:consumed+48])
        consumed += 48

        plen3 = v3[7]
        if consumed + plen3 >= total_bytes:
            return [False, "Failed plen3 too big"]
        d_ext2 += data[consumed:consumed + plen3]
        consumed += plen3

        # seg 4
        if consumed + 48 >= total_bytes:
            return [False, "Failed plen4 header no enough data"]
        v4 = struct.unpack("@IIIIIIIIIIII", data[consumed:consumed+48])
        consumed += 48

        plen4 = v4[7]
        if consumed + plen4 > total_bytes:
            return [False, "Failed plen4 too big"]
        d_ext2 += data[consumed:consumed + plen4]
        consumed += plen4

        if consumed != total_bytes:
            return [False, "Failed total_bytes not match to consumed"]

        if snap_num == 1:
            rets = [True, d_ext1]
        elif snap_num == 2:
            rets = [True, d_ext2]
        else:
            rets = [False, "Failed snap num not 1 or 2"]
        return rets

    def snapshot(self, idx_str):
        args = idx_str.split('/')
        if type(args) is not list or len(args) < 2 or not args[0].isdigit() or not args[1].isdigit():
            return [False, "Failed to decode input argument"]
        import time
        tm1 = time.time()
        seq = int(args[0])
        sidx = int(args[1])
        self.listContent()
        rv = self.__snapshot_createJpeg(seq, sidx)
        tm2 = time.time()
        print("  snapshot decoding consumed %.2f" % (tm2 - tm1))

        if rv is None:
            return [False, "Failed no decoded data"]
        if type(rv) is list and len(rv) == 2:
            if type(rv[0]) is bool:
                return rv # ok, returning the jpeg image
        return [False, "Failed no decoded return format"]


    def __askvcap_touchfile(self, seq):
        sidx = self._seqmap.get(seq, None)
        if sidx == None:
            return False # fail

        filepath = self._seqs[sidx][1] + '/upload_req'
        if os.path.isfile(filepath):
            return True # done ok

        done_ok = False
        try:
            with open(filepath, "wb") as f_out:
                import time
                f_out.write("%.0f" % time.time())
                f_out.close()
                done_ok = True # ok
        except:
            pass

        return done_ok

    def askvcap(self, idx_str):
        args = idx_str.split('/')
        if type(args) is not list or len(args) < 1 or not args[0].isdigit():
            return False
        seq = int(args[0])
        self.listContent()
        rv = self.__askvcap_touchfile(seq)
        return rv


    def __asklive_touchfile(self, seq):
        sidx = self._seqmap.get(seq, None)
        if sidx == None:
            return False # fail

        filepath = self._seqs[sidx][1] + '/live_stop'
        if os.path.isfile(filepath):
            return True # done ok

        done_ok = False
        try:
            with open(filepath, "wb") as f_out:
                import time
                f_out.write("%.0f" % time.time())
                f_out.close()
                done_ok = True # ok
        except:
            pass

        return done_ok

    def asklive(self, idx_str):
        args = idx_str.split('/')
        if type(args) is not list or len(args) < 1 or not args[0].isdigit():
            return False
        seq = int(args[0])
        self.listContent()
        rv = self.__asklive_touchfile(seq)
        return rv

