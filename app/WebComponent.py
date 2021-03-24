import socket

class WebComponent:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        self.socket.bind(('', 80))
        self.socket.listen(5)

    def check_input(self, request):
        jacuzzi_heater_on = request.find('/?jacuzzi_heater_on')
        jacuzzi_heater_off = request.find('/?jacuzzi_heater_off')
        jacuzzi_filter_on = request.find('/?jacuzzi_filter_on')
        jacuzzi_filter_off = request.find('/?jacuzzi_filter_off')
        jacuzzi_bubbels_on = request.find('/?jacuzzi_bubbels_on')
        jacuzzi_bubbels_off = request.find('/?jacuzzi_bubbels_off')
        print("got to the check input")

        #return jacuzzi_heater_on, jacuzzi_heater_off, jacuzzi_filter_on, jacuzzi_filter_off, jacuzzi_bubbels_on,  jacuzzi_bubbels_off

    def webpage_response(self, conn, uart_status):
        print("got to webpage response")
        response = self.web_page(uart_status)
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()

    def web_page(self, uart_status):
        print("Got to web page")
        print(uart_status)
        if uart_status['heater_state_on']:
            jacuzzi_heater = "On"
        else:
            jacuzzi_heater = "Off"

        if uart_status['filter_state_on']:
            jacuzzi_filter = "On"
        else:
            jacuzzi_filter = "Off"

        if uart_status['bubbel_state_on']:
            jacuzzi_bubbels = "On"
        else:
            jacuzzi_bubbels = "Off"

        remote_temp = uart_status['remote_temp']
        x05_message = uart_status['x05_message']
        jacuzzi_current_temp = uart_status['jacuzzi_current_temp']
        x07_message = uart_status['x07_message']
        jacuzzi_filter_state_str = uart_status['jacuzzi_filter_state_str']
        r_message = uart_status['r_message']
        x0b_message = uart_status['x0b_message']
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
