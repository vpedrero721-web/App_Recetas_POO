from __future__ import annotations

from peewee import (
    AutoField,
    CharField,
    CompositeKey,
    DateField,
    DecimalField,
    ForeignKeyField,
    IntegerField,
    Model,
    SmallIntegerField,
    TextField,
)

from datos.conexion import database


class BaseModel(Model):
    class Meta:
        database = database


class UsuarioORM(BaseModel):
    id_usuario = AutoField()
    nombre = CharField(max_length=100)
    email = CharField(max_length=100, unique=True)

    class Meta:
        table_name = "Usuarios"


class CategoriaORM(BaseModel):
    id_categoria = AutoField()
    nombre = CharField(max_length=100, unique=True)
    descripcion = CharField(max_length=255)

    class Meta:
        table_name = "Categorias"


class RecetaORM(BaseModel):
    id_receta = AutoField()
    nombre = CharField(max_length=100)
    descripcion = TextField()
    tiempo_preparacion = IntegerField()
    dificultad = CharField(max_length=20)
    instrucciones = TextField()
    porciones = IntegerField(default=4)
    imagen_url = CharField(max_length=255, null=True)
    usuario = ForeignKeyField(
        UsuarioORM,
        column_name="id_usuario",
        backref="recetas",
        lazy_load=False,
    )

    class Meta:
        table_name = "Recetas"


class IngredienteORM(BaseModel):
    id_ingrediente = AutoField()
    nombre = CharField(max_length=100, unique=True)
    categoria_ingrediente = CharField(max_length=100)

    class Meta:
        table_name = "Ingredientes"


class DetalleIngredienteORM(BaseModel):
    receta = ForeignKeyField(
        RecetaORM,
        column_name="id_receta",
        backref="detalles_ingredientes",
        lazy_load=False,
    )
    ingrediente = ForeignKeyField(
        IngredienteORM,
        column_name="id_ingrediente",
        backref="detalles_recetas",
        lazy_load=False,
    )
    cantidad = DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = CharField(max_length=50)

    class Meta:
        table_name = "DetalleIngrediente"
        primary_key = CompositeKey("receta", "ingrediente")


class RecetaCategoriaORM(BaseModel):
    receta = ForeignKeyField(
        RecetaORM,
        column_name="id_receta",
        backref="relaciones_categorias",
        lazy_load=False,
    )
    categoria = ForeignKeyField(
        CategoriaORM,
        column_name="id_categoria",
        backref="relaciones_recetas",
        lazy_load=False,
    )

    class Meta:
        table_name = "RecetasCategorias"
        primary_key = CompositeKey("receta", "categoria")


class ValoracionORM(BaseModel):
    id_valoracion = AutoField()
    puntuacion = SmallIntegerField()
    comentario = TextField(null=True)
    fecha = DateField()
    usuario = ForeignKeyField(
        UsuarioORM,
        column_name="id_usuario",
        backref="valoraciones",
        lazy_load=False,
    )
    receta = ForeignKeyField(
        RecetaORM,
        column_name="id_receta",
        backref="valoraciones",
        lazy_load=False,
    )

    class Meta:
        table_name = "Valoraciones"
        indexes = ((("usuario", "receta"), True),)


class RecetaGuardadaORM(BaseModel):
    usuario = ForeignKeyField(
        UsuarioORM,
        column_name="id_usuario",
        backref="recetas_guardadas",
        lazy_load=False,
    )
    receta = ForeignKeyField(
        RecetaORM,
        column_name="id_receta",
        backref="guardada_por",
        lazy_load=False,
    )
    fecha_guardado = DateField()

    class Meta:
        table_name = "RecetasGuardadas"
        primary_key = CompositeKey("usuario", "receta")


__all__ = [
    "database",
    "UsuarioORM",
    "CategoriaORM",
    "RecetaORM",
    "IngredienteORM",
    "DetalleIngredienteORM",
    "RecetaCategoriaORM",
    "ValoracionORM",
    "RecetaGuardadaORM",
]
