/* ============================================================================
   DUMMY 5 - Prueba de equivalencia antes de sustituir cualquier objeto
   Se corre en QA/CUA. Regla del proyecto: ningun objeto parametrizado entra a
   produccion sin este resultado firmado.
   NO EJECUTAR EN PRODUCCION.
   ============================================================================ */

DECLARE @FECHA DATE = '20260228';   -- un dia habil ya cerrado y conciliado

/* ---------------------------------------------------------- A. Reporte cobranza
   Comparacion en los dos sentidos: EXCEPT solo en un sentido oculta filas
   sobrantes en el nuevo.                                                     */
CREATE TABLE #ACT (CARTERA VARCHAR(80), SECUENCIA VARCHAR(60), ID_EXTERNO VARCHAR(60),
    CLASIFICACION_DE_VIVIENDA VARCHAR(60), RESTRINGIDO VARCHAR(20), CEDIDO VARCHAR(20),
    ESTATUS VARCHAR(20), CONCEPTO VARCHAR(40), BANCO VARCHAR(80), TIPO_CREDITO VARCHAR(20),
    FECHA_MOVIMIENTO DATE, PRINCIPAL MONEY, INTERESES MONEY, IVA_INTERESES MONEY,
    SEGURO_DANOS MONEY, IVA_SEGURO_DANOS MONEY, SEGURO_VIDA MONEY,
    COMISION_ADMINISTRACION MONEY, IVA_COMISION_ADMINISTRACION MONEY, MORATORIOS MONEY,
    IVA_MORATORIOS MONEY, SALDO_FAVOR MONEY, OTRO MONEY, IVA_OTRO MONEY, TOTAL MONEY,
    ETAPA INT, IND_COVID CHAR(1));
CREATE TABLE #NEW (CARTERA VARCHAR(80), SECUENCIA VARCHAR(60), ID_EXTERNO VARCHAR(60),
    CLASIFICACION_DE_VIVIENDA VARCHAR(60), RESTRINGIDO VARCHAR(20), CEDIDO VARCHAR(20),
    ESTATUS VARCHAR(20), CONCEPTO VARCHAR(40), BANCO VARCHAR(80), TIPO_CREDITO VARCHAR(20),
    FECHA_MOVIMIENTO DATE, PRINCIPAL MONEY, INTERESES MONEY, IVA_INTERESES MONEY,
    SEGURO_DANOS MONEY, IVA_SEGURO_DANOS MONEY, SEGURO_VIDA MONEY,
    COMISION_ADMINISTRACION MONEY, IVA_COMISION_ADMINISTRACION MONEY, MORATORIOS MONEY,
    IVA_MORATORIOS MONEY, SALDO_FAVOR MONEY, OTRO MONEY, IVA_OTRO MONEY, TOTAL MONEY,
    ETAPA INT, IND_COVID CHAR(1));

INSERT INTO #ACT EXEC dbo.REPORTE_COBRANZA_INTEGRACION @FECHA;
INSERT INTO #NEW EXEC DUMMY.REPORTE_COBRANZA_INTEGRACION_V2 @FECHA;

SELECT 'FALTA_EN_NUEVO' AS DIFERENCIA, * FROM (SELECT * FROM #ACT EXCEPT SELECT * FROM #NEW) D
UNION ALL
SELECT 'SOBRA_EN_NUEVO', * FROM (SELECT * FROM #NEW EXCEPT SELECT * FROM #ACT) D;

-- Resumen por columna: donde esta la diferencia y de que tamano
SELECT  'PRINCIPAL' AS COLUMNA, SUM(A.PRINCIPAL) AS ACTUAL, SUM(N.PRINCIPAL) AS NUEVO,
        SUM(N.PRINCIPAL) - SUM(A.PRINCIPAL) AS DELTA
FROM #ACT A CROSS JOIN #NEW N
UNION ALL SELECT 'OTRO',     SUM(A.OTRO),     SUM(N.OTRO),     SUM(N.OTRO)     - SUM(A.OTRO)     FROM #ACT A CROSS JOIN #NEW N
UNION ALL SELECT 'IVA_OTRO', SUM(A.IVA_OTRO), SUM(N.IVA_OTRO), SUM(N.IVA_OTRO) - SUM(A.IVA_OTRO) FROM #ACT A CROSS JOIN #NEW N
UNION ALL SELECT 'TOTAL',    SUM(A.TOTAL),    SUM(N.TOTAL),    SUM(N.TOTAL)    - SUM(A.TOTAL)    FROM #ACT A CROSS JOIN #NEW N;

/* Criterio de aceptacion:
     TOTAL, PRINCIPAL, INTERESES, MORATORIOS, SEGUROS: delta = 0.
     OTRO / IVA_OTRO: delta distinta de 0 esperada por la correccion del defecto
     de 'IVA COMISION_ANTICIPADA'; se documenta el monto y lo firma contabilidad.
   Cualquier otra diferencia detiene el cambio.                                */
DROP TABLE #ACT; DROP TABLE #NEW;
GO


/* ------------------------------------- B. Catalogo de tipos contra el codigo
   Verifica que la matriz de banderas reproduce exactamente las listas literales
   que hoy viven en el codigo. Se corre una vez por bandera migrada.           */
DECLARE @FECHA2 DATE = SYSDATETIME();

SELECT 'SOBRA_EN_CATALOGO' AS DIFERENCIA, T.NUM_DESC_TIPO_CREDITO
FROM  DUMMY.FN_TIPOS_CREDITO('SEGMENTO_INDIVIDUAL', @FECHA2) T
WHERE T.NUM_DESC_TIPO_CREDITO NOT IN (1, 3, 4, 9, 10, 11, 16, 17)
UNION ALL
SELECT 'FALTA_EN_CATALOGO', V.N
FROM (VALUES (1),(3),(4),(9),(10),(11),(16),(17)) V(N)
WHERE V.N NOT IN (SELECT NUM_DESC_TIPO_CREDITO FROM DUMMY.FN_TIPOS_CREDITO('SEGMENTO_INDIVIDUAL', @FECHA2));
-- Resultado exigido: cero filas. Se repite con cada una de las 12 banderas.
GO


/* ------------------------------------------- C. Integridad de configuracion
   Se ejecuta despues de cada cambio hecho desde el portal, antes de aplicarlo. */

-- C1. Tipos activos sin segmento: quedarian fuera de todas las polizas.
SELECT T.NUM_DESC_TIPO_CREDITO, 'SIN_SEGMENTO' AS PROBLEMA
FROM   DUMMY.CAT_TIPO_CREDITO T
WHERE  T.IND_ACTIVO = 1
  AND  NOT EXISTS (SELECT 1 FROM DUMMY.CAT_TIPO_CREDITO_BANDERA B
                   WHERE B.NUM_DESC_TIPO_CREDITO = T.NUM_DESC_TIPO_CREDITO
                     AND B.BANDERA IN ('SEGMENTO_INDIVIDUAL','SEGMENTO_COMERCIAL','SEGMENTO_SINDICADA')
                     AND CAST(SYSDATETIME() AS DATE) BETWEEN B.VIGENCIA_DESDE AND B.VIGENCIA_HASTA);

-- C2. Tipos en dos segmentos a la vez: hoy la precedencia es implicita
--     (dbo.FN_CARTERA_CREDITO privilegia COMERCIAL). Debe ser excepcion.
SELECT B.NUM_DESC_TIPO_CREDITO, COUNT(*) AS SEGMENTOS
FROM   DUMMY.CAT_TIPO_CREDITO_BANDERA B
WHERE  B.BANDERA IN ('SEGMENTO_INDIVIDUAL','SEGMENTO_COMERCIAL','SEGMENTO_SINDICADA')
  AND  CAST(SYSDATETIME() AS DATE) BETWEEN B.VIGENCIA_DESDE AND B.VIGENCIA_HASTA
GROUP BY B.NUM_DESC_TIPO_CREDITO
HAVING COUNT(*) > 1;

-- C3. Vigencias traslapadas de la misma bandera: producirian filas duplicadas
--     si se usara JOIN en lugar de EXISTS.
SELECT A.NUM_DESC_TIPO_CREDITO, A.BANDERA
FROM   DUMMY.CAT_TIPO_CREDITO_BANDERA A
JOIN   DUMMY.CAT_TIPO_CREDITO_BANDERA B
         ON  B.NUM_DESC_TIPO_CREDITO = A.NUM_DESC_TIPO_CREDITO
         AND B.BANDERA = A.BANDERA
         AND B.VIGENCIA_DESDE > A.VIGENCIA_DESDE
         AND B.VIGENCIA_DESDE <= A.VIGENCIA_HASTA;

-- C4. Rubros de grupo OTRO sin su contraparte de IVA (o al reves).
SELECT R.RUBRO, 'IVA_FALTANTE' AS PROBLEMA
FROM   DUMMY.CAT_RUBRO R
WHERE  R.ES_IVA = 0
  AND  R.GRUPO <> 'SALDO_FAVOR' AND R.GRUPO <> 'PRINCIPAL' AND R.GRUPO <> 'SEGURO_VIDA'
  AND  NOT EXISTS (SELECT 1 FROM DUMMY.CAT_RUBRO I WHERE I.RUBRO = 'IVA ' + R.RUBRO);

-- C5. Un dia de movimientos no puede tener rubros fuera del catalogo.
--     Es la consulta que el portal ejecuta cada manana como semaforo.
GO
