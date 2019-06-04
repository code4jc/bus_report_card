#
# usage:
# (statewide)                           tripwatcher.py
# (only routes in route_config.py)      tripwatcher.py --limit
#

import argparse
import sys
import datetime, time
import werkzeug
import itertools
import numpy as np

from lib import BusAPI, Localizer
from lib.DataBases import SQLAlchemyDBConnection, Trip, BusPosition, ScheduledStop

from route_config import reportcard_routes


def watch(**kwargs):

    ##############################################
    # 1 -- FETCH AND LOCALIZE CURRENT POSITIONS
    ##############################################

    with SQLAlchemyDBConnection() as db:


        # get buses from NJT API

        if limit is True:
            ## route_config buses only
            while True:
                try:
                    buses = BusAPI.parse_xml_getBusesForRoute(
                        BusAPI.get_xml_data(args.source, 'buses_for_route', route=r['route']))
                except werkzeug.exceptions.NotFound as e:
                    sys.stdout.write('.')
                    time.sleep(2)
                    continue
                break

        if limit is not True:
            ## entire state
            while True:
                try:
                    buses = BusAPI.arse_xml_getBusesForRouteAll(
                        BusAPI.get_xml_data(args.source, 'all_buses'))
                except werkzeug.exceptions.NotFound as e:
                    sys.stdout.write('.')
                    time.sleep(2)
                    continue
                break

        # NEW parse trips separately and create before we add the positions -- to honor the foreign key constraint
        triplist = []
        for bus in buses:
            bus.trip_id = ('{id}_{run}_{dt}').format(id=bus.id, run=bus.run,
                                                     dt=datetime.datetime.today().strftime('%Y%m%d'))
            triplist.append(bus.trip_id)
            result = db.session.query(Trip).filter(Trip.trip_id == bus.trip_id).first()
            if result is None:
                trip_id = Trip(args.source, r['route'], bus.id, bus.run, bus.pid)
                db.session.add(trip_id)

            else:
                pass

            db.__relax__()  # disable foreign key checks before...
            db.session.commit()  # we save the position_log.

        # #populate stoplist
        # records_to_update = db.session.query(Trip).filter(Trip.trip_id.in_(triplist)).all()
        # for record in records_to_update:
        #     record.populate_stoplist()

        # add the bus positions to the db
        bus_positions = Localizer.get_nearest_stop(buses, r['route'])
        for group in bus_positions:
            for bus in group:
                db.session.add(bus)
        db.session.commit()

    ##############################################
    #   2 -- ASSIGN ARRIVALS
    ##############################################

    with SQLAlchemyDBConnection() as db:
        for trip_id in triplist:

            # load the trip card for reference
            scheduled_stops = db.session.query(Trip, ScheduledStop) \
                .join(ScheduledStop) \
                .filter(Trip.trip_id == trip_id) \
                .all()

            # select all the BusPositions on ScheduledStops where there is no arrival flag yet
            arrival_candidates = db.session.query(BusPosition) \
                .join(ScheduledStop) \
                .filter(BusPosition.trip_id == trip_id) \
                .filter(ScheduledStop.arrival_timestamp == None) \
                .order_by(BusPosition.timestamp.asc()) \
                .all()

            # split them into groups by stop
            position_groups = [list(g) for key, g in itertools.groupby(arrival_candidates, lambda x: x.stop_id)]

            # iterate over all but last one (which is stop bus is currently observed at)
            for x in range(len(position_groups) - 1):

                # slice the positions for the xth stop
                position_list = position_groups[x]

                # GRAB THE STOP RECORD FROM DB FOR UPDATING ARRIVAL INFO
                stop_to_update = db.session.query(ScheduledStop, BusPosition) \
                    .join(BusPosition) \
                    .filter(ScheduledStop.trip_id == position_list[0].trip_id) \
                    .filter(ScheduledStop.stop_id == position_list[0].stop_id) \
                    .all()

                ##############################################
                #   ONE POSITION
                #   if we only have one observation and since
                #   this isn't the current stop, then we've
                #   already passed it and can just assign it
                #   as the arrival
                ##############################################

                if len(position_list) == 1:
                    arrival_time = position_list[0].timestamp
                    position_list[0].arrival_flag = True
                    case_identifier = '1a'
                    approach_array = np.array([0, position_list[0].distance_to_stop])

                ##############################################
                #   TWO POSITIONS
                #   calculate the slope between the two points
                #   and assign to CASE A,B, or C
                #   arrival is either the 1st observed position
                #   or the 2nd
                ##############################################

                elif len(position_list) == 2:

                    # create and display approach array
                    points = []
                    for y in range(len(position_list)):
                        points.append((y, position_list[y].distance_to_stop))
                    approach_array = np.array(points)

                    # calculate classification metrics
                    slope = np.diff(approach_array, axis=0)[:, 1]
                    acceleration = np.diff(slope, axis=0)
                    slope_avg = np.mean(slope, axis=0)

                    # CASE A sitting at the stop, then gone without a trace
                    # determined by [d is <100, doesn't change e.g. slope = 0 ]
                    # (0, 50)  <-----
                    # (1, 50)
                    if slope_avg == 0:
                        arrival_time = position_list[0].timestamp
                        position_list[0].arrival_flag = True
                        case_identifier = '2a'

                    # CASE B approaches, then vanishes
                    # determined by [d is decreasing, slope is always negative]
                    # (0, 400)
                    # (1, 300) <-----
                    elif slope_avg < 0:
                        arrival_time = position_list[-1].timestamp
                        position_list[-1].arrival_flag = True
                        case_identifier = '2b'

                    # CASE C appears, then departs
                    # determined by [d is increasing, slope is always positive]
                    # (0, 50)  <-----
                    # (1, 100)
                    elif slope_avg > 0:
                        arrival_time = position_list[0].timestamp
                        position_list[0].arrival_flag = True
                        case_identifier = '2c'

                ##############################################
                #   THREE OR MORE POSITIONS
                ##############################################

                elif len(position_list) > 2:

                    # create and display approach array
                    # print(('\tapproaching {b}').format(a=trip_id, b=position_list[0].stop_id))
                    points = []
                    for y in range(len(position_list)):
                        points.append((y, position_list[y].distance_to_stop))
                    approach_array = np.array(points)
                    # for point in approach_array:
                    # print(('\t\t {a:.0f} distance_to_stop {b}').format(a=point[0], b=point[1]))

                    # calculate classification metrics
                    slope = np.diff(approach_array, axis=0)[:, 1]
                    acceleration = np.diff(slope, axis=0)
                    slope_avg = np.mean(slope, axis=0)

                    try:
                        # CASE A
                        if slope_avg == 0:
                            arrival_time = position_list[0].timestamp
                            position_list[0].arrival_flag = True
                            case_identifier = '3a'
                            # plot_approach(trip_id, np.array([0, position_list[0].distance_to_stop]), case_identifier)

                        # CASE B
                        elif slope_avg < 0:
                            arrival_time = position_list[-1].timestamp
                            position_list[-1].arrival_flag = True
                            case_identifier = '3b'
                            # plot_approach(trip_id, np.array([0, position_list[-1].distance_to_stop]), case_identifier)

                        # CASE C
                        elif slope_avg > 0:
                            arrival_time = position_list[0].timestamp
                            position_list[0].arrival_flag = True
                            case_identifier = '3c'
                            # plot_approach(trip_id, np.array([0, position_list[0].distance_to_stop]), case_identifier)

                    except:
                        pass

                # catch errors for unassigned 3+-position approaches
                try:
                    stop_to_update[0][0].arrival_timestamp = arrival_time
                except:
                    pass

        db.session.commit()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', dest='source', default='nj', help='source name')
    parser.add_argument('-l', '--limit', dest='limit', required=True, default=False, help='use routes specified in route_config.py only')
    args = parser.parse_args()

    ran = False

    while True:
        if ran is True:
            delay = 30
        else:
            delay = 0
        time.sleep(delay)

        if args.limit is True:
            for route_iteration in reportcard_routes:
                watch(limit=args.limit, r=route_iteration)
            ran = True

        if args.limit is False:
            watch(limit=args.limit, r=0)
            ran = True


##################################################
# UNUSED - FOR VISUAL APPROACH DIAGNOSTICS
##################################################
#
# import matplotlib.pyplot as plt
# def plot_approach(trip_id, approach_array,case_identifier):
#     x = [row[0] for row in approach_array]
#     y = [row[1] for row in approach_array]
#     # x = approach_array[:,0]
#     # y = approach_array[:,1]
#     x_max = np.max(x)
#     y_max = np.max(y)
#     plt.scatter(x, y)
#     label = ('{a} {b}').format(a=trip_id, b=case_identifier)
#     plt.xlabel(label)
#     plt.axis([0, 1.1 * x_max, 0, 1.1 * y_max])
#     plt.show()
#     # print ('plot failed')
#     return