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
                self.process_message(remote_buffer)

                if str(remote_buffer) != "b\'\\xa5\\x01\\x00\\xa6\'" and str(
                        remote_buffer) != "b\'\\xa5\\x02\\x00\\xa7\'" and str(
                    remote_buffer) != "b\'\\xa5\\x03\\x00\\xa8\'":
                    # self.f.write(str(remote_buffer))
                    print("The remote bin value is: " + str(remote_buffer) + "\n" + str(bytearray(remote_buffer)))
                    print("The remote hex value is: " + str(ubinascii.hexlify(remote_buffer)))
                    print("The remote base64 value is: " + str(ubinascii.b2a_base64(remote_buffer)))

                    self.uart1_jacuzzi.write(remote_buffer)

            if self.uart1_jacuzzi.any():
                jacuzzi_buffer = self.uart1_jacuzzi.readline()

                if str(jacuzzi_buffer) != "b\'\\xa5\\x01\\x00\\xa6\'" and str(
                        jacuzzi_buffer) != "b\'\\xa5\\x02\\x00\\xa7\'" and str(
                    jacuzzi_buffer) != "b\'\\xa5\\x03\\x00\\xa8\'":
                    print("The jacuzzi bin value is: " + str(jacuzzi_buffer) + "\n" + str(bytearray(jacuzzi_buffer)))
                    print("The jacuzzi hex value is: " + str(ubinascii.hexlify(jacuzzi_buffer)))
                    print("The jacuzzi base64 value is: " + str(ubinascii.b2a_base64(jacuzzi_buffer)))

                self.uart2_remote.write(bytearray(jacuzzi_buffer))

    def init_uart(self):
        # uart1 = Jacuzzi
        self.uart1_jacuzzi = UART(1, baudrate=9600, tx=14, rx=4, bits=8, stop=1, parity=None)

        # uart2 = remote
        self.uart2_remote = UART(2, baudrate=9600, tx=15, rx=27, bits=8, stop=1, parity=None)
        # print(" baudrate inits at = " + str(self.baudrate))

    def de_init_uart(self):
        self.uart1_jacuzzi.deinit()
        self.uart2_remote.deinit()

    def get_temp(self):
        pass
        # \xa5\x06\x00\xab = 0.0 graden en heater en filter aan
        # \xa5\x06\x01\xac = 0.5 graden en heater en filter aan
        # \xa5\x06\x02\xad = 1.0 graden en heater en filter aan
        # \xa5\x06\x03\xae = 1.5 graden
        # \xa5\x06\x04\xaf = 2.0 graden
        # \xa5\x06\x1e\xc9 = 15.0 graden
        # \xa5\x06\x28\xd3 = 20.0 graden
        # \xa5\x06\x3c\xe7 = 30.0 graden
        # \xa5\x06\x50\xfb = 40.0 graden
        # \xa5\x06\x54\xff = 42.0 graden
        # \xa5\x06\x55\x00 = 42.5 graden
        # \xa5\x06\x5f\x0A = 47.5 graden
        # \xa5\x06\x65\x10 = 50.5 graden alles hoger dan dit is E0
        # E1 = Tried to head/filter didn't get acknowledgement

    def protocol(self):
        pass
        # bit1 = Adress?
        # bit2 = function?  x06 = temprature in jacuzzi  x03 = Bubbels aan of uit  x02 = filter aan of uit
        # bit3 = value for function
        # bit4 = value of bit1 + bit2 + bit3

    def bubbel_on(self, message):
        pass
        # bit2 = x03
        # bit3 = x00 is off and x01 is on

    def filter_on(self, message):
        pass
        # bit2 = x02
        # bit3 = x00 is off and x01 is on

    def split_message_to_array(self, message):
        message_str = str(message)
        msg = message_str.split("\'")
        main_msg = msg[1]
        bytes = main_msg.split("\\")

        # check nr of messages
        print(len(bytes))
        single_message = []
        messages = []

        i = 1
        x = 0
        while i < len(bytes):

            single_message.append(bytes[i])
            x += 1
            i += 1

            if x == 4:
                messages.append(single_message)
                x = 0
                single_message = []

        print(messages)
        return messages

    def process_message(self, message):
        # split message to usefull array
        messages_array = self.split_message_to_array(message=message)

        for message in messages_array:
            # check message
            if message[0] == 'xa5':
                hex_val1 = message[0].replace('x', '')
                hex_val2 = message[1].replace('x', '')
                hex_val3 = message[2].replace('x', '')
                hex_val4 = message[3].replace('x', '')
                sum_msg = int(hex_val1, 16) + int(hex_val2, 16) + int(hex_val3, 16)
                check_msg = int(hex_val4, 16)
                print(str(sum_msg) + "    " + str(check_msg))

        # if bytes[2] == "x01":
        #    pass
        # filter on
        # if bytes[2] == "x02":
        #    pass
        # bubbel on
        # if bytes[2] == "x03":
        #    pass
        # if bytes[2] == "x04":
        #    pass
        # if bytes[2] == "x05":
        #    pass
        # temprature from jacuzzi
        # if bytes[2] == "x06":
        #    pass


def startApp():
    connect = RunUartConnection(baudrate=4800)
    connect.test_uart()
    # connect.de_init_uart()


# connectToWifiAndUpdate()
startApp()
