# main.py


import numpy as np
from scipy.fftpack import fft, ifft
from scipy.signal import butter, lfilter
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt



def calc_fft(time_sec, vibr):
    """Compute the single-sided amplitude spectrum of a time-domain signal using FFT.

    The sampling interval is derived from the mean difference between consecutive
    time stamps, so non-uniform sampling is handled gracefully as long as the
    average interval is representative.

    Args:
        time_sec (array-like): Time stamps in seconds. Must be the same length as ``vibr``.
        vibr (array-like): Vibration (or any time-domain) signal in its original units.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]:
            - **freqhz** – Frequency axis in Hz (single-sided, length N/2).
            - **vibr_fft** – Single-sided amplitude spectrum in the same units as ``vibr``.

    Example:
        >>> import numpy as np
        >>> from siglyser import calc_fft
        >>> t = np.linspace(0, 1, 1000)
        >>> signal = np.sin(2 * np.pi * 50 * t)
        >>> freq, amp = calc_fft(t, signal)
    """
    datalength_fft = len(time_sec)
    datalengthby2 = int(datalength_fft/2)
    timeavgcalc = np.array([], dtype = np.float64)
    time_sec_i = time_sec[1:]
    time_sec_i_1 = time_sec[:-1]
    timeavgcalc = time_sec_i - time_sec_i_1
    sigint_avg = np.mean(timeavgcalc)
    siginf = 1/(datalength_fft*sigint_avg)
    freqhztemp = np.arange(0,datalength_fft,dtype = np.float64)
    freqhz = freqhztemp*siginf
    freqhz = freqhz[0:datalengthby2]
    vibr_fft = np.abs(fft(vibr,axis = -1))
    vibr_fft = ((vibr_fft[0:datalengthby2])/datalength_fft)*2
    return freqhz,vibr_fft



def calc_3dfft(time_sec, speed_rpm, vibr):
    """Compute a speed-frequency amplitude map (3D FFT / waterfall) for rotating machinery.

    The signal is segmented into engine cycles (one cycle = 720° of crankshaft rotation).
    An FFT is computed for each cycle, and the per-cycle spectra are interpolated onto a
    common frequency grid using Akima interpolation so the result can be plotted as a
    contour or surface map with speed on one axis and frequency on the other.

    Args:
        time_sec (array-like): Time stamps in seconds.
        speed_rpm (array-like): Instantaneous rotational speed in RPM, same length as ``time_sec``.
        vibr (array-like): Vibration signal in its original units, same length as ``time_sec``.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]:
            - **freq3dx** – 2-D frequency grid (Hz) shaped (n_cycles, n_freq).
            - **freq3dy** – 2-D speed grid (RPM) shaped (n_cycles, n_freq).
            - **freq3dz** – 2-D amplitude grid in the same units as ``vibr``, shaped (n_cycles, n_freq).

    Note:
        The three returned arrays are intended to be passed directly to :func:`plot_3dfft`
        or to ``matplotlib.pyplot.contourf`` / ``matplotlib.pyplot.plot_surface``.

    Example:
        >>> from siglyser import calc_3dfft, plot_3dfft
        >>> freq_x, speed_y, amp_z = calc_3dfft(time, rpm, vibration)
        >>> plot_3dfft(freq_x, speed_y, amp_z, xlim=(0, 1000), ylim=(500, 6000))
    """
    time_sec_i = time_sec[1:]
    time_sec_i_1 = time_sec[:-1]
    speed_rpm_i_1 = speed_rpm[:-1]
    cccum2_vect_temp = (((speed_rpm_i_1/2)/60)*360*(time_sec_i-time_sec_i_1))
    cccum2_vect_temp = np.insert(cccum2_vect_temp,0,0)
    cccum2_vect_temp = np.cumsum(cccum2_vect_temp)
    cycle_vect= np.floor(((cccum2_vect_temp/720.0))+1)
    ccrel2_vect_temp = cccum2_vect_temp-(cycle_vect-1)*720
    maxcy_vect = max(cycle_vect)
    alldata_vect = np.stack((cycle_vect, time_sec, speed_rpm, vibr), axis = 1)
    e, inds = np.unique(alldata_vect[:,0], return_index=True)
    alldata_cycle_vect = np.split(alldata_vect, inds)[1:]
    speedindex = [(np.mean(alldata_cycle_vect[int(j)-1][:,2])) for j in e]

    freqhztemp_vibrffttemp = [(calc_fft((alldata_cycle_vect[int(j)-1][:,1]), (alldata_cycle_vect[int(j)-1][:,3]))) for j in e]
    freqhztemp = [freqhztemp_vibrffttemp[int(j)-1][0]  for j in e]
    vibrffttemp = [freqhztemp_vibrffttemp[int(j)-1][1]  for j in e]
    freqhz3d = np.array([], dtype = np.float64)
    vibrfft3d = np.array([], dtype = np.float64)
    freqhz3d = freqhztemp
    vibrfft3d = vibrffttemp
    freqhz3d = freqhz3d[:-1]
    vibrfft3d = vibrfft3d[:-1]
    e_1 = e[:-1]
    freqvibr3d_freq_interptemp = np.array([], dtype = np.float64)
    freqvibr3d_vibr_interptemp = np.array([], dtype = np.float64)
    freqvibr3d_vibr_interp = np.array([], dtype = np.float64)
    funcakimainterp = [(sp.interpolate.Akima1DInterpolator(freqhz3d[int(j)-1], vibrfft3d[int(j)-1])) for j in e_1] 
    tempceilval = int(max(e_1)-1)
    maxfreqval = ((np.around(max(freqhz3d[tempceilval]),decimals=-3)))
    freqvibr3d_freq_interptemp = np.array([np.arange(0, maxfreqval+0.1, 0.1)])
    freqvibr3d_vibr_interptemp = [(funcakimainterp[int(j)-1](freqvibr3d_freq_interptemp)) for j in e_1]
    freqvibr3d_freq_interp = freqvibr3d_freq_interptemp[0]
    freqvibr3d_vibr_interp = [(np.hstack((freqvibr3d_vibr_interp, freqvibr3d_vibr_interptemp[int(j)-1][0]))) for j in e_1]
    #freqvibr3d_vibr_interp = freqvibr3d_vibr_interp[:-1]
    lengrid = len(freqvibr3d_freq_interp)
    

    freq3dx = np.tile(freqvibr3d_freq_interp,(tempceilval+1,1))
    freq3dy = np.transpose(np.tile(speedindex[:-1], (lengrid,1)))
    freq3dz = freqvibr3d_vibr_interp
    freq3dz = np.array([arr.tolist() for arr in freq3dz])
    maxz = np.amax(freq3dz)

        
    return freq3dx, freq3dy, freq3dz

def calc_rms_ampl(time_sec, speed_rpm, vibr):
    """Compute RMS and peak-to-peak amplitude of a vibration signal per engine cycle vs speed.

    The signal is segmented into engine cycles (720° per cycle) using the instantaneous
    speed trace. For each cycle the mean speed, RMS value, and half peak-to-peak amplitude
    are calculated, giving a speed-domain view of signal strength useful for run-up/run-down
    analyses.

    Args:
        time_sec (array-like): Time stamps in seconds.
        speed_rpm (array-like): Instantaneous rotational speed in RPM, same length as ``time_sec``.
        vibr (array-like): Vibration signal in its original units, same length as ``time_sec``.

    Returns:
        tuple[list, list, list]:
            - **speedindex** – Mean speed (RPM) for each cycle.
            - **rms_vibr** – RMS value of the vibration signal for each cycle, in the same units as ``vibr``.
            - **ampl_vibr** – Half peak-to-peak amplitude ``(max - min) / 2`` for each cycle, in the same units as ``vibr``.

    Example:
        >>> from siglyser import calc_rms_ampl
        >>> speed, rms, amplitude = calc_rms_ampl(time, rpm, vibration)
        >>> import matplotlib.pyplot as plt
        >>> plt.plot(speed, rms, label='RMS')
        >>> plt.plot(speed, amplitude, label='Amplitude')
        >>> plt.xlabel('Speed (RPM)'); plt.ylabel('Vibration'); plt.legend(); plt.show()
    """
    time_sec_i = time_sec[1:]
    time_sec_i_1 = time_sec[:-1]
    speed_rpm_i_1 = speed_rpm[:-1]
    cccum2_vect_temp = (((speed_rpm_i_1/2)/60)*360*(time_sec_i-time_sec_i_1))
    cccum2_vect_temp = np.insert(cccum2_vect_temp,0,0)
    cccum2_vect_temp = np.cumsum(cccum2_vect_temp)
    cycle_vect= np.floor(((cccum2_vect_temp/720.0))+1)
    ccrel2_vect_temp = cccum2_vect_temp-(cycle_vect-1)*720
    maxcy_vect = max(cycle_vect)
    alldata_vect = np.stack((cycle_vect, time_sec, speed_rpm, vibr), axis = 1)
    e, inds = np.unique(alldata_vect[:,0], return_index=True)
    alldata_cycle_vect = np.split(alldata_vect, inds)[1:]
    speedindex = [(np.mean(alldata_cycle_vect[int(j)-1][:,2])) for j in e]
    rms_vibr = [(np.sqrt(np.mean(np.square((alldata_cycle_vect[int(j)-1][:,3]))))) for j in e]
    ampl_vibr = [((max(((alldata_cycle_vect[int(j)-1][:,3])))-min(((alldata_cycle_vect[int(j)-1][:,3]))))/2) for j in e]
    return speedindex, rms_vibr, ampl_vibr

def plot_3dfft(x, y, z, xlim, ylim):
    """Plot a speed-frequency amplitude map as a filled contour plot.

    Renders the output of :func:`calc_3dfft` as a ``matplotlib`` filled contour plot
    with a jet colormap and a colorbar scaled to the maximum amplitude in ``z``.
    The plot is drawn on the current active matplotlib axes.

    Args:
        x (numpy.ndarray): 2-D frequency grid in Hz, as returned by :func:`calc_3dfft`.
        y (numpy.ndarray): 2-D speed grid in RPM, as returned by :func:`calc_3dfft`.
        z (numpy.ndarray): 2-D amplitude grid, as returned by :func:`calc_3dfft`.
        xlim (tuple[float, float]): Frequency axis display limits in Hz, e.g. ``(0, 1000)``.
        ylim (tuple[float, float]): Speed axis display limits in RPM, e.g. ``(500, 6000)``.

    Example:
        >>> from siglyser import calc_3dfft, plot_3dfft
        >>> import matplotlib.pyplot as plt
        >>> freq_x, speed_y, amp_z = calc_3dfft(time, rpm, vibration)
        >>> plot_3dfft(freq_x, speed_y, amp_z, xlim=(0, 1000), ylim=(500, 6000))
        >>> plt.xlabel('Frequency (Hz)'); plt.ylabel('Speed (RPM)'); plt.show()
    """
    maxz = np.amax(z)
    CS = plt.contourf(x,y, z, 10, cmap = plt.cm.jet)
    
    norm = mpl.colors.Normalize(0,maxz,10)
    
    barcolors = plt.cm.ScalarMappable(norm, cmap="jet")
    bounds = np.linspace(0,maxz,10)
    
    plt.colorbar(cmap = "jet", norm=norm, orientation='vertical', spacing = 'proportional', ticks=bounds, boundaries=bounds)
    plt.xlim(xlim)
    plt.ylim(ylim)
