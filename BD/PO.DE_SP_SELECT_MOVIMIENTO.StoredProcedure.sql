SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE   PROC [PO].[DE_SP_SELECT_MOVIMIENTO]
(
	@ID_DESEMBOLSO	 UNIQUEIDENTIFIER
)
AS BEGIN
	SELECT [ID]
      ,[ID_DESEMBOLSO] as IdDesembolso
	  ,[ORDEN] as Orden
      ,[CONCEPTO] as Concepto
      ,[MONTO] as Monto
      ,[CUENTA_DEPOSITAR] as CuentaDepositar
      ,[CLABE_INTERBANCARIA] as ClabeInterbancaria
      ,[BANCO_BENEFICIARIO] as BancoBeneficiario
      ,[NOMBRE_BENEFICIARIO] as NombreBeneficiario
      ,[NUMERO_DESEMBOLSO] as NumeroDesembolso
	  ,[FECHA_FONDEO] as FechaFondeo
	  ,[BANCO_ORIGEN] as BancoOrigen
	  ,[CUENTA_ORIGEN] as CuentaOrigen
	  ,[FECHA_FONDEO_SOLICITADO] as FechaFondeoSolicitado
	  ,[ERROR] as Error
      ,[REGISTRADO_POR] as RegistradoPor
      ,[CREADO] as Creado
      ,[ACTUALIZADO] as Actualizado
	FROM 
		[KARDIA].[PO].[DE_MOVIMIENTO] m
	WHERE 
		m.ID_DESEMBOLSO = @ID_DESEMBOLSO
	ORDER BY m.ORDEN
END
GO
