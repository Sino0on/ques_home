from idlelib.rpc import request_queue
from random import shuffle

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render
import requests
import json
from pprint import pprint
from decouple import config


def products_list(request):
    try:
        with open('db.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        update_data(request, test=True)
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Пагинация
    page = request.GET.get('page', 1)  # Получаем номер страницы, по умолчанию 1
    paginator = Paginator(data, 12)  # Показываем по 10 элементов на страницу

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    current_page = products.number
    total_pages = paginator.num_pages
    # 🔢 Логика кастомной пагинации (макс. 6 страниц вокруг текущей)
    max_visible = 4
    half = max_visible // 2

    if total_pages <= max_visible:
        custom_page_range = range(1, total_pages + 1)
    else:
        start = max(current_page - half, 1)
        end = start + max_visible - 1

        if end > total_pages:
            end = total_pages
            start = end - max_visible + 1

        custom_page_range = range(start, end + 1)

    context = {
        "products": products.object_list,
        "paginator": paginator,
        "page_obj": products,
        "is_paginated": products.has_other_pages(),
        "custom_page_range": custom_page_range,
    }
    pprint(products.object_list)
    return render(request, 'index.html', context)


def product_detail(request, pk):
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    shuffle(data)
    for i in data:
        if i['id'] == pk:
            return render(request, 'productDetail.html', {'product': i, "products": data[:4]})
    return HttpResponse('Error')


def update_data(request, test=None):


    # URL для запроса
    url = "https://app.pos-service.kg/proxy/?path=%2Fdata%2F64abd976dac244c8d30a926c%2Fcatalog%2F%3Flimit%3D1000%26offset%3D0&api=v3&timezone=21600"

    # Заголовок с cookies
    cookies = {
        "connect.sid": config("CONNECT_ID"),
        "company_id": config("COMPANY_ID"),
    }

    response = requests.get(url, cookies=cookies)

    if response.status_code == 200:
        # print("Ответ получен успешно!")
        data = response.json()
        dastan = []
        print(len(data['data']))
        for i in range(len(data['data'])):
            if data["data"][i]['type'] != 'group':

                a =  {
                    (k[1:] if k.startswith('_') else k): v
                    for k, v in data["data"][i].items()
                }
                dastan.append(a)
        with open('db.json', 'w', encoding='utf-8') as f:
            json.dump(dastan[::-1], f, ensure_ascii=False, indent=4)
        if not test:
            return HttpResponse("ok")
    else:
        if not test:
            return HttpResponse("error")
