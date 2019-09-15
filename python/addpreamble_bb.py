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

import numpy as np
import numpy
from gnuradio import gr

class addpreamble_bb(gr.basic_block):    
    """
    This block will add a preamble to your fixed size byte stream
    """
    def __init__(self, packet_len, preamble_len, access_code):
        self.packet_len = packet_len;
        self.preamble_len = preamble_len;
        self.access_code = access_code;        
        self.remainder = 0;
        self.preamble_rem = 0;
        self.packets = []
        gr.basic_block.__init__(self,
            name="addpreamble_bb",
            in_sig=[numpy.int8],
            out_sig=[numpy.int8])

    def forecast2(self, noutput_items, ninput_items_required):		
		if (self.remainder > 0):
			ninput_items_required[0]	= self.remainder;
			noutput_items 				= self.remainder;					
		else:
			ninput_items_required[0] = self.packet_len;
			noutput_items = self.packet_len + self.preamble_len;
			


    def general_work2(self, input_items, output_items):					
		noutput = len(output_items[0])
		ninput = len(input_items[0])				
		if (self.remainder > 0):			
			for i in range(self.remainder):				
				if i >= noutput:
					self.consume(0, i);
					ret_rem = i;	
					self.remainder -= i;	
					return ret_rem;
				output_items[0][i] = input_items[0][i];							
			self.consume(0, self.remainder)
			ret_rem = self.remainder;	
			self.remainder = 0;	
			return ret_rem;
		else:
			if (self.preamble_rem > 0):
				for i in range(self.preamble_rem, self.preamble_len):	
					if (i - self.preamble_rem >= noutput):
						self.preamble_rem = self.preamble_len - (i - self.preamble_rem);
						return i - self.preamble_rem;
					else:	
						output_items[0][i - self.preamble_rem] = 225;
				self.preamble_rem = 0;				
			else:
				for i in range(self.preamble_len):				
					if (i >= noutput):
						self.preamble_rem = self.preamble_len - i;
						return i;
					#output_items[0][i] = 3 - numpy.mod(i,4);
					output_items[0][i] = 225;
			for i in range(self.packet_len):
				if (i + self.preamble_len >= noutput):
					rem = self.packet_len - i;
					self.remainder = rem;
					self.consume(0, i)
					return self.preamble_len + i;
				output_items[0][i + self.preamble_len] = input_items[0][i];			
				
			self.consume(0, self.packet_len)
			#self.consume_each(len(input_items[0]))
			if (len(input_items[0]) - self.packet_len < self.packet_len):
				self.remainder = len(input_items[0]) - self.packet_len;
			return self.preamble_len + self.packet_len;
    def forecast(self, noutput_items, ninput_items_required):
		noutput_items = self.packet_len + self.preamble_len;				
		ninput_items_required[0] = self.packet_len;
		
    def general_work(self, input_items, output_items):					
		noutput = len(output_items[0])
		ninput = len(input_items[0])	
		
		if (ninput < self.packet_len):
			return 0;
		if (noutput < self.packet_len + self.preamble_len):
			return 0;
		
		for i in range(self.preamble_len):
			output_items[0][i] = self.access_code[i];
		for i in range(self.packet_len):
			output_items[0][i + self.preamble_len] = 
												self.input_items[0][i];
		return self.packet_len + self.preamble_len;
			
			
		
							
			
		
			
			
