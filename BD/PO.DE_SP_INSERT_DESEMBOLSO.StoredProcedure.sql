SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE   PROC [PO].[DE_SP_INSERT_DESEMBOLSO]
(
	@ID_EXTERNO		 VARCHAR(20),
	@REGISTRADO_POR  VARCHAR(100)	
)
AS BEGIN
	DECLARE @ID UNIQUEIDENTIFIER
	DECLARE @NUM_CREDITO INT
		
	-- buscar si hay un credito mas reciente que los existentes
	SET @NUM_CREDITO = (	
		select max(c.NUM_CREDITO) as NUM_CREDITO
		from [Quiero_Confianza].[PR].[PR_CREDITOS] c
		where
			c.IND_LINEA = 'N'
			and c.ID_EXTERNO = @ID_EXTERNO
			and not exists (
				select 1 from [KARDIA].[PO].[DE_DESEMBOLSO] d 
				where c.COD_EMPRESA = d.COD_EMPRESA
				and c.COD_AGENCIA = d.COD_AGENCIA
				and c.NUM_CREDITO = d.NUM_CREDITO
				and c.ID_EXTERNO = d.ID_EXTERNO
			)	
		group by c.id_externo
	)
	print @NUM_CREDITO
	IF @NUM_CREDITO is not null and @NUM_CREDITO > 0 BEGIN
		SET @ID = NEWID();
		INSERT INTO [PO].[DE_DESEMBOLSO]
			([ID]
			,[COD_EMPRESA]
			,[COD_AGENCIA]
			,[NUM_CREDITO]
			,[ID_EXTERNO]
			,[DESC_ESTATUS]
			,[REGISTRADO_POR], [CREADO], [ACTUALIZADO])
		SELECT
			@ID,
			c.COD_EMPRESA,
			c.COD_AGENCIA,
			c.NUM_CREDITO,
			c.ID_EXTERNO,
			'' as DESC_ESTATUS,
			@REGISTRADO_POR, getdate(), null
		FROM 
			[Quiero_Confianza_shadow].[PR].[PR_CREDITOS] c
		WHERE 
			c.NUM_CREDITO = @NUM_CREDITO
	END
	ELSE BEGIN
		SET @ID = (
			select ID 
			from [KARDIA].po.DE_DESEMBOLSO d 
			where d.NUM_CREDITO = (select max(c.NUM_CREDITO) as NUM_CREDITO
				from [Quiero_Confianza].[PR].[PR_CREDITOS] c
				where
					c.IND_LINEA = 'N'
					and c.ID_EXTERNO = @ID_EXTERNO
				group by c.id_externo
			)
		)
	END
	print 'id'
	print @ID
	IF @ID is not null BEGIN
		 EXEC [KARDIA].[PO].[DE_SP_SELECT_DESEMBOLSO] @ID
	END
END
GO
