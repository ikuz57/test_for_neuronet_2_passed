import pytest
import requests
from flask import Flask

from ..distance import distance


@pytest.fixture
def client():
    """
    Фикстура для создания тестового клиента Flask-приложения.
    """
    app = Flask(__name__)
    app.register_blueprint(distance, url_prefix="/distance")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_missing_address(client):
    """
    Тест на отсутствие адреса в запросе (нет поля "address").
    Проверяет, что при отправке POST-запроса без поля "address"
    возвращается ошибка с кодом состояния 400 и соответствующее сообщение.
    """
    response = client.post("/distance/calculate", json={})

    # Проверяем, что код состояния равен 400 и есть ожидаемое сообщение
    assert response.status_code == 400
    assert "Address is missing in the request" in response.data.decode()


def test_inside_mkad(client):
    """
    Тест на адрес, который находится внутри МКАД.
    Проверяет, что при отправке POST-запроса с адресом, который находится
    внутри МКАД, возвращается JSON-ответ с кодом состояния 200 и сообщением
    о том, что адрес находится внутри МКАД.
    """
    response = client.post(
        "/distance/calculate", json={"address": "ул. Тверская, 1, Москва"}
    )

    # Проверяем, что код состояния равен 200 и расстояние равно 0 км
    assert response.status_code == 200
    assert "answer" in response.get_json()
    assert response.get_json()["answer"] == "Address within Moscow Ring Road"


def test_outside_mkad(client):
    """
    Тест на адрес за пределами МКАД.
    Проверяет, что при отправке POST-запроса с адресом, который находится
    за пределами МКАД, возвращается JSON-ответ с кодом состояния 200,
    сообщением о том, что адрес не находится внутри МКАД, и расстоянием,
    которое корректно вычислено.
    """
    response = client.post(
        "/distance/calculate",
        json={
            "address": "Центральная улица, 57, деревня Глухово, городской "
            "округ Красногорск"
        },
    )

    # Проверяем, что код состояния равен 200 и расстояние корректно вычислено
    assert response.status_code == 200
    assert "answer" in response.get_json()
    assert "distance" in response.get_json()
    assert response.get_json()[
        "answer"] == "Address not within Moscow Ring Road"
    assert response.get_json()["distance"] == 13


def test_invalid_address(client):
    """
    Тест на некорректный адрес.
    Проверяет, что при отправке POST-запроса с некорректным адресом,
    который не может быть распознан или отсутствует в ответе Yandex Геокодера,
    возвращается JSON-ответ с кодом состояния 500 и сообщением о невозможности
    получить данные о геолокации.
    """
    response = client.post(
        "/distance/calculate", json={"address": "некорректный_адрес"}
    )
    assert response.status_code == 500
    assert "answer" in response.get_json()
    assert (
        response.get_json()["answer"]
        == "Unable to fetch geolocation data from Yandex API"
    )


def test_missing_blueprint_route(client):
    """
    Тест на запрос без указания Blueprint маршрута.
    Проверяет, что при отправке GET-запроса на несуществующий маршрут,
    приложение должно вернуть код состояния 404.
    """
    response = client.get("/nonexistent_route")
    assert response.status_code == 404


def test_unavailable_geocoder_api(client, monkeypatch):
    """
    Тест на недоступность Yandex API Геокодера.
    Проверяет, что приложение корректно обрабатывает ситуацию, когда
    Yandex API Геокодера недоступен (замокан запросы к API).
    Ожидаемый результат: Приложение должно вернуть код состояния 500 и
    сообщение о невозможности получить данные о геолокации из-за
    недоступности API.
    """

    def mock_requests_get(*args, **kwargs):
        raise requests.exceptions.RequestException

    monkeypatch.setattr("requests.get", mock_requests_get)

    response = client.post(
        "/distance/calculate", json={"address": "ул. Тверская, 1, Москва"}
    )
    assert response.status_code == 500
    assert "answer" in response.get_json()
    assert (
        response.get_json()["answer"]
        == "Unable to fetch geolocation data from Yandex API"
    )


def test_correct_write_log(client):
    """ """
    response = client.post(
        "/distance/calculate",
        json={
            "address": "Центральная улица, 57, деревня Глухово, городской "
            "округ Красногорск"
        },
    )

    # Проверяем, что код состояния равен 200 и расстояние корректно вычислено
    assert response.status_code == 200
    assert "answer" in response.get_json()
    assert "distance" in response.get_json()
    assert response.get_json()[
        "answer"] == "Address not within Moscow Ring Road"
    assert response.get_json()["distance"] > 0
