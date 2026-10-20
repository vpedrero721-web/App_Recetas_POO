# App_Recetas_POO
Proyecto Modular de POO

Aplicación modular de recetas con persistencia en MySQL/MariaDB mediante Peewee.

## Instalación

Desde la carpeta del proyecto, instala las dependencias:

```powershell
python -m pip install -r requirements.txt
```

Importa `datos/SQL/recetas.sql` en MySQL/MariaDB para crear la base `recetas` y
sus tablas. El script vuelve a crear las tablas y elimina sus datos si se
ejecuta nuevamente.

## Estructura del proyecto

- `datos/`: modelos, repositorio, conexión, auxiliares y scripts SQL.
- `negocio/`: reglas y operaciones de negocio para las recetas.
- `presentacion/`: menú de consola y aplicación web.
- `main.py`: punto de entrada para iniciar el menú de consola.
- `Diagrama_UML.md`: diagrama de clases y relaciones principales.

## Conexión a la base de datos

La aplicación lee las variables de conexión desde un archivo `.env` local o
desde el entorno del sistema. Copia `.env.example` como `.env` y completa los
valores de tu equipo. El archivo `.env` está excluido de Git: no subas
contraseñas ni credenciales a GitHub.

En PowerShell:

```powershell
Copy-Item .env.example .env
notepad .env
python main.py
```

Si prefieres, configura las variables `RECETAS_DB_HOST`, `RECETAS_DB_PORT`,
`RECETAS_DB_USER`, `RECETAS_DB_PASSWORD` y `RECETAS_DB_NAME` directamente en
PowerShell. Las clases ORM que representan las tablas están en
`datos/orm_models.py`; el repositorio usa Peewee para leer y guardar recetas,
ingredientes y categorías.

## Generar modelos con pwiz

Peewee incluye `pwiz` para generar un borrador de modelos a partir de la base
existente. Desde PowerShell, por ejemplo:

```powershell
python -m pwiz -e mysql -H 127.0.0.1 -p 3307 -u tu_usuario -P recetas > datos\modelos_generados.py
```

`-P` solicita la contraseña de forma interactiva. El archivo generado es una
referencia: revisa los nombres y relaciones antes de usarlo; la aplicación usa
los modelos mantenidos en `datos/orm_models.py`.
