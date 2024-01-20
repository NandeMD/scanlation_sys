# Scanlation API
Almost every data related to the tasks performed is stored here, and it serves as the backbone of the entire system.

Uses SQLite as databases. DB schemas are present in `chs`, `speedruns` and `sqa` directories.

Uses FastAPI framework so you can access automatically generated API docs from `api_url/docs` and `api_url/redoc`.

Do not expose this API to the internet openly because it lacks authentication. Otherwise, your team's data could be at risk of external exposure.
It is designed only for internal use by the main bot and the website.

Note: Speedrun endpoints are not implemented yet.
## How To Use

1. Install Python 3.11 or higher.
2. Create a virtual environment.
    ```bash
   # On Linux and Mac:
   cd project_dir
   python3 -m venv venv
   source venv/bin/activate
   
   # On Windows:
   cd project_dir
   py -m venv venv
   venv\Scripts\activate
   ```
3. Install requirements.
   ```bash
   # On Linux and Mac:
   pip3 install -r requirements.txt
   
   # On Windows:
   pip install -r requirements.txt
   ```
4. Start the API. This will start to listen 0.0.0.0:8000.
   ```bash
   # On Linux and Mac:
   sudo chmod +x start.sh
   ./start.sh
   
   # On Windows:
   # I use Ubuntu as a daily driver so you have to figure out how to run FastAPI on Windows
   ```
5. To access docs, visit http://0.0.0.0:8000/docs or http://0.0.0.0:8000/redoc.