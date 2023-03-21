from hcraft.cli import hcraft_cli
from hcraft.render.human import render_env_with_human


def main():
    """Run hcraftommand line interface."""
    env = hcraft_cli()
    render_env_with_human(env)


if __name__ == "__main__":
    main()
