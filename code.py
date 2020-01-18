import board
import neopixel
import time
import audiobusio
import displayio
import random
import digitalio
import array
from teaandtechtime_fft import spectrogram, fft, ifft
from math import sin, pi

display = board.DISPLAY

# Create a bitmap with heatmap colors
bitmap = displayio.Bitmap(display.width, display.height, 56)

# Create a heatmap color palette
palette = displayio.Palette(56)
palette[55]= 0xFF0000
palette[54]= 0xFF0a00
palette[53]= 0xFF1400
palette[52]= 0xFF1e00
palette[51]= 0xFF2800
palette[50]= 0xFF3200
palette[49]= 0xFF3c00
palette[48]= 0xFF4600
palette[47]= 0xFF5000
palette[46]= 0xFF5a00
palette[45]= 0xFF6400
palette[44]= 0xFF6e00
palette[43]= 0xFF7800
palette[42]= 0xFF8200
palette[41]= 0xFF8c00
palette[40]= 0xFF9600
palette[39]= 0xFFa000
palette[38]= 0xFFaa00
palette[37]= 0xFFb400
palette[36]= 0xFFbe00
palette[35]= 0xFFc800
palette[34]= 0xFFd200
palette[33]= 0xFFdc00
palette[32]= 0xFFe600
palette[31]= 0xFFf000
palette[30]= 0xFFfa00
palette[29]= 0xfdff00
palette[28]= 0xd7ff00
palette[27]= 0xb0ff00
palette[26]= 0x8aff00
palette[25]= 0x65ff00
palette[24]= 0x3eff00
palette[23]= 0x17ff00
palette[22]= 0x00ff10
palette[21]= 0x00ff36
palette[20]= 0x00ff5c
palette[19]= 0x00ff83
palette[18]= 0x00ffa8
palette[17]= 0x00ffd0
palette[16]= 0x00fff4
palette[15]= 0x00e4ff
palette[14]= 0x00d4ff
palette[13]= 0x00c4ff
palette[12]= 0x00b4ff
palette[11]= 0x00a4ff
palette[10]= 0x0094ff
palette[9]= 0x0084ff
palette[8]= 0x0074ff
palette[7]= 0x0064ff
palette[6]= 0x0054ff
palette[5]= 0x0044ff
palette[4]= 0x0032ff
palette[3]= 0x0022ff
palette[2]= 0x0012ff
palette[1]= 0x0002ff
palette[0]= 0x0000ff


# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette,
                            width = 1,
                            height = display.height,
                            tile_width = display.width,
                            tile_height = 1)

# Create a Group
group = displayio.Group()

# Add the TileGrid to the Group
group.append(tile_grid)

# Add the Group to the Display
display.show(group)

# instantiate board mic
mic = audiobusio.PDMIn(
    board.D1,
    board.D12,
    sample_rate=16000,
    bit_depth=16
)

#assign the fft size we want to use
fft_size = 256
#use some extra sample to account for the mic startup
samples_bit = array.array('H', [0] * (fft_size+3))

#Uncomment this code to test the fft library
"""
#create basic data structure to hold samples
samples = array.array('f', [0] * fft_size)

#assign a sinusoid to the samples
frequency = 63  # Set this to the Hz of the tone you want to generate.
for i in range(fft_size):
    samples[i] = sin(pi * 2 * i / (fft_size/frequency))

#create complex samples
test_complex_samples = []
for n in range(fft_size):
    test_complex_samples.append(((float(samples[n]))-1 + 0.0j))

#compute fft of complex samples
test_fft = fft(test_complex_samples)

#compute ifft of the fft values
test_ifft = ifft(test_fft)

#print computed values for testing and verification
#print complex samples
print("samples")
for i in test_complex_samples:
    print(i)
    time.sleep(.01)

#print fft values
print("fft")
for i in test_fft:
    print(i)
    time.sleep(.01)

#print ifft values
print("ifft")
for i in test_ifft:
    print(i)
    time.sleep(.01)

#compute absolut value of the error per sample
print("error")
for i in range(fft_size):
    print(abs(test_ifft[i] - test_complex_samples[i]))
    time.sleep(.01)
"""

# Main Loop
i = 0
max_all = 1

while True:
    # Draw even more pixels
    for y in range(display.height):
        mic.record(samples_bit, len(samples_bit))
        complex_samples = []
        for n in range(fft_size):
            complex_samples.append((float(samples_bit[n+3])/32768.0) + 0.0j)
        #compute spectrogram
        spectrogram1 = spectrogram(complex_samples)
        spectrogram1 = spectrogram1[1:(fft_size//2)-1]
        min_curr = abs(min(spectrogram1))
        max_curr = max(spectrogram1)+min_curr

        if max_curr > max_all:
            max_all = max_curr
        else:
            max_curr = max_curr-1

        # Slide tile window
        for line in range(display.height):
            tile_grid[line] = (display.height-y-1+line)%display.height

        # Plot FFT
        offset = (display.width-len(spectrogram1))//2
        for x in range(len(spectrogram1)):
            bitmap[x+offset, display.height-y-1] = int(((spectrogram1[x]+min_curr)/(max_all))*55)
