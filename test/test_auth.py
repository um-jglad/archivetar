import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import MagicMock

import archivetar
import archivetar.auth
import pytest
from GlobusTransfer import GlobusTransfer
import GlobusTransfer as globus_transfer_module


def test_auth_does_not_access_a_collection(monkeypatch, capsys):
    """The auth command creates an authorizer without collection defaults."""
    transfer = MagicMock()
    transfer.token_file = Path("/tmp/globus/tokens.json")
    authenticate = MagicMock(return_value=transfer)
    monkeypatch.setattr(archivetar.auth.GlobusTransfer, "authenticate", authenticate)

    archivetar.auth.main([])

    authenticate.assert_called_once_with(force_authentication=False)
    assert "tokens.json" in capsys.readouterr().out


def test_auth_force_replaces_the_saved_token(monkeypatch):
    """--force asks GlobusTransfer to begin a new native-app login."""
    authenticate = MagicMock()
    monkeypatch.setattr(archivetar.auth.GlobusTransfer, "authenticate", authenticate)

    archivetar.auth.main(["--force"])

    authenticate.assert_called_once_with(force_authentication=True)


def test_authenticate_initializes_without_a_collection(tmp_path, monkeypatch):
    """Generic authentication does not require source or destination details."""
    native_client = MagicMock()
    transfer_client = MagicMock()
    login = MagicMock(return_value=transfer_client)
    monkeypatch.setattr(
        globus_transfer_module.Path, "home", classmethod(lambda _cls: tmp_path)
    )
    monkeypatch.setattr(
        globus_transfer_module.globus_sdk, "NativeAppAuthClient", native_client
    )
    monkeypatch.setattr(GlobusTransfer, "do_native_app_authentication", login)

    auth = GlobusTransfer.authenticate(force_authentication=True)

    native_client.assert_called_once_with("8359fb34-39cf-410d-bd93-e8502aa68c46")
    login.assert_called_once_with()
    assert auth.tc is transfer_client
    assert auth.token_file == tmp_path / ".globus" / "tokens.json"
    assert not hasattr(auth, "ep_source")


def test_main_dispatches_auth_without_archive_arguments(monkeypatch):
    """Auth is a top-level command and therefore does not require --prefix."""
    auth_main = MagicMock()
    monkeypatch.setattr(archivetar.auth, "main", auth_main)

    archivetar.main(["archivetar", "auth", "--force"])

    auth_main.assert_called_once_with(["--force"])


def test_wrapper_keeps_auth_out_of_slurm(monkeypatch):
    """Authentication is always run in the current interactive shell."""
    wrapper_path = Path(__file__).parents[1] / "bin" / "archivetar"
    loader = SourceFileLoader("archivetar_wrapper", str(wrapper_path))
    spec = importlib.util.spec_from_loader("archivetar_wrapper", loader)
    wrapper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wrapper)

    run = MagicMock(return_value=MagicMock(returncode=0))
    monkeypatch.setattr(wrapper.subprocess, "run", run)
    monkeypatch.setattr(sys, "argv", ["archivetar", "auth", "--force"])
    monkeypatch.setenv("AT_SLURM_OFFLOAD", "1")

    with pytest.raises(SystemExit) as exit_status:
        wrapper.main()

    assert exit_status.value.code == 0
    run.assert_called_once_with([".archivetar", "auth", "--force"])
