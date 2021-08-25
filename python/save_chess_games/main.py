import re
import requests

import chess
from google.cloud import firestore

import constants
import fast_hash
from ChessScript import ChessScript

def app(event, context):
    url = 'https://theweekinchess.com/a-year-of-pgn-game-files'
    print("opening %s" % (url))
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    html_response = requests.get(url, headers=headers)
    print("html_response length %d" % (len(html_response.text)))
    db = firestore.Client()
    for match in re.finditer(r'"assets/files/pgn/([^"]*)"', html_response.text):
        url = 'https://theweekinchess.com/assets/files/pgn/{0}'.format(match.group(1))
        print("downloading {0}".format(url))
        pgn_response = requests.get(url, headers=headers)
        if pgn_response.status_code != 200:
            print("http response %d" % (pgn_response.status_code))
            continue
        print("pgn response length %d" % (len(pgn_response.text)))
        for single_game_pgn in pgn_response.text.split(constants.GAME_DELIMITER):
            if single_game_pgn == '':
                continue
            document_name = fast_hash.fast_hash(single_game_pgn)
            print(document_name)
            single_game_pgn = "{0}{1}".format(constants.GAME_DELIMITER, single_game_pgn)
            script = ChessScript(single_game_pgn)
            headers = script.game.headers
            data = {
                u'pgn': single_game_pgn,
                u'White': headers["White"],
                u'Black': headers["Black"],
                u'Date': headers["Date"],
                u'Result': headers["Result"],
                u'Round': headers.get("Round", default=""),
                u'Opening': headers.get("Opening", default=""),
                u'Variation': headers.get("Variation", default=""),
                u'WhiteElo': headers.get("WhiteElo", default=0),
                u'BlackElo': headers.get("BlackElo", default=0),
                u'HalfMoves': script.get_half_moves_count(),
                u'WhiteCastle': script.get_castle(chess.WHITE),
                u'BlackCastle': script.get_castle(chess.BLACK),
                constants.SCRIPT_FIELD: '',
            }
            document = db.document(constants.CHESS_GAME_COLLECTION, document_name).get()
            if document.exists:
                db.document(constants.CHESS_GAME_COLLECTION, document_name).update(data)
            else:
                db.document(constants.CHESS_GAME_COLLECTION, document_name).set(data)

if __name__ == "__main__":
    # execute only if run as a script
    app(None, None)
