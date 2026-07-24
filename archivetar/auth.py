"""Command-line support for authenticating with Globus before an archive job."""

import argparse
import os

from GlobusTransfer import GlobusTransfer


def parse_args(argv):
    """Parse arguments for ``archivetar auth``.

    A configured destination can be authorized without requiring a source or
    destination path.
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
    parser.add_argument(
        "--destination",
        default=os.getenv("AT_DESTINATION"),
        help="Destination collection to authorize. Defaults to AT_DESTINATION when set.",
    )
    return parser.parse_args(argv)


def main(argv):
    """Authenticate and optionally authorize a destination without a transfer."""
    args = parse_args(argv)
    globus = GlobusTransfer.authenticate(
        force_authentication=args.force,
        destination=args.destination,
    )
    print(
        "Globus authentication is ready. "
        f"Tokens are stored in {globus.token_file}."
    )
