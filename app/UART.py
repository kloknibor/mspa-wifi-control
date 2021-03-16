from machine import UART
# uart1 = Jacuzzi
uart1 = UART(1, baudrate=9600, tx=4, rx=14)
# uart2 = remote
uart2 = UART(2, baudrate=9600, tx=15, rx=27)

While True:
 uart1.read()
