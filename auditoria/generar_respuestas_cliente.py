# -*- coding: utf-8 -*-
"""Genera 15_respuestas_cliente.html y 15_respuestas_cliente.csv: lectura de las
respuestas del cliente a las 31 confirmaciones, reencuadradas al alcance
productivo (CIERRE, SAF, PO y dbo.REPORTE_COBRANZA_INTEGRACION).
"""
import csv
from pathlib import Path

from plantilla import e, page

OUT = Path(__file__).resolve().parent

# id, area, pregunta, respuesta del cliente, estado, lectura, accion
CERRADA = 'Cerrada'
PARCIAL = 'Cerrada a medias'
REPREGUNTAR = 'Repreguntar'
FUERA = 'Fuera de alcance'
SIN = 'Sin respuesta'

PILL = {CERRADA: 'ok', PARCIAL: 'm', REPREGUNTAR: 'a', FUERA: 'info', SIN: 'c'}

R = [
    ('Q01', 'Contabilidad',
     'Columna correcta del segundo bloque de ajustes ballon: PRINCIPAL_FINAL o MONTOEXIGIBLECOM',
     '',
     SIN,
     'Es el hallazgo contable de mayor impacto que sigue abierto y está dentro del alcance '
     '(CIERRE.SP_IND_GEN_MES). Sin esta definición no se puede cerrar la revisión del cierre individual.',
     'Insistir. Es de las cinco que valen la reunión personal.'),
    ('Q02', 'Contabilidad',
     'Criterio único de crédito cancelado para el universo del cierre',
     'Únicamente para el cierre: FEC_CANCELACION nula o mayor a la fecha de corte.',
     CERRADA,
     'Queda una regla única y comprobable. El código usa criterios distintos según el procedimiento, '
     'así que la respuesta convierte esas variantes en defecto, no en decisión pendiente.',
     'Unificar el predicado en la familia de cierre y dejarlo como control de la prueba de equivalencia. '
     'No es parametrizable: es regla fija.'),
    ('Q03', 'Contabilidad',
     'Catálogo oficial de rubros del cierre: se materializa, en qué reporte participa, causa IVA',
     'La tabla es [Quiero_Confianza].[PR].[PR_RUBRO]; es la que controla los rubros desde SAF y lo ideal es '
     'que al agregar uno ahí exista la ventana de configuración para que la póliza lo tome.',
     PARCIAL,
     'La fuente queda identificada, pero la petición no se resuelve sólo con una ventana de configuración: '
     'hoy cada rubro está escrito además como columna de salida. El rubro es un catálogo espejo con '
     'banderas, no una bandera del tipo de cartera.',
     'Diseñar el espejo PR_RUBRO + banderas por rubro y, en paralelo, cambiar la forma del cierre para '
     'que las columnas por rubro dejen de estar escritas una por una (ver la sección de hallazgos).'),
    ('Q04', 'Contabilidad',
     'Definición oficial de cartera sin restricción por COD_ORIGEN y etiquetas de salida',
     'La tabla es Quiero_Confianza_shadow.PR.PR_ORIGEN_FONDOS; es la que controla el cedido desde SAF y '
     'debería tener ventana de configuración.',
     PARCIAL,
     'Confirma que el origen de fondos es catálogo externo y que la clasificación restringido / no '
     'restringido es una propiedad de ese catálogo: hoy vive como lista literal en el cierre comercial. '
     'La respuesta cita la base shadow, que es justamente el objeto del hallazgo de drift.',
     'Espejo de PR_ORIGEN_FONDOS con bandera ES_NO_RESTRINGIDO por origen, y resolver primero el sinónimo '
     'por ambiente (Fase 1) para no consolidar la referencia a shadow.'),
    ('Q05', 'Contabilidad',
     'Política de redondeo y tolerancia de cuadre cargo-abono',
     'Los cálculos se hacen con los decimales del campo y sólo el resultado final va a dos decimales.',
     CERRADA,
     'Regla clara y verificable. No define tolerancia de descuadre, pero con redondeo sólo al final la '
     'tolerancia esperada es cero y cualquier diferencia es defecto.',
     'Usarla como criterio de aceptación de la prueba de equivalencia: delta exacto de cero, sin banda de '
     'tolerancia. Confirmar en la reunión que cero es la expectativa.'),
    ('Q06', 'Contabilidad',
     "El cierre comercial lee 'otras comisiones' de la fecha fija '20260123'",
     'Ya no debe estar en código lo que se indica.',
     PARCIAL,
     'El cliente reconoce el defecto y afirma que fue corregido, pero la fecha sigue presente en el '
     'archivo que tenemos de producción. Es evidencia de que el repositorio auditado no refleja lo que '
     'corre hoy, que es exactamente el riesgo R1.',
     'No cerrarla por declaración: verificarla en la Fase 0 comparando el texto del objeto contra la '
     'instancia. Si allá ya no está, el hallazgo se cierra y el drift queda demostrado con un caso '
     'concreto.'),
    ('Q07', 'Contabilidad',
     'Reproceso de un periodo ya cerrado: permitido, quién autoriza, acumular o recalcular',
     'Nunca se reprocesa un periodo cerrado; si por intermitencia no se generó la póliza, se reprocesa en '
     'un ambiente controlado con un respaldo a la fecha requerida, se procesa como primera vez y el '
     'resultado se migra a producción.',
     CERRADA,
     'Queda claro y además explica por qué la idempotencia no era el problema real: el reproceso no ocurre '
     'en producción. Lo que sí falta es que ese ambiente controlado use la configuración vigente en la '
     'fecha reprocesada, no la de hoy; con parámetros en catálogo, un respaldo de datos con configuración '
     'actual daría una cifra distinta a la original.',
     'Incorporar al diseño el sello de configuración por corrida y la consulta "cómo estaba configurado el '
     'día X". Es la respuesta que más valor agrega al portal.'),
    ('Q08', 'Contabilidad',
     'Valores vigentes y su fecha de vigencia: IVA, base de días, umbral de avalúo, fechas COVID',
     'Las constantes que están en código son las correctas actualmente. Conviene revisar la factibilidad '
     'de que se tomen de un catálogo y sean dinámicas, cuidando que los cambios no afecten fechas '
     'anteriores; hoy la póliza no maneja histórico de estos valores.',
     CERRADA,
     'Da la línea base para sembrar el catálogo sin cambiar ninguna cifra, y confirma el requisito duro: '
     'un cambio no puede alterar lo ya publicado. Eso se resuelve resolviendo el parámetro por fecha de '
     'proceso y no por "vigente hoy".',
     'Sembrar cada constante con vigencia desde el origen del histórico y exigir que el cierre pida el '
     'valor con la fecha del periodo. Sí es factible ver el pasado: ver la sección Q08 ampliada.'),
    ('Q09', 'Negocio',
     'Porcentaje de participación del convenio vigente, desde cuándo, y si se conserva el bruto',
     'No hay valor fijo y puede cambiar; lo ideal es configurarlo a la llegada de un cedido, incluso con la '
     'opción "no establecido" porque a veces depende del sistema del cliente que lo fija cada mes. De '
     'referencia: Afirme 90/10, administrada 100/0, sindicada variable.',
     CERRADA,
     'La respuesta corta que anotaste es correcta y además agrega dos requisitos que no teníamos: la '
     'participación es por convenio y por periodo, y existe un estado "no establecido" que hoy no existe '
     'en el código, donde 0.10 / 0.90 está escrito en 28 archivos.',
     'Tabla de participación por convenio con vigencia mensual y estado pendiente de captura que bloquee '
     'el cierre de ese convenio en lugar de calcular con un valor equivocado. Conservar bruto y '
     'participado por separado.'),
    ('Q10', 'Negocio',
     'La cartera sindicada debe aplicar COVID y la separación balance / cuentas de orden de etapa 3',
     '',
     SIN,
     'Sigue dentro del alcance: es cierre comercial. Es una de las que más divergencia explica entre '
     'procedimientos hermanos.',
     'Insistir en la reunión, junto con Q01.'),
    ('Q11', 'Negocio',
     'Dos procesos distintos pueden compartir el mismo número de póliza',
     'No: es regla de programación, cada proceso debe tener una póliza específica.',
     CERRADA,
     'Confirma tu lectura y convierte el caso detectado en defecto de código, no en decisión de negocio.',
     'Entra a la limpieza general con una restricción de unicidad proceso - número de póliza, y como '
     'validación de salud en el portal.'),
    ('Q12', 'Negocio',
     'Cuáles divergencias entre los procedimientos hermanos comercial e individual son intencionales',
     'No hay diferencia ni descuido: así es la operativa y funcionamiento de cada cartera.',
     REPREGUNTAR,
     'La respuesta es defendible como principio pero no resuelve nada operativamente: la pregunta era por '
     'divergencias puntuales y la respuesta es general. Hay diferencias que no son de operativa sino de '
     'escritura, como un literal de rubro distinto entre hermanos o un filtro comentado en uno y activo '
     'en el otro; esas no pueden ser intencionales.',
     'Repreguntar caso por caso con la diferencia enfrente, no en abstracto. Redacción propuesta abajo.'),
    ('Q13', 'Negocio',
     'Catálogo oficial de tipos de crédito, en qué procesos participa cada uno, qué pasa con uno desconocido',
     'Si se refiere a NUM_DESC_TIPO_CREDITO, está en [Quiero_Confianza].[PR].[PR_DESC_TIPOS_CREDITO], y el '
     'nombre correcto es tipo de cartera.',
     CERRADA,
     'Dato de alto valor y con dos consecuencias directas: la fuente autoritativa es la tabla de SAF y no '
     'PO.SAF_CAT_DESC_TIPO, que es la copia local que sembró la demo; y el vocabulario del portal debe '
     'decir tipo de cartera. No responde qué hacer con un tipo desconocido, que es el hueco de los tipos '
     '23, 24, 25, 27, 28 y 29.',
     'Cambiar la fuente y el nombre en el diseño y en la demo. Mantener abierta la parte de tipo '
     'desconocido: es la que justifica la validación de salud.'),
    ('Q14', 'Negocio',
     'Dueño de cada catálogo y quién autoriza el alta de un rubro o concepto nuevo',
     'El dueño de los catálogos es el área de cartera y ellos autorizan.',
     CERRADA,
     'Un solo dueño simplifica el modelo de roles: no hacen falta aprobadores por familia. No define '
     'tiempo de respuesta, que es lo que sostiene el compromiso de servicio del proceso.',
     'Un rol aprobador único llamado Cartera (dueño de catálogos) en lugar de Aprobador de contabilidad, y '
     'preguntar sólo el tiempo de respuesta comprometido.'),
    ('Q15', 'Negocio',
     'El reporte a Afirme deja la comisión de administración en cero por un literal de rubro mal escrito',
     '',
     SIN,
     'Sigue en alcance y es dinero: si el literal no empata, la columna sale en cero. La auditoría ya '
     "encontró el mismo patrón con 'OPI VALOR' y 'OPI_VALOR' conviviendo en el mismo procesamiento.",
     'Insistir. Es la evidencia más fácil de entender del valor del catálogo.'),
    ('Q16', 'Negocio',
     'Salida autoritativa cuando dos artefactos publican la misma cifra',
     'Todos los reportes son independientes; lo que indican son características propias de cada reporte.',
     REPREGUNTAR,
     'No responde la pregunta. La duda no es si los reportes son independientes sino qué hacer cuando dos '
     'reportes que se presentan como la misma cifra no coinciden, porque hoy hay dos variantes del reporte '
     'de póliza contable con lógica distinta. Independientes y contradictorios no pueden ser ambos '
     'correctos si alguien los compara.',
     'Repreguntar con las dos cifras concretas enfrente. Redacción propuesta abajo.'),
    ('Q17', 'Negocio',
     'Tratamiento del tipo de crédito 8 en los estados de cuenta',
     'Para póliza por ahora no se trabajará estados de cuenta.',
     FUERA,
     'Correcto, y coincide con tu lectura: el esquema edc queda fuera del alcance productivo declarado.',
     'Baja prioridad. Se conserva documentada por si el alcance vuelve a abrirse.'),
    ('Q18', 'Riesgos',
     "El canal minorista o comercial puede seguir derivándose de TIP_TASA='F'",
     'Para póliza ahorita no se trabajarán regulatorios.',
     FUERA,
     'De acuerdo, con un matiz: el filtro por TIP_TASA sigue vivo dentro del cierre comercial, así que lo '
     'que sale del alcance es la validación regulatoria, no el hardcodeo. Ese sigue en la lista técnica.',
     'Baja prioridad como pregunta de negocio; el valor literal permanece en el inventario de hardcodeo.'),
    ('Q19', 'Riesgos',
     'Criterio correcto de asignación de etapa de riesgo y si hubo periodos mal clasificados',
     'La etapa la controla SAF; la única condición es que si se tiene 0 pase a 1.',
     REPREGUNTAR,
     'La primera parte sí es útil y cierra media pregunta: la etapa no se calcula, se recibe, y la única '
     'transformación permitida es 0 a 1. Lo que no responde es la segunda mitad, que era si hubo periodos '
     'mal clasificados por el filtro de periodo anulado, es decir si hay que corregir el pasado.',
     'Cerrar la parte de criterio y repreguntar sólo por el efecto retroactivo. Redacción propuesta abajo.'),
    ('Q20', 'Riesgos',
     'Granularidad del reporte de riesgos: folio o folio más sección',
     'Para póliza ahorita no se trabajará reporte de riesgo.',
     FUERA,
     'De acuerdo.',
     'Baja prioridad.'),
    ('Q21', 'Riesgos',
     'El universo COVID se define por NUM_CREDITO menor a 6051 o por un atributo del crédito',
     'Por ambos.',
     REPREGUNTAR,
     '"Por ambos" deja la regla sin definir, porque ambos criterios pueden no coincidir y el código aplica '
     'sólo el umbral, además con valor distinto entre ambientes (6051 en desarrollo y 6086 en producción). '
     'Hay que saber si el umbral es condición necesaria, suficiente o redundante.',
     'Repreguntar en forma de tabla de verdad, con las cuatro combinaciones. Redacción propuesta abajo.'),
    ('Q22', 'Operación',
     'Los esquemas PAG, edc, edcc, juicios, demandas, ori y cierre_puente existen en producción, y qué '
     'versión del cierre corre realmente',
     'Para póliza ahorita no se trabajará.',
     REPREGUNTAR,
     'Aquí sí hay un malentendido que conviene deshacer: la primera mitad puede quedar fuera, pero la '
     'segunda mitad es el corazón del alcance. La pregunta era qué versión del cierre corre en producción, '
     'y sin eso cualquier corrección puede aplicarse sobre código equivocado.',
     'Repreguntar sólo la segunda mitad, y reencuadrarla como acceso de lectura a metadatos en QA (CUA), '
     'no como decisión de negocio. Redacción propuesta abajo.'),
    ('Q23', 'Operación',
     'Quién recibe la alerta cuando el cierre termina con errores, en qué tiempo, y qué se hace mientras',
     'Para póliza ahorita no se trabajará cierre.',
     REPREGUNTAR,
     'Confirmo tu lectura: la respuesta contradice el alcance, que es precisamente el cierre. La pregunta '
     'no era sobre construir un monitor sino sobre qué pasa hoy cuando el cierre falla: 102 objetos '
     'escriben la bitácora de errores de póliza y ninguno la vigila.',
     'Repreguntar en términos de operación actual, no de proyecto nuevo. Redacción propuesta abajo.'),
    ('Q24', 'Operación',
     'Calendario oficial de días hábiles y fecha de negocio que debe usar el proceso',
     '',
     SIN,
     'Sigue en alcance: el cierre es diario y dispara minutos después de SAF, así que la definición de día '
     'hábil y de fecha de negocio determina qué se procesa.',
     'Insistir. Es requisito de la parametrización de calendario.'),
    ('Q25', 'Operación',
     'Si alguna vez se ejecutó en producción el generador de órdenes con importes aleatorios',
     'Para póliza ahorita no se trabajará facturación.',
     FUERA,
     'De acuerdo en cuanto a alcance, pero el objeto existe en el repositorio y escribe en tablas de '
     'facturación reales. Fuera de alcance no es lo mismo que inofensivo.',
     'Baja prioridad como pregunta; se mantiene la recomendación técnica de aislarlo o retirarlo.'),
    ('Q26', 'Operación',
     'Revisión retroactiva de los pagos emparejados por coincidencia parcial de referencia',
     'Para póliza ahorita no se trabajará aplicación de pagos.',
     FUERA,
     'De acuerdo.',
     'Baja prioridad.'),
    ('Q27', 'Seguridad y legal',
     'Alcance del enmascaramiento de datos personales y bancarios, y quién puede verlos sin máscara',
     'Para póliza ahorita no se trabajará esto.',
     REPREGUNTAR,
     'La pregunta original era demasiado amplia y por eso recibió una respuesta genérica. Reducida al '
     'alcance sigue teniendo peso: el cierre comercial y el reporte de cobranza sí exponen nombre, '
     'domicilio y datos de crédito, y el portal va a mostrar información derivada.',
     'Reformular en dos preguntas concretas y cerradas sobre los reportes del alcance y sobre el portal. '
     'Redacción propuesta abajo.'),
    ('Q28', 'Seguridad y legal',
     'Cuatro procedimientos de producción leyeron datos de la base de QA: ¿hay que revisar las pólizas '
     'generadas',
     '',
     SIN,
     'Sigue en alcance (objetos de PO y CIERRE) y es la única pregunta con posible impacto en cifras ya '
     'publicadas.',
     'Insistir. Va junto con Q06 en la verificación de Fase 0.'),
    ('Q29', 'Seguridad y legal',
     'El correo de prueba en el campo de contacto de los clientes',
     '',
     SIN,
     'Queda fuera del alcance por ser del esquema edc, igual que Q17.',
     'Baja prioridad.'),
    ('Q30', 'Gobierno del portal',
     'Se permiten cambios de parámetro con vigencia retroactiva y quién los autoriza',
     'Esto no debe ocurrir.',
     CERRADA,
     'Tu lectura es correcta: la vigencia siempre es a futuro. Es un requisito que hay que imponer en la '
     'base de datos y no sólo en la pantalla, y encaja con Q08: nunca se altera lo publicado.',
     'Restricción de fecha de inicio mayor a hoy en la tabla de vigencias y en la validación del portal. '
     'La demo hoy no lo impide.'),
    ('Q31', 'Gobierno del portal',
     'Propietario de cada uno de los 63 grupos de valores hardcodeados',
     'El propietario es el área de cartera; lo que se espera del análisis es identificar los grupos con '
     'los cuales las configuraciones se simplifican.',
     CERRADA,
     'Coincide con Q14 y además fija la expectativa del entregable: agrupar, no enumerar. Los 63 grupos ya '
     'están consolidados en 12 banderas y tres catálogos, más los espejos de rubro y origen que salen de '
     'Q03 y Q04.',
     'Un solo dueño y entrega orientada a grupos. Sin cambios de diseño.'),
]

REPREGUNTAS = [
    ('Q12', 'Divergencias entre procedimientos hermanos',
     'Preguntar en abstracto por "las divergencias" invita a una respuesta de principio. Hay que poner la '
     'diferencia enfrente y pedir sólo una de tres respuestas.',
     'Te muestro cinco diferencias concretas entre el procedimiento comercial y el individual. Para cada '
     'una necesito una de estas tres respuestas: (a) es intencional porque la operativa de esa cartera lo '
     'requiere, (b) es un error y debe igualarse al otro, o (c) no lo sé y hay que revisarlo con quien '
     'operaba esa cartera. Las cinco son: el IVA fijo en individual y calculado en comercial; el filtro de '
     'moratorios comentado en uno y activo en el otro; el literal de rubro escrito de dos formas; el '
     'criterio de fecha de cancelación; y la columna destino del ajuste ballon.'),
    ('Q16', 'Cifra autoritativa entre reportes',
     'La respuesta de que son independientes no resuelve el conflicto. Hay que preguntar por el caso en '
     'que dos números que se presentan como el mismo no coinciden.',
     'No pregunto si los reportes son independientes, sino qué hacer cuando dos de ellos publican la misma '
     'cifra con distinto resultado. Caso concreto: existen dos variantes del reporte de póliza contable, '
     'con lógica distinta, y ambas se pueden ejecutar sobre el mismo periodo. Si la contabilidad de un mes '
     'se cuestionara, ¿cuál de las dos es la que se presenta como oficial, y la otra puede retirarse o '
     'renombrarse como reporte de trabajo?'),
    ('Q19', 'Etapa de riesgo, efecto retroactivo',
     'La primera mitad ya quedó respondida. Falta sólo el efecto sobre el pasado, y conviene preguntarlo '
     'sin mezclarlo con el criterio.',
     'Tomo como cerrado que la etapa la controla SAF y que la única transformación permitida es 0 a 1. Lo '
     'que falta: el procedimiento excluye los periodos marcados como anulados al buscar la '
     'reclasificación, y por esa exclusión hay créditos que pudieron quedar en una etapa distinta a la de '
     'SAF en periodos ya cerrados. ¿Se requiere identificar esos casos y reexpresarlos, o el tratamiento '
     'es corregir de aquí en adelante y dejar el pasado como está?'),
    ('Q21', 'Universo del programa COVID',
     '"Por ambos" no permite escribir la regla. Conviene pedirlo como tabla de verdad, que además deja '
     'documentado el caso raro.',
     'Necesito saber cómo combinar los dos criterios, porque pueden no coincidir. Para cada combinación, '
     '¿el crédito entra al tratamiento COVID? (1) número menor al umbral y con el atributo COVID; (2) '
     'número menor al umbral pero sin el atributo; (3) número mayor o igual al umbral pero con el '
     'atributo; (4) ninguno de los dos. Y una segunda: ¿el umbral correcto es 6051 o 6086? La función '
     'dbo.FN_ES_COVID usa 6051 en desarrollo y 6086 en producción.'),
    ('Q22', 'Qué versión del cierre corre en producción',
     'La primera mitad puede archivarse; la segunda es el corazón del alcance y hay que separarla y '
     'presentarla como un acceso de lectura, no como una decisión.',
     'Retiro la parte de los esquemas que no están en alcance. Lo que sí necesito es confirmar qué versión '
     'del cierre está corriendo: el procedimiento de saldos que tenemos del repositorio tiene 573 líneas '
     'en desarrollo y 223 en producción, y falta la fecha fija de comisiones que ya nos dijeron que fue '
     'corregida. Con acceso de consulta al ambiente de QA (CUA) lo resolvemos nosotros en una hora, sin '
     'tocar nada: es una consulta de sólo lectura sobre el texto de los objetos.'),
    ('Q23', 'Qué pasa hoy cuando el cierre falla',
     'La respuesta indica que se entendió como un proyecto nuevo de alertas. Hay que preguntar por la '
     'operación actual.',
     'No pregunto por construir un monitor, sino por lo que pasa hoy. El cierre diario dispara minutos '
     'después de SAF y hay una tabla donde 102 objetos escriben los errores de póliza. Si mañana el cierre '
     'termina a medias, ¿quién se enteraría y cómo: alguien revisa esa tabla, hay un correo, o se detecta '
     'cuando contabilidad reclama el descuadre? ¿Y hasta qué hora del día siguiente sigue siendo '
     'recuperable?'),
    ('Q27', 'Datos personales, reducido al alcance',
     'La pregunta original abarcaba todo el sistema. Reducida a los objetos del alcance y al portal, se '
     'vuelve concreta y de respuesta corta.',
     'Reduzco la pregunta a dos: (1) el cierre comercial y el reporte de cobranza incluyen nombre, '
     'domicilio y datos del crédito en su salida, y esos archivos se comparten por correo; ¿esa salida '
     'requiere enmascaramiento o el control es sobre quién recibe el archivo? (2) el portal de '
     'configuración no mostrará datos de clientes, sólo catálogos y reglas; ¿confirman que con eso queda '
     'fuera del alcance de datos personales, o su norma exige igual clasificar la aplicación?'),
]

CAMBIOS_DEMO = [
    ('D1', 'Alto', 'Bajo',
     'Renombrar tipo de crédito a tipo de cartera y cambiar la fuente del catálogo',
     'Q13 confirma que el nombre correcto es tipo de cartera y que la fuente autoritativa es '
     '[Quiero_Confianza].[PR].[PR_DESC_TIPOS_CREDITO], no la copia local PO.SAF_CAT_DESC_TIPO con la que '
     'sembramos la demo. Es un cambio de vocabulario y de etiqueta de origen, no de estructura: el '
     'catálogo se muestra igual, pero deja claro que es un espejo de SAF y no una tabla nuestra.'),
    ('D2', 'Alto', 'Medio',
     'Nueva pestaña de rubros, con banderas por rubro y detección de rubro nuevo',
     'Es la petición explícita de Q03: cuando cartera agrega un rubro en SAF, que exista la ventana para '
     'decirle a la póliza qué hacer con él. Se administra como espejo de PR_RUBRO con banderas: se '
     'materializa, causa IVA, a qué póliza va y en qué reportes participa. El elemento que da más valor es '
     'la bandeja de rubro detectado en el origen y sin configurar, que hoy es la situación que obliga a '
     'llamar al desarrollador.'),
    ('D3', 'Alto', 'Bajo',
     'Nueva pestaña de origen de fondos y cedido, con la bandera de cartera no restringida',
     'Q04 confirma que el origen de fondos es catálogo externo y que restringido o no restringido es una '
     "propiedad suya. Hoy es una lista literal COD_ORIGEN IN ('008','031') dentro del cierre comercial. La "
     'pestaña muestra los orígenes con su bandera y el mismo patrón de detección de origen nuevo.'),
    ('D4', 'Alto', 'Medio',
     'Participación por convenio con vigencia y estado no establecido',
     'Q09 agrega un requisito que la demo no contempla: la participación cambia en el tiempo, es por '
     'convenio (Afirme 90/10, administrada 100/0, sindicada variable) y a veces todavía no se conoce. El '
     'estado no establecido debe bloquear el cierre de ese convenio en lugar de dejar que calcule con el '
     'valor del mes anterior; es lo contrario de lo que hace hoy el código con 0.10 / 0.90 escrito en 28 '
     'archivos.'),
    ('D5', 'Alto', 'Bajo',
     'Prohibir la vigencia retroactiva en la solicitud',
     'Q30 es un no rotundo. La demo hoy acepta cualquier fecha de inicio; debe rechazar fechas anteriores '
     'a mañana y explicar por qué, porque es la regla que garantiza que nunca se altere una póliza ya '
     'publicada.'),
    ('D6', 'Medio', 'Bajo',
     'Un solo rol aprobador, llamado Cartera',
     'Q14 y Q31 dicen que el dueño de todos los catálogos es el área de cartera. El rol Aprobador de '
     'contabilidad de la demo debe llamarse Cartera (dueño de catálogos) y ser el único aprobador; queda '
     'pendiente sólo el tiempo de respuesta comprometido.'),
    ('D7', 'Alto', 'Medio',
     'Sello de configuración por corrida y consulta cómo estaba configurado el día X',
     'Sale de cruzar Q07 con Q08: el reproceso se hace en un ambiente controlado con un respaldo a la '
     'fecha, así que si los parámetros pasan a un catálogo, ese reproceso tiene que resolverlos con la '
     'configuración de esa fecha o dará una cifra distinta de la original. Una pestaña de versiones que '
     'muestre la configuración vigente en cualquier fecha, y el identificador de versión sellado en cada '
     'póliza, es lo que convierte al portal en la respuesta a "por qué esta cifra salió así".'),
    ('D8', 'Medio', 'Bajo',
     'Constantes con vigencia desde el origen del histórico',
     'Q08 confirma que los valores actuales son correctos. Sembrarlos con vigencia desde el inicio del '
     'histórico, y no desde hoy, es lo que permite reprocesar el pasado sin cambiar ninguna cifra. En la '
     'demo se ve como una fila de vigencia abierta con la nota de que reproduce el valor que ya estaba en '
     'el código.'),
    ('D9', 'Bajo', 'Bajo',
     'Validaciones de salud alineadas a las respuestas',
     'Tres controles nuevos que ahora tienen respaldo del cliente: número de póliza repetido entre '
     'procesos (Q11), etapa de riesgo en cero que no fue promovida a uno (Q19) y rubro o tipo de cartera '
     'presente en el origen pero sin configuración (Q03, Q13). Se suman al panel que ya existe.'),
]

NO_AHORA = [
    ('Estados de cuenta, facturación, pagos y reportes de riesgo (Q17, Q20, Q25, Q26)',
     'El cliente los declaró fuera del alcance y no aportan a la póliza. No se agregan a la demo ni se '
     'diseñan catálogos para ellos; quedan documentados.'),
    ('Módulo de datos personales en el portal (Q27)',
     'Hasta tener la respuesta reformulada, el portal no muestra datos de clientes. Es la decisión más '
     'segura y no cuesta nada mantenerla.'),
    ('Reproceso ejecutable desde el portal (Q07)',
     'El cliente describió un procedimiento con ambiente controlado y respaldo. El portal debe mostrar la '
     'configuración de esa fecha, no disparar el reproceso: dar ese botón sería asumir un riesgo que hoy '
     'no existe.'),
    ('Parametrizar el factor 9 y la partición 0.10 / 0.90 en el mismo lugar',
     'Q09 aclara la participación por convenio, pero no explica la relación con el factor 9 del reporte de '
     'cobranza. Son bases de cálculo distintas y se administran por separado hasta entenderlas.'),
]

est = {k: sum(1 for r in R if r[4] == k) for k in (CERRADA, PARCIAL, REPREGUNTAR, FUERA, SIN)}

filas = '\n'.join(
    f'<tr><td class="num">{r[0]}</td><td>{e(r[2])}<div class="src">{e(r[1])}</div></td>'
    f'<td><span class="pill {PILL[r[4]]}">{e(r[4])}</span></td>'
    f'<td>{e(r[3]) if r[3] else "<i>sin respuesta del cliente</i>"}</td>'
    f'<td>{e(r[5])}</td><td>{e(r[6])}</td></tr>'
    for r in R)

repreg = '\n'.join(
    f'<div class="card azul"><h3>{r[0]} &mdash; {e(r[1])}</h3><p>{e(r[2])}</p>'
    f'<p class="q">Redacción propuesta</p><blockquote>{e(r[3])}</blockquote></div>'
    for r in REPREGUNTAS)

cambios = '\n'.join(
    f'<tr><td class="num">{c[0]}</td><td>{e(c[3])}</td>'
    f'<td><span class="pill {"a" if c[1] == "Alto" else "m" if c[1] == "Medio" else "info"}">{c[1]}</span></td>'
    f'<td class="num">{c[2]}</td><td>{e(c[4])}</td></tr>'
    for c in CAMBIOS_DEMO)

noahora = '\n'.join(f'<li><b>{e(t)}.</b> {e(d)}</li>' for t, d in NO_AHORA)

body = f"""
<p class="lead">Lectura de las respuestas del cliente a las 31 confirmaciones, reencuadradas al alcance
productivo declarado: <b>CIERRE</b>, <b>SAF</b>, <b>PO</b> y <b>dbo.REPORTE_COBRANZA_INTEGRACION</b>. Las
preguntas se escribieron antes de ese recorte, así que varias respuestas de tipo "por ahora no se trabajará"
son consistentes con el alcance y no evasivas; las que sí conviene repreguntar son otras, y se distinguen
aquí.</p>

<div class="kpis">
  <div class="kpi ok"><b>{est[CERRADA]}</b><span>Cerradas</span></div>
  <div class="kpi m"><b>{est[PARCIAL]}</b><span>Cerradas a medias</span></div>
  <div class="kpi a"><b>{est[REPREGUNTAR]}</b><span>Para repreguntar</span></div>
  <div class="kpi b"><b>{est[FUERA]}</b><span>Fuera de alcance</span></div>
  <div class="kpi c"><b>{est[SIN]}</b><span>Sin respuesta</span></div>
</div>

<h2>1. Lo que se desbloquea hoy</h2>
<p>Con las respuestas cerradas ya se puede avanzar en cuatro frentes que estaban detenidos:</p>
<ul>
<li><b>El criterio de universo del cierre y el redondeo</b> (Q02, Q05) dejan de ser preguntas y pasan a ser
criterios de aceptación de la prueba de equivalencia: predicado único de cancelación y delta exacto de cero,
sin banda de tolerancia.</li>
<li><b>La fuente autoritativa de los tres catálogos grandes</b> queda identificada: tipo de cartera en
<code>PR.PR_DESC_TIPOS_CREDITO</code>, rubros en <code>PR.PR_RUBRO</code> y cedido en
<code>PR.PR_ORIGEN_FONDOS</code> (Q03, Q04, Q13). Los tres viven en el origen, no en KARDIA, y eso cambia el
diseño: son espejos con banderas locales, no catálogos nuestros.</li>
<li><b>El gobierno del portal</b> queda definido con un solo dueño, el área de cartera, y con prohibición
absoluta de vigencia retroactiva (Q14, Q30, Q31).</li>
<li><b>El reproceso</b> deja de ser una incógnita: no ocurre en producción, se hace en un ambiente controlado
con respaldo a la fecha (Q07). Eso reencuadra por completo el hallazgo de idempotencia y agrega un requisito
nuevo al portal.</li>
</ul>

<h2>2. Respuesta por respuesta</h2>
<table>
<thead><tr><th style="width:44px">Id</th><th style="width:20%">Pregunta</th><th style="width:92px">Estado</th>
<th style="width:22%">Respuesta del cliente</th><th style="width:26%">Lectura</th><th>Acción</th></tr></thead>
<tbody>
{filas}
</tbody></table>

<h2>3. Tres hallazgos nuevos que salen de las respuestas</h2>

<div class="card rojo"><h3>H-A &mdash; Configurar el rubro no basta: hoy cada rubro es también una columna
escrita a mano</h3>
<p>Q03 pide que al agregar un rubro en SAF exista la ventana para que la póliza lo tome. El catálogo con
banderas resuelve la mitad del problema: la otra mitad es que la salida del cierre tiene una columna y un
<code>LEFT JOIN</code> por cada combinación de rubro y tipo de operación. Medido sobre el código del
repositorio, descontando comentarios:</p>
<table><thead><tr><th>Objeto</th><th>Ambiente</th><th class="num">Líneas</th>
<th class="num">Predicados por rubro</th><th class="num">Rubros distintos</th></tr></thead><tbody>
<tr><td><code>CIERRE.SP_CMR_GEN_MES</code></td><td>BD_prod</td><td class="num">879</td><td class="num">68</td>
<td class="num">19</td></tr>
<tr><td><code>CIERRE.SP_IND_GEN_MES</code></td><td>BD (ausente del export de producción)</td>
<td class="num">1.302</td><td class="num">171</td><td class="num">7</td></tr>
<tr><td><code>CIERRE.SP_SAF_SALDOS</code></td><td>BD_prod</td><td class="num">223</td><td class="num">12</td>
<td class="num">7</td></tr>
<tr><td><code>dbo.REPORTE_COBRANZA_INTEGRACION</code></td><td>BD_prod</td><td class="num">203</td>
<td class="num">39</td><td class="num">42</td></tr>
</tbody></table>
<p>En el cierre comercial hay siete bloques de operación (dación, adjudicación, condonación, descuento, pago,
pago COVID y saldos) y cada uno repite el mismo juego de seis rubros, uno por línea. Dar de alta un rubro
nuevo no es agregar una fila al catálogo: es agregar siete uniones y siete columnas, y por eso hoy requiere
desarrollador. <b>Si el portal permite registrar el rubro pero el procedimiento sigue con columnas fijas, el
rubro nuevo se configura y de todas formas no aparece en la póliza.</b> La remediación tiene dos partes: el
espejo con banderas y el cambio de forma de la salida a un pivote resuelto por catálogo.</p>
<p class="q">Evidencia adicional del mismo problema</p>
<p>En el reporte de cobranza conviven <code>'OPI VALOR'</code> con espacio y <code>'OPI_VALOR'</code> con
guion bajo como si fueran rubros distintos, y el cierre comercial usa la variante con espacio. Es el mismo
defecto que Q15 describe para el reporte a Afirme: un literal que no empata y una columna que sale en cero,
sin ningún error visible.</p></div>

<div class="card ambar"><h3>H-B &mdash; La respuesta de Q04 apunta a la base shadow, que es el objeto del
hallazgo de drift</h3>
<p>El cliente indica <code>Quiero_Confianza_shadow.PR.PR_ORIGEN_FONDOS</code> como fuente del cedido, y así
está escrito en <code>dbo.FN_ORIGEN_FONDOS</code>, mientras que el cierre comercial lee la misma tabla desde
<code>Quiero_Confianza</code>. Dos objetos del alcance leen el mismo catálogo de dos bases distintas.</p>
<pre>-- dbo.FN_ORIGEN_FONDOS (BD y BD_prod, identico)
SELECT @VALOR = DES_ORIGEN
FROM [Quiero_Confianza_shadow].PR.PR_ORIGEN_FONDOS
WHERE COD_ORIGEN = @COD_ORIGEN AND COD_EMPRESA = @COD_EMPRESA

-- CIERRE.SP_CMR_GEN_MES (BD_prod, linea 761)
LEFT JOIN Quiero_Confianza.PR.PR_ORIGEN_FONDOS F WITH (NOLOCK)
       ON C.COD_EMPRESA = F.COD_EMPRESA AND C.COD_ORIGEN = F.COD_ORIGEN</pre>
<p>No es un detalle de estilo: si las dos bases no están sincronizadas, la descripción del cedido y la
clasificación de cartera restringida pueden diferir entre la función y el cierre. Confirma que el sinónimo por
ambiente de la Fase 1 es prerrequisito de la parametrización del cedido, no una limpieza opcional.</p></div>

<div class="card azul"><h3>H-C &mdash; El punto exacto donde entra la matriz de banderas ya existe en el
código</h3>
<p>Q13 confirma la fuente del tipo de cartera y, al revisarla, aparece que el cierre comercial ya consulta esa
tabla: le aplica una lista literal encima y guarda el resultado en una tabla temporal. Es el mejor punto de
inserción posible, porque cambiar sólo cómo se llena <code>#TIPO_CREDITOS</code> no toca ningún filtro
posterior.</p>
<pre>-- CIERRE.SP_CMR_GEN_MES (BD_prod, linea 48)
SELECT NUM_DESC_TIPO_CREDITO
INTO #TIPO_CREDITOS
FROM Quiero_Confianza.PR.PR_DESC_TIPOS_CREDITO
WHERE COD_EMPRESA = '001' AND NUM_DESC_TIPO_CREDITO IN (
         12,13,14,15,28 -- minoristas
        ,2,18,27        -- puente
        --,7             -- sindicada</pre>
<p>Los comentarios del propio código nombran las banderas que propusimos (minorista, puente, sindicada) y una
de ellas está desactivada con dos guiones, que es la forma en que hoy se administra una regla contable. Eso
es, en una sola pantalla, el argumento de por qué hace falta el catálogo.</p></div>

<h2>4. Sobre tu pregunta de Q08: sí, con la nueva estructura se podrá ver el pasado</h2>
<p>Confirmado, con una condición de diseño que hay que respetar desde el inicio. Hoy la póliza no guarda con
qué valores se calculó, así que la única forma de saber qué IVA o qué fechas COVID aplicaban en un periodo es
leer la versión del código de ese momento, que además no está identificada (riesgo R1). Con el catálogo, ver
el pasado es posible si se cumplen tres cosas:</p>
<ul>
<li><b>Vigencia por fecha, no valor actual.</b> El cierre no pregunta "cuál es el IVA", pregunta "cuál era el
IVA en la fecha del periodo que estoy procesando". Es una diferencia de una línea en la consulta y es lo que
hace que un cambio no altere lo publicado, que es la preocupación explícita del cliente en Q08 y la
prohibición de Q30.</li>
<li><b>Semilla desde el origen del histórico.</b> Las constantes actuales se cargan con vigencia desde antes
del primer cierre almacenado, no desde la fecha de implantación; si se cargaran desde hoy, el pasado quedaría
sin valor y el reproceso fallaría o tomaría el actual.</li>
<li><b>Sello de versión en la póliza.</b> Cada corrida guarda el identificador de la versión de configuración
que usó. Con eso, el reproceso en el ambiente controlado que describe Q07 puede pedir explícitamente esa
versión y reproducir la cifra original, en lugar de recalcular con la configuración de hoy sobre datos de
ayer, que es lo que ocurriría si no se sella.</li>
</ul>
<p>Con las tres, el portal responde dos preguntas que hoy nadie puede responder sin leer código: cómo estaba
configurado el sistema el día del cierre, y qué cambió entre dos periodos que dieron cifras distintas.</p>

<h2>5. Repreguntas propuestas</h2>
<p>Siete de las respuestas no cierran la duda. Para cada una, por qué no cierra y una redacción de reemplazo
pensada para que la respuesta sea corta y verificable. La diferencia principal con la primera versión es que
estas preguntas llevan la evidencia adentro y ofrecen las opciones, en lugar de pedir una definición
abierta.</p>
{repreg}

<h2>6. Las seis que quedaron sin respuesta</h2>
<p>De las 31, seis no fueron contestadas: Q01, Q10, Q15, Q24, Q28 y Q29. Cinco siguen dentro del alcance y
conviene llevarlas a la reunión personal, porque son las de mayor consecuencia:</p>
<ul>
<li><b>Q01</b>, columna destino del ajuste ballon en el cierre individual: afecta una cifra publicada y no
tiene forma de resolverse por análisis estático.</li>
<li><b>Q10</b>, tratamiento COVID y separación balance / cuentas de orden en cartera sindicada: explica varias
divergencias entre procedimientos hermanos y se relaciona con Q12.</li>
<li><b>Q15</b>, comisión de administración en cero en el reporte a Afirme por un literal mal escrito: es el
mismo patrón que documenta H-A y el ejemplo más claro del valor del catálogo.</li>
<li><b>Q24</b>, calendario de días hábiles y fecha de negocio: el cierre es diario y dispara minutos después
de SAF, así que la definición determina qué se procesa y qué se omite en puentes y fines de mes.</li>
<li><b>Q28</b>, lectura de la base de QA desde objetos productivos: es la única pregunta con posible impacto
sobre pólizas ya publicadas. Va junto con la verificación de Q06 en la Fase 0.</li>
</ul>
<p>La sexta, <b>Q29</b> (correo de prueba en el contacto de los clientes), es del esquema de estados de cuenta
y queda fuera del alcance igual que Q17.</p>

<h2>7. ¿Hay que actualizar la demo de administración?</h2>
<p class="lead">Sí, y vale la pena hacerlo antes de presentarla otra vez: cuatro de las respuestas cambian el
vocabulario o agregan objetos que hoy no existen en la pantalla. Nueve cambios, ninguno estructural; los
cinco marcados como alto valor son los que el cliente reconocería de inmediato como respuesta a lo que
pidió.</p>
<table><thead><tr><th style="width:44px">Id</th><th style="width:26%">Cambio</th><th style="width:80px">Valor</th>
<th style="width:70px">Esfuerzo</th><th>Por qué, según las respuestas</th></tr></thead><tbody>
{cambios}
</tbody></table>
<p>Lo que <b>no</b> haría ahora, para que la demo no crezca por crecer:</p>
<ul>
{noahora}
</ul>
<p>Mi recomendación de secuencia: D1, D3, D5 y D6 son de una sola sesión de trabajo y ya cambian la
conversación, porque hablan el vocabulario del cliente. D2 y D7 son los que aportan valor nuevo y merecen su
propia sesión cada uno. D4, D8 y D9 pueden ir con cualquiera de los dos grupos. La demo actual sigue siendo
válida mientras se decide: ningún cambio la invalida, todos la extienden.</p>

<h2>8. Efecto en el plan y en los reportes</h2>
<ul>
<li><b>El plan de remediación no cambia de orden.</b> La Fase 0 sigue primero, y las respuestas la refuerzan:
Q06 y Q22 sólo se pueden cerrar comparando contra la instancia, y Q28 depende de lo mismo.</li>
<li><b>El diseño del dummy se amplía, no se corrige.</b> Las 12 banderas y los tres catálogos siguen válidos;
se agregan dos espejos (rubro y origen de fondos) y la tabla de participación por convenio.</li>
<li><b>Baja la prioridad de siete confirmaciones</b> (Q17, Q18, Q20, Q22 en su primera mitad, Q25, Q26, Q29) y
se mantiene la documentación por si el alcance se reabre.</li>
<li><b>Sube la prioridad de una que no estaba en la lista corta:</b> el tiempo de respuesta comprometido del
área de cartera para autorizar un alta. Sin ese número, el portal cambia quién hace el trabajo pero no cuánto
tarda el negocio en tener el rubro nuevo disponible, que es el beneficio que se está prometiendo.</li>
</ul>

<h2>9. Límites de esta lectura</h2>
<ul>
<li>Las respuestas del cliente son declaraciones; tres de ellas (Q06, Q08, Q22) contradicen o no coinciden con
el código que tenemos, y sólo se pueden verificar con lectura de metadatos de la instancia.</li>
<li>Las cifras de este informe salen del análisis estático del repositorio, con los comentarios descontados.
No se ejecutó nada contra SQL Server.</li>
<li>Los cambios de la sección 7 están descritos, no implementados: la demo publicada sigue siendo la
anterior.</li>
</ul>
"""

(OUT / '15_respuestas_cliente.html').write_text(page(
    'Respuestas del cliente: lectura, repreguntas y efecto en la solución',
    'Las 31 confirmaciones reencuadradas al alcance productivo &middot; CIERRE, SAF, PO y '
    'dbo.REPORTE_COBRANZA_INTEGRACION',
    body), encoding='utf-8')

with (OUT / '15_respuestas_cliente.csv').open('w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, delimiter=';')
    w.writerow(['Id', 'Area', 'Pregunta', 'Estado', 'Respuesta del cliente', 'Lectura', 'Accion',
                'Responsable', 'Fecha compromiso'])
    for r in R:
        w.writerow([r[0], r[1], r[2], r[4], r[3], r[5], r[6], '', ''])

print('ok 15_respuestas_cliente.html', est)
