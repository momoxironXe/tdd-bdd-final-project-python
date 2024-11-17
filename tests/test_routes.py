    def test_get_product(self):
        """It should Get a single Product"""
        # get the id of a product
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

######################################################################
# READ A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """
    Retrieve a single Product

    This endpoint will return a Product based on it's id
    """
    app.logger.info("Request to Retrieve a product with id [%s]", product_id)

    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    app.logger.info("Returning product: %s", product.name)
    return product.serialize(), status.HTTP_200_OK

    def test_get_product_not_found(self):
        """It should not Get a Product thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_update_product(self):
        """It should Update an existing Product"""
        # create a product to update
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = response.get_json()
        new_product["description"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_product['id']}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["description"], "unknown")

######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """
    Update a Product

    This endpoint will update a Product based the body that is posted
    """
    app.logger.info("Request to Update a product with id [%s]", product_id)
    check_content_type("application/json")

    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    product.deserialize(request.get_json())
    product.id = product_id
    product.update()
    return product.serialize(), status.HTTP_200_OK

    def test_delete_product(self):
        """It should Delete a Product"""
        products = self._create_products(5)
        product_count = self.get_product_count()
        test_product = products[0]
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        new_count = self.get_product_count()
        self.assertEqual(new_count, product_count - 1)

######################################################################
# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """
    Delete a Product

    This endpoint will delete a Product based the id specified in the path
    """
    app.logger.info("Request to Delete a product with id [%s]", product_id)

    product = Product.find(product_id)
    if product:
        product.delete()

    return "", status.HTTP_204_NO_CONTENT

    def test_get_product_list(self):
        """It should Get a list of Products"""
        self._create_products(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

######################################################################
# LIST PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns a list of Products"""
    app.logger.info("Request to list Products...")

    products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("[%s] Products returned", len(results))
    return results, status.HTTP_200_OK

    def test_query_by_name(self):
        """It should Query Products by name"""
        products = self._create_products(5)
        test_name = products[0].name
        name_count = len([product for product in products if product.name == test_name])
        response = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["name"], test_name)

######################################################################
# LIST PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns a list of Products"""
    app.logger.info("Request to list Products...")

    products = []
    name = request.args.get("name")

    if name:
        app.logger.info("Find by name: %s", name)
        products = Product.find_by_name(name)
    else:
        app.logger.info("Find all")
        products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("[%s] Products returned", len(results))
    return results, status.HTTP_200_OK

    def test_query_by_category(self):
        """It should Query Products by category"""
        products = self._create_products(10)
        category = products[0].category
        found = [product for product in products if product.category == category]
        found_count = len(found)
        logging.debug("Found Products [%d] %s", found_count, found)

        # test for available
        response = self.client.get(BASE_URL, query_string=f"category={category.name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), found_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["category"], category.name)

######################################################################
# LIST PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns a list of Products"""
    app.logger.info("Request to list Products...")

    products = []
    name = request.args.get("name")
    category = request.args.get("category")

    if name:
        app.logger.info("Find by name: %s", name)
        products = Product.find_by_name(name)
    elif category:
        app.logger.info("Find by category: %s", category)
        # create enum from string
        category_value = getattr(Category, category.upper())
        products = Product.find_by_category(category_value)
    else:
        app.logger.info("Find all")
        products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("[%s] Products returned", len(results))
    return results, status.HTTP_200_OK

    def test_query_by_availability(self):
        """It should Query Products by availability"""
        products = self._create_products(10)
        available_products = [product for product in products if product.available is True]
        available_count = len(available_products)        
        # test for available
        response = self.client.get(
            BASE_URL, query_string="available=true"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), available_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["available"], True)

######################################################################
# LIST PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns a list of Products"""
    app.logger.info("Request to list Products...")

    products = []
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")

    if name:
        app.logger.info("Find by name: %s", name)
        products = Product.find_by_name(name)
    elif category:
        app.logger.info("Find by category: %s", category)
        # create enum from string
        category_value = getattr(Category, category.upper())
        products = Product.find_by_category(category_value)
    elif available:
        app.logger.info("Find by available: %s", available)
        # create bool from string
        available_value = available.lower() in ["true", "yes", "1"]
        products = Product.find_by_availability(available_value)
    else:
        app.logger.info("Find all")
        products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("[%s] Products returned", len(results))
    return results, status.HTTP_200_OK
