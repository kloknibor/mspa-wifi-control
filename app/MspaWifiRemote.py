import select
from .UartHelper import UartConnection
from .WebComponent import WebComponent


class Main:
    def __init__(self):
        self.uart_status = {}

    def loop(self):
        uart_interface = UartConnection()
        web = WebComponent()

        while True:
            # get UART data
            uart_interface.check_uart()
            self.uart_status = uart_interface.return_status()
            print(self.uart_status)

            # Check websocket
            r, w, err = select.select((web.socket,), (), (), 1)
            if r:
                for readable in r:
                    conn, addr = web.socket.accept()
                    print('Got a connection from %s' % str(addr))
                    request = conn.recv(1024)
                    request = str(request)
                    print('Content = %s' % request)

                    try:
                        web_response = web.check_input(request)
                        # if web_response.jacuzzi_heater_on == 6:
                        #     uart_interface.set_heather_on()
                        #     print("turning heater on")
                        # if web_response.jacuzzi_heater_off == 6:
                        #     uart_interface.set_heather_off()
                        #     print("turning heater off")
                        # if web_response.jacuzzi_filter_on == 6:
                        #     uart_interface.set_filter_on()
                        #     print("turning filter on")
                        # if web_response.jacuzzi_filter_off == 6:
                        #     uart_interface.set_filter_off()
                        #     print("turning filter off")
                        # if web_response.jacuzzi_bubbels_on == 6:
                        #     uart_interface.set_bubbel_on()
                        #     print("turning bubbel on")
                        # if web_response.jacuzzi_bubbels_off == 6:
                        #     uart_interface.set_bubbel_off()
                        #     print("turning bubbel off")
                        print(web_response)
                        web.webpage_response(conn=conn, uart_status=self.uart_status)

                    except OSError as e:
                        pass
