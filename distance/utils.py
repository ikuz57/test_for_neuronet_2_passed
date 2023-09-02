from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points


def is_inside_mkad(point: Point, mkad_poly: Polygon) -> bool:
    """
    Проверяет, находится ли точка внутри МКАД.

    :param point: Объект точки Shapely Point.
    :param mkad_poly: Объект точки Shapely Polygon.
    :return: True, если точка находится внутри МКАД, иначе False.
    """
    return point.within(mkad_poly)


def calculate_distance_to_mkad(point: Point, mkad_poly: Polygon) -> int:
    """
    Вычисляет расстояние от точки до МКАД.

    :param point: Объект точки Shapely Point.
    :param mkad_poly: Объект точки Shapely Polygon.
    :return: Расстояние в километрах до МКАД.
    """
    # Можно сделать нахождение расстояния по дорогам через
    # яндекс API Маршрутизатора, но такого в задании не было :)

    # Находим ближайшую точку на МКАД к данной точке
    nearest_point, _ = list(nearest_points(mkad_poly, point))

    # Извлекаем координаты точек
    x_point, y_point = point.coords[0]
    x_nearest_point, y_nearest_point = nearest_point.coords[0]

    # Вычисляем расстояние между точками с использованием geodesic
    distance_km = geodesic(
        (x_nearest_point, y_nearest_point), (x_point, y_point)
    ).kilometers

    # так показалось лучше
    return int(distance_km)
