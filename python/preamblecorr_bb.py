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
        noutput = len(output_items[0])
		ninput = len(input_items[0])
        
        output_items[0][:] = input_items[0]
        consume(0, len(input_items[0]))
        #self.consume_each(len(input_items[0]))
        return len(output_items[0])
