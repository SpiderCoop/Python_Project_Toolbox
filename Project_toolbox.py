"""
Created on Thu Jan 30 12:30:09 2025

@author: DJIMENEZ
"""
# Librerias necesarias ---------------------------------------------------------------------------------------------------

import subprocess
import sys
import os

# Creacion de la clase Project -------------------------------------------------------------------------------------------

class Project:
    def __init__(self, directory:str=None, venv_name:str='venv', requirements_name:str='requirements.txt'):
        self.directory = directory
        self.venv_name = venv_name
        self.venv_path = self.venv_name if self.directory is None else os.path.join(self.directory, self.venv_name)
        self.requirements_path = requirements_name if self.directory is None else os.path.join(self.directory, requirements_name)

    # Funcion para crear un archivo de .gitignore con los patrones de archivos mas comunes
    def create_default_gitignore(self):
        """
        Crea un archivo .gitignore con contenido predeterminado.
        
        """
        # Definir la ruta al archivo .gitignore
        gitignore_path = '.gitignore' if self.directory is None else os.path.join(self.directory, '.gitignore')
        
        # Contenido predeterminado para el archivo .gitignore
        gitignore_content = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Caches and logs
.cache
*.log
*.tmp

# Virtual environment
venv/
*.venv

# Operating system files
.DS_Store
Thumbs.db

# IDE and editor directories
.idea/
.vscode/
*.swp
*~

# Node.js dependencies
node_modules/

# Build artifacts
/dist/
/build/
/target/

# Ignore secrets and credentials
secrets.yaml
config/credentials.yml

# Personal files
Project_toolbox.py
.env
*.pdf
"""

        # Intentar escribir el contenido en el archivo .gitignore
        try:
            with open(gitignore_path, "w") as file:
                file.write(gitignore_content)
            print(f"Archivo .gitignore creado con configuración predeterminada en {gitignore_path}.")
        except Exception as e:
            print(f"Error al crear el archivo .gitignore en {gitignore_path}: {e}")

    # Funcion para crear un ambiente virtual
    def create_virtual_environment(self):
        """
        Crea un entorno virtual en el directorio especificado.
        
        """
        
        if os.path.exists(self.venv_path):
            print(f"El entorno virtual '{self.venv_name}' ya existe.")
        else:
            try:
                print(f"Creando el entorno virtual '{self.venv_name}' en {self.venv_path}...")
                subprocess.check_call([sys.executable, '-m', 'venv', self.venv_path])
                print(f"El entorno virtual '{self.venv_name}' ha sido creado exitosamente.")
            except subprocess.CalledProcessError as e:
                print(f"Ha ocurrido un error al crear el entorno virtual. Detalles del error: {e}")


    # Funcion para activar el entorno virtual
    # Tener en cuenta que la configuracion de la politica de ejecucion de scripts debe  estar en RemoteSigned
    # En caso contrario, debe de entrar a la consola de Windows (cmd) y ejecutar el comando:
    # Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    # Esto cambia la configuracion, pero solo para el usuario actual, lo cual no necesita permisos de admin
    # Se puede desactivar con el comando deactivate en la terminal
    def activate_virtual_environment(self):
        """
        Activa el entorno virtual especificado.

        """
        # Construye el comando para activar el entorno
        activate_command = f"{self.venv_path}\\Scripts\\activate.bat"
        
        # Verifica si el archivo de activación existe
        if os.path.exists(activate_command):
            # Ejecuta el comando en el shell
            os.system(f'cmd /k "{activate_command}"')
        else:
            print("El script de activación no existe. ¿Está seguro de que el entorno virtual está creado?")

    # Funcion para crear el archivo requirements con las librarias instaladas en el directorio
    def create_requirements_file(self, from_venv:bool=True):
        """
        Crea un archivo de requirements con las librerias usadas en el proyecto.
        
        :param from_venv: Indicador booleano, por defecto es igual a True, con lo cual, toma las librerias instaladas en el ambiente virtual especificado.
        """
        
        # Determinar la ruta del ejecutable de Python
        if from_venv:

            # Ubicar el directorio del ambiente virtual
            if os.path.exists(self.venv_path):
                # Ruta dentro del ambiente virtual
                python_executable = os.path.join(self.venv_path, 'bin', 'python') if os.name != 'nt' else os.path.join(self.venv_path, 'Scripts', 'python.exe')
                print('Ambiente virtual encontrado.')
            else:
                raise FileNotFoundError(f'Ambiente virtual no encontrado en {self.venv_path}.')

        else:
            # Usar el Python del sistema
            python_executable = sys.executable
        
        try:
            # Abrir el archivo en el modo de escritura
            with open(self.requirements_path, 'w') as f:
                # Llamar a pip freeze y dirigir la salida al archivo
                subprocess.check_call([python_executable, '-m', 'pip', 'freeze'], stdout=f)
            print(f'Archivo requirements.txt creado en {self.requirements_path}')
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar pip freeze: {e}")
        except Exception as ex:
            print(f"Error al crear el archivo requirements.txt en {self.requirements_path}: {ex}")


    # Funcion para instalar la libreria dada
    def install_library(self,library_name:str|list, on_venv:bool=True, update_requirements:bool=True):
        """
        Instala la librería especificada usando pip. 
        Por defecto se instala en un entorno virtual y se actualiza el archivo requirements.
        
        :param library_name: String o lista de nombre(s) de la librería(s) a instalar
        :param on_venv: Indicador booleano, por defecto es igual a True con lo cual instala la libreria en el entorno virtual.
        :param update_requirements: Indicador booleano, por defecto es igual a True con lo cual actualiza el archivo requirements.
        """

        if isinstance(library_name, str):
            library_name = [library_name]
        elif not isinstance(library_name, list):
            raise ValueError("El parámetro 'libraries' debe ser un string o lista de nombre(s) de librería(s).")

        try:
            if on_venv:
                if not os.path.exists(self.venv_path):
                    self.create_virtual_environment()
                python_executable = os.path.join(self.venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(self.venv_path, 'bin', 'python')
            else:
                python_executable = sys.executable
            
            subprocess.check_call([python_executable, "-m", "pip", "install"] + library_name)
            print(f"{library_name} instalado correctamente en {python_executable}.")

            if update_requirements:
                self.create_requirements_file(from_venv=on_venv)

        except subprocess.CalledProcessError as e:
            print(f"Error al instalar {library_name}. Detalles: {e}")

    def check_outdated_libraries(self, on_venv=True):
        """
        Chequea las librerías desactualizadas usando pip list --outdated.
        
        :param on_venv: Indicador booleano, por defecto True con lo cual revisa en el entorno virtual.
        """
        try:
            if on_venv:
                if not os.path.exists(self.venv_path):
                    raise FileNotFoundError(f'Ambiente virtual no encontrado en {self.venv_path}.')
                python_executable = os.path.join(self.venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(self.venv_path, 'bin', 'python')
            else:
                python_executable = sys.executable
            
            output = subprocess.check_output([python_executable, "-m", "pip", "list", "--outdated"], text=True)
            print("Librerías desactualizadas:\n", output)

        except subprocess.CalledProcessError as e:
            print(f"Error al chequear librerías desactualizadas. Detalles: {e}")

    # Funcion para actualizar la libreria especificada
    def upgrade_library(self,library_name:str|list, on_venv:bool=True, update_requirements:bool=True):
        """
        Actualiza la librería especificada usando pip.
        Por defecto se actualiza en un entorno virtual.

        :param library_name: Nombre de la librería a actualizar.
        :param on_venv: Indicador booleano, por defecto es igual a True con lo cual instala la libreria en el entorno virtual.
        :param update_requirements: Indicador booleano, por defecto es igual a True con lo cual actualiza el archivo requirements.
        """
        if library_name=='all':
            pass
        elif isinstance(library_name, str):
            library_name = [library_name]
        elif not isinstance(library_name, list):
            raise ValueError("El parámetro 'libraries' debe ser un string o lista de nombre(s) de librería(s).")

        try:
            if on_venv:
                if not os.path.exists(self.venv_path):
                    raise FileNotFoundError(f'Ambiente virtual no encontrado en {self.venv_path}.')
                else:
                    python_executable = os.path.join(self.venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(self.venv_path, 'bin', 'python')
            else:
                python_executable = sys.executable
            
            if library_name=='all':
                subprocess.check_call([python_executable, "-m", "pip", "install", "--upgrade", "pip"])
                subprocess.check_call([python_executable, "-m", "pip", "list", "--outdated"], text=True)
                outdated_packages = subprocess.check_output([python_executable, "-m", "pip", "list", "--outdated"], text=True).splitlines()
                for package in outdated_packages:
                    package_name = package.split('==')[0]
                    subprocess.check_call([python_executable, "-m", "pip", "install", "--upgrade", package_name])
                    print(f"{package_name} actualizado correctamente.")
            else:
                subprocess.check_call([python_executable, "-m", "pip", "install", "--upgrade"] + library_name)
                print(f"{library_name} actualizado correctamente en {python_executable}.")

            if update_requirements:
                self.create_requirements_file(from_venv=on_venv)

        except subprocess.CalledProcessError as e:
            print(f"Error al actualizar {library_name}. Detalles: {e}")


    # Funcion para desintalar la libreria dada
    def uninstall_library(self,library_name:str|list, from_venv:bool=True, update_requirements:bool=True):
        """
        Desinstala la librería especificada usando pip.
        Por defecto se desintala en un entorno virtual.
        
        :param library_name: Nombre de la librería a desinstalar.
        :param from_venv: Indicador booleano, por defecto es igual a True con lo cual desinstala la libreria del entorno virtual.
        :param update_requirements: Indicador booleano, por defecto es igual a True con lo cual actualiza el archivo requirements.
        """

        if isinstance(library_name, str):
            library_name = [library_name]
        elif not isinstance(library_name, list):
            raise ValueError("El parámetro 'libraries' debe ser un string o lista de nombre(s) de librería(s).")

        try:
            if from_venv:
                if not os.path.exists(self.venv_path):
                    raise FileNotFoundError(f'Ambiente virtual no encontrado en {self.venv_path}.')
                else:
                    python_executable = os.path.join(self.venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(self.venv_path, 'bin', 'python')
            else:
                python_executable = sys.executable

            subprocess.check_call([python_executable, "-m", "pip", "uninstall", "-y"] + library_name)
            print(f"{library_name} desinstalado correctamente en {python_executable}.")

            if update_requirements:
                self.create_requirements_file(from_venv=from_venv)

        except subprocess.CalledProcessError as e:
            print(f"Error al desinstalar {library_name}. Detalles: {e}")


    # Funcion para revisar e instalar la libreria dada
    def check_installation(self, on_venv: bool = True) -> list[str]:
        """
        Verifica las librerias instaladas.
        Por defecto se verifica la instalación en un entorno virtual.

        :param on_venv: Indicador booleano, por defecto es igual a True con lo cual revisa la libreria del entorno virtual.
        :return: Lista de las librerías instaladas.
        """

        try:
            if on_venv:
                if not os.path.exists(self.venv_path):
                    raise FileNotFoundError(f'Ambiente virtual no encontrado en {self.venv_path}.')
                else:
                    python_executable = os.path.join(self.venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(self.venv_path, 'bin', 'python')
            else:
                python_executable = sys.executable
            
            installed_libraries = subprocess.check_output([python_executable, "-m", "pip", "list"], text=True).splitlines()[2:]

            print("\nLibrerías instaladas:")
            for lib in installed_libraries:
                print(lib)
            print("\n")
            return installed_libraries

        except (ImportError, subprocess.CalledProcessError):
            return []

    def verify_dependencies(self):
        """
        Verifica si todas las dependencias en requirements.txt están instaladas.
        """
        if not os.path.exists(self.requirements_path):
            raise FileNotFoundError(f"No se encontró el archivo {self.requirements_path}.")

        try:
            with open(self.requirements_path, 'r') as req_file:
                required_packages = req_file.read().splitlines()

            installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True).splitlines()
            installed_packages = [pkg.split('==')[0] for pkg in installed_packages]

            missing_packages = [pkg for pkg in required_packages if pkg.split('==')[0] not in installed_packages]

            if missing_packages:
                print("Las siguientes dependencias no están instaladas:")
                for pkg in missing_packages:
                    print(f"  - {pkg}")
                
                return missing_packages
            
            else:
                print("Todas las dependencias están instaladas.")
        except Exception as e:
            print(f"Error al verificar dependencias. Detalles: {e}")

    def update_all_libraries(self, on_venv=True, update_requirements=True):
        """
        Actualiza todas las librerías instaladas a sus versiones más recientes.
        
        :param on_venv: Booleano que indica si se deben actualizar en el entorno virtual.
        :param update_requirements: Booleano que indica si se debe actualizar el archivo requirements.
        """
        try:
            if on_venv:
                if not os.path.exists(self.venv_path):
                    raise FileNotFoundError(f'Ambiente virtual no encontrado en {self.venv_path}.')
                python_executable = os.path.join(self.venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(self.venv_path, 'bin', 'python')
            else:
                python_executable = sys.executable
            
            subprocess.check_call([python_executable, "-m", "pip", "list", "--outdated", "--format=freeze"], text=True)
            outdated_packages = subprocess.check_output([python_executable, "-m", "pip", "list", "--outdated", "--format=freeze"], text=True).splitlines()
            for package in outdated_packages:
                package_name = package.split('==')[0]
                subprocess.check_call([python_executable, "-m", "pip", "install", "--upgrade", package_name])
                print(f"{package_name} actualizado correctamente.")

            if update_requirements:
                self.create_requirements_file(from_venv=on_venv)

        except subprocess.CalledProcessError as e:
            print(f"Error al actualizar las librerías. Detalles: {e}")


    # Funcion para instalar las librarias especificadas en el archivo requirements
    def install_requirements(self, on_venv:bool=True):
        """
        Instala las librerias especificadas en el archivo requirements que se encuentre en el directorio especificado.
        Por defecto se instalan en el entorno virtual del mismo directorio.
        
        :param on_venv: Indicador booleano, por defecto es igual a True con lo cual instala las librerias en el entorno virtual.
        """

        # Determinar la ruta del ejecutable de Python
        if on_venv:
            # Evalua la existencia del ambiente virtual o lo crea
            if not os.path.exists(self.venv_path):
                # Creacion de un ambiente virtual
                self.create_virtual_environment()
                print('Ambiente virtual no encontrado. Se ha creado un ambiente virtual.')

            else:
                print('Ambiente virtual encontrado.')
            
            # Ruta dentro del ambiente virtual
            python_executable = os.path.join(self.venv_path, 'bin', 'python') if os.name != 'nt' else os.path.join(self.venv_path, 'Scripts', 'python.exe')
            
        else:
            # Usar el Python del sistema
            python_executable = sys.executable
            print("Las dependencias se instalarán en el intérprete de Python del sistema.")

        if os.path.exists(self.requirements_path):
            try:
                subprocess.check_call([python_executable, '-m', 'pip', 'install', '-r', self.requirements_path])
                print("Las dependencias se han instalado correctamente.")
            except subprocess.CalledProcessError as e:
                print("Ha ocurrido un error al instalar las dependencias. Detalles del error:", e)
        else:
            print("El archivo requirements.txt no se encuentra en el directorio especificado.")

    # Funcion para crear archivo .bat que ejecute el script, este puede ayudar a automatizar su ejecucion usando el programador de tareas de windows
    def create_bat_file(self, script_name:str=None, bat_file_name:str=None, on_venv:bool=True):
        """
        Crea un archivo .bat que asiste en la ejecucion del script.
        Por defecto se usa el entorno virtual para la ejecucion del script.
        
        :param script_name: Nombre del script que se quiere ejecutar
        :param bat_file_name: Nombre que se asigna al archivo .bat
        :param on_venv: Indicador booleano, por defecto es igual a True con lo cual utiliza el interprete del entorno virtual.
        """

        if not self.script_name or not self.bat_file_name:
            raise ValueError("Cuando 'bat_file=True', es necesario especificar 'script_name' y 'bat_file_name'.")

        # Ruta completa al script
        script_path = script_name if self.directory is None else os.path.join(self.directory, script_name)

        # Nombre del archivo .bat
        bat_file_name = os.path.basename(script_path) if bat_file_name is None else bat_file_name
        bat_file_name = os.path.splitext(bat_file_name)[0] + '.bat'
        
        # Verificar si el entorno virtual existe
        if on_venv:
            if not os.path.exists(self.venv_path):
                self.create_virtual_environment()

            python_executable = os.path.join(self.venv_path, 'bin', 'python') if os.name != 'nt' else os.path.join(self.venv_path, 'Scripts', 'python.exe')
            print('Se usará el ambiente virtual.')

        else:
            # Usar el intérprete de Python del sistema
            python_executable = sys.executable
            print("Se usará el intérprete de Python del sistema.")
        
        # Línea de comando para ejecutar el script
        linea_comando = f'"{os.path.abspath(python_executable)}" "{os.path.abspath(script_path)}"'

        # Crear el archivo .bat
        with open(bat_file_name, 'w') as archivo_bat:
            archivo_bat.write(linea_comando)
        
        print(f'Archivo {bat_file_name} creado con éxito.')



#---------------------------------------------------------------------------------------


# Obtener la ruta del directorio del archivo de script actual
script_dir = os.path.dirname(os.path.abspath(__file__))

# Establece el directorio de trabajo de donde se encuentra el script
sys.path.append(script_dir)
os.chdir(script_dir)

# Uso del objeto Project
project = Project(directory=script_dir, venv_name="venv", requirements_name='requirements.txt')

# Llama a las funciones según sea necesario

# NUEVO PROYECTO
#project.create_default_gitignore()
#project.create_virtual_environment()
#project.activate_virtual_environment()
#project.install_library(['pandas','numpy'], on_venv=True, update_requirements=True)
#project.uninstall_library('pandas', from_venv=True, update_requirements=True)

# MANTENIMIENTO DE PROYECTO
#project.check_outdated_libraries(on_venv=True)
#project.check_installation(on_venv=True)
#project.upgrade_library('all', on_venv=True, update_requirements=True)
#project.update_all_libraries(on_venv=True, update_requirements=True)
#project.verify_dependencies()

# PROYECTO TERMINADO
#project.create_requirements_file(from_venv=True)
#project.create_bat_file(script_name='script.py', bat_file_name='script.bat', on_venv=True)

# CLONAR PROYECTO
#project.install_requirements(on_venv=True)