import click
import yaml

from linkml_runtime import SchemaView
from rdflib import Graph, Namespace, Literal, URIRef
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


def parse_property_uri(property_uri: str, graph: Graph) -> URIRef:
    """
    Parse a property URI which can be in the format:
    - 'namespace:term' (using prefixes from the graph)
    - Full URI like 'http://example.com/property'
    """
    if ":" in property_uri and not property_uri.startswith(("http://", "https://")):
        # Handle namespace:term format
        namespace_prefix, term = property_uri.split(":", 1)
        
        # Get the namespace URI from the graph's namespace manager
        namespace_uri = None
        for prefix, uri in graph.namespace_manager.namespaces():
            if prefix == namespace_prefix:
                namespace_uri = str(uri)
                break
        
        if namespace_uri is None:
            raise ValueError(f"Namespace prefix '{namespace_prefix}' not found in the RDF graph")
        
        return URIRef(namespace_uri + term)
    else:
        # Handle full URI
        return URIRef(property_uri)


@click.command()
@click.option("--schema_path", "-s", type=click.Path(exists=True), required=True,
              help="Path to the LinkML schema YAML file")
@click.option("--data_path", "-d", type=click.Path(exists=True), required=True,
              help="Path to the data YAML file")
@click.option("--turtle_path", "-t", type=click.Path(exists=True), required=True,
              help="Path to the input Turtle RDF file")
@click.option("--out_path", "-o", type=click.Path(), default="voc.skos.ttl",
              help="Output path for the modified Turtle file")
def add_language_annotation(schema_path, data_path, turtle_path, out_path):
    """
    Add language annotations to RDF properties based on translation data.
    
    This script transforms translation objects in RDF into language-tagged literals
    attached directly to the original properties.
    """
    # Load the schema and data from YAML files
    with open(schema_path, "r") as schema_file:
        schema = yaml.safe_load(schema_file)

    with open(data_path, "r") as data_file:
        data = yaml.safe_load(data_file)

    # Define the mapping
    property_mapping = get_property_mapping(data, schema)
    if property_mapping is None:
        raise ValueError("LinkML schema does not contain translations.")
    
    # get uri of translations schema
    schema_view = SchemaView(schema_path)
    property_name_uri = schema_view.get_uri('property_name', expand=True)
    language_uri = schema_view.get_uri('language', expand=True)
    translated_value_uri = schema_view.get_uri('translated_value', expand=True)
    translations_uri = schema_view.get_uri('translations', expand=True)

    # Initialize the graph and namespace
    g = Graph()
    # Parse the RDF file
    g.parse(turtle_path)

    # Parse the configurable property URIs
    property_name_predicate = parse_property_uri(property_name_uri, g)
    language_predicate = parse_property_uri(language_uri, g)
    translated_value_predicate = parse_property_uri(translated_value_uri, g)
    translations_predicate = parse_property_uri(translations_uri, g)

    click.echo(f"Using translations predicate: {translations_predicate}")
    click.echo(f"Using property name predicate: {property_name_predicate}")
    click.echo(f"Using language predicate: {language_predicate}")
    click.echo(f"Using translated value predicate: {translated_value_predicate}")

    # Debug: show all translation triples found
    translation_triples = list(g.triples((None, translations_predicate, None)))
    click.echo(f"Found {len(translation_triples)} translation objects")
    
    # Iterate over the triples and perform the transformation and removal
    for s, p, o in translation_triples:
        language = g.value(o, language_predicate)
        property_name = str(g.value(o, property_name_predicate))
        translated_value = g.value(o, translated_value_predicate)
        
        # Apply the mapping
        if property_name in property_mapping:
            mapped_property = property_mapping[property_name]
            g.add((s, mapped_property, Literal(translated_value, lang=language)))
            click.echo(f"Added translation: {s} {mapped_property} '{translated_value}'@{language}")

        # Remove the unnecessary blank node triples
        g.remove((o, None, None))
        g.remove((None, None, o))

    # Generate output: serialize the graph to a Turtle file
    g.serialize(destination=out_path, format="turtle")
    click.echo(f"Output written to: {out_path}")


if __name__ == "__main__":
    add_language_annotation()