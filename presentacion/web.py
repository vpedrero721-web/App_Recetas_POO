from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from negocios.servicio_recetas import ServicioRecetas


DIRECTORIO_ESTATICO = Path(__file__).with_name("web")
MAXIMO_CUERPO = 1_000_000


def _serializar_receta(receta) -> dict[str, object]:
    return {
        "id_receta": receta.id_receta,
        "nombre": receta.nombre,
        "descripcion": receta.descripcion,
        "tiempo_preparacion": receta.tiempo_preparacion,
        "dificultad": receta.dificultad,
        "porciones": receta.porciones,
        "instrucciones": receta.instrucciones.splitlines(),
        "categorias": [categoria.nombre for categoria in receta.categorias],
        "ingredientes": [
            {
                "nombre": detalle.ingrediente.nombre if detalle.ingrediente else "Ingrediente",
                "cantidad": str(detalle.cantidad),
                "unidad_medida": detalle.unidad_medida,
            }
            for detalle in receta.ingredientes
        ],
        "autor": receta.autor.nombre if receta.autor else "Cocina de casa",
    }


class ManejadorRecetas(SimpleHTTPRequestHandler):
    servicio = ServicioRecetas()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(DIRECTORIO_ESTATICO), **kwargs)

    def _responder_json(self, estado: int, contenido: object) -> None:
        cuerpo = json.dumps(contenido, ensure_ascii=False).encode("utf-8")
        self.send_response(estado)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _leer_json(self) -> dict[str, object]:
        try:
            longitud = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("El tamaño de la solicitud no es válido.") from exc
        if longitud <= 0 or longitud > MAXIMO_CUERPO:
            raise ValueError("La solicitud debe incluir datos y no superar 1 MB.")
        try:
            datos = json.loads(self.rfile.read(longitud))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("El cuerpo debe contener JSON válido.") from exc
        if not isinstance(datos, dict):
            raise ValueError("El cuerpo debe ser un objeto JSON.")
        return datos

    def _campos_receta(self, datos: dict[str, object], crear: bool) -> dict[str, object]:
        campos: dict[str, object] = {}
        textos = {
            "nombre": "nombre",
            "descripcion": "descripción",
            "dificultad": "dificultad",
        }
        for campo, etiqueta in textos.items():
            if campo in datos:
                valor = datos[campo]
                if not isinstance(valor, str):
                    raise ValueError(f"El campo {etiqueta} debe ser texto.")
                campos[campo] = valor
            elif crear and campo == "nombre":
                raise ValueError("El nombre de la receta es obligatorio.")

        for campo, etiqueta in (
            ("tiempo_preparacion", "tiempo de preparación"),
            ("porciones", "porciones"),
        ):
            if campo in datos:
                valor = datos[campo]
                if isinstance(valor, bool) or not isinstance(valor, int):
                    raise ValueError(f"El campo {etiqueta} debe ser un número entero.")
                campos[campo] = valor
            elif crear and campo == "tiempo_preparacion":
                raise ValueError("El tiempo de preparación es obligatorio.")

        if "instrucciones" in datos:
            instrucciones = datos["instrucciones"]
            if isinstance(instrucciones, list) and all(
                isinstance(paso, str) for paso in instrucciones
            ):
                campos["instrucciones"] = "\n".join(instrucciones)
            elif isinstance(instrucciones, str):
                campos["instrucciones"] = instrucciones
            else:
                raise ValueError("Las instrucciones deben ser texto o una lista de textos.")
        elif crear:
            campos["instrucciones"] = ""

        if "ingredientes" in datos:
            ingredientes = datos["ingredientes"]
            if not isinstance(ingredientes, list) or not all(
                isinstance(ingrediente, str) for ingrediente in ingredientes
            ):
                raise ValueError("Los ingredientes deben ser una lista de textos.")
            campos["ingredientes"] = [ingrediente.strip() for ingrediente in ingredientes if ingrediente.strip()]
        elif crear:
            campos["ingredientes"] = []

        if crear:
            campos.setdefault("descripcion", "")
            campos.setdefault("dificultad", "Fácil")
            campos.setdefault("porciones", 1)
        return campos

    def _responder_error(self, estado: int, mensaje: str) -> None:
        self._responder_json(estado, {"error": mensaje})

    def do_GET(self) -> None:
        ruta = urlsplit(self.path).path
        if ruta == "/api/recetas":
            recetas = self.servicio.listar_recetas()
            self._responder_json(200, [_serializar_receta(receta) for receta in recetas])
            return

        prefijo = "/api/recetas/"
        if ruta.startswith(prefijo):
            try:
                id_receta = int(ruta[len(prefijo):])
            except ValueError:
                self._responder_error(400, "El identificador de la receta no es válido.")
                return
            receta = self.servicio.obtener_receta(id_receta)
            if receta is None:
                self._responder_error(404, "No se encontró la receta.")
                return
            self._responder_json(200, _serializar_receta(receta))
            return

        super().do_GET()

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/recetas":
            self._responder_error(404, "La ruta solicitada no existe.")
            return
        try:
            campos = self._campos_receta(self._leer_json(), crear=True)
            receta = self.servicio.crear_receta(
                nombre=str(campos["nombre"]),
                descripcion=str(campos["descripcion"]),
                tiempo=int(campos["tiempo_preparacion"]),
                dificultad=str(campos["dificultad"]),
                instrucciones=str(campos["instrucciones"]),
                porciones=int(campos["porciones"]),
            )
            for ingrediente in campos["ingredientes"]:
                self.servicio.agregar_ingrediente(receta.id_receta, str(ingrediente), "1", "unidad")
        except ValueError as exc:
            self._responder_error(400, str(exc))
            return
        self._responder_json(201, _serializar_receta(receta))

    def do_PATCH(self) -> None:
        prefijo = "/api/recetas/"
        ruta = urlsplit(self.path).path
        if not ruta.startswith(prefijo):
            self._responder_error(404, "La ruta solicitada no existe.")
            return
        try:
            id_receta = int(ruta[len(prefijo):])
            campos = self._campos_receta(self._leer_json(), crear=False)
            receta = self.servicio.editar_receta(id_receta, **{
                "nombre": campos.get("nombre"),
                "descripcion": campos.get("descripcion"),
                "tiempo": campos.get("tiempo_preparacion"),
                "dificultad": campos.get("dificultad"),
                "instrucciones": campos.get("instrucciones"),
                "porciones": campos.get("porciones"),
            })
            if "ingredientes" in campos:
                receta.ingredientes.clear()
                for ingrediente in campos["ingredientes"]:
                    self.servicio.agregar_ingrediente(id_receta, str(ingrediente), "1", "unidad")
        except ValueError as exc:
            self._responder_error(400, str(exc))
            return
        self._responder_json(200, _serializar_receta(receta))

    def do_DELETE(self) -> None:
        prefijo = "/api/recetas/"
        ruta = urlsplit(self.path).path
        if not ruta.startswith(prefijo):
            self._responder_error(404, "La ruta solicitada no existe.")
            return
        try:
            id_receta = int(ruta[len(prefijo):])
        except ValueError:
            self._responder_error(400, "El identificador de la receta no es válido.")
            return
        if not self.servicio.eliminar_receta(id_receta):
            self._responder_error(404, "No se encontró la receta.")
            return
        self._responder_json(200, {"eliminada": True})


def iniciar_servidor() -> None:
    direccion = ("127.0.0.1", 8000)
    servidor = ThreadingHTTPServer(direccion, ManejadorRecetas)
    print("App de Recetas disponible en http://127.0.0.1:8000 (Ctrl+C para salir)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()
