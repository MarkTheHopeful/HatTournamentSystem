from sqlalchemy import Table

from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, unique=True)
    password_hash = db.Column(db.String)
    tokens = db.relationship('Token', backref='owner', lazy='dynamic')
    tournaments = db.relationship('Tournament', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


class Token(db.Model):
    id = db.Column(db.String, primary_key=True)
    expires_in = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Token {self.id} of user {self.user_id}>'


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    players = db.relationship('Player', backref='tournament', lazy='dynamic')
    words = db.relationship('Word', backref='tournament', lazy='dynamic')
    rounds = db.relationship('Round', backref='tournament', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


players_in_rounds = Table("players_in_rounds", db.Model.metadata,
                          db.Column("player_id", db.Integer, db.ForeignKey('player.id'), primary_key=True),
                          db.Column("round_id", db.Integer, db.ForeignKey('round.id'), primary_key=True))


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    difficulty = db.Column(db.Integer)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    players = db.relationship(
        "Player",
        secondary=players_in_rounds,
        back_populates="rounds")
    # subrounds = db.relationship('Subround', backref='round', lazy='dynamic')


# class Subround(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
#
#
# class Game(db.Model):
#     id = db.Column(db.Integer, primary_key=True)


class Player(db.Model):     # FIXME: Actually, it's a pair of players, but I postponed renaming
    id = db.Column(db.Integer, primary_key=True)
    name_first = db.Column(db.String, index=True)
    name_second = db.Column(db.String, index=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    rounds = db.relationship(
        "Round",
        secondary=players_in_rounds,
        back_populates="players"
    )


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, index=True, unique=True)
    difficulty = db.Column(db.Integer, index=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
