import pytest

from sentinel_uas import cli


@pytest.mark.unit
def test_cli_starts_local_uvicorn(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: dict[str, object] = {}

    def fake_run(app: str, **kwargs: object) -> None:
        observed["app"] = app
        observed.update(kwargs)

    monkeypatch.setattr(cli.uvicorn, "run", fake_run)

    cli.main()

    assert observed == {
        "app": "sentinel_uas.app:app",
        "host": "127.0.0.1",
        "port": 8080,
        "reload": False,
    }
