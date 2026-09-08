from idlelib.rpc import request_queue
from random import shuffle
import random
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
import time

from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import requests
import json
from pprint import pprint
from decouple import config
from openpyxl import Workbook
from openpyxl.styles import Font

from . import finik
from .models import WinxOrder

SALES_REPORT_URL = "https://app.pos-service.kg/proxy/?path=%2Freport%2F64abd976dac244c8d30a926c%2Fsales%2Fgroups-products%2F0%2F1000%2F&api=v3&timezone=21600"

TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID", default="")

WINX_PUZZLE_COUNT = 5

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


WINX_MAX_QUANTITY = 10


def _send_telegram(text):
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        print("Telegram is not configured, message:", text)
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=10,
        )
    except requests.RequestException as e:
        print("Telegram send failed:", e)


def _notify_order_paid(order):
    method_label = "Доставка" if order.method == WinxOrder.DELIVERY else "Самовывоз"
    lines = [
        "💳 Куплен QUES x WINX Secret Box!",
        f"ФИО: {order.full_name}",
        f"Телефон: {order.phone}",
        f"Количество: {order.quantity}",
        f"Сумма: {order.amount} сом",
        f"Получение: {method_label}",
    ]
    if order.method == WinxOrder.DELIVERY:
        lines.append(f"Адрес: {order.address}")
    lines.append(f"Скидка 5% (пазл): {'да' if order.discount_claimed else 'нет'}")
    _send_telegram("\n".join(lines))


def _mark_order_paid(order, payment_id=""):
    """Single entry point for confirming a Finik payment — called by
    the real webhook and the local test-mode fake gateway alike.
    Idempotent, so a retried webhook delivery is safe."""
    if order.status == WinxOrder.STATUS_PAID:
        return
    order.status = WinxOrder.STATUS_PAID
    order.payment_id = payment_id
    order.paid_at = datetime.now(timezone.utc)
    order.save()
    _notify_order_paid(order)


def _mark_order_failed(order):
    if order.status == WinxOrder.STATUS_PAID:
        return
    order.status = WinxOrder.STATUS_FAILED
    order.save(update_fields=["status"])


def winx_landing(request):
    if "winx_puzzle_index" not in request.session:
        request.session["winx_puzzle_index"] = random.randint(0, WINX_PUZZLE_COUNT - 1)

    context = {
        "puzzle_index": request.session["winx_puzzle_index"],
        "discount_claimed": request.session.get("winx_discount_claimed", False),
        "box_price": settings.WINX_BOX_PRICE_KGS,
    }
    return render(request, "winx.html", context)


@require_POST
def winx_claim_discount(request):
    already_claimed = request.session.get("winx_discount_claimed", False)
    request.session["winx_discount_claimed"] = True
    return JsonResponse({
        "ok": True,
        "already_claimed": already_claimed,
        "discount_percent": 5,
    })


@require_POST
def winx_submit_order(request):
    discount_claimed = request.session.get("winx_discount_claimed", False)
    if not discount_claimed:
        return JsonResponse({"ok": False, "error": "Сначала собери пазл, чтобы получить скидку"}, status=403)

    full_name = request.POST.get("full_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    method = request.POST.get("method", "").strip()
    address = request.POST.get("address", "").strip()

    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        quantity = 0
    if quantity < 1 or quantity > WINX_MAX_QUANTITY:
        return JsonResponse({"ok": False, "error": "Некорректное количество боксов"}, status=400)

    if not full_name or not phone or method not in ("delivery", "pickup"):
        return JsonResponse({"ok": False, "error": "Заполните все обязательные поля"}, status=400)
    if method == "delivery" and not address:
        return JsonResponse({"ok": False, "error": "Укажите точный адрес доставки"}, status=400)

    amount = Decimal(settings.WINX_BOX_PRICE_KGS) * quantity
    if discount_claimed:
        amount = (amount * Decimal("0.95")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    order = WinxOrder.objects.create(
        full_name=full_name,
        phone=phone,
        method=method,
        address=address if method == "delivery" else "",
        discount_claimed=discount_claimed,
        quantity=quantity,
        amount=amount,
    )

    try:
        redirect_url = finik.create_payment(order)
    except finik.FinikError as exc:
        return JsonResponse({"ok": False, "error": f"Не удалось создать платёж: {exc}"}, status=502)

    return JsonResponse({"ok": True, "redirect_url": redirect_url})


def winx_finik_return(request, token):
    """Where Finik redirects the buyer's browser after they pay. Just a
    landing page — the webhook below (not this) is the source of truth
    for whether the order is actually paid, so this may render slightly
    before that webhook has landed."""
    order = get_object_or_404(WinxOrder, qr_token=token)
    return render(request, "winx_payment_return.html", {"order": order})


@csrf_exempt
@require_POST
def winx_finik_webhook(request):
    """Server-to-server notification Finik sends once a payment
    succeeds (per their docs, only ever sent on success — there's no
    webhook call for a failed/abandoned payment)."""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)

    if not finik.verify_webhook(request, payload):
        return HttpResponse(status=401)

    status = str(payload.get("status", "")).lower()
    if status not in ("success", "succeeded"):
        return HttpResponse(status=200)

    payment_id = (payload.get("fields") or {}).get("paymentId")
    order = WinxOrder.objects.filter(qr_token=payment_id).first()
    if not order:
        return HttpResponse(status=200)

    _mark_order_paid(order, payment_id=payload.get("transactionId", ""))
    return HttpResponse(status=200)


def winx_fake_gateway(request, token):
    """Stand-in for Finik's hosted payment page. Only reachable while
    FINIK_TEST_MODE is on or real credentials aren't configured yet —
    lets the full purchase flow be tested end to end without a live
    Finik account."""
    order = get_object_or_404(WinxOrder, qr_token=token)

    if request.method == "POST":
        if request.POST.get("action") == "pay":
            _mark_order_paid(order, payment_id="TEST-" + str(order.qr_token)[:8])
        else:
            _mark_order_failed(order)
        return redirect("winx_finik_return", token=order.qr_token)

    return render(request, "winx_fake_gateway.html", {"order": order})
