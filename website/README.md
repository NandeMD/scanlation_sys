# Scanlation System Website
This is the website for listing and modifying entries in the API. Since using Flask with Gunicorn is recommended, it only runs on Linux.
## How To Use

1. Install Python 3.11 or higher.
2. Edit [`config.json`](https://github.com/NandeMD/scanlation_sys/blob/main/website/config.json) to your preferences.
3. Create a sqlite database from [template file](https://github.com/NandeMD/scanlation_sys/blob/main/website/website/generate_database_tables.sql), then create a user with `super` role. This user will have all the permissions for website.
4. Create a virtual environment.
    ```bash
   # On Linux and Mac:
   cd project_dir
   python3 -m venv venv
   source venv/bin/activate
   ```
5. Install requirements.
   ```bash
   # On Linux and Mac:
   pip3 install -r requirements.txt
   ```
6. Start the website.
   ```bash
   # with 4 workers
   gunicorn -w 4 'app:create_app()'
   ```
7. Login the website as your super user.