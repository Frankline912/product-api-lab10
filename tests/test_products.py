def get_auth_headers(client, test_user):
    client.post("/register", json=test_user)

    response = client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_create_product(client, test_user):
    headers = get_auth_headers(client, test_user)

    product = {
        "name": "Laptop",
        "description": "Test laptop",
        "price": 1000.0,
        "stock": 10
    }

    response = client.post(
        "/products",
        json=product,
        headers=headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Laptop"
    assert data["price"] == 1000.0
    assert data["stock"] == 10


def test_list_products(client, test_user):
    headers = get_auth_headers(client, test_user)

    product = {
        "name": "Mouse",
        "description": "Wireless mouse",
        "price": 25.0,
        "stock": 20
    }

    client.post(
        "/products",
        json=product,
        headers=headers
    )

    response = client.get(
        "/products",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert data[0]["name"] == "Mouse"


def test_get_product(client, test_user):
    headers = get_auth_headers(client, test_user)

    product = {
        "name": "Keyboard",
        "description": "USB keyboard",
        "price": 50.0,
        "stock": 15
    }

    create_response = client.post(
        "/products",
        json=product,
        headers=headers
    )

    product_id = create_response.json()["id"]

    response = client.get(
        f"/products/{product_id}",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Keyboard"


def test_update_product(client, test_user):
    headers = get_auth_headers(client, test_user)

    product = {
        "name": "Old Name",
        "description": "Old description",
        "price": 100.0,
        "stock": 5
    }

    create_response = client.post(
        "/products",
        json=product,
        headers=headers
    )

    product_id = create_response.json()["id"]

    response = client.patch(
        f"/products/{product_id}",
        json={
            "name": "Updated Name",
            "price": 150.0
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Name"
    assert data["price"] == 150.0


def test_delete_product(client, test_user):
    headers = get_auth_headers(client, test_user)

    product = {
        "name": "Delete Me",
        "description": "Product to delete",
        "price": 20.0,
        "stock": 5
    }

    create_response = client.post(
        "/products",
        json=product,
        headers=headers
    )

    product_id = create_response.json()["id"]

    response = client.delete(
        f"/products/{product_id}",
        headers=headers
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/products/{product_id}",
        headers=headers
    )

    assert get_response.status_code == 404


def test_unauthorized_access(client):
    response = client.get("/products")

    assert response.status_code == 401