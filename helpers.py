from config import *
import math

# This function takes a collection of data given as a list of floats,
# and returns those numers plotted on a log scale. The resulting data
# can be plotted on with 'output_range' as the x axis. The input data
# is linearly interpolated between points in the output_range to get
# the resulting data.
# data: points to be plotted (not logged)
# output_range: the x values at which plots will occur
def log_interpolate(data, output_range, x_scale):

  # find the points on the x axis where the given data will be plotted
  logged_range = map(lambda x: math.log(x + 1)*x_scale, range(len(data)))

  # index into the logged x range
  i_log = 0

  # index into the output x range
  i_out = 0

  # create the array to hold the resulting data
  output_data = [0] * len(output_range)

  # zero fill the desired output if there are any unknown requests
  while output_range[i_out] < logged_range[0]:
    i_out += 1

  # eat any logged x points before the output points begin
  while logged_range[i_log] < output_range[0]:
    i_log += 1

  # outer loop - for each logged range value
  while i_log < len(logged_range) and i_out < len(output_range):
    # determine the gradient between the current and previous logged value
    dy = data[i_log] - data[i_log-1]
    dx = logged_range[i_log] - logged_range[i_log-1]
    gradient = float(dy)/float(dx)
    y_icp = data[i_log] - gradient * logged_range[i_log]

    # interpolate the values between the current and last logged values
    while i_out < len(output_range) and output_range[i_out] < logged_range[i_log]:
      output_data[i_out] = gradient * output_range[i_out] + y_icp
      i_out += 1

    # increment the outer loop counter
    while i_log < len(logged_range) and i_out < len(output_range) and not(output_range[i_out] < logged_range[i_log]):
      i_log += 1

  return map(int, output_data)


def display_freq(interpolated, base, offset, colour):

  x_val = 0

  for i in interpolated:
    x_pos = x_val
    y_pos = i
    pygame.draw.line(surface, colour, (x_pos, HEIGHT), (x_pos, HEIGHT - y_pos))
    x_val += + RES


