# `bgtrain`
Backgammon position database --- backgammon training web application.

Running at https://www.bgtrain.com/ .


## Running `bgtrain`

Install dependencies:
```bash
sudo apt install gnubg sqlite3
# or equivalent on your platform
```

Set up your virtual environment:
```bash
pip install -r requirements.txt
```

Edit the `config` file to use appropriate directories for your setup.

Set up the database
```bash
sqlite3 /path/to/db.sqlite < db_schema/db_schema.sql
 sqlite3 /path/to/db.sqlite < initial_data/initial_data.sql 
```


Generate some positions
```bash
# generate positions for 5 minutes
BGTRAIN_CONFIG_FILE=config python -m generate 5 0
```

Start the deveserver
```bash
BGTRAIN_CONFIG_FILE=config python -m webapp devserver
```

To start the devserver run "python webapp.py devserver"
