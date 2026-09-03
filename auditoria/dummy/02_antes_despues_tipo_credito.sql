/* ============================================================================
   DUMMY 2 - Antes / despues de las lineas reales que hay que cambiar
   Fuente: BD_prod (produccion). Cada bloque "ANTES" es codigo textual del
   repositorio; el bloque "DESPUES" es la version propuesta.

   NO EJECUTAR EN PRODUCCION. Ilustrativo.
   ============================================================================ */


/* ----------------------------------------------------------------------------
   CASO 1 - Lista literal en un filtro
   Archivo: BD_prod/dbo.FN_CARTERA_CREDITO.UserDefinedFunction.sql
   ---------------------------------------------------------------------------- */

-- ANTES (dos listas literales, una por cartera):
--   SELECT @NR_I = COUNT(1) FROM Quiero_Confianza.PR.PR_CREDITOS
--   WHERE NUM_CREDITO = @NUM_CREDITO
--     AND NUM_DESC_TIPO_CREDITO IN (1, 3, 4, 9, 10, 11, 16, 17, 26, 4, 20, 23)
--
--   SELECT @NR_C = COUNT(1) FROM Quiero_Confianza.PR.PR_CREDITOS
--   WHERE NUM_CREDITO = @NUM_CREDITO
--     AND NUM_DESC_TIPO_CREDITO IN (12,13,14,15,28, 2,18,27, 7, 25, 5,6,19,21,22,24)
--
-- Observaciones que el catalogo corrige por construccion:
--   * el 4 esta repetido en la primera lista (sin efecto, pero indica edicion manual);
--   * el 26 (castigo individual) esta en individual y el 25 (castigo comercial)
--     en comercial: la pertenencia a segmento y la condicion de castigo estan
--     mezcladas en la misma lista, que es justo lo que separan las banderas;
--   * si un tipo nuevo no se agrega a ninguna lista, la funcion lo clasifica
--     silenciosamente como COMERCIAL (rama ELSE). Con catalogo se detecta.

-- DESPUES:
SELECT @NR_I = COUNT(1)
FROM   Quiero_Confianza.PR.PR_CREDITOS C
WHERE  C.NUM_CREDITO = @NUM_CREDITO
  AND  EXISTS (SELECT 1 FROM DUMMY.FN_TIPOS_CREDITO('SEGMENTO_INDIVIDUAL', @FECHA_PROCESO) T
               WHERE T.NUM_DESC_TIPO_CREDITO = C.NUM_DESC_TIPO_CREDITO);

SELECT @NR_C = COUNT(1)
FROM   Quiero_Confianza.PR.PR_CREDITOS C
WHERE  C.NUM_CREDITO = @NUM_CREDITO
  AND  EXISTS (SELECT 1 FROM DUMMY.FN_TIPOS_CREDITO('SEGMENTO_COMERCIAL', @FECHA_PROCESO) T
               WHERE T.NUM_DESC_TIPO_CREDITO = C.NUM_DESC_TIPO_CREDITO);

-- Se usa EXISTS y no JOIN porque EXISTS no puede multiplicar filas aunque el
-- catalogo devolviera duplicados. Regla para todo el proyecto: en un filtro,
-- EXISTS; solo se usa JOIN cuando ademas se necesita una columna del catalogo.


/* ----------------------------------------------------------------------------
   CASO 2 - Tabla temporal sembrada con una lista literal
   Archivo: BD_prod/CIERRE.SP_CMR_GEN_MES.StoredProcedure.sql
   Este es el caso mas favorable: el procedimiento YA centralizo el conjunto en
   #TIPO_CREDITOS y lo reutiliza en varios filtros. Solo cambia como se llena.
   ---------------------------------------------------------------------------- */

-- ANTES:
--   SELECT NUM_DESC_TIPO_CREDITO
--   INTO #TIPO_CREDITOS
--   FROM Quiero_Confianza.PR.PR_DESC_TIPOS_CREDITO
--   WHERE COD_EMPRESA = '001' AND NUM_DESC_TIPO_CREDITO IN (
--            12,13,14,15,28 -- minoristas
--           ,2,18,27        -- puente
--           --,7              -- sindicada
--           ,25             -- castigo
--           ,5              -- mezzanine
--           ,6,19,21,22,24) -- administrada
--
-- Los comentarios de esta lista son el origen de las banderas del dummy 1.
-- El "--,7" comentado es exactamente el problema: sacar la cartera sindicada
-- del cierre comercial fue un cambio de codigo, sin fecha, sin autor visible
-- y sin registro de por que. Con el catalogo es un cierre de vigencia con
-- usuario, fecha y motivo.

-- DESPUES:
SELECT T.NUM_DESC_TIPO_CREDITO
INTO   #TIPO_CREDITOS
FROM   DUMMY.FN_TIPOS_CREDITO('SEGMENTO_COMERCIAL', @FECHA_PROCESO) T;

-- Los ~14 filtros posteriores del procedimiento NO se tocan:
--   AND C.NUM_DESC_TIPO_CREDITO IN (SELECT NUM_DESC_TIPO_CREDITO FROM #TIPO_CREDITOS)
-- Es el patron que conviene generalizar: sembrar una vez el conjunto vigente al
-- inicio del procedimiento y filtrar contra la temporal, para no invocar el
-- catalogo decenas de veces ni depender de la conexion al origen en cada filtro.


/* ----------------------------------------------------------------------------
   CASO 3 - Lista literal que ademas escribe valores literales
   Archivo: BD_prod/PO.SP_IND_CASTIGOS_CONDONACION.StoredProcedure.sql
   ---------------------------------------------------------------------------- */

-- ANTES:
--   UPDATE H SET
--       H.ID_PRODUCTO = 51,
--       H.NOMBRE_PRODUCTO = 'EMPLEADO'
--   FROM PO.SAF_MOV_ABONO H
--   INNER JOIN Quiero_Confianza.PR.PR_CREDITOS GG ON GG.NUM_CREDITO = H.NUM_CREDITO
--   WHERE GG.NUM_DESC_TIPO_CREDITO IN (9, 10, 11)
--     AND FECHA_MOVIMIENTO = @FECHA_INICIO AND H.ID_POLIZA = @ID_POLIZA
--
-- Aqui hay DOS hardcodeos de naturaleza distinta y no se resuelven igual:
--   (a) el conjunto (9,10,11)  -> pertenencia: va al catalogo, lo administra negocio;
--   (b) ID_PRODUCTO = 51 y 'EMPLEADO' -> atributo de salida: va al catalogo de
--       producto, y su cambio afecta la contabilidad, asi que requiere
--       aprobacion de contabilidad, no autoservicio.

-- DESPUES:
UPDATE H
   SET H.ID_PRODUCTO     = P.ID_PRODUCTO,
       H.NOMBRE_PRODUCTO = P.NOMBRE_PRODUCTO
FROM   PO.SAF_MOV_ABONO H
JOIN   Quiero_Confianza.PR.PR_CREDITOS GG ON GG.NUM_CREDITO = H.NUM_CREDITO
CROSS  APPLY (SELECT ID_PRODUCTO, NOMBRE_PRODUCTO
              FROM   DUMMY.CAT_PRODUCTO_POR_BANDERA
              WHERE  BANDERA = 'ES_EMPLEADO'
                AND  @FECHA_INICIO BETWEEN VIGENCIA_DESDE AND VIGENCIA_HASTA) P
WHERE  EXISTS (SELECT 1 FROM DUMMY.FN_TIPOS_CREDITO('ES_EMPLEADO', @FECHA_INICIO) T
               WHERE T.NUM_DESC_TIPO_CREDITO = GG.NUM_DESC_TIPO_CREDITO)
  AND  H.FECHA_MOVIMIENTO = @FECHA_INICIO
  AND  H.ID_POLIZA = @ID_POLIZA;


/* ----------------------------------------------------------------------------
   CASO 4 - Lista compuesta (union de dos segmentos)
   Archivo: BD_prod/PO.SP_IND_TRASPASO_SALDO_FAVOR.StoredProcedure.sql
   ---------------------------------------------------------------------------- */

-- ANTES:
--   WHERE NUM_DESC_TIPO_CREDITO IN (1, 3, 4, 9, 10, 11, 16, 17, 2,12,13,14,15,28)
--   --complemento con los num_desc de comercial

-- DESPUES (sin inventar una bandera nueva: se piden las dos):
WHERE EXISTS (SELECT 1
              FROM  DUMMY.CAT_TIPO_CREDITO_BANDERA B
              WHERE B.NUM_DESC_TIPO_CREDITO = C.NUM_DESC_TIPO_CREDITO
                AND B.BANDERA IN ('SEGMENTO_INDIVIDUAL','SEGMENTO_COMERCIAL')
                AND @FECHA_PROCESO BETWEEN B.VIGENCIA_DESDE AND B.VIGENCIA_HASTA);

-- Regla de diseno: no se crea una bandera por cada combinacion que aparezca en
-- el codigo (eso reproduciria las 34 listas de hoy en forma de catalogo). Las
-- banderas son conceptos de negocio; las combinaciones se expresan en la
-- consulta con IN sobre la matriz.


/* ----------------------------------------------------------------------------
   CASO 5 - Lo que NO se parametriza
   ---------------------------------------------------------------------------- */

-- BD_prod/dbo.FN_CARTERA_CREDITO.UserDefinedFunction.sql
--   IF @NR_C > 0 SET @CARTERA = 'COMERCIAL'
--   ELSE IF @NR_I > 0 SET @CARTERA = 'INDIVIDUAL'
--   ELSE SET @CARTERA = 'COMERCIAL'
--
-- La precedencia (comercial gana si el credito cae en ambos) y el valor por
-- omision son REGLA CONTABLE, no pertenencia. Quedan en codigo y bajo control
-- de cambios. El unico ajuste recomendado es que el ELSE final no devuelva
-- 'COMERCIAL' de forma silenciosa: si un tipo no esta en ninguna bandera de
-- segmento, es un hueco de configuracion y debe registrarse en
-- PO.SAF_POLIZA_ERRORES para que el portal lo muestre como pendiente.
