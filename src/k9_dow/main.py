# SPDX-License-Identifier: Apache-2.0
# DAS CLI entry point

import click


@click.group()
def cli():
    pass


@cli.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8000, type=int)
def serve(host, port):
    import uvicorn
    uvicorn.run("k9_dow.api.app:app", host=host, port=port, reload=True)


@cli.command()
def version():
    from k9_dow.config.settings import build_info
    click.echo(f"DAS — Defense Acquisition System v{build_info()['version']}")


if __name__ == "__main__":
    cli()
