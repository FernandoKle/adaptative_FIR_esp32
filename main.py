# Filtro adaptativo en MicroPython
from machine import Timer, Pin, ADC, DAC
import math

#try:
#    from ulab import numpy as np
#except ImportError:
#    import numpy as np

# ADC0 - Pin 3 de la placa
adc_sen = ADC(Pin(36)) 
# ADC3 - Pin 4 de la placa
adc_ruido = ADC(Pin(39)) 

# DAC1 - Pin 9 de la placa - valores: 0 a 255
dac = DAC(Pin(25)) 

Fs = 1000 # Hz
muestreo = Timer(0)

adc_ready = False

def interrupcion_periodica():
    adc_ready = True

#muestreo.init(period=int(1/Fs*1000), mode=Timer.PERIODIC, 
#            callback=lambda t: interrupcion_periodica() )

mu = 0.0000001
N = 10
#w = np.zeros(size=N, dtype=float32) # filtro
#x = np.zeros(size=N, dtype=float32) # ruido
w = [0] * N # filtro
x = [0] * N # ruido

########################## MAIN ###########################

adc_ready=True
while True:
    if adc_ready:
        #adc_ready = False

        sum = 0

        # desplazar x a la izquierda
        for i in range(N-1):
            x[i] = x[i+1]

        # read_uv() es en mV 0 ~ 1100000
        # read_u16() es 0 ~ 65535
        x[N-1] = adc_ruido.read_uv() // 1000
        
        # filtro
        for i in range(N):
            sum += int(w[i] * x[N - 1 - i])
        
        # leemos y
        y = adc_sen.read_uv() // 1000
        e = y - sum
        
        # LMS
        for i in range(N):
            w[i] += 2 * mu * e * x[N - 1 - i]
        
        #if e == math.inf or math.nan:
        #    e = 0.5
        
        # salida
        #salida = int( (e + 255) // 2 )
        salida = y // 4
        if salida > 255:
            salida: int = 255
        if salida < 0:
            salida: int = 0

        dac.write(salida)
        #print("y:",y,"x:",x[-1],"e:",e, "salida:", salida,
        #    "sum:",sum, "\nw:",w,"\n")
        #print("y:",y,"x:",x[-1],"e:",e, "salida:", salida,
        #    "sum:",sum, end='\r')

######################## END MAIN #########################