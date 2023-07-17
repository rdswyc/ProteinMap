# ProteinMap application
> Rodrigo Chin

A rest API with protein information.
This application was developed in `Python 3.11.3` using the `Django Rest Framework`.

The project was built using a virtual environment using the commands below:

``` bash
# Install dependencies for development and testing
pip install django==3.0.3
pip install djangorestframework==3.14.0
pip install factory_boy==3.0.1

# Use a virtual environment
source virtualenvwrapper.sh
mkvirtualenv -p python3 cm3035_midterm

# Create blank project and app
django-admin startproject midterm
cd midterm
python manage.py startapp proteinmap
```

A full list of dependencies can be found on
[requirements.txt](midterm/requirements.txt).

## Project structure

- [data](data)
Provided CSV files used to populate the database.

- [midterm](midterm)
All source code including the `manage.py` file.

- [midterm/midterm](midterm/midterm)
Main project folder containing settings and URL mapping.

- [midterm/proteinmap](midterm/proteinmap)
App folder containing API mappings, models and serializers.

  - [api.py](midterm/proteinmap/api.py)
  API views and methods.

  - [model_factories.py](midterm/proteinmap/model_factories.py)
  Factory objects and fakes used by the tests.

  - [serializers.py](midterm/proteinmap/serializers.py)
  Serializer classes with mappings and validation.

  - [urls.py](midterm/proteinmap/urls.py)
  Endpoints and path mappings.

- [midterm/scripts](midterm/scripts)
Path to the script to populate initial database data.

- [midterm/openapi-schema.yml](midterm/openapi-schema.yml)
OpenAPI specification used by the Swagger UI.

## Setup

To get the application up and running, unzip the files and run the commands:

```bash
# Change directory to the project
cd midterm

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run tests
python manage.py test

# Start the development server
python manage.py runserver
```

## Database

This is the relational model:

- Organism (*taxa_id*, clade, genus, species)
- Protein (*protein_id*, length, organism_id)
- Sequence (*protein_id*, sequence)
- Pfam (*pfam_id*, description)
- Domain (*protein_id*,  *pfam_id*, description, start, stop)

A script was provided to populate initial data into the database.
Data is presented in the `csv` format, and available on the [data](data) folder.

```bash
# Optional. Run script to populate data on the database
python midterm/scripts/populate_data.py
```

## Django administration

All the database information is exposed by the endpoints of the application.
However, the Django administration site was enabled with management for all tables.
In order the login, a `superuser` was created using the command below:

```bash
python manage.py createsuperuser
> Username: admin
> Email address: rodrigo.chin@outlook.com
> Password: Physalis
```

## OpenAPI Specification

By default, the home page for the app will redirect to the Swagger UI.
The OpenAPI Specification was done using these commands:

```bash
pip install pyyaml uritemplate
python manage.py generateschema --file openapi-schema.yml
```

## Data validation

Most of the data validation is done on the serializer level.
There are also database constraints on data types and lengths.
After observing the provided data, more validations were implemented.
- Organism clade was limited to 2 characters, since all sample data have the value `E`. This might be misleading.
- Protein sequence only allows 20 amino acids defined on the `AMINOACIDS` setting. This is based on [Amino Acid Code](https://www.genscript.com/Amino_Acid_Code.html).
- On post, if the protein sequence is provided, it should match with the also provided protein length.
- The domain start and stop values must be in the correct order.

It is relevant to say that not all protein sequences on the provided data would pass the amino acid validation such as `A5AHB2` and `E2D4M6`.
