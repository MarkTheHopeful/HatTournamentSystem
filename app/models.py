from sqlalchemy import Table

from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    tokens = db.relationship('Token', backref='owner', lazy='dynamic')
    tournaments = db.relationship('Tournament', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


class Token(db.Model):
    id = db.Column(db.String, primary_key=True)
    expires_in = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Token {self.id} of user {self.user_id}>'


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    players = db.relationship('Player', backref='tournament', lazy='dynamic', cascade="all, delete-orphan")
    words = db.relationship('Word', backref='tournament', lazy='dynamic', cascade="all, delete-orphan")
    rounds = db.relationship('Round', backref='tournament', lazy='dynamic', cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


players_in_rounds = Table("players_in_rounds", db.Model.metadata,
                          db.Column("player_id", db.Integer, db.ForeignKey('player.id'), primary_key=True),
                          db.Column("round_id", db.Integer, db.ForeignKey('round.id'), primary_key=True))

players_in_subrounds = Table("players_in_subrounds", db.Model.metadata,
                             db.Column("player_id", db.Integer, db.ForeignKey('player.id'), primary_key=True),
                             db.Column("subround_id", db.Integer, db.ForeignKey('subround.id'), primary_key=True))

players_in_games = Table("players_in_games", db.Model.metadata,
                         db.Column("player_id", db.Integer, db.ForeignKey('player.id'), primary_key=True),
                         db.Column("game_id", db.Integer, db.ForeignKey("game.id"), primary_key=True))


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    players = db.relationship(
        "Player",
        secondary=players_in_rounds,
        back_populates="rounds",
        lazy='dynamic')
    subrounds = db.relationship('Subround', backref='round', lazy='dynamic', cascade="all, delete-orphan")
    results = db.Column(db.PickleType)


class Subround(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)
    players = db.relationship(
        "Player",
        secondary=players_in_subrounds,
        back_populates="subrounds",
        lazy='dynamic'
    )
    words = db.relationship('Word', backref='subround', lazy='dynamic')
    games = db.relationship('Game', backref='subround', lazy='dynamic', cascade="all, delete-orphan")
    results = db.Column(db.PickleType)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subround_id = db.Column(db.Integer, db.ForeignKey('subround.id'), nullable=False)
    players = db.relationship(
        "Player",
        secondary=players_in_games,
        back_populates="games",
        lazy='dynamic',
    )
    results = db.Column(db.PickleType)
    results_set = db.Column(db.Boolean)


class Player(db.Model):  # FIXME: Actually, it's a pair of players, but I postponed renaming
    id = db.Column(db.Integer, primary_key=True)
    name_first = db.Column(db.String, index=True, nullable=False)
    name_second = db.Column(db.String, index=True, nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    rounds = db.relationship(
        "Round",
        secondary=players_in_rounds,
        back_populates="players",
        lazy='dynamic'
    )
    subrounds = db.relationship(
        "Subround",
        secondary=players_in_subrounds,
        back_populates="players",
        lazy='dynamic'
    )
    games = db.relationship(
        "Game",
        secondary=players_in_games,
        back_populates="players",
        lazy='dynamic'
    )


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, index=True, unique=True, nullable=False)
    difficulty = db.Column(db.Integer, index=True, nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    subround_id = db.Column(db.Integer, db.ForeignKey('subround.id'))
    random_seed = db.Column(db.Integer, index=True, nullable=False)
