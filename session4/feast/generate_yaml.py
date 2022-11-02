import os
import click

from jinja2 import Environment, FileSystemLoader
from glob import glob


@click.command()
@click.option("--redis-url", required=True)
@click.option("--registry-url", required=True)
def generate_yaml(redis_url: str="localhost:6379",
                  registry_url: str="s3://data/feast/dev/registry.pb",
                  templates_dir="feature_store"):
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )

    for x in glob(os.path.join(templates_dir, "*.yaml")):
        os.remove(x)

    for x in glob(os.path.join(templates_dir, "*.yaml.j2")):
        x = os.path.basename(x)
        template = env.get_template(x)
        with open(os.path.join(templates_dir, x.replace(".j2", "")), "w") as f:
            f.write(template.render(registry_url=registry_url, redis_url=redis_url))


if __name__ == "__main__":
    generate_yaml()
