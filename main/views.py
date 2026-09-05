from idlelib.rpc import request_queue
from random import shuffle
from datetime import datetime, timezone, timedelta
import time

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render
import requests
import json
from pprint import pprint
from decouple import config
from openpyxl import Workbook
from openpyxl.styles import Font

SALES_REPORT_URL = "https://app.pos-service.kg/proxy/?path=%2Freport%2F64abd976dac244c8d30a926c%2Fsales%2Fgroups-products%2F0%2F1000%2F&api=v3&timezone=21600"

SALES_REPORT_HEADERS = [
    "Наименование", "Штрих-код", "Артикул", "Выручка", "Прибыль",
    "Себест. продаж", "Продажи", "Продано", "Рентабельность", "Маржинальность",
]

BISHKEK_TZ = timezone(timedelta(hours=6))  # matches api=v3&timezone=21600


def products_list(request):
    try:
        with open('db.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        update_data(request, test=True)
    with open('db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open('categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)


    if request.GET.get('id_group', None):
        category = [i for i in categories if i['id_group'] == request.GET.get('id_group', None)]
        data = [i for i in data if i['id_group'] == request.GET.get('id_group', None)]

    else:
        category = [i for i in categories if i['id_group'] == 0]

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
        'categories': category
    }
    if request.GET.get('id_group', None):
        context['params'] = request.GET.get('id_group', None)
        print(context['params'])
    # pprint(products.object_list)
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
    headers = {
        "Accept": "application/json, text/plain, */*",
        "cloudshop-timezone": "21600",
        "Referer": "https://app.pos-service.kg/",
    }

    response = requests.get(url, cookies=cookies, headers=headers)

    if response.status_code == 200:
        # print("Ответ получен успешно!")
        data = response.json()
        dastan = []
        categories = []
        # print(len(data['data']))
        for i in range(len(data['data'])):
            if data["data"][i]['type'] != 'group':

                a =  {
                    (k[1:] if k.startswith('_') else k): v
                    for k, v in data["data"][i].items()
                }
                dastan.append(a)
            else:
                a = {
                    (k[1:] if k.startswith('_') else k): v
                    for k, v in data["data"][i].items()
                }
                categories.append(a)
        with open('db.json', 'w', encoding='utf-8') as f:
            json.dump(dastan[::-1], f, ensure_ascii=False, indent=4)
        with open('categories.json', 'w', encoding='utf-8') as f:
            json.dump(categories[::-1], f, ensure_ascii=False, indent=4)
        if not test:
            return HttpResponse("ok")
    else:
        print(response.status_code)

        if not test:
            return HttpResponse("error")


def _pos_cookies():
    return {
        "connect.sid": config("CONNECT_ID"),
        "company_id": config("COMPANY_ID"),
    }


def _day_bounds_to_timestamps(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    start_ts = int(start_date.replace(tzinfo=BISHKEK_TZ).timestamp())
    end_ts = int(end_date.replace(hour=23, minute=59, second=59, tzinfo=BISHKEK_TZ).timestamp())
    return start_ts, end_ts


def fetch_sales_report(start_date_str, end_date_str):
    start_ts, end_ts = _day_bounds_to_timestamps(start_date_str, end_date_str)
    payload = {"no_group": True, "start": start_ts, "end": end_ts}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "cloudshop-timezone": "21600",
        "Origin": "https://app.pos-service.kg",
        "Referer": "https://app.pos-service.kg/card/reports/product",
    }
    response = requests.post(SALES_REPORT_URL, cookies=_pos_cookies(), json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if not data.get("status"):
        raise ValueError(data.get("error") or "Не удалось получить отчет")
    return data.get("data", [])


def _split_rows_and_totals(raw_rows):
    rows, totals = [], None
    for item in raw_rows:
        if item.get("_id") == "total/avg":
            totals = item
            continue
        rows.append(item)
    return rows, totals


def _format_row(item):
    product = item.get("product") or {}
    return {
        "name": product.get("name") or "-",
        "barcode": product.get("barcode") or "",
        "sku": product.get("sku") or "",
        "revenue": item.get("revenue", 0),
        "profit": item.get("profit", 0),
        "cost": item.get("cost", 0),
        "sales": item.get("sales", 0),
        "count": item.get("count", 0),
        "rent": round(item.get("rent", 0) * 100, 1),
        "margin": round(item.get("margin", 0) * 100, 1),
    }


def _default_date_range():
    today = datetime.now().date()
    return today.replace(day=1).isoformat(), today.isoformat()


def _iter_dates(start_date_str, end_date_str):
    current = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    while current <= end:
        yield current
        current += timedelta(days=1)


def _write_report_sheet(ws, raw_rows, raw_totals, day_label=None):
    if day_label:
        ws.append([day_label])
        ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=12)

    ws.append(SALES_REPORT_HEADERS)
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True)

    for item in raw_rows:
        row = _format_row(item)
        ws.append([
            row["name"], row["barcode"], row["sku"], row["revenue"], row["profit"],
            row["cost"], row["sales"], row["count"], row["rent"], row["margin"],
        ])

    if raw_totals:
        row = _format_row(raw_totals)
        ws.append([
            "ИТОГО / СРЕДНЕЕ", "", "", row["revenue"], row["profit"],
            row["cost"], row["sales"], row["count"], row["rent"], row["margin"],
        ])
        for cell in ws[ws.max_row]:
            cell.font = Font(bold=True)


def sales_report(request):
    default_start, default_end = _default_date_range()
    start_date = request.GET.get("start_date") or default_start
    end_date = request.GET.get("end_date") or default_end

    rows, totals, error = [], None, None
    try:
        raw_rows, raw_totals = _split_rows_and_totals(fetch_sales_report(start_date, end_date))
        rows = [_format_row(item) for item in raw_rows]
        totals = _format_row(raw_totals) if raw_totals else None
    except Exception as e:
        error = str(e)
        print(error)

    context = {
        "rows": rows,
        "totals": totals,
        "start_date": start_date,
        "end_date": end_date,
        "error": error,
    }
    return render(request, "salesReport.html", context)


def sales_report_export(request):
    default_start, default_end = _default_date_range()
    start_date = request.GET.get("start_date") or default_start
    end_date = request.GET.get("end_date") or default_end

    wb = Workbook()
    ws = wb.active
    ws.title = "Продажи по товарам"

    try:
        if start_date == end_date:
            raw_rows, raw_totals = _split_rows_and_totals(fetch_sales_report(start_date, end_date))
            _write_report_sheet(ws, raw_rows, raw_totals)
        else:
            days = list(_iter_dates(start_date, end_date))
            for i, day in enumerate(days):
                day_str = day.isoformat()
                raw_rows, raw_totals = _split_rows_and_totals(fetch_sales_report(day_str, day_str))
                _write_report_sheet(ws, raw_rows, raw_totals, day_label=day.strftime("%d.%m.%Y"))
                ws.append([])
                if i < len(days) - 1:
                    time.sleep(0.5)
    except Exception as e:
        return HttpResponse(f"Ошибка получения отчета: {e}", status=502)

    for col_cells in ws.columns:
        width = max((len(str(c.value)) for c in col_cells if c.value is not None), default=10)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(width + 2, 10), 40)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="sales_report_{start_date}_{end_date}.xlsx"'
    wb.save(response)
    return response
