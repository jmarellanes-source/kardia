/* ============================================================================
   Fase 0 - Paso 1: fotografia del codigo que realmente corre en la instancia
   ----------------------------------------------------------------------------
   SOLO LECTURA. No crea, no modifica y no borra nada. Se ejecuta en cada
   ambiente (produccion y QA/CUA) conectado a KARDIA, y su salida se guarda como
   CSV para cruzarla despues contra el repositorio con 03_comparar_paridad.py.

     sqlcmd -S <servidor> -d KARDIA -i 01_inventario_instancia.sql -s"|" -W -h-1 ^
            -o inventario_PROD.csv

   Por que hace falta: hoy 19 de los 27 objetos de la familia CIERRE no existen
   en el export de BD_prod y SP_SAF_SALDOS aparece con 223 de sus 573 lineas, de
   modo que nadie puede afirmar cual version del cierre esta ejecutandose. Esta
   consulta responde exactamente eso.

   El hash se calcula sobre el texto NORMALIZADO (sin CRLF, sin tabuladores y
   con espacios colapsados) para que una diferencia de formato no se reporte
   como diferencia de codigo. La normalizacion es la misma que aplica el
   comparador del repositorio.
   ============================================================================ */
SET NOCOUNT ON;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;  -- metadatos, sin bloquear nada

;WITH modulos AS (
    SELECT
        o.object_id,
        nombre      = QUOTENAME(SCHEMA_NAME(o.schema_id)) + N'.' + QUOTENAME(o.name),
        tipo        = o.type_desc,
        creado      = o.create_date,
        modificado  = o.modify_date,
        texto       = m.definition
    FROM sys.sql_modules AS m
    JOIN sys.objects     AS o ON o.object_id = m.object_id
    WHERE o.is_ms_shipped = 0
),
normalizado AS (
    SELECT
        nombre, tipo, creado, modificado,
        lineas = LEN(texto) - LEN(REPLACE(texto, CHAR(10), N'')) + 1,
        bytes  = DATALENGTH(texto),
        -- normalizacion: CRLF y tabuladores a espacio, espacios dobles colapsados
        plano  = REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                 texto, CHAR(13), N' '), CHAR(10), N' '), CHAR(9), N' '),
                 N'  ', N' '), N'  ', N' ')
    FROM modulos
)
SELECT
    ambiente   = CAST(SERVERPROPERTY('MachineName') AS nvarchar(128)) + N'/' + DB_NAME(),
    nombre, tipo, lineas, bytes,
    creado     = CONVERT(char(19), creado, 126),
    modificado = CONVERT(char(19), modificado, 126),
    hash_sha2  = CONVERT(char(64), HASHBYTES('SHA2_256', LTRIM(RTRIM(plano))), 2)
FROM normalizado
ORDER BY nombre;
GO

/* Complemento: objetos que NO son modulos (tablas) con su conteo de columnas,
   llaves y restricciones. Sirve para verificar la declaracion de normalizacion
   hasta 3FN, que el repositorio por si solo no permite comprobar. */
SELECT
    tabla        = QUOTENAME(SCHEMA_NAME(t.schema_id)) + N'.' + QUOTENAME(t.name),
    columnas     = (SELECT COUNT(*) FROM sys.columns c WHERE c.object_id = t.object_id),
    tiene_pk     = CASE WHEN EXISTS (SELECT 1 FROM sys.key_constraints k
                                     WHERE k.parent_object_id = t.object_id AND k.type = 'PK')
                        THEN 1 ELSE 0 END,
    fks          = (SELECT COUNT(*) FROM sys.foreign_keys f WHERE f.parent_object_id = t.object_id),
    checks       = (SELECT COUNT(*) FROM sys.check_constraints ck WHERE ck.parent_object_id = t.object_id),
    indices      = (SELECT COUNT(*) FROM sys.indexes i WHERE i.object_id = t.object_id AND i.index_id > 0),
    cols_money   = (SELECT COUNT(*) FROM sys.columns c JOIN sys.types ty ON ty.user_type_id = c.user_type_id
                    WHERE c.object_id = t.object_id AND ty.name IN ('money', 'smallmoney')),
    filas        = SUM(CASE WHEN p.index_id IN (0, 1) THEN p.rows ELSE 0 END)
FROM sys.tables AS t
LEFT JOIN sys.partitions AS p ON p.object_id = t.object_id
WHERE t.is_ms_shipped = 0
GROUP BY t.schema_id, t.name, t.object_id
ORDER BY tabla;
GO
