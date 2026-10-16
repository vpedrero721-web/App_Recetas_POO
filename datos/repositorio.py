from __future__ import annotations

import sqlite3
from decimal import Decimal
from pathlib import Path

from datos.Recetas import RECETAS_CHILENAS
from datos.models import (
    Categoria,
    DetalleIngrediente,
    Ingrediente,
    Receta,
    Usuario,
)


class RepositorioRecetas:
    """Repositorio con persistencia en SQLite para que las recetas queden guardadas."""

    def __init__(self) -> None:
        self.db_path = Path(__file__).resolve().parents[1] / "database" / "test.bd"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.usuarios: dict[int, Usuario] = {}
        self.categorias: dict[int, Categoria] = {}
        self.ingredientes: dict[int, Ingrediente] = {}
        self.recetas: dict[int, Receta] = {}

        self._proximo_id_usuario = 1
        self._proximo_id_categoria = 1
        self._proximo_id_ingrediente = 1
        self._proximo_id_receta = 1

        self._inicializar_bd()
        self._cargar_desde_bd()
        if not self.recetas:
            self._cargar_datos_demo()

    def _conexion(self) -> sqlite3.Connection:
        conexion = sqlite3.connect(self.db_path)
        conexion.row_factory = sqlite3.Row
        return conexion

    def _inicializar_bd(self) -> None:
        if self.db_path.exists():
            try:
                with sqlite3.connect(self.db_path) as conexion:
                    conexion.execute("SELECT 1")
            except sqlite3.DatabaseError:
                self.db_path.write_bytes(b"")

        with self._conexion() as conexion:
            conexion.executescript(
                """
                CREATE TABLE IF NOT EXISTS Usuarios (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS Categorias (
                    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    descripcion TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS Recetas (
                    id_receta INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    tiempo_preparacion INTEGER NOT NULL,
                    dificultad TEXT NOT NULL,
                    instrucciones TEXT NOT NULL,
                    porciones INTEGER NOT NULL,
                    imagen_url TEXT,
                    id_usuario INTEGER NOT NULL,
                    FOREIGN KEY(id_usuario) REFERENCES Usuarios(id_usuario)
                );

                CREATE TABLE IF NOT EXISTS Ingredientes (
                    id_ingrediente INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    categoria_ingrediente TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS DetalleIngrediente (
                    id_receta INTEGER NOT NULL,
                    id_ingrediente INTEGER NOT NULL,
                    cantidad TEXT NOT NULL,
                    unidad_medida TEXT NOT NULL,
                    PRIMARY KEY (id_receta, id_ingrediente),
                    FOREIGN KEY(id_receta) REFERENCES Recetas(id_receta),
                    FOREIGN KEY(id_ingrediente) REFERENCES Ingredientes(id_ingrediente)
                );

                CREATE TABLE IF NOT EXISTS RecetasCategorias (
                    id_receta INTEGER NOT NULL,
                    id_categoria INTEGER NOT NULL,
                    PRIMARY KEY (id_receta, id_categoria),
                    FOREIGN KEY(id_receta) REFERENCES Recetas(id_receta),
                    FOREIGN KEY(id_categoria) REFERENCES Categorias(id_categoria)
                );
                """
            )

    def _cargar_desde_bd(self) -> None:
        self.usuarios.clear()
        self.categorias.clear()
        self.ingredientes.clear()
        self.recetas.clear()

        with self._conexion() as conexion:
            for fila in conexion.execute("SELECT id_usuario, nombre, email FROM Usuarios ORDER BY id_usuario"):
                usuario = Usuario(
                    id_usuario=fila["id_usuario"],
                    nombre=fila["nombre"],
                    email=fila["email"],
                )
                self.usuarios[usuario.id_usuario] = usuario

            for fila in conexion.execute("SELECT id_categoria, nombre, descripcion FROM Categorias ORDER BY id_categoria"):
                categoria = Categoria(
                    id_categoria=fila["id_categoria"],
                    nombre=fila["nombre"],
                    descripcion=fila["descripcion"],
                )
                self.categorias[categoria.id_categoria] = categoria

            for fila in conexion.execute("SELECT id_ingrediente, nombre, categoria_ingrediente FROM Ingredientes ORDER BY id_ingrediente"):
                ingrediente = Ingrediente(
                    id_ingrediente=fila["id_ingrediente"],
                    nombre=fila["nombre"],
                    categoria_ingrediente=fila["categoria_ingrediente"],
                )
                self.ingredientes[ingrediente.id_ingrediente] = ingrediente

            for fila in conexion.execute(
                """
                SELECT r.id_receta, r.nombre, r.descripcion, r.tiempo_preparacion, r.dificultad,
                       r.instrucciones, r.porciones, r.imagen_url, r.id_usuario
                FROM Recetas r
                ORDER BY r.id_receta
                """
            ):
                receta = Receta(
                    id_receta=fila["id_receta"],
                    nombre=fila["nombre"],
                    descripcion=fila["descripcion"],
                    tiempo_preparacion=int(fila["tiempo_preparacion"]),
                    dificultad=fila["dificultad"],
                    instrucciones=fila["instrucciones"],
                    porciones=int(fila["porciones"]),
                    imagen_url=fila["imagen_url"],
                    id_usuario=fila["id_usuario"],
                    autor=self.usuarios.get(fila["id_usuario"]),
                    categorias=[],
                    ingredientes=[],
                )

                for categoria_fila in conexion.execute(
                    """
                    SELECT c.id_categoria, c.nombre, c.descripcion
                    FROM RecetasCategorias rc
                    JOIN Categorias c ON c.id_categoria = rc.id_categoria
                    WHERE rc.id_receta = ?
                    ORDER BY c.id_categoria
                    """,
                    (receta.id_receta,),
                ):
                    receta.categorias.append(
                        Categoria(
                            id_categoria=categoria_fila["id_categoria"],
                            nombre=categoria_fila["nombre"],
                            descripcion=categoria_fila["descripcion"],
                        )
                    )

                for detalle_fila in conexion.execute(
                    """
                    SELECT di.id_receta, di.id_ingrediente, di.cantidad, di.unidad_medida,
                           i.nombre, i.categoria_ingrediente
                    FROM DetalleIngrediente di
                    JOIN Ingredientes i ON i.id_ingrediente = di.id_ingrediente
                    WHERE di.id_receta = ?
                    ORDER BY di.id_ingrediente
                    """,
                    (receta.id_receta,),
                ):
                    ingrediente = self.ingredientes.get(detalle_fila["id_ingrediente"])
                    if ingrediente is None:
                        ingrediente = Ingrediente(
                            id_ingrediente=detalle_fila["id_ingrediente"],
                            nombre=detalle_fila["nombre"],
                            categoria_ingrediente=detalle_fila["categoria_ingrediente"],
                        )
                        self.ingredientes[ingrediente.id_ingrediente] = ingrediente
                    receta.ingredientes.append(
                        DetalleIngrediente(
                            id_receta=detalle_fila["id_receta"],
                            id_ingrediente=detalle_fila["id_ingrediente"],
                            ingrediente=ingrediente,
                            cantidad=Decimal(str(detalle_fila["cantidad"])),
                            unidad_medida=detalle_fila["unidad_medida"],
                        )
                    )

                self.recetas[receta.id_receta] = receta

        self._proximo_id_usuario = max(self.usuarios.keys(), default=0) + 1
        self._proximo_id_categoria = max(self.categorias.keys(), default=0) + 1
        self._proximo_id_ingrediente = max(self.ingredientes.keys(), default=0) + 1
        self._proximo_id_receta = max(self.recetas.keys(), default=0) + 1

    def _sincronizar_relaciones_receta(self, receta: Receta) -> None:
        with self._conexion() as conexion:
            conexion.execute("DELETE FROM DetalleIngrediente WHERE id_receta = ?", (receta.id_receta,))
            conexion.execute("DELETE FROM RecetasCategorias WHERE id_receta = ?", (receta.id_receta,))

            for detalle in receta.ingredientes:
                ingrediente = detalle.ingrediente
                if ingrediente is not None:
                    nombre = ingrediente.nombre.strip()
                    fila = conexion.execute(
                        "SELECT id_ingrediente FROM Ingredientes WHERE LOWER(nombre) = LOWER(?)",
                        (nombre,),
                    ).fetchone()
                    if fila is None:
                        cursor = conexion.execute(
                            "INSERT INTO Ingredientes (nombre, categoria_ingrediente) VALUES (?, ?)",
                            (nombre, ingrediente.categoria_ingrediente),
                        )
                        ingrediente.id_ingrediente = cursor.lastrowid
                    else:
                        ingrediente.id_ingrediente = int(fila["id_ingrediente"])
                    self.ingredientes[ingrediente.id_ingrediente] = ingrediente
                id_ingrediente = detalle.ingrediente.id_ingrediente if detalle.ingrediente is not None else None
                if id_ingrediente is None:
                    continue
                conexion.execute(
                    "INSERT INTO DetalleIngrediente (id_receta, id_ingrediente, cantidad, unidad_medida) VALUES (?, ?, ?, ?)",
                    (receta.id_receta, id_ingrediente, str(detalle.cantidad), detalle.unidad_medida),
                )

            for categoria in receta.categorias:
                nombre = categoria.nombre.strip()
                fila = conexion.execute(
                    "SELECT id_categoria FROM Categorias WHERE LOWER(nombre) = LOWER(?)",
                    (nombre,),
                ).fetchone()
                if fila is None:
                    cursor = conexion.execute(
                        "INSERT INTO Categorias (nombre, descripcion) VALUES (?, ?)",
                        (nombre, categoria.descripcion),
                    )
                    categoria.id_categoria = cursor.lastrowid
                else:
                    categoria.id_categoria = int(fila["id_categoria"])
                self.categorias[categoria.id_categoria] = categoria
                conexion.execute(
                    "INSERT OR IGNORE INTO RecetasCategorias (id_receta, id_categoria) VALUES (?, ?)",
                    (receta.id_receta, categoria.id_categoria),
                )

    def agregar_usuario(self, usuario: Usuario) -> Usuario:
        if usuario.id_usuario is None:
            with self._conexion() as conexion:
                cursor = conexion.execute(
                    "INSERT INTO Usuarios (nombre, email) VALUES (?, ?)",
                    (usuario.nombre, usuario.email),
                )
                usuario.id_usuario = cursor.lastrowid
        else:
            with self._conexion() as conexion:
                conexion.execute(
                    "INSERT OR REPLACE INTO Usuarios (id_usuario, nombre, email) VALUES (?, ?, ?)",
                    (usuario.id_usuario, usuario.nombre, usuario.email),
                )
        self.usuarios[usuario.id_usuario] = usuario
        self._proximo_id_usuario = max(self._proximo_id_usuario, usuario.id_usuario + 1)
        return usuario

    def obtener_usuario(self, id_usuario: int) -> Usuario | None:
        return self.usuarios.get(id_usuario)

    def listar_usuarios(self) -> list[Usuario]:
        return list(self.usuarios.values())

    def agregar_categoria(self, categoria: Categoria) -> Categoria:
        if categoria.id_categoria is None:
            with self._conexion() as conexion:
                cursor = conexion.execute(
                    "INSERT INTO Categorias (nombre, descripcion) VALUES (?, ?)",
                    (categoria.nombre, categoria.descripcion),
                )
                categoria.id_categoria = cursor.lastrowid
        else:
            with self._conexion() as conexion:
                conexion.execute(
                    "INSERT OR REPLACE INTO Categorias (id_categoria, nombre, descripcion) VALUES (?, ?, ?)",
                    (categoria.id_categoria, categoria.nombre, categoria.descripcion),
                )
        self.categorias[categoria.id_categoria] = categoria
        self._proximo_id_categoria = max(self._proximo_id_categoria, categoria.id_categoria + 1)
        return categoria

    def obtener_categoria(self, id_categoria: int) -> Categoria | None:
        return self.categorias.get(id_categoria)

    def listar_categorias(self) -> list[Categoria]:
        return list(self.categorias.values())

    def agregar_ingrediente(self, ingrediente: Ingrediente) -> Ingrediente:
        if ingrediente.nombre.strip() == "":
            raise ValueError("El nombre del ingrediente es obligatorio.")

        with self._conexion() as conexion:
            fila = conexion.execute(
                "SELECT id_ingrediente FROM Ingredientes WHERE LOWER(nombre) = LOWER(?)",
                (ingrediente.nombre.strip(),),
            ).fetchone()
            if fila is not None:
                ingrediente.id_ingrediente = int(fila["id_ingrediente"])
                ingrediente.nombre = ingrediente.nombre.strip()
                self.ingredientes[ingrediente.id_ingrediente] = ingrediente
                return ingrediente

        if ingrediente.id_ingrediente is None:
            with self._conexion() as conexion:
                cursor = conexion.execute(
                    "INSERT INTO Ingredientes (nombre, categoria_ingrediente) VALUES (?, ?)",
                    (ingrediente.nombre.strip(), ingrediente.categoria_ingrediente),
                )
                ingrediente.id_ingrediente = cursor.lastrowid
        else:
            with self._conexion() as conexion:
                conexion.execute(
                    "INSERT OR REPLACE INTO Ingredientes (id_ingrediente, nombre, categoria_ingrediente) VALUES (?, ?, ?)",
                    (ingrediente.id_ingrediente, ingrediente.nombre.strip(), ingrediente.categoria_ingrediente),
                )
        self.ingredientes[ingrediente.id_ingrediente] = ingrediente
        self._proximo_id_ingrediente = max(self._proximo_id_ingrediente, ingrediente.id_ingrediente + 1)
        return ingrediente

    def obtener_ingrediente(self, id_ingrediente: int) -> Ingrediente | None:
        return self.ingredientes.get(id_ingrediente)

    def listar_ingredientes(self) -> list[Ingrediente]:
        return list(self.ingredientes.values())

    def agregar_receta(self, receta: Receta) -> Receta:
        if receta.autor is not None and receta.autor.id_usuario is None:
            self.agregar_usuario(receta.autor)

        if receta.id_usuario is not None and receta.autor is None:
            usuario = self.obtener_usuario(receta.id_usuario)
            if usuario is not None:
                receta.autor = usuario

        if receta.id_receta is None:
            with self._conexion() as conexion:
                cursor = conexion.execute(
                    """
                    INSERT INTO Recetas (nombre, descripcion, tiempo_preparacion, dificultad, instrucciones, porciones, imagen_url, id_usuario)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        receta.nombre.strip(),
                        receta.descripcion.strip(),
                        int(receta.tiempo_preparacion),
                        receta.dificultad,
                        receta.instrucciones,
                        int(receta.porciones),
                        receta.imagen_url,
                        receta.id_usuario or (receta.autor.id_usuario if receta.autor else 1),
                    ),
                )
                receta.id_receta = cursor.lastrowid
        else:
            with self._conexion() as conexion:
                conexion.execute(
                    """
                    UPDATE Recetas
                    SET nombre = ?, descripcion = ?, tiempo_preparacion = ?, dificultad = ?, instrucciones = ?, porciones = ?, imagen_url = ?, id_usuario = ?
                    WHERE id_receta = ?
                    """,
                    (
                        receta.nombre.strip(),
                        receta.descripcion.strip(),
                        int(receta.tiempo_preparacion),
                        receta.dificultad,
                        receta.instrucciones,
                        int(receta.porciones),
                        receta.imagen_url,
                        receta.id_usuario or (receta.autor.id_usuario if receta.autor else 1),
                        receta.id_receta,
                    ),
                )

        self.recetas[receta.id_receta] = receta
        self._sincronizar_relaciones_receta(receta)
        self._proximo_id_receta = max(self._proximo_id_receta, receta.id_receta + 1)
        return receta

    def obtener_receta(self, id_receta: int) -> Receta | None:
        return self.recetas.get(id_receta)

    def listar_recetas(self) -> list[Receta]:
        return list(self.recetas.values())

    def buscar_recetas_por_nombre(self, nombre: str) -> list[Receta]:
        texto = nombre.strip().lower()
        if not texto:
            return self.listar_recetas()
        return [
            receta
            for receta in self.recetas.values()
            if texto in receta.nombre.lower() or texto in receta.descripcion.lower()
        ]

    def buscar_recetas_por_categoria(self, nombre_categoria: str) -> list[Receta]:
        texto = nombre_categoria.strip().lower()
        if not texto:
            return self.listar_recetas()

        resultados: list[Receta] = []
        for receta in self.recetas.values():
            for categoria in receta.categorias:
                if texto in categoria.nombre.lower():
                    resultados.append(receta)
                    break
        return resultados

    def editar_receta(self, id_receta: int, receta_nueva: Receta) -> Receta:
        if id_receta not in self.recetas:
            raise ValueError(f"La receta con id {id_receta} no existe.")

        receta_nueva.id_receta = id_receta
        if receta_nueva.autor is not None and receta_nueva.autor.id_usuario is None:
            self.agregar_usuario(receta_nueva.autor)
        self.recetas[id_receta] = receta_nueva
        self.agregar_receta(receta_nueva)
        return receta_nueva

    def eliminar_receta(self, id_receta: int) -> bool:
        if id_receta not in self.recetas:
            return False
        with self._conexion() as conexion:
            conexion.execute("DELETE FROM DetalleIngrediente WHERE id_receta = ?", (id_receta,))
            conexion.execute("DELETE FROM RecetasCategorias WHERE id_receta = ?", (id_receta,))
            conexion.execute("DELETE FROM Recetas WHERE id_receta = ?", (id_receta,))
        self.recetas.pop(id_receta, None)
        return True

    def agregar_ingrediente_a_receta(
        self,
        id_receta: int,
        ingrediente: Ingrediente,
        cantidad: Decimal | int | float,
        unidad_medida: str,
    ) -> DetalleIngrediente:
        receta = self.obtener_receta(id_receta)
        if receta is None:
            raise ValueError(f"La receta con id {id_receta} no existe.")

        ingrediente_guardado = self.obtener_ingrediente(ingrediente.id_ingrediente) if ingrediente.id_ingrediente is not None else None
        if ingrediente_guardado is None:
            ingrediente_guardado = self.agregar_ingrediente(ingrediente)

        detalle = DetalleIngrediente(
            id_receta=id_receta,
            id_ingrediente=ingrediente_guardado.id_ingrediente,
            ingrediente=ingrediente_guardado,
            cantidad=Decimal(str(cantidad)),
            unidad_medida=unidad_medida,
        )
        receta.ingredientes.append(detalle)
        with self._conexion() as conexion:
            conexion.execute(
                "INSERT OR REPLACE INTO DetalleIngrediente (id_receta, id_ingrediente, cantidad, unidad_medida) VALUES (?, ?, ?, ?)",
                (id_receta, ingrediente_guardado.id_ingrediente, str(detalle.cantidad), unidad_medida),
            )
        return detalle

    def _cargar_datos_demo(self) -> None:
        usuario1 = self.agregar_usuario(Usuario(id_usuario=None, nombre="Antonia", email="antonia@gmail.com"))
        self.agregar_usuario(Usuario(id_usuario=None, nombre="Joaquín", email="joaquin@gmail.com"))

        for receta_data in RECETAS_CHILENAS:
            categorias = []
            if receta_data.get("tipo"):
                categorias.append(
                    Categoria(
                        id_categoria=None,
                        nombre=receta_data["tipo"],
                        descripcion="Receta chilena recomendada para cocinar en casa.",
                    )
                )
            receta = Receta(
                id_receta=None,
                nombre=receta_data["nombre"],
                descripcion=receta_data["descripcion"],
                tiempo_preparacion=int(receta_data["tiempo_preparacion"]),
                dificultad=receta_data["dificultad"],
                instrucciones="\n".join(receta_data["instrucciones"]),
                porciones=int(receta_data["porciones"]),
                imagen_url=None,
                id_usuario=usuario1.id_usuario,
                autor=usuario1,
                categorias=categorias,
            )

            for ingrediente_data in receta_data["ingredientes"]:
                ingrediente = self.obtener_ingrediente_by_name(ingrediente_data.strip())
                if ingrediente is None:
                    ingrediente = self.agregar_ingrediente(
                        Ingrediente(
                            id_ingrediente=None,
                            nombre=ingrediente_data.strip(),
                            categoria_ingrediente="General",
                        )
                    )

                receta.ingredientes.append(
                    DetalleIngrediente(
                        id_receta=None,
                        id_ingrediente=ingrediente.id_ingrediente,
                        ingrediente=ingrediente,
                        cantidad=Decimal("1"),
                        unidad_medida="unidad",
                    )
                )

            self.agregar_receta(receta)

    def obtener_ingrediente_by_name(self, nombre: str) -> Ingrediente | None:
        texto = nombre.strip().lower()
        for ingrediente in self.ingredientes.values():
            if ingrediente.nombre.lower() == texto:
                return ingrediente
        return None


__all__ = ["RepositorioRecetas"]
