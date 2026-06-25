# SPDX-License-Identifier: Apache-2.0

import argparse
import sys


def cli():
    parser = argparse.ArgumentParser(
        prog="k9-dow",
        description="K9-AIF DoW Architecture Workbench",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("serve", help="Start the FastAPI server")
    sub.add_parser("version", help="Print version")

    args = parser.parse_args()

    if args.command == "version":
        print("k9-dow 0.1.0")
    elif args.command == "serve":
        import uvicorn
        uvicorn.run("k9_dow.api.app:app", host="0.0.0.0", port=8000, reload=True)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    cli()
