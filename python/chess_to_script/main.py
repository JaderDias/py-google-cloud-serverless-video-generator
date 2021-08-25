from google.cloud import firestore, storage, texttospeech

import Constants
import Publisher
from ChessScript import ChessScript
import chess
import chess.pgn
import chess.svg
import os.path
from cairosvg import svg2png

client = texttospeech.TextToSpeechClient()
storage_client = storage.Client()

def save_svg(game, filename):
    tmp_svg_filename = "/tmp/{0}.svg".format(filename)
    print(tmp_svg_filename)
    if os.path.exists(tmp_svg_filename):
        return tmp_svg_filename
    boardsvg = chess.svg.board(
        board=game.board(),
        size=Constants.SVG_SIZE_VALUE,
        lastmove=game.move
    )
    with open(tmp_svg_filename, "w") as text_file:
        text_file.write(boardsvg)
    return tmp_svg_filename

def convert_to_png(game_data, board, filename, tmp_svg_filename, bucket):
    png_filename = "{0}/{1}/{2}/{3}".format(
        Constants.SCENE_FOLDER,
        game_data.id,
        board.ply(),
        Constants.PNG_BLOB,
    )
    png_blob = bucket.blob(png_filename)
    if png_blob.exists():
        print("png already exists")
        return
    tmp_png_filename = "/tmp/{0}.png".format(filename)
    svg2png(url=tmp_svg_filename,write_to=tmp_png_filename)
    png_blob.upload_from_filename(tmp_png_filename)

def save_audio_blob(script, game, bucket):
    audio_blob = bucket.blob(script.audio_blob_path())
    if audio_blob is None:
        print("text for scene {0} is missing".format(game.ply()))
        return
    if audio_blob == '':
        print("text for scene {0} is empty".format(game.ply()))
        return
    if audio_blob.exists():
        print("audio for scene {0} already exists".format(game.ply()))
        return
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=script.get_text()),
        voice=texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-G"),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            pitch=0,
            speaking_rate= 1),
    )
    tmp_filename = "/tmp/{0}".format(game.ply())
    with open(tmp_filename, 'wb') as f:
        f.write(response.audio_content)
    audio_blob.upload_from_filename(tmp_filename)
    
def chess_to_script(games_ref, game_data):
    script_ref = firestore.Client().collection(Constants.SCRIPT_COLLECTION)
    print("game id {0}", game_data.id)
    pgn = game_data.get(u'pgn')
    print(pgn)
    script = ChessScript(pgn)
    bucket = storage_client.get_bucket("{0}-bucket" % storage_client.project)
    for game in script:
        filename = script.get_filename()
        tmp_svg_filename = save_svg(game, filename)
        print(tmp_svg_filename)
        convert_to_png(game_data, game, filename, tmp_svg_filename, bucket)
        save_audio_blob(script, game, bucket)
    script_ref.document(game_data.id).set({
        Constants.AUDIO_FIELD: '',
        Constants.DESCRIPTION_FIELD: script.get_description(),
        Constants.SCENES_COUNT_FIELD: script.get_half_moves_count(),
        Constants.TITLE_FIELD: script.get_title(),
        Constants.VIDEO_FIELD: '',
    })
    games_ref.document(game_data.id).update({
        Constants.SCRIPT_FIELD: game_data.id
    })
    Publisher.publish(Constants.SCRIPT_CREATED_TOPIC, { Constants.ID_FIELD: game_data.id })

def app(event, context):
    games_ref = firestore.Client().collection(Constants.CHESS_GAME_COLLECTION)
    print('initialized')
    query = games_ref \
        .where(u'Result', '==', '1-0') \
        .where(Constants.SCRIPT_FIELD, '==', '') \
        .order_by(u'HalfMoves') \
        .order_by(u'WhiteElo', direction=firestore.Query.DESCENDING) \
        .limit(1)
    for game_data in query.stream():
        chess_to_script(games_ref, game_data)
        
if __name__ == "__main__":
    # execute only if run as a script
    app(None, None)
