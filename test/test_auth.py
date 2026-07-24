import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import MagicMock

import archivetar
import archivetar.auth
import pytest


def test_auth_uses_selected_collections(monkeypatch, capsys):
    """The auth command validates the supplied collections without archiving."""
    transfer = MagicMock()
    transfer.token_file = Path("/tmp/globus/tokens.json")
    globus_transfer = MagicMock(return_value=transfer)
    monkeypatch.setattr(archivetar.auth, "GlobusTransfer", globus_transfer)

    archivetar.auth.main(
        [
            "--source",
            "source-collection",
            "--destination",
            "guest-collection",
            "--destination-path",
            "/guest/archive",
        ]
    )

    globus_transfer.assert_called_once_with(
        "source-collection",
        "guest-collection",
        "/guest/archive",
        force_authentication=False,
    )
    assert "tokens.json" in capsys.readouterr().out


def test_auth_force_replaces_the_saved_token(monkeypatch):
    """--force asks GlobusTransfer to begin a new native-app login."""
    globus_transfer = MagicMock()
    monkeypatch.setattr(archivetar.auth, "GlobusTransfer", globus_transfer)

    archivetar.auth.main(["--force"])

    assert globus_transfer.call_args.kwargs["force_authentication"] is True


def test_main_dispatches_auth_without_archive_arguments(monkeypatch):
    """Auth is a top-level command and therefore does not require --prefix."""
    auth_main = MagicMock()
    monkeypatch.setattr(archivetar.auth, "main", auth_main)

    archivetar.main(["archivetar", "auth", "--destination", "guest-collection"])

    auth_main.assert_called_once_with(["--destination", "guest-collection"])


def test_wrapper_keeps_auth_out_of_slurm(monkeypatch):
    """Authentication is always run in the current interactive shell."""
    wrapper_path = Path(__file__).parents[1] / "bin" / "archivetar"
    loader = SourceFileLoader("archivetar_wrapper", str(wrapper_path))
    spec = importlib.util.spec_from_loader("archivetar_wrapper", loader)
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)

    run = MagicMock(return_value=MagicMock(returncode=0))
    monkeypatch.setattr(wrapper.subprocess, "run", run)
    monkeypatch.setattr(sys, "argv", ["archivetar", "auth", "--destination", "guest"])
    monkeypatch.setenv("AT_SLURM_OFFLOAD", "1")

    with pytest.raises(SystemExit) as exit_status:
        wrapper.main()

    assert exit_status.value.code == 0
    run.assert_called_once_with([".archivetar", "auth", "--destination", "guest"])
