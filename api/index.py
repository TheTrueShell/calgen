# path/filename: /app/server.py

from flask import Flask, request, Response
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

@app.route('/cal')
def calendar_event():
    # Retrieve the parameters from the query string
    timestamp = request.args.get('ts', default=None, type=int)
    event_name = request.args.get('name', default="Unnamed Event", type=str)
    iso = request.args.get('iso', default=None, type=str)

    # Validation to ensure either 'ts' or 'iso' is provided, but not both
    if timestamp is not None and iso is not None:
        return "Provide either 'ts' or 'iso', but not both.", 400
    if timestamp is None and iso is None:
        return "Either 'ts' or 'iso' parameter must be provided.", 400

    try:
        if iso:
            # Parse the ISO8601 date string to a datetime object
            event_time = datetime.strptime(iso, "%Y%m%dT%H%M%S")
        else:
            # Convert UNIX timestamp to a timezone-aware datetime object
            event_time = datetime.fromtimestamp(timestamp, tz=pytz.utc)

        # Create an iCalendar file with the product identifier for Biotic's CalGen
        cal = Calendar()
        cal.add('prodid', '-//Biotic\'s CalGen//mxm.dk//')
        cal.add('version', '2.0')

        event = Event()
        event.add('dtstart', event_time)
        event.add('dtend', event_time + timedelta(hours=1))  # Assuming 1 hour event duration
        event.add('summary', event_name)  # Add the event name

        cal.add_component(event)

        # Convert the calendar to an ical formatted string
        response = Response(cal.to_ical())
        response.headers['Content-Disposition'] = f'attachment; filename="{event_name}.ics"'
        response.headers['Content-Type'] = 'text/calendar; charset=utf-8'

        return response

    except ValueError as e:
        return f"Invalid date format: {e}", 400


if __name__ == '__main__':
    app.run(debug=True)
