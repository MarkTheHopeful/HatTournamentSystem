EXAMPLE_USER = ("Example User", "Never Gonna Give You Up")
EXAMPLE_TOURNAMENT_NAME = "Example tournament"
EXAMPLE_ROUNDS_NAMES = ["Example round 1", "Example round 2"]
EXAMPLE_SUBROUNDS = [
    ("Subround 1.1", 0),
    ("Subround 1.2", 0),
    ("Subround 2.1", 1),
    ("Subround 2.2", 1),
]

EXAMPLE_WORDS = [(f"Word {i}", i % 6 + 1) for i in range(50)]
EXAMPLE_PLAYERS = [
    (f"Player {2 * i}", f"Player {2 * i + 1}", (i % 4) // 2, i % 4, i + 1)
    for i in range(20)
]
