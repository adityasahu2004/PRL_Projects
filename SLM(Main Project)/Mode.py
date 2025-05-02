import tkinter as tk
from screeninfo import get_monitors
from PIL import Image, ImageTk
import numpy as np
import pygetwindow as gw
import threading
import time
import pandas as pd
from scipy.special import factorial, genlaguerre

# ---------------------- Beam Mode Classes ----------------------

class SLM:
    def __init__(self, waveLength, XPix, YPix, pixel, XAngle, YAngle, Lens):
        self.waveLength = waveLength
        self.XPix = XPix
        self.YPix = YPix
        self.pixel = pixel
        self.XAngle = XAngle
        self.YAngle = YAngle
        self.Lens = Lens

class LG:
    def __init__(self, azimuthal, radial, waist, weight, phase, XCenter, YCenter):
        self.type = 'LG'
        self.azimuthal = azimuthal
        self.radial = radial
        self.waist = waist
        self.weight = weight
        self.phase = phase
        self.XCenter = XCenter
        self.YCenter = YCenter

# ---------------------- SLM Field and Hologram Calculation ----------------------

def calculateField(SLMz, modes):
    waveLength = SLMz.waveLength
    XPix = SLMz.XPix
    YPix = SLMz.YPix
    pixel = SLMz.pixel
    kk = 2 * np.pi / waveLength

    xi = np.linspace(start=-XPix / 2, stop=XPix / 2 - 1, num=XPix)
    yi = np.linspace(start=-YPix / 2, stop=YPix / 2 - 1, num=YPix)
    xx, yy = np.meshgrid(xi * pixel, yi * pixel)
    rad = np.sqrt(xx ** 2 + yy ** 2)
    phi = np.arctan2(yy, xx)

    Field = np.zeros((YPix, XPix), dtype=complex)
    for mode in modes:
        if mode.type == 'LG':
            pp = mode.radial
            ll = mode.azimuthal
            w0 = mode.waist
            zz = 1e-9

            zR = np.pi * w0 ** 2 / waveLength
            psi = (abs(ll) + 2 * pp + 1) * np.arctan2(zz, zR)
            wz = w0 * np.sqrt(1.0 + (zz / zR) ** 2)
            Rz = zz * (1.0 + (zR / zz) ** 2)
            U0 = np.sqrt(2 * factorial(pp) / (np.pi * factorial(pp + abs(ll))))
            U1 = 1 / wz
            U2 = (np.sqrt(2) * rad / wz) ** abs(ll)
            U3 = np.exp(-(rad / w0) ** 2)
            U4 = genlaguerre(pp, abs(ll))(2 * (rad / wz) ** 2)
            U5 = np.exp(-1j * kk * rad ** 2 / Rz)
            U6 = np.exp(-1j * ll * phi)
            U7 = np.exp(1j * psi)

            ModeField = U0 * U1 * U2 * U3 * U4 * U5 * U6 * U7
            Field += mode.weight * ModeField * np.exp(1j * mode.phase)
    return Field

def calculateHologram(SLMz, Field):
    waveLength = SLMz.waveLength
    XPix = SLMz.XPix
    YPix = SLMz.YPix
    pixel = SLMz.pixel
    kk = 2 * np.pi / waveLength
    XAngle = SLMz.XAngle
    YAngle = SLMz.YAngle

    xi = np.linspace(start=-XPix / 2, stop=XPix / 2 - 1, num=XPix)
    yi = np.linspace(start=-YPix / 2, stop=YPix / 2 - 1, num=YPix)
    xx, yy = np.meshgrid(xi * pixel, yi * pixel)

    scalingData = np.array(pd.read_csv('fx2.csv', sep=',', header=None).values)
    intensity = abs(Field) / np.max(abs(Field))
    aux = np.round(intensity * 800)
    ff = np.zeros((YPix, XPix))

    for mh in range(YPix):
        for nh in range(XPix):
            temp = int(aux[mh][nh])
            ff[mh][nh] = scalingData[0][temp]

    correction = True
    if correction:
        Hologram = ff * ((np.angle(Field) + kk * np.sin(XAngle) * xx + kk * np.sin(YAngle) * yy) % (2 * np.pi))
    else:
        Hologram = intensity * ((np.angle(Field) + kk * np.sin(XAngle) * xx + kk * np.sin(YAngle) * yy) % (2 * np.pi))

    SLMPattern = Hologram * 255 / np.max(Hologram)
    return SLMPattern

# ---------------------- Display Logic ----------------------

def display_hologram(hologram_array, delay=10):
    monitors = get_monitors()
    if not monitors:
        print("No monitors detected.")
        return
    
    monitor = monitors[-1]
    screen_width, screen_height = monitor.width, monitor.height

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    label = tk.Label(root)
    label.pack()

    image = Image.fromarray(hologram_array.astype(np.uint8))
    img_tk = ImageTk.PhotoImage(image)
    label.config(image=img_tk)
    label.image = img_tk

    root.geometry("1920x1080+1592+0")
    root.update()
    window = gw.getWindowsWithTitle("Tk")[0]
    window.moveTo(monitor.x, monitor.y)

    def close_after_delay():
        time.sleep(delay)
        root.destroy()

    threading.Thread(target=close_after_delay, daemon=True).start()
    root.mainloop()

# ---------------------- Main Execution ----------------------

if __name__ == "__main__":
    SLM1 = SLM(waveLength=633e-9, XPix=1920, YPix=1080, pixel=8e-6, XAngle=np.sin(10e-3), YAngle=0, Lens=1000)
    mode1 = LG(azimuthal=4, radial=3, waist=500e-6, weight=1, phase=0, XCenter=0, YCenter=0)
    

    Field = calculateField(SLM1, modes=[mode1])
    Hologram = calculateHologram(SLM1, Field)

    display_hologram(Hologram, delay=1000)
