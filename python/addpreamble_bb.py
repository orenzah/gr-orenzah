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
			
    def forecast(self, noutput_items, ninput_items_required):		
		if (noutput_items < self.packet_len):
			nout = self.packet_len;
		else:
			nout = noutput_items / self.packet_len;
			nout *= self.packet_len; 
		ninput_items_required[0] = nout;

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
						output_items[0][i - self.preamble_rem] = 120;
				self.preamble_rem = 0;				
			else:
				for i in range(self.preamble_len):				
					if (i >= noutput):
						self.preamble_rem = self.preamble_len - i;
						return i;
					#output_items[0][i] = 3 - numpy.mod(i,4);
					output_items[0][i] = 120;
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

    def general_work(self, input_items, output_items):					
		noutput = len(output_items[0])
		ninput = len(input_items[0])	
		packet_size = self.packet_len + self.preamble_len;			
		packet = np.zeros(packet_size);
		
		npackets = ninput / (self.packet_len);		
		if (npackets <= 0):
			return 0;		
		for i in range(npackets):			
			for j in range(self.preamble_len):
				packet[j] = self.access_code[j];
			for j in range(self.packet_len):
				packet[j + self.preamble_len] = input_items[0][j];
			self.consume_each(ninput);
			self.packets.append(packet);
			
		
		npacket_out = 0;
		while 1:
			if ((npacket_out + 1) * packet_size <= noutput):				
				if (len(self.packets) == 0):
					break;
				packet = self.packets.pop(0)						
				for i in range(packet_size):
					j = i + npacket_out * packet_size;
					output_items[0][j] = packet[i];	
				npacket_out += 1;							
			else:
				break;			
		return (npacket_out) * (packet_size);
		
							
			
		
			
			
