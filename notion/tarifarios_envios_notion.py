
##  ACTUALIZACION DE TARIFAS DEL SISTEMA DE ENVIOS EN NOTION

#   EN ZONAS TARIFARIAS AGREGAR COLUMNAS CON TARIFARIOS NUEVOS 
    #   Ej de nombre ML23A-ENERO, ML23B-MARZO, ML24A-FEBRERO, FA23A-ENERO, etc
    #   Tipo propiedad "Number", Number Format "Argentine peso"

#   En LOCALIDADES agregar tarifas nuevas:
    #   Agregar columna tipo "Rollup" Relation "AMBA" Calculate "Sum" apuntando Property al tarifario nuevo en ZONAS TARIFARIAS y con Property Name el mismo del tarifario
    #   Agregar columna tipo "Formula" apuntando a la propiedad Rollup que creamos anteriormente. El "Property Name" agrega "Formula" al nombre original. Ej: "Formula FA23A-ENERO". El Number Format de la Formula es "Argentine peso"

#   En ENVIOS FLEX
    #   En columna TARIFARIO agregar opciones para los tarifarios nuevos en GRIS CLARO. El día que entran en VIGENCIA los nuevos tarifarios, se les pone color gris a todos los demás, y COLOR a los nuevos.

    #   Agregar columna con rollup "Rollup" Relation LOCALIDAD apuntando Property la FORMULA del TARIFARIO NUEVO con opción Calculate "Sum"
    #       Si se copia la propiedad de la versión anterior del mismo tarifario, ya la crea con la RELACION. Sólo resta renombrar la propiedad, editar la PROPIEDAD relacionada para apuntarla a la fórmula correcta, y confirmar la opción CALCULATE > SUM.

    #   Editar la Fórmula de la columna IMPORTE agregando condiciones para los nuevos tarifarios.
    #       Ej, si se agrega el nuevo tarifario "MELI 2023 F-NOV" que toma el Rollup "ML23F", la fórmula pasaría de esto:
    #   ORIGINAL FORMATEADA
    #   if(prop("Tarifario") == "MELI 2023 B", prop("ML23B"), 
    #      if(prop("Tarifario") == "FABIAN 2023 A", prop("FA23A"), 
    #         if(prop("Tarifario") == "FABIAN 2023 B", prop("FA23B"), 
    #            if(prop("Tarifario") == "MELI 2023 C-JUNIO", prop("ML23C-JUNIO"), 
    #               if(prop("Tarifario") == "FABIAN 2023 C", prop("FA23C-JUNIO"), 
    #                  if(prop("Tarifario") == "MELI 2023 D-AGOSTO", prop("ML23D"), 
    #                     if(prop("Tarifario") == "FABIAN 2023 D-AGOSTO", prop("FA23D"), 
    #                        if(prop("Tarifario") == "MELI 2023 E-SEPTIEMBRE",prop("ML23E"), 
    #                           if(prop("Tarifario") == "FABIAN 2023 E-SEPTIEMBRE", prop("FA23E"), 
    #                              prop("ML23A")))))))))) + prop("Recargo")    
    #
    #   A esto:
    #   NUEVA
    #   if(prop("Tarifario") == "MELI 2023 B", prop("ML23B"), 
    #      if(prop("Tarifario") == "FABIAN 2023 A", prop("FA23A"), 
    #         if(prop("Tarifario") == "FABIAN 2023 B", prop("FA23B"), 
    #            if(prop("Tarifario") == "MELI 2023 C-JUNIO", prop("ML23C-JUNIO"), 
    #               if(prop("Tarifario") == "FABIAN 2023 C", prop("FA23C-JUNIO"), 
    #                  if(prop("Tarifario") == "MELI 2023 D-AGOSTO", prop("ML23D"), 
    #                     if(prop("Tarifario") == "FABIAN 2023 D-AGOSTO", prop("FA23D"), 
    #                        if(prop("Tarifario") == "MELI 2023 E-SEPTIEMBRE",prop("ML23E"), 
    #                           if(prop("Tarifario") == "FABIAN 2023 E-SEPTIEMBRE", prop("FA23E"), 
    #                              if(prop("Tarifario") == "MELI 2023 F-NOV", prop("ML23F"),
    #                              prop("ML23A")))))))))))) + prop("Recargo")
    #
    #   Lo importante a tener en cuenta que se agrega un nuevo "if(prop("Tarifario") == $OPCION_TARIFARIO, $ROLLUP_TARIFARIO" por cada tarifario nuevo
    #   Y por cada nuevo if(prop("Tarifario") que agregamos, tenemos que agregar un ")" luego del último $ROLLUP_TARIFARIO "("ML23A")". 
    #   Tiene que quedar con n+1 paréntesis, siendo n la cantidad de condiciones "if(prop("Tarifario") que tengamos en la fórmula.


### ACTUALIZACIÓN DE FÓRMULA DE ENVIOS FLEX

# CONFIG

# Copiar la fórmula original de la columna IMPORTE
FORMULA_ORIGINAL = 'if(prop("Tarifario") == "MELI 2023 B", prop("ML23B"), if(prop("Tarifario") == "FABIAN 2023 A", prop("FA23A"), if(prop("Tarifario") == "FABIAN 2023 B", prop("FA23B"), if(prop("Tarifario") == "MELI 2023 C-JUNIO", prop("ML23C-JUNIO"), if(prop("Tarifario") == "FABIAN 2023 C", prop("FA23C-JUNIO"), if(prop("Tarifario") == "MELI 2023 D-AGOSTO", prop("ML23D"), if(prop("Tarifario") == "FABIAN 2023 D-AGOSTO", prop("FA23D"), if(prop("Tarifario") == "MELI 2023 E-SEPTIEMBRE", prop("ML23E"),if(prop("Tarifario") == "FABIAN 2023 E-SEPTIEMBRE", prop("FA23E"), prop("ML23A")))))))))) + prop("Recargo")'

# Cargar una tupla con cada tarifario nuevo y su rollup
TARIFARIOS_NUEVOS = [("Columna TARIFARIO", "Columna ROLLUP"), ("OTRO_TARIFARIO", "OTRO_ROLLUP")]

def arma_nueva_condicion(nuevo_tarifario):
    """Formatea la primera parte de un if statement de Notion
    """
    new_if = f' if(prop("Tarifario") == "{nuevo_tarifario}"'
    return new_if

def arma_nuevo_rollup(nuevo_rollup):
    """Formatea la segunda parte de un if statement de Notion
    """
    new_rollup = f' prop("{nuevo_rollup}")'
    return new_rollup

def lista_condicion_accion(tupla_tarifario_nuevo):
    """Formatea una tupla de tarifario y rollup para crear un if statement de Notion
    """
    single_if = []
    for i in range(2):
        if i == 0:
            item = arma_nueva_condicion(tupla_tarifario_nuevo[0])
        else:
            item = arma_nuevo_rollup(tupla_tarifario_nuevo[i])
        single_if.append(item)
    return single_if

def inserta_if_nuevo(formula_split, condicion_nueva):
    """Inserta los nuevos if statements a la fórmula original
    """
    for i in condicion_nueva:
        formula_split.insert(-1, i)
    return formula_split

def lista_de_condiciones_acciones(tarifarios_nuevos):
    """Genera una lista de listas con las condiciones y acciones de cada tarifario nuevo.
    """
    lista_de_listas = []
    for tarifario in tarifarios_nuevos:
        lista_de_listas.append(lista_condicion_accion(tarifario))
    return lista_de_listas

def separa_ultimo_item(formula_split):
    """Separa el último item de la fórmula original, para poder insertar un nuevo paréntesis de cierre.
    """
    split_ultimo_item = formula_split[-1].split(" + ")
    #print(split_ultimo_item)
    return split_ultimo_item
    pass

def inserta_parentesis(formula_split):
    """Inserta un paréntesis de cierre al último item de la fórmula original.
    """
    #print(formula_split)
    split = separa_ultimo_item(formula_split)
    cierre_if = split[0]
    cierre_if = cierre_if + ")"
    split[0] = cierre_if
    nuevo_ultimo_item = split[0] + " + " + split[1]
    formula_split[-1] = nuevo_ultimo_item
    #print(formula_split)
    return formula_split

def formato_final_formula(formula_split):
    """Formatea la fórmula final para poder insertarla en Notion.
    """
    formula_final = ""
    for i in formula_split:
        formula_final = formula_final + "," + i
    return formula_final[1:]
    

def genera_formula_nueva(formula_original, tarifarios_nuevos):
    """Genera la nueva fórmula a insertar en Notion.
    """
    print(f'Fórmula original: {formula_original}')
    print()

    formula_split = formula_original.split(',')

    for tarifarios in tarifarios_nuevos:
        condicion_nueva = lista_condicion_accion(tarifarios_nuevos[0])
        formula_split = inserta_if_nuevo(formula_split, condicion_nueva)
        formula_split = inserta_parentesis(formula_split)

    formula_actualizada = formato_final_formula(formula_split)
    
    print(f'Fórmula nueva: {formula_actualizada}')
    print()
    return formula_actualizada


if __name__ == "__main__":

    genera_formula_nueva(FORMULA_ORIGINAL, TARIFARIOS_NUEVOS)
            