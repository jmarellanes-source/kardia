SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE   PROC [PO].[DE_SP_SELECT_DESEMBOLSO]
(
	@ID	 UNIQUEIDENTIFIER	
)
AS BEGIN
	SELECT
		d.ID,
		d.COD_EMPRESA as CodEmpresa,
		d.COD_AGENCIA as CodAgencia,	
		d.NUM_CREDITO as NumCredito,
		d.ID_EXTERNO as IdExterno,
		c.TIP_CREDITO as TipCredito,
		tc.DES_TIP_CREDITO as DesTipCredito,
		c.MON_CREDITO as MonCredito,
		c.FEC_APERTURA as FechaApertura,
		p.COD_CLIENTE as CodCliente,
		[KARDIA].[dbo].FN_FORMA_NOMBRE(p.PRIMER_APELLIDO, p.SEGUNDO_APELLIDO, p.PRIMER_NOMBRE, p.SEGUNDO_NOMBRE, null, null)  Titular,
		coalesce(d.DESC_ESTATUS, '') as DesEstatus,
		(select coalesce(sum(m.MONTO), 0) from [KARDIA].[PO].[DE_MOVIMIENTO] m where m.ID_DESEMBOLSO = d.ID and coalesce(m.ERROR, '') = '') MontoDesembolsos,
		d.REGISTRADO_POR as RegistradoPor,
		d.CREADO as Creado,
		d.ACTUALIZADO as Actualizado
	FROM 
		[KARDIA].[PO].[DE_DESEMBOLSO] d
		inner join [Quiero_Confianza_shadow].[PR].[PR_CREDITOS] c on d.COD_EMPRESA = c.COD_EMPRESA and d.COD_AGENCIA = c.COD_AGENCIA and d.NUM_CREDITO = c.NUM_CREDITO
		left join [Quiero_Confianza_shadow].[PR].[PR_TIPO_CREDITO] tc on c.COD_EMPRESA = tc.COD_EMPRESA and c.tip_credito = tc.tip_credito
		left join [Quiero_Confianza_shadow].[CL].[CL_PERSONAS_FISICAS] p on p.COD_EMPRESA = c.COD_EMPRESA and p.COD_CLIENTE = c.COD_CLIENTE
	WHERE 
		d.id = coalesce(@ID, d.id) -- se usa para obtener todos los creditos consultados previamente en el modulo de desembolsos o 1 por id
END
GO
