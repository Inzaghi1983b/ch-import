import pytest

from chimport.gemeinde import ist_bfs_nummer

GUELTIGE_BFS_NUMMERN = [
    "1",
    "2",
    "261",
    "1000",
    "9999",
    "0001",
    "0999",
]

UNGUELTIGE_BFS_NUMMERN = [
    "",
    "0",
    "0000",
    "10000",
    " 261",
    "261 ",
    "26a",
    "٢٦١",
    "٣",
    "2 61",
    "-1",
    "1.0",
    "00001",
    "12\n",
]


@pytest.mark.parametrize("wert", GUELTIGE_BFS_NUMMERN)
def test_ist_bfs_nummer(wert: str) -> None:
    assert ist_bfs_nummer(wert) is True


@pytest.mark.parametrize("wert", UNGUELTIGE_BFS_NUMMERN)
def test_ist_bfs_nummer_ungueltig(wert: str) -> None:
    assert ist_bfs_nummer(wert) is False


def test_grenzen_der_bfs_nummer() -> None:
    assert ist_bfs_nummer("1") is True
    assert ist_bfs_nummer("0") is False
    assert ist_bfs_nummer("9999") is True
    assert ist_bfs_nummer("10000") is False


def test_ist_bfs_nummer_wirft_nie() -> None:
    for wert in ["", "abc", "٣", "  ", "26a", "10000"]:
        assert ist_bfs_nummer(wert) is False
