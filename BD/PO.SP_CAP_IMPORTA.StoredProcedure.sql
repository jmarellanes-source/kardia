SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Autor:		Eneas Armas
-- Creacion: 	20250529
-- Descripcion:	Realiza la importacion de un txt separado por | para las polizas de captacion
-- =============================================
CREATE PROCEDURE [PO].[SP_CAP_IMPORTA]
	@archivo varchar(max)
AS
BEGIN
	SET NOCOUNT ON;

    create table #Poliza(
         ID int
        ,IDLOTE varchar(12)
        ,IDLINEA int
        ,CONCEPTO varchar(256)
        ,CUENTA varchar(20)
        ,CARGO numeric(16,2)
        ,ABONO numeric(16,2)
        ,TIPO_POLIZA varchar(50)
        ,DYNAMICS varchar(5)
        ,FECHA date
    )

    declare @ini int,@fin int,@tamano int,@linea int,@renglon varchar(max)
    ,@ID int
    ,@IDLOTE varchar(12)
    ,@IDLINEA int
    ,@CONCEPTO varchar(256)
    ,@CUENTA varchar(20)
    ,@CARGO numeric(16,2)
    ,@ABONO numeric(16,2)
    ,@TIPO_POLIZA varchar(50)
    ,@DYNAMICS varchar(5)
    ,@FECHA varchar(10)

    ,@E_TIPO_POLIZA varchar(50)
    ,@E_DYNAMICS varchar(5)
    ,@E_FECHA date
    ,@ID_POLIZA int

    ,@ind1 int
    ,@ind2 int
    ,@ind3 int
    ,@ind4 int
    ,@ind5 int
    ,@ind6 int
    ,@ind7 int
    ,@ind8 int
    ,@ind9 int

    set @linea = 0
    set @tamano = LEN(@archivo)+1
    set @ini = 1 
    set @fin = CHARINDEX(CHAR(13),@archivo)

    while @ini < @fin begin

        set @renglon = replace(replace(SUBSTRING(@archivo,@ini,@fin-@ini),CHAR(10),''),CHAR(13),'')
        set @linea = @linea + 1
        if @linea > 1 begin
            --print @renglon

            set @ind1 = CHARINDEX('|',@renglon,1)
            set @ind2 = CHARINDEX('|',@renglon,@ind1+1)
            set @ind3 = CHARINDEX('|',@renglon,@ind2+1)
            set @ind4 = CHARINDEX('|',@renglon,@ind3+1)
            set @ind5 = CHARINDEX('|',@renglon,@ind4+1)
            set @ind6 = CHARINDEX('|',@renglon,@ind5+1)
            set @ind7 = CHARINDEX('|',@renglon,@ind6+1)
            set @ind8 = CHARINDEX('|',@renglon,@ind7+1)
            set @ind9 = CHARINDEX('|',@renglon,@ind8+1)

            if @ind9 > 0 begin

                set @ID          = SUBSTRING(@renglon,1      ,@ind1-1)
                set @IDLOTE      = SUBSTRING(@renglon,@ind1+1,@ind2-@ind1-1)
                set @IDLINEA     = SUBSTRING(@renglon,@ind2+1,@ind3-@ind2-1)
                set @CONCEPTO    = SUBSTRING(@renglon,@ind3+1,@ind4-@ind3-1)
                set @CUENTA      = SUBSTRING(@renglon,@ind4+1,@ind5-@ind4-1)
                set @CARGO       = SUBSTRING(@renglon,@ind5+1,@ind6-@ind5-1)
                set @ABONO       = SUBSTRING(@renglon,@ind6+1,@ind7-@ind6-1)
                set @TIPO_POLIZA = SUBSTRING(@renglon,@ind7+1,@ind8-@ind7-1)
                set @DYNAMICS    = SUBSTRING(@renglon,@ind8+1,@ind9-@ind8-1)
                set @FECHA       = SUBSTRING(@renglon,@ind9+1,len(@renglon)-@ind9)

                insert into #Poliza( ID, IDLOTE, IDLINEA, CONCEPTO, CUENTA, CARGO, ABONO, TIPO_POLIZA, DYNAMICS, FECHA)
                values             (@ID,@IDLOTE,@IDLINEA,@CONCEPTO,@CUENTA,@CARGO,@ABONO,@TIPO_POLIZA,@DYNAMICS, CONVERT(date, @FECHA, 103))

            end
        end 

        if  @fin = @tamano begin
            break
        end 

        set @ini = @fin
        set @fin = CHARINDEX(CHAR(13),@archivo,@fin+1)

        if @fin = 0 begin
            set @fin = @tamano
        end 

    end
	--    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GENERACION DE POLIZAS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

	CREATE TABLE #POLIZAF(CONCEPTO VARCHAR(255),CUENTA VARCHAR(355),MONTO_CARGO MONEY, MONTO_ABONO MONEY)

    exec CursorCloseDeallocate 'db_cursor_captacion'

    DECLARE db_cursor_captacion CURSOR FOR

        SELECT DISTINCT TIPO_POLIZA,DYNAMICS,FECHA
		from #Poliza

    OPEN db_cursor_captacion
        FETCH NEXT FROM db_cursor_captacion
        INTO @E_TIPO_POLIZA, @E_DYNAMICS, @E_FECHA
    WHILE @@FETCH_STATUS = 0 BEGIN

        set @ID_POLIZA = 0

        select @ID_POLIZA = ID
        from [PO].[CAT_TIPO_POLIZA]
        where DESCRIPCION = 'CAP '+ @E_TIPO_POLIZA
            AND TIPO_POLIZA = @E_DYNAMICS

		INSERT INTO #POLIZAF(CONCEPTO, CUENTA, MONTO_CARGO, MONTO_ABONO)  
		SELECT CONCEPTO,CUENTA,CARGO,ABONO
		FROM #Poliza
		WHERE TIPO_POLIZA = @E_TIPO_POLIZA
            AND DYNAMICS = @E_DYNAMICS
            AND FECHA = @E_FECHA

		exec [PO].[SP_SAF_POLIZA_FINALIZA] @E_FECHA, @ID_POLIZA
	
		TRUNCATE TABLE #POLIZAF

        FETCH NEXT FROM db_cursor_captacion
        INTO @E_TIPO_POLIZA, @E_DYNAMICS, @E_FECHA
    END 

    CLOSE db_cursor_captacion
    DEALLOCATE db_cursor_captacion

END
GO
