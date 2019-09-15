#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2019 Oren Zaharia.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr

class preamblecorr_bb(gr.basic_block):
    """
    This block will try to match the preamble access_code from
    a byte size stream.
    The block will remove the preamble from the stream.    
    """
    def __init__(self, packet_len, preamble_len, access_code):
        self.packet_len = packet_len;
        self.preamble_len = preamble_len;
        self.access_code = access_code;
        self.access_code_crumbs = list(numpy.ones(preamble_len * 4));
        self.synchronized = False;
        self.unpack_accesscode();
        self.success_sync = 0;
        print(self.access_code_crumbs);
        self.crumbs_window = [];
        self.curr_window = [];        
        self.produced = 0;
        if (len(access_code) !=  preamble_len):
            assert("Access code and Preamble Length doesn't match")
        gr.basic_block.__init__(self,
            name="preamblecorr_bb",
            in_sig=[numpy.int8],
            out_sig=[numpy.int8])

    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        if (self.synchronized):
            noutput_items = 1;
            ninput_items_required[0] = noutput_items*4;
        else:    
            noutput_items = 1;
            ninput_items_required[0] = noutput_items;

    def general_work(self, input_items, output_items):
        # consume one byte/4 each iteration that is 1/4 items
        # byte/4 is one crumb (2 bits)
        # notice, we consider four bytes as one
        
        noutput = len(output_items[0])
        ninput = len(input_items[0])        
        if (not self.synchronized):
            if (len(self.crumbs_window) < self.preamble_len * 4):            
                self.crumbs_window.append(input_items[0][0]);
                self.consume_each(1);
                #output_items[0][0] = 2;                    
                return 0;
            else:
                # we have collected 16*4 crumbs items
                # compare the access_code to the crumbs window                
                cnt = self.sliding_window();                                
                if cnt == 0:
                    # that is we have a match, we are sync
                    # output now preamble_len bytes
                    # using preamble_len*4 crumbs input                    
                    self.synchronized = True;
                    self.crumbs_window = [];        
                    #output_items[0][0] = 2;                    
                    return 0;
                else:
                    for i in range(cnt):
                        self.crumbs_window.pop(0);                    
                        #output_items[0][0] = 2;
                    return 0;
        else:
            if (self.produced < self.packet_len):                
                input_arr = input_items[0]
                if (ninput < 4):
                    return 0;
                output_byte = self.pack_four_bytes(input_arr);
                self.consume_each(4);
                output_items[0][0] = output_byte;
                self.produced += 1;
                return 1;
            else:
                self.produced = 0;
                self.synchronized = False;
                print("Done", self.success_sync);
                self.success_sync += 1;
                return 0;
        #consume(0, len(input_items[0]))
        
        return len(output_items[0])
    def sliding_window(self):
        #return the number of the unmatch indexex
        #e.g. if access_code is [1,2,3,4] and curr_window [1,2,3,4]
        #return 0
        #e.g. if access_code is [1,1,3,1] and curr_window [1,2,3,4]
        #return 2
        cnt = self.preamble_len * 4;
        for i in range(self.preamble_len * 4):
            cnt -= (self.crumbs_window[i] == self.access_code_crumbs[i]);
        return cnt;        
    def unpack_accesscode(self):
        copy_acc = self.access_code[:];
        for j in range(self.preamble_len):
            i = j*4;
            shift = 6;
            self.access_code_crumbs[i] = (copy_acc[j] & (0x03 << shift))
            self.access_code_crumbs[i] = self.access_code_crumbs[i] >> shift;
            shift = 4;
            self.access_code_crumbs[i+1] = (copy_acc[j] & (0x03 << shift))
            self.access_code_crumbs[i+1] = self.access_code_crumbs[i+1] >> shift;
            shift = 2;
            self.access_code_crumbs[i+2] = (copy_acc[j] & (0x03 << shift))
            self.access_code_crumbs[i+2] = self.access_code_crumbs[i+2] >> shift;
            shift = 0;
            self.access_code_crumbs[i+3] = (copy_acc[j] & (0x03 << shift))
            self.access_code_crumbs[i+3] = self.access_code_crumbs[i+3] >> shift;
        return;
    def pack_four_bytes(self, input_items):       
        alignedByte  = input_items[0] << 6;
        alignedByte += input_items[1] << 4;
        alignedByte += input_items[2] << 2;
        alignedByte += input_items[3] << 0;
        return alignedByte;
