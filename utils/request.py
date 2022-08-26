import json
import requests
from config_data import config
from datetime import date, timedelta

base_url = 'https://hotels4.p.rapidapi.com'
headers = {
    'x-rapidapi-key': config.RAPID_API_KEY,
    'x-rapidapi-host': "hotels4.p.rapidapi.com"
}


def locations_search(query: str, locale: str = 'ru_RU', currency: str = 'USD'):
    """Функция производит поиск локаций по заданной строке"""
    querystring = {'query': query, 'locale': locale, 'currency': currency}
    response = requests.request('GET', base_url + '/locations/v2/search', headers=headers, params=querystring)
    response_dict = json.loads(response.text)
    if bool(response.text):
        suggestions = {entity['name']: int(entity['destinationId'])
                       for group in response_dict['suggestions'] if group['group'] == 'CITY_GROUP'
                       for entity in group['entities']
                       }
        return suggestions
    return False


def hotel_list(searching_params: dict):
    """Функция производит поиск отелей по заданным параметрам"""
    querystring = {
        'destinationId': searching_params['id'],
        'pageNumber': searching_params['page'],
        'pageSize': searching_params['page_size'],
        'checkIn': searching_params['arrival'].isoformat(),
        'checkOut': searching_params['departure'].isoformat(),
        'adults1': 1,
        'sortOrder': searching_params['sort_order'],
        'locale': 'ru_RU',
    }
    if searching_params['sort_order'] == 'BEST_SELLER':
        querystring['priceMin'] = searching_params['min_price']
        querystring['priceMax'] = searching_params['max_price']
        querystring['pageSize'] = 25
    response = requests.request('GET', base_url + '/properties/list', headers=headers, params=querystring)
    hotels = []
    response_dict = json.loads(response.text)
    for hotel in response_dict['data']['body']['searchResults']['results']:
        hotels.append(
            {
                'id': hotel['id'],
                'name': hotel['name'],
                'address': hotel.get('address', {}).get('streetAddress', 'Адрес не указан'),
                'distance': hotel.get('landmarks', [{}])[0].get('distance', "Расстояние до центра не указано"),
                'price': hotel.get('ratePlan', {}).get('price', {}).get('current', 'Цена не указана'),
                'exact_price': hotel.get('ratePlan', {}).get('price', {}).get('exactCurrent', 0)
             }
        )
    return hotels


def get_photos_urls(hotel_id):
    """Функция возвращает список ссылок на фотографии отеля с заданным id"""
    response = requests.request("GET", base_url+'/properties/get-hotel-photos',
                                headers=headers, params={'id': hotel_id})
    if not response.text:
        return False
    response_dict = json.loads(response.text)
    photo_urls = [image['baseUrl'].format(
        size=image['sizes'][0]['suffix'])
        for image in response_dict['hotelImages']]
    return photo_urls
