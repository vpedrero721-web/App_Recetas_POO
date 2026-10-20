from __future__ import annotations


RECETAS_CHILENAS = [
    {
        "id_receta": 1,
        "nombre": "Pastel de Choclo",
        "descripcion": "Un clásico chileno con choclo, carne picada y huevos, ideal para cenas familiares.",
        "tipo": "Plato principal",
        "dificultad": "Media",
        "tiempo_preparacion": 75,
        "porciones": 6,
        "ingredientes": [
            "1 kg de choclo molido",
            "500 g de carne molida",
            "1 cebolla picada",
            "2 huevos",
            "2 cucharadas de azúcar",
            "1 cucharadita de comino",
            "1 taza de caldo",
            "aceite, sal y pimienta"
        ],
        "instrucciones": [
            "Sofríe la cebolla y la carne con comino, sal y pimienta.",
            "Agrega caldo y cocina hasta que la mezcla se espese.",
            "Mezcla el choclo molido con azúcar y un poco de sal.",
            "Coloca la carne en un molde y cubre con la preparación de choclo.",
            "Hornea hasta dorar y sirve caliente."
        ]
    },
    {
        "id_receta": 2,
        "nombre": "Cazuela de Pollo",
        "descripcion": "Receta tradicional chilena, reconfortante y muy nutritiva.",
        "tipo": "Sopa / plato principal",
        "dificultad": "Media",
        "tiempo_preparacion": 90,
        "porciones": 4,
        "ingredientes": [
            "1 pollo entero o trozos",
            "2 papas grandes",
            "2 zanahorias",
            "1 calabaza",
            "1 cebolla",
            "2 dientes de ajo",
            "1 taza de arroz o sémola",
            "agua, sal, pimienta y perejil"
        ],
        "instrucciones": [
            "Hierve el pollo con cebolla y ajo hasta que esté tierno.",
            "Retira y corta los trozos. Reserve el caldo.",
            "Añade las verduras y cocina hasta ablandar.",
            "Incorpora el arroz o sémola y deja cocinar hasta espesar.",
            "Vuelve el pollo al caldo y corrige la sazón."
        ]
    },
    {
        "id_receta": 3,
        "nombre": "Empanadas de Pino",
        "descripcion": "Clásicas empanadas chilenas rellenas de carne, huevo y aceitunas.",
        "tipo": "Snack / entrada",
        "dificultad": "Media",
        "tiempo_preparacion": 60,
        "porciones": 10,
        "ingredientes": [
            "500 g de harina",
            "200 ml de agua tibia",
            "2 cucharadas de aceite",
            "500 g de carne molida",
            "1 cebolla picada",
            "2 huevos cocidos",
            "aceitunas",
            "pimentón, comino y sal"
        ],
        "instrucciones": [
            "Prepara la masa con harina, agua y aceite hasta obtener una masa suave.",
            "Sofríe la cebolla con la carne molida y condimentos.",
            "Deja enfriar la mezcla y agrega huevo picado y aceitunas.",
            "Rellena los círculos de masa y doblalos en forma de empanada.",
            "Hornea hasta dorar y servir tibias."
        ]
    },
    {
        "id_receta": 4,
        "nombre": "Humitas en Chala",
        "descripcion": "Delicada preparación de maíz dulce envuelta en chala.",
        "tipo": "Entrada / desayuno",
        "dificultad": "Media",
        "tiempo_preparacion": 50,
        "porciones": 6,
        "ingredientes": [
            "10 choclos frescos",
            "1 cebolla picada",
            "2 cucharadas de mantequilla",
            "1 taza de leche",
            "sal y pimienta",
            "chalas para envolver"
        ],
        "instrucciones": [
            "Ralla el choclo y mezcla con la mantequilla, la cebolla y la leche.",
            "Sazona con sal y pimienta.",
            "Coloca la mezcla sobre las chalas y dóblalas.",
            "Hiérvelas en agua hasta que estén bien cocidas.",
            "Sírvelas calientes con mantequilla o queso."
        ]
    },
    {
        "id_receta": 5,
        "nombre": "Churrasco a la Parrilla",
        "descripcion": "Clásico plato chileno para asados con sabor ahumado.",
        "tipo": "Plato principal",
        "dificultad": "Fácil",
        "tiempo_preparacion": 40,
        "porciones": 3,
        "ingredientes": [
            "3 filetes de carne",
            "2 dientes de ajo",
            "1 cucharada de ají de color",
            "sal, pimienta y aceite",
            "papas o ensalada para acompañar"
        ],
        "instrucciones": [
            "Marina la carne con ajo, aceite, sal, pimienta y ají de color.",
            "Calienta la parrilla a fuego medio-alto.",
            "Asa la carne a tu punto deseado.",
            "Deja reposar unos minutos antes de cortar.",
            "Sirve con papas o ensalada."
        ]
    },
    {
        "id_receta": 6,
        "nombre": "Sopaipillas Pasadas",
        "descripcion": "Repostería chilena tradicional, ideal para una tarde de invierno.",
        "tipo": "Dulce / postre",
        "dificultad": "Media",
        "tiempo_preparacion": 35,
        "porciones": 8,
        "ingredientes": [
            "2 tazas de harina",
            "1 cucharadita de polvo de hornear",
            "1 cucharadita de sal",
            "1 taza de agua",
            "pasa, azúcar y canela para decorar"
        ],
        "instrucciones": [
            "Forma la masa con la harina, el polvo de hornear, la sal y el agua.",
            "Amasa suavemente y corta discos pequeños.",
            "Fríe hasta dorar en aceite caliente.",
            "Escurre y pasa por azúcar y canela.",
            "Sirve tibias y crocantes."
        ]
    },
    {
        "id_receta": 7,
        "nombre": "Tomaticán",
        "descripcion": "Preparación simple y sabrosa con tomates, cebolla y huevo.",
        "tipo": "Plato rápido",
        "dificultad": "Fácil",
        "tiempo_preparacion": 20,
        "porciones": 2,
        "ingredientes": [
            "4 tomates maduros",
            "1 cebolla",
            "2 huevos",
            "1 cucharada de aceite",
            "sal, pimienta y ají molido"
        ],
        "instrucciones": [
            "Pica la cebolla y sofríela suavemente.",
            "Agrega los tomates cortados y cocina a fuego medio.",
            "Condimenta con sal, pimienta y ají.",
            "Añade los huevos y cocina hasta que cuajen.",
            "Sirve con pan o arroz."
        ]
    },
    {
        "id_receta": 8,
        "nombre": "Mote con Huesillo",
        "descripcion": "Bebida tradicional chilena, fresca y muy típica en verano.",
        "tipo": "Bebida",
        "dificultad": "Fácil",
        "tiempo_preparacion": 15,
        "porciones": 4,
        "ingredientes": [
            "1 taza de mote",
            "1 taza de duraznos secos",
            "agua fría",
            "azúcar al gusto",
            "corteza de limón"
        ],
        "instrucciones": [
            "Deja remojar el huesillo y el mote según sea necesario.",
            "Hierve el huesillo con azúcar y corteza de limón.",
            "Sirve en vasos con hielo y agrega mote.",
            "Completa con agua fría al gusto.",
            "Sirve bien fría."
        ]
    },
    {
        "id_receta": 9,
        "nombre": "Lomo a lo Pobre",
        "descripcion": "Clásico chileno con carne, papas fritas, huevo y cebolla caramelizada.",
        "tipo": "Plato principal",
        "dificultad": "Media",
        "tiempo_preparacion": 45,
        "porciones": 2,
        "ingredientes": [
            "2 filetes de lomo",
            "2 papas medianas",
            "2 huevos",
            "1 cebolla",
            "1 cucharada de aceite",
            "sal y pimienta"
        ],
        "instrucciones": [
            "Corta las papas y fríelas hasta dorar.",
            "Sofríe la cebolla hasta caramelizar.",
            "Saltea la carne a la plancha con sal y pimienta.",
            "Fríe los huevos por separado.",
            "Sirve la carne con papas, cebolla y huevo encima."
        ]
    },
    {
        "id_receta": 10,
        "nombre": "Porotos Granados",
        "descripcion": "Guiso tradicional chileno con porotos, maíz y carne.",
        "tipo": "Plato principal",
        "dificultad": "Media",
        "tiempo_preparacion": 80,
        "porciones": 4,
        "ingredientes": [
            "500 g de porotos",
            "1 maíz desgranado",
            "200 g de carne",
            "1 cebolla",
            "2 dientes de ajo",
            "caldo y sal"
        ],
        "instrucciones": [
            "Remoja los porotos y cocínalos hasta ablandar.",
            "Sofríe la cebolla y el ajo con la carne.",
            "Agrega el maíz y cocina junto con los porotos.",
            "Añade caldo y sazona a gusto.",
            "Deja hervir hasta obtener una preparación cremosa."
        ]
    },
    {
        "id_receta": 11,
        "nombre": "Paila Marina",
        "descripcion": "Sopa tradicional chilena a base de mariscos y pescado.",
        "tipo": "Sopa / mariscos",
        "dificultad": "Difícil",
        "tiempo_preparacion": 60,
        "porciones": 4,
        "ingredientes": [
            "300 g de pescado",
            "200 g de mariscos",
            "1 cebolla",
            "2 papas",
            "1 litro de caldo",
            "pimentón y perejil"
        ],
        "instrucciones": [
            "Sofríe la cebolla y añade el caldo.",
            "Incorpora las papas y cocina hasta ablandar.",
            "Agrega el pescado y los mariscos.",
            "Sazona con pimentón y perejil.",
            "Cocina a fuego suave hasta que todo esté listo."
        ]
    },
    {
        "id_receta": 12,
        "nombre": "Torta de Mil Hojas con Manjar",
        "descripcion": "Postre chileno dulce y festivo para ocasiones especiales.",
        "tipo": "Postre",
        "dificultad": "Media",
        "tiempo_preparacion": 90,
        "porciones": 8,
        "ingredientes": [
            "1 masa hojaldre",
            "1 taza de manjar",
            "1 taza de crema",
            "azúcar y canela",
            "frutas para decorar"
        ],
        "instrucciones": [
            "Hornea la masa hasta que quede dorada y crocante.",
            "Separa la masa en capas.",
            "Unta manjar y crema entre cada capa.",
            "Termina con azúcar y canela.",
            "Refrigera antes de servir."
        ]
    },
    {
        "id_receta": 13,
        "nombre": "Calzones de Queso",
        "descripcion": "Snack casero muy sabroso, ideal para compartir.",
        "tipo": "Snack",
        "dificultad": "Fácil",
        "tiempo_preparacion": 30,
        "porciones": 6,
        "ingredientes": [
            "6 tortillas",
            "200 g de queso",
            "1 tomate",
            "1 cebolla",
            "aceite y pimienta"
        ],
        "instrucciones": [
            "Pica la cebolla y el tomate.",
            "Rellena cada tortilla con queso y vegetales.",
            "Dobla la tortilla y cocina en sartén.",
            "Dorá por ambos lados.",
            "Sirve calientes."
        ]
    },
    {
        "id_receta": 14,
        "nombre": "Ensalada Chilena",
        "descripcion": "Preparación fresca y ligera, ideal como acompañamiento.",
        "tipo": "Acompañamiento",
        "dificultad": "Fácil",
        "tiempo_preparacion": 15,
        "porciones": 4,
        "ingredientes": [
            "1 tomate",
            "1 cebolla",
            "1 aguacate",
            "1 limón",
            "aceite y sal"
        ],
        "instrucciones": [
            "Corta todos los ingredientes en trozos medianos.",
            "Mezcla en un bol.",
            "Aliña con limón, aceite y sal.",
            "Refrigera unos minutos.",
            "Sirve fría."
        ]
    }
]


def recetas_principal():
    """Función principal para mostrar ejemplos de recetas chilenas."""
    return RECETAS_CHILENAS


if __name__ == "__main__":
    for receta in RECETAS_CHILENAS:
        print(f"- {receta['nombre']} ({receta['tipo']})")

