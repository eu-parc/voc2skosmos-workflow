import click
import logging
import yaml
import sys

from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def modify_schema_dict(schema: Dict, entity_name: str) -> bool:
    try:
        schema['classes'][entity_name]['class_uri'] = 'http://www.w3.org/2004/02/skos/core#Concept'
    except KeyError as e:
        logger.error(f"Schema does not have the required classes/{entity_name}/class_uri structure: {e}")
        sys.exit(1)
    
    return True

@click.command()
@click.option("--schema_path", "-s", type=click.Path(exists=True), required=True,
              help="Path to the LinkML schema YAML file")
@click.option("--skos_schema_path", "-o", "skos_schema_path", type=click.Path(exists=False), required=True,
              help="Outputpath to the modified LinkML schema YAML file")
@click.option("--entity", '-e', 'entity', type=str, help="Name of class that is a skos concept.")
def modify_schema(schema_path: str, skos_schema_path:str, entity: str):
    with open(schema_path, 'r') as f:
        schema_dict = yaml.safe_load(f)

    logger.info(f'Changing class_uri of entity {entity}')
    _ = modify_schema_dict(schema_dict, entity) 

    with open(skos_schema_path, 'w') as f:
        yaml.safe_dump(schema_dict, stream=f, sort_keys=False)

if __name__ == "__main__":
    modify_schema()