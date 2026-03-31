from django.shortcuts import render

from django.http import HttpRequest,JsonResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.db import transaction
from decimal import Decimal
from .models import Client, Product, Order, OrderItem
from .forms import ProductForm,ClientForm
from django.db.models import Sum, Count, F, DecimalField,Q
from django.db.models.functions import Coalesce


CREDIT_WARNING_THRESHOLD = Decimal("0.9")

def home(request):
    return render(request, "arm/home.html")


def clients_list(request:HttpRequest):
    clients = Client.objects.all()
    return render(request, "arm/clients_list.html", {"clients": clients})

def client_search_ajax(request:HttpRequest):
    query_search=request.GET.get('q','')
    if query_search and len(query_search)>=2:
        clients =Client.objects.filter(
            Q(name__icontains=query_search)
        ).order_by('name')[:10]
        result=[]
        for c in clients:
            result.append({
                'id':c.id,
                'name':c.name,
                'total_purchases':float(c.total_purchases),
                'current_balance':float(c.current_balance),
                'credit_limit':float(c.credit_limit),
                'current_debt':float(c.current_debt),
                'credit_remainder':float(c.credit_remaining),
                'comment':c.comment
            })
        return JsonResponse({
            'success':True,
            'clients':result,
            'count':len(clients),
            'query':query_search
            })
    return JsonResponse({
            'success':True,
            'clients':[],
            'count':0,
            'query':query_search
            })
    

def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clients_list')
    else:
        form = ClientForm()
    return render(request, "arm/client_form.html", {"form": form})

def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('clients_list')
    else:
        form = ClientForm(instance=client)
    return render(request, "arm/client_form.html", {"form": form, "client": client})

def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        client.delete()
        return redirect('clients_list')
    return render(request, "arm/client_confirm_delete.html", {"client": client})

def products_list(request):
    products = Product.objects.all()
    return render(request, "arm/products_list.html", {"products": products})

def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products_list')
    else:
        form = ProductForm()
    return render(request, "arm/product_form.html", {"form": form})

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products_list')
    else:
        form = ProductForm(instance=product)
    return render(request, "arm/product_form.html", {"form": form, "product": product})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect('products_list')
    return render(request, "arm/product_delete.html", {"product": product})

from django.db.models import Sum, Count, F
from django.db.models.functions import Coalesce

def clients_orders_report(request):
    clients = (
        Client.objects
        .annotate(
            total_orders_sum=Sum('orders__total_amount', default=0),
            orders_count=Count('orders', distinct=True),
        )
    )

    clients_data = []
    for c in clients:
        product_names = (
            Product.objects
            .filter(orderitem__order__client=c)
            .distinct()
            .values_list('name', flat=True)
        )
        clients_data.append({
            "client": c,
            "total_orders_sum": c.total_orders_sum,
            "orders_count": c.orders_count,
            "product_names": ", ".join(product_names),
        })

    return render(request, "arm/clients_orders_report.html", {
        "clients_data": clients_data
    })

def orders_report(request):
    orders = Order.objects.all().select_related('client').prefetch_related(
        'items__product'
    ).order_by('-created_at')
    
    total_sum=Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    orders_data = []
    for order in orders:
        items = order.items.all()
        items_list = []

        for item in items:
            items_list.append({
                'name': item.product.name,
                'quantity': item.quantity, 
                'price': str(item.price),  
                'line_total': str(item.line_total)
            })
        payment_type_map = {
            'cash': 'Наличный расчет',
            'noncash': 'Безналичный расчет',
            'credit': 'Кредит',
            'barter': 'Бартер',
            'offset': 'Взаимозачет'
        }
        payment_type_display = payment_type_map.get(order.payment_type, order.payment_type)
        
        items_summary = []
        for item in items:
            items_summary.append(f"{item.product.name} ({item.quantity} шт.)")
        
        order_dict = {
            'client_name': order.client.name,
            'payment_type': payment_type_display,
            'payment_type_code': order.payment_type,
            'total_amount': float(order.total_amount),  
            'items_count': len(items_list),
            'items_list': items_list,
            'items_summary': '; '.join(items_summary)  
        }
        
        orders_data.append(order_dict)  
    return render(request, "arm/order_report.html", {
        "orders_data": orders_data,
        "total_sum":total_sum
    })


@transaction.atomic
def order_create(request):
    clients = Client.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        client_id = request.POST.get("client")
        payment_type = request.POST.get("payment_type")

        client = Client.objects.select_for_update().get(pk=client_id)

        
        if payment_type != "barter":
            items = []
            index = 0
            total = Decimal("0")
            
            while True:
                product_id = request.POST.get(f"item-{index}-product")
                qty_str = request.POST.get(f"item-{index}-qty")
                if not product_id:
                    break
                qty = Decimal(qty_str or "0")
                if qty <= 0:
                    index += 1
                    continue

                product = Product.objects.select_for_update().get(pk=product_id)
                price = product.price
                line_total = price * qty

                if qty > product.stock_qty:
                    return render(request, "arm/order_form.html", {
                        "clients": clients,
                        "products": products,
                        "error": f"Недостаточно товара {product.name} на складе",
                    })

                items.append((product, qty, price, line_total))
                total += line_total
                index += 1

            if not items:
                return render(request, "arm/order_form.html", {
                    "clients": clients,
                    "products": products,
                    "error": "Добавьте хотя бы одну строку с товаром",
                })

            order = Order.objects.create(client=client, payment_type=payment_type)
            
            for product, qty, price, line_total in items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=price,
                    line_total=line_total,
                )
                if payment_type in ("cash", "noncash", "credit"):
                    product.stock_qty -= qty
                elif payment_type == "offset":
                    product.stock_qty += qty
                product.save()

            order.total_amount = total
            order.save()

            
            if payment_type == "cash":
                client.total_purchases += total
            elif payment_type == "noncash":
                client.total_purchases += total
                client.current_balance -= total
            elif payment_type == "credit":
                to_use_from_balance = min(client.current_balance, total)
                remaining_to_credit = total - to_use_from_balance
                client.current_balance -= to_use_from_balance
                client.total_purchases += total
                client.current_debt += remaining_to_credit
                if client.current_debt > client.credit_limit:
                    return render(request, "arm/order_form.html", {
                        "clients": clients,
                        "products": products,
                        "error": "Превышен кредитный лимит клиента",
                    })
            elif payment_type == "offset":
                if total>client.current_debt:
                    return render(request, "arm/order_form.html", {
            "clients": clients,
            "products": products,
            "error": f"Сумма взаимозачета ({total}) превышает текущий долг клиента ({client.current_debt})",})
            client.current_debt -= total

            client.save()
            return redirect("order_create")

        
        else:
            
            out_items = []
            out_index = 0
            out_total = Decimal("0")
            
            while True:
                product_id = request.POST.get(f"barter-out-{out_index}-product")
                qty_str = request.POST.get(f"barter-out-{out_index}-qty")
                if not product_id:
                    break
                qty = Decimal(qty_str or "0")
                if qty <= 0:
                    out_index += 1
                    continue

                product = Product.objects.select_for_update().get(pk=product_id)
                price = product.price
                line_total = price * qty

                if qty > product.stock_qty:
                    return render(request, "arm/order_form.html", {
                        "clients": clients,
                        "products": products,
                        "error": f"Недостаточно товара {product.name} на складе для обмена",
                    })

                out_items.append((product, qty, price, line_total))
                out_total += line_total
                out_index += 1

            
            in_items = []
            in_index = 0
            in_total = Decimal("0")
            
            while True:
                product_id = request.POST.get(f"barter-in-{in_index}-product")
                qty_str = request.POST.get(f"barter-in-{in_index}-qty")
                if not product_id:
                    break
                qty = Decimal(qty_str or "0")
                if qty <= 0:
                    in_index += 1
                    continue

                product = Product.objects.select_for_update().get(pk=product_id)
                price = product.price
                line_total = price * qty

                in_items.append((product, qty, price, line_total))
                in_total += line_total
                in_index += 1

            
            if not out_items or not in_items:
                return render(request, "arm/order_form.html", {
                    "clients": clients,
                    "products": products,
                    "error": "Для бартера нужно указать как отдаваемые, так и получаемые товары",
                })

            if out_total != in_total:
                return render(request, "arm/order_form.html", {
                    "clients": clients,
                    "products": products,
                    "error": f"Сумма отдаваемых товаров ({out_total}) не равна сумме получаемых ({in_total})",
                })

            
            order = Order.objects.create(client=client, payment_type=payment_type, total_amount=out_total)
            
            
            for product, qty, price, line_total in out_items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=-qty,
                    price=price,
                    line_total=line_total,
                )
                product.stock_qty -= qty
                product.save()
            
            
            for product, qty, price, line_total in in_items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=price,
                    line_total=line_total,
                )
                product.stock_qty += qty
                product.save()

            return redirect("order_create")

    return render(request, "arm/order_form.html", {
        "clients": clients,
        "products": products,
    })
