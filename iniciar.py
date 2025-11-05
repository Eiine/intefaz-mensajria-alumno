import os
import subprocess
import sys
from pathlib import Path

# Detectar la ruta del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Detectar sistema operativo
IS_WINDOWS = os.name == "nt"

# Ruta al Python del entorno virtual
python_venv = BASE_DIR / ".venv" / ("Scripts" if IS_WINDOWS else "bin") / ("python.exe" if IS_WINDOWS else "python")

# Archivo manage.py
manage_py = BASE_DIR / "manage.py"

# Comando a ejecutar
comando = [str(python_venv), str(manage_py), "runserver"]

print("🚀 Iniciando servidor Django...")
print(f"Usando entorno virtual: {python_venv}")

# Ejecutar el comando
subprocess.run(comando)
