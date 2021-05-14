# 1) Ввод данных (на потом, ввод будет с сайта)
# 2) Поиск конференций по теме
# 3) Применение фильтра для дат
# 4) Составления для каждой конференции словаря:
# Конференция, город, цена на авиабилет, цена на поезд, цена на проживание, код города этой конференции(можно
# расширять словарь, содержащий инфу о конференциях
# 5) Отсеять конференции, не подходящие по бюджету
# 6) Получить массив словарей с необходимой информацие
# 7) Далее зависит от интерфейса, пока оставляем

"""Алгоритм первого шага
Доработать:
1) Сделать фильтр цен (есть)
2) Добавить работу с бд
3) Доработать под изменения в остальных программах (есть)"""

from findconf.backend import get_city_code, conf_pars, train_pars, fly_price_info, hotel_api as h
import time
from findconf.models import *
from findconf.backend.hotel_api import strtodate
from findconf.backend.hotel_api import date_str_to_cal

# True - входит в бюджет, False - нет
def price_filtr(hotel_price, budget):
    if budget == -1:
        return True
    else:
        budget = int(budget)
    return hotel_price < budget


# 1. Пользователь выбирает тематику
# Допустим пользователь выбрал тематикой математику. Также допустим, что человек живет в Москве.
def get_res(Country, city, theme, keywords, money_do, data_p_s, data_p_e):
    # 1. Анализ въодных данных
    t1 = time.time()
    city = get_city(city)
    if money_do == '':
        money_do = -1
    if data_p_e == '':
        data_p_s = -1
    if data_p_e == '':
        data_p_e = -1
    # 2. Поиск всех конференций по тематике
    t1 = time.time()
    s_conf = conf_pars.Conf_parser(data_p_s, data_p_e, keywords, theme)
    s_conf = s_conf.getRes()
    # Получаем код родного города
    home_city_code = get_city_code.get_IATA_code(city)
    home_city_code = home_city_code.get_res()
    print(f"1. {time.time() - t1}")
    # 3.2 Для каждой конференции считается цена билета на самолет/проживание
    t1 = time.time()
    for j in s_conf:
        # Получаем код города
        city_code = get_city_code.get_IATA_code(j["city"])
        city_code = city_code.get_res()
        j["code"] = city_code
        if j["code"] == -1:
            j["train"] = -1
            j["plane"] = -1
            j["hotel"] = -1
        elif j["code"] == home_city_code:
            j["train"] = -2
            j["plane"] = -2
            j["hotel"] = -2
        else:
            tab = table_avia_sr(home_city_code, j["code"], date_str_to_cal(strtodate(j["date_start"]), -1), date_str_to_cal(strtodate(j["date_end"]), 1))
            if tab == -1:
                plane_price = fly_price_info.fly_price_info(home_city_code, j["code"], j["date_start"], j["date_end"])
                j["plane"] = plane_price.get_res()
            else:
                j["plane"] = tab
            tab = table_hotel_sr(j["code"], date_str_to_cal(strtodate(j["date_start"]), -1), date_str_to_cal(strtodate(j["date_start"]), 1))
            if tab == -1:
                hotel_price = h.hotel_api(j["code"], j["date_start"], j["date_end"])
                j["hotel"] = hotel_price.get_res()
            else:
                j["hotel"] = tab
            if not price_filtr(j["hotel"], money_do):
                s_conf.remove(j)
                continue
    print(f"2. {time.time() - t1}")
    t1 = time.time()
    for i in s_conf:
        if i["train"] == -1 or i["code"] == home_city_code:
            continue
        info = table_find_sr(train_pars.transliteration2(city), train_pars.transliteration2(i["city"]),
                             date_str_to_cal(strtodate(j["date_start"]), -1), date_str_to_cal(strtodate(j["date_start"]), 1))
        if info != 0:
            i["train"] = info
        else:
            train = train_pars.train_parse(city, i["city"], i["date_start"], i["date_end"])
            train_price = train.get_aver()
            i["train"] = train_price
    print(f"3. {time.time() - t1}")
    return s_conf

def table_avia_sr(city_iz, city_v, date_start, date_finish):
    a = avia_info.objects.filter(city_iz=city_iz, city_v=city_v, date_start=date_start,
                                 date_finish=date_finish)
    for i in a:
        return i.price
    return -1


def table_hotel_sr(city, date_start, date_finish):
    a = hotel_info.objects.filter(city=city, date_start=date_start, date_finish=date_finish)
    for i in a:
        return i.price
    return -1


def table_find_sr(city_iz, city_v, date_iz, date_v):
    """Поиск по базе данных о средних ценах на поезда и выгрузка, возвращает массив словарей значений"""
    a = train_sr.objects.filter(city_iz=city_iz, city_v=city_v, date_iz=date_iz, date_v=date_v)
    d = {}
    for i in a:
        d["Плацкарт"] = i.price_1
        d["Купе"] = i.price_2
        d["СВ"] = i.price_3
        return d
    return 0


def get_city(city_code):
    a = city_info.objects.filter(city_id=int(city_code))
    return a[0].city_name



# def table_find(city_iz, city_v, date_iz, date_v):
#     """Поиск по базе данных о поездах"""
#     a = train_inf.objects.filter(city_iz=city_iz, city_v=city_v, date_iz=date_iz, date_v=date_v)
#     mas = []
#     d = {}
#     for i in a:
#         d[""]
#         d["Плацкарт"] = i.price_1
#         d["Купе"] = i.price_2
#         d["СВ"] = i.price_3
#         mas.append(d)
#     return d

