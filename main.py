import app.secrets as secrets
import gc
import machine
import network
import time
import socket
#import picoweb
#import ulogging as logging

#app = picoweb.WebApp(__name__)


from machine import UART

# @app.route("/")
# def index(req, resp):
#     yield from picoweb.start_response(resp)
#     yield from resp.awrite(b"Static image: <img src='static/logo.png'><br />")
#     yield from resp.awrite(b"Dynamic image: <img src='dyna-logo.png'><br />")
#
# @app.route("/dyna-logo.png")
# def squares(req, resp):
#     yield from picoweb.start_response(resp, "image/png")
#     yield from resp.awrite(
#         b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x000\x00\x00\x000\x01\x03\x00\x00\x00m\xcck"
#         b"\xc4\x00\x00\x00\x06PLTE\xff\xff\xff\x00\x00\x00U\xc2\xd3~\x00\x00\x00\xd2IDAT\x18\xd3c`"
#         b"\x80\x01\xc6\x06\x08-\x00\xe1u\x80)\xa6\x040\xc5\x12\x00\xa18\xc0\x14+\x84\xe2\xf5\x00Sr"
#         b"\x10J~\x0e\x98\xb2\xff\x83\x85\xb2\x86P\xd2\x15\x10\x95\x10\x8a\xff\x07\x98b\xff\x80L\xb1"
#         b"\xa5\x83-?\x95\xff\x00$\xf6\xeb\x7f\x01\xc8\x9eo\x7f@\x92r)\x9fA\x94\xfc\xc4\xf3/\x80\x94"
#         b"\xf8\xdb\xff'@F\x1e\xfcg\x01\xa4\xac\x1e^\xaa\x01R6\xb1\x8f\xff\x01);\xc7\xff \xca\xfe\xe1"
#         b"\xff_@\xea\xff\xa7\xff\x9f\x81F\xfe\xfe\x932\xbd\x81\x81\xb16\xf0\xa4\x1d\xd0\xa3\xf3\xfb"
#         b"\xba\x7f\x02\x05\x97\xff\xff\xff\x14(\x98\xf9\xff\xff\xb4\x06\x06\xa6\xa8\xfa\x7fQ\x0e\x0c"
#         b"\x0c\xd3\xe6\xff\xcc\x04\xeaS]\xfet\t\x90\xe2\xcc\x9c6\x01\x14\x10Q )\x06\x86\xe9/\xc1\xee"
#         b"T]\x02\xa68\x04\x18\xd0\x00\x00\xcb4H\xa2\x8c\xbd\xc0j\x00\x00\x00\x00IEND\xaeB`\x82"
#     )


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


class RunApp():
    def __init__(self):
        # keep track of messages
        self.last_message_x01 = []
        self.last_message_x02 = []
        self.last_message_x03 = []
        self.last_message_x04 = []
        self.last_message_x05 = []
        self.last_message_x06 = []
        self.last_message_x07 = []
        self.last_message_x08 = []
        self.last_message_r = []
        self.last_message_x0b = []

        # current states
        self.jacuzzi_temp = 0
        self.bubbel_state_on = False
        self.heater_state_on = False
        self.filter_state_on = False
        self.heating_temp = 0
        self.jacuzzi_filter_state = ""

        # init UART
        self.uart1_jacuzzi = UART(1, baudrate=9600, tx=14, rx=4, bits=8, stop=1, parity=None)
        self.uart2_remote = UART(2, baudrate=9600, tx=15, rx=27, bits=8, stop=1, parity=None)

    def start_uart(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 80))
        s.listen(5)

        while True:
            if self.uart2_remote.any():
                remote_buffer = self.uart2_remote.readline()
                self.process_message(remote_buffer, "remote")
                self.uart1_jacuzzi.write(bytearray(remote_buffer))

            if self.uart1_jacuzzi.any():
                jacuzzi_buffer = self.uart1_jacuzzi.readline()
                self.process_message(jacuzzi_buffer, "jacuzzi")
                self.uart2_remote.write(bytearray(jacuzzi_buffer))

            conn, addr = s.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            request = str(request)
            print('Content = %s' % request)

            jacuzzi_heater_on = request.find('/?jacuzzi_heater_on')
            jacuzzi_heater_off = request.find('/?jacuzzi_heater_off')
            jacuzzi_filter_on = request.find('/?jacuzzi_filter_on')
            jacuzzi_filter_off = request.find('/?jacuzzi_filter_off')
            jacuzzi_bubbels_on = request.find('/?jacuzzi_bubbels_on')
            jacuzzi_bubbels_off = request.find('/?jacuzzi_bubbels_off')

            if jacuzzi_heater_on == 6:
                self.set_heather_on()
                print("turning heater on")
            if jacuzzi_heater_off == 6:
                self.set_heather_off()
                print("turning heater off")
            if jacuzzi_filter_on == 6:
                self.set_filter_on()
                print("turning filter on")
            if jacuzzi_filter_off == 6:
                self.set_filter_off()
                print("turning filter off")
            if jacuzzi_bubbels_on == 6:
                self.set_bubbel_on()
                print("turning bubbel on")
            if jacuzzi_bubbels_off == 6:
                self.set_bubbel_off()
                print("turning bubbel off")

            response = self.web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()

    def de_init_uart(self):
        self.uart1_jacuzzi.deinit()
        self.uart2_remote.deinit()

    def get_temp(self):
        return self.jacuzzi_temp

    def get_heating_temp(self):
        return self.heating_temp

    def get_bubbel_state(self):
        return self.bubbel_state_on

    def get_heater_state(self):
        return self.heater_state_on

    def get_filter_state(self):
        return self.filter_state_on

    def set_bubbel_on(self):
        self.uart2_remote.write(bytearray(b'\xa5\x03\x01\xa9'))
        self.bubbel_state_on = True

    def set_filter_on(self):
        self.uart1_jacuzzi.write(bytearray(b'\xa5\x02\x01\xa8'))
        self.filter_state_on = True

    def set_heather_on(self):
        self.heater_state_on = True

    def set_bubbel_off(self):
        self.uart1_jacuzzi.write(bytearray(b'\xa5\x03\x00\xa8'))
        self.bubbel_state_on = False

    def set_filter_off(self):
        self.uart1_jacuzzi.write(bytearray(b'\xa5\x02\x00\xa7'))
        self.filter_state_on = False

    def set_heather_off(self):
        self.heater_state_on = False

    def set_heating_temp(self, temp):
        # temp -> hex
        # Controle nr uitrekenen
        # bytestring van maken
        # sturen : self.uart1_jacuzzi.write(bytearray(b'\xa5\x02\x00\xa7'))
        pass

    def split_message_to_array(self, message):
        message_str = str(message)
        msg = message_str.split("\'")
        main_msg = msg[1]
        bytes = main_msg.split("\\")

        # check nr of messages
        # print(len(bytes))
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

        # print(messages)
        return messages

    def process_message(self, message, sender):
        # split message to usefull array
        messages_array = self.split_message_to_array(message=message)

        for message in messages_array:
            # check message
            if message[0] == 'xa5':
                if message[1] == 'r':
                    sum_msg = 1
                    check_msg = 1
                else:
                    hex_val1 = message[0].replace('x', '')
                    hex_val2 = message[1].replace('x', '')
                    hex_val3 = message[2].replace('x', '')
                    hex_val4 = message[3].replace('x', '')
                    try:
                        sum_msg = int(hex_val1, 16) + int(hex_val2, 16) + int(hex_val3, 16)
                        check_msg = int(hex_val4, 16)
                    except ValueError:
                        print("failed to process message, message was : " + message)
                        print_exception()

                # verify if message is complete
                if sum_msg == check_msg:
                    if message[1] == "x01":
                        if self.last_message_x01 != message:
                            self.last_message_x01 = message
                            if message[2] == "x00":
                                print(" Heater is uit " + str(message) + str(sender))
                                self.filter_state_on = False
                            elif message[2] == "x01":
                                self.filter_state_on = True
                                print(" Heater is aan" + str(message) + str(sender))
                            else:
                                print(" unkown Heater state " + str(message) + str(sender))
                    # filter aan x02
                    elif message[1] == "x02":
                        if self.last_message_x02 != message:
                            self.last_message_x02 = message
                            if message[2] == "x00":
                                print(" Filter is uit " + str(message) + str(sender))
                                self.filter_state_on = False
                            elif message[2] == "x01":
                                self.filter_state_on = True
                                print(" Filter is aan" + str(message) + str(sender))
                            else:
                                print(" unkown filter state " + str(message) + str(sender))

                    # bubbels aan x03
                    elif message[1] == "x03":
                        if self.last_message_x03 != message:
                            self.last_message_x03 = message
                            if message[2] == "x00":
                                print(" Bubbels zijn uit " + str(sender))
                                self.bubbel_state_on = False
                            elif message[2] == "x01":
                                self.bubbel_state_on = True
                                print(" Bubbels zijn aan" + str(sender))
                            else:
                                print(" unkown bubbel state " + str(message) + str(sender))
                    elif message[1] == "x04":
                        if self.last_message_x04 != message:
                            self.last_message_x04 = message
                            temp_val = message[2].replace('x', '')
                            # maximum setting seems to be 31! Bug in Remote? Lie in specs?
                            print(
                                "The temprature on remote is set to : " + str(int(temp_val, 16)) + "   " + str(
                                    message) + str(sender))
                            self.jacuzzi_temp = int(temp_val, 16)
                    elif message[1] == "x05":
                        if self.last_message_x05 != message:
                            self.last_message_x05 = message
                            print("still unkown message : " + str(message) + str(sender))
                    # temp van jacuzzi x06
                    elif message[1] == "x06":
                        if self.last_message_x06 != message:
                            self.last_message_x06 = message
                            temp_hex_jac = message[2].replace('x', '')
                            temp_jac = ((int(temp_hex_jac, 16)) * 10) / 2
                            print("The jacuzzi temp is : " + str(temp_jac) + " devide by 10 " + str(sender))
                    elif message[1] == "x07":
                        if self.last_message_x07 != message:
                            self.last_message_x07 = message
                            print("still unkown message (bit = x07): " + str(message) + str(sender))
                    elif message[1] == "x08":
                        if self.last_message_x08 != message:
                            self.last_message_x08 = message
                            if message[2] == "x00":
                                print(" Filter is uit vanaf jacuzzi" + str(message) + str(sender))
                                self.jacuzzi_filter_state = "Filtering off in jacuzzi"
                            elif message[2] == "x03":
                                print(" Filter is zonder error aan vanaf jacuzzi" + str(message) + str(sender))
                                self.jacuzzi_filter_state = "Filtering on, no errors"
                            else:
                                print(" unkown filter state " + str(message) + str(sender))
                                self.jacuzzi_filter_state = "Filter in unkown state"
                    elif message[1] == "r":
                        if self.last_message_r != message:
                            self.last_message_r = message
                            print("still unkown message (bit = r): " + str(message) + str(sender))

                    elif message[1] == "x0b":
                        if self.last_message_x0b != message:
                            self.last_message_x0b = message
                            print("still unkown message (bit = x0b): " + str(message) + str(sender))

                    else:
                        print("still unkown message : " + str(message) + str(sender))
                        print("bit 2 was:" + message[1])
                else:
                    print("verify failed, mesages wrong " + str(message) + str(sender))

    def web_page(self):
        if self.heater_state_on:
            jacuzzi_heater = "On"
        else:
            jacuzzi_heater = "Off"

        if self.filter_state_on:
            jacuzzi_filter = "On"
        else:
            jacuzzi_filter = "Off"

        if self.bubbel_state_on:
            jacuzzi_bubbels = "On"
        else:
            jacuzzi_bubbels = "Off"

        remote_temp = self.heating_temp
        x05_message = self.last_message_x05
        jacuzzi_current_temp = self.jacuzzi_temp
        x07_message = self.last_message_x07
        jacuzzi_filter_state_str = self.jacuzzi_filter_state
        r_message = self.last_message_r
        x0b_message = self.last_message_x0b
        html = """
        <html>
            <head>
                <title>Mspa Wifi remote</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link rel="icon" href="data:,">
                <style>
                    body { text-align: center; font-family: "Trebuchet MS", Arial;}
                    table { border-collapse: collapse; margin-left:auto; margin-right:auto; }
                    th { padding: 12px; background-color: #0043af; color: white; }
                    tr { border: 1px solid #ddd; padding: 12px; }
                    tr:hover { background-color: #bcbcbc; }
                    td { border: none; padding: 5px; }
                    .button{display: inline-block; background-color: #e7bd3b; border: none;
                    border-radius: 4px; color: white; padding: 4px 4px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
                    .button2{background-color: #4286f4;}
                </style>
            </head>
            <body>
                <h1>Mspa Wifi remote</h1>
                <table>
                <tr>
                    <th>States</th>
                    <th>Current state</th>
                    <th>Turn on or off</th>
                </tr>
                <tr>
                    <td>Jacuzzi heater</td>
                    <td><span class="sensor">""" + str(jacuzzi_heater) + """</span></td>
                    <td><p>
                    <a href="/?jacuzzi_heater_on"><button class="button">ON</button></a>
                    <a href="/?jacuzzi_heater_off"><button class="button button2">OFF</button></a></p></td>
                </tr>
                <tr>
                    <td>Jacuzzi Filter</td>
                    <td><span class="sensor">""" + str(jacuzzi_filter) + """</span></td>
                <td><p>
                    <a href="/?jacuzzi_filter_on"><button class="button">ON</button></a>
                    <a href="/?jacuzzi_filter_off"><button class="button button2">OFF</button></a></p></td>
                </tr>
                <tr>
                    <td>Jacuzzi Bubbels</td>
                    <td><span class="sensor">""" + str(jacuzzi_bubbels) + """</span></td>
                    <td><p>
                    <a href="/?jacuzzi_bubbels_on"><button class="button">ON</button></a>
                    <a href="/?jacuzzi_bubbels_off"><button class="button button2">OFF</button></a></p></td>
                </tr>
                <tr>
                    <td>Set remote temprature</td>
                    <td><span class="sensor">""" + str(remote_temp) + """ C</span></td>
                    <td></td>
                </tr>
                <tr>
                    <td>x05 - still unkown</td>
                    <td><span class="sensor">""" + str(x05_message) + """</span></td>
                    <td></td>
                </tr>
                <tr>
                    <td>Jacuzzi temprature</td>
                    <td><span class="sensor">""" + str(jacuzzi_current_temp) + """ C</span></td>
                    <td></td>
                </tr>
                <tr>
                    <td>x07 - still unkown</td>
                    <td><span class="sensor">""" + str(x07_message) + """</span></td>
                    <td></td>
                </tr>
                <tr>
                    <td>Jacuzzi filter state</td>
                    <td><span class="sensor">""" + str(jacuzzi_filter_state_str) + """</span></td>
                    <td></td>
                </tr>
                <tr>
                    <td>r - still unkown</td>
                    <td><span class="sensor">""" + str(r_message) + """</span></td>
                    <td></td>
                </tr>
                <tr>
                    <td>x0b - still unkown</td>
                    <td><span class="sensor">""" + str(x0b_message) + """</span></td>
                    <td></td>
                </tr>
            </body>
        </html>"""
        return html

def startApp():
    #logging.basicConfig(level=logging.INFO)
    #app.run(debug=True)
    connect = RunApp()
    connect.start_uart()


connectToWifiAndUpdate()
startApp()
