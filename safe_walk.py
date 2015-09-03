import simplejson as json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/score', methods=['POST'])
def score():
    conn = psycopg2.connect(host='postgres1.ceipocejvkue.us-west-2.rds.amazonaws.com', database='blacksburg', user='blacksburg_read', password='nrv', cursor_factory=RealDictCursor)
    cur = conn.cursor()
    query = "SELECT roads.gid, roads.label, roads.speedlmt, roads.hasstreetlights, roads.hassidewalks, roads.day_score, roads.night_score, \
                ST_Distance(ST_GeomFromText('POINT(%(lon)s %(lat)s)',4326), \
                            ST_Transform(roads.geom, 4326)) AS myLineDistance \
             FROM public.roads \
             WHERE ST_Transform(roads.geom, 4326) && \
                   ST_Expand(ST_GeomFromText('POINT(%(lon)s %(lat)s)',4326), 0.00001) \
             ORDER BY myLineDistance;"
    coordinates = json.loads(request.get_data())
    roads = []
    road_ids = []
    scores = {'day': [], 'night': []}
    scoring = {"red": 1, "yellow": 2, "green": 3}
    for coordinate in coordinates:
        cur.execute(query, coordinate)
        road = cur.fetchone()
        if road['gid'] not in road_ids:
            scores['day'].append(scoring[road['day_score']])
            scores['night'].append(scoring[road['night_score']])
            roads.append(road)
            road_ids.append(road['gid'])
    #return json.dumps({'roads': roads});
    return json.dumps({'scores': {'day': sum(scores['day'])/float(len(scores['day'])), 'night': sum(scores['night'])/float(len(scores['night']))}, 'roads': roads})

if __name__ == '__main__':
    app.run(debug=True)
