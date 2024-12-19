import click
import yaml

from rdflib import Graph, Namespace, Literal
from typing import Mapping


def get_property_mapping(data: Mapping, schema: Mapping) -> Mapping:
    mapping = None
    translation_class = schema["classes"].get("Translation", None)
    if translation_class is not None:
        namespace_mapping = {
            key: Namespace(value) for key, value in schema["prefixes"].items()
        }
        mapping = {}
        data_entry = next(iter(data.values()))[0]
        translations = data_entry.get("translations", None)
        if translations is not None:
            for translation in translations:
                property_name = translation["property_name"]
                property_uri = schema["slots"][property_name]["slot_uri"]
                property_namespace, property_term = property_uri.split(":")
                mapping[property_name] = getattr(
                    namespace_mapping[property_namespace], property_term
                )

    return mapping


@click.command()
@click.option("--schema_path", "-s", type=click.Path(exists=True), required=True)
@click.option("--data_path", "-d", type=click.Path(exists=True), required=True)
@click.option("--turtle_path", "-t", type=click.Path(exists=True), required=True)
@click.option("--namespace", "-n", type=str, required=True)
@click.option("--out_path", "-o", type=click.Path(), default="voc.skos.ttl")
def add_language_annotation(schema_path, data_path, turtle_path, namespace, out_path):
    # Load the schema and data from YAML files
    with open(schema_path, "r") as schema_file:
        schema = yaml.safe_load(schema_file)

    with open(data_path, "r") as data_file:
        data = yaml.safe_load(data_file)

    # Define the mapping
    property_mapping = get_property_mapping(data, schema)
    if property_mapping is None:
        raise ValueError("LinkML schema does not contain translations.")

    # Initialize the graph and namespace
    g = Graph()
    BASE = Namespace(namespace)
    # Parse the RDF file
    g.parse(turtle_path)

    #  Iterate over the triples and perform the transformation and removal
    for s, p, o in g.triples((None, BASE.translations, None)):
        language = g.value(o, BASE.language)
        property_name = str(g.value(o, BASE.property_name))
        translated_value = g.value(o, BASE.translated_value)
        # Apply the mapping
        if property_name in property_mapping:
            mapped_property = property_mapping[property_name]
            g.add((s, mapped_property, Literal(translated_value, lang=language)))

        # Remove the unnecessary blank node triples
        g.remove((o, None, None))
        g.remove((None, None, o))

    # generate output: serialize the graph to a Turtle file
    g.serialize(destination=out_path, format="turtle")


if __name__ == "__main__":
    add_language_annotation()
