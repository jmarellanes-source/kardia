/* ============================================================================
   DUMMY 4 - dbo.REPORTE_COBRANZA_INTEGRACION reescrito contra los catalogos
   Version demostrativa en el esquema DUMMY. NO EJECUTAR EN PRODUCCION.

   Equivalencias con el procedimiento actual:
     * las 39 listas de rubro       -> DUMMY.CAT_RUBRO (GRUPO / ES_IVA)
     * los 26 predicados ID_POLIZA  -> DUMMY.CAT_POLIZA_COBRANZA
     * "monto * 9" / "monto * 1"    -> DUMMY.CAT_PARTICIPACION (FACTOR)
     * los dos bloques UNION ALL    -> las dos filas VISTA del catalogo

   Las columnas de salida, su orden y su nombre NO cambian: es el contrato con
   el consumidor del reporte. Lo unico que cambia es de donde salen las reglas.
   ============================================================================ */

CREATE PROCEDURE DUMMY.REPORTE_COBRANZA_INTEGRACION_V2
    @fechaMovimiento DATE
AS
BEGIN
    SET NOCOUNT ON;

    /* 1. Reglas vigentes a la fecha del movimiento. Se resuelven una sola vez:
          si manana cambia el catalogo, reejecutar este dia sigue dando lo mismo. */
    DECLARE @POLIZAS TABLE (
        ID_POLIZA INT PRIMARY KEY, ETIQUETA_CARTERA VARCHAR(40),
        TIPO_CREDITO_REPORT VARCHAR(20), USA_TIPO_VIVIENDA BIT, SUFIJO_EN_BLANCO BIT);

    INSERT INTO @POLIZAS
    SELECT ID_POLIZA, ETIQUETA_CARTERA, TIPO_CREDITO_REPORT, USA_TIPO_VIVIENDA, SUFIJO_EN_BLANCO
    FROM   DUMMY.CAT_POLIZA_COBRANZA
    WHERE  INCLUIR_EN_REPORTE = 1
      AND  @fechaMovimiento BETWEEN VIGENCIA_DESDE AND VIGENCIA_HASTA;

    /* 2. Movimientos anotados con su grupo de rubro y su factor por vista.
          Un movimiento aparece una vez por vista aplicable, que es exactamente
          lo que hoy producen los dos bloques del UNION ALL.                    */
    ;WITH MOV AS (
        SELECT  H.ID_POLIZA, H.ID_SECUENCIA, H.ID_EXTERNO, H.TIPO_VIVIENDA, H.TIPO_CREDITO,
                H.ID_FONDEO, H.CEDIDO, H.IND_ETAPA, H.CONCEPTO_ANT, H.BANCO_RECEPTOR,
                H.FECHA_MOVIMIENTO, H.MONTO, H.RUBRO, ISNULL(H.IND_COVID,'N') AS IND_COVID
        FROM    PO.SAF_MOV_ABONO H
        WHERE   H.FECHA_MOVIMIENTO = @fechaMovimiento
          AND   H.ID_SECUENCIA IS NOT NULL
          AND   H.MONTO > 0
          AND   NOT (H.CONCEPTO LIKE 'TRS %' OR H.CONCEPTO LIKE 'PAGO CCO %')
          AND   EXISTS (SELECT 1 FROM @POLIZAS P WHERE P.ID_POLIZA = H.ID_POLIZA)
    ),
    ANOTADO AS (
        SELECT  M.*,
                PA.VISTA, PA.FACTOR, PA.ETIQUETA,
                R.GRUPO, R.ES_IVA
        FROM    MOV M
        JOIN    DUMMY.CAT_PARTICIPACION PA
                  ON  @fechaMovimiento BETWEEN PA.VIGENCIA_DESDE AND PA.VIGENCIA_HASTA
                  AND (PA.TIPO_CREDITO = M.TIPO_CREDITO
                       OR (PA.TIPO_CREDITO = '*'
                           AND NOT EXISTS (SELECT 1 FROM DUMMY.CAT_PARTICIPACION X
                                           WHERE X.VISTA = PA.VISTA AND X.TIPO_CREDITO = M.TIPO_CREDITO
                                             AND @fechaMovimiento BETWEEN X.VIGENCIA_DESDE AND X.VIGENCIA_HASTA)))
        LEFT JOIN DUMMY.CAT_RUBRO R
                  ON  R.RUBRO = M.RUBRO
                  AND @fechaMovimiento BETWEEN R.VIGENCIA_DESDE AND R.VIGENCIA_HASTA
    )
    SELECT
        P.ETIQUETA_CARTERA
          + CASE WHEN A.ETIQUETA <> '' THEN A.ETIQUETA
                 WHEN P.SUFIJO_EN_BLANCO = 1 THEN ''
                 ELSE ISNULL(A.TIPO_CREDITO,'') END                        AS CARTERA,
        A.ID_SECUENCIA                                                     AS SECUENCIA,
        MAX(A.ID_EXTERNO)                                                  AS ID_EXTERNO,
        CASE WHEN P.USA_TIPO_VIVIENDA = 1 THEN MAX(A.TIPO_VIVIENDA)
             ELSE A.TIPO_CREDITO END                                       AS CLASIFICACION_DE_VIVIENDA,
        MAX(CASE WHEN A.ID_FONDEO = 2 THEN 'NO RESTRINGIDO' ELSE 'RESTRINGIDO' END) AS RESTRINGIDO,
        MAX(A.CEDIDO)                                                      AS CEDIDO,
        MAX(CASE WHEN A.IND_ETAPA IN (1,2) THEN 'VIGENTE' ELSE 'VENCIDA' END)       AS ESTATUS,
        MAX(CASE WHEN A.CONCEPTO_ANT LIKE '%PAGO DESCARGA FAVOR%' THEN 'DESCARGA A FAVOR' ELSE 'BANCO' END) AS CONCEPTO,
        MAX(CASE WHEN A.CONCEPTO_ANT LIKE '%PAGO DESCARGA FAVOR%' THEN 'DESCARGA A FAVOR' ELSE A.BANCO_RECEPTOR END) AS BANCO,
        P.TIPO_CREDITO_REPORT                                              AS TIPO_CREDITO,
        MAX(A.FECHA_MOVIMIENTO)                                            AS FECHA_MOVIMIENTO,

        /* Las 14 columnas de importe: una linea cada una, sin listas de rubro.
           Alta de un rubro nuevo = una fila en DUMMY.CAT_RUBRO, cero cambios aqui. */
        SUM(CASE WHEN A.GRUPO='PRINCIPAL'               AND A.ES_IVA=0 THEN A.MONTO*A.FACTOR ELSE 0 END) AS PRINCIPAL,
        SUM(CASE WHEN A.GRUPO='INTERESES'               AND A.ES_IVA=0 THEN A.MONTO*A.FACTOR ELSE 0 END) AS INTERESES,
        SUM(CASE WHEN A.GRUPO='INTERESES'               AND A.ES_IVA=1 THEN A.MONTO*A.FACTOR ELSE 0 END) AS IVA_INTERESES,
        SUM(CASE WHEN A.GRUPO='SEGURO_DANOS'            AND A.ES_IVA=0 THEN A.MONTO*A.FACTOR ELSE 0 END) AS SEGURO_DANOS,
        SUM(CASE WHEN A.GRUPO='SEGURO_DANOS'            AND A.ES_IVA=1 THEN A.MONTO*A.FACTOR ELSE 0 END) AS IVA_SEGURO_DANOS,
        SUM(CASE WHEN A.GRUPO='SEGURO_VIDA'             AND A.ES_IVA=0 THEN A.MONTO*A.FACTOR ELSE 0 END) AS SEGURO_VIDA,
        SUM(CASE WHEN A.GRUPO='COMISION_ADMINISTRACION' AND A.ES_IVA=0 THEN A.MONTO*A.FACTOR ELSE 0 END) AS COMISION_ADMINISTRACION,
        SUM(CASE WHEN A.GRUPO='COMISION_ADMINISTRACION' AND A.ES_IVA=1 THEN A.MONTO*A.FACTOR ELSE 0 END) AS IVA_COMISION_ADMINISTRACION,
        SUM(CASE WHEN A.GRUPO='MORATORIOS'              AND A.ES_IVA=0 THEN A.MONTO*A.FACTOR ELSE 0 END) AS MORATORIOS,
        SUM(CASE WHEN A.GRUPO='MORATORIOS'              AND A.ES_IVA=1 THEN A.MONTO*A.FACTOR ELSE 0 END) AS IVA_MORATORIOS,
        SUM(CASE WHEN A.GRUPO='SALDO_FAVOR'             AND A.ES_IVA=0 THEN A.MONTO*A.FACTOR ELSE 0 END) AS SALDO_FAVOR,
        SUM(CASE WHEN A.GRUPO='OTRO'                    AND A.ES_IVA=0 THEN A.MONTO*A.FACTOR ELSE 0 END) AS OTRO,
        SUM(CASE WHEN A.GRUPO='OTRO'                    AND A.ES_IVA=1 THEN A.MONTO*A.FACTOR ELSE 0 END) AS IVA_OTRO,
        SUM(A.MONTO*A.FACTOR)                                                                            AS TOTAL,
        A.IND_ETAPA                                                        AS ETAPA,
        A.IND_COVID                                                        AS IND_COVID
    FROM      ANOTADO A
    JOIN      @POLIZAS P ON P.ID_POLIZA = A.ID_POLIZA
    GROUP BY  A.VISTA, A.ID_POLIZA, A.ID_SECUENCIA, A.TIPO_CREDITO, A.IND_ETAPA, A.IND_COVID,
              P.ETIQUETA_CARTERA, P.TIPO_CREDITO_REPORT, P.USA_TIPO_VIVIENDA, P.SUFIJO_EN_BLANCO,
              A.ETIQUETA;

    /* 3. Control de configuracion: rubros que llegaron en los movimientos y no
          estan en el catalogo. Hoy este caso es invisible (el rubro simplemente
          no suma en ninguna columna y solo se nota en el TOTAL). Con catalogo se
          vuelve una excepcion visible en el portal.                            */
    SELECT DISTINCT H.RUBRO AS RUBRO_SIN_CATALOGAR
    FROM   PO.SAF_MOV_ABONO H
    WHERE  H.FECHA_MOVIMIENTO = @fechaMovimiento
      AND  NOT EXISTS (SELECT 1 FROM DUMMY.CAT_RUBRO R
                       WHERE R.RUBRO = H.RUBRO
                         AND @fechaMovimiento BETWEEN R.VIGENCIA_DESDE AND R.VIGENCIA_HASTA);
END
GO

/* ---------------------------------------------------------------------------
   NOTAS DE ALCANCE (para no vender mas de lo que el dummy hace)

   * El V2 reproduce el comportamiento actual, incluidos los cuatro defectos
     listados en el dummy 3 solo si se decide conservarlos. Tal como esta
     escrito, los CORRIGE (GRUPO/ES_IVA no permite que el IVA de la comision
     anticipada caiga en OTRO). Por eso la prueba de equivalencia del dummy 5
     va a mostrar diferencia en OTRO / IVA_OTRO: es diferencia esperada y debe
     firmarse con contabilidad antes de sustituir el procedimiento.

   * El factor 9 se conserva tal cual esta hoy. No se convierte en un valor
     editable desde el portal hasta que contabilidad y negocio confirmen su
     base de calculo y su relacion con el 0.10/0.90 de los cierres comerciales.

   * TIPO_CREDITO (texto que viene del movimiento) y NUM_DESC_TIPO_CREDITO
     (numero del credito) son dimensiones distintas. Este dummy NO las une:
     unirlas requiere una relacion explicita validada con negocio, y es una de
     las tareas de la ola siguiente.
   --------------------------------------------------------------------------- */
