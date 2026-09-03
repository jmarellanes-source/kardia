/* ============================================================================
   DUMMY 3 - Catalogos para dbo.REPORTE_COBRANZA_INTEGRACION
   Hallazgos que remedia: catalogo de rubros hardcodeado, etiquetas de poliza
   hardcodeadas y factor de participacion hardcodeado (monto * 9 / monto * 1).

   Medido sobre BD_prod/dbo.REPORTE_COBRANZA_INTEGRACION.StoredProcedure.sql:
     203 lineas, 39 predicados sobre "rubro", 42 rubros distintos,
     124 ocurrencias de literales de rubro, 26 predicados sobre ID_POLIZA,
     14 apariciones de "monto * 9", 45 de 'ADMINISTRACION INDIVIDUAL'.

   Punto importante para el cliente: aqui NO se propone un registro por poliza
   ni por combinacion. Son tres catalogos ortogonales y pequenos:
     5 polizas + 42 rubros + 2 factores de participacion.
   Las combinaciones (5 x 42 x 2 = 420 celdas de reporte) se derivan por
   consulta, no se almacenan.

   NO EJECUTAR EN PRODUCCION.
   ============================================================================ */

IF SCHEMA_ID(N'DUMMY') IS NULL EXEC(N'CREATE SCHEMA DUMMY');
GO

/* ------------------------------------------------ 1. Catalogo de rubros
   Una fila por rubro del core. GRUPO es la columna del reporte a la que suma;
   ES_IVA separa el impuesto del concepto. Alta de un rubro nuevo = 2 filas
   (el rubro y su IVA), sin tocar codigo ni liberar.                          */
CREATE TABLE DUMMY.CAT_RUBRO (
    RUBRO          VARCHAR(60) NOT NULL PRIMARY KEY,
    GRUPO          VARCHAR(40) NOT NULL,   -- PRINCIPAL, INTERESES, SEGURO_DANOS, ...
    ES_IVA         BIT         NOT NULL,
    VIGENCIA_DESDE DATE        NOT NULL CONSTRAINT DF_CR_DESDE DEFAULT ('19000101'),
    VIGENCIA_HASTA DATE        NOT NULL CONSTRAINT DF_CR_HASTA DEFAULT ('99991231'),
    USUARIO_ALTA   SYSNAME     NOT NULL CONSTRAINT DF_CR_USR   DEFAULT (SUSER_SNAME()),
    CONSTRAINT CK_CR_GRUPO CHECK (GRUPO IN ('PRINCIPAL','INTERESES','SEGURO_DANOS','SEGURO_VIDA',
                                            'COMISION_ADMINISTRACION','MORATORIOS','SALDO_FAVOR','OTRO'))
);
GO

/* ---------------------------------------------- 2. Catalogo de polizas
   Sustituye los 26 predicados sobre ID_POLIZA y los cuatro CASE de etiquetas.
   Cinco filas.                                                               */
CREATE TABLE DUMMY.CAT_POLIZA_COBRANZA (
    ID_POLIZA           INT          NOT NULL PRIMARY KEY,
    ETIQUETA_CARTERA    VARCHAR(40)  NOT NULL,   -- 'INDIVIDUAL ', 'COMERCIAL CASTIGO', ...
    TIPO_CREDITO_REPORT VARCHAR(20)  NOT NULL,   -- 'INDIVIDUAL' / 'COMERCIAL'
    USA_TIPO_VIVIENDA   BIT          NOT NULL,   -- hoy: ID_POLIZA IN (7,35,37)
    SUFIJO_EN_BLANCO    BIT          NOT NULL,   -- hoy: ID_POLIZA IN (40,51) -> ''
    INCLUIR_EN_REPORTE  BIT          NOT NULL CONSTRAINT DF_CPC_INC DEFAULT (1),
    VIGENCIA_DESDE      DATE         NOT NULL CONSTRAINT DF_CPC_DESDE DEFAULT ('19000101'),
    VIGENCIA_HASTA      DATE         NOT NULL CONSTRAINT DF_CPC_HASTA DEFAULT ('99991231')
);
GO

/* ------------------------------------- 3. Catalogo de participacion (factor)
   Sustituye el "monto * 9" / "monto * 1" y los dos bloques del UNION ALL.
   Dos filas: la vista del total administrado y la vista de la parte propia.

   ADVERTENCIA para la sesion con contabilidad: el 9 NO se debe migrar como
   configuracion sin validarlo. En este procedimiento el factor es 9 (implica
   una participacion de 1/9 = 11.11%), mientras que en los procedimientos de
   cierre comercial la participacion Afirme esta partida en 0.10 / 0.90 (10%).
   Los dos numeros no son compatibles: o uno de los dos esta mal, o son bases
   distintas. Es pregunta abierta (relacionada con Q05), no un valor a copiar. */
CREATE TABLE DUMMY.CAT_PARTICIPACION (
    VISTA          VARCHAR(30)   NOT NULL,       -- ADMINISTRADA_TOTAL / ADMINISTRADA_PROPIA
    TIPO_CREDITO   VARCHAR(60)   NOT NULL,       -- hoy: 'ADMINISTRACION INDIVIDUAL'
    FACTOR         DECIMAL(18,8) NOT NULL,
    ETIQUETA       VARCHAR(20)   NOT NULL,       -- 'AFIRME' / 'ION'
    SOLO_ESTE_TIPO BIT           NOT NULL,       -- si 1, la vista filtra solo ese tipo
    VIGENCIA_DESDE DATE          NOT NULL,
    VIGENCIA_HASTA DATE          NOT NULL CONSTRAINT DF_CP_HASTA DEFAULT ('99991231'),
    CONSTRAINT PK_CP PRIMARY KEY (VISTA, TIPO_CREDITO, VIGENCIA_DESDE),
    CONSTRAINT CK_CP_FACTOR CHECK (FACTOR > 0)
);
GO


/* ============================ SEMILLA ======================================
   Derivada literalmente del procedimiento actual.                            */

INSERT INTO DUMMY.CAT_RUBRO (RUBRO, GRUPO, ES_IVA) VALUES
 ('PRINCIPAL','PRINCIPAL',0),
 ('INTERESES','INTERESES',0),                          ('IVA INTERESES','INTERESES',1),
 ('INTERES_ORDINARIO_A','INTERESES',0),                ('IVA INTERES_ORDINARIO_A','INTERESES',1),
 ('SEGURO_DANOS','SEGURO_DANOS',0),                    ('IVA SEGURO_DANOS','SEGURO_DANOS',1),
 ('SEG_DAN','SEGURO_DANOS',0),                         ('IVA SEG_DAN','SEGURO_DANOS',1),
 ('CARGO_SEGURO','SEGURO_DANOS',0),                    ('IVA CARGO_SEGURO','SEGURO_DANOS',1),
 ('SEGURO_VIDA','SEGURO_VIDA',0),
 ('CARGO_PORCENTAJE','SEGURO_VIDA',0),
 ('COMISION_ADMINISTRACION','COMISION_ADMINISTRACION',0),
 ('IVA COMISION_ADMINISTRACION','COMISION_ADMINISTRACION',1),
 ('MORATORIOS','MORATORIOS',0),                        ('IVA MORATORIOS','MORATORIOS',1),
 ('INTERES_MORATORIO','MORATORIOS',0),                 ('IVA INTERES_MORATORIO','MORATORIOS',1),
 ('MORA_EMPRESARIAL','MORATORIOS',0),                  ('IVA MORA_EMPRESARIAL','MORATORIOS',1),
 ('SALDO_FAVOR','SALDO_FAVOR',0),
 ('COMISION_ANTICIPADA','OTRO',0),                     ('IVA COMISION_ANTICIPADA','OTRO',1),
 ('COMISION_PREPAGO','OTRO',0),                        ('IVA COMISION_PREPAGO','OTRO',1),
 ('VISITA_EXTRA','OTRO',0),                            ('IVA VISITA_EXTRA','OTRO',1),
 ('COM_CIERRE_OBRA','OTRO',0),                         ('IVA COM_CIERRE_OBRA','OTRO',1),
 ('ASE_FINANCIERA','OTRO',0),                          ('IVA ASE_FINANCIERA','OTRO',1),
 ('COM_PRORROGA','OTRO',0),                            ('IVA COM_PRORROGA','OTRO',1),
 ('COM_REESTRUCTURA','OTRO',0),                        ('IVA COM_REESTRUCTURA','OTRO',1),
 ('OPI VALOR','OTRO',0),                               ('IVA OPI VALOR','OTRO',1),
 ('COMISION_ANTIC_M','OTRO',0),                        ('IVA COMISION_ANTIC_M','OTRO',1),
 ('PRORROGA','OTRO',0),                                ('IVA PRORROGA','OTRO',1);
GO

INSERT INTO DUMMY.CAT_POLIZA_COBRANZA
      (ID_POLIZA, ETIQUETA_CARTERA,     TIPO_CREDITO_REPORT, USA_TIPO_VIVIENDA, SUFIJO_EN_BLANCO) VALUES
      (7,         'INDIVIDUAL ',        'INDIVIDUAL',        1,                 0),
      (35,        'INDIVIDUAL ',        'INDIVIDUAL',        1,                 0),
      (37,        'INDIVIDUAL CASTIGO ','INDIVIDUAL',        1,                 0),
      (40,        'COMERCIAL',          'COMERCIAL',         0,                 1),
      (51,        'COMERCIAL CASTIGO',  'COMERCIAL',         0,                 1);
GO

INSERT INTO DUMMY.CAT_PARTICIPACION
      (VISTA,                  TIPO_CREDITO,                FACTOR, ETIQUETA, SOLO_ESTE_TIPO, VIGENCIA_DESDE) VALUES
      ('ADMINISTRADA_TOTAL',   'ADMINISTRACION INDIVIDUAL', 9,      'AFIRME', 0,              '19000101'),
      ('ADMINISTRADA_TOTAL',   '*',                         1,      '',       0,              '19000101'),
      ('ADMINISTRADA_PROPIA',  'ADMINISTRACION INDIVIDUAL', 1,      'ION',    1,              '19000101');
GO


/* ---------------------------------------------------------------------------
   DEFECTOS QUE EL CATALOGO ELIMINA POR CONSTRUCCION
   (encontrados al normalizar las 39 listas de rubro del procedimiento actual)

   1) Columna OTRO, primer bloque del UNION ALL. La rama de cartera propia
      pide 'IVA COMISION_ANTICIPADA' donde debia pedir 'COMISION_ANTICIPADA':

        SUM(CASE WHEN rubro IN ('COMISION_ANTICIPADA',...) and tipo_credito =  'ADMINISTRACION INDIVIDUAL' THEN monto * 9
                 WHEN rubro IN ('IVA COMISION_ANTICIPADA',...) AND tipo_credito <> 'ADMINISTRACION INDIVIDUAL' THEN monto * 1

      Consecuencia: en cartera propia la comision anticipada no entra en OTRO y
      su IVA entra en OTRO en lugar de IVA_OTRO. Con GRUPO+ES_IVA en catalogo el
      error es imposible de escribir. Pendiente de cuantificar con datos reales.

   2) Columna IVA_OTRO, primer bloque: la lista omite 'IVA COMISION_ANTICIPADA',
      que el segundo bloque si incluye. Los dos bloques no son consistentes.

   3) Etiqueta de ID_POLIZA = 35: 'INDIVIDUAL ' en el primer bloque y
      'INDIVIDUAL EMPLEADO ' en el segundo.

   4) Etiqueta de 'ADMINISTRACION INDIVIDUAL': 'AFIRME' en el primer bloque y
      'ION' en el segundo. Es intencional (total vs parte propia) pero no esta
      documentado en el codigo; en el catalogo es la columna ETIQUETA de la vista.

   Los cuatro son consecuencia del mismo mecanismo: mantener 39 listas a mano en
   dos bloques casi identicos.
   --------------------------------------------------------------------------- */
