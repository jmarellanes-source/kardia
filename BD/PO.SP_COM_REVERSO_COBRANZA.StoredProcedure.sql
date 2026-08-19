SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [PO].[SP_COM_REVERSO_COBRANZA]
(
	@FECHA_INICIO DATE
)
AS
BEGIN
    SET NOCOUNT ON

    declare @ID_POLIZA int = 42
           ,@FECHA_ANT date
    
    set @FECHA_ANT = DATEADD(day, -1, @FECHA_INICIO)

    create table #CuentasDeOtrasPolizas(cuenta varchar(24))

    insert into #CuentasDeOtrasPolizas(cuenta)
          select '140103009001'     --operacion vivienda bonificacion y reestructura
    union select '140103009002'     --operacion comercial bonificacion y reestructura
    union select '140103009003'     --operacion reestructura
    union select '1401030090010000' --operacion vivienda ajuste
    union select '1401030090020000' --operacion comercial ajuste
    union select '5050260901000300' --condonacion
	union select '2073'             --DACION
	union select '2074'             --ADJUDICACION
	union select '2076'             --EX_EMPLEADO
	union select '2068'             --SINIESTRO
    union select '2061'             --STDR FISO DAMNIF_6641
    union select '2056'             --INBURSA ADMON COBRANZA

	BEGIN TRY
		BEGIN TRANSACTION
		
			DELETE FROM PO.SAF_MOV_ABONO WHERE FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA

			--# BLOCK: EXTRACTOR DE MOVIMIENTOS PAGO
			INSERT INTO PO.SAF_MOV_ABONO(
			ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, CUENTA_CARGO, CUENTA_ABONO, ID_PRODUCTO, NOMBRE_PRODUCTO, ID_FONDEO, RUBRO, MONTO
			,MON_PAGO_IVA, IND_FORMA_PAGO, ID_TIPO_CREDITO, TIPO_CREDITO, IND_ESTADO, CARTERA_VENCIDA, FECHA_MOVIMIENTO
			,TIP_TRANSACCION, SUBTIP_TRANSAC, IND_ETAPA, MON_CREDITO, CEDIDO, FEC_APERTURA, ID_SECUENCIA, ID_REFERENCIA, ID_CUENTA, IND_COVID, 
			CONCEPTO_FINAL, APELLIDO, TABLA_ORIGEN, ID_POLIZA, TIPO_VIVIENDA, REVERSO, CANAL)
			SELECT  
				C.ID_EXTERNO
				,C.NUM_CREDITO
				,dbo.FN_FORMA_NOMBRE(PF.PRIMER_APELLIDO, PF.SEGUNDO_APELLIDO, PF.PRIMER_NOMBRE, PF.SEGUNDO_NOMBRE, PJ.RAZON_SOCIAL, PJ.NOM_COMERCIAL)
				,'' AS CUENTA_CARGO
				,'' AS CUENTA_ABONO
				,ISNULL((SELECT TOP 1 NUM_PRODUCTO FROM PO.PR_CAT_PRODUCTO WHERE ID_SAF = P.TIP_CREDITO), P.TIP_CREDITO) ID_PRODUCTO
				--,(SELECT TOP 1 NOMBRE_PRODUCTO FROM PO.PR_CAT_PRODUCTO WHERE ID_SAF = P.TIP_CREDITO) NOMBRE_PRODUCTO
				,CP.NOMBRE_CORTO
				,CH.ID_FONDEO
				,B.COD_CONCEPTO AS RUBRO
				,B.MON_PAGO MONTO
				,B.MON_PAGO_IVA
				,CASE WHEN A.IND_FORMA_PAGO = '' THEN 0 ELSE A.IND_FORMA_PAGO END IND_FORMA_PAGO
				,C.NUM_DESC_TIPO_CREDITO
				--,(SELECT TOP 1 DESC_TIPO_CREDITO FROM [PO].[SAF_CAT_DESC_TIPO] WHERE NUM_DESC_TIPO_CREDITO = C.NUM_DESC_TIPO_CREDITO)
				,CP.NOMBRE_CORTO
				,C.IND_ESTADO
				,CASE WHEN C.Ind_estado_Cont = 'VI' THEN 'NO' WHEN C.Ind_estado_Cont = 'VE' THEN 'SI' END CARTERA_VENCIDA
				,A.FEC_MOVIMIENTO
				,A.TIP_TRANSACCION
				,A.SUBTIP_TRANSAC
				,CH.IND_ETAPA
				,C.MON_CREDITO
				,[dbo].[FN_ORIGEN_FONDOS](C.COD_ORIGEN,C.COD_EMPRESA) AS CEDIDO 
				,C.FEC_APERTURA
				,A.Id_secuencia
                ,B.ID_REFERENCIA
				,case when exists(select * from Quiero_Confianza_Shadow.PR.PR_DEPOSITOS_X_IDENTIFICAR where id_carga = A.id_carga and id_deposito = A.id_deposito) then 2080 else CAST(A.Id_cuenta AS bigint) end
				,dbo.FN_ES_COVID(Q.Ind_Posposicion,Q.Fecha_Posposicion,Q.Num_Credito)
				,''
				,IIF(PF.PRIMER_APELLIDO IS NULL OR PF.PRIMER_APELLIDO = '', 'NOMBRE', PF.PRIMER_APELLIDO)
				,'REVERSO COBRANZA COM'
				,@ID_POLIZA
                ,''--CH.TIPO_VIVIENDA
				,case when exists(select * from Quiero_Confianza_shadow.PR.PR_ENCABEZADO_PAGO where num_asiento = A.num_asiento and Mon_movimiento = -A.Mon_movimiento) then 'SI' else 'NO' end
				,dbo.FN_TIPO_CANAL(C.TIP_TASA)
			FROM Quiero_Confianza_shadow.PR.PR_ENCABEZADO_PAGO A WITH (NOLOCK)
					INNER JOIN Quiero_Confianza_shadow.PR.PR_DETALLE_PAGO B WITH (NOLOCK) ON A.ID_SECUENCIA = B.ID_SECUENCIA
					INNER JOIN Quiero_Confianza_shadow.PR.PR_CREDITOS C WITH (NOLOCK) ON A.COD_EMPRESA = C.COD_EMPRESA AND A.NUM_CREDITO = C.NUM_CREDITO
					INNER JOIN Quiero_Confianza_shadow.PR.PR_TIPO_CREDITO P WITH (NOLOCK) ON C.TIP_CREDITO = P.TIP_CREDITO AND C.COD_EMPRESA = P.COD_EMPRESA

					LEFT JOIN Quiero_Confianza_shadow.PR.PR_RUBRO_COBRO_X_CREDITO Q WITH (NOLOCK) ON Q.Num_Secuencia = B.Id_referencia
					    AND Q.Num_Credito = A.Num_credito AND Q.Num_Det_Secuencia = B.Num_det_secuencia AND Q.Cod_Rubro = B.Cod_concepto AND Q.Ind_Estado != 'N'
                    LEFT JOIN PO.CONTROL_HISTORICO_TRASPASOS CH ON A.NUM_CREDITO = CH.NUM_CREDITO AND CH.FECHA_SISTEMA = @FECHA_ANT
					LEFT JOIN PO.PR_CREDITO_EXTRA CE ON CE.ID_EXTERNO = C.ID_EXTERNO
					LEFT JOIN PO.PR_CREDITO_PRODUCTO CP ON CP.ID_PRODUCTO = CE.ID_PRODUCTO
					LEFT JOIN Quiero_Confianza_shadow.CL.CL_PERSONAS_JURIDICAS PJ WITH (NOLOCK) ON C.COD_EMPRESA = PJ.COD_EMPRESA AND C.COD_CLIENTE = PJ.COD_CLIENTE
					LEFT JOIN Quiero_Confianza_shadow.CL.CL_PERSONAS_FISICAS PF WITH (NOLOCK) ON C.COD_EMPRESA = PF.COD_EMPRESA AND C.COD_CLIENTE = PF.COD_CLIENTE
			WHERE C.IND_ESTADO IN ('C', 'D')
					AND C.IND_LINEA = 'N'
                    AND C.NUM_DESC_TIPO_CREDITO IN (5,   12,13,14,15,28,   2,18,27)
					AND A.TIP_TRANSACCION !=3  --Evita que se traigan desembolsos que se jalan en SP FIRMA
					AND NOT ((TIP_TRANSACCION = 4 AND SUBTIP_TRANSAC = 5)
                            OR (A.ID_CUENTA IN (select cuenta from #CuentasDeOtrasPolizas))
                        ) 
                    AND A.mon_movimiento < 0 -- SOLO se consideran cancelaciones
					AND A.FEC_MOVIMIENTO = @FECHA_INICIO
					AND (B.MON_PAGO <> 0 OR B.MON_PAGO_IVA <> 0)
			--# END_BLOCK: EXTRACTOR
						
		---# Calcula TIPO DE PRODUCTO, TIPO VIVIENDA deacuerdo al avaluo		
		--MONTO DEL AVALUO
		--DECLARE @MONTO_AVALUO NUMERIC(11,2) = IIF(@FECHA_INICIO >= '2024-01-01', 2648615.20, 2207161.60) --2648615.20 --2207161.60

		/*UPDATE H SET
			H.IND_ETAPA = 1
		FROM PO.SAF_MOV_ABONO H 
		WHERE H.IND_ETAPA = 0 AND H.FECHA_MOVIMIENTO BETWEEN @FECHA_INICIO AND @FECHA_FIN
		AND H.ID_POLIZA = @ID_POLIZA*/

        /*select distinct num_credito
        into #etapa_ant
		FROM PO.SAF_MOV_ABONO H 
		WHERE H.ID_POLIZA = @ID_POLIZA AND H.FECHA_MOVIMIENTO = DATEADD(day, -1, @FECHA_INICIO)
            and H.IND_ETAPA = 3
        group by num_credito

        UPDATE PO.SAF_MOV_ABONO
        SET IND_ETAPA = 3
		WHERE ID_POLIZA = @ID_POLIZA AND FECHA_MOVIMIENTO = @FECHA_INICIO
		    AND IND_ETAPA = 1
            and num_credito in (select num_credito from #etapa_ant)*/

		--TIPO DE VIVIENDA DE ACUERDO AL MONTO DEL AVALUO
		/*UPDATE H SET
				H.TIPO_VIVIENDA = IIF(CC.MON_AVALUO >  @MONTO_AVALUO, 'MEDIA RESIDENCIAL', 'INTERES SOCIAL'),
				H.ID_PRODUCTO = IIF(CC.MON_AVALUO > @MONTO_AVALUO, 2, 1),
				H.NOMBRE_PRODUCTO = IIF(CC.MON_AVALUO > @MONTO_AVALUO, 'MEDIA RESIDENCIAL', 'INTERES SOCIAL')
			FROM PO.SAF_MOV_ABONO H 
				INNER JOIN Quiero_Confianza_shadow.PR.PR_GARANTIAS_CREDITO GG ON GG.NUM_CREDITO = H.NUM_CREDITO
				INNER JOIN Quiero_Confianza_shadow.PR.PR_GARANTIAS CC ON GG.NUM_SECUENCIA = CC.NUM_GARANTIA
			WHERE H.FECHA_MOVIMIENTO BETWEEN @FECHA_INICIO AND @FECHA_FIN
			AND H.ID_POLIZA = @ID_POLIZA*/
		/*
		--- SI ALGUN TIPO VIVIENDA ES NULL se clasifica como consumo
		UPDATE PO.SAF_MOV_ABONO 
				SET TIPO_VIVIENDA = 'CONSUMO',
				ID_PRODUCTO = 50,	
				NOMBRE_PRODUCTO = 'CONSUMO'
			WHERE FECHA_MOVIMIENTO = @FECHA_INICIO AND TIPO_VIVIENDA IS NULL
				AND ID_POLIZA = @ID_POLIZA

		-- SE DETERMINA EL TIPO DE PRODUCTO DEACUERDO AL ID EMPLEADO O CONSUMO
		UPDATE H SET 
				H.ID_PRODUCTO = 50,	
				H.NOMBRE_PRODUCTO = 'CONSUMO'
			FROM  PO.SAF_MOV_ABONO H  
			INNER JOIN Quiero_Confianza_shadow.PR.PR_CREDITOS GG ON GG.NUM_CREDITO = H.NUM_CREDITO
			WHERE GG.NUM_DESC_TIPO_CREDITO = 1 AND FECHA_MOVIMIENTO = @FECHA_INICIO
			AND H.ID_POLIZA = @ID_POLIZA

		UPDATE H SET 
			H.ID_PRODUCTO = 51,	
			H.NOMBRE_PRODUCTO = 'EMPLEADO'
		FROM  PO.SAF_MOV_ABONO H  INNER JOIN Quiero_Confianza_shadow.PR.PR_CREDITOS GG ON GG.NUM_CREDITO = H.NUM_CREDITO
			WHERE GG.NUM_DESC_TIPO_CREDITO IN (9, 10, 11) AND FECHA_MOVIMIENTO = @FECHA_INICIO
			AND H.ID_POLIZA = @ID_POLIZA
		*/
        UPDATE H
			SET H.BANCO_RECEPTOR = C.DES_CUENTA+'/'+C.NUM_CUENTA
		FROM PO.SAF_MOV_ABONO H
			INNER JOIN Quiero_Confianza_shadow.BA.BA_CTA_CORRIENTE C ON H.ID_CUENTA = CAST( C.ID_CUENTA AS VARCHAR(50))
		WHERE H.FECHA_MOVIMIENTO = @FECHA_INICIO
			AND H.ID_POLIZA = @ID_POLIZA

		------------- ###################################### ------------------------------------------------
		------------- ###################################### ------------------------------------------------

		---# Crea un nuevo registro si existe IVA en el universo extraido
		INSERT INTO PO.SAF_MOV_ABONO (ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, ID_PRODUCTO, NOMBRE_PRODUCTO, ID_FONDEO, 
										TIP_TRANSACCION, SUBTIP_TRANSAC, RUBRO, MONTO, MON_PAGO_IVA, ID_TIPO_CREDITO,
										TIPO_CREDITO, TIPO_VIVIENDA, FECHA_MOVIMIENTO, IND_ESTADO, IND_ETAPA, IND_FORMA_PAGO,
										FEC_APERTURA, CEDIDO, MON_CREDITO, ID_SECUENCIA,ID_REFERENCIA, ID_CUENTA, BANCO_RECEPTOR, IND_COVID, APELLIDO, TABLA_ORIGEN, ID_POLIZA, REVERSO,
										CANAL)
		SELECT ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, ID_PRODUCTO, NOMBRE_PRODUCTO, ID_FONDEO,
				TIP_TRANSACCION, SUBTIP_TRANSAC, CONCAT('IVA ', RUBRO), MON_PAGO_IVA, 0, ID_TIPO_CREDITO, 
				TIPO_CREDITO, TIPO_VIVIENDA, FECHA_MOVIMIENTO, IND_ESTADO, IND_ETAPA, IND_FORMA_PAGO,
				FEC_APERTURA, CEDIDO, MON_CREDITO, ID_SECUENCIA, ID_REFERENCIA, ID_CUENTA, BANCO_RECEPTOR, IND_COVID, APELLIDO, 'REVERSO COBRANZA COM', @ID_POLIZA, REVERSO,
				CANAL
		FROM PO.SAF_MOV_ABONO
		WHERE MON_PAGO_IVA != 0 AND FECHA_MOVIMIENTO = @FECHA_INICIO
		    AND ID_POLIZA = @ID_POLIZA
		------------- ###################################### ------------------------------------------------
		------------- ###################################### ------------------------------------------------

		---# NUEVO REGISTRO PARA CANCELACION DE CUENTAS POR COBRAR PARA COMISION_PREPAGO
		INSERT INTO PO.SAF_MOV_ABONO (ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, ID_PRODUCTO, NOMBRE_PRODUCTO, ID_FONDEO, 
										TIP_TRANSACCION, SUBTIP_TRANSAC, RUBRO, MONTO, MON_PAGO_IVA, ID_TIPO_CREDITO,
										TIPO_CREDITO, TIPO_VIVIENDA, FECHA_MOVIMIENTO, IND_ESTADO, IND_ETAPA, IND_FORMA_PAGO,
										FEC_APERTURA, CEDIDO, MON_CREDITO, ID_SECUENCIA,ID_REFERENCIA, ID_CUENTA, BANCO_RECEPTOR, IND_COVID, 
										APELLIDO, TABLA_ORIGEN, ID_POLIZA, CONCEPTO, REVERSO, CANAL)
		SELECT ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, ID_PRODUCTO, NOMBRE_PRODUCTO, ID_FONDEO,
				TIP_TRANSACCION, SUBTIP_TRANSAC, CONCAT('IVA ', RUBRO), MON_PAGO_IVA, 0, ID_TIPO_CREDITO, 
				TIPO_CREDITO, TIPO_VIVIENDA, FECHA_MOVIMIENTO, IND_ESTADO, IND_ETAPA, IND_FORMA_PAGO,
				FEC_APERTURA, CEDIDO, MON_CREDITO, ID_SECUENCIA, ID_REFERENCIA, ID_CUENTA, BANCO_RECEPTOR, IND_COVID, APELLIDO, 'REVERSO COBRANZA COM', @ID_POLIZA,
				'CANC PREPAGO', REVERSO, CANAL
		FROM PO.SAF_MOV_ABONO
		WHERE MON_PAGO_IVA != 0 AND FECHA_MOVIMIENTO = @FECHA_INICIO
		    AND ID_POLIZA = @ID_POLIZA AND RUBRO='COMISION_PREPAGO' 
		------------- ###################################### ------------------------------------------------
		------------- ###################################### ------------------------------------------------

		--- CALIFICACION BASE DEL CONCEPTO DEACUERDO A REGLAS GLOBALES
		UPDATE PO.SAF_MOV_ABONO
				SET CONCEPTO = CONCAT(
				'CMR ',
				CASE
					WHEN CONCEPTO = 'CANC PREPAGO' THEN 'CANC CXC '
					--WHEN TIP_TRANSACCION = 4 AND IND_FORMA_PAGO = 5 AND ID_PRODUCTO=50 THEN 'PAGO SALDO_FAVOR CONSUMO ' --Pago que se aplica utilizando saldo a favor "este es descarga saldo a favor y es de consumo"
					--WHEN TIP_TRANSACCION = 4 AND IND_FORMA_PAGO = 5 AND ID_PRODUCTO=51 THEN 'PAGO SALDO_FAVOR EMPLEADO ' --Pago que se aplica utilizando saldo a favor "este es descarga saldo a favor y es de consumo"
					--WHEN TIP_TRANSACCION = 4 AND IND_FORMA_PAGO = 5 THEN 'PAGO SALDO_FAVOR ' --Pago que se aplica utilizando saldo a favor "este es descarga saldo a favor"
					WHEN (TIP_TRANSACCION = 113) OR (TIP_TRANSACCION = 4 AND RUBRO = 'SALDO_FAVOR') THEN 'SALDO_FAVOR '  --Al recibirse un pago y una parte se va a saldo a favor

					--WHEN ID_PRODUCTO= 50 THEN 'PAGO CONSUMO '
					--WHEN ID_PRODUCTO= 51 THEN 'PAGO EMPLEADO '

					WHEN TIP_TRANSACCION = 4 THEN 'PAGO '
					--WHEN ID_TIPO_CREDITO = 26 THEN 'CASTIGO '
					ELSE ''
				END,
                /*IIF(ID_PRODUCTO= 50, 'CONSUMO ', ''),IIF(ID_PRODUCTO= 51, 'EMPLEADO ', ''),
				IIF( (ID_CUENTA = '2076' OR ID_CUENTA = '1020010502130300') AND ID_PRODUCTO= 50, 'EXEM ', ''),*/ -- VALIDAR 
				IIF(IND_COVID = 'S', 'COVID ', ''), --# Si el registro tiene COVID le agrega la palabra
				IIF(TIP_TRANSACCION = 113 OR (TIP_TRANSACCION = 4 AND RUBRO = 'SALDO_FAVOR'), '', IIF(CONCEPTO='PREPAGO',dbo.FN_RUBRO_POL(RUBRO)+' CANC ',dbo.FN_RUBRO_POL(RUBRO))/* + ' '*/),  --# Si no es saldo a favor le agrega el rubro
				-- tipo_credito
				CASE WHEN RUBRO IN ('CARGO_PORCENTAJE','CARGO_SEGURO','SEG_DAN','SEGURO_DANOS','SEGURO_VIDA') THEN ''
					WHEN TIP_TRANSACCION = 113 OR (TIP_TRANSACCION = 4 AND RUBRO = 'SALDO_FAVOR') THEN ''
					ELSE ' '+TIPO_CREDITO+' '
				END,
				-- canal
				CASE WHEN RUBRO IN ('CARGO_PORCENTAJE','CARGO_SEGURO','SEG_DAN','SEGURO_DANOS','SEGURO_VIDA') THEN ''
					WHEN TIP_TRANSACCION = 113 OR (TIP_TRANSACCION = 4 AND RUBRO = 'SALDO_FAVOR') THEN ''
					ELSE CANAL
				END,
				-- espacio para continuar con cedido
				IIF(RUBRO LIKE '%IVA%' OR RUBRO IN ('CARGO_PORCENTAJE','CARGO_SEGURO','SEG_DAN','SEGURO_DANOS','SEGURO_VIDA') 
				OR (TIP_TRANSACCION = 113 OR (TIP_TRANSACCION = 4 AND RUBRO = 'SALDO_FAVOR')),'',' '),
				/*IIF(ID_PRODUCTO= 50,'', CONCAT(TIPO_VIVIENDA, ' ')),*/
				-- 'NO' OPCIONAL PARA CEDIDO
				CASE WHEN RUBRO IN ('CARGO_PORCENTAJE','CARGO_SEGURO','SEG_DAN','SEGURO_DANOS','SEGURO_VIDA') THEN ''
					WHEN TIP_TRANSACCION = 113 OR (TIP_TRANSACCION = 4 AND RUBRO = 'SALDO_FAVOR') THEN ''
					WHEN RUBRO LIKE '%IVA%' THEN ''
					ELSE IIF(ID_FONDEO = 2, 'NO ', '')
				END,
				-- RESTRINGIDO
				CASE WHEN RUBRO IN ('CARGO_PORCENTAJE','CARGO_SEGURO','SEG_DAN','SEGURO_DANOS','SEGURO_VIDA') THEN ''
					WHEN TIP_TRANSACCION = 113 OR (TIP_TRANSACCION = 4 AND RUBRO = 'SALDO_FAVOR') THEN ''
					WHEN RUBRO LIKE '%IVA%' THEN ''
					ELSE 'RESTRINGIDO '
				END,
				-- ETAPA
                CASE WHEN RUBRO IN ('CARGO_PORCENTAJE','CARGO_SEGURO','SEG_DAN','SEGURO_DANOS','SEGURO_VIDA') THEN ''
					WHEN TIP_TRANSACCION = 113 OR (TIP_TRANSACCION = 4 AND RUBRO = 'SALDO_FAVOR') THEN ''
					WHEN RUBRO LIKE '%IVA%' THEN ''
					ELSE CAST(IND_ETAPA AS VARCHAR(1))
				END) 
			WHERE FECHA_MOVIMIENTO = @FECHA_INICIO
			AND ID_POLIZA = @ID_POLIZA AND RUBRO != '' AND ID_TIPO_CREDITO != 5

		-- GENERACION DE CONCEPTOS MEZZANINE COMERCIALES
		UPDATE PO.SAF_MOV_ABONO
				SET CONCEPTO = CONCAT(
				'CMR DCM ',
				CASE
					WHEN CONCEPTO = 'CANC PREPAGO' THEN 'CANC CXC '
					--WHEN TIP_TRANSACCION = 4 AND IND_FORMA_PAGO = 5 AND ID_PRODUCTO=50 THEN 'PAGO SALDO_FAVOR CONSUMO ' --Pago que se aplica utilizando saldo a favor "este es descarga saldo a favor y es de consumo"
					--WHEN TIP_TRANSACCION = 4 AND IND_FORMA_PAGO = 5 AND ID_PRODUCTO=51 THEN 'PAGO SALDO_FAVOR EMPLEADO ' --Pago que se aplica utilizando saldo a favor "este es descarga saldo a favor y es de consumo"
					--WHEN TIP_TRANSACCION = 4 AND IND_FORMA_PAGO = 5 THEN 'PAGO SALDO_FAVOR ' --Pago que se aplica utilizando saldo a favor "este es descarga saldo a favor"
					WHEN (TIP_TRANSACCION = 113) OR (TIP_TRANSACCION = 4 AND RUBRO = 'SALDO_FAVOR') THEN 'SALDO_FAVOR '  --Al recibirse un pago y una parte se va a saldo a favor

					--WHEN ID_PRODUCTO= 50 THEN 'PAGO CONSUMO '
					--WHEN ID_PRODUCTO= 51 THEN 'PAGO EMPLEADO '

					WHEN TIP_TRANSACCION = 4 THEN 'PAGO '
					--WHEN ID_TIPO_CREDITO = 26 THEN 'CASTIGO '
					ELSE ''
				END,
                /*IIF(ID_PRODUCTO= 50, 'CONSUMO ', ''),IIF(ID_PRODUCTO= 51, 'EMPLEADO ', ''),
				IIF( (ID_CUENTA = '2076' OR ID_CUENTA = '1020010502130300') AND ID_PRODUCTO= 50, 'EXEM ', ''),*/ -- VALIDAR 
				IIF(TIP_TRANSACCION = 113 OR (TIP_TRANSACCION = 4 AND RUBRO = 'SALDO_FAVOR'), '', IIF(CONCEPTO='PREPAGO',dbo.FN_RUBRO_POL(RUBRO)+' CANC ',dbo.FN_RUBRO_POL(RUBRO))/* + ' '*/)  --# Si no es saldo a favor le agrega el rubro
				) 
			WHERE FECHA_MOVIMIENTO = @FECHA_INICIO
			AND ID_POLIZA = @ID_POLIZA AND RUBRO != '' AND ID_TIPO_CREDITO = 5

		--- VALIDAR
		UPDATE PO.SAF_MOV_ABONO
		SET CONCEPTO_ANT = 
		IIF(CONCEPTO LIKE '%CMR CANC CXC%', CONCEPTO, -- NUEVA, SOLO APLICA PARA CANC CXC Y TOMAR LAS CAS CUENTAS DIRECTO DEL CONCEPTO
		CONCAT('CMR PAGO'
                ,CASE
					WHEN TIP_TRANSACCION = 4 AND IND_FORMA_PAGO = 5 AND ID_PRODUCTO=50 THEN ' DESCARGA FAVOR CONSUMO'
					WHEN TIP_TRANSACCION = 4 AND IND_FORMA_PAGO = 5 AND ID_PRODUCTO=51 THEN ' DESCARGA FAVOR EMPLEADO'
					WHEN TIP_TRANSACCION = 4 AND IND_FORMA_PAGO = 5 THEN ' DESCARGA FAVOR'
					WHEN ID_CUENTA = 2080 THEN ' NO IDENTIFICADO'
					ELSE ' NO IDENTIFICADO'
				END)
		)-- END IF
        WHERE FECHA_MOVIMIENTO = @FECHA_INICIO
			AND ID_POLIZA = @ID_POLIZA
		
		------------- ###################################### ------------------------------------------------
		------------- ###################################### ------------------------------------------------

		--# Variables a usar para lectura linea a linea
		DECLARE  @ID_EXTERNO		VARCHAR(15),	@NUM_CREDITO		NUMERIC(8, 0), 
				 @ID_FONDEO		    INT, 			@ID_PRODUCTO		NUMERIC(3, 0), 
				 @TIP_TRANSACCION   VARCHAR(5),		@SUBTIP_TRANSAC		VARCHAR(5), 
				 @RUBRO			    VARCHAR(30),	@MONTO				NUMERIC(16, 2), 
				 @MON_PAGO_IVA		NUMERIC(16, 2), @TIPO_CREDITO		VARCHAR(255), 
				 @TIPO_VIVIENDA		VARCHAR(150),	@FECHA_MOVIMIENTO	DATE, 
				 @IND_ESTADO		VARCHAR(2),		@NOM_CLIENTE		VARCHAR(250),
				 @ID_TIPO_CREDITO   INT,			@IND_ETAPA			INT, 
				 @MAX_INDICE		INT,			@INDICE				INT = 0,
				 @IND_FORMA_PAGO	INT,			@NOMBRE_PRODUCTO	VARCHAR(355),
				 @IND_ETAPA_ANTERIOR INT,			@IND_ETAPA_ACTUAL	INT,
				 @FECHA_ACTUAL		DATE,			@FECHA_ANTERIOR		DATE,
				 @ID_FONDEO_ACTUAL	INT,			@ID_FONDEO_ANTERIOR	INT,
				 @FEC_APERTURA		DATE,			@MON_CREDITO		NUMERIC(16, 2),
				 @CEDIDO			VARCHAR(255),   @ID_SECUENCIA	    INT,
				 @ID_CUENTA	        VARCHAR(25),	@ID_UNICO			VARCHAR(150),
				 @CONCEPTO	        VARCHAR(150),	@LEYENDA			VARCHAR(70),
				 @QUERY				VARCHAR(MAX),   @BANDERA			INT,
				 @TOTAL				DECIMAL(16,2) = 0,	@EL_RUBRO			VARCHAR(30) = '',
				 @ORDEN				DECIMAL(16,2),	@MONTO_BALANCE		DECIMAL(16,2),
				 @NUM_CREDITO_ANT	NUMERIC(8, 0) = 0,
				 @CONCEPTO_FINAL	VARCHAR(30),	@APELLIDO			VARCHAR(30)
				 ,@CANAL			VARCHAR(30)
			 
        declare @MONTO_OFFSET numeric(16,6),@ORDEN_TOT numeric(16,6),@DIAS_PERIODO_INTERNO int,@fecha_ref date, @Dias_offset int


		--# variables para uso de la separacion balance/orden
		DECLARE @SUMA89 NUMERIC(16, 2), @SUMA90 NUMERIC(16, 2), @FAVOR NUMERIC(16, 2), @IMPAGO DATE, @ETAPA_3_INI  DATE, @DIA_CORTE int
		
		--# Tabla temporal para almacenar la fila a trabajar
		DECLARE @MOVS TABLE (ID INT, ID_EXTERNO VARCHAR(15), NUM_CREDITO NUMERIC(8, 0), NOM_CLIENTE VARCHAR(250), ID_PRODUCTO NUMERIC(3,0), 
							NOMBRE_PRODUCTO VARCHAR(355), ID_FONDEO INT, TIP_TRANSACCION VARCHAR(5), SUBTIP_TRANSAC VARCHAR(5),
							RUBRO VARCHAR(30), MONTO NUMERIC(16, 2), MON_PAGO_IVA NUMERIC(16,2), ID_TIPO_CREDITO INT, 
							TIPO_CREDITO VARCHAR(255), TIPO_VIVIENDA VARCHAR(150), FECHA_MOVIMIENTO DATETIME, IND_ESTADO VARCHAR(2), 
							CARTERA_VENCIDA VARCHAR(2), IND_ETAPA INT, IND_FORMA_PAGO INT, FEC_APERTURA DATE, CEDIDO VARCHAR(255),
							MON_CREDITO NUMERIC(16, 2), ID_SECUENCIA	INT, ID_REFERENCIA INT, ID_CUENTA	VARCHAR(25), ID_UNICO VARCHAR(150), CONCEPTO VARCHAR(150),
							CONCEPTO_FINAL VARCHAR(30), APELLIDO VARCHAR(30), CANAL VARCHAR(30))

		--# Se insertan todos los registros que se trabajaran con un indice a la tabla temporal
		INSERT INTO @MOVS (ID, ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, ID_PRODUCTO,
							NOMBRE_PRODUCTO, ID_FONDEO, TIP_TRANSACCION, SUBTIP_TRANSAC,
							RUBRO, MONTO, MON_PAGO_IVA, ID_TIPO_CREDITO, 
							TIPO_CREDITO, TIPO_VIVIENDA, FECHA_MOVIMIENTO, IND_ESTADO, 
							IND_ETAPA, IND_FORMA_PAGO, FEC_APERTURA, CEDIDO, MON_CREDITO, ID_SECUENCIA, ID_REFERENCIA, ID_CUENTA, ID_UNICO, CONCEPTO,
							CONCEPTO_FINAL, APELLIDO, CANAL)
		SELECT 
			ROW_NUMBER() OVER (ORDER BY NUM_CREDITO, RUBRO, ID_SECUENCIA, ID_REFERENCIA) ID
			,ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, ID_PRODUCTO, 
			NOMBRE_PRODUCTO, ID_FONDEO, TIP_TRANSACCION, SUBTIP_TRANSAC
			,RUBRO, MONTO, MON_PAGO_IVA, ID_TIPO_CREDITO, 
			TIPO_CREDITO, TIPO_VIVIENDA, FECHA_MOVIMIENTO, IND_ESTADO, 
			IND_ETAPA, IND_FORMA_PAGO, FEC_APERTURA, CEDIDO, MON_CREDITO, ID_SECUENCIA, ID_REFERENCIA, ID_CUENTA, ID, CONCEPTO,
			CONCEPTO_FINAL, APELLIDO, CANAL
			FROM PO.SAF_MOV_ABONO
            WHERE FECHA_MOVIMIENTO = @FECHA_INICIO
			    AND ID_POLIZA = @ID_POLIZA
                AND IND_ETAPA = 3
				AND RUBRO NOT IN ('PRINCIPAL','SALDO_FAVOR','COMISION_PREPAGO','IVA COMISION_PREPAGO') 
				AND CONCEPTO NOT LIKE '%COVID%' 


		--# Se obtiene el tamaño total de registros
		SELECT @MAX_INDICE = COUNT(ID) FROM @MOVS
		WHILE @INDICE < @MAX_INDICE	BEGIN
			--# BLOC: lee todos los campos del registro actual
			SELECT 
				@ID_EXTERNO = ID_EXTERNO, @NUM_CREDITO = NUM_CREDITO, @NOM_CLIENTE = NOM_CLIENTE, @ID_PRODUCTO = ID_PRODUCTO, 
				@NOMBRE_PRODUCTO = NOMBRE_PRODUCTO, @ID_FONDEO = ID_FONDEO, @TIP_TRANSACCION = TIP_TRANSACCION, @SUBTIP_TRANSAC = SUBTIP_TRANSAC,
				@RUBRO = RUBRO, @MONTO = ABS(MONTO), @MON_PAGO_IVA = MON_PAGO_IVA, @ID_TIPO_CREDITO = ID_TIPO_CREDITO, 
				@TIPO_CREDITO = TIPO_CREDITO, @TIPO_VIVIENDA = TIPO_VIVIENDA, @FECHA_MOVIMIENTO = FECHA_MOVIMIENTO, 
				@IND_ESTADO = IND_ESTADO, @IND_ETAPA = IND_ETAPA, @IND_FORMA_PAGO = IND_FORMA_PAGO, @FEC_APERTURA = FEC_APERTURA, @CEDIDO = CEDIDO, @MON_CREDITO = MON_CREDITO,
				@IND_ETAPA_ACTUAL = IND_ETAPA, @FECHA_ACTUAL = FECHA_MOVIMIENTO, @ID_FONDEO_ACTUAL = ID_FONDEO,
				@ID_SECUENCIA = ID_SECUENCIA, @ID_CUENTA = ID_CUENTA, @ID_UNICO = ID_UNICO, @CONCEPTO = CONCEPTO,
				@CONCEPTO_FINAL = CONCEPTO_FINAL, @APELLIDO = APELLIDO, @CANAL = CANAL
			FROM @MOVS WHERE ID = @INDICE + 1
			--# BLOC_END

			--# BLOC: inicializan variables
			SELECT @IND_ETAPA_ANTERIOR = 0, @FECHA_ANTERIOR = NULL, @ID_FONDEO_ANTERIOR = NULL, @LEYENDA = ''
			--# BLOC_END

			--# BLOC: toma valores dia anterior
			SELECT @IND_ETAPA_ANTERIOR = IND_ETAPA, @FECHA_ANTERIOR = FECHA_SISTEMA, @ID_FONDEO_ANTERIOR = ID_FONDEO
			FROM PO.CONTROL_HISTORICO_TRASPASOS WITH (NOLOCK)
			WHERE NUM_CREDITO = @NUM_CREDITO AND FECHA_SISTEMA = DATEADD(day, -1, @FECHA_MOVIMIENTO)
			--# BLOC_END

--print '|@NUM_CREDITO:|'+isnull(cast(@NUM_CREDITO as varchar),'')+'|@IND_ETAPA_ACTUAL:|'+isnull(cast(@IND_ETAPA_ACTUAL as varchar),'')+'|@IND_ETAPA_ANTERIOR:|'+isnull(cast(@IND_ETAPA_ANTERIOR as varchar),'')

			-- # TRATAMIENTO PARA SEPARACION DE CUENTAS BALANCE/ORDEN ETAPA 3    @IND_ETAPA_ANTERIOR
			--IF (@IND_ETAPA_ACTUAL = 3 OR @IND_ETAPA_ACTUAL = 1) AND @DE_TIPO = 'new' AND @RUBRO
       --print '|NUM_CREDITO:|'+isnull(cast(@NUM_CREDITO as varchar),'')+'|NUM_CREDITO_ANT:|'+isnull(cast(@NUM_CREDITO_ANT as varchar),'')+'|RUBRO:|'+isnull(cast(@RUBRO as varchar),'')+'|EL_RUBRO:|'+isnull(cast(@EL_RUBRO as varchar),'')
			        IF @NUM_CREDITO != @NUM_CREDITO_ANT BEGIN
				        --UPDATE PO.CALC_BALANCE_ORDEN SET MONTO_BALANCE = @SUMA89 - @TOTAL WHERE NUM_Credito = @NUM_CREDITO_ANT AND RUBRO = @EL_RUBRO
				        SELECT @NUM_CREDITO_ANT = @NUM_CREDITO, @TOTAL = 0
                        --print '==============================================================='
                        --print '|CAMBIO Cred:|'+isnull(cast(@NUM_CREDITO as varchar),'')
			        END

					IF @EL_RUBRO != @RUBRO  BEGIN --- OR @NUM_CREDITO != @NUM_CREDITO_ANT
						/*IF @TOTAL != 0 BEGIN
							UPDATE PO.CALC_BALANCE_ORDEN SET MONTO_BALANCE = @SUMA89 - @TOTAL WHERE NUM_Credito = @NUM_CREDITO AND RUBRO = @EL_RUBRO
						END*/


						--# BLOC: inicializa variables, lee impago y balance
						SELECT @BANDERA = 0, @EL_RUBRO = @RUBRO, @TOTAL = 0, @SUMA89 = 0, @ORDEN = 0
                        --print '|CAMBIO rub:|'+isnull(cast(@RUBRO as varchar),'')
						--SELECT @IMPAGO = FECHA_INICIO, @SUMA89 = MONTO_BALANCE FROM PO.CALC_BALANCE_ORDEN WHERE NUM_CREDITO = @NUM_CREDITO AND RUBRO = @RUBRO

                        --------------------------------------------------------------------------------------------------------------------------
                        /*SELECT @ETAPA_3_INI = fec_reclasificacion
                        FROM Quiero_Confianza_shadow.PR.PR_RECLASIFICACION_ETAPA_RIESGO
                        where num_credito = @NUM_CREDITO
                            and (ind_etapa_act = 3 or (ind_etapa_act = 1 and ind_etapa_ant = 3 ))
                            and fec_reclasificacion In (
                                SELECT max(fec_reclasificacion)
                                FROM Quiero_Confianza_shadow.PR.PR_RECLASIFICACION_ETAPA_RIESGO
                                where num_credito = @NUM_CREDITO and not (ind_etapa_act = 1 and ind_etapa_ant = 3 )
                            )*/
						--############################ NUEVO BLOQUE #######################################################################
						--DECLARACION DE VARIABLES
						DECLARE @NUM_ASIENTO INT, @FEC_PAGO_ORIGINAL DATE
						
						-- OBTENER EL NUM_ASIENTO DEL REVERSO
						SELECT @NUM_ASIENTO = NUM_ASIENTO FROM Quiero_Confianza_shadow.PR.PR_ENCABEZADO_PAGO 
						WHERE NUM_CREDITO = @NUM_CREDITO AND Fec_movimiento = @FECHA_INICIO AND MON_MOVIMIENTO < 0
						
						-- CON EL NUM_ASIENTO, OBTENER LA FECHA DEL PAGO ORIGINAL
						SELECT @FEC_PAGO_ORIGINAL= FEC_MOVIMIENTO FROM Quiero_Confianza_shadow.PR.PR_ENCABEZADO_PAGO
						WHERE NUM_CREDITO = @NUM_CREDITO
						AND NUM_ASIENTO = @NUM_ASIENTO
						AND MON_MOVIMIENTO > 0 --BUSCAMOS MONTO POSITIVO
						AND COD_ESTADO = 'N' -- ANULADO
						
						-- COMPARAR FECHAS PARA ENTRAR A QUERY
						IF @FECHA_INICIO = @FEC_PAGO_ORIGINAL BEGIN 
							--SELECT 'FECHAS IGUALES' 
							-- QUERY SI LAS FECHAS SON IGUALES
							SELECT @ETAPA_3_INI = Fec_Reclasificacion
							FROM Quiero_Confianza_shadow.PR.PR_RECLASIFICACION_ETAPA_RIESGO
							where num_credito = @NUM_CREDITO
								and (ind_etapa_act = 3 or (ind_etapa_act = 1 and ind_etapa_ant = 3 ))
								and fec_reclasificacion In (
									SELECT max(fec_reclasificacion)
									FROM Quiero_Confianza_shadow.PR.PR_RECLASIFICACION_ETAPA_RIESGO
									where num_credito = @NUM_CREDITO and not (ind_etapa_act = 1 and ind_etapa_ant = 3 )
								)
							--SELECT @ETAPA_3_INI
						END
						ELSE BEGIN --SELECT 'FECHAS DIFERENTES' 
						-- QUERY SI LAS FECHAS SON DIFERENTES
							SELECT @ETAPA_3_INI = Fec_Reclasificacion
							FROM Quiero_Confianza_shadow.PR.PR_RECLASIFICACION_ETAPA_RIESGO
							where num_credito = @NUM_CREDITO
								and (ind_etapa_act = 3 or (ind_etapa_act = 1 and ind_etapa_ant = 3 ))
								and fec_reclasificacion In (
									SELECT max(fec_reclasificacion)
									FROM Quiero_Confianza_shadow.PR.PR_RECLASIFICACION_ETAPA_RIESGO
									where num_credito = @NUM_CREDITO and not (ind_etapa_act = 1 and ind_etapa_ant = 3 )
									AND FEC_RECLASIFICACION < @FECHA_INICIO AND IND_ETAPA_ACT = 3
								)
							--  SELECT @ETAPA_3_INI
						END

                        set @ETAPA_3_INI = dateadd(d,-2,@ETAPA_3_INI)

						--####################################################################################################################

                        --print '|ETAPA_3_INI:|'+isnull(cast(@ETAPA_3_INI as varchar),'')+'|NUM_CREDITO:|'+isnull(cast(@NUM_CREDITO as varchar),'')
						
                        if not @ETAPA_3_INI is null begin --se encuentra en etapa 3
                            if @RUBRO IN ('INTERESES') begin

                                SELECT @SUMA89 = ABS(isnull(sum(B.MON_PAGO),0)),@fecha_ref = max(FEC_COBRO)
                                FROM Quiero_Confianza_shadow.PR.PR_ENCABEZADO_PAGO A INNER JOIN
                                    Quiero_Confianza_shadow.PR.PR_DETALLE_PAGO B ON A.ID_SECUENCIA = B.ID_SECUENCIA INNER JOIN
                                    Quiero_Confianza_shadow.PR.PR_RUBRO_COBRO_X_CREDITO C ON C.NUM_SECUENCIA = B.ID_REFERENCIA AND A.NUM_CREDITO = C.NUM_CREDITO AND C.NUM_DET_SECUENCIA = B.NUM_DET_SECUENCIA AND C.COD_RUBRO = B.COD_CONCEPTO
                                WHERE A.TIP_TRANSACCION = 4 -- AND A.COD_ESTADO = 'A'
                                    AND C.NUM_CREDITO = @NUM_CREDITO
                                    and C.cod_rubro = @RUBRO
                                    and A.FEC_MOVIMIENTO = @FECHA_INICIO
                                    and C.FEC_EXIGIBLE_PAGO <= @ETAPA_3_INI


                                select @MONTO_OFFSET = isnull(sum(MON_DIARIO),0)
                                from Quiero_Confianza_shadow.PR.PR_CALCULO_INTERESES_DIA
                                where num_credito = @NUM_CREDITO
                                    and @fecha_ref <= fecha_calculo and fecha_calculo < @ETAPA_3_INI

                                if @SUMA89 > 0 begin
                                    set @SUMA89 = @SUMA89 + @MONTO_OFFSET
                                end

                                set @SUMA89 = isnull(@SUMA89,0)
		
                            end else if @RUBRO IN ('IVA INTERESES') begin

                                SELECT @SUMA89 = ABS(isnull(sum(B.MON_PAGO_IVA),0)),@fecha_ref = max(FEC_COBRO)
                                FROM Quiero_Confianza_shadow.PR.PR_ENCABEZADO_PAGO A INNER JOIN
                                    Quiero_Confianza_shadow.PR.PR_DETALLE_PAGO B ON A.ID_SECUENCIA = B.ID_SECUENCIA INNER JOIN
                                    Quiero_Confianza_shadow.PR.PR_RUBRO_COBRO_X_CREDITO C ON C.NUM_SECUENCIA = B.ID_REFERENCIA AND A.NUM_CREDITO = C.NUM_CREDITO AND C.NUM_DET_SECUENCIA = B.NUM_DET_SECUENCIA AND C.COD_RUBRO = B.COD_CONCEPTO
                                WHERE A.TIP_TRANSACCION = 4 -- AND A.COD_ESTADO = 'A'
									AND C.NUM_CREDITO = @NUM_CREDITO
                                    and C.cod_rubro = replace(@RUBRO,'IVA ','')
                                    and A.FEC_MOVIMIENTO = @FECHA_INICIO
                                    and C.FEC_EXIGIBLE_PAGO <= @ETAPA_3_INI

                                select @MONTO_OFFSET = isnull(sum(MON_DIARIO),0)*0.16
                                from Quiero_Confianza_shadow.PR.PR_CALCULO_INTERESES_DIA
                                where num_credito = @NUM_CREDITO
                                    and @fecha_ref <= fecha_calculo and fecha_calculo < @ETAPA_3_INI

                                if @SUMA89 > 0 begin
                                    set @SUMA89 = @SUMA89 + @MONTO_OFFSET
                                end

                                set @SUMA89 = isnull(@SUMA89,0)

                            end else if @RUBRO Like 'IVA%' begin

                                SELECT @SUMA89 = ABS(isnull(sum(B.MON_PAGO_IVA),0))
                                FROM Quiero_Confianza_shadow.PR.PR_ENCABEZADO_PAGO A INNER JOIN
                                    Quiero_Confianza_shadow.PR.PR_DETALLE_PAGO B ON A.ID_SECUENCIA = B.ID_SECUENCIA INNER JOIN
                                    Quiero_Confianza_shadow.PR.PR_RUBRO_COBRO_X_CREDITO C ON C.NUM_SECUENCIA = B.ID_REFERENCIA AND A.NUM_CREDITO = C.NUM_CREDITO AND C.NUM_DET_SECUENCIA = B.NUM_DET_SECUENCIA AND C.COD_RUBRO = B.COD_CONCEPTO
                                WHERE A.TIP_TRANSACCION = 4-- AND A.COD_ESTADO = 'A'
                                    AND C.NUM_CREDITO = @NUM_CREDITO
                                    and C.cod_rubro = replace(@RUBRO,'IVA ','')
                                    and A.FEC_MOVIMIENTO = @FECHA_INICIO
                                    and C.FEC_EXIGIBLE_PAGO <= @ETAPA_3_INI--C.fec_cobro <= @ETAPA_3_INI_1M

                            end else begin

                                SELECT @SUMA89 = ABS(isnull(sum(B.MON_PAGO),0))
                                FROM Quiero_Confianza_shadow.PR.PR_ENCABEZADO_PAGO A INNER JOIN
                                    Quiero_Confianza_shadow.PR.PR_DETALLE_PAGO B ON A.ID_SECUENCIA = B.ID_SECUENCIA INNER JOIN
                                    Quiero_Confianza_shadow.PR.PR_RUBRO_COBRO_X_CREDITO C ON C.NUM_SECUENCIA = B.ID_REFERENCIA AND A.NUM_CREDITO = C.NUM_CREDITO AND C.NUM_DET_SECUENCIA = B.NUM_DET_SECUENCIA AND C.COD_RUBRO = B.COD_CONCEPTO
                                WHERE A.TIP_TRANSACCION = 4-- AND A.COD_ESTADO = 'A'
                                    AND C.NUM_CREDITO = @NUM_CREDITO
                                    and C.cod_rubro = @RUBRO
                                    and A.FEC_MOVIMIENTO = @FECHA_INICIO
									AND C.FEC_EXIGIBLE_PAGO <= @ETAPA_3_INI
                                    --and C.fec_base_calc <= @ETAPA_3_INI--C.fec_cobro <= @ETAPA_3_INI_1M

                            end
                        end

                        --print '|NUM_CREDITO:|'+isnull(cast(@NUM_CREDITO as varchar),'')+'|RUBRO:|'+isnull(cast(@RUBRO as varchar),'')+'|@ETAPA_3_INI_1M:|'+isnull(cast(@ETAPA_3_INI_1M as varchar),'')+'|SUMA89:|'+isnull(cast(@SUMA89 as varchar),'')
					END

					--# BLOC: incrementa total
					SET  @TOTAL =  @TOTAL + @MONTO
					
					--# BLOC_END
		

					--#	SOLO SE VALIDA UNA UNICA OCACION SI EL PAGO DEBE DIVIDIRSE
                    --print '|@TOTAL:|'+isnull(cast(@TOTAL as varchar),'')+'|@MONTO:|'+isnull(cast(@MONTO as varchar),'')+'|@SUMA89:|'+isnull(cast(@SUMA89 as varchar),'')+'|@ORDEN:|'+isnull(cast(@ORDEN as varchar),'')+'|@BANDERA:|'+isnull(cast(@BANDERA as varchar),'')
					
					IF @BANDERA = 0 BEGIN
						IF @TOTAL > @SUMA89 AND @SUMA89 > 0 BEGIN
						--PRINT 'ENTRA'
						--PRINT @NUM_CREDITO
							SELECT @ORDEN = @TOTAL - @SUMA89, @BANDERA = 1
							IF @ORDEN != 0 BEGIN
							
									INSERT INTO PO.SAF_MOV_ABONO (ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, ID_FONDEO, ID_PRODUCTO,
											CONCEPTO, NOMBRE_PRODUCTO, RUBRO, MONTO, MON_PAGO_IVA, ID_TIPO_CREDITO, 
											TIPO_CREDITO, TIPO_VIVIENDA, FECHA_MOVIMIENTO, IND_ESTADO, IND_ETAPA, FEC_APERTURA, CEDIDO, TABLA_ORIGEN, ID_POLIZA,ID_SECUENCIA,ID_CUENTA, BANCO_RECEPTOR, REVERSO,
											CANAL)
									SELECT TOP 1 ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, ID_FONDEO, ID_PRODUCTO,
											REPLACE(CONCEPTO, 'PAGO ', 'PAGO CO '),
											NOMBRE_PRODUCTO, RUBRO, -1*@ORDEN, 0, ID_TIPO_CREDITO, 
											TIPO_CREDITO, TIPO_VIVIENDA, FECHA_MOVIMIENTO, IND_ESTADO, IND_ETAPA,
											FEC_APERTURA, CEDIDO, 'REVERSO COBRANZA COM', ID_POLIZA,ID_SECUENCIA,ID_CUENTA, BANCO_RECEPTOR, REVERSO,
											CANAL
									FROM PO.SAF_MOV_ABONO 
									WHERE ID_POLIZA = @ID_POLIZA
                                        AND ID = @ID_UNICO
                                        --AND CONCEPTO NOT LIKE '%COVID%' AND NUM_CREDITO = @NUM_CREDITO AND RUBRO = @RUBRO AND FECHA_MOVIMIENTO BETWEEN @FECHA_FIN AND @FECHA_FIN
									
									UPDATE PO.SAF_MOV_ABONO SET MONTO = MONTO + @ORDEN --, CONCEPTO = REPLACE(CONCEPTO, 'PAGO ', 'PAGO CO ') --COAA
									WHERE ID = @ID_UNICO                

									IF (@MONTO - @ORDEN) = 0 BEGIN
										DELETE FROM PO.SAF_MOV_ABONO  WHERE ID = @ID_UNICO	
									END
						
							END --# @ORDEN != 0
						
						END --# @TOTAL > @SUMA89 AND @SUMA89 >
					END

					IF @TOTAL >  @SUMA89 BEGIN
						IF @ORDEN <= 0 BEGIN
							UPDATE PO.SAF_MOV_ABONO SET CONCEPTO = REPLACE(CONCEPTO, 'PAGO ', 'PAGO CO ') --COBB
							WHERE ID = @ID_UNICO
						END
						SET  @ORDEN = 0

					END -- # @MONTO > @SUMA89

			SET @INDICE = @INDICE + 1
		END --# WHILE

		/*IF @TOTAL != 0 BEGIN
			UPDATE PO.CALC_BALANCE_ORDEN SET MONTO_BALANCE = @SUMA89 - @TOTAL WHERE NUM_Credito = @NUM_CREDITO AND RUBRO = @EL_RUBRO
		END*/

        declare @NUM_CREDITO_C int,@RUBRO_C varchar(30),@MONTO_C numeric(18,2)

        exec CursorCloseDeallocate 'db_cursor_poliza_cobranza_rev_cmr'

        DECLARE db_cursor_poliza_cobranza_rev_cmr CURSOR FOR

            select NUM_CREDITO,RUBRO,isnull(sum(MONTO),0)
            FROM PO.SAF_MOV_ABONO 
            WHERE ID_POLIZA = @ID_POLIZA AND FECHA_MOVIMIENTO = @FECHA_INICIO AND CONCEPTO LIKE '%PAGO CO %'
            group by NUM_CREDITO,RUBRO

        OPEN db_cursor_poliza_cobranza_rev_cmr  
            FETCH NEXT FROM db_cursor_poliza_cobranza_rev_cmr
            INTO @NUM_CREDITO_C, @RUBRO_C, @MONTO_C

        WHILE @@FETCH_STATUS = 0  
        BEGIN  

			INSERT INTO PO.SAF_MOV_ABONO (ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, ID_FONDEO, ID_PRODUCTO,
				    CONCEPTO, NOMBRE_PRODUCTO, RUBRO, MONTO, MON_PAGO_IVA, ID_TIPO_CREDITO, 
				    TIPO_CREDITO, TIPO_VIVIENDA, FECHA_MOVIMIENTO, IND_ESTADO, IND_ETAPA, FEC_APERTURA, CEDIDO, TABLA_ORIGEN, ID_POLIZA, REVERSO,
					CANAL, ID_SECUENCIA)
			SELECT TOP 1 ID_EXTERNO, NUM_CREDITO, NOM_CLIENTE, ID_FONDEO, ID_PRODUCTO,
				    replace(CONCEPTO,'PAGO CO ','PAGO CCO '),
				    NOMBRE_PRODUCTO, RUBRO, @MONTO_C, 0, ID_TIPO_CREDITO, 
				    TIPO_CREDITO, TIPO_VIVIENDA, FECHA_MOVIMIENTO, IND_ESTADO, IND_ETAPA,
				    FEC_APERTURA, CEDIDO, 'REVERSO COBRANZA COM', ID_POLIZA, REVERSO, CANAL, ID_SECUENCIA
			FROM PO.SAF_MOV_ABONO 
			WHERE ID_POLIZA = @ID_POLIZA AND NUM_CREDITO = @NUM_CREDITO_C AND RUBRO = @RUBRO_C AND FECHA_MOVIMIENTO = @FECHA_INICIO
                AND CONCEPTO LIKE '%PAGO CO %'
				AND ((ID_TIPO_CREDITO != 5) OR (ID_TIPO_CREDITO = 5 AND RUBRO NOT LIKE '%SEGURO%' AND RUBRO NOT LIKE '%IVA%')) -- MEZZANINE
			
            FETCH NEXT FROM db_cursor_poliza_cobranza_rev_cmr
            INTO @NUM_CREDITO_C, @RUBRO_C, @MONTO_C
        END 

        CLOSE db_cursor_poliza_cobranza_rev_cmr  
        DEALLOCATE db_cursor_poliza_cobranza_rev_cmr
		------------- ###################################### ------------------------------------------------
		------------- ###################################### ------------------------------------------------

		UPDATE H SET H.ID_CONCEPTO = C.ID
		FROM PO.SAF_MOV_ABONO H JOIN PO.SAF_CATALOGO_CONCEPTOS C ON C.CONCEPTO = H.CONCEPTO 
		WHERE H.FECHA_MOVIMIENTO = @FECHA_INICIO
		AND H.ID_POLIZA = @ID_POLIZA

		UPDATE H SET H.ID_CONCEPTO_ANT = C.ID
		FROM PO.SAF_MOV_ABONO H JOIN PO.SAF_CATALOGO_CONCEPTOS C ON C.CONCEPTO = H.CONCEPTO_ANT 
		WHERE H.FECHA_MOVIMIENTO = @FECHA_INICIO
		AND H.ID_POLIZA = @ID_POLIZA

		--- ASIGNACION DE CUENTAS
		UPDATE H SET 
			H.CUENTA_CARGO = CC.CUENTA_CARGO
		FROM PO.SAF_MOV_ABONO H JOIN PO.SAF_CAT_CONTABLE CC ON H.ID_CONCEPTO_ANT = CC.ID_CONCEPTO 
		WHERE FECHA_MOVIMIENTO = @FECHA_INICIO
		AND H.ID_POLIZA = @ID_POLIZA

		UPDATE H SET 
			H.CUENTA_CARGO = CC.CUENTA_CARGO
		FROM PO.SAF_MOV_ABONO H JOIN PO.SAF_CAT_CONTABLE CC ON H.ID_CONCEPTO = CC.ID_CONCEPTO 
		WHERE FECHA_MOVIMIENTO = @FECHA_INICIO
		AND H.ID_POLIZA = @ID_POLIZA and H.CUENTA_CARGO is null

		UPDATE H SET 
			H.CUENTA_ABONO = CC.CUENTA_ABONO
		FROM PO.SAF_MOV_ABONO H JOIN PO.SAF_CAT_CONTABLE CC ON H.ID_CONCEPTO = CC.ID_CONCEPTO 
		WHERE FECHA_MOVIMIENTO = @FECHA_INICIO
		AND H.ID_POLIZA = @ID_POLIZA

		----------- ########### Valida si hay cuenta SAF
		UPDATE H
			SET H.CUENTA_CARGO = IIF(C.CUENTA_MASCARA IS NULL, D.CUENTA_MASCARA, C.CUENTA_MASCARA)
		FROM
			PO.SAF_MOV_ABONO H
			LEFT JOIN Quiero_Confianza_shadow.BA.BA_CTA_CORRIENTE B ON H.ID_CUENTA = CAST( B.ID_CUENTA AS VARCHAR(50))
			LEFT JOIN Quiero_Confianza_shadow.CG.CG_CATALOGO_X_EMPRESA C ON B.CTA_CONTABLE = C.CUENTA_CONTABLE
			LEFT JOIN Quiero_Confianza_shadow.CG.CG_CATALOGO_X_EMPRESA D ON CAST( H.ID_CUENTA AS VARCHAR(50))= D.CUENTA_CONTABLE
		WHERE 
			H.CUENTA_CARGO = 'Cuenta SAF'
			AND H.FECHA_MOVIMIENTO = @FECHA_INICIO
			AND H.ID_POLIZA = @ID_POLIZA

		UPDATE H
			SET H.CUENTA_ABONO = IIF(C.CUENTA_MASCARA IS NULL, D.CUENTA_MASCARA, C.CUENTA_MASCARA)
		FROM
			PO.SAF_MOV_ABONO H
			LEFT JOIN Quiero_Confianza_shadow.BA.BA_CTA_CORRIENTE B ON H.ID_CUENTA = B.ID_CUENTA
			LEFT JOIN Quiero_Confianza_shadow.CG.CG_CATALOGO_X_EMPRESA C ON B.CTA_CONTABLE = C.CUENTA_CONTABLE
			LEFT JOIN Quiero_Confianza_shadow.CG.CG_CATALOGO_X_EMPRESA D ON CAST( H.ID_CUENTA AS VARCHAR(50))= D.CUENTA_CONTABLE
		WHERE 
			H.CUENTA_ABONO = 'Cuenta SAF'
			AND H.FECHA_MOVIMIENTO = @FECHA_INICIO
			AND H.ID_POLIZA = @ID_POLIZA
	    

		--no deben quedar nulos en las cuentas
        UPDATE PO.SAF_MOV_ABONO
        SET   CUENTA_ABONO = ''
		WHERE FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA
            and CUENTA_ABONO is null

		UPDATE PO.SAF_MOV_ABONO
        SET   CUENTA_CARGO = ''
		WHERE FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA
            and CUENTA_CARGO is null

		-- >>>>>>>>>>>>>>>>>>>>>>>>>>> GENERACION DE CONCEPTO FINAL <<<<<<<<<<<<<<<<<<<<<<<<<<<
		/*
		--- SE CREA TABLA PARA LOS NUMERO DE SECUENCIA
		DECLARE @SEC TABLE (ID_SECUENCIA INT)
		INSERT INTO @SEC (ID_SECUENCIA) SELECT DISTINCT(ID_SECUENCIA) FROM PO.SAF_MOV_ABONO 
		WHERE FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA
		    AND ID_SECUENCIA IS NOT NULL

		--- VARIABLES PARA RECORRER LOS ID_SECUENCIA
		DECLARE @CS INT = 0, @INDICE_S INT = 0, @SEC_S INT = 0
		SELECT @CS = COUNT(ID_SECUENCIA) FROM @SEC

		--- CICLO PARA ACTUALIZAR TIPO_DEP
		WHILE @INDICE_S < @CS	BEGIN		
			SELECT TOP 1 @SEC_S = ID_SECUENCIA FROM @MOVS
		
			IF EXISTS(SELECT TOP (1) 1 FROM PO.SAF_MOV_ABONO WHERE ID_SECUENCIA = @SEC_S AND TIP_TRANSACCION=3) BEGIN
				UPDATE PO.SAF_MOV_ABONO SET TIPO_DEP = 4 WHERE ID_SECUENCIA = @SEC_S AND FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA		
			END

			ELSE IF EXISTS(SELECT TOP (1) 1 FROM PO.SAF_MOV_ABONO WHERE ID_SECUENCIA = @SEC_S AND ID_TIPO_CREDITO = 4 AND CUENTA_CARGO= '1020-0105-0205-0100') BEGIN
				UPDATE PO.SAF_MOV_ABONO SET TIPO_DEP = 3 WHERE ID_SECUENCIA = @SEC_S AND FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA
			END 

			ELSE IF EXISTS(SELECT TOP (1) 1 FROM PO.SAF_MOV_ABONO WHERE ID_SECUENCIA = @SEC_S AND CONCEPTO LIKE 'SALDO_FAVOR%')	BEGIN
				UPDATE PO.SAF_MOV_ABONO SET TIPO_DEP = 1 WHERE ID_SECUENCIA = @SEC_S AND FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA		
			END
			ELSE IF EXISTS(SELECT TOP (1) 1 FROM PO.SAF_MOV_ABONO WHERE ID_SECUENCIA = @SEC_S AND CONCEPTO LIKE 'PAGO SALDO_FAVOR%')	BEGIN
				UPDATE PO.SAF_MOV_ABONO SET TIPO_DEP = 2 WHERE ID_SECUENCIA = @SEC_S AND FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA	
			END
	
			DELETE FROM @MOVS WHERE ID_SECUENCIA = @SEC_S
			SET @INDICE_S = @INDICE_S + 1
		END -- END WHILE
        */

	    UPDATE PO.SAF_MOV_ABONO SET TIPO_DEP = 1 WHERE FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA AND CONCEPTO LIKE 'SALDO_FAVOR %'	
        UPDATE PO.SAF_MOV_ABONO SET TIPO_DEP = 2 WHERE FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA and (CONCEPTO LIKE 'PAGO SALDO_FAVOR %' OR CONCEPTO LIKE 'PAGO CO SALDO_FAVOR %')
	   

		UPDATE PO.SAF_MOV_ABONO
			SET CONCEPTO_FINAL= 
			LEFT(CASE
				WHEN CONCEPTO LIKE '%CANC CXC%' THEN CONCEPTO
			ELSE
				CONCAT( 
					CASE
						WHEN TIPO_DEP = 2 THEN 'DESCARGA FAVOR '
						ELSE 'DEP '
					END, 
					CASE
						WHEN TIPO_DEP = 2 THEN CONCAT(dbo.FN_SECUENCIA_ORIGEN(ID_SECUENCIA), ' ', NOMBRE_PRODUCTO,' ',IIF(ID_FONDEO=2,'NO RESTRINGIDO ','RESTRINGIDO '),IND_ETAPA)
					    ELSE CONCAT(ID_EXTERNO, ' ', dbo.FN_SECUENCIA_ORIGEN(ID_SECUENCIA), ' ', NOM_CLIENTE)
					END)
			END, 96) -- CON LEFT SE ASEGURA QUE EL CONCEPTO NO SOBREPASE EL NUMERO DE CARACTERES DETERMINADO PARA EL CONCEPTO
			WHERE FECHA_MOVIMIENTO = @FECHA_INICIO AND ID_POLIZA = @ID_POLIZA
		
		--    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GENERACION DE POLIZA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

	    CREATE TABLE #POLIZA (CONCEPTO VARCHAR(255),CUENTA VARCHAR(355),MONTO_CARGO MONEY, MONTO_ABONO MONEY, ID_SECUENCIA INT)
	    CREATE TABLE #POLIZAF(CONCEPTO VARCHAR(255),CUENTA VARCHAR(355),MONTO_CARGO MONEY, MONTO_ABONO MONEY, ID_SECUENCIA INT)

		INSERT INTO #POLIZA (CONCEPTO, CUENTA, MONTO_CARGO, MONTO_ABONO, ID_SECUENCIA) 
		SELECT CONCEPTO_FINAL, A.CUENTA_ABONO AS CUENTA, 
			   CAST(0.00 AS decimal (16,2)) AS MONTO_CARGO,
			   CAST(SUM(MONTO) AS decimal (16,2)) AS MONTO_ABONO,
			   ID_SECUENCIA
		FROM [PO].[SAF_MOV_ABONO] A 
		WHERE FECHA_MOVIMIENTO = @FECHA_INICIO
				AND A.ID_POLIZA = @ID_POLIZA
				AND A.CUENTA_ABONO LIKE '7017-%'
		GROUP BY A.CUENTA_ABONO, CONCEPTO_FINAL, ID_SECUENCIA
		
		INSERT INTO #POLIZA (CONCEPTO, CUENTA, MONTO_CARGO, MONTO_ABONO, ID_SECUENCIA) 
		SELECT CONCEPTO_FINAL,
			A.CUENTA_CARGO AS CUENTA, 
			CAST(SUM(MONTO) AS decimal (16,2)) AS MONTO_CARGO, 
			CAST(0.00 AS decimal (16,2)) AS MONTO_ABONO,
            ID_SECUENCIA
        FROM [PO].[SAF_MOV_ABONO] A 
        WHERE FECHA_MOVIMIENTO = @FECHA_INICIO
				AND A.ID_POLIZA = @ID_POLIZA
		GROUP BY A.CUENTA_CARGO, A.CONCEPTO_FINAL, ID_SECUENCIA
		
	    INSERT INTO #POLIZA (CONCEPTO, CUENTA, MONTO_CARGO, MONTO_ABONO, ID_SECUENCIA) 
		SELECT IIF(CONCEPTO_ANT LIKE '%DESCARGA FAVOR%',
			   CONCAT('SALDO_FAVOR ', dbo.FN_SECUENCIA_ORIGEN(A.ID_SECUENCIA), ' ', A.NOMBRE_PRODUCTO,' ',IIF(A.ID_FONDEO=2,'NO RESTRINGIDO ','RESTRINGIDO '),A.IND_ETAPA),CONCEPTO_FINAL),	 
				A.CUENTA_ABONO CUENTA, 
				CAST(0.00 AS decimal (16,2)) AS MONTO_CARGO,
				CAST(SUM(MONTO) AS decimal (16,2)) AS MONTO_ABONO,
				ID_SECUENCIA
		FROM [PO].[SAF_MOV_ABONO] A 
        WHERE FECHA_MOVIMIENTO = @FECHA_INICIO
				AND A.ID_POLIZA = @ID_POLIZA
				AND A.CUENTA_CARGO NOT LIKE '7016-%'
		GROUP BY A.CUENTA_ABONO, CONCEPTO_FINAL, CONCEPTO_ANT, A.NOMBRE_PRODUCTO,A.ID_FONDEO,A.IND_ETAPA, ID_SECUENCIA


        -- se actualizan los conceptos para marcarlos como reversos
		UPDATE #POLIZA
		SET CONCEPTO = 'REV '+CONCEPTO
        where not CONCEPTO like 'REV %'

		INSERT INTO #POLIZAF(CONCEPTO, CUENTA, MONTO_CARGO, MONTO_ABONO)
		SELECT               CONCEPTO, CUENTA,
			SUM(MONTO_CARGO) CARGO, 
			SUM(MONTO_ABONO) ABONO
		FROM #POLIZA
		WHERE CONCEPTO LIKE 'DEP %'  OR CUENTA LIKE '7016-%'
		GROUP BY CONCEPTO, CUENTA, ID_SECUENCIA

		INSERT INTO #POLIZAF(CONCEPTO, CUENTA, MONTO_CARGO, MONTO_ABONO)
		SELECT               CONCEPTO, CUENTA,
			SUM(MONTO_CARGO) CARGO, 
			SUM(MONTO_ABONO) ABONO
		FROM #POLIZA
		WHERE CONCEPTO NOT LIKE 'DEP %' AND CUENTA NOT LIKE '7016-%'
		GROUP BY CONCEPTO, CUENTA, ID_SECUENCIA


        exec [PO].[SP_SAF_POLIZA_FINALIZA] @FECHA_INICIO, @ID_POLIZA

		COMMIT
	END TRY
	BEGIN CATCH
		ROLLBACK

        INSERT INTO PO.SAF_POLIZA_ERRORES
               (FECHA_GENERACION, FECHA_SISTEMA, ID_POLIZA, DESCRIPCION)
        VALUES (getdate()       ,@FECHA_INICIO ,@ID_POLIZA, 'Linea:'+cast(ERROR_LINE() as varchar)+'. '+ERROR_MESSAGE())

	END CATCH
	
END
GO
