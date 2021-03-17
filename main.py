import time, machine, network, gc, ubinascii, app.secrets as secrets
from machine import UART

def connectToWifiAndUpdate():
    time.sleep(1)
    print('Memory free', gc.mem_free())

    from app.ota_updater import OTAUpdater

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    otaUpdater = OTAUpdater('https://github.com/kloknibor/mspa-wifi-control', main_dir='app', secrets_file="secrets.py")
    hasUpdated = otaUpdater.install_update_if_available()
    if hasUpdated:
        machine.reset()
    else:
        del(otaUpdater)
        gc.collect()


class RunUartConnection():
    def __init__(self, baudrate):
        self.run = 0
        self.baudrate = baudrate

        # init UART
        self.init_uart()

    def test_uart(self):
        while True:
            #jacuzzi_buffer = bytearray("", 'utf-8')
            #remote_buffer = bytearray("", 'utf-8')
            #jacuzzi_buffer = self.uart1_jacuzzi.read()
            remote_buffer = self.uart2_remote.read()

            #if jacuzzi_buffer is not "":
            #    print("uart1")
            #    print(jacuzzi_buffer)
            #    if jacuzzi_buffer is not None:
            #        print(ubinascii.hexlify(jacuzzi_buffer))
            #        print(ubinascii.b2a_base64(jacuzzi_buffer))

            if remote_buffer is not "":
               # print("uart2")
                if remote_buffer is not None:
                    print(remote_buffer)
                    print(ubinascii.hexlify(remote_buffer))
                    print(ubinascii.b2a_base64(remote_buffer))


    def init_uart(self):
        # uart1 = Jacuzzi
        self.uart1_jacuzzi = UART(1, baudrate=self.baudrate, tx=14, rx=4, bits=7, stop=1, parity=None)

        # uart2 = remote
        self.uart2_remote = UART(2, baudrate=self.baudrate, tx=15, rx=27, bits=7, stop=1, parity=None)
        print(" baudrate inits at = " + str(self.baudrate))

    def de_init_uart(self):
        self.uart1_jacuzzi.deinit()
        self.uart2_remote.deinit()

def startApp():
    baud_9600 = RunUartConnection(baudrate=4800)
    baud_9600.test_uart()
    baud_9600.de_init_uart()


connectToWifiAndUpdate()
startApp()
