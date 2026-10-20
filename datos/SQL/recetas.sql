-- ============================================
-- BASE DE DATOS: APP DE RECETAS
-- Versión 2: datos de prueba de cocina fusión, plant-based y cero desperdicio
-- Compatible con MySQL 8.0.16+ / MariaDB 10.5+
-- Guardar el archivo con codificación UTF-8
-- ============================================

CREATE DATABASE IF NOT EXISTS recetas
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE recetas;

-- ============================================
-- LIMPIEZA (permite volver a ejecutar el script)
-- OJO: borra todos los datos de estas tablas.
-- Orden: primero las tablas hijas, luego las padres.
-- ============================================

DROP VIEW  IF EXISTS vw_recetas_resumen;
DROP TABLE IF EXISTS RecetasCategorias;
DROP TABLE IF EXISTS RecetasGuardadas;
DROP TABLE IF EXISTS Valoraciones;
DROP TABLE IF EXISTS DetalleIngrediente;
DROP TABLE IF EXISTS Ingredientes;
DROP TABLE IF EXISTS Recetas;
DROP TABLE IF EXISTS Categorias;
DROP TABLE IF EXISTS Usuarios;


-- ============================================
-- TABLA: USUARIOS
-- ============================================

CREATE TABLE Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);


-- ============================================
-- TABLA: CATEGORIAS
-- ============================================

CREATE TABLE Categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NOT NULL
);


-- ============================================
-- TABLA: RECETAS
-- ============================================

CREATE TABLE Recetas (
    id_receta INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    tiempo_preparacion INT NOT NULL COMMENT 'Tiempo de preparación y cocción en minutos, sin contar reposos, refrigeración ni fermentación',
    dificultad ENUM('Fácil', 'Media', 'Difícil') NOT NULL,
    instrucciones TEXT NOT NULL,
    porciones INT NOT NULL DEFAULT 4,
    imagen_url VARCHAR(255) NULL,
    id_usuario INT NOT NULL,

    CONSTRAINT chk_receta_tiempo CHECK (tiempo_preparacion > 0),
    CONSTRAINT chk_receta_porciones CHECK (porciones > 0),

    CONSTRAINT fk_recetas_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES Usuarios(id_usuario)
        ON DELETE RESTRICT
);


-- ============================================
-- TABLA: INGREDIENTES
-- ============================================

CREATE TABLE Ingredientes (
    id_ingrediente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    categoria_ingrediente VARCHAR(100) NOT NULL
);


-- ============================================
-- TABLA: DETALLE INGREDIENTE
-- (ingredientes de cada receta)
-- ============================================

CREATE TABLE DetalleIngrediente (
    id_receta INT NOT NULL,
    id_ingrediente INT NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    unidad_medida VARCHAR(50) NOT NULL,

    PRIMARY KEY (id_receta, id_ingrediente),

    CONSTRAINT chk_detalle_cantidad CHECK (cantidad > 0),

    CONSTRAINT fk_detalle_receta
        FOREIGN KEY (id_receta)
        REFERENCES Recetas(id_receta)
        ON DELETE CASCADE,

    CONSTRAINT fk_detalle_ingrediente
        FOREIGN KEY (id_ingrediente)
        REFERENCES Ingredientes(id_ingrediente)
        ON DELETE RESTRICT
);


-- ============================================
-- TABLA: VALORACIONES
-- Un usuario solo puede valorar una vez cada receta
-- ============================================

CREATE TABLE Valoraciones (
    id_valoracion INT AUTO_INCREMENT PRIMARY KEY,
    puntuacion TINYINT NOT NULL,
    comentario TEXT,
    fecha DATE NOT NULL,
    id_usuario INT NOT NULL,
    id_receta INT NOT NULL,

    CONSTRAINT chk_valoracion_puntuacion CHECK (puntuacion BETWEEN 1 AND 5),
    CONSTRAINT uq_valoracion_usuario_receta UNIQUE (id_usuario, id_receta),

    CONSTRAINT fk_valoraciones_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES Usuarios(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT fk_valoraciones_receta
        FOREIGN KEY (id_receta)
        REFERENCES Recetas(id_receta)
        ON DELETE CASCADE
);


-- ============================================
-- TABLA INTERMEDIA:
-- USUARIOS QUE GUARDAN RECETAS
-- ============================================

CREATE TABLE RecetasGuardadas (
    id_usuario INT NOT NULL,
    id_receta INT NOT NULL,
    fecha_guardado DATE NOT NULL,

    PRIMARY KEY (id_usuario, id_receta),

    CONSTRAINT fk_guardadas_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES Usuarios(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT fk_guardadas_receta
        FOREIGN KEY (id_receta)
        REFERENCES Recetas(id_receta)
        ON DELETE CASCADE
);


-- ============================================
-- TABLA INTERMEDIA:
-- RECETAS Y CATEGORIAS
-- ============================================

CREATE TABLE RecetasCategorias (
    id_receta INT NOT NULL,
    id_categoria INT NOT NULL,

    PRIMARY KEY (id_receta, id_categoria),

    CONSTRAINT fk_reccat_receta
        FOREIGN KEY (id_receta)
        REFERENCES Recetas(id_receta)
        ON DELETE CASCADE,

    CONSTRAINT fk_reccat_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES Categorias(id_categoria)
        ON DELETE CASCADE
);


-- ============================================
-- VISTA: RESUMEN DE RECETAS
-- Pensada para el listado de la web
-- (promedio y cantidad de valoraciones)
-- ============================================

CREATE VIEW vw_recetas_resumen AS
SELECT
    r.id_receta,
    r.nombre,
    r.descripcion,
    r.tiempo_preparacion,
    r.dificultad,
    r.porciones,
    r.imagen_url,
    u.nombre AS autor,
    ROUND(AVG(v.puntuacion), 1) AS promedio,
    COUNT(v.id_valoracion) AS total_valoraciones
FROM Recetas r
JOIN Usuarios u ON u.id_usuario = r.id_usuario
LEFT JOIN Valoraciones v ON v.id_receta = r.id_receta
GROUP BY r.id_receta, u.nombre;


-- ============================================
-- DATOS DE PRUEBA - VERSIÓN 2
-- Temática: cocina fusión, plant-based y cero desperdicio
-- (las relaciones se hacen por NOMBRE/EMAIL y no por
--  números de ID, así evitamos cruces equivocados)
-- ============================================

-- ---------- USUARIOS ----------
INSERT INTO Usuarios (nombre, email)
VALUES
('Antonia',  'antonia@gmail.com'),
('Joaquín',  'joaquin@gmail.com'),
('Fernanda', 'fernanda@gmail.com'),
('Tomás',    'tomas@gmail.com'),
('Isidora',  'isidora@gmail.com'),
('Benjamín', 'benjamin@gmail.com');


-- ---------- CATEGORIAS ----------
INSERT INTO Categorias (nombre, descripcion)
VALUES
('Fusión global', 'Platos que mezclan técnicas y sabores de distintas cocinas del mundo.'),
('Plant-based', 'Recetas 100% vegetales, sin carne, pescado ni productos de origen animal.'),
('Cero desperdicio', 'Ideas para aprovechar sobras, cáscaras, tallos y alimentos que ya no lucen perfectos.'),
('Bowls y ensaladas', 'Platos completos y coloridos, servidos en un solo bowl.'),
('Bebidas funcionales', 'Bebidas con ingredientes que aportan energía, frescura o bienestar.'),
('Postres creativos', 'Postres originales hechos con ingredientes inesperados.'),
('Snacks saludables', 'Bocados y untables nutritivos para picar entre comidas.'),
('Fermentados y conservas', 'Recetas de fermentación y conservación natural para alargar la vida de los alimentos.');


-- ---------- INGREDIENTES ----------
INSERT INTO Ingredientes (nombre, categoria_ingrediente)
VALUES
-- Frutas
('Sandía', 'Frutas'),
('Piña', 'Frutas'),
('Plátano', 'Frutas'),
('Limón', 'Frutas'),
('Aguacate', 'Frutas'),
-- Verduras y hortalizas
('Coliflor', 'Verduras y hortalizas'),
('Camote', 'Verduras y hortalizas'),
('Betarraga', 'Verduras y hortalizas'),
('Cebolla morada', 'Verduras y hortalizas'),
('Ajo', 'Verduras y hortalizas'),
('Espinaca', 'Verduras y hortalizas'),
('Champiñones', 'Verduras y hortalizas'),
('Repollo chino', 'Verduras y hortalizas'),
('Zanahoria', 'Verduras y hortalizas'),
('Hojas de zanahoria', 'Verduras y hortalizas'),
('Pepino', 'Verduras y hortalizas'),
('Cebollín', 'Verduras y hortalizas'),
('Ají verde', 'Verduras y hortalizas'),
('Tomate cherry', 'Verduras y hortalizas'),
('Restos de verduras', 'Verduras y hortalizas'),
-- Hierbas y especias
('Cilantro', 'Hierbas y especias'),
('Albahaca', 'Hierbas y especias'),
('Jengibre', 'Hierbas y especias'),
('Comino', 'Hierbas y especias'),
('Pimentón ahumado', 'Hierbas y especias'),
('Canela', 'Hierbas y especias'),
('Laurel', 'Hierbas y especias'),
('Pimienta en grano', 'Hierbas y especias'),
('Ají en hojuelas', 'Hierbas y especias'),
-- Cereales y legumbres
('Quinoa', 'Cereales y legumbres'),
('Arroz', 'Cereales y legumbres'),
('Garbanzos cocidos', 'Cereales y legumbres'),
('Frijoles negros cocidos', 'Cereales y legumbres'),
('Harina de garbanzo', 'Cereales y legumbres'),
('Aquafaba', 'Cereales y legumbres'),
('Edamame', 'Cereales y legumbres'),
('Fideos de ramen', 'Cereales y legumbres'),
-- Proteínas
('Tofu firme', 'Proteínas'),
('Salmón', 'Pescados y mariscos'),
-- Salsas y condimentos
('Pasta de miso', 'Salsas y condimentos'),
('Salsa de soja', 'Salsas y condimentos'),
('Tahini', 'Salsas y condimentos'),
('Vinagre de manzana', 'Salsas y condimentos'),
('Levadura nutricional', 'Salsas y condimentos'),
-- Frutos secos y semillas
('Almendras', 'Frutos secos y semillas'),
('Semillas de sésamo', 'Frutos secos y semillas'),
-- Panadería
('Tortillas de maíz', 'Panadería'),
('Pan duro', 'Panadería'),
-- Dulces y repostería
('Cacao en polvo', 'Dulces y repostería'),
('Chocolate negro', 'Dulces y repostería'),
('Polvo de hornear', 'Dulces y repostería'),
('Jarabe de agave', 'Dulces y repostería'),
('Mantequilla de maní', 'Dulces y repostería'),
-- Té y bebidas vegetales
('Matcha', 'Té y bebidas vegetales'),
('Té negro', 'Té y bebidas vegetales'),
('Leche de avena', 'Té y bebidas vegetales'),
-- Fermentos
('SCOBY', 'Fermentos'),
('Kombucha madura', 'Fermentos'),
-- Básicos de cocina
('Sal', 'Básicos de cocina'),
('Aceite de oliva', 'Básicos de cocina'),
('Aceite de sésamo', 'Básicos de cocina'),
('Agua', 'Básicos de cocina'),
('Hielo', 'Básicos de cocina'),
('Caldo de verduras', 'Básicos de cocina'),
('Azúcar', 'Básicos de cocina'),
('Huevos', 'Básicos de cocina'),
('Leche', 'Básicos de cocina'),
('Mantequilla', 'Básicos de cocina');


-- ---------- RECETAS ----------
INSERT INTO Recetas (nombre, descripcion, tiempo_preparacion, dificultad, instrucciones, porciones, imagen_url, id_usuario)
VALUES
('Ceviche de sandía',
 'Versión 100% vegetal del ceviche: cubos de sandía marinados en limón, ají y jengibre.',
 20, 'Fácil',
 '1. Corta la sandía en cubos de 2 cm y refrigérala. 2. Corta la cebolla morada en pluma fina y remójala 5 minutos en agua fría para suavizar su sabor; escúrrela. 3. Pica el ají sin semillas y el cilantro, y ralla el jengibre. 4. Mezcla el jugo de los limones con el ají, el jengibre, la sal y el aceite: esa es la leche de tigre vegetal. 5. Vierte la mezcla sobre la sandía, agrega la cebolla y el cilantro y deja reposar 5 minutos. 6. Sirve con palta en cubos por encima.',
 4, 'img/recetas/ceviche-de-sandia.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'antonia@gmail.com')),

('Tacos de coliflor al pastor',
 'Coliflor marinada y horneada con piña dorada, inspirada en los clásicos tacos al pastor.',
 45, 'Media',
 '1. Precalienta el horno a 220°C. 2. Mezcla el aceite, el vinagre, el pimentón, el comino, el ajo picado y la sal para hacer la marinada. 3. Corta la coliflor en floretes pequeños y mézclalos con la marinada; deja reposar 10 minutos. 4. Hornea la coliflor 25 minutos, dándole vuelta a la mitad, hasta que esté dorada en los bordes. 5. Corta la piña en cubos y dórala 3 minutos en una sartén bien caliente. 6. Calienta las tortillas y rellénalas con coliflor, piña, cebolla morada picada y cilantro. 7. Termina con un chorrito de limón.',
 4, 'img/recetas/tacos-de-coliflor.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'joaquin@gmail.com')),

('Ramen vegano de miso y setas',
 'Caldo profundo de miso con champiñones salteados, tofu crujiente y fideos.',
 40, 'Media',
 '1. Corta el tofu en cubos y dóralo en una sartén con un poco de aceite de sésamo hasta que esté crujiente; resérvalo. 2. En la misma sartén saltea los champiñones laminados durante 5 minutos. 3. En una olla sofríe el ajo y el jengibre picados durante 1 minuto y agrega el caldo de verduras. 4. Cuando hierva, baja el fuego y disuelve la pasta de miso con un poco del caldo caliente antes de incorporarla; no dejes que hierva después. 5. Agrega la salsa de soja. 6. Cocina los fideos aparte según el paquete y repártelos en dos bowls. 7. Sirve el caldo sobre los fideos y añade el tofu, los champiñones, la espinaca fresca, el cebollín picado y el sésamo.',
 2, 'img/recetas/ramen-vegano.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'fernanda@gmail.com')),

('Bowl de quinoa y camote asado',
 'Bowl completo con quinoa, camote al horno, garbanzos crujientes y aderezo cremoso de tahini.',
 40, 'Fácil',
 '1. Precalienta el horno a 200°C. 2. Corta el camote en cubos, mézclalo con la mitad del aceite, el pimentón y la mitad de la sal, y hornea 25 minutos. 3. Enjuaga la quinoa y cocínala en 300 ml de agua con el resto de la sal durante 15 minutos; déjala reposar tapada 5 minutos. 4. Dora los garbanzos escurridos en una sartén con el aceite restante durante 5 minutos. 5. Mezcla el tahini con el jugo de limón y un poco de agua para hacer un aderezo cremoso. 6. Arma los bowls con la quinoa, la espinaca, el camote, los garbanzos y el aguacate en láminas, y baña con el aderezo.',
 2, 'img/recetas/bowl-quinoa-camote.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'tomas@gmail.com')),

('Poke bowl de salmón',
 'Bowl hawaiano con salmón marinado en soja y sésamo, arroz, aguacate y verduras crujientes.',
 30, 'Fácil',
 '1. Cocina el arroz según las instrucciones del paquete y deja que se entibie. 2. Corta el salmón en cubos de 2 cm; usa salmón fresco apto para consumir crudo. 3. Mezcla la salsa de soja, el aceite de sésamo y el jugo de limón, y marina el salmón 10 minutos en el refrigerador. 4. Corta el pepino y el aguacate en láminas y ralla la zanahoria. 5. Reparte el arroz en dos bowls y coloca encima el salmón, las verduras y el edamame. 6. Termina con cebollín picado y semillas de sésamo.',
 2, 'img/recetas/poke-de-salmon.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'isidora@gmail.com')),

('Hummus de betarraga',
 'Untable de garbanzos y betarraga de un color rosado intenso y sabor suave.',
 15, 'Fácil',
 '1. Escurre los garbanzos y pela la betarraga cocida. 2. Coloca en una procesadora la betarraga, los garbanzos, el tahini, el jugo de limón, el ajo, el comino y la sal. 3. Procesa 2 minutos, agregando el aceite de oliva y unas cucharadas de agua fría hasta lograr una crema suave. 4. Prueba y ajusta la sal y el limón. 5. Sirve con un chorrito de aceite y acompaña con palitos de zanahoria o pan pita.',
 6, 'img/recetas/hummus-de-betarraga.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'benjamin@gmail.com')),

('Caldo de cáscaras',
 'Caldo casero hecho con los restos de verduras que normalmente se botan.',
 60, 'Fácil',
 '1. Durante la semana junta en una bolsa dentro del congelador las cáscaras limpias, puntas y tallos de zanahoria, cebolla, apio y champiñones; evita el repollo, la betarraga y el brócoli, que amargan el caldo. 2. Coloca los restos, el ajo, el laurel y la pimienta en una olla grande. 3. Cubre con el agua y lleva a ebullición. 4. Baja el fuego y cocina 45 minutos con la olla semitapada. 5. Cuela, agrega sal al gusto y deja enfriar. 6. Guarda hasta 5 días en el refrigerador o 3 meses en el congelador.',
 8, 'img/recetas/caldo-de-cascaras.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'antonia@gmail.com')),

('Pesto de hojas de zanahoria',
 'Pesto vegano que aprovecha las hojas de zanahoria, con almendras y levadura nutricional.',
 10, 'Fácil',
 '1. Lava muy bien las hojas de zanahoria y sécalas. 2. Tuesta las almendras en una sartén seca durante 3 minutos. 3. Procesa las hojas, las almendras, el ajo, la levadura nutricional, el jugo de limón y la sal. 4. Agrega el aceite en hilo mientras procesas hasta obtener una salsa espesa. 5. Úsalo con pasta, en sándwiches o como untable; dura 5 días en el refrigerador.',
 6, 'img/recetas/pesto-hojas-de-zanahoria.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'fernanda@gmail.com')),

('Budín de pan con plátanos maduros',
 'Postre que da una segunda vida al pan duro y a los plátanos que ya están muy maduros.',
 70, 'Fácil',
 '1. Precalienta el horno a 180°C y unta un molde con mantequilla. 2. Corta el pan duro en cubos y remójalo 15 minutos en la leche. 3. Aplasta los plátanos maduros con un tenedor. 4. Mezcla el pan remojado con los plátanos, los huevos batidos, el azúcar y la canela. 5. Vierte en el molde y hornea 40 minutos, hasta que esté firme y dorado. 6. Deja entibiar antes de desmoldar.',
 6, 'img/recetas/budin-de-pan.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'joaquin@gmail.com')),

('Mousse de chocolate con aquafaba',
 'Mousse aireado de chocolate sin huevo ni crema: el secreto es el líquido de los garbanzos.',
 30, 'Media',
 '1. Derrite el chocolate a baño María y deja que se entibie unos 10 minutos. 2. Escurre una lata de garbanzos y reserva el líquido, que es la aquafaba; los garbanzos puedes usarlos en otra receta. 3. Bate la aquafaba con la sal a velocidad alta durante 5 a 8 minutos, hasta que forme picos firmes. 4. Agrega el azúcar poco a poco sin dejar de batir. 5. Incorpora el chocolate tibio a la merengue con movimientos suaves y envolventes, sin bajar el volumen. 6. Reparte en vasos y refrigera al menos 3 horas antes de servir.',
 4, 'img/recetas/mousse-aquafaba.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'isidora@gmail.com')),

('Brownie de frijoles negros',
 'Brownie húmedo e intenso, sin harina de trigo: los frijoles negros le dan la textura.',
 50, 'Media',
 '1. Precalienta el horno a 180°C y forra un molde cuadrado con papel de horno. 2. Escurre y enjuaga muy bien los frijoles. 3. Procesa los frijoles con los huevos, el aceite y el azúcar hasta obtener una crema sin trocitos. 4. Agrega el cacao, el polvo de hornear y la sal, y procesa de nuevo. 5. Incorpora el chocolate picado con una espátula. 6. Vierte la mezcla en el molde y hornea 30 minutos. 7. Deja enfriar por completo antes de cortar: así queda más firme.',
 9, 'img/recetas/brownie-frijoles-negros.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'tomas@gmail.com')),

('Helado de plátano y cacao',
 'Helado cremoso de un solo ingrediente base: plátanos congelados, cacao y mantequilla de maní.',
 10, 'Fácil',
 '1. La noche anterior pela los plátanos maduros, córtalos en rodajas y congélalos. 2. Coloca las rodajas congeladas en una procesadora con el cacao, la mantequilla de maní y la leche de avena. 3. Procesa de 3 a 5 minutos, deteniéndote a raspar las paredes, hasta lograr una textura cremosa tipo helado. 4. Sirve de inmediato o congela 30 minutos para una textura más firme.',
 2, 'img/recetas/helado-de-platano.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'benjamin@gmail.com')),

('Matcha latte helado',
 'Bebida fresca de té matcha con leche de avena y un toque de agave.',
 5, 'Fácil',
 '1. Tamiza el matcha en un bol para evitar grumos. 2. Agrega el agua caliente, a unos 80°C y sin que hierva, y bate con un batidor hasta que quede sin grumos. 3. Llena un vaso alto con hielo. 4. Añade la leche de avena y el jarabe de agave. 5. Vierte el matcha por encima y mezcla antes de beber.',
 1, 'img/recetas/matcha-latte-helado.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'antonia@gmail.com')),

('Kombucha casera',
 'Bebida fermentada de té, ligeramente ácida y burbujeante, preparada en casa.',
 30, 'Media',
 '1. Hierve el agua, retírala del fuego e infusiona el té negro durante 10 minutos. 2. Disuelve el azúcar en el té caliente, retira las hojas y deja enfriar por completo a temperatura ambiente. 3. Vierte el té frío en un frasco de vidrio limpio y agrega la kombucha madura y el SCOBY. 4. Cubre la boca del frasco con un paño limpio sujeto con una liga. 5. Deja fermentar en un lugar tibio y sin luz directa entre 7 y 10 días, probándola desde el día 7 hasta que tenga el equilibrio de dulce y ácido que te guste. 6. Retira el SCOBY con las manos limpias, guarda una parte del líquido para la próxima tanda y refrigera el resto.',
 4, 'img/recetas/kombucha-casera.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'tomas@gmail.com')),

('Kimchi rápido de repollo',
 'Kimchi vegano y crujiente, listo para comer en 2 o 3 días de fermentación.',
 40, 'Media',
 '1. Corta el repollo en trozos de 3 a 4 cm y mézclalo con la sal, masajeándolo un par de minutos. 2. Déjalo reposar 1 hora; soltará líquido. 3. Enjuágalo 2 veces con agua fría y escúrrelo bien. 4. Prepara la pasta mezclando el ajo y el jengibre triturados con el ají en hojuelas, la salsa de soja y el azúcar. 5. Corta la zanahoria en tiras finas y el cebollín en trozos, y mézclalos con el repollo y la pasta usando guantes. 6. Pasa todo a un frasco de vidrio presionando para sacar el aire, y deja 2 cm libres arriba. 7. Deja fermentar a temperatura ambiente de 2 a 3 días, abriendo el frasco cada día para liberar gases, y luego guarda en el refrigerador.',
 8, 'img/recetas/kimchi-rapido.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'fernanda@gmail.com')),

('Socca de garbanzo',
 'Tortilla crujiente de harina de garbanzo, típica del sur de Francia, con tomates cherry y albahaca.',
 25, 'Fácil',
 '1. Mezcla la harina de garbanzo con el agua, 1 cucharada de aceite, el comino y la sal hasta que no queden grumos. 2. Deja reposar la masa 30 minutos; mientras tanto precalienta el horno a 230°C con una sartén de hierro adentro. 3. Corta los tomates cherry por la mitad y la cebolla morada en pluma. 4. Saca la sartén caliente, agrega el aceite restante y vierte la masa. 5. Hornea 12 minutos, hasta que los bordes estén dorados. 6. Cubre con los tomates, la cebolla y la albahaca fresca, y corta en porciones.',
 4, 'img/recetas/socca-de-garbanzo.jpg',
 (SELECT id_usuario FROM Usuarios WHERE email = 'joaquin@gmail.com'));


-- ---------- INGREDIENTES DE CADA RECETA ----------
INSERT INTO DetalleIngrediente (id_receta, id_ingrediente, cantidad, unidad_medida)
SELECT r.id_receta, i.id_ingrediente, d.cantidad, d.unidad_medida
FROM (
              SELECT 'Ceviche de sandía' AS receta, 'Sandía' AS ingrediente, 600 AS cantidad, 'g' AS unidad_medida
    UNION ALL SELECT 'Ceviche de sandía', 'Cebolla morada', 60, 'g'
    UNION ALL SELECT 'Ceviche de sandía', 'Limón', 4, 'unidades'
    UNION ALL SELECT 'Ceviche de sandía', 'Ají verde', 1, 'unidades'
    UNION ALL SELECT 'Ceviche de sandía', 'Cilantro', 15, 'g'
    UNION ALL SELECT 'Ceviche de sandía', 'Jengibre', 5, 'g'
    UNION ALL SELECT 'Ceviche de sandía', 'Palta', 1, 'unidades'
    UNION ALL SELECT 'Ceviche de sandía', 'Sal', 1, 'cucharaditas'
    UNION ALL SELECT 'Ceviche de sandía', 'Aceite de oliva', 1, 'cucharadas'

    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Coliflor', 600, 'g'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Piña', 200, 'g'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Tortillas de maíz', 8, 'unidades'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Pimentón ahumado', 2, 'cucharaditas'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Comino', 1, 'cucharaditas'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Ajo', 2, 'dientes'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Cebolla morada', 60, 'g'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Cilantro', 15, 'g'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Limón', 1, 'unidades'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Aceite de oliva', 3, 'cucharadas'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Vinagre de manzana', 2, 'cucharadas'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Sal', 1, 'cucharaditas'

    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Fideos de ramen', 200, 'g'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Pasta de miso', 3, 'cucharadas'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Champiñones', 200, 'g'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Espinaca', 80, 'g'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Tofu firme', 200, 'g'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Jengibre', 10, 'g'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Ajo', 2, 'dientes'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Salsa de soja', 2, 'cucharadas'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Caldo de verduras', 1000, 'ml'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Cebollín', 30, 'g'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Semillas de sésamo', 1, 'cucharadas'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Aceite de sésamo', 1, 'cucharadas'

    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Quinoa', 150, 'g'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Camote', 400, 'g'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Garbanzos cocidos', 240, 'g'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Aguacate', 1, 'unidades'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Espinaca', 80, 'g'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Limón', 1, 'unidades'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Tahini', 2, 'cucharadas'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Aceite de oliva', 2, 'cucharadas'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Pimentón ahumado', 1, 'cucharaditas'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Sal', 1, 'cucharaditas'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Agua', 300, 'ml'

    UNION ALL SELECT 'Poke bowl de salmón', 'Salmón', 300, 'g'
    UNION ALL SELECT 'Poke bowl de salmón', 'Arroz', 200, 'g'
    UNION ALL SELECT 'Poke bowl de salmón', 'Aguacate', 1, 'unidades'
    UNION ALL SELECT 'Poke bowl de salmón', 'Pepino', 100, 'g'
    UNION ALL SELECT 'Poke bowl de salmón', 'Zanahoria', 60, 'g'
    UNION ALL SELECT 'Poke bowl de salmón', 'Edamame', 100, 'g'
    UNION ALL SELECT 'Poke bowl de salmón', 'Salsa de soja', 3, 'cucharadas'
    UNION ALL SELECT 'Poke bowl de salmón', 'Aceite de sésamo', 1, 'cucharadas'
    UNION ALL SELECT 'Poke bowl de salmón', 'Semillas de sésamo', 1, 'cucharadas'
    UNION ALL SELECT 'Poke bowl de salmón', 'Limón', 1, 'unidades'
    UNION ALL SELECT 'Poke bowl de salmón', 'Cebollín', 20, 'g'

    UNION ALL SELECT 'Hummus de betarraga', 'Betarraga', 250, 'g'
    UNION ALL SELECT 'Hummus de betarraga', 'Garbanzos cocidos', 240, 'g'
    UNION ALL SELECT 'Hummus de betarraga', 'Tahini', 3, 'cucharadas'
    UNION ALL SELECT 'Hummus de betarraga', 'Limón', 1, 'unidades'
    UNION ALL SELECT 'Hummus de betarraga', 'Ajo', 1, 'dientes'
    UNION ALL SELECT 'Hummus de betarraga', 'Aceite de oliva', 2, 'cucharadas'
    UNION ALL SELECT 'Hummus de betarraga', 'Comino', 0.5, 'cucharaditas'
    UNION ALL SELECT 'Hummus de betarraga', 'Sal', 0.5, 'cucharaditas'

    UNION ALL SELECT 'Caldo de cáscaras', 'Restos de verduras', 500, 'g'
    UNION ALL SELECT 'Caldo de cáscaras', 'Ajo', 3, 'dientes'
    UNION ALL SELECT 'Caldo de cáscaras', 'Laurel', 2, 'unidades'
    UNION ALL SELECT 'Caldo de cáscaras', 'Pimienta en grano', 1, 'cucharaditas'
    UNION ALL SELECT 'Caldo de cáscaras', 'Agua', 2000, 'ml'
    UNION ALL SELECT 'Caldo de cáscaras', 'Sal', 1, 'cucharaditas'

    UNION ALL SELECT 'Pesto de hojas de zanahoria', 'Hojas de zanahoria', 60, 'g'
    UNION ALL SELECT 'Pesto de hojas de zanahoria', 'Almendras', 40, 'g'
    UNION ALL SELECT 'Pesto de hojas de zanahoria', 'Ajo', 1, 'dientes'
    UNION ALL SELECT 'Pesto de hojas de zanahoria', 'Limón', 1, 'unidades'
    UNION ALL SELECT 'Pesto de hojas de zanahoria', 'Aceite de oliva', 100, 'ml'
    UNION ALL SELECT 'Pesto de hojas de zanahoria', 'Levadura nutricional', 2, 'cucharadas'
    UNION ALL SELECT 'Pesto de hojas de zanahoria', 'Sal', 0.5, 'cucharaditas'

    UNION ALL SELECT 'Budín de pan con plátanos maduros', 'Pan duro', 300, 'g'
    UNION ALL SELECT 'Budín de pan con plátanos maduros', 'Plátano', 3, 'unidades'
    UNION ALL SELECT 'Budín de pan con plátanos maduros', 'Leche', 500, 'ml'
    UNION ALL SELECT 'Budín de pan con plátanos maduros', 'Huevos', 2, 'unidades'
    UNION ALL SELECT 'Budín de pan con plátanos maduros', 'Azúcar', 80, 'g'
    UNION ALL SELECT 'Budín de pan con plátanos maduros', 'Canela', 1, 'cucharaditas'
    UNION ALL SELECT 'Budín de pan con plátanos maduros', 'Mantequilla', 20, 'g'

    UNION ALL SELECT 'Mousse de chocolate con aquafaba', 'Aquafaba', 120, 'ml'
    UNION ALL SELECT 'Mousse de chocolate con aquafaba', 'Chocolate negro', 150, 'g'
    UNION ALL SELECT 'Mousse de chocolate con aquafaba', 'Azúcar', 30, 'g'
    UNION ALL SELECT 'Mousse de chocolate con aquafaba', 'Sal', 1, 'pizca'

    UNION ALL SELECT 'Brownie de frijoles negros', 'Frijoles negros cocidos', 400, 'g'
    UNION ALL SELECT 'Brownie de frijoles negros', 'Huevos', 3, 'unidades'
    UNION ALL SELECT 'Brownie de frijoles negros', 'Cacao en polvo', 40, 'g'
    UNION ALL SELECT 'Brownie de frijoles negros', 'Chocolate negro', 100, 'g'
    UNION ALL SELECT 'Brownie de frijoles negros', 'Azúcar', 100, 'g'
    UNION ALL SELECT 'Brownie de frijoles negros', 'Aceite de oliva', 60, 'ml'
    UNION ALL SELECT 'Brownie de frijoles negros', 'Polvo de hornear', 1, 'cucharaditas'
    UNION ALL SELECT 'Brownie de frijoles negros', 'Sal', 1, 'pizca'

    UNION ALL SELECT 'Helado de plátano y cacao', 'Plátano', 4, 'unidades'
    UNION ALL SELECT 'Helado de plátano y cacao', 'Cacao en polvo', 2, 'cucharadas'
    UNION ALL SELECT 'Helado de plátano y cacao', 'Mantequilla de maní', 2, 'cucharadas'
    UNION ALL SELECT 'Helado de plátano y cacao', 'Leche de avena', 50, 'ml'

    UNION ALL SELECT 'Matcha latte helado', 'Matcha', 2, 'cucharaditas'
    UNION ALL SELECT 'Matcha latte helado', 'Agua', 50, 'ml'
    UNION ALL SELECT 'Matcha latte helado', 'Leche de avena', 250, 'ml'
    UNION ALL SELECT 'Matcha latte helado', 'Jarabe de agave', 1, 'cucharadas'
    UNION ALL SELECT 'Matcha latte helado', 'Hielo', 150, 'g'

    UNION ALL SELECT 'Kombucha casera', 'Té negro', 8, 'g'
    UNION ALL SELECT 'Kombucha casera', 'Azúcar', 70, 'g'
    UNION ALL SELECT 'Kombucha casera', 'Agua', 1000, 'ml'
    UNION ALL SELECT 'Kombucha casera', 'SCOBY', 1, 'unidades'
    UNION ALL SELECT 'Kombucha casera', 'Kombucha madura', 100, 'ml'

    UNION ALL SELECT 'Kimchi rápido de repollo', 'Repollo chino', 1000, 'g'
    UNION ALL SELECT 'Kimchi rápido de repollo', 'Sal', 40, 'g'
    UNION ALL SELECT 'Kimchi rápido de repollo', 'Zanahoria', 100, 'g'
    UNION ALL SELECT 'Kimchi rápido de repollo', 'Cebollín', 50, 'g'
    UNION ALL SELECT 'Kimchi rápido de repollo', 'Ajo', 5, 'dientes'
    UNION ALL SELECT 'Kimchi rápido de repollo', 'Jengibre', 15, 'g'
    UNION ALL SELECT 'Kimchi rápido de repollo', 'Ají en hojuelas', 3, 'cucharadas'
    UNION ALL SELECT 'Kimchi rápido de repollo', 'Salsa de soja', 2, 'cucharadas'
    UNION ALL SELECT 'Kimchi rápido de repollo', 'Azúcar', 1, 'cucharadas'

    UNION ALL SELECT 'Socca de garbanzo', 'Harina de garbanzo', 150, 'g'
    UNION ALL SELECT 'Socca de garbanzo', 'Agua', 250, 'ml'
    UNION ALL SELECT 'Socca de garbanzo', 'Aceite de oliva', 3, 'cucharadas'
    UNION ALL SELECT 'Socca de garbanzo', 'Comino', 0.5, 'cucharaditas'
    UNION ALL SELECT 'Socca de garbanzo', 'Sal', 0.5, 'cucharaditas'
    UNION ALL SELECT 'Socca de garbanzo', 'Tomate cherry', 150, 'g'
    UNION ALL SELECT 'Socca de garbanzo', 'Cebolla morada', 40, 'g'
    UNION ALL SELECT 'Socca de garbanzo', 'Albahaca', 10, 'g'
) AS d
JOIN Recetas r      ON r.nombre = d.receta
JOIN Ingredientes i ON i.nombre = d.ingrediente;


-- ---------- CATEGORIAS DE CADA RECETA ----------
INSERT INTO RecetasCategorias (id_receta, id_categoria)
SELECT r.id_receta, c.id_categoria
FROM (
              SELECT 'Ceviche de sandía' AS receta, 'Fusión global' AS categoria
    UNION ALL SELECT 'Ceviche de sandía', 'Plant-based'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Fusión global'
    UNION ALL SELECT 'Tacos de coliflor al pastor', 'Plant-based'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Fusión global'
    UNION ALL SELECT 'Ramen vegano de miso y setas', 'Plant-based'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Bowls y ensaladas'
    UNION ALL SELECT 'Bowl de quinoa y camote asado', 'Plant-based'
    UNION ALL SELECT 'Poke bowl de salmón', 'Bowls y ensaladas'
    UNION ALL SELECT 'Poke bowl de salmón', 'Fusión global'
    UNION ALL SELECT 'Hummus de betarraga', 'Snacks saludables'
    UNION ALL SELECT 'Hummus de betarraga', 'Plant-based'
    UNION ALL SELECT 'Caldo de cáscaras', 'Cero desperdicio'
    UNION ALL SELECT 'Caldo de cáscaras', 'Plant-based'
    UNION ALL SELECT 'Pesto de hojas de zanahoria', 'Cero desperdicio'
    UNION ALL SELECT 'Pesto de hojas de zanahoria', 'Snacks saludables'
    UNION ALL SELECT 'Pesto de hojas de zanahoria', 'Plant-based'
    UNION ALL SELECT 'Budín de pan con plátanos maduros', 'Cero desperdicio'
    UNION ALL SELECT 'Budín de pan con plátanos maduros', 'Postres creativos'
    UNION ALL SELECT 'Mousse de chocolate con aquafaba', 'Postres creativos'
    UNION ALL SELECT 'Mousse de chocolate con aquafaba', 'Plant-based'
    UNION ALL SELECT 'Brownie de frijoles negros', 'Postres creativos'
    UNION ALL SELECT 'Helado de plátano y cacao', 'Postres creativos'
    UNION ALL SELECT 'Helado de plátano y cacao', 'Plant-based'
    UNION ALL SELECT 'Matcha latte helado', 'Bebidas funcionales'
    UNION ALL SELECT 'Matcha latte helado', 'Plant-based'
    UNION ALL SELECT 'Kombucha casera', 'Bebidas funcionales'
    UNION ALL SELECT 'Kombucha casera', 'Fermentados y conservas'
    UNION ALL SELECT 'Kombucha casera', 'Plant-based'
    UNION ALL SELECT 'Kimchi rápido de repollo', 'Fermentados y conservas'
    UNION ALL SELECT 'Kimchi rápido de repollo', 'Plant-based'
    UNION ALL SELECT 'Socca de garbanzo', 'Snacks saludables'
    UNION ALL SELECT 'Socca de garbanzo', 'Plant-based'
) AS d
JOIN Recetas r    ON r.nombre = d.receta
JOIN Categorias c ON c.nombre = d.categoria;


-- ---------- VALORACIONES ----------
INSERT INTO Valoraciones (puntuacion, comentario, fecha, id_usuario, id_receta)
SELECT d.puntuacion, d.comentario, d.fecha, u.id_usuario, r.id_receta
FROM (
              SELECT 5 AS puntuacion, 'Sorprendente: la sandía hace de pescado. Lo preparé para un asado y triunfó.' AS comentario, '2026-08-04' AS fecha, 'joaquin@gmail.com' AS email, 'Ceviche de sandía' AS receta
    UNION ALL SELECT 4, 'Fresco y original. Le agregué más ají y quedó perfecto.', '2026-08-19', 'tomas@gmail.com', 'Ceviche de sandía'

    UNION ALL SELECT 5, 'La coliflor queda crocante y la piña le da el toque dulce.', '2026-08-08', 'fernanda@gmail.com', 'Tacos de coliflor al pastor'
    UNION ALL SELECT 5, 'Ni se nota que no lleva carne.', '2026-08-22', 'isidora@gmail.com', 'Tacos de coliflor al pastor'
    UNION ALL SELECT 4, 'Muy ricos, la próxima vez subiría un poco el pimentón.', '2026-09-06', 'benjamin@gmail.com', 'Tacos de coliflor al pastor'

    UNION ALL SELECT 5, 'Caldo profundo y reconfortante, el miso hace toda la diferencia.', '2026-08-12', 'antonia@gmail.com', 'Ramen vegano de miso y setas'
    UNION ALL SELECT 4, 'Buenísimo. Me costó encontrar los fideos, pero valió la pena.', '2026-09-02', 'tomas@gmail.com', 'Ramen vegano de miso y setas'

    UNION ALL SELECT 4, 'Completo y sacia harto. El aderezo de tahini es lo mejor.', '2026-08-15', 'isidora@gmail.com', 'Bowl de quinoa y camote asado'
    UNION ALL SELECT 5, 'Mi almuerzo de la semana, lo preparo por adelantado.', '2026-09-10', 'benjamin@gmail.com', 'Bowl de quinoa y camote asado'

    UNION ALL SELECT 5, 'Fresco, rápido y se ve increíble en el plato.', '2026-08-17', 'tomas@gmail.com', 'Poke bowl de salmón'
    UNION ALL SELECT 4, 'Muy rico; conviene comprar el salmón el mismo día.', '2026-09-08', 'antonia@gmail.com', 'Poke bowl de salmón'

    UNION ALL SELECT 5, 'El color es espectacular y el sabor más suave que el hummus clásico.', '2026-08-21', 'fernanda@gmail.com', 'Hummus de betarraga'
    UNION ALL SELECT 4, 'Lo serví en una junta de amigos y desapareció.', '2026-09-01', 'joaquin@gmail.com', 'Hummus de betarraga'

    UNION ALL SELECT 5, 'Genial para no botar nada. Ahora guardo todo en el congelador.', '2026-08-25', 'benjamin@gmail.com', 'Caldo de cáscaras'
    UNION ALL SELECT 4, 'Simple y muy útil, me sirvió de base para varias sopas.', '2026-09-13', 'isidora@gmail.com', 'Caldo de cáscaras'

    UNION ALL SELECT 4, 'No sabía que las hojas de zanahoria se podían comer. Muy rico.', '2026-08-29', 'antonia@gmail.com', 'Pesto de hojas de zanahoria'
    UNION ALL SELECT 5, 'Increíble sobre pasta. Cero desperdicio de verdad.', '2026-09-11', 'tomas@gmail.com', 'Pesto de hojas de zanahoria'

    UNION ALL SELECT 5, 'Una forma deliciosa de usar el pan de ayer.', '2026-08-06', 'isidora@gmail.com', 'Budín de pan con plátanos maduros'
    UNION ALL SELECT 4, 'Queda muy húmedo; con un poco de manjar es un sueño.', '2026-09-04', 'benjamin@gmail.com', 'Budín de pan con plátanos maduros'

    UNION ALL SELECT 5, 'Cuesta creer que el secreto es el agua de los garbanzos.', '2026-08-31', 'fernanda@gmail.com', 'Mousse de chocolate con aquafaba'
    UNION ALL SELECT 4, 'Textura aérea. Hay que tener paciencia al batir.', '2026-09-15', 'joaquin@gmail.com', 'Mousse de chocolate con aquafaba'
    UNION ALL SELECT 5, 'Liviano e intenso a la vez, lo repetiría siempre.', '2026-09-16', 'tomas@gmail.com', 'Mousse de chocolate con aquafaba'

    UNION ALL SELECT 4, 'Húmedo y muy chocolatoso, no se siente el frijol.', '2026-08-13', 'antonia@gmail.com', 'Brownie de frijoles negros'
    UNION ALL SELECT 3, 'Rico, pero personalmente prefiero el brownie clásico.', '2026-09-07', 'benjamin@gmail.com', 'Brownie de frijoles negros'

    UNION ALL SELECT 5, 'Listo en 5 minutos y sin culpa.', '2026-08-27', 'joaquin@gmail.com', 'Helado de plátano y cacao'
    UNION ALL SELECT 4, 'Quedó cremoso; usé plátanos bien maduros y ayudó mucho.', '2026-09-12', 'fernanda@gmail.com', 'Helado de plátano y cacao'

    UNION ALL SELECT 4, 'Muy refrescante. Tamizar el matcha es clave.', '2026-08-09', 'tomas@gmail.com', 'Matcha latte helado'
    UNION ALL SELECT 5, 'Mi nueva bebida de la tarde.', '2026-09-14', 'isidora@gmail.com', 'Matcha latte helado'

    UNION ALL SELECT 4, 'Muy fácil, aunque hay que armarse de paciencia.', '2026-09-03', 'fernanda@gmail.com', 'Kombucha casera'
    UNION ALL SELECT 5, 'Me quedó burbujeante y con el punto justo de acidez.', '2026-09-18', 'antonia@gmail.com', 'Kombucha casera'

    UNION ALL SELECT 5, 'Picante, crujiente y adictivo. Ya voy en el segundo frasco.', '2026-09-05', 'tomas@gmail.com', 'Kimchi rápido de repollo'
    UNION ALL SELECT 4, 'Muy bueno, reduje el ají a la mitad.', '2026-09-16', 'joaquin@gmail.com', 'Kimchi rápido de repollo'

    UNION ALL SELECT 4, 'Crocante por fuera y suave por dentro.', '2026-08-23', 'benjamin@gmail.com', 'Socca de garbanzo'
    UNION ALL SELECT 5, 'La hice para la once y fue un éxito.', '2026-09-09', 'antonia@gmail.com', 'Socca de garbanzo'
) AS d
JOIN Usuarios u ON u.email = d.email
JOIN Recetas r  ON r.nombre = d.receta;


-- ---------- RECETAS GUARDADAS ----------
INSERT INTO RecetasGuardadas (id_usuario, id_receta, fecha_guardado)
SELECT u.id_usuario, r.id_receta, d.fecha_guardado
FROM (
              SELECT 'antonia@gmail.com' AS email, 'Ramen vegano de miso y setas' AS receta, '2026-08-12' AS fecha_guardado
    UNION ALL SELECT 'antonia@gmail.com',  'Bowl de quinoa y camote asado',    '2026-09-10'
    UNION ALL SELECT 'joaquin@gmail.com',  'Ceviche de sandía',                '2026-08-04'
    UNION ALL SELECT 'joaquin@gmail.com',  'Kimchi rápido de repollo',         '2026-09-16'
    UNION ALL SELECT 'fernanda@gmail.com', 'Tacos de coliflor al pastor',      '2026-08-08'
    UNION ALL SELECT 'fernanda@gmail.com', 'Mousse de chocolate con aquafaba', '2026-08-31'
    UNION ALL SELECT 'tomas@gmail.com',    'Hummus de betarraga',              '2026-08-24'
    UNION ALL SELECT 'tomas@gmail.com',    'Pesto de hojas de zanahoria',      '2026-09-11'
    UNION ALL SELECT 'isidora@gmail.com',  'Budín de pan con plátanos maduros','2026-08-06'
    UNION ALL SELECT 'isidora@gmail.com',  'Caldo de cáscaras',                '2026-09-13'
    UNION ALL SELECT 'benjamin@gmail.com', 'Poke bowl de salmón',              '2026-09-01'
    UNION ALL SELECT 'benjamin@gmail.com', 'Kombucha casera',                  '2026-09-19'
    UNION ALL SELECT 'benjamin@gmail.com', 'Socca de garbanzo',                '2026-09-20'
) AS d
JOIN Usuarios u ON u.email = d.email
JOIN Recetas r  ON r.nombre = d.receta;


-- ============================================
-- VERIFICACIÓN RÁPIDA
-- Resultado esperado:
-- Usuarios 6 | Categorias 8 | Ingredientes 68 | Recetas 16
-- DetalleIngrediente 126 | RecetasCategorias 33
-- Valoraciones 34 | RecetasGuardadas 13
-- ============================================

SELECT 'Usuarios' AS tabla, COUNT(*) AS filas FROM Usuarios
UNION ALL SELECT 'Categorias', COUNT(*) FROM Categorias
UNION ALL SELECT 'Ingredientes', COUNT(*) FROM Ingredientes
UNION ALL SELECT 'Recetas', COUNT(*) FROM Recetas
UNION ALL SELECT 'DetalleIngrediente', COUNT(*) FROM DetalleIngrediente
UNION ALL SELECT 'RecetasCategorias', COUNT(*) FROM RecetasCategorias
UNION ALL SELECT 'Valoraciones', COUNT(*) FROM Valoraciones
UNION ALL SELECT 'RecetasGuardadas', COUNT(*) FROM RecetasGuardadas;



-- ============================================
-- CONSULTAS DE EJEMPLO PARA LA WEB
-- (descomentar para probar los datos insertados)
-- ============================================

--1) Listado principal: recetas con promedio de valoraciones
-- SELECT * FROM vw_recetas_resumen ORDER BY promedio DESC;

-- 2) Ingredientes de una receta (página de detalle)
--  SELECT i.nombre, d.cantidad, d.unidad_medida
-- FROM DetalleIngrediente d
-- JOIN Ingredientes i ON i.id_ingrediente = d.id_ingrediente
-- WHERE d.id_receta = 1;

-- 3) Recetas de una categoría
-- SELECT r.nombre, r.tiempo_preparacion, r.dificultad
-- FROM Recetas r
--  JOIN RecetasCategorias rc ON rc.id_receta = r.id_receta
-- JOIN Categorias c ON c.id_categoria = rc.id_categoria
-- WHERE c.nombre = 'Plant-based';

-- 4) Buscar recetas por ingrediente
-- SELECT DISTINCT r.nombre
-- FROM Recetas r
-- JOIN DetalleIngrediente d ON d.id_receta = r.id_receta
-- JOIN Ingredientes i ON i.id_ingrediente = d.id_ingrediente
-- WHERE i.nombre = 'Limón';

-- 5) Filtro de recetas rápidas (20 minutos o menos)
-- SELECT nombre, tiempo_preparacion, dificultad
-- FROM Recetas
-- WHERE tiempo_preparacion <= 20
-- ORDER BY tiempo_preparacion;

-- 6) Recetas guardadas de un usuario
-- SELECT r.nombre, g.fecha_guardado
-- FROM RecetasGuardadas g
-- JOIN Recetas r ON r.id_receta = g.id_receta
-- JOIN Usuarios u ON u.id_usuario = g.id_usuario
-- WHERE u.email = 'antonia@gmail.com'
-- ORDER BY g.fecha_guardado DESC;

-- 7) Comentarios de una receta
-- SELECT u.nombre, v.puntuacion, v.comentario, v.fecha
-- FROM Valoraciones v
-- JOIN Usuarios u ON u.id_usuario = v.id_usuario
-- WHERE v.id_receta = 1
-- ORDER BY v.fecha DESC;



