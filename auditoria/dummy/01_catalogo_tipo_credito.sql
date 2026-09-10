/* ============================================================================
   DUMMY 1 - Catalogo de tipos de credito con banderas por proceso
   Hallazgo que remedia: L2-018 (listas IN(...) de NUM_DESC_TIPO_CREDITO)

   NO EJECUTAR EN PRODUCCION. Todo se crea en el esquema DUMMY para que pueda
   correrse en QA/CUA sobre una copia y compararse contra el comportamiento
   actual sin tocar ningun objeto existente.

   Idea central: el catalogo YA EXISTE (PO.SAF_CAT_DESC_TIPO, 29 tipos) pero
   hoy solo se usa como diccionario de descripciones. No se agrega un catalogo
   nuevo: se le agrega la matriz de banderas y se convierte en la fuente de la
   decision. Son 29 tipos x ~12 banderas, no un registro por poliza.
   ============================================================================ */

IF SCHEMA_ID(N'DUMMY') IS NULL EXEC(N'CREATE SCHEMA DUMMY');
GO

/* --------------------------------------------------------------- 1. Catalogo
   Reflejo del catalogo real. En el despliegue definitivo esta tabla NO se
   duplica: se usa PO.SAF_CAT_DESC_TIPO tal como esta.                        */
CREATE TABLE DUMMY.CAT_TIPO_CREDITO (
    NUM_DESC_TIPO_CREDITO INT          NOT NULL PRIMARY KEY,
    DESC_TIPO_CREDITO     VARCHAR(255) NULL,
    IND_ACTIVO            BIT          NOT NULL CONSTRAINT DF_CTC_ACT DEFAULT (1)
);
GO

/* ------------------------------------------------- 2. Catalogo de banderas
   Una fila por bandera, no por tipo. El portal la presenta como una lista de
   reglas con su dueno; el operador no la edita, solo la consulta.            */
CREATE TABLE DUMMY.CAT_BANDERA (
    BANDERA     VARCHAR(40)  NOT NULL PRIMARY KEY,
    DESCRIPCION VARCHAR(300) NOT NULL,
    AREA_DUENA  VARCHAR(40)  NOT NULL      -- responde Q14/Q31 del cuestionario
);
GO

/* ------------------------------------------------------ 3. Matriz con vigencia
   Solo se almacenan las combinaciones marcadas. Con las 12 banderas derivadas
   del codigo actual son ~70 filas para los 28 tipos: es la matriz de casillas
   que ve el usuario en el portal, no un registro por poliza.

   VIGENCIA_DESDE / VIGENCIA_HASTA permiten que un tipo entre o salga de un
   proceso en una fecha sin reprocesar el historico: el cierre de ayer sigue
   viendo la matriz de ayer.                                                  */
CREATE TABLE DUMMY.CAT_TIPO_CREDITO_BANDERA (
    NUM_DESC_TIPO_CREDITO INT         NOT NULL,
    BANDERA               VARCHAR(40) NOT NULL,
    VIGENCIA_DESDE        DATE        NOT NULL,
    VIGENCIA_HASTA        DATE        NOT NULL CONSTRAINT DF_CTCB_HASTA DEFAULT ('99991231'),
    USUARIO_ALTA          SYSNAME     NOT NULL CONSTRAINT DF_CTCB_USR DEFAULT (SUSER_SNAME()),
    FECHA_ALTA            DATETIME2(0) NOT NULL CONSTRAINT DF_CTCB_FEC DEFAULT (SYSDATETIME()),
    CONSTRAINT PK_CTCB PRIMARY KEY (NUM_DESC_TIPO_CREDITO, BANDERA, VIGENCIA_DESDE),
    CONSTRAINT FK_CTCB_TIPO    FOREIGN KEY (NUM_DESC_TIPO_CREDITO) REFERENCES DUMMY.CAT_TIPO_CREDITO (NUM_DESC_TIPO_CREDITO),
    CONSTRAINT FK_CTCB_BANDERA FOREIGN KEY (BANDERA)               REFERENCES DUMMY.CAT_BANDERA (BANDERA),
    CONSTRAINT CK_CTCB_VIG     CHECK (VIGENCIA_DESDE <= VIGENCIA_HASTA)
);
GO

/* ------------------------------------------- 3b. Atributos de salida por bandera
   Los literales que hoy se ESCRIBEN junto a la lista (ID_PRODUCTO = 51,
   NOMBRE_PRODUCTO = 'EMPLEADO') no son pertenencia sino atributo de salida:
   viven en su propia tabla, con una fila por bandera y vigencia, y su cambio
   requiere aprobacion de contabilidad (no autoservicio de negocio).           */
CREATE TABLE DUMMY.CAT_PRODUCTO_POR_BANDERA (
    BANDERA         VARCHAR(40) NOT NULL,
    ID_PRODUCTO     INT         NOT NULL,
    NOMBRE_PRODUCTO VARCHAR(60) NOT NULL,
    VIGENCIA_DESDE  DATE        NOT NULL,
    VIGENCIA_HASTA  DATE        NOT NULL CONSTRAINT DF_CPB_HASTA DEFAULT ('99991231'),
    CONSTRAINT PK_CPB PRIMARY KEY (BANDERA, VIGENCIA_DESDE),
    CONSTRAINT FK_CPB_BANDERA FOREIGN KEY (BANDERA) REFERENCES DUMMY.CAT_BANDERA (BANDERA),
    CONSTRAINT CK_CPB_VIG     CHECK (VIGENCIA_DESDE <= VIGENCIA_HASTA)
);
GO

/* -------------------------------------------------------------- 4. Resolvedor
   Funcion en linea (inline TVF): el optimizador la expande dentro de la
   consulta, asi que el plan es equivalente a un JOIN y no repite el problema
   de las funciones escalares fila por fila del hallazgo L6-005.              */
CREATE FUNCTION DUMMY.FN_TIPOS_CREDITO (@BANDERA VARCHAR(40), @FECHA DATE)
RETURNS TABLE
AS RETURN
(
    SELECT B.NUM_DESC_TIPO_CREDITO
    FROM   DUMMY.CAT_TIPO_CREDITO_BANDERA B
    JOIN   DUMMY.CAT_TIPO_CREDITO         T ON T.NUM_DESC_TIPO_CREDITO = B.NUM_DESC_TIPO_CREDITO
    WHERE  B.BANDERA = @BANDERA
      AND  @FECHA BETWEEN B.VIGENCIA_DESDE AND B.VIGENCIA_HASTA
      AND  T.IND_ACTIVO = 1
);
GO

/* ============================ SEMILLA ======================================
   Los 28 tipos y las 12 banderas se derivan literalmente de los predicados
   del codigo de BD_prod: son los valores que aparecen en algun filtro sobre
   NUM_DESC_TIPO_CREDITO (falta el 8, que no aparece en ningun predicado).
   Las descripciones y la carga real de tipos viven en PO.SAF_CAT_DESC_TIPO;
   aqui van en NULL porque el repositorio no incluye datos. En la instancia
   real esta semilla se sustituye por:
     INSERT INTO DUMMY.CAT_TIPO_CREDITO (NUM_DESC_TIPO_CREDITO, DESC_TIPO_CREDITO)
     SELECT NUM_DESC_TIPO_CREDITO, DESC_TIPO_CREDITO
     FROM   PO.SAF_CAT_DESC_TIPO WHERE IND_ACTIVO = 1;                       */

INSERT INTO DUMMY.CAT_TIPO_CREDITO (NUM_DESC_TIPO_CREDITO)
VALUES (1),(2),(3),(4),(5),(6),(7),(9),(10),(11),(12),(13),(14),(15),(16),(17),
       (18),(19),(20),(21),(22),(23),(24),(25),(26),(27),(28),(29);
GO

INSERT INTO DUMMY.CAT_BANDERA (BANDERA, DESCRIPCION, AREA_DUENA) VALUES
 /* El conteo de cada descripcion es el numero de filtros de BD_prod cuyo
    conjunto contiene por completo el grupo de la bandera, medido con
    auditoria/dummy/06_medir_esfuerzo.py. */
 ('SEGMENTO_INDIVIDUAL',       'Participa en las polizas individuales. Hoy: IN (1,3,4,9,10,11,16,17) en 33 filtros de 26 archivos.', 'Contabilidad'),
 ('SEGMENTO_COMERCIAL',        'Participa en las polizas comerciales. Hoy: IN (2,12,13,14,15,18,27,28) en 50 filtros de 30 archivos.', 'Contabilidad'),
 ('SEGMENTO_SINDICADA',        'Participa en las polizas de cartera sindicada. Hoy: el 7, presente en 24 filtros de 17 archivos.', 'Negocio'),
 ('ES_MINORISTA',              'Tipo minorista. Hoy: 12,13,14,15,28, etiquetado como "minoristas" en CIERRE.SP_CMR_GEN_MES; 51 filtros en 31 archivos.', 'Negocio'),
 ('ES_PUENTE',                 'Credito puente. Hoy: 2,18,27, etiquetado como "puente" en CIERRE.SP_CMR_GEN_MES; 50 filtros en 30 archivos.', 'Negocio'),
 ('ES_MEZZANINE',              'Tipo mezzanine. Hoy: el 5, presente en 24 de los 50 filtros comerciales.', 'Negocio'),
 ('ES_EMPLEADO',               'Credito a empleado. Hoy: IN (9,10,11) en 66 filtros de 38 archivos; fuerza ID_PRODUCTO=51 y NOMBRE_PRODUCTO=EMPLEADO.', 'Negocio'),
 ('ES_ADMINISTRADA_IND',       'Cartera administrada individual. Hoy: IN (4,20,23) en 4 filtros, entre ellos PO.SP_IND_ADMINISTRADA.', 'Negocio'),
 ('ES_ADMINISTRADA_COM',       'Cartera administrada comercial. Hoy: IN (6,19,21,22,24) en 7 filtros, etiquetado como "administrada".', 'Negocio'),
 ('ES_CASTIGO_COMERCIAL',      'Tipo de castigo comercial. Hoy: IN (25,29) en 16 filtros de 11 archivos.', 'Contabilidad'),
 ('ES_CASTIGO_INDIVIDUAL',     'Tipo de castigo individual. Hoy: el 26, presente en 16 filtros de 14 archivos.', 'Contabilidad'),
 ('ES_ADMON_AFIRME',           'Cartera en administracion Afirme, sujeta a factor de participacion. Hoy: = 4 y la cadena ADMINISTRACION INDIVIDUAL.', 'Negocio');
GO

DECLARE @D DATE = '19000101';

INSERT INTO DUMMY.CAT_TIPO_CREDITO_BANDERA (NUM_DESC_TIPO_CREDITO, BANDERA, VIGENCIA_DESDE)
SELECT V.T, V.B, @D
FROM (VALUES
  -- SEGMENTO_INDIVIDUAL: IN (1, 3, 4, 9, 10, 11, 16, 17)
  (1,'SEGMENTO_INDIVIDUAL'),(3,'SEGMENTO_INDIVIDUAL'),(4,'SEGMENTO_INDIVIDUAL'),(9,'SEGMENTO_INDIVIDUAL'),
  (10,'SEGMENTO_INDIVIDUAL'),(11,'SEGMENTO_INDIVIDUAL'),(16,'SEGMENTO_INDIVIDUAL'),(17,'SEGMENTO_INDIVIDUAL'),
  -- SEGMENTO_COMERCIAL: IN (12,13,14,15,28, 2,18,27)
  (2,'SEGMENTO_COMERCIAL'),(12,'SEGMENTO_COMERCIAL'),(13,'SEGMENTO_COMERCIAL'),(14,'SEGMENTO_COMERCIAL'),
  (15,'SEGMENTO_COMERCIAL'),(18,'SEGMENTO_COMERCIAL'),(27,'SEGMENTO_COMERCIAL'),(28,'SEGMENTO_COMERCIAL'),
  -- SEGMENTO_SINDICADA: = 7
  (7,'SEGMENTO_SINDICADA'),
  -- ES_MINORISTA / ES_PUENTE / ES_MEZZANINE
  (12,'ES_MINORISTA'),(13,'ES_MINORISTA'),(14,'ES_MINORISTA'),(15,'ES_MINORISTA'),(28,'ES_MINORISTA'),
  (2,'ES_PUENTE'),(18,'ES_PUENTE'),(27,'ES_PUENTE'),
  (5,'ES_MEZZANINE'),(5,'SEGMENTO_COMERCIAL'),
  -- ES_EMPLEADO: IN (9,10,11)
  (9,'ES_EMPLEADO'),(10,'ES_EMPLEADO'),(11,'ES_EMPLEADO'),
  -- administradas
  (4,'ES_ADMINISTRADA_IND'),(20,'ES_ADMINISTRADA_IND'),(23,'ES_ADMINISTRADA_IND'),
  (6,'ES_ADMINISTRADA_COM'),(19,'ES_ADMINISTRADA_COM'),(21,'ES_ADMINISTRADA_COM'),
  (22,'ES_ADMINISTRADA_COM'),(24,'ES_ADMINISTRADA_COM'),
  -- castigos
  (25,'ES_CASTIGO_COMERCIAL'),(29,'ES_CASTIGO_COMERCIAL'),(26,'ES_CASTIGO_INDIVIDUAL'),
  -- participacion
  (4,'ES_ADMON_AFIRME')
) V(T, B);
GO

INSERT INTO DUMMY.CAT_PRODUCTO_POR_BANDERA
       (BANDERA, ID_PRODUCTO, NOMBRE_PRODUCTO, VIGENCIA_DESDE)
VALUES ('ES_EMPLEADO', 51, 'EMPLEADO', '19000101');
GO

/* Ejemplo de alta de un tipo nuevo, que hoy exige tocar codigo y liberar:
   INSERT DUMMY.CAT_TIPO_CREDITO (NUM_DESC_TIPO_CREDITO, DESC_TIPO_CREDITO) VALUES (30, 'PMP-ADQ-VERDE');
   INSERT DUMMY.CAT_TIPO_CREDITO_BANDERA (NUM_DESC_TIPO_CREDITO, BANDERA, VIGENCIA_DESDE)
   VALUES (30,'SEGMENTO_COMERCIAL','20260401'), (30,'ES_MINORISTA','20260401');
   Cero cambios de codigo, cero liberaciones, y el cierre del 31/03 no se altera. */

/* Contraste de mantenimiento con el estado actual (medido sobre BD_prod con
   auditoria/dummy/06_medir_esfuerzo.py): 239 filtros sobre
   NUM_DESC_TIPO_CREDITO en 96 archivos, 29 conjuntos distintos y 625
   ocurrencias del campo. Con el catalogo, el alta de un tipo es un INSERT y
   unas casillas en el portal.                                                */
