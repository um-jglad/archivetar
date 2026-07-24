"""Command-line support for authenticating with Globus before an archive job."""

import argparse

from GlobusTransfer import GlobusTransfer


def parse_args(argv):
    """Parse arguments for ``archivetar auth``.

    Authentication does not access a collection, so it works on any cluster.
    """
    parser = argparse.ArgumentParser(
        prog="archivetar auth",
        description="Authenticate with Globus for a future archivetar transfer.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Start a new Globus login and replace the saved transfer token.",
    )
    return parser.parse_args(argv)


def main(argv):
    """Authenticate without accessing a collection or creating a transfer."""
    args = parse_args(argv)
    globus = GlobusTransfer.authenticate(force_authentication=args.force)
    print(
        "Globus authentication is ready. "
        f"Tokens are stored in {globus.token_file}."
    )
