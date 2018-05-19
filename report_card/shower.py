# busreport.code4jc.org

import sqlite3, argparse

parser = argparse.ArgumentParser()

args = parser.parse_args()

conn = sqlite3.connect('data/%s.db' % args.route)


# ANALYSIS

# 1. Frequency of service. This is simply calculated by looking at how often a bus on a particular route passes a given stop.
# this route does it for all stops on the route, later should do it for specified stops

# create list of only observations of buses arriving at stops
arrivals=[]
query = ('SELECT * FROM stop_predictions WHERE (rd = %s AND pt = "Approaching")' % args.route)
cursor = conn.cursor()
for row in cursor.execute(query):
        arrivals.append(row)

# throw these results into pandas?
df = pd.arrivals # ????

# calculate the mean time between arrivals for various periods (last hour, last day, last week, rush hour only, etc)

for stop in stop_id:    # not sure if this is how to do it, do i need to unique(stop_id) or something)

    # for a given stop
    # find all the buses in the desired time window
    # sort the buses by timestamp
    # calculate the time in minutes between them
    # average over the # of buses


# q: what happens when there are gaps in the data? can detect this?





#
# # 2. Travel time. How long is it taking to get from one stop to the next. We can do this by tracking individual vehicles and seeing how long it takes them to get from one stop to the next.
#
# is there a unique run id? for each date, calculate travel time on each segment of the route and display average for all buses?
#
#
# # 3. Schedule adherence. Is the bus actually hitting its scheduled stops. This is more of an issue on less frequent routes, and its becoming less important as more people use apps to meet the bus. At rush time its often not at all important. But its pretty easy to do, comparing against GTFS timetables, so lets do it.
#
# too complicated for now


# setup the routes to display the page

# app = Flask(__name__)
# api = Api(app)
# @app.route('/<path:path>')
# def staticHost(self, path):
#     try:
#         return flask.send_from_directory(app.config['RESULT_STATIC_PATH'], path)
#     except werkzeug.exceptions.NotFound as e:
#         if path.endswith("/"):
#             return flask.send_from_directory(app.config['RESULT_STATIC_PATH'], path + "index.html")
#         raise e
#

