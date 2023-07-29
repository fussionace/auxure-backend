import requests


ENDPOINT = "http://127.0.0.1:8000/api/v1/"


# Re-usable Helper Functions
def create_category(payload):
    return requests.post(ENDPOINT + "categories/", json=payload)

def update_category(category_id, payload):
    return requests.put(ENDPOINT + f"categories/{category_id}/", json=payload)

def delete_category(category_id):
    return requests.delete(ENDPOINT + f"categories/{category_id}/")

def get_category(category_id):
    return requests.get(ENDPOINT + f"categories/{category_id}/")

def category_payload():
    payload = {
        "title": "Fiction",
        "gender": "M",
        "slug": "ZixpEXt2tnkj"
    }
    return payload

# End of helper functions


# Test the root endpoint
def test_can_call_endpoint():
    response = requests.get(ENDPOINT)
    assert response.status_code == 200


#  pytest -v -s runs the test and all the print statements

# PERFUME ENDPOINTS TESTS
# GET PERFUMES
def test_can_get_perfumes():
    response = requests.get(ENDPOINT + "perfumes/")
    assert response.status_code == 200 



# CATEGORY ENDPOINTS TESTS
# GET CATEGORIES
def test_can_get_category():
    response = requests.get(ENDPOINT + "categories/")
    assert response.status_code == 200  


# POST CATEGORIES
def test_can_create_category():

    payload = category_payload()
    
    create_category_response = create_category(payload)
    assert create_category_response.status_code == 201  

    data = create_category_response.json()

    category_id = data['category_id']
    get_category_response = get_category(category_id)

    assert get_category_response.status_code == 200
    get_category_data = get_category_response.json()
    assert get_category_data['title'] == payload['title']
    assert get_category_data['slug'] == payload['slug']
    # print(get_category_data['category_id'])


def test_can_update_category():
    payload = category_payload()
    # Creates the category
    create_category_response = create_category(payload)
    assert create_category_response.status_code == 201 # Check if it was created
    category_id = create_category_response.json()['category_id']
    # print(category_id)

    new_payload = {
        "category_id": category_id,
        "title": "Non Fiction",
        "gender": "M",
    }

    # Updates the category
    update_category_response = update_category(category_id, new_payload)
    assert update_category_response.status_code == 200

    get_category_response = get_category(category_id)
    assert get_category_response.status_code == 200
    get_category_data = get_category_response.json()
    # Tests if the category was updated
    assert get_category_data['title'] == new_payload['title']
    assert get_category_data['gender'] == new_payload['gender'] 


def test_can_delete_category():
    payload = category_payload()
    # Create a category
    create_category_response = create_category(payload)
    assert create_category_response.status_code == 201 # Check if it was created
    category_id = create_category_response.json()['category_id']

    # Delete the category
    delete_category_response = delete_category(category_id)
    print(delete_category_response.status_code) # Checking the expected status code
    assert delete_category_response.status_code == 204

    # Check if the category was deleted
    get_category_response = get_category(category_id)
    assert get_category_response.status_code == 404

