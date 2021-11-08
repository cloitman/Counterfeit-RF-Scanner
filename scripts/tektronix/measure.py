import csv
import math
import time
import visa

def b2s(enable):
    return 'ON' if enable else 'OFF'

class MDO3054(object):
    def __init__(self, timeout=10):
        self.rm = visa.ResourceManager()
        res = self.rm.list_resources()[0]
        self.inst = self.rm.open_resource(res)
        self.inst.timeout = timeout*1000 # seconds to milliseconds

    def __del__(self):
        self.inst.close()

    def _read(self, cmd, converter='f'):
        return self.inst.query_ascii_values(cmd, converter=converter)

    def _write(self, cmd):
        self.inst.write(cmd)

    def turn_rf_on(self, enable=True):
        self.select_rf(enable)
        self.turn_spectrogram_on(enable)
        self.set_marker_enable(enable)

    def select_rf(self, enable=True):
        self._write('SELect:RF_NORMal %s' % b2s(enable))

    def turn_spectrogram_on(self, enable=True):
        self._write('RF:SPECTRogram:STATE %s' % b2s(enable))

    def select_channel(self, ch, enable=True):
        self._write('SELect:CH%d %s' % (ch, b2s(enable)))

    def turn_afg_on(self, enable=True):
        self._write('AFG:OUTPut:LOAd:IMPEDance FIFty')
        self._write('AFG:OUTPut:STATE %s' % b2s(enable))

    def set_frequency(self, freq):
        self._write('RF:FREQuency %e' % freq)

    def set_span(self, freq):
        self._write('RF:SPAN %e' % freq)

    def set_marker(self, freq, id=1):
        self._write('MARKER:M%d:FREQuency:ABSolute %e' % (id, freq))

    def get_marker_amp(self, id=1):
        return self._read('MARKER:M%d:AMPLitude:ABSolute?' % id)[0]

    def set_marker_enable(self, enable):
        self._write('MARKER:MANUAL %s' % b2s(enable))

    def reset(self):
        self._write('*RST')
        self.select_channel(1, False)
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


    def get_rf_data(self, n=1, points=10000, binary=True):
        time.sleep(1)
        self._write('DATa:SOUrce RF_NORMal')
        time.sleep(1)
        # print(self._read('DATA:SOurce?', 's'))
        # self._write('DATa:STARt 1')
        # self._write('DATa:STOP %d' % points)
        enc = 'BINary' if binary else 'ASCii'
        self._write('WFMOutpre:ENCdg %s' % (enc))
        self._write('WFMOutpre:BYT_Nr 4')
        self._write('HEADer 0')
        xinc = self._read('WFMOutpre:XINcr?')[0]
        xstart = self._read('WFMOutpre:XZEro?')[0]
        points = int(self._read('WFMOutpre:NR_Pt?')[0])
        freqs = [xstart + xinc*i for i in range(points)]
        ymult = self._read('WFMOutpre:YMUlt?')[0]
        curves = [0]*n
        tstart = time.time()
        for i in range(n):
            if binary:
                curves[i] = self.inst.query_binary_values('CURVE?', datatype='f', is_big_endian=True)
            else:
                curves[i] = self._read('CURVE?')
        tend = time.time()
        print ("RF RAW", enc, tend-tstart)
        self._write('WFMOutpre:ENCdg ASCii')
        for i in range(n):
            curves[i] = [30 + 10*math.log10(ymult*c) for c in curves[i]]
        return (freqs, curves)
        return list(zip(freqs, curve))

    def set_afg_ampl(self, volt): # peak to peak
        self._write('AFG:AMPLitude %.3f' % volt)

    def set_afg_freq(self, freq):
        self._write('AFG:FREQuency %.1f' % freq)

    def set_afg_offset(self, dc):
        self._write('AFG:OFFSet %.2f' % dc)

    def set_afg_func(self, func):
        # {SINE|SQUare|PULSe|RAMP|NOISe|DC|SINC|GAUSsian|LORENtz|ERISe|EDECAy|HAVERSINe|CARDIac|ARBitrary}
        self._write('AFG:FUNCtion %s' % func)

    def set_afg_phase(self, phase):
        self._write('AFG:PHASe %.1f' % phase)

    def set_analog_horizontal_scale(self, seconds):
        # self._write('WFMInpre:XINcr %e' % seconds)
        self._write('HORizontal:SCAle %e' % seconds)

    def set_analog_vertical_scale(self, ch, volts):
        self._write('CH%d:SCAle %e' % (ch, volts))

    def get_analog_data(self, ch=1, points=10000, binary=True):
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
        self._write('ACQuire:STATE STOP')
        tstart = time.time()
        if binary:
            curve = self.inst.query_binary_values('CURVE?', datatype='b', is_big_endian=True)
        else:
            curve = self._read('CURVE?')
        tend = time.time()
        print('CH RAW', enc, tend-tstart)
        self._write('ACQuire:STATE RUN')
        self._write('WFMOutpre:ENCdg ASCii')
        curve = [ystart + ymult*c for c in curve]
        return (times, [curve])

    def save_to_csv(self, temp_path, local_path=None):
        self._write('SAVe:WAVEform:FILEFormat SPREADSheet')
        self._write('SAVE:WAVEFORM ALL,"%s"' % temp_path)
        self._read("*OPC?")
        self.copy_file(temp_path, local_path)

    def save_multiple(self, basename, n, local_dir='.', spreadsheet=True):
        if spreadsheet:
            formatting = 'SPREADSheet'
            ext = 'csv'
        else:
            formatting = 'INTERNal'
            ext = 'isf'
        self._write('SAVe:WAVEform:FILEFormat %s' % formatting)
        tstart = time.time()
        for i in range(n):
            self._write('SAVE:WAVEFORM ALL,"%s_%d.%s"' % (basename, i, ext))
            self._read("*OPC?")
        tend = time.time()
        print (ext, tend-tstart)
        for i in range(n):
            local_fname = "%s_%d.%s" % (basename, i, ext)
            if spreadsheet:
                remote_fname = local_fname
            else:
                remote_fname = "%s_%d.isf_RF_NORMal.%s" % (basename, i, ext)

            self.copy_file(remote_fname, "%s/%s" % (local_dir, local_fname))


def write_file(outfile, data):
    header, rows = data
    with open(outfile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


mdo = MDO3054()

# mdo.reset()
# mdo.turn_afg_on()
# mdo.set_afg_func('SINE')
# mdo.set_afg_ampl(0.5)
# mdo.set_afg_freq(1e6)

# time.sleep(1)
# ch = 4
# mdo.select_channel(ch)
# mdo.set_analog_horizontal_scale(10e-9)
# mdo.set_analog_vertical_scale(ch, 1)
# data = mdo.get_analog_data(ch, 10000)
# write_file('examples/timeseries.csv', data)

mdo.turn_rf_on()
mdo.set_frequency(200e6)
mdo.set_span(300e6)
mdo.set_marker(200e6)
mdo.set_marker(300e6, 2)
print("Mark 1", mdo.get_marker_amp())
print("Mark 2", mdo.get_marker_amp(2))

nseries = 100

data = mdo.get_rf_data(nseries) # about 0.13 seconds per data
write_file('examples/powers.csv', data)

# # These are slower
# mdo.save_multiple('saved_data', nseries, 'examples/isf', spreadsheet=False)
# mdo.save_multiple('saved_data', nseries, 'examples/csv', spreadsheet=True)

# filename = 'screenshot.png'
# mdo.save_image(filename, 'examples/%s' % filename)
# mdo.save_to_csv('test.csv')

