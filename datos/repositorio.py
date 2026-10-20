from __future__ import annotations

from decimal import Decimal

from peewee import fn

from datos.Recetas import RECETAS_CHILENAS
from datos.models import (
    Categoria,
    DetalleIngrediente,
    Ingrediente,
    Receta,
    Usuario,
)
from datos.orm_models import (
    CategoriaORM,
    DetalleIngredienteORM,
    IngredienteORM,
    RecetaCategoriaORM,
    RecetaORM,
    UsuarioORM,
    database,
)


class RepositorioRecetas:
    """Repositorio con persistencia Peewee en MariaDB/MySQL."""

    def __init__(self) -> None:
        self.usuarios: dict[int, Usuario] = {}
        self.categorias: dict[int, Categoria] = {}
        self.ingredientes: dict[int, Ingrediente] = {}
        self.recetas: dict[int, Receta] = {}

        self._inicializar_bd()
        self._cargar_desde_bd()
        if not self.recetas:
            self._cargar_datos_demo()

    def _inicializar_bd(self) -> None:
        with database.connection_context():
            tablas_requeridas = {
                "usuarios",
                "categorias",
                "recetas",
                "ingredientes",
                "detalleingrediente",
                "recetascategorias",
            }
            tablas_disponibles = {nombre.lower() for nombre in database.get_tables()}
            faltantes = tablas_requeridas - tablas_disponibles
            if faltantes:
                nombres = ", ".join(sorted(faltantes))
                nombre_bd = database.database
                raise RuntimeError(
                    f"Faltan tablas en la base '{nombre_bd}': {nombres}. "
                    "Importa datos/SQL/recetas.sql en phpMyAdmin."
                )

    @staticmethod
    def _convertir_usuario(fila: UsuarioORM) -> Usuario:
        return Usuario(
            id_usuario=fila.id_usuario,
            nombre=fila.nombre,
            email=fila.email,
        )

    @staticmethod
    def _convertir_categoria(fila: CategoriaORM) -> Categoria:
        return Categoria(
            id_categoria=fila.id_categoria,
            nombre=fila.nombre,
            descripcion=fila.descripcion,
        )

    @staticmethod
    def _convertir_ingrediente(fila: IngredienteORM) -> Ingrediente:
        return Ingrediente(
            id_ingrediente=fila.id_ingrediente,
            nombre=fila.nombre,
            categoria_ingrediente=fila.categoria_ingrediente,
        )

    def _cargar_desde_bd(self) -> None:
        self.usuarios.clear()
        self.categorias.clear()
        self.ingredientes.clear()
        self.recetas.clear()

        with database.connection_context():
            for fila in UsuarioORM.select().order_by(UsuarioORM.id_usuario):
                usuario = self._convertir_usuario(fila)
                self.usuarios[usuario.id_usuario] = usuario

            for fila in CategoriaORM.select().order_by(CategoriaORM.id_categoria):
                categoria = self._convertir_categoria(fila)
                self.categorias[categoria.id_categoria] = categoria

            for fila in IngredienteORM.select().order_by(IngredienteORM.id_ingrediente):
                ingrediente = self._convertir_ingrediente(fila)
                self.ingredientes[ingrediente.id_ingrediente] = ingrediente

            for fila in RecetaORM.select().order_by(RecetaORM.id_receta):
                autor = self.usuarios.get(fila.usuario)
                receta = Receta(
                    id_receta=fila.id_receta,
                    nombre=fila.nombre,
                    descripcion=fila.descripcion,
                    tiempo_preparacion=int(fila.tiempo_preparacion),
                    dificultad=fila.dificultad,
                    instrucciones=fila.instrucciones,
                    porciones=int(fila.porciones),
                    imagen_url=fila.imagen_url,
                    id_usuario=fila.usuario,
                    autor=autor,
                )

                relaciones = (
                    RecetaCategoriaORM.select()
                    .where(RecetaCategoriaORM.receta == receta.id_receta)
                    .order_by(RecetaCategoriaORM.categoria)
                )
                for relacion in relaciones:
                    categoria = self.categorias.get(relacion.categoria)
                    if categoria is not None:
                        receta.categorias.append(categoria)

                detalles = (
                    DetalleIngredienteORM.select()
                    .where(DetalleIngredienteORM.receta == receta.id_receta)
                    .order_by(DetalleIngredienteORM.ingrediente)
                )
                for detalle in detalles:
                    ingrediente = self.ingredientes.get(detalle.ingrediente)
                    if ingrediente is not None:
                        receta.ingredientes.append(
                            DetalleIngrediente(
                                id_receta=detalle.receta,
                                id_ingrediente=detalle.ingrediente,
                                ingrediente=ingrediente,
                                cantidad=Decimal(str(detalle.cantidad)),
                                unidad_medida=detalle.unidad_medida,
                            )
                        )
                self.recetas[receta.id_receta] = receta

    def _guardar_usuario(self, usuario: Usuario) -> Usuario:
        valores = {"nombre": usuario.nombre, "email": usuario.email}
        if usuario.id_usuario is None:
            fila = UsuarioORM.create(**valores)
            usuario.id_usuario = fila.id_usuario
        else:
            existente = UsuarioORM.get_or_none(
                UsuarioORM.id_usuario == usuario.id_usuario
            )
            if existente is None:
                UsuarioORM.create(id_usuario=usuario.id_usuario, **valores)
            else:
                (
                    UsuarioORM.update(**valores)
                    .where(UsuarioORM.id_usuario == usuario.id_usuario)
                    .execute()
                )
        self.usuarios[usuario.id_usuario] = usuario
        return usuario

    def _guardar_categoria(self, categoria: Categoria) -> Categoria:
        valores = {"nombre": categoria.nombre, "descripcion": categoria.descripcion}
        if categoria.id_categoria is None:
            fila = CategoriaORM.create(**valores)
            categoria.id_categoria = fila.id_categoria
        else:
            existente = CategoriaORM.get_or_none(
                CategoriaORM.id_categoria == categoria.id_categoria
            )
            if existente is None:
                CategoriaORM.create(id_categoria=categoria.id_categoria, **valores)
            else:
                (
                    CategoriaORM.update(**valores)
                    .where(CategoriaORM.id_categoria == categoria.id_categoria)
                    .execute()
                )
        self.categorias[categoria.id_categoria] = categoria
        return categoria

    def _guardar_ingrediente(self, ingrediente: Ingrediente) -> Ingrediente:
        nombre = ingrediente.nombre.strip()
        fila = (
            IngredienteORM.select()
            .where(fn.LOWER(IngredienteORM.nombre) == nombre.lower())
            .first()
        )
        if fila is not None:
            ingrediente.id_ingrediente = fila.id_ingrediente
            ingrediente.nombre = nombre
            self.ingredientes[ingrediente.id_ingrediente] = ingrediente
            return ingrediente

        valores = {
            "nombre": nombre,
            "categoria_ingrediente": ingrediente.categoria_ingrediente,
        }
        if ingrediente.id_ingrediente is None:
            fila = IngredienteORM.create(**valores)
            ingrediente.id_ingrediente = fila.id_ingrediente
        else:
            existente = IngredienteORM.get_or_none(
                IngredienteORM.id_ingrediente == ingrediente.id_ingrediente
            )
            if existente is None:
                IngredienteORM.create(id_ingrediente=ingrediente.id_ingrediente, **valores)
            else:
                (
                    IngredienteORM.update(**valores)
                    .where(
                        IngredienteORM.id_ingrediente == ingrediente.id_ingrediente
                    )
                    .execute()
                )
        self.ingredientes[ingrediente.id_ingrediente] = ingrediente
        return ingrediente

    def _buscar_o_crear_ingrediente(self, ingrediente: Ingrediente) -> Ingrediente:
        nombre = ingrediente.nombre.strip()
        fila = (
            IngredienteORM.select()
            .where(fn.LOWER(IngredienteORM.nombre) == nombre.lower())
            .first()
        )
        if fila is None:
            fila = IngredienteORM.create(
                nombre=nombre,
                categoria_ingrediente=ingrediente.categoria_ingrediente,
            )
        ingrediente.id_ingrediente = fila.id_ingrediente
        ingrediente.nombre = fila.nombre
        self.ingredientes[ingrediente.id_ingrediente] = ingrediente
        return ingrediente

    def _buscar_o_crear_categoria(self, categoria: Categoria) -> Categoria:
        nombre = categoria.nombre.strip()
        fila = (
            CategoriaORM.select()
            .where(fn.LOWER(CategoriaORM.nombre) == nombre.lower())
            .first()
        )
        if fila is None:
            fila = CategoriaORM.create(nombre=nombre, descripcion=categoria.descripcion)
        categoria.id_categoria = fila.id_categoria
        categoria.nombre = fila.nombre
        self.categorias[categoria.id_categoria] = categoria
        return categoria

    def _sincronizar_relaciones_receta(self, receta: Receta) -> None:
        DetalleIngredienteORM.delete().where(
            DetalleIngredienteORM.receta == receta.id_receta
        ).execute()
        RecetaCategoriaORM.delete().where(
            RecetaCategoriaORM.receta == receta.id_receta
        ).execute()

        for detalle in receta.ingredientes:
            ingrediente = detalle.ingrediente
            if ingrediente is None:
                continue
            ingrediente = self._buscar_o_crear_ingrediente(ingrediente)
            detalle.id_ingrediente = ingrediente.id_ingrediente
            detalle.id_receta = receta.id_receta
            DetalleIngredienteORM.create(
                receta=receta.id_receta,
                ingrediente=ingrediente.id_ingrediente,
                cantidad=detalle.cantidad,
                unidad_medida=detalle.unidad_medida,
            )

        for categoria in receta.categorias:
            categoria = self._buscar_o_crear_categoria(categoria)
            RecetaCategoriaORM.create(
                receta=receta.id_receta,
                categoria=categoria.id_categoria,
            )

    def agregar_usuario(self, usuario: Usuario) -> Usuario:
        with database.connection_context(), database.atomic():
            self._guardar_usuario(usuario)
        return usuario

    def obtener_usuario(self, id_usuario: int) -> Usuario | None:
        return self.usuarios.get(id_usuario)

    def listar_usuarios(self) -> list[Usuario]:
        return list(self.usuarios.values())

    def agregar_categoria(self, categoria: Categoria) -> Categoria:
        with database.connection_context(), database.atomic():
            self._guardar_categoria(categoria)
        return categoria

    def obtener_categoria(self, id_categoria: int) -> Categoria | None:
        return self.categorias.get(id_categoria)

    def listar_categorias(self) -> list[Categoria]:
        return list(self.categorias.values())

    def agregar_ingrediente(self, ingrediente: Ingrediente) -> Ingrediente:
        if not ingrediente.nombre.strip():
            raise ValueError("El nombre del ingrediente es obligatorio.")
        with database.connection_context(), database.atomic():
            self._guardar_ingrediente(ingrediente)
        return ingrediente

    def obtener_ingrediente(self, id_ingrediente: int) -> Ingrediente | None:
        return self.ingredientes.get(id_ingrediente)

    def listar_ingredientes(self) -> list[Ingrediente]:
        return list(self.ingredientes.values())

    def agregar_receta(self, receta: Receta) -> Receta:
        with database.connection_context(), database.atomic():
            if receta.autor is not None and receta.autor.id_usuario is None:
                self._guardar_usuario(receta.autor)

            if receta.id_usuario is not None and receta.autor is None:
                receta.autor = self.usuarios.get(receta.id_usuario)

            id_usuario = receta.id_usuario or (
                receta.autor.id_usuario if receta.autor else 1
            )
            valores = {
                "nombre": receta.nombre.strip(),
                "descripcion": receta.descripcion.strip(),
                "tiempo_preparacion": int(receta.tiempo_preparacion),
                "dificultad": receta.dificultad,
                "instrucciones": receta.instrucciones,
                "porciones": int(receta.porciones),
                "imagen_url": receta.imagen_url,
                "usuario": id_usuario,
            }

            if receta.id_receta is None:
                fila = RecetaORM.create(**valores)
                receta.id_receta = fila.id_receta
            else:
                existente = RecetaORM.get_or_none(
                    RecetaORM.id_receta == receta.id_receta
                )
                if existente is None:
                    RecetaORM.create(id_receta=receta.id_receta, **valores)
                else:
                    (
                        RecetaORM.update(**valores)
                        .where(RecetaORM.id_receta == receta.id_receta)
                        .execute()
                    )

            receta.id_usuario = id_usuario
            self._sincronizar_relaciones_receta(receta)
            self.recetas[receta.id_receta] = receta
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
        return [
            receta
            for receta in self.recetas.values()
            if any(texto in categoria.nombre.lower() for categoria in receta.categorias)
        ]

    def editar_receta(self, id_receta: int, receta_nueva: Receta) -> Receta:
        if id_receta not in self.recetas:
            raise ValueError(f"La receta con id {id_receta} no existe.")
        receta_nueva.id_receta = id_receta
        if receta_nueva.autor is not None and receta_nueva.autor.id_usuario is None:
            self.agregar_usuario(receta_nueva.autor)
        return self.agregar_receta(receta_nueva)

    def eliminar_receta(self, id_receta: int) -> bool:
        if id_receta not in self.recetas:
            return False
        with database.connection_context(), database.atomic():
            DetalleIngredienteORM.delete().where(
                DetalleIngredienteORM.receta == id_receta
            ).execute()
            RecetaCategoriaORM.delete().where(
                RecetaCategoriaORM.receta == id_receta
            ).execute()
            RecetaORM.delete().where(RecetaORM.id_receta == id_receta).execute()
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

        with database.connection_context(), database.atomic():
            ingrediente_guardado = self._buscar_o_crear_ingrediente(ingrediente)
            detalle = DetalleIngrediente(
                id_receta=id_receta,
                id_ingrediente=ingrediente_guardado.id_ingrediente,
                ingrediente=ingrediente_guardado,
                cantidad=Decimal(str(cantidad)),
                unidad_medida=unidad_medida,
            )
            existente = DetalleIngredienteORM.get_or_none(
                (DetalleIngredienteORM.receta == id_receta)
                & (
                    DetalleIngredienteORM.ingrediente
                    == ingrediente_guardado.id_ingrediente
                )
            )
            if existente is None:
                DetalleIngredienteORM.create(
                    receta=id_receta,
                    ingrediente=ingrediente_guardado.id_ingrediente,
                    cantidad=detalle.cantidad,
                    unidad_medida=unidad_medida,
                )
            else:
                (
                    DetalleIngredienteORM.update(
                        cantidad=detalle.cantidad,
                        unidad_medida=unidad_medida,
                    )
                    .where(
                        (DetalleIngredienteORM.receta == id_receta)
                        & (
                            DetalleIngredienteORM.ingrediente
                            == ingrediente_guardado.id_ingrediente
                        )
                    )
                    .execute()
                )
        receta.ingredientes = [
            item
            for item in receta.ingredientes
            if item.id_ingrediente != ingrediente_guardado.id_ingrediente
        ]
        receta.ingredientes.append(detalle)
        return detalle

    def _cargar_datos_demo(self) -> None:
        usuario1 = self.agregar_usuario(
            Usuario(id_usuario=None, nombre="Antonia", email="antonia@gmail.com")
        )
        self.agregar_usuario(
            Usuario(id_usuario=None, nombre="Joaquín", email="joaquin@gmail.com")
        )

        for receta_data in RECETAS_CHILENAS:
            categorias = []
            if receta_data.get("tipo"):
                categorias.append(
                    Categoria(
                        nombre=receta_data["tipo"],
                        descripcion="Receta chilena recomendada para cocinar en casa.",
                    )
                )
            receta = Receta(
                nombre=receta_data["nombre"],
                descripcion=receta_data["descripcion"],
                tiempo_preparacion=int(receta_data["tiempo_preparacion"]),
                dificultad=receta_data["dificultad"],
                instrucciones="\n".join(receta_data["instrucciones"]),
                porciones=int(receta_data["porciones"]),
                id_usuario=usuario1.id_usuario,
                autor=usuario1,
                categorias=categorias,
            )

            for nombre_ingrediente in receta_data["ingredientes"]:
                ingrediente = self.obtener_ingrediente_by_name(nombre_ingrediente)
                if ingrediente is None:
                    ingrediente = self.agregar_ingrediente(
                        Ingrediente(
                            nombre=nombre_ingrediente.strip(),
                            categoria_ingrediente="General",
                        )
                    )
                receta.ingredientes.append(
                    DetalleIngrediente(
                        ingrediente=ingrediente,
                        cantidad=Decimal("1"),
                        unidad_medida="unidad",
                    )
                )
            self.agregar_receta(receta)

    def obtener_ingrediente_by_name(self, nombre: str) -> Ingrediente | None:
        texto = nombre.strip().lower()
        return next(
            (
                ingrediente
                for ingrediente in self.ingredientes.values()
                if ingrediente.nombre.lower() == texto
            ),
            None,
        )


__all__ = ["RepositorioRecetas"]
