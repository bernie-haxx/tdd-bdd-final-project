# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_a_product(self):
        """
        It should read a product in the system.
        """
        # Instantiate product_factory
        product = ProductFactory()

        # Add logging message displaying the product
        logging.debug("Product : %s", product.serialize())

        # Setting product to None and AssertIsNotNone Check
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        # Fetch the product from the database
        found_product = Product.find(product.id)

        # Assert the contents in the product
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """
        It should update a product in the system
        """
        # Instantiate product_factory
        product = ProductFactory()

        # Logging message displaying the product
        logging.debug("Product : %s", product.serialize())

        # Setting product to None and AssertIsNotNone Check
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        # Logging to check for the desired property of product.id
        logging.debug("Product : %s", product.serialize())

        # Set description for update
        description = f"This is a description for {product.name}"
        product.description = description
        previous_id = product.id
        product.update()
        self.assertEqual(product.id, previous_id)
        self.assertEqual(product.description, description)

        # Fetch all the products from the database
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, previous_id)
        self.assertEqual(products[0].description, description)

    def test_delete_a_product(self):
        """
        It should delete a Product
        """
        # Create product factory object
        product = ProductFactory()
        product.create()

        # Assertion for a product object in the system
        self.assertEqual(len(Product.all()), 1)

        # Delete product object and make sure is not in the system
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """
        It should list all Products in the database
        """
        # Call all products in the DB
        products = Product.all()

        # Assert there are no products in the DB
        self.assertEqual(products, [])

        # Geenrate five products and add them to DB
        for __ in range(5):
            product = ProductFactory()
            product.create()

        # Fetch created product records and assert there in the DB
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """
        It should find a Product by Name
        """
        # Create a batch of 5 Product objects using the ProductFactory and save them
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        # Retrieve the name of the first product
        name = products[0].name

        # Count the number of occurrences of the product name in the list
        count = len([product for product in products if product.name == name])

        # Retrieve products from the database that have the specified name
        found = Product.find_by_name(name)

        # Assert if the count of the found products matches the expected count
        self.assertEqual(found.count(), count)

        # Assert that each product’s name matches the expected name
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """
        It should Find Products by Availability
        """
        # Create a batch of 10 Product objects using the ProductFactory and save them
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Retrieve the availability of the first product in the products list
        available = products[0].available

        # Count the number of occurrences of the product availability in the list
        count = len([product for product in products if product.available == available])

        # Retrieve products from the database that have the specified availability
        found = Product.find_by_availability(available)

        # Assert if the count of the found products matches the expected count
        self.assertEqual(found.count(), count)

        # Assert that each product's availability matches the expected availability
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """
        It should Find Products by Category
        """
        # Create a batch of 10 Product objects using the ProductFactory and save them
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Retrieve the category of the first product in the products list
        category = products[0].category

        # Count the number of occurrences of the product that have the same category in the list
        count = len([product for product in products if product.category == category])

        # Retrieve products from the database that have the specified category
        found = Product.find_by_category(category)

        # Assert if the count of the found products matches the expected count
        self.assertEqual(found.count(), count)

        # Assert that each product's category matches the expected category
        for product in found:
            self.assertEqual(product.category, category)

    def test_update_error_if_not_found(self):
        """
        Testing for update field not getting a product
        """
        product = ProductFactory()
        product.create()

        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_find_by_price(self):
        """
        It should Find Products by price
        """
        # Create a batch of 10 Product objects using the ProductFactory and save them
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Retrieve the price of the first product in the products list
        price = products[0].price

        # Count the number of occurrences of the product that have the same price in the list
        count = len([product for product in products if product.price == price])

        # Retrieve products from the database that have the specified price
        found = Product.find_by_price(price)

        # Assert if the count of the found products matches the expected count
        self.assertEqual(found.count(), count)

        # Assert that each product's category matches the expected price
        for product in found:
            self.assertEqual(product.price, price)

    def test_find_by_price_string(self):
        """
        If string data is added to the field
        """
        product = ProductFactory()
        product.create()

        string_price = str(product.price)
        found = Product.find_by_price(string_price)
        self.assertEqual(str(found[0].price), string_price)

    def test_deserialized_data_errors_for_available(self):
        """
        Cross Checking Errors from wrong serialized data in available field
        """
        product = ProductFactory()
        product.create()
        product_dict = product.serialize()

        # For available field error validations
        # int
        product_dict["available"] = 1
        self.assertRaises(DataValidationError, product.deserialize, product_dict)

        # Random String
        product_dict["available"] = "redwhine"
        self.assertRaises(DataValidationError, product.deserialize, product_dict)

    def test_deserialized_data_errors_for_category(self):
        """
        Cross Checking Errors from wrong serialized data in category field
        """
        product = ProductFactory()
        product.create()
        product_dict = product.serialize()

        # For category field error validations
        # Empty
        product_dict["category"] = ""
        self.assertRaises(DataValidationError, product.deserialize, product_dict)

        # Unknown category
        product_dict["category"] = "redddy"
        self.assertRaises(DataValidationError, product.deserialize, product_dict)

        # Unknown category
        product_dict["category"] = None
        self.assertRaises(DataValidationError, product.deserialize, product_dict)
