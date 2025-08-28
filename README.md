# Documentation voc2skosmos
This repository contains two reusable actions that can be used to build a skos-compatible vocabulary. Either you can build from a `.csv` or you can start out from a `.yaml` file with LInkML schema-compatible content.

# Publish Vocabulary Workflow from CSV

This GitHub workflow automates the process of converting vocabulary data from a **CSV** source into **SKOS (Simple Knowledge Organization System)** format using **YARRRML → RML → RDF → SKOS** transformations.  

The generated SKOS vocabulary can be uploaded as an artifact and optionally published when triggered on a release event.

---

## Workflow Overview

This workflow is designed to be **reusable** via [`workflow_call`](https://docs.github.com/en/actions/using-workflows/reusing-workflows) so it can be invoked from other workflows in the repository.  

### Key features
- Cancel any previously running workflow instances
- Convert YARRRML mappings into RML
- Use RML Mapper to generate RDF from CSV data
- Run [skosify](https://github.com/NatLibFi/skosify) to produce SKOS vocabularies
- Optionally publish SKOS files on release events

---

## Inputs

| Name             | Required | Type     | Default | Description                                        |
|------------------|----------|----------|---------|----------------------------------------------------|
| `ref`            | ✅       | `string` | —       | Git reference (branch, tag, or commit SHA) to use.  |
| `version`        | ❌       | `string` | —       | Version of the vocabulary being published.          |
| `namespace_label`| ✅       | `string` | —       | Label for the SKOS namespace.                       |
| `namespace`      | ✅       | `string` | —       | Namespace URI for the SKOS vocabulary.              |
| `mappings_file`  | ✅       | `string` | —       | Path to the YARRRML mapping file.                   |

---

## Secrets

| Name    | Required | Description                           |
|---------|----------|---------------------------------------|
| `token` | ✅       | GitHub token for repository checkout.  |

---

## Usage Example

To call this workflow from another workflow:

```yaml
name: CSV to SKOS Conversion

on:
  workflow_dispatch:

jobs:
  csv-to-skos:
    uses: ./.github/workflows/csv-to-skos.yml
    with:
      ref: main
      namespace_label: "My Vocabulary"
      namespace: "https://example.org/vocab/"
      mappings_file: "mappings/mappings.yml"
    secrets:
      token: ${{ secrets.GITHUB_TOKEN }}
```

# Publish Vocabulary Workflow from YML

This GitHub workflow automates the process of converting vocabulary data from a **YAML** source into **SKOS (Simple Knowledge Organization System)** format using **LinkML → RDF → SKOS** transformations.  

The resulting SKOS vocabulary file can be uploaded as an artifact and optionally published on release events.

---

## Workflow Overview

This workflow is designed to be **reusable** via [`workflow_call`](https://docs.github.com/en/actions/using-workflows/reusing-workflows), making it easy to integrate into other workflows in the repository.

### Key features
- Supports both local files and artifacts as data sources
- Processes LinkML schemas (from local paths or URLs)
- Adds SKOS and language annotations
- Converts YAML input into RDF, then to SKOS
- Validates the generated SKOS file
- Optionally publishes SKOS files on release events

---

## Inputs

| Name            | Required | Type     | Default | Description                                                         |
|-----------------|----------|----------|---------|---------------------------------------------------------------------|
| `ref`           | ✅       | `string` | —       | Git reference (branch, tag, or commit SHA) to use.                   |
| `version`       | ❌       | `string` | —       | Version of the vocabulary being published.                           |
| `namespace`     | ✅       | `string` | —       | Base namespace for RDF resources.                                    |
| `voc_uri`       | ✅       | `string` | —       | Namespace URI for the SKOS vocabulary.                               |
| `entity_name`   | ✅       | `string` | —       | Name of the entity class in the LinkML schema.                       |
| `linkml_schema` | ✅       | `string` | —       | Path or URL to the LinkML schema file.                                |
| `data`          | ❌       | `string` | —       | Path to the YAML data file containing vocabulary terms.               |
| `artefact_name` | ❌       | `string` | —       | Name of an artifact containing the data file (alternative to `data`). |

---

## Secrets

| Name    | Required | Description                           |
|---------|----------|---------------------------------------|
| `token` | ✅       | GitHub token for repository checkout.  |

---

## Usage Example

To call this workflow from another workflow:

```yaml
name: YML to SKOS Conversion

on:
  workflow_dispatch:

jobs:
  yml-to-skos:
    uses: ./.github/workflows/yml-to-skos.yml
    with:
      ref: main
      namespace: "https://example.org/base/"
      voc_uri: "https://example.org/vocab/"
      entity_name: "MyEntity"
      linkml_schema: "schema/my_schema.yml"
      data: "data/vocabulary.yml"
    secrets:
      token: ${{ secrets.GITHUB_TOKEN }}
