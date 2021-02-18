#!flask/bin/python
import requests
import logging

from flask import Flask, render_template,  render_template, redirect, url_for, request, jsonify
from stravalib import Client

app = Flask(__name__)
app.config.from_envvar('APP_SETTINGS')

routes = {'21748253': "Queens Highway",
          '12118362': "Hilly Route",
          }

@app.route("/")
def login():
    c = Client()
    url = c.authorization_url(client_id=app.config['STRAVA_CLIENT_ID'],
                              redirect_uri=url_for('.logged_in', _external=True),
                              approval_prompt='auto')
    return render_template('login.html', authorize_url=url)


@app.route("/strava-oauth")
def logged_in():
    """
    Method called by Strava (redirect) that includes parameters.
    - state
    - code
    - error
    """
    error = request.args.get('error')
    state = request.args.get('state')
    if error:
        return render_template('login_error.html', error=error)
    else:
        code = request.args.get('code')
        client = Client()
        access_token = client.exchange_code_for_token(client_id=app.config['STRAVA_CLIENT_ID'],
                                                      client_secret=app.config['STRAVA_CLIENT_SECRET'],
                                                      code=code)
        strava_athlete = client.get_athlete()

        route_data = {}

        for id in routes:
            route = client.get_segment(id)
            route_name = route.name
            segment_efforts = client.get_segment_efforts(id, athlete_id=strava_athlete)
            route_count = len(list(segment_efforts))
            route_data[route_name] = route_count


        return render_template('login_results.html',
                                athlete=strava_athlete,
                                route_data=route_data
                                )


if __name__ == '__main__':
    app.run(debug=True)
