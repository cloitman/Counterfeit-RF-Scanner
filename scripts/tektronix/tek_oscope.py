#
# Copyright (C) 2020
# Author: Ilias Giechaskiel <ilias@giechaskiel.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

import pyvisa as visa # deprecated import visa
import time
import csv # for write_file

def b2s(enable):
	return 'ON' if enable else 'OFF'

class TekMDO3104(object):
	def __init__(self, instr='USB0::1689::1032::C013559::0::INSTR', timeout=10):
		self.rm = visa.ResourceManager()
		self.inst = self.rm.open_resource(instr)
		self.inst.timeout = timeout*1000 # seconds to milliseconds

	def __del__(self):
		self.inst.close()

	def _read(self, cmd, converter='f'):
		return self.inst.query_ascii_values(cmd, converter=converter)

	def _write(self, cmd):
		self.inst.write(cmd)
		time.sleep(0.1)

	def select_channel(self, ch, enable=True):
		self._write('SELect:CH%d %s' % (ch, b2s(enable)))

	def reset(self):
		self._write('*RST')
		self.select_channel(1, False)
		self.select_channel(2, False)
		# self._read("*OPC?")

	def save_image(self, temp_path, local_path=None):
		self._write("SAVe:IMAGe:FILEFormat PNG")
		self._write("SAVe:IMAGe \"%s\"" % temp_path)
		self._read("*OPC?")
		self.copy_file(temp_path, local_path)

	def copy_file(self, remote_path, local_path=None, delete=True):
		self._write("FILESystem:READFile \"%s\"" % remote_path)
		# timeout = self.inst.timeout
		# self.inst.timeout = 60000 # 1 minute
		data = self.inst.read_raw()
		# self.inst.timeout = timeout
		if not local_path:
			local_path = remote_path
		with open(local_path, 'wb') as f:
			f.write(data)
		if delete:
			self._write("FILESystem:DELEte \"%s\"" % remote_path)

	def set_analog_horizontal_scale(self, seconds):
		# self._write('WFMInpre:XINcr %e' % seconds)
		self._write('HORizontal:SCAle %e' % seconds)

	def set_analog_vertical_scale(self, ch, volts):
		self._write('CH%d:SCAle %e' % (ch, volts))

	def set_analog_vertical_offset(self, ch, volts):
		self._write('CH%d:OFFSET %e' % (ch, volts))

	def center_vertical(self, ch, pos=0):
		self._write('CH%d:POSITION %.2f' % (ch, pos))

	def get_analog_data(self, ch=1, points=10000, binary=True):
		# self._write('DATa INIT')
		self._write('DATa:SOUrce CH%d' % ch)
		self._write('DATa:START 1')
		self._write('DATa:STOP %d' % points)
		# self._write('WFMInpre:DOMain TIMe')
		enc = 'BINary' if binary else 'ASCii'
		self._write('WFMOutpre:ENCdg %s' % enc)
		self._write('WFMOutpre:BYT_Nr 1')
		self._write('HEADer 0')
		xinc = self._read('WFMOutpre:XINcr?')[0]
		xstart = self._read('WFMOutpre:XZEro?')[0]
		times = [xstart + xinc*i for i in range(points)]
		ymult = self._read('WFMOutpre:YMUlt?')[0]
		ystart = self._read('WFMOutpre:YZEro?')[0]
		ypos = self._read('CH%d:POSition?' % ch)[0]
		yscale = self._read('CH%d:SCALE?' % ch)[0]
		# print(ch, xinc, xstart, ymult, ystart, ypos, yscale)
		self._write('ACQuire:MODe HiRes')
		self._write('ACQuire:NUMAVg 4')
		self._write('ACQuire:STATE STOP')

		tstart = time.time()
		if binary:
		    curve = self.inst.query_binary_values('CURVE?', datatype='b', is_big_endian=True)
		else:
		    curve = self._read('CURVE?')
		tend = time.time()
		# print('CH RAW', enc, tend-tstart)
		self._write('ACQuire:STATE RUN')
		self._write('WFMOutpre:ENCdg ASCii')
		# if ch == 2:
		#     print (curve)
		curve = [ystart + ymult*c-ypos*yscale for c in curve]
		return (times, [curve])

def write_file(outfile, data):
	header, rows = data
	with open(outfile, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(header)
		for row in rows:
			writer.writerow(row)

def get_data(ch):
	mdo = TekMDO3104()
	mdo.reset()
	time.sleep(1)
	mdo.set_analog_horizontal_scale(0.001)
	mdo.select_channel(ch)
	if ch == 1:
		mdo.set_analog_vertical_scale(ch, 0.6)
		mdo.set_analog_vertical_offset(ch, 10)
		mdo.center_vertical(ch, -5)
	elif ch == 2:
		mdo.set_analog_vertical_scale(ch, 0.01)
		mdo.set_analog_vertical_offset(ch, 1)
		mdo.center_vertical(ch, 0)
	else:
	    raise ValueError("Unexpected channel %d" % ch)

	# time.sleep(0.3)
	data = mdo.get_analog_data(ch, 10000)
	times = data[0]
	volts = data[1][0]
	return volts
