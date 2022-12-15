# Demos

It contains data and scripts to run demos for each case study.

## Quick start

## Developing

### Structure

- `data`: contains sample data for each case study. Additionally, there is a `<museum>_template.env` that can
be used to deploy the Community model
- `config.py`: Dictionaries employed to send POST requests. They are configured according to the template.env
described above.
- `postUser.py`, `postPerspective.py` and `postContribution.py` are scripts to launch POST requests in order to
inject data to the Community model simulating the work of the User Model.

## License

The content of this repository is distributed under [Apache 2.0 License](LICENSE).
