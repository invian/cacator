from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from server.adapters.fake import FakeSessionStorage
from server.adapters.tinydb import TinyDBSessionStorage
from server.schemas import Session


@pytest.mark.skip(reason="TinyDB isn't used")
@given(st.builds(Session))
def test_session_write(session: Session):
    session_code = "test"
    fake_repo = FakeSessionStorage()
    tiny_repo = TinyDBSessionStorage(Path("tests/tmp/test.db"))

    fake_repo.update(session_code, session)
    tiny_repo.update(session_code, session)

    assert fake_repo.all_sessions() == tiny_repo.all_sessions()
    tiny_repo.path.unlink()


@pytest.mark.skip(reason="TinyDB isn't used")
@given(st.builds(Session))
def test_session_read(session: Session):
    session_code = "test"
    fake_repo = FakeSessionStorage()
    tiny_repo = TinyDBSessionStorage(Path("tests/tmp/test.db"))

    fake_repo.update(session_code, session)
    tiny_repo.update(session_code, session)

    assert fake_repo.session(session_code) == tiny_repo.session(session_code)
    tiny_repo.path.unlink()
