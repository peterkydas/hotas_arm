import asyncio
import evdev
import threading

_BTN_TRIGGER    =   288
_BTN_SE         =   298
_BTN_ST         =   299
# bar thing on throttle
_BAR            =   6 #values from 0 (left) to 255 (right)
_THROTTLE       =   2 #values 255 (down) to 0 (full), 128 middle bump
_HNDL_PITCH     =   1 #values 0 (forward) to 1023 (backwards), 512 middle
_HNDL_ROLL      =   0 #values 0 (left) to 1023 (right), 512 middle
_HDNL_YAW       =   5 #values 0 (left) to 255 (right), 128 middle

exit_flag       =   0

class Joystick (threading.Thread):
    def __init__(self, threadID, name, counter):

        threading.Thread.__init__(self)
        
        self.threadID = threadID
        self.name = name
        self.counter = counter

        self.dev = None
        # Set your controller name here
        self.device_name = "Thrustmaster T.Flight Hotas X"

        self.event_codes = {
            288         :   "_BTN_TRIGGER",#    :   288,
            298         :   "_BTN_SE",#         :   298,
            299         :   "_BTN_ST",#         :   299,
            # bar thing on throttle
            6           :   "_BAR",#            :   6, #values from 0 (left) to 255 (right)
            2           :   "_THROTTLE",#       :   2, #values 255 (down) to 0 (full), 128 middle bump
            1           :   "_HNDL_PITCH",#     :   1, #values 0 (forward) to 1023 (backwards), 512 middle
            0           :   "_HNDL_ROLL",#      :   0, #values 0 (left) to 1023 (right), 512 middle
            5           :   "_HDNL_YAW"#       :   5, #values 0 (left) to 255 (right), 128 middle
        }

        self.event_values = {
            "_BTN_TRIGGER"    :   0,
            "_BTN_SE"         :   0,
            "_BTN_ST"         :   0,
            # bar thing on throttle
            "_BAR"            :   0, #values from 0 (left) to 255 (right)
            "_THROTTLE"       :   0, #values 255 (down) to 0 (full), 128 middle bump
            "_HNDL_PITCH"     :   0, #values 0 (forward) to 1023 (backwards), 512 middle
            "_HNDL_ROLL"      :   0, #values 0 (left) to 1023 (right), 512 middle
            "_HDNL_YAW"       :   0, #values 0 (left) to 255 (right), 128 middle
        }

        self.set_device()

    def set_device(self):
        if not self.find_device(self.get_current_devices()):
            print("Cannot find device!")
            exit(1)

        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.reader(self.dev))
    
    def run(self):
        print("Starting: " + self.name)
        self.th_reader()
        print("Exiting: " + self.name)

    async def reader(self):
        async for ev in self.dev.async_read_loop():
            # print(repr(ev))
            self.parse_event(ev)
    
    def th_reader(self):
        for ev in self.dev.read_loop():
            if exit_flag:
                self.name.exit()
            self.parse_event(ev)

    def parse_event(self, ev):
        # print(ev.code)
        # if ev.code in self.event_codes.values():
        #     # self.event_values[ev.code]
        #     print (ev.value)

        # Not sure why but ev.code 0 is always present, even though it is used for roll
        # roll will never (really) be zero so can clean it out like that
        if (ev.code == 0 and ev.value == 0):
            return

        code = self.event_codes.get(ev.code)
        if code:
            self.event_values[code] = ev.value
            print(code + ":" + str(ev.value))

    def get_event_values(self):
        return self.event_values

    def get_current_devices(self):
        return [evdev.InputDevice(path) for path in evdev.list_devices()]
    
    def find_device(self, devices):
        for i in range(len(devices)):
            if devices[i].name == self.device_name:
                self.dev = devices[i]
                return True
        return False

if __name__ == "__main__":

    js = Joystick(1, "Thread - Joystick", 1)
    js.start()
    js.join()

    print("Exiting Main Thread")