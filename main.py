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
        del (otaUpdater)
        gc.collect()


class RunUartConnection():
    def __init__(self, baudrate):
        self.run = 0
        self.baudrate = baudrate
        self.remote_buffer = bytearray(26)

        # init UART
        self.init_uart()


    def forward_jacuzzi_to_remote(self):
        while self.run < 10:
            if self.uart1_jacuzzi.any():
                # self.uart2_remote.readinto(self.remote_buffer)
                remote_buffer = self.uart1_jacuzzi.readline()
                print("The bin value is: " + str(remote_buffer))
                print("The hex value is: " + str(ubinascii.hexlify(remote_buffer)))
                print("The base64 value is: " + str(ubinascii.b2a_base64(remote_buffer)))
                array_buffer = bytearray(remote_buffer)
                self.uart2_remote.write(array_buffer)

                self.run += 1


    def test_uart(self):
        while True:
            if self.uart2_remote.any():
                # self.uart2_remote.readinto(self.remote_buffer)
                remote_buffer = self.uart2_remote.readline()

                # self.f.write(str(remote_buffer))
                print("The remote bin value is: " + str(remote_buffer) + "\n" + str(bytearray(remote_buffer)))
                print("The remote hex value is: " + str(ubinascii.hexlify(remote_buffer)))
                print("The remote base64 value is: " + str(ubinascii.b2a_base64(remote_buffer)))

                self.uart1_jacuzzi.write(remote_buffer)

            if self.uart1_jacuzzi.any():
                jacuzzi_buffer = self.uart1_jacuzzi.readline()

                print("The jacuzzi bin value is: " + str(jacuzzi_buffer) + "\n" + str(bytearray(jacuzzi_buffer)))
                print("The jacuzzi hex value is: " + str(ubinascii.hexlify(jacuzzi_buffer)))
                print("The jacuzzi base64 value is: " + str(ubinascii.b2a_base64(jacuzzi_buffer)))

                self.uart2_remote.write(bytearray(jacuzzi_buffer))

            # jacuzzi_buffer = bytearray("", 'utf-8')

            # jacuzzi_buffer = self.uart1_jacuzzi.read()
            # remote_buffer = self.uart2_remote.read()

            # if jacuzzi_buffer is not "":
            #    print("uart1")
            #    print(jacuzzi_buffer)
            #    if jacuzzi_buffer is not None:
            #        print(ubinascii.hexlify(jacuzzi_buffer))
            #        print(ubinascii.b2a_base64(jacuzzi_buffer))

            # if remote_buffer is not "":
            #    # print("uart2")
            #     if remote_buffer is not None:
            #         print(remote_buffer)
            #         print(ubinascii.hexlify(remote_buffer))
            #         print(ubinascii.b2a_base64(remote_buffer))

    def init_uart(self):
        # uart1 = Jacuzzi
        self.uart1_jacuzzi = UART(1, baudrate=9600, tx=14, rx=4, bits=8, stop=1, parity=None)

        # uart2 = remote
        self.uart2_remote = UART(2, baudrate=9600, tx=15, rx=27, bits=8, stop=1, parity=None)
        # print(" baudrate inits at = " + str(self.baudrate))

    def de_init_uart(self):
        self.uart1_jacuzzi.deinit()
        self.uart2_remote.deinit()


def startApp():
    baud_9600 = RunUartConnection(baudrate=4800)
    baud_9600.test_uart()
    baud_9600.de_init_uart()


connectToWifiAndUpdate()
startApp()
