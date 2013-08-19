import pygame, sys
from pygame.locals import *

from numpy import fromstring, short, angle
from numpy.fft import fft
import pyaudio
import wave
import math

from config import *
from helpers import *

CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.4
WAVE_OUTPUT_FILENAME = "output.wav"
print "starting"
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

def highest_point(data):
  max_point = 0
  best_idx = 0
  for i in range(0, len(data)):
    if data[i] > max_point:
      max_point = data[i]
      best_idx = i
  return (best_idx, max_point)


pygame.init()
surface = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Microphone Pitch')
while True:
    for event in pygame.event.get():
        if event.type == QUIT:

            stream.stop_stream()
            stream.close()
            p.terminate()

            pygame.quit()
            sys.exit()

    try:

        # get some data from the mic as a string
        data_str = stream.read(CHUNK)

        # convert the string to an integer array representing amplitude over time
        data_time_domain = fromstring(data_str, dtype=short)

        # just use the left channel
        data_l = data_time_domain[1::2]

        # discrete fourier transform to convert the data into a complex number array
        # representing the amplidue of the different frequencies in the sample
        data_freq_domain = fft(data_l)[:len(data_l)/2]


        interpolated =
          log_interpolate(                 # evenly distribute values on the x axis
          map(lambda x: max(x, 300) - 300, # filter out low amplitudes
          map(lambda x: math.log(x+1)*40,  # evenly distribute values on the y axis
          map(abs, data_freq_domain))),    # get the absolute value of each frequency domain value
          map(lambda x: RES * x, range(WIDTH/RES)), # x axis points we're interested in
          110   # scale in the x axis
        )

        # clear the screen
        surface.fill(BLACK)

        best = highest_point(interpolated) # find the loudest frequency
        if best[0] > 80 and best[1] > 80:  # filter out low frequencies quiet noises
          x = (best[0] - 80) * 4           # horizontal scaling
          y = best[1]

          # draw the line
          pygame.draw.line(surface, (255, 255, 255),
            (x, HEIGHT), (x, HEIGHT-y), 5)

        pygame.display.update()

    except IOError:
        # skip over errors
        pass

