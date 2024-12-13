from flask import Flask, jsonify, request
from flask_cors import CORS
from recommender import Recommender
from db.db_handler import DB

app = Flask(__name__)
CORS(app)
db = DB()
recommender = Recommender(reuse_model=True)


@app.route('/api/v1/recommend', methods=['POST'])
def recommend():
    data = request.json

    if not data or 'ids' not in data.keys():
        return jsonify({"error": "Missing 'ids' in request payload"}), 400

    ids = data['ids']
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        return jsonify({"error": "'ids' must be a list of strings"}), 400

    n_recs = data['n_recs']
    if not isinstance(n_recs, int):
        return jsonify({"error": "'n_recs' must be an integer"}), 400

    recs = sum(recommender.recommend(ids=ids, n_recs=n_recs).tolist(), [])  # flatten the results

    results = db.query_table(
        table_name='tracks as tr'
        , columns=['tr.track_id', "concat(tr.track_name, ' by ', a.artist) as track_artist"]
        , join={
            'tracks_artists as ta': ['tr.track_id = ta.track_id']
            , 'artists as a': ['ta.artist_id = a.artist_id']
        }
        , filters={'idx': recs}
    ).to_dict(orient='records')

    return jsonify(results), 200


@app.route('/api/v1/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '')
    suggestions = db.query_table(
        table_name='tracks as tr'
        , columns=['tr.track_id', "concat(tr.track_name, ' by ', a.artist) as track_artist"]
        , join={
            'tracks_artists as ta': ['tr.track_id = ta.track_id']
            , 'artists as a': ['ta.artist_id = a.artist_id']
        }
        , filters={'tr.track_name_like': query}
        , limit=10
    ).to_dict(orient='records')

    return suggestions, 200


@app.route('/api/v1/test', methods=['GET'])
def test_api():
    return {'api_status': 'works fine'}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
