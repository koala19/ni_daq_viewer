import numpy as np
import matplotlib.pyplot as plt

sf = 1000
samples = 20000

t = np.linspace(0, samples * (1/sf), num=samples)
signal = 0.15*np.sin(2*np.pi*159.2*t)

sp = np.fft.rfft(signal, n=signal.shape[-1])
sp = np.abs(sp.real)
freq = np.fft.rfftfreq(n=signal.shape[-1], d=1/sf)

fig, ax = plt.subplots(1, 2)
ax[0].plot(t, signal)
ax[1].stem(freq, sp, use_line_collection=True)
plt.show()


print(freq[np.argmax(sp)])
