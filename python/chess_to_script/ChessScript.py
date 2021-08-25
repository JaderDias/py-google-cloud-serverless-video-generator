from unittest.case import TestCase
from NonCryptographicHash import fastHash
import chess.pgn
import io
import Constants

class ChessScript:
    def __init__(self, pgn):
        self.pgn = pgn
        with io.StringIO(pgn) as pgn_io:
            self.game = chess.pgn.read_game(pgn_io)
        self.headers = self.game.headers
    def __iter__(self):
        return self
    def __next__(self):
        if self.game.is_end():
            raise StopIteration
        self.previous_position = self.game.board()
        self.game = self.game.next()
        return self.game
    def get_description(self):
        return self.pgn
    def get_filename(self):
        fen_and_last_move = "{0}{1}".format(
            self.game.board().fen(),
            self.game.move
        )
        return fastHash(fen_and_last_move)
    def piece_at(self, square):
        piece_type = self.previous_position.piece_type_at(square)
        return chess.piece_name(piece_type)
    def _get_text(self):
        board = self.previous_position
        move = self.game.move
        if board.is_queenside_castling(move):
            if board.turn == chess.BLACK:
                return 'black castles on the Queen side'
            else:
                return 'white castles on the Queen side'
        if board.is_kingside_castling(move):
            if board.turn == chess.BLACK:
                return 'black castles on the King side'
            else:
                return 'white castles on the King side'
        if board.is_en_passant(move):
            from_square_name = chess.SQUARE_NAMES[move.from_square]
            return 'the {0} pawn takes en passant'.format(
                from_square_name
            )
        moving_piece = self.piece_at(move.from_square)
        to_square_name = chess.SQUARE_NAMES[move.to_square]
        if board.is_capture(move):
            captured_piece = self.piece_at(move.to_square)
            return '{0} captures the {1} on {2}'.format(
                moving_piece,
                captured_piece,
                to_square_name)
        return '{0} to {1}'.format(moving_piece, to_square_name)
    def get_text(self):
        text = self._get_text()
        board = self.game.board()
        if board.is_checkmate():
            return "{0}, and that's checkmate".format(text)
        if board.is_stalemate():
            return "{0}, and that's a stalemate".format(text)
        if board.is_check():
            return "{0}, with a check".format(text)
        return text
    def get_title(self):
        headers = self.headers
        return "{0} vs {1} on {2} round {3}".format(
            headers["White"],
            headers["Black"],
            headers["Date"],
            headers["Round"]
        )
    def get_white_player_name(self):
        return self.headers["White"].split(",")[0]
    def get_half_moves_count(self):
        half_moves = 0
        for _ in ChessScript(self.pgn):
            half_moves += 1
        return half_moves
    def get_castle(self, color):
        clone = ChessScript(self.pgn)
        for child_game in clone:
            board = clone.previous_position
            if board.turn != color:
                continue
            move = child_game.move
            if board.is_queenside_castling(move):
                return 'q'
            if board.is_kingside_castling(move):
                return 'k'
        return ''
    def audio_blob_path(self):
        self.text = self.get_text()
        self.text_digest = fastHash(self.text)
        print("text {0} digest {1}".format(
            self.text,
            self.text_digest,
        ))
        path = "{0}/{1}".format(
            Constants.AUDIO_BLOB,
            self.text_digest
        )
        return path