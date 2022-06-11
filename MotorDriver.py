#from pyb import PWM
from pyb import Pin
from pyb import Timer
from pyb import SPI
import pyb
import micropython
import math
import time

# tim_num is 1-14, last time we used timer 7, we might try 1 for funsies
# using PA8 utilizes MC0, our clock control pin
# this currently outputs 20MHz

# make spi object, SPI2, and start runnning it this way
# chip select and enable are pins we have to get going

class TMC4210_mass_manipulator():
    def __init__(self):
        self.en1 = Pin(Pin.cpu.B7, mode = Pin.OUT_PP)
        self.cs1 = Pin(Pin.cpu.B6, mode = Pin.OUT_PP)
        self.en2 = Pin(Pin.cpu.C7, mode = Pin.OUT_PP)
        self.cs2 = Pin(Pin.cpu.B9, mode = Pin.OUT_PP)
        self.spi = SPI(2, SPI.CONTROLLER, baudrate = 115200, polarity = 1, phase = 1, bits = 32, firstbit = SPI.MSB)

    def find_PMulPDiv(self, a_max, ramp_div, pulse_div, p_reduction):
        pm = -1
        pd = -1
        p_ideal = a_max / (2 ** (ramp_div-pulse_div) * 128)
        p = a_max / (128 * 2 ** (ramp_div-pulse_div))
        p_reduced = p *(1.0 - p_reduction)
       
        for pdiv in range(14):
            pmul = (int) (p_reduced * 8  * 2 ** pdiv) - 128
            if ((0 <= pmul) and (pmul <= 127)):
                pm = pmul + 128
                pd = pdiv
               
        pmul = pm
        pdiv = pd
        p_best = pm/2**(pd+3)
       
        return pmul, pdiv, p_best

    def start_motor_2(self, pmul, pdiv, a_max, ramp_div, pulse_div):
        send_buf = bytearray(4)
       
        ''' Send en_sd as 1 '''
        send_buf[0] = 0b01101000
        send_buf[1] = 0x00
        send_buf[2] = 0x00
        send_buf[3] = 0x20
        self.cs2.low()    
        #print('Pre en_sd: ', send_buf)
        self.spi.send(send_buf, timeout = 5000)
        self.cs2.high()    

        ''' Setting velocity parameters, V_MIN and V_MAX '''
        #send_buf = ([0b00000100, 0x00, 0b 0000 00 10 bits of Vmin follow])
        # setting V_Min
        send_buf = bytearray([0b00000100, 0x00, 0x00, 0x02])
        self.cs2.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs2.high()    

        # setting V_Max
        send_buf = bytearray([0b00000110, 0x00, 0x00, 0x03])
        self.cs2.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs2.high()  

        # set clock pre dividers Pulse_Div and Ramp_Div, arbitrarily set to 0 for both for now
        # set Pulse_div, Ramp_div, 0011, 0011, Matteo's suggestion
        pulse_div = 0b0011
        ramp_div = 0b0011
        pulse_and_ramp = (pulse_div << 4) | ramp_div
        print('pulse and ramp: ', bin(pulse_and_ramp))
        send_buf = bytearray([0b00011000, 0x00, pulse_and_ramp, 0x00])
        self.cs2.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs2.high()  
               
       
        # set A_Max with PMUL and PDiv set A_Max
        a_max_first = a_max >> 8
        a_max_second = a_max & 0xFF
        send_buf = bytearray([0b00001100, 0x00, a_max_first, a_max_second])
        self.cs2.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs2.high()

        # set Pmul and Pdiv
        #print('pmul: ', pmul)
        pmul_send = pmul | 0x80
        send_buf = bytearray([0b00010010, 0x00, pmul_send, pdiv])
        self.cs2.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs2.high()

        # set Ramp Mode = 0b00, lp and REF_CONF are read-only bits I believe, and R_M is
        send_buf = bytearray([0b00010000, 0x00, 0x00, 0x00])
        self.cs2.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs2.high()        


        # set mot1r to 0 to not use left and right reference switch
        send_buf = bytearray([0b01111110, 0b00100000, 0x02, 0x00])
        self.cs2.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs2.high()
       

    def start_motor_1(self, pmul, pdiv, a_max, ramp_div, pulse_div):
        send_buf = bytearray(4)
       
        ''' Send en_sd as 1 '''
        send_buf[0] = 0b01101000
        send_buf[1] = 0x00
        send_buf[2] = 0x00
        send_buf[3] = 0x20
        self.cs1.low()    
        #print('Pre en_sd: ', send_buf)
        self.spi.send(send_buf, timeout = 5000)
        self.cs1.high()    

        ''' Setting velocity parameters, V_MIN and V_MAX '''
        #send_buf = ([0b00000100, 0x00, 0b 0000 00 10 bits of Vmin follow])
        # setting V_Min
        send_buf = bytearray([0b00000100, 0x00, 0x00, 0x02])
        self.cs1.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs1.high()    

        # setting V_Max
        send_buf = bytearray([0b00000110, 0x00, 0x00, 0x03])
        self.cs1.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs1.high()  

        # set clock pre dividers Pulse_Div and Ramp_Div, arbitrarily set to 0 for both for now
        # set Pulse_div, Ramp_div, 0011, 0011, Matteo's suggestion
        pulse_div = 0b0011
        ramp_div = 0b0011
        pulse_and_ramp = (pulse_div << 4) | ramp_div
        print('pulse and ramp: ', bin(pulse_and_ramp))
        send_buf = bytearray([0b00011000, 0x00, pulse_and_ramp, 0x00])
        self.cs1.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs1.high()  
               
       
        # set A_Max with PMUL and PDiv set A_Max
        a_max_first = a_max >> 8
        a_max_second = a_max & 0xFF
        send_buf = bytearray([0b00001100, 0x00, a_max_first, a_max_second])
        self.cs1.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs1.high()

        # set Pmul and Pdiv
        #print('pmul: ', pmul)
        pmul_send = pmul | 0x80
        send_buf = bytearray([0b00010010, 0x00, pmul_send, pdiv])
        self.cs1.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs1.high()

        # set Ramp Mode = 0b00, lp and REF_CONF are read-only bits I believe, and R_M is
        send_buf = bytearray([0b00010000, 0x00, 0x00, 0x00])
        self.cs1.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs1.high()        


        # set mot1r to 0 to not use left and right reference switch
        send_buf = bytearray([0b01111110, 0b00100000, 0x02, 0x00])
        self.cs1.low()        
        self.spi.send(send_buf, timeout=5000)
        self.cs1.high()
   
    def glizzy_grip(self):
        Pinnie = Pin(Pin.cpu.A5, mode=Pin.OUT_PP)
        tim1 = Timer(8)
        tim1.init(freq = 500)
        ch1 = tim1.channel(1, pin = Pinnie, mode = Timer.PWM, pulse_width = 2)

        count = 0
        while count <= 2000:
            ch1.pulse_width_percent(90)
            count += .1
       
        count = 0
        while count <= 920:
            ch1.pulse_width_percent(15)
            count += .1
       
        ch1.pulse_width_percent(25)

def main():
    tim = pyb.Timer(8)
    tim.init(period = 3, prescaler = 0)
    PC6 = Pin(Pin.cpu.C6, mode = Pin.OUT_PP)    
    clk = tim.channel(1, pin = PC6, mode =Timer.PWM, pulse_width = 2)
   
    Driver = TMC4210_mass_manipulator()

    ''' Enable both drivers '''
    Driver.en1.low()
    Driver.en2.low()
    Driver.cs1.high()
    Driver.cs2.high()
   
    ''' Home Procedure '''
    '''
    send_buf = bytearray([0b0011100, 0x00, 0x00, 0x00])
    Driver.spi.send(send_buf, timeout=5000) # arbitrary last 24 bits for X_latched just to initialize it
    # how to set x1 and x2 for xref and xtraveler?
    '''    

   
    ''' To read from the Type_Version register: technically should give  '''
    send_buf = bytearray(4)
    recv_buf = bytearray(4)
    send_buf[0] = 0x73
   
    Driver.cs1.low()
    Driver.spi.send_recv(send_buf, recv_buf)
    Driver.cs1.high()
   
    print('send_buf: ', send_buf)
    print('recv_buf, Type_Version: ', recv_buf)
   
   
    # Array_ans = Pmul, Pdiv, Pbest
    # Ramp Div and Pulse Div depend on velocity.
    # Ramp_Div >= Pulse_div - 1
    # Large Ramp_div = slow acceleration, large Pulse_div = low velocity
    # A_max_lower = 2 ^ (Ramp_div - Pulse_div - 1)
    # A_max_upper = 2 ^ (Ramp_div - Pulse_div + 12) - 1
    a_max = 0b00000000001
    ramp_div = 0b1001
    pulse_div = 0b0001
    array_ans = Driver.find_PMulPDiv(a_max, ramp_div, pulse_div, .01)

    pmul = array_ans[0]
    pdiv = array_ans[1]
   
    Driver.start_motor_1(pmul, pdiv, a_max, ramp_div, pulse_div)
    Driver.start_motor_2(pmul, pdiv, a_max, ramp_div, pulse_div)
    '''
    Official Notation:
    Clockwise is 0x0->0xF (Forward)
    Counter Clockwise is 0xF -> 0x0 (Backward)
    Motors 1 and 2 follow this
    '''

    ''' Motor 1: setup a X_Target or V_Target to now run the motor in your choice of ramp mode '''
    send_buf = bytearray([0x00, 0x00,0x00, 0xFF])
    Driver.cs1.low()
    Driver.spi.send(send_buf)
    Driver.cs1.high()

    ''' Motor 2: setup a X_Target or V_Target to now run the motor in your choice of ramp mode '''
    send_buf = bytearray([0x00, 0x00,0x00, 0xFF])
    Driver.cs2.low()
    Driver.spi.send(send_buf)
    Driver.cs2.high()

    Driver.glizzy_grip()


if __name__ == "__main__":
    main()