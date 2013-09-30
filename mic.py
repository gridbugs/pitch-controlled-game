from config import *

from numpy import fromstring, short, angle
from numpy.fft import fft
import pyaudio
import wave
import math

from helpers import *

class Mic:

  def __init__(self):
    self.loud = True
    self.loud_count = 0

    self.p = pyaudio.PyAudio()
    self.stream = self.p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)



  def process(self):
    try:
      # get some data from the mic as a string
      data_str = self.stream.read(CHUNK)
      # convert the string to an integer array representing amplitude over time
      data_time_domain = fromstring(data_str, dtype=short)

      # just use the left channel
      data_l = data_time_domain[1::2]

      # discrete fourier transform to convert the data into a complex number array
      # representing the amplidue of the different frequencies in the sample
      data_freq_domain = fft(data_l)[:len(data_l)/2]


      interpolated = \
        log_interpolate(                 # evenly distribute values on the x axis
        map(lambda x: max(x,0) - 0, # filter out low amplitudes
        map(lambda x: x / float(10000),  # evenly distribute values on the y axis
        map(abs, data_freq_domain))),    # get the absolute value of each frequency domain value
        map(lambda x: RES * x, range(0, WIDTH/RES)), # x axis points we're interested in
        110   # scale in the x axis
      )[100:200]

      volume = sum(interpolated)

      loud = self.loud
      loud_count = self.loud_count

      if loud:
        if volume <= THRESHOLD:
          loud_count -= 1
        else:
          loud_count = min(loud_count + 1, 0)
      else:
        if volume > THRESHOLD:
          loud_count += 1
        else:
          loud_count = max(loud_count - 1, 0)

      if loud_count > STATE_CHANGE_CHALLENGE:
        loud = True
        loud_count = 0
      elif loud_count < -STATE_CHANGE_CHALLENGE:
        loud = False
        loud_count = 0

      self.loud = loud
      self.loud_count = loud_count

      self.volume = volume
      self.interpolated = interpolated

    except IOError:
      pass
