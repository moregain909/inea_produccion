import unittest
from unittest.mock import patch
from datetime import datetime
from bs4 import BeautifulSoup
import os, sys; 

path2root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(path2root)
from precios_mg import parse_mgcat, ProductoMG, mg_get_products

class TestParseMGCat(unittest.TestCase):

    def setUp(self):
        # Sample XML response for testing
        self.sample_xml = """
            <catalog>
                <item>
                    <partNumber>123</partNumber>
                    <descripcion>Product 1</descripcion>
                    <codMarca>Brand1</codMarca>
                    <categoria>Category1</categoria>
                    <codCategoria>1</codCategoria>
                    <precio>10.99</precio>
                    <stock>100</stock>
                    <iva_pct>0.18</iva_pct>
                    <upc>123456789012</upc>
                </item>
                <item>
                    <partNumber>456</partNumber>
                    <descripcion>Product 2</descripcion>
                    <codMarca>Brand2</codMarca>
                    <categoria>Category2</categoria>
                    <codCategoria>2</codCategoria>
                    <precio>20.99</precio>
                    <stock>50</stock>
                    <iva_pct>0.12</iva_pct>
                    <upc>987654321098</upc>
                </item>
            </catalog>
        """

    def test_default_args(self):
        parsed_data = parse_mgcat(self.sample_xml)
        self.assertEqual(len(parsed_data), 2)
        self.assertIsInstance(parsed_data[0], ProductoMG)
        self.assertIsInstance(parsed_data[1], ProductoMG)
        # Add more assertions based on your expected data

    def test_custom_args(self):
        custom_args = {
            "timestamp": False,
            "sku": False,
            "nombre": True,
            "marca": True,
            "categoria": False,
            "cod_cat": False,
            "costo": True,
            "stock": True,
            "iva": False,
            "ean": True
        }
        parsed_data = parse_mgcat(self.sample_xml, **custom_args)
        self.assertEqual(len(parsed_data), 2)
        self.assertIsInstance(parsed_data[0], ProductoMG)
        self.assertIsInstance(parsed_data[1], ProductoMG)


    def test_price_args(self):
        custom_args = {
            "timestamp": True,
            "sku": True,
            "costo": True,
        }
        parsed_data = parse_mgcat(self.sample_xml, **custom_args)
        self.assertEqual(len(parsed_data), 2)
        self.assertIsInstance(parsed_data[0].timestamp, datetime)
        self.assertIsInstance(parsed_data[0].sku, str)
        self.assertIsInstance(parsed_data[0].nombre, bool)
        self.assertEqual(parsed_data[0].nombre, False)
        self.assertEqual(parsed_data[0].marca, False)
        self.assertEqual(parsed_data[0].categoria, False)
        self.assertEqual(parsed_data[0].cod_cat, False)
        self.assertIsInstance(parsed_data[0].costo, float)
        self.assertEqual(parsed_data[0].stock, False)
        self.assertEqual(parsed_data[0].iva, False)
        self.assertEqual(parsed_data[0].ean, False)

    def test_stock_args(self):
        custom_args = {
            "timestamp": True,
            "sku": True,
            "stock": True,
        }
        parsed_data = parse_mgcat(self.sample_xml, **custom_args)
        self.assertEqual(len(parsed_data), 2)
        self.assertIsInstance(parsed_data[0].timestamp, datetime)
        self.assertIsInstance(parsed_data[0].sku, str)
        self.assertIsInstance(parsed_data[0].nombre, bool)
        self.assertEqual(parsed_data[0].nombre, False)
        self.assertEqual(parsed_data[0].marca, False)
        self.assertEqual(parsed_data[0].categoria, False)
        self.assertEqual(parsed_data[0].cod_cat, False)
        self.assertIsInstance(parsed_data[0].stock, int)
        self.assertEqual(parsed_data[0].costo, False)
        self.assertEqual(parsed_data[0].iva, False)
        self.assertEqual(parsed_data[0].ean, False)

    def test_producto_args(self):
        custom_args = {
            "timestamp": True,
            "sku": True,
            "nombre": True, 
            "marca": True, 
            "categoria": True, 
            "cod_cat": True, 
            "costo": True, 
            "stock": True,
            "iva": True, 
            "ean": True
        }
        parsed_data = parse_mgcat(self.sample_xml, **custom_args)
        self.assertEqual(len(parsed_data), 2)
        self.assertIsInstance(parsed_data[0].timestamp, datetime)
        self.assertIsInstance(parsed_data[0].sku, str)
        self.assertIsInstance(parsed_data[0].nombre, str)
        self.assertIsInstance(parsed_data[0].marca, str)
        self.assertIsInstance(parsed_data[0].categoria, str)
        self.assertIsInstance(parsed_data[0].cod_cat, str)
        self.assertIsInstance(parsed_data[0].stock, int)
        self.assertIsInstance(parsed_data[0].costo, float)
        self.assertIsInstance(parsed_data[0].iva, float)
        self.assertIsInstance(parsed_data[0].ean, str)



class TestMGGetProducts(unittest.TestCase):

    def setUp(self):
        # Sample XML response for testing
        self.sample_xml = """
            <catalog>
                <item>
                    <partNumber>123</partNumber>
                    <descripcion>Product 1</descripcion>
                    <codMarca>Brand1</codMarca>
                    <categoria>Category1</categoria>
                    <codCategoria>1</codCategoria>
                    <precio>10.99</precio>
                    <stock>100</stock>
                    <iva_pct>0.18</iva_pct>
                    <upc>123456789012</upc>
                </item>
            </catalog>
        """

    # 
    @patch('precios_mg.precios_mg_helpers.parse_mgcat')
    def test_default_format(self, mock_parse_mgcat):
        # Set up the mock return value
        mock_parse_mgcat.return_value = [ProductoMG()]

        products = mg_get_products(self.sample_xml)

        # Assertions based on the expected behavior
        self.assertIsInstance(products, list)
        self.assertEqual(len(products), 1)
        self.assertTrue(all(isinstance(product, ProductoMG) for product in products))
        self.assertTrue(all(hasattr(product, attr) for product in products for attr in ["timestamp", "sku", "nombre", "marca", "categoria", "cod_cat", "costo", "stock", "iva", "ean"]))

        # Ensure that parse_mgcat was called with the correct arguments
        mock_parse_mgcat.assert_called_once_with(self.sample_xml, timestamp=True, sku=True, nombre=True, marca=True, categoria=True, cod_cat=True, costo=True, stock=True, iva=True, ean=True)


    @patch('precios_mg.precios_mg_helpers.parse_mgcat')
    def test_prices_format(self, mock_parse_mgcat):
        # Set up the mock return value
        mock_parse_mgcat.return_value = [ProductoMG()]

        products = mg_get_products(self.sample_xml, format="prices")

        # Assertions based on the expected behavior
        self.assertIsInstance(products, list)
        self.assertEqual(len(products), 1)
        self.assertTrue(all(isinstance(product, ProductoMG) for product in products))
        self.assertTrue(all(hasattr(product, attr) for product in products for attr in ["timestamp", "sku", "costo"]))

        # Ensure that parse_mgcat was called with the correct arguments
        mock_parse_mgcat.assert_called_once_with(self.sample_xml, timestamp=True, sku=True, costo=True)

    @patch('precios_mg.precios_mg_helpers.parse_mgcat')
    def test_stock_format(self, mock_parse_mgcat):
        # Set up the mock return value
        mock_parse_mgcat.return_value = [ProductoMG()]

        products = mg_get_products(self.sample_xml, format="stock")

        # Assertions based on the expected behavior
        self.assertIsInstance(products, list)
        self.assertEqual(len(products), 1)
        self.assertTrue(all(isinstance(product, ProductoMG) for product in products))
        self.assertTrue(all(hasattr(product, attr) for product in products for attr in ["timestamp", "sku", "stock"]))

        # Ensure that parse_mgcat was called with the correct arguments
        mock_parse_mgcat.assert_called_once_with(self.sample_xml, timestamp=True, sku=True, stock=True)


if __name__ == '__main__':
    unittest.main()