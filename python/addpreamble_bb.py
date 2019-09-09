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

class addpreamble_bb(gr.basic_block):    
    """
    This block will add a preamble to your fixed size byte stream
    """
    def __init__(self, packet_len, preamble_len):
        self.packet_len = packet_len;
        self.preamble_len = preamble_len;
        gr.basic_block.__init__(self,
            name="addpreamble_bb",
            in_sig=[numpy.int8],
            out_sig=[numpy.int8])

    def forecast(self, noutput_items, ninput_items_required):        
            ninput_items_required[0] = self.packet_len;
            noutput_items = self.packet_len + self.preamble_len;

    def general_work(self, input_items, output_items):
		print("input_items",len(input_items))		
		print("output_items",len(output_items))
		for i in range(self.preamble_len):
			output_items[0][i] = 3;
														
		for i in range(self.packet_len):
			output_items[0][i + self.preamble_len] = input_items[0][i];
		self.consume(0, self.packet_len)
        #self.consume_each(len(input_items[0]))
		return self.packet_len + self.preamble_len;
