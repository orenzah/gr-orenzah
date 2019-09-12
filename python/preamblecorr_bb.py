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
        self.access_code_crumbs = [];
        self.unpack_accesscode();
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
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
        # consume one byte each iteration
        # notice, we consider four bytes as one
        noutput = len(output_items[0])
        ninput = len(input_items[0])
        if (len(self.crumbs_window) < self.preamble_len * 4):
            self.crumbs_window[0] = input_items[0][0];
            self.consume_each(1);
        else:                            
            pop_cnt = self.sliding_window();
            if pop_cnt > 0:
                #there is not match remove it                
                while pop_cnt > 0:
                    self.crumbs_window.pop(0);
                    pop_cnt -= 1;
            else:
                #there is a match
                #consume packet_len items
                #output packet_len items                
                output_items[0][0] = pack_four_bytes(input_items);
                return 1;                
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
        for i in range(self.preamble_len):
            self.access_code_crumbs.append(
            (self.access_code[i] << 6) & (0xFF << 6));            
            self.access_code_crumbs[i + 1] = (
            (self.access_code[i] << 4) & (0xFF << 4));
            self.access_code_crumbs[i + 2] = (
            (self.access_code[i] << 2) & (0xFF << 2));
            self.access_code_crumbs[i + 3] = (
            (self.access_code[i] << 0) & (0xFF << 0));
        return;
    def pack_four_bytes(self, input_items):       
        alignedByte = (
            input_items[0][0] << 6
        +   input_items[0][1] << 4 
        +   input_items[0][2] << 2 
        +   input_items[0][3] << 0);
        return alignedByte;
