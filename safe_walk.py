import simplejson as json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request

app = Flask(__name__)

@app.route('/score', methods=['POST'])
def score():
    conn = psycopg2.connect(host='postgres1.ceipocejvkue.us-west-2.rds.amazonaws.com', database='blacksburg', user='blacksburg_read', password='nrv', cursor_factory=RealDictCursor)
    cur = conn.cursor()
    query = "SELECT roads.gid, roads.name, roads.label, roads.speedlmt, roads.hasstreetlights, roads.hassidewalks, \
                ST_Distance(ST_GeomFromText('POINT(%(lon)s %(lat)s)',4326), \
                            ST_Transform(roads.geom, 4326)) AS myLineDistance \
             FROM public.roads \
             WHERE ST_Transform(roads.geom, 4326) && \
                   ST_Expand(ST_GeomFromText('POINT(%(lon)s %(lat)s)',4326), 0.00001) \
             ORDER BY myLineDistance;"
    coordinates = json.loads(request.get_data())
    roads = []
    road_ids = []
    scores = []
    for coordinate in coordinates:
        cur.execute(query, coordinate)
        road = cur.fetchone()
        if road['gid'] not in road_ids:
            score = 1
            if road['speedlmt'] <= 25:
                score = 3
            elif road['speedlmt'] <= 35:
                score = 2
            if not road['hassidewalks']:
                score -= 1
            if not road['hasstreetlights']:
                score -= 1
            scores.append(score)
            road['score'] = score
            roads.append(road)
            road_ids.append(road['gid'])
    return json.dumps({'score': sum(scores)/len(scores), 'roads': roads})

if __name__ == '__main__':
    app.run(debug=True)