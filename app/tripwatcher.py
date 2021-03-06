
import time

from lib.RouteScan import RouteScan

from lib.TransitSystem import load_system_map

if __name__ == "__main__":

    run_frequency = 60 # seconds
    time_start=time.monotonic()

    while True:
        system_map = load_system_map()
        RouteScan(system_map)
        time.sleep(run_frequency - ((time.monotonic() - time_start) % 60.0))  # sleep remainder of the 60 second loop




