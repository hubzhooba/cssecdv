Download Zip and Unzip Folder
Open CLI, and do "pip install virtualenv" in the Main Directory.
Create a virtual machine locally via "virtualenv .venv" or "python -m virtualenv .venv".
After the installation run the virtual environment by entering in the CLI ".venv/Scripts/activate" (Assuming you're using Windows).
Go toIn the Main Directory and run uvicorn main:app --reload(ensure all Dependencies are installed).
Run web app at: http://127.0.0.1:8000/register

For running with self signed certificate use this command:
uvicorn main:app --host 127.0.0.1 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem