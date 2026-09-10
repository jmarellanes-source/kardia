/* ============================================================================
   Fase 1 - Paso 3: verificacion posterior al despliegue (SOLO LECTURA)
   ----------------------------------------------------------------------------
   Se ejecuta en cada ambiente despues de aplicar los sinonimos y el codigo
   sustituido. Las cuatro consultas deben devolver los resultados indicados; si
   alguna falla, el despliegue no esta completo y no debe promoverse.
   ============================================================================ */
SET NOCOUNT ON;

/* 1) Debe devolver 0 filas: ningun objeto programable menciona ya el nombre de
      la base de origen. Es la prueba de que el drift por ambiente desaparecio. */
SELECT objeto = QUOTENAME(SCHEMA_NAME(o.schema_id)) + N'.' + QUOTENAME(o.name),
       tipo   = o.type_desc
FROM sys.sql_modules AS m
JOIN sys.objects     AS o ON o.object_id = m.object_id
WHERE o.is_ms_shipped = 0
  AND m.definition LIKE N'%Quiero_Confianza%'
ORDER BY objeto;

/* 2) Debe devolver 38 filas, todas apuntando a la MISMA base, y esa base debe
      ser la del ambiente (Quiero_Confianza en produccion). */
SELECT sinonimo   = QUOTENAME(SCHEMA_NAME(s.schema_id)) + N'.' + QUOTENAME(s.name),
       apunta_a   = s.base_object_name,
       base       = PARSENAME(s.base_object_name, 3),
       resuelve   = CASE WHEN OBJECT_ID(s.base_object_name) IS NULL
                         THEN 'NO RESUELVE' ELSE 'OK' END
FROM sys.synonyms AS s
WHERE SCHEMA_NAME(s.schema_id) = N'EXT'
ORDER BY sinonimo;

/* 3) Debe devolver 1 fila: una sola base de origen distinta entre los 38
      sinonimos. Mas de una fila significa que quedo un ambiente mezclado. */
SELECT base = PARSENAME(s.base_object_name, 3), sinonimos = COUNT(*)
FROM sys.synonyms AS s
WHERE SCHEMA_NAME(s.schema_id) = N'EXT'
GROUP BY PARSENAME(s.base_object_name, 3);

/* 4) Debe devolver 0 filas: ningun sinonimo roto (objeto inexistente o sin
      permiso de lectura en el origen). Verificarlo con la cuenta de servicio
      que ejecuta el cierre, no con una cuenta administrativa. */
SELECT sinonimo = QUOTENAME(SCHEMA_NAME(s.schema_id)) + N'.' + QUOTENAME(s.name),
       apunta_a = s.base_object_name
FROM sys.synonyms AS s
WHERE SCHEMA_NAME(s.schema_id) = N'EXT'
  AND OBJECT_ID(s.base_object_name) IS NULL
ORDER BY sinonimo;
GO
