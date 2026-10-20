from __future__ import annotations

from decimal import Decimal

from datos.models import DetalleIngrediente, Ingrediente, Receta, Usuario
from datos.repositorio import RepositorioRecetas


class ServicioRecetas:
    """Lógica de negocio para gestionar recetas."""

    def __init__(self, repositorio: RepositorioRecetas | None = None) -> None:
        self.repositorio = repositorio or RepositorioRecetas()

    def listar_recetas(self):
        return self.repositorio.listar_recetas()

    def buscar_por_nombre(self, texto: str):
        return self.repositorio.buscar_recetas_por_nombre(texto)

    def buscar_por_categoria(self, texto: str):
        return self.repositorio.buscar_recetas_por_categoria(texto)

    def crear_receta(self, nombre: str, descripcion: str, tiempo: int, dificultad: str, instrucciones: str, porciones: int, id_usuario: int | None = None):
        if not nombre.strip():
            raise ValueError("El nombre de la receta es obligatorio.")
        if tiempo <= 0:
            raise ValueError("El tiempo de preparación debe ser mayor a 0.")

        autor = None
        if id_usuario is not None:
            autor = self.repositorio.obtener_usuario(id_usuario)
        if autor is None:
            autor = self.repositorio.listar_usuarios()[0] if self.repositorio.listar_usuarios() else Usuario(nombre="Usuario demo", email="demo@recetas.com")

        receta = Receta(
            id_receta=None,
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            tiempo_preparacion=tiempo,
            dificultad=dificultad.strip() or "Fácil",
            instrucciones=instrucciones.strip(),
            porciones=porciones if porciones > 0 else 1,
            imagen_url=None,
            id_usuario=autor.id_usuario,
            autor=autor,
        )
        return self.repositorio.agregar_receta(receta)

    def agregar_ingrediente(self, id_receta: int, nombre_ingrediente: str, cantidad: str, unidad: str):
        ingrediente = Ingrediente(nombre=nombre_ingrediente.strip(), categoria_ingrediente="General")
        ingrediente_guardado = self.repositorio.agregar_ingrediente(ingrediente)
        return self.repositorio.agregar_ingrediente_a_receta(
            id_receta,
            ingrediente_guardado,
            Decimal(cantidad),
            unidad.strip() or "unidad",
        )

    def editar_receta(self, id_receta: int, nombre: str | None = None, descripcion: str | None = None, tiempo: int | None = None, dificultad: str | None = None, instrucciones: str | None = None, porciones: int | None = None):
        receta = self.repositorio.obtener_receta(id_receta)
        if receta is None:
            raise ValueError("La receta no existe.")

        if nombre is not None:
            receta.nombre = nombre.strip() or receta.nombre
        if descripcion is not None:
            receta.descripcion = descripcion.strip() or receta.descripcion
        if tiempo is not None:
            if tiempo <= 0:
                raise ValueError("El tiempo de preparación debe ser mayor a 0.")
            receta.tiempo_preparacion = tiempo
        if dificultad is not None:
            receta.dificultad = dificultad.strip() or receta.dificultad
        if instrucciones is not None:
            receta.instrucciones = instrucciones.strip() or receta.instrucciones
        if porciones is not None:
            if porciones <= 0:
                raise ValueError("Las porciones deben ser mayores a 0.")
            receta.porciones = porciones

        return self.repositorio.editar_receta(id_receta, receta)

    def eliminar_receta(self, id_receta: int):
        return self.repositorio.eliminar_receta(id_receta)

    def obtener_receta(self, id_receta: int):
        return self.repositorio.obtener_receta(id_receta)
