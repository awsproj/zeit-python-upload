#!/usr/bin/env python
#   video_chn2_decap.py

import os
import sys

local_base_path = 'url_www/upload'
local_file_name = 'data_chn2'

class urlTestPublisherLocal:
    def __clear(self):
        self._seqs = []
        self._seqmap = {}
        self._decoded_num_frames = 0
        self._decoded_num_packets = 0

    def __init__(self):
        self.__clear()

    def listContent(self):
        if not os.path.isdir(local_base_path):
            return
        cont1 = os.listdir(local_base_path)
        cont2 = sorted(cont1, key=lambda x: int(x))
        self.__clear()
        self._seqs = [ [int(x), "%s/%s" % (local_base_path, x)] for x in cont2]
        self._seqmap = { int(x):i for i,x in enumerate(cont2) }

    def checkSeq(self, seq):
        self.listContent()
        seq = int(seq)
        if seq in self._seqmap.keys():
            return True
        return False

    def __updateContent_createTable(self):
        rets = ""
        rets += "    "
        rets += " %-6s " % "seq"
        rets += " %s " % "size"
        rets += "\r\n"
        for y in self._seqs:
            x = y[0]
            d = y[1]
            retv =  "    "
            retv += " %-6d " % x

            rawf2 = d + '/' + local_file_name
            cond2 = os.path.isfile(rawf2)
            if cond2:
                statinfo = os.stat(rawf2)
                retv += " %s " % (str(statinfo.st_size))
            else:
                retv += " %s " % ( "<non-chn-file>" )

            rets += retv + "\r\n"
        return rets

    def updateContent(self):
        import time
        tm1 = time.time()
        self.listContent()
        rv1 = self.__updateContent_createTable()
        tm2 = time.time()
        rv = "\n%s\n  updated in %s  content %s " % (
            rv1, "%.2f seconds" % (tm2 - tm1), " %d bytes " % len(rv1))
        return rv

    def __snapshot_createJpeg(self, seq, snap_num):
        rets = None
        sidx = self._seqmap.get(seq, None)
        if sidx == None:
            return rets

        filepath = self._seqs[sidx][1] + '/' + local_file_name
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

        self._decoded_num_frames = 0
        self._decoded_num_packets = 0

        total_bytes = len(data)
        import struct

        running_rec = {"consumed":0, "result":""}
        running_rec["consumed"] = 0

        def dec_seg(topn, segn):
            consumed = running_rec["consumed"]
            errn = " -- %d %d" % (topn, segn)

            # seg 1
            if consumed + 48 >= total_bytes:
                return [False, "Failed plen1 header no enough data" + errn]
            # 12 * 4 = 48 bytes: video seg header
            v1 = struct.unpack("@IIIIIIIIIIII", data[consumed:consumed + 48])
            #    uint32_t msg_type, hdr_len, seqn;
            #    uint32_t vpss_chn, /* 0:h265, 1:h265, 2:jpeg */
            #             key_frame, /* 1 for I frame */
            #             frame_count, frame_msg_no, frame_data_len;
            #    uint32_t mono_stamp_lo, mono_stamp_hi, wall_stamp_lo, wall_stamp_hi;
            consumed += 48
            running_rec["consumed"] = consumed

            d_ext_seg = data[0:0]

            plen1 = v1[7]
            if consumed + plen1 > total_bytes:
                return [False, "Failed plen1 too big" + errn]
            d_ext_seg += data[consumed:consumed + plen1]
            consumed += plen1
            running_rec["consumed"] = consumed

            return [True, d_ext_seg]

        def dec_top(topn):
            consumed = running_rec["consumed"]
            errn = " -- %d" % topn

            # top level header
            if consumed + 24 >= total_bytes:
                return [False, "Failed top level 1 header no enough data" + errn]

            # 6 * 4 = 24 bytes: packet header
            # h_type, h_len, h_seqn, h_total_len, h_segs, h_working
            h1 = struct.unpack("@IIIIII", data[consumed:consumed+24])
            if h1[3] >= total_bytes:
                return [False, "Failed top level 1 frame size match" + errn]
            if h1[0] != 0xff0f0201:
                return [False, "Failed top level 1 jpeg packet type check" + errn]
            if h1[1] != 24:
                return [False, "Failed top level 1 header size check" + errn]
            if h1[4] != 2:
                return [False, "Failed top level 1 header segs check" + errn]
            consumed += 24
            running_rec["consumed"] = consumed

            h_segs = h1[4]
            ret_data = ""
            for seg in range(h_segs):
                rs = dec_seg(topn, seg)
                if type(rs) is not list or len(rs) != 2 or type(rs[0]) is not bool:
                    return [False, "seg %d rs condition failed" % seg + errn]
                if not rs[0]:
                    return [False, rs[1] + errn]
                ret_data += rs[1]

            return [True, ret_data]

        def dec_top_n(n):
            rt = dec_top(n)
            if type(rt) is not list or len(rt) != 2 or type(rt[0]) is not bool:
                return [False, "top %d rt condition failed" % n]
            return rt

        rt = dec_top_n(1)
        if not rt[0]:
            return rt
        d_ext1 = rt[1]

        rt = dec_top_n(2)
        if not rt[0]:
            return rt
        d_ext2 = rt[1]

        if snap_num == 1:
            rets = [True, d_ext1]
        elif snap_num == 2:
            rets = [True, d_ext2]
        else:
            rets = [False, "Failed snap num not 1 or 2"]
        return rets

    def snapshot(self, idx_str):
        args = idx_str.split('/')
        if type(args) is not list or len(args) < 1 or not args[0].isdigit():
            return [False, "Failed to decode input argument"]
        import time
        tm1 = time.time()
        seq = int(args[0])
        sidx = 0
        if len(args) > 1:
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

def video_chn0_decap(inst):
    if len(sys.argv) < 2:
        print("Error: argv")
        return
    seqn = sys.argv[1]
    idxn = "1"
    if len(sys.argv) >=3:
        idxn = sys.argv[2]
    if not inst.checkSeq(seqn):
        print("Error: seqn %s not exist" % seqn)
        return
    retv = inst.snapshot(seqn + "/" + idxn)
    if not type(retv) is list:
        print(" retv type %s " % str(type(retv)))
    if len(retv) != 2:
        print(" retv len %s " % str(len(retv)))
    if retv[0]:
        print("Ok, size %d" % len(retv[1]))
        wfname = "snap_%s_%s.jpeg" % (seqn, idxn)
        with open(wfname, "wb") as f:
            f.write(retv[1])
            f.close()
        print("Ok, written to file %s" % wfname)
    else:
        print("Error: %s" % retv[1])


if __name__ == '__main__':
    inst = urlTestPublisherLocal()
    if len(sys.argv) <= 1:
        r = inst.updateContent()
        print(r)
        print("\nSelect the sequence number to decap")
    else:
        video_chn0_decap(inst)


