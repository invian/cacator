from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from server.adapters.tinydb import TinyDBSessionStorage
from server.schemas import Session, Stream


@given(st.integers(min_value=0, max_value=50))
def test_packet(total: int):
    stream = Stream(total_pkts=total)
    assert len(stream.pkts) == total


@given(st.builds(Stream))
def test_stream_data_persists(stream: Stream):
    session_code = "test"
    session = Session(streams={"aa": stream})
    path = Path("tests/tmp/test.db")
    if path.exists():
        path.unlink()
    repo = TinyDBSessionStorage(path)
    repo.update(session_code, session)

    session_in_repo = repo.session(session_code)
    assert session_in_repo
    assert session_in_repo.streams["aa"] == session.streams["aa"]
