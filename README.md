1. Download Zip and Unzip Folder
2. Open CLI, and do "pip install virtualenv" in the Main Directory.
3. Create a virtual machine locally via "virtualenv .venv" or "python -m virtualenv .venv".
4. After the installation run the virtual environment by entering in the CLI ".venv/Scripts/activate" (Assuming you're using Windows).
4. In the Main Directory and run uvicorn main:app --reload(ensure all Dependencies are installed).
5. Run web app at: http://127.0.0.1:8000/register
