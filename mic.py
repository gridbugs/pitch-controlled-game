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
pygame.display.set_caption('Hello, World!')
while True:
    for event in pygame.event.get():
        if event.type == QUIT:

            stream.stop_stream()
            stream.close()
            p.terminate()

            pygame.quit()
            sys.exit()

    try:

        data_str = stream.read(CHUNK)
        data_time_domain = fromstring(data_str, dtype=short)
        data_l = data_time_domain[1::2]
        data_freq_domain = fft(data_l)[:len(data_l)/2]

        surface.fill(BLACK)

        freq = map(lambda x: x/1000, map(int, map(abs, data_freq_domain)))
        interpolated = log_interpolate(
            map(lambda x: max(x, 300) - 300,
            map(lambda x:
              math.log(x+1)*40,
              freq
            )),
            map(lambda x: RES * x, range(WIDTH/RES)),
            110
        )

        best = highest_point(interpolated)
        if best[1] > 80 and best[1] > 80:
          x = (best[0] - 80) * 4
          y = best[1] * 2
          pygame.draw.line(surface, (255, 255, 255),
            (x, HEIGHT), (x, HEIGHT-y), 5)

        pygame.display.update()

    except IOError:
        pass

