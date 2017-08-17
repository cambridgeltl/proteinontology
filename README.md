# Protein Ontology tools

Tools for working with Protein Ontology (PRO) data
(<http://pir.georgetown.edu/pro/>).

## Quickstart

To download PRO source data and generate a JSON-LD version of the data
and a mapping between PRO and UniProt IDs, run

    ./REBUILD-DATA.sh

If succesful, this process generates the file `data/compacted/pr.jsonld`
and `pr-idmapping.dat`.

Note that this process is likely to take 10-15 min and may take over an
hour to complete on some systems.

## Requirements

- Unix shell and standard tools (e.g. `wget`)
- Python 2.7
- Java Development Kit (e.g. <http://openjdk.java.net>)
- Maven (<https://maven.apache.org>)

## Troubleshooting

- `ogconvert` step fails with error `ogger not found`: this step
  requires OBO Graphs (<https://github.com/geneontology/obographs>)
  tools. If these are installed on the system, you can update the
  script `scripts/30-ogconvert.sh` to make the `CONVERTER` variable
  point to the correct location. Alternatively, a local version can
  be installed by running

      git clone https://github.com/geneontology/obographs.git
      cd obographs
      mvn install

  in the root directory of this repository.

- OBO Graphs `mvn install` fails at `sign-artifacts` step: GPG is not
  set up for signing. Although the build does not complete with
  success, signing is not necessary to use OBO Graphs: if the directory
  `obographs/bin` contains the files `ogger` and `obographs.jar`, the
  tool should work without resolving this error.
