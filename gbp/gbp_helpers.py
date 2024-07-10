
from copy import deepcopy
from dataclasses import dataclass, field

import logging
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Time, Boolean, UniqueConstraint, \
    Engine, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from openpyxl import load_workbook, Workbook
from typing import List, Union, Dict, Type

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

path2root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(path2root)

data_dir = os.path.join(path2root, "data")
sys.path.append(data_dir)

from data.data_helpers import create_tables, db_connection
from data.data_helpers import Base, Database, GbpSeveralTables_DbItem, GbpSkuMlItem
#from flask import session
from utils.utils_helpers import create_class_instance


#logging.basicConfig(level=logging.DEBUG)



def get_field_name(field_id, spreadsheet_schema):
    for k, v in spreadsheet_schema.__dict__.items():
        if v[0] == field_id:
            return k

def get_schema_idxs(spreadsheet_schema):
    schema_col_idxs = [col[0] for col in spreadsheet_schema.__dict__.values() if isinstance(col, tuple)]
    return schema_col_idxs
    

# Clases que representan información de GBP

class GbpDataSource:
    """ Fuente de datos de GBP
    """

    def get_data(self, filename, path_to_data_dir = None, *fields):
        pass


class ExcelSchema:

    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        #attribute_names = list(cls.__dict__.keys())
        attribute_names = [attr for attr in cls.__dict__.keys() if not attr.startswith('_') and not attr.endswith('__')]
        return attribute_names
    pass

    def create_excel(self, content_rows, filename=None):
        pass

    def get_attributes(self) -> Dict:
        """ Retorna un dict con {atributo: valor}
        """
        attributes = {attribute: value for attribute, value in self.__class__.__dict__.items() \
                      if not attribute.startswith('_') and not attribute.endswith('__') and not callable(getattr(self, attribute, None))}
        return attributes


class GbpWSDataSource(GbpDataSource):
    """ Fuente de datos de GBP a través de WEB SERVICE
    """
    pass


class GbpDbDataSource(GbpDataSource):
    """ Fuente de datos de GBP a través de una DATABASE
    """
    pass


class GbpExcelDataSource(GbpDataSource):
    """ Fuente de datos de GBP a través de PLANILLA EXCEL
    """

    _spreadsheet_name = None
    _spreadsheet_schema = None
    _row_object = None


    def __init__(self):
        self.items = []


    def show_attr(self):
        return vars(self._spreadsheet_schema)


    #def get_schema_idxs(self):
    #    schema_col_idxs = [col[0] for col in self._spreadsheet_schema.__dict__.values() if isinstance(col, tuple)]
    #    return schema_col_idxs
    def get_schema_idxs(self):
        return get_schema_idxs(self._spreadsheet_schema)

    
    def get_schema(self):
        schema = {schema_field: schema_col[0] for schema_field, schema_col in self._spreadsheet_schema.__dict__.items() if isinstance(schema_col, tuple)}
        return schema


    def set_attributes(self, attribute, value):
        """ Setea attribute con value en cada item de self.items 
        """        
        # Valida que self.items no esté vacío, y si lo está, obtiene los items
        if not self.items:
            self.get_data()

        # Valida que el attribute sea válido
        self_attributes = [attribute for attribute in self.items[0].__dict__.keys()]

        if attribute not in self_attributes:
            logging.error(f"El campo {attribute} no está definido en el esquema de planilla excel {self.items[0].__class__.__name__}")
            return False        

        for item in self.items:
            setattr(item, attribute, value)
            return True


    def set_clone_fields(self, original_field, clone_field):
        """ Setea el atributo clone_field con el valor original_field en cada item de self.items
        """

        # Valida que self.items no esté vacío, y si lo está, obtiene los items
        if not self.items:
            self.get_data()

        self_attributes = [attribute for attribute in self.items[0].__dict__.keys()]

        # Valida que el clone_field sea un atributo válido
        if clone_field not in self_attributes:
            logging.error(f"El campo {clone_field} no está definido en el esquema de planilla excel {self.items[0].__class__.__name__}")
            return False

        # Valida que el original_field sea un atributo válido
        if original_field not in self_attributes:
            logging.error(f"El campo {original_field} no está definido en el esquema de planilla excel {self.items[0].__class__.__name__}")
            return False
        

        for item in self.items:
            value_to_clone = getattr(item, original_field)
            setattr(item, clone_field, value_to_clone)
            #logging.debug(f'Clonado {original_field} = {value_to_clone} a {clone_field}')
        return True


    def set_ids(self, field_name, reference_source):
        """ Setea el ID del field_name
        """
        
        # Arma diccionario con {field_name: col_idx}
        schema = reference_source.get_schema()

        # Valida que el campo esté definido en el esquema de planilla excel
        if field_name not in schema.keys():
            logging.error(f"El campo {field_name} no está definido en el esquema de planilla excel {reference_source._spreadsheet_schema.__name__}")
            return False

        # Valida que self.items no esté vacío, y si lo está, obtiene los items
        if not self.items:
            self.get_data()

        for item in self.items:
            item.set_id(field_name, reference_source)

        ## Carga reference_source
        #reference_source.get_data()
        #
        ## Setea el ID del campo "id_ + field_name" en cada item de self.items
        #id_field_name = 'id_' + field_name
        #
        #for item in self.items:
        #    field_name_value = getattr(item, field_name)
        #
        #    for reference_item in reference_source.items:
        #        reference_attribute = getattr(reference_item, field_name)
        #        reference_id = getattr(reference_item, id_field_name)
        #        #logging.debug(f'Comparando {field_name_value} con {reference_attribute}')
        #        if field_name_value == reference_attribute:
        #            setattr(item, id_field_name, reference_id)
        #            #logging.info(f'Agregado ID {reference_id} a {id_field_name} para {field_name} = {field_name_value}')                
        

    def get_data(self, filename = None, path_to_data_dir = None, spreadsheet_schema = None, item = None, row_object = None, *fields):
        """ Lee el archivo de planilla y carga las filas en la lista self.items
        """

        # Validate input parameters
        
        if not filename:
            if not self._spreadsheet_name:
                logging.error(f"No se ha definido el nombre del archivo de planilla para el archivo {file_path}")
                return False
            else:
                filename = self._spreadsheet_name

        if path_to_data_dir != None:
            path_to_data_dir = data_dir
    
        file_path = data_dir + "/" + filename

        if not spreadsheet_schema:
            if not self._spreadsheet_schema:
                logging.error(f"No se ha definido el esquema de planilla para el archivo {file_path}")
                return False                
            else:
                spreadsheet_schema = self._spreadsheet_schema
                #logging.debug(f'Schema: {vars(spreadsheet_schema)}')

        if not row_object:
            if not self._row_object:
                logging.error(f"No se ha definido el objeto de planilla para el archivo {file_path}")
                return False
            else:
                row_object = self._row_object

        # Set fields to get from excel
                
        schema_fields = spreadsheet_schema.get_fields()
        if not fields:
            fields = schema_fields   # trae todos los campos definidos en el schema
        else:
            # Validate fields
            for field in fields[:]:
                if not field in schema_fields:
                    logging.error(f"Se omite el campo {field}. No está definido en el esquema de planilla excel {self.__class__.__name__}")
                    #print(f"Se omite el campo {field}. No está definido en el esquema de planilla excel PublisGbpSchema")
                    fields.remove(field)

        # Gets data from spreadsheet
                    
        # Loads spreadsheet
                    
        wb = load_workbook(filename = file_path)
        sheet = wb.active

        # Retrieves each spreadhseet row              

        #schema_col_idxs = [col[0] for attr, col in spreadsheet_schema.__dict__.items() if isinstance(col, tuple)]
        schema_col_idxs = self.get_schema_idxs()
        #logging.debug(f'schema_items: {spreadsheet_schema.__dict__.items()}')
        #logging.debug(f'schema_col_idxs generado: {schema_col_idxs}')

        for row in sheet.iter_rows(min_row=2):
            item = row_object
            item.get_row_data(row, spreadsheet_schema=spreadsheet_schema, sheet=sheet)
            item.gbp_table = self._gbp_table

        
            # Appends item to item list
            self.items.append(deepcopy(item))
            #logging.info(f'Agregando item: {item}')

        # Sets gbp_table attribute for GbpSeveralTablesItems
        if self._row_object == GbpSeveralTablesItem():
            for item in self.items:
                item.gbp_table = self.gbp_table

        #self.show_data()
        logging.info(f'Encontrados {len(self.items)} items para {self.__class__.__name__} de la planilla {filename}')

        return self.items
    

    def show_data():
        pass


@dataclass
class GbpItem:

    def get_row_data(self, row, spreadsheet_schema = None, sheet = None):
        # Retrieves a spreadhseet row              

        for idx, cell in enumerate(row):
            #logging.debug(f"Row cells: idx {idx} cell value {cell.value}")
            #logging.debug(f'{ListasPreciosGbpSchema.__dict__.items()}')
            spreadsheet_schema_class = type(spreadsheet_schema)
            schema_col_idxs = [col[0] for attr, col in spreadsheet_schema_class.__dict__.items() if isinstance(col, tuple)]
            #logging.debug(f'schema_col_idxs: {schema_col_idxs}')
            if idx in schema_col_idxs:
                field_name = get_field_name(idx, spreadsheet_schema_class)
                #logging.info(f'Got this field names: {field_name} - {cell.value}')
                setattr(self, field_name, cell.value)
                #logging.debug(f'setting attr: {field_name} {cell.value}')
        #logging.debug(f'spreadshet_schema: {spreadsheet_schema.}')
        
        #logging.debug(" ")
                
            
@dataclass    
class GbpMlItem(GbpItem):
    """ Clase que representa una publicación de ML en GBP
    """
    
    ml_item_id: str = field(default=None, repr=True)
    sku: str = field(default=None, repr=True)
    variation_id: str = field(default=None, repr=True)
    store: str = field(default=None, repr=True)
    price_list: str = field(default=None, repr=True)
    price_list_id: int = field(default=None, repr=True)
    warehouse: str = field(default=None, repr=True)
    warehouse_id: int = field(default=None, repr=True)
    type: str = field(default=None, repr=True)
    ml_title: str = field(default=None, repr=True)
    gbp_title: str = field(default=None, repr=True)
    gbp_id: int = field(default=None, repr=True)

    def __repr__(self):
        attributes = {attr: value for attr, value in self.__dict__.items() if not attr.startswith('_') and not attr.endswith('__') and value != None}
        return f'{self.__class__.__name__}: {attributes}'
    
    def format_ml_item_id(self):
        """ Agrega prefijo MLA al ml_item_id, si no lo tiene
        """
        if not self.ml_item_id.startswith("MLA"):
            self.ml_item_id = "MLA" + self.ml_item_id
            return True


@dataclass    
class GbpArticle(GbpItem):
    """ Clase que representa un artículo (producto) en GBP
    """
    
    gbp_id: int = field(default=None, repr=True)
    sku: str = field(default=None, repr=True)
    title: str = field(default=None, repr=True)
    description: str = field(default=None, repr=True)
    category: str = field(default=None, repr=True)
    sub_category: str = field(default=None, repr=True)
    auxiliary_sub_category: str = field(default=None, repr=True)
    brand: str = field(default=None, repr=True)
    detail: str = field(default=None, repr=True)    # por lo gral clona la info de title
    supplier: str = field(default=None, repr=True)
    iva: str = field(default=None, repr=True)

    #TODO: objeto GbpPrices
    #prices: GbpPrices = field(default=None, repr=True)


    def __repr__(self):
        attributes = {attr: value for attr, value in self.__dict__.items() if not attr.startswith('_') and not attr.endswith('__') and value != None}
        return f'{self.__class__.__name__}: {attributes}'
    
        

@dataclass
class ListaPreciosGBP(GbpItem):
    """ Clase que representa una lista de precios de GBP
    """
    gbp_table: str = "lista_precios"
    name: str = field(default=None, repr=True)
    extra: str = field(default=None, repr=True)
    id_gbp: int = field(default=None, repr=True)


@dataclass
class ListaCostoGBP(GbpItem):
    """ Clase que representa una lista de costos de GBP
    """
    gbp_table: str = "lista_costos"
    name: str = field(default=None, repr=True)
    extra: str = field(default=None, repr=True)
    id_gbp: int = field(default=None, repr=True)


@dataclass
class GbpSeveralTablesItem(GbpItem):
    """ Clase que representa un ítem de varias tablas de GBP para usarse en la tabla gbp_several_tables
    """    
    name: str = field(default=None, repr=True)
    extra: str = field(default=None, repr=True)
    id_gbp: int = field(default=None, repr=True)
    gbp_table: str = field(default=None, repr=True)


@dataclass
class GBPWarehouse:
    """ Clase que representa un deposito de GBP
    """
    name: str
    id_gbp: int


@dataclass
class StoreGBP:
    """ Clase que representa una tienda de ML en GBP
    """
    name: str
    id_gbp: int
    id_ml: str


class PublisGbpSchema(ExcelSchema):
    """ Esquema de planilla de publicaciones de ML en GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "Publis_GBP.xlsx"    

    ml_item_id = (3, "Mercadolibre©   ID de Publicacion", 30)
    sku = (5, "Codigo  \nArticulo", 20)
    title = (7, "Titulo de la Publicacion", 50)
    type = (8, "Tipo   de Publicacion", 20)
    gbp_name = (6, "Articulo", 50)
    gbp_id = (36, "ID", 15)
    store = (27, "Tienda", 20)
    price_list = (28, "Lista de Precios", 25)

    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(PublisGbpSchema.__dict__.keys())
        return attribute_names


class ArticulosExtendidaGbpSchema(ExcelSchema):
    """ Esquema de planilla de artículos extendida de ML en GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "Articulos_GBP_extendida.xlsx"    

    sku = (6, "Codigo/EAN", 15)
    description = (7, "Descripcion del Articulo", 50)
    category = (10, "Categorias", 20)
    sub_category = (11, "SubCategorias", 20)
    auxiliary_sub_category = (12, "Sub Categoria Auxiliar", 20)
    brand = (14, "Marca", 20)
    detail = (17, "Detalle", 50)
    supplier = (20, "Proveedor", 30)
    iva = (25, "Impuesto al valor agregado", 15)
    ml_title = (140, "Titulo para MercadoLibre©", 50)   #! CHEKEAR COLUMNA
    ml_description = (141, "Descripcion Texto de la Publicacion en MercadoLibre©", 100)     #! CHEKEAR COLUMNA
    gbp_id = (200, "ID", 15)   #! CHEKEAR COLUMNA


    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(ArticulosExtendidaGbpSchema.__dict__.keys())
        return attribute_names
    

class ImportPublisGBP(ExcelSchema):
    """ Formato atributos:\n
    Atributos de nombres:\n
    _sheet_name = nombre            #   Usado para el nombre del archivo excel y de la hoja activa\n
    _ spreadsheet_name = nombre     #   Usado para el nombre del archivo excel\n

    Atributos con mapeo de la planilla:\n
    atributo_en_clase_original  = (mapeo en planilla gbp)\n
    atributo                    = (# col, título col, ancho col)
    """
    _sheet_name = "PublicacionesMercadoLibre"
    _spreadsheet_name = "import_publis_gbp.xlsx"

    ml_item_id = (1, "ID Publicación de MercadoLibre©", 30)
    sku = (2, "Código EAN del Artículo", 25)
    variation_id = (3, "ID de la Variación", 20)
    price_list_id = (4, "ID de Lista de Precios", 20)
    warehouse_id = (5, "ID de Depósito", 20)


class ListasPreciosGbpSchema(ExcelSchema):
    """ Esquema de planilla de Listas de Precios de GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "gbp_listasprecios.xlsx"  

    gbp_id = (14, "ID", 15)
    #name = (4, "Descr&#161;pcion", 20)
    name = (4, "Descripcion", 20)

    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(ListasPreciosGbpSchema.__dict__.keys())
        return attribute_names


class ListasCostosGbpSchema(ExcelSchema):
    """ Esquema de planilla de Listas de Costos de GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "gbp_listascostos.xlsx"  

    gbp_id = (12, "ID", 15)
    #name = (4, "Descr&#161;pcion", 20)
    name = (4, "Descripcion", 20)

    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(ListasCostosGbpSchema.__dict__.keys())
        return attribute_names
    

class DepositosGbpSchema(ExcelSchema):
    """ Esquema de planilla de Depositos de GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "gbp_depositos.xlsx"  

    gbp_id = (4, "ID", 15)
    name = (3, "Descripcion", 20)


    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(DepositosGbpSchema.__dict__.keys())
        return attribute_names
    

class CategoriasGbpSchema(ExcelSchema):
    """ Esquema de planilla de Categorias de GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "gbp_categorias.xlsx"  

    gbp_id = (9, "ID", 15)
    name = (3, "Descripcion", 20)


    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(CategoriasGbpSchema.__dict__.keys())
        return attribute_names


class SubcategoriasGbpSchema(ExcelSchema):
    """ Esquema de planilla de SubCategorias de GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "gbp_subcategorias.xlsx"  

    gbp_id = (10, "ID", 15)
    name = (3, "Categorias", 20)
    extra = (4, "Descripcion", 20)


    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(SubcategoriasGbpSchema.__dict__.keys())
        return attribute_names
    

class SubcategoriasAuxiliaresGbpSchema(ExcelSchema):
    """ Esquema de planilla de SubCategorias Auxiliares de GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "gbp_subcategorias_auxiliares.xlsx"  

    gbp_id = (10, "ID", 15)
    name = (3, "Descripcion", 20)


    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(SubcategoriasAuxiliaresGbpSchema.__dict__.keys())


class MarcasGbpSchema(ExcelSchema):
    """ Esquema de planilla de Marcas de GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "gbp_marcas.xlsx"  

    gbp_id = (7, "ID", 15)
    name = (2, "Descripcion", 20)


    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(MarcasGbpSchema.__dict__.keys())


class MonedasGbpSchema(ExcelSchema):
    """ Esquema de planilla de Monedas de GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "gbp_monedas.xlsx"  

    gbp_id = (5, "ID", 15)
    name = (2, "Moneda", 20)


    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(MonedasGbpSchema.__dict__.keys())


class TiendasGbpSchema(ExcelSchema):
    """ Esquema de planilla de Tiendas de GBP
    attributte (data reference) = excel column
    """
    _sheet_name = "Table"
    _spreadsheet_name = "gbp_tiendas.xlsx"  

    gbp_id = (33, "ID", 15)
    name = (6, "Descripcion", 20)
    extra  = (9, "MercadoLibre©:  ID de Usuario", 20)    


    @classmethod
    def get_fields(cls):
        """ Devuelve una lista con los campos definidos en el schema.
        """
        attribute_names = list(MonedasGbpSchema.__dict__.keys())


class ExcelPublisGbp(GbpExcelDataSource):
    """ Planilla Excel con publicaciones de ML en GBP
    """

    # 
    spreadsheet_schema = PublisGbpSchema()
    row_object = GbpMlItem()

    def __init__(self):
        self.items = []


    def get_data(self, filename, path_to_data_dir = None, *fields):
        """ Lee el archivo de planilla y carga las publicaciones en la lista publis
        """

        if path_to_data_dir != None:
            path_to_data_dir = data_dir
    
        file_path = data_dir + "/" + filename
        
        # Set fields to get from excel
        schema_fields = PublisGbpSchema.get_fields()
        if not fields:
            fields = schema_fields   # trae todos los campos definidos en el schema
        else:
            # Validate fields
            for field in fields[:]:
                if not field in schema_fields:
                    logging.error(f"Se omite el campo {field}. No está definido en el esquema de planilla excel PublisGbpSchema")
                    #print(f"Se omite el campo {field}. No está definido en el esquema de planilla excel PublisGbpSchema")
                    fields.remove(field)

        # Gets data from spreadsheet
                    
        # Loads spreadsheet
        wb = load_workbook(filename = file_path)
        sheet = wb.active

        
        def get_field_name(field_id):
            for k, v in PublisGbpSchema.__dict__.items():
                if v[0] == field_id:
                    return k

        # Retrieves each spreadhseet row              
        for row in sheet.iter_rows(min_row=2):
            item = GbpMlItem()
            for idx, cell in enumerate(row):
                #logging.debug(f"col: {col}, cell: {cell.value}")

                schema_col_idxs = [col[0] for attr, col in PublisGbpSchema.__dict__.items() if isinstance(col, tuple)]
                if idx in schema_col_idxs:
                    field_name = get_field_name(idx)
                    #logging.info(f'{field_name} - {cell.value}')
                    setattr(item, field_name, cell.value)
                
            self.items.append(item)
            
        
        #self.show_data()
        #logging.info(f"items: {len(self.items)}")

        return self.items
        

    def show_data(self):
        for item in self.items:
            print(item)
        return True
            

class ExcelArticulosExtendidaGbp(GbpExcelDataSource):
    """ Planilla Excel con articulos extendida de GBP
    """

    # 
    spreadsheet_schema = ArticulosExtendidaGbpSchema()
    row_object = GbpArticle()

    def __init__(self):
        self.items = []


    def get_data(self, filename, path_to_data_dir = None, *fields):
        """ Lee el archivo de planilla y carga las publicaciones en la lista publis
        """

        if path_to_data_dir != None:
            path_to_data_dir = data_dir
    
        file_path = data_dir + "/" + filename
        
        # Set fields to get from excel
        schema_fields = ArticulosExtendidaGbpSchema.get_fields()
        if not fields:
            fields = schema_fields   # trae todos los campos definidos en el schema
        else:
            # Validate fields
            for field in fields[:]:
                if not field in schema_fields:
                    logging.error(f"Se omite el campo {field}. No está definido en el esquema de planilla excel PublisGbpSchema")
                    #print(f"Se omite el campo {field}. No está definido en el esquema de planilla excel PublisGbpSchema")
                    fields.remove(field)

        # Gets data from spreadsheet
                    
        # Loads spreadsheet
        wb = load_workbook(filename = file_path)
        sheet = wb.active

        
        def get_field_name(field_id):
            for k, v in ArticulosExtendidaGbpSchema.__dict__.items():
                if v[0] == field_id:
                    return k

        # Retrieves each spreadhseet row              
        for row in sheet.iter_rows(min_row=2):
            article = GbpArticle()
            for idx, cell in enumerate(row):
                #logging.debug(f"col: {col}, cell: {cell.value}")

                schema_col_idxs = [col[0] for attr, col in ArticulosExtendidaGbpSchema.__dict__.items() if isinstance(col, tuple)]
                if idx in schema_col_idxs:
                    field_name = get_field_name(idx)
                    #logging.info(f'{field_name} - {cell.value}')
                    setattr(article, field_name, cell.value)
                
            self.items.append(article)
            
        
        #self.show_data()
        #logging.info(f"items: {len(self.items)}")

        return self.items
        

    def show_data(self):
        for item in self.items:
            print(item)
        return True            


class ExcelListasPreciosGbp(GbpExcelDataSource):
    """ Planilla Excel con Listas de Precios de GBP
    """

    def __init__(self):
        self.items = []

    _spreadsheet_schema = ListasPreciosGbpSchema()
    _row_object = GbpSeveralTablesItem()
    _gbp_table = "listas_precios" 


class ExcelListasCostosGbp(GbpExcelDataSource):
    """ Planilla Excel con Listas de Costos de GBP
    """

    def __init__(self):
        self.items = []

    _spreadsheet_schema = ListasCostosGbpSchema()
    _row_object = GbpSeveralTablesItem()
    _gbp_table = "listas_costos" 


class ExcelDepositosGbp(GbpExcelDataSource):
    """ Planilla Excel con Depósitos de GBP
    """

    def __init__(self):
        self.items = []

    _spreadsheet_schema = DepositosGbpSchema()
    _row_object = GbpSeveralTablesItem()
    _gbp_table = "depositos" 


class ExcelCategoriasGbp(GbpExcelDataSource):
    """ Planilla Excel con Categorías de GBP
    """

    def __init__(self):
        self.items = []

    _spreadsheet_schema = CategoriasGbpSchema()
    _row_object = GbpSeveralTablesItem()
    _gbp_table = "categorias" 


class ExcelSubcategoriasGbp(GbpExcelDataSource):
    """ Planilla Excel con SubCategorías de GBP
    """

    def __init__(self):
        self.items = []

    _spreadsheet_schema = SubcategoriasGbpSchema()
    _row_object = GbpSeveralTablesItem()
    _gbp_table = "subcategorias" 


class ExcelSubcategoriasAuxiliaresGbp(GbpExcelDataSource):
    """ Planilla Excel con SubCategorías Auxiliares de GBP
    """

    def __init__(self):
        self.items = []

    _spreadsheet_schema = SubcategoriasAuxiliaresGbpSchema()
    _row_object = GbpSeveralTablesItem()
    _gbp_table = "subcategorias_auxiliares" 


class ExcelMarcasGbp(GbpExcelDataSource):
    """ Planilla Excel con Marcas de GBP
    """

    def __init__(self):
        self.items = []

    _spreadsheet_schema = MarcasGbpSchema()
    _row_object = GbpSeveralTablesItem()
    _gbp_table = "marcas" 


class ExcelMonedasGbp(GbpExcelDataSource):
    """ Planilla Excel con Monedas de GBP
    """

    def __init__(self):
        self.items = []

    _spreadsheet_schema = MonedasGbpSchema()
    _row_object = GbpSeveralTablesItem()
    _gbp_table = "monedas" 


class ExcelTiendasGbp(GbpExcelDataSource):
    """ Planilla Excel con Tiendas de GBP
    """

    def __init__(self):
        self.items = []

    _spreadsheet_schema = TiendasGbpSchema()
    _row_object = GbpSeveralTablesItem()
    _gbp_table = "tiendas" 

#
#class GbpSkuMlItem(Base):
#    """ Clase que representa un registro de la tabla gbp_sku_ml_item, que almacena los skus que contiene cada publi ML
#    """
#
#    __tablename__ = "gbp_sku_ml_item"
#
#    ml_item_id = Column(String (20), primary_key=True, index=True)
#    sku = Column(String (100))
#
#    def __init__(self, **kwargs):
#        
#        if kwargs:
#            for k, v in kwargs.items():
#                setattr(self, k, v)
#
#    
#    def __repr__(self):
#        return f"id_ml: {self.ml_item_id}, sku: {self.sku}"
#    
#
#    def get_data_from_gbp_item(self, gbp_ml_item):
#        
#        class_table = self.__table__
#        attributes = class_table.columns.keys()
#        
#        for attribute in attributes:
#            if attribute in gbp_ml_item.__dict__.keys():
#                setattr(self, attribute, getattr(gbp_ml_item, attribute))
#
#        
#    def is_on_db(self, session):
#        
#        sku_on_db = session.query(GbpSkuMlItem).filter(GbpSkuMlItem.ml_item_id == self.ml_item_id).first()
#        
#        if sku_on_db:
#            return True
#        return False
#    
#    def insert_into_db(self, session):
#        
#        try:
#            session.add(self)
#            session.commit()
#            print(f'Producto {self.sku} insertado correctamente.')
#            session.close()
#            return True
#        
#        except IntegrityError as e:
#            print(f'Error al insertar el producto {self}: {e}')
#            return False            
#        
#        except Exception as e:
#            print(f'Error al insertar el producto {self}: {e}')
#            return False
#
#
#class GbpSeveralTables_DbItem(Base):
#    """ Clase que representa un registro de la tabla gbp_several_tables, que almacena data de distintas tablas de GBP:\n
#    Lista de precios\n
#    Lista de costos\n
#    Depósitos\n
#    Categorias\n
#    Subcategorías\n
#    Subcategoria Auxiliar\n
#    Marcas\n
#    Monedas\n
#    Tiendas ML\n
#    """
#
#    __tablename__ = "gbp_several_tables"
#
#    db_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
#    gbp_table = Column(String (50))
#    gbp_id = Column(String (20))
#    name = Column(String (100))
#    extra = Column(String (100))
#
#    def __init__(self, **kwargs):
#        
#        if kwargs:
#            for k, v in kwargs.items():
#                setattr(self, k, v)    
#
#    def __repr__(self):
#        return f"db_id: {self.db_id}, table: {self.gbp_table}, gbp_id: {self.gbp_id}, name: {self.name}, extra: {self.extra}"
#    
#    def is_on_db(self, session):
#        
#        item_on_db = session.query(GbpSeveralTables_DbItem).filter(GbpSeveralTables_DbItem.gbp_id == self.gbp_id, GbpSeveralTables_DbItem.gbp_table == self.gbp_table).first()
#        
#        if item_on_db:
#            logging.debug(f'{self.name} gbp_id {self.gbp_id} in on db already')
#            return True
#        logging.debug(f'{self.name} gbp_id {self.gbp_id} not in on db')
#        return False
#    



class Tables:
    """ Mapa de tablas de la base de datos con sus respectivas clases (SQLAlchemy)
    """
    #costos_mg = CostoMG()
    #disponibilidad_stock_mg = DisponibilidadStock()
    #productos_mg = ItemMG()
    gbp_sku_ml_item = GbpSkuMlItem()
    
    
class Spreadsheets:
    """ Mapa de planillas con data de GBP con sus respectivas clases
    """
    publis_gbp = ExcelPublisGbp()


def update_db_from_excel(filename = None, table = None, session = None):

    # Valida que los argumentos necesarios estén presentes
    if filename == None or table == None or session == None:
        print(f'Argumento faltante. Se requiere el ingreso de todos los argumentos (filename, table, session)')
        return False
    
    # TODO: Validar los tipos de datos que contienen los argumentos

    # Define el objeto que contiene los datos de la planilla
    spreadsheet_name = filename.split(".")[0].lower()
    excel_item_class = getattr(Spreadsheets, spreadsheet_name).__class__.__name__
    excel_items = create_class_instance(excel_item_class)

    # Define el objeto que contiene los datos de la tabla    
    db_item_class = getattr(Tables, table).__class__.__name__

    # Lee los datos de la planilla y los carga en el objeto de la planilla
    excel_items.get_data(filename = filename)


    for excel_item in excel_items.items:
        db_item = create_class_instance(db_item_class)
        db_item.get_data_from_gbp_item(excel_item)
        #break
        if not db_item.is_on_db(session):
            print(f'Insertando en la base de datos {db_item}')
            db_item.insert_into_db(session)
    return True


def create_excel(items: List[Type], spreadsheet_type: Type, filename: str = None, sheet_name: str = None, path_to_data_dir: str = None, *fields) -> bool:
    """ Crea una planilla de excel a partir de una lista de objetos.\n
    Args:\n
        items = lista de objetos.\n
        spreadsheet_type = clase que contiene definiciones de la planilla a partir de objetos heredados de ExcelSchema. Nombre de archivo, nombre de hoja activa, mapeo de columnas.\n
        filename = permite sobreescribir el nombre de archivo a generar definido en el ExcelSchema.\n
        sheet_name = permite sobreeescribir el nombre de hoja activa definido en el ExcelSchema.\n
        path_to_data_dir = ruta absoluta al directorio data donde se guarda el achivo.\n
        *fields = args no implementados hasta el momento.        
    """

    # Sets output file and it's location
    if filename == None:
        filename = spreadsheet_type._spreadsheet_name

    if path_to_data_dir == None:
        file_path = filename
    else:
        path_to_data_dir = data_dir
        file_path = data_dir + "/" + filename
        
    ## Creates new worksheet        #   creándola de cero no logro que la reconozca GBP
    #wb = Workbook()
    #sheet = wb.active
    #if sheet_name:
    #    sheet.title = sheet_name
    #else:
    #    sheet.title = spreadsheet_type._sheet_name
        
    # Loads template worksheet
    wb = load_workbook(filename = file_path)
    sheet = wb.active

    # Clear existing data        
    sheet.delete_rows(2, sheet.max_row)

    # Retrieves class attributes
    class_attributes = {attribute: value for attribute, value in vars(spreadsheet_type).items() if not attribute.startswith('_') and not attribute.endswith('__')}

    # Sets spreadsheet first row with column names
    for idx, column in enumerate(class_attributes.values()):
        logging.debug(f'{column[0]} / {chr(column[0] + 64)} -- {column[1]}')
        sheet.cell(1, column[0]).value = column[1]
        sheet.column_dimensions[chr(column[0] + 64)].width = column[2]

    # Populates spreadsheet with data
    for idx, item in enumerate(items):
        row = idx + 2

        for attribute in class_attributes.keys():
            #setattr(item, attribute, sheet.cell(row, getattr(spreadsheet_type, attribute)[0]))
            setattr(sheet.cell(row, getattr(spreadsheet_type, attribute)[0]), "value", str(getattr(item, attribute)))

    # Saves spreadsheet file
    wb.save(file_path)
    logging.info(f'Planilla {file_path} creada correctamente.')
    return True


def get_list_id_from_desc(lista_de_precios_gbp, name):
    """ Función que devuelve el id de una lista de precios de GBP a partir de su descripción
    """
    for lista in lista_de_precios_gbp:
        if lista.extra == name:
            return lista.id_gbp

    return None


def get_warehouse_id_from_name(depositos_gbp, name):
    """ Función que devuelve el id de un deposito de GBP a partir de su nombre
    """
    for deposito in depositos_gbp:
        if deposito.name == name:
            return deposito.id_gbp

    return None


# DATA

listas_de_precios_gbp = [ListaPreciosGBP(extra="ml_clasica", name="ML Clásica",id_gbp=1),
                         ListaPreciosGBP(extra="ml_premium", name="ML Premium",id_gbp=5),
                         ListaPreciosGBP(extra="ml_3csi", name="ML 3 Cuotas Sin Interés",id_gbp=22),                         
                         ListaPreciosGBP(extra="mg_tecnorium_clasica", name="MG Tecnorium Clásica",id_gbp=10),
                         ListaPreciosGBP(extra="mg_tecnorium_premium", name="MG Tecnorium Premium",id_gbp=12),
                         ListaPreciosGBP(extra="mg_lenovo_clasica", name="MG Lenovo Clásica",id_gbp=11),
                         ListaPreciosGBP(extra="mg_lenovo_premium", name="MG Lenovo Premium",id_gbp=13)]

depositos_gbp = [GBPWarehouse(name="Perón", id_gbp=1)]

tiendas_gbp = [{"tienda": "Tecnorium"}, {"tienda": "Celestron"}, {"tienda": "Lenovo"}]

tiendas_gbp = [StoreGBP(name="Tecnorium", id_gbp=1, id_ml="77581040"),
               StoreGBP(name="Celestron", id_gbp=2, id_ml="146367667"),
               StoreGBP(name="Lenovo", id_gbp=3, id_ml="301181249")]


if __name__ == "__main__":
    
    """
    database = Database(db_location = "desarrollo")

    #   Create database session
    Session = sessionmaker(bind=database.engine)
    session = Session()    


    # ! Descomentar para crear tablas nuevas que se hayan definido
    #create_tables(database.engine)

    # Retrieves publis ML from spreadsheet
    publis_gbp = ExcelPublisGbp()
    publis_gbp.get_data(filename = "Publis_GBP.xlsx")
    
    # Inserts into gbp_sku_ml_item database table the items that aren't present already
    for publi_gbp in publis_gbp.items:
        publi_db = GbpSkuMlItem()
        publi_db.get_data_from_gbp_item(publi_gbp)
        
        if not publi_db.is_on_db(session):
            logging.info(f'Insertando en la base de datos {publi_db}')
            publi_db.insert_into_db(session)


        
    database.connection.close()
    """    


    