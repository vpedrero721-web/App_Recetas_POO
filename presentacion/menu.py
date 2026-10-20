from __future__ import annotations

from negocio.servicio_recetas import ServicioRecetas


class MenuRecetas:
    """Menú principal de la aplicación en consola."""

    def __init__(self) -> None:
        self.servicio = ServicioRecetas()

    def leer_entrada(self, mensaje: str) -> str:
        try:
            return input(mensaje).strip()
        except EOFError:
            print("\nSe cerró la entrada de datos. Saliendo...")
            raise SystemExit

    def mostrar_menu(self) -> None:
        print("\n=== APP DE RECETAS ===")
        print("1. Ver recetas")
        print("2. Agregar receta")
        print("3. Editar receta")
        print("4. Eliminar receta")
        print("5. Buscar receta")
        print("6. Salir")

    def mostrar_detalle_receta(self, id_receta: int) -> None:
        receta = self.servicio.obtener_receta(id_receta)
        if receta is None:
            print("No se encontró la receta.")
            return

        print(f"\n=== {receta.nombre.upper()} ===")
        print(f"Dificultad: {receta.dificultad}")
        print(f"Tiempo: {receta.tiempo_preparacion} min")
        print(f"Porciones: {receta.porciones}")
        print(f"Descripción: {receta.descripcion}")

        print("\nIngredientes:")
        if receta.ingredientes:
            for detalle in receta.ingredientes:
                nombre = detalle.ingrediente.nombre if detalle.ingrediente else "Ingrediente"
                print(f"- {nombre}: {detalle.cantidad} {detalle.unidad_medida}")
        else:
            print("- Sin ingredientes registrados.")

        print("\nPreparación:")
        instrucciones = receta.instrucciones.split("\n") if receta.instrucciones else ["Sin instrucciones."]
        for i, paso in enumerate(instrucciones, start=1):
            print(f"{i}. {paso.strip()}")

    def mostrar_recetas(self) -> None:
        recetas = self.servicio.listar_recetas()
        if not recetas:
            print("No hay recetas registradas.")
            return

        print("\nRECETAS DISPONIBLES")
        for receta in recetas:
            print(f"- [{receta.id_receta}] {receta.nombre} | {receta.dificultad} | {receta.tiempo_preparacion} min")
            print(f"  {receta.descripcion}")

        try:
            opcion = self.leer_entrada("\nIngrese el ID de la receta para ver el detalle (0 para volver): ")
        except SystemExit:
            return

        if opcion == "0":
            return

        try:
            self.mostrar_detalle_receta(int(opcion))
        except ValueError:
            print("Debe ingresar un número válido.")

    def buscar_receta(self) -> None:
        texto = self.leer_entrada("Ingrese nombre o parte del nombre: ")
        if not texto:
            print("Debe ingresar un texto.")
            return

        recetas = self.servicio.buscar_por_nombre(texto)
        if not recetas:
            print("No se encontraron recetas.")
            return

        print("\nRESULTADOS DE BÚSQUEDA:")
        for receta in recetas:
            print(f"- {receta.id_receta} | {receta.nombre} | {receta.dificultad}")

        try:
            opcion = self.leer_entrada("\nIngrese el ID de la receta para ver el detalle (0 para volver): ")
        except SystemExit:
            return

        if opcion == "0":
            return

        try:
            self.mostrar_detalle_receta(int(opcion))
        except ValueError:
            print("Debe ingresar un número válido.")

    def agregar_receta(self) -> None:
        print("\nNUEVA RECETA")
        nombre = self.leer_entrada("Nombre: ")
        descripcion = self.leer_entrada("Descripción: ")
        tiempo = int(self.leer_entrada("Tiempo de preparación (min): "))
        dificultad = self.leer_entrada("Dificultad (Fácil/Media/Difícil): ")
        instrucciones = self.leer_entrada("Instrucciones: ")
        porciones = int(self.leer_entrada("Porciones: "))

        receta = self.servicio.crear_receta(nombre, descripcion, tiempo, dificultad, instrucciones, porciones)
        print(f"Receta creada: {receta.nombre}")

    def editar_receta(self) -> None:
        try:
            id_receta = int(self.leer_entrada("Ingrese el id de la receta a editar: "))
        except ValueError:
            print("Debe ingresar un número válido.")
            return

        receta = self.servicio.obtener_receta(id_receta)
        if receta is None:
            print("No se encontró la receta.")
            return

        print(f"\nEditando: {receta.nombre}")
        print("Deja vacío el campo si quieres conservar el valor actual.")

        nombre = self.leer_entrada(f"Nuevo nombre ({receta.nombre}): ")
        descripcion = self.leer_entrada(f"Nueva descripción ({receta.descripcion}): ")
        tiempo_texto = self.leer_entrada(f"Nuevo tiempo de preparación ({receta.tiempo_preparacion}): ")
        dificultad = self.leer_entrada(f"Nueva dificultad ({receta.dificultad}): ")
        instrucciones = self.leer_entrada(f"Nuevas instrucciones ({receta.instrucciones[:40]}...): ")
        porciones_texto = self.leer_entrada(f"Nuevas porciones ({receta.porciones}): ")

        try:
            tiempo = int(tiempo_texto) if tiempo_texto else None
            porciones = int(porciones_texto) if porciones_texto else None
            receta_editada = self.servicio.editar_receta(
                id_receta,
                nombre=nombre or None,
                descripcion=descripcion or None,
                tiempo=tiempo,
                dificultad=dificultad or None,
                instrucciones=instrucciones or None,
                porciones=porciones,
            )
            print(f"Receta actualizada: {receta_editada.nombre}")
        except ValueError as exc:
            print(f"Error: {exc}")

    def eliminar_receta(self) -> None:
        id_receta = int(self.leer_entrada("Ingrese el id de la receta a eliminar: "))
        eliminado = self.servicio.eliminar_receta(id_receta)
        if eliminado:
            print("Receta eliminada.")
        else:
            print("No se encontró la receta.")

    def ejecutar(self) -> None:
        while True:
            self.mostrar_menu()
            try:
                opcion = self.leer_entrada("Seleccione una opción: ")
            except SystemExit:
                break

            if opcion == "1":
                self.mostrar_recetas()
            elif opcion == "2":
                self.agregar_receta()
            elif opcion == "3":
                self.editar_receta()
            elif opcion == "4":
                self.eliminar_receta()
            elif opcion == "5":
                self.buscar_receta()
            elif opcion == "6":
                print("Saliendo de la aplicación...")
                break
            else:
                print("Opción no válida.")

            try:
                self.leer_entrada("\nPresione Enter para continuar...")
            except SystemExit:
                break
