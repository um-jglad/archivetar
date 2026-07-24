"""Command-line support for authenticating with Globus before an archive job."""

import argparse

from environs import Env

from GlobusTransfer import GlobusTransfer


def parse_args(argv):
    """Parse arguments for ``archivetar auth``.

    The source and destination are checked after authentication so that any
    collection-specific consent or single-domain requirements are handled
    while the user is still at an interactive terminal.
    """
    env = Env()
    parser = argparse.ArgumentParser(
        prog="archivetar auth",
        description="Authenticate with Globus for a future archivetar transfer.",
    )
    parser.add_argument(
        "--source",
        default=env.str("AT_SOURCE", default="umich#greatlakes"),
        help="Source collection. Defaults to AT_SOURCE or umich#greatlakes.",
    )
    parser.add_argument(
        "--destination",
        default=env.str("AT_DESTINATION", default="umich#flux"),
        help="Destination collection. Defaults to AT_DESTINATION or umich#flux.",
    )
    parser.add_argument(
        "--destination-dir",
        "--destination-path",
        default="~",
        help="Path used to validate the destination collection. Defaults to ~.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Start a new Globus login and replace the saved transfer token.",
    )
    return parser.parse_args(argv)


def main(argv):
    """Authenticate and validate the collections without creating a transfer."""
    args = parse_args(argv)
    globus = GlobusTransfer(
        args.source,
        args.destination,
        args.destination_dir,
        force_authentication=args.force,
    )
    print(
        "Globus authentication is ready for "
        f"{args.source} to {args.destination}. Tokens are stored in {globus.token_file}."
    )
