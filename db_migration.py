import sqlite3
import os
from datetime import datetime

class DatabaseMigration:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        # Crear backup antes de cualquier migración
        self._create_backup()
        
    def _create_backup(self):
        """Crear una copia de seguridad de la base de datos"""
        if os.path.exists(self.db_name):
            backup_name = f"backup_{self.db_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(self.db_name, 'rb') as source:
                with open(backup_name, 'wb') as target:
                    target.write(source.read())
            print(f"Backup creado: {backup_name}")

    def _execute_query(self, query, params=None):
        """Ejecutar una consulta SQL con manejo de errores"""
        try:
            with sqlite3.connect(self.db_name) as conexion:
                cursor = conexion.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error en la consulta SQL: {e}")
            return False

    def agregar_campo(self, tabla, nombre_campo, tipo_campo, default=None):
        """
        Agregar un nuevo campo a una tabla existente
        Ejemplo: migration.agregar_campo('usuarios', 'edad', 'INTEGER', '18')
        """
        query = f"ALTER TABLE {tabla} ADD COLUMN {nombre_campo} {tipo_campo}"
        if default is not None:
            query += f" DEFAULT {default}"
        
        if self._execute_query(query):
            print(f"Campo '{nombre_campo}' agregado exitosamente a la tabla '{tabla}'")
        else:
            print("No se pudo agregar el campo")

    def crear_tabla(self, nombre_tabla, campos):
        """
        Crear una nueva tabla
        Ejemplo: 
        campos = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
            "nombre TEXT NOT NULL",
            "fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP"
        ]
        migration.crear_tabla('nueva_tabla', campos)
        """
        campos_str = ", ".join(campos)
        query = f"CREATE TABLE IF NOT EXISTS {nombre_tabla} ({campos_str})"
        
        if self._execute_query(query):
            print(f"Tabla '{nombre_tabla}' creada exitosamente")
        else:
            print("No se pudo crear la tabla")

    def eliminar_tabla(self, nombre_tabla):
        """Eliminar una tabla existente"""
        query = f"DROP TABLE IF EXISTS {nombre_tabla}"
        
        if self._execute_query(query):
            print(f"Tabla '{nombre_tabla}' eliminada exitosamente")
        else:
            print("No se pudo eliminar la tabla")

    def renombrar_tabla(self, nombre_viejo, nombre_nuevo):
        """Renombrar una tabla existente"""
        query = f"ALTER TABLE {nombre_viejo} RENAME TO {nombre_nuevo}"
        
        if self._execute_query(query):
            print(f"Tabla renombrada de '{nombre_viejo}' a '{nombre_nuevo}'")
        else:
            print("No se pudo renombrar la tabla")

    def mostrar_estructura(self, nombre_tabla):
        """Mostrar la estructura de una tabla"""
        try:
            with sqlite3.connect(self.db_name) as conexion:
                cursor = conexion.cursor()
                cursor.execute(f"PRAGMA table_info({nombre_tabla})")
                estructura = cursor.fetchall()
                
                print(f"\nEstructura de la tabla '{nombre_tabla}':")
                print("ID | Nombre | Tipo | NotNull | Default | PK")
                print("-" * 50)
                for col in estructura:
                    print(f"{col[0]} | {col[1]} | {col[2]} | {col[3]} | {col[4]} | {col[5]}")
        except sqlite3.Error as e:
            print(f"Error al obtener la estructura: {e}")

    def verificar_tabla(self, nombre_tabla):
        """Verificar si una tabla existe"""
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        
        try:
            with sqlite3.connect(self.db_name) as conexion:
                cursor = conexion.cursor()
                cursor.execute(query, (nombre_tabla,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Error al verificar la tabla: {e}")
            return False

# Ejemplo de uso
if __name__ == "__main__":
    # Crear una instancia de la clase de migración
    migration = DatabaseMigration()
    
    # Ejemplo 1: Agregar un nuevo campo a la tabla usuarios
    # migration.agregar_campo('usuarios', 'fecha_registro', 'DATETIME', 'CURRENT_TIMESTAMP')
    
    # Ejemplo 2: Crear una nueva tabla para perfiles
    # campos_perfil = [
    #     "id INTEGER PRIMARY KEY AUTOINCREMENT",
    #     "usuario_id INTEGER",
    #     "telefono TEXT",
    #     "direccion TEXT",
    #     "fecha_nacimiento DATE",
    #     "FOREIGN KEY (usuario_id) REFERENCES usuarios(id)"
    # ]
    # migration.crear_tabla('perfiles', campos_perfil)
    
    # Ejemplo 3: Mostrar la estructura de la tabla usuarios
    # migration.mostrar_estructura('usuarios')
    
    print("\nPara usar este script:")
    print("1. Descomenta las líneas de ejemplo que quieras ejecutar")
    print("2. Modifica los parámetros según tus necesidades")
    print("3. Ejecuta el script con: python db_migration.py")