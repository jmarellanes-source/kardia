/* ============================================================================
   Fase 0 - Paso 2: quien dispara el cierre diario y a que hora
   ----------------------------------------------------------------------------
   SOLO LECTURA. El cierre corre automatico minutos despues de que SAF cierra
   operaciones, pero el repositorio no dice quien lo lanza ni con que parametros.
   Sin esto no se puede fijar la ventana de despliegue ni saber que objeto es
   punto de entrada.

     sqlcmd -S <servidor> -d msdb -i 02_disparadores_cierre.sql -s"|" -W -o jobs_PROD.csv
   ============================================================================ */
SET NOCOUNT ON;

-- 1) Jobs y sus pasos: comando exacto, base de datos y si estan habilitados
SELECT
    job        = j.name,
    habilitado = j.enabled,
    paso       = s.step_id,
    nombre_paso= s.step_name,
    subsistema = s.subsystem,
    base       = s.database_name,
    comando    = s.command,
    al_fallar  = s.on_fail_action,
    reintentos = s.retry_attempts
FROM msdb.dbo.sysjobs      AS j
JOIN msdb.dbo.sysjobsteps  AS s ON s.job_id = j.job_id
ORDER BY j.name, s.step_id;

-- 2) Calendario de ejecucion (hora de arranque y frecuencia)
SELECT
    job         = j.name,
    programa    = sch.name,
    habilitado  = sch.enabled,
    frecuencia  = CASE sch.freq_type WHEN 1 THEN 'Una vez' WHEN 4 THEN 'Diario'
                                     WHEN 8 THEN 'Semanal' WHEN 16 THEN 'Mensual'
                                     WHEN 32 THEN 'Mensual relativo' WHEN 64 THEN 'Al iniciar SQL Agent'
                                     WHEN 128 THEN 'Cuando el CPU esta inactivo' END,
    cada        = sch.freq_interval,
    hora_inicio = STUFF(STUFF(RIGHT('000000' + CAST(sch.active_start_time AS varchar(6)), 6), 5, 0, ':'), 3, 0, ':'),
    subdiario   = sch.freq_subday_interval
FROM msdb.dbo.sysjobs           AS j
JOIN msdb.dbo.sysjobschedules   AS js  ON js.job_id = j.job_id
JOIN msdb.dbo.sysschedules      AS sch ON sch.schedule_id = js.schedule_id
ORDER BY j.name;

-- 3) Ultimas 30 corridas con duracion y resultado: da la ventana real del cierre
SELECT TOP (30)
    job       = j.name,
    paso      = h.step_name,
    fecha     = h.run_date,
    hora      = STUFF(STUFF(RIGHT('000000' + CAST(h.run_time AS varchar(6)), 6), 5, 0, ':'), 3, 0, ':'),
    duracion  = STUFF(STUFF(RIGHT('000000' + CAST(h.run_duration AS varchar(6)), 6), 5, 0, ':'), 3, 0, ':'),
    resultado = CASE h.run_status WHEN 0 THEN 'Fallo' WHEN 1 THEN 'Exito' WHEN 2 THEN 'Reintento'
                                  WHEN 3 THEN 'Cancelado' ELSE 'En progreso' END,
    mensaje   = h.message
FROM msdb.dbo.sysjobhistory AS h
JOIN msdb.dbo.sysjobs       AS j ON j.job_id = h.job_id
ORDER BY h.run_date DESC, h.run_time DESC;
GO

/* 4) La bitacora que hoy nadie vigila: 102 objetos escriben en
      PO.SAF_POLIZA_ERRORES y ningun objeto la lee. Ejecutar contra KARDIA. */
USE KARDIA;
SELECT TOP (100) * FROM PO.SAF_POLIZA_ERRORES ORDER BY 1 DESC;
GO
