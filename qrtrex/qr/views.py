from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.urls import reverse
from .models import Restaurant,MenuItem,Menu,UserMembership,Payment,Rating,Offer,LiquorTypes,Enquiry
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.utils.timezone import now
import json
import base64
import qrcode
import io
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from django.db.models import Prefetch
import logging
import requests
import uuid
from .utils import generate_qr_image_with_logo
from django.views.decorators.http import require_GET
from .documents import MenuItemDocument
from django.db import models
from django.views.decorators.http import require_GET
from django.db import transaction
from razorpay import utility
from razorpay.errors import BadRequestError, ServerError, GatewayError


MEMBERSHIP_PRICING = {
    'monthly': {'amount': 99900, 'duration': 1},        
    'semi-annual': {'amount': 539400, 'duration': 6},   
    'annual': {'amount': 958800, 'duration': 12},       
}


def demo(request):
    return render(request,'qr/createQr.html')

def cart(request,id):
    
    restaurant = get_object_or_404(Restaurant,restaurant_id = id)
    return render(request,'qr/cart.html',{'restaurant':restaurant})

def get_restaurant_details(user):

    restaurant = Restaurant.objects.select_related('user').get(user=user)
    menus = Menu.objects.filter(restaurant=restaurant).prefetch_related('items')
    menuItems = MenuItem.objects.select_related('restaurant', 'menu').filter(restaurant=restaurant)
    payment = Payment.objects.select_related('user').filter(user=user)
    ratings = Rating.objects.select_related('restaurant').filter(restaurant=restaurant)
    membership = UserMembership.objects.select_related('restaurant').get(restaurant=restaurant)

    context = {
        'user':user,
        'restaurant':restaurant,
        'menus':menus,
        'menuItems':menuItems,
        'payments':payment,
        'ratings':ratings,
        'membership':membership
    }
    return context








def homepage(request):
    return render(request,'qr/homepage.html')

def qr_home(request,id,table):
    # slug = restaurant
    # restaurant_name = slug.replace('-', ' ')

    # Find the restaurant
    restaurant = get_object_or_404(Restaurant, restaurant_id=id)
    menus = Menu.objects.filter(restaurant=restaurant).prefetch_related('items')
    liquor = LiquorTypes.objects.filter(restaurant=restaurant).prefetch_related('liquorItems')
    context = {
        # 'slug':slug,
        'id':id,
        'restaurant': restaurant,
        'table_number': table,
        'menus':menus,
        'liquor':liquor
    }

    return render(request, 'qr/qr_home.html', context)

def qr_liquor(request,id,table):
    # slug = restaurant
    # restaurant_name = slug.replace('-', ' ')

    # Find the restaurant
    restaurant = get_object_or_404(Restaurant, restaurant_id=id)
    liquor = LiquorTypes.objects.filter(restaurant=restaurant).prefetch_related('liquorItems')
    context = {
        # 'slug':slug,
        'id':id,
        'restaurant': restaurant,
        'table_number': table,
        'liquor':liquor
    }

    return render(request, 'qr/qr-liquor.html', context)

def qr_menu(request,id,table):
    # restaurant_name = restaurant.replace('-', ' ')
    restaurant = get_object_or_404(Restaurant, restaurant_id=id)
    menus = Menu.objects.filter(restaurant=restaurant).prefetch_related('items')
    current_date = timezone.now().date()
    offers = Offer.objects.filter(restaurant=restaurant,
    end_date__lt=timezone.now().date(),
    is_active=True
    )
    context = {
        'id':id,
        'restaurant': restaurant,
        'table_number': table,
        'menus':menus,
        'offers':offers
    }
    return render(request, 'qr/qr_menu.html', context)



def register(request):
    if request.method == 'POST':
        # Get data from the POST request
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if not fname or not lname or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            # Create new user
            try:
                user = User.objects.create(
                    first_name=fname,
                    last_name=lname,
                    email=email,
                    username=email,
                )
                user.set_password(password)
                user.save()
                # Log the user in after registration
                login(request, user)
                messages.success(request, "Registration successful! You are loged in.")
                return render(request,'qr/add_restaurant.html', {
                'membership_choices': UserMembership.MEMBERSHIP,
                'restaurant_type': Restaurant.TYPE_CHOICES,
                'restaurant_category': Restaurant.CATEGORY_CHOICES
                })
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        
    return render(request,'qr/register.html')

def login_view(request):
    if request.method == "POST" :
        username = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect(reverse('dashboard'))
        else:
            messages.success(request,"Invalid Username or Password.")

    return render(request,'qr/login.html')
def create_razorpay_order(user, amount):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order = client.order.create({"amount": amount, "currency": "INR", "payment_capture": 1})
    Payment.objects.create(user=user, order_id=order["id"], amount=amount, status='created')
    return order

def verify_and_update_payment(user, razorpay_order_id, razorpay_payment_id, razorpay_signature):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    client.utility.verify_payment_signature({
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    })
    payment = Payment.objects.get(order_id=razorpay_order_id, user=user)
    payment.payment_id = razorpay_payment_id
    payment.signature = razorpay_signature
    payment.status = "paid"
    payment.save()

    
    return payment


@login_required
def add_restaurant(request):
    user = request.user

    if Restaurant.objects.filter(user=user).exists():
        return redirect('dashboard')

    if request.method == "POST":
        membership_type = request.POST.get("membership_type")
        if membership_type not in dict(UserMembership.MEMBERSHIP):
            return render(request, "qr/add_restaurant.html", {
                "error": "Invalid membership type",
                'membership_choices': UserMembership.MEMBERSHIP,
                'restaurant_type': Restaurant.TYPE_CHOICES,
                'restaurant_category': Restaurant.CATEGORY_CHOICES
            })

        plan = MEMBERSHIP_PRICING[membership_type]
        amount = plan["amount"]

        # Save form data to session
        request.session["restaurant_form"] = {
            field: request.POST.get(field) for field in [
                'restaurant_name', 'address','description', 'restaurant_type', 'mobile',
                'wifi', 'category', 'fassai', 'membership_type'
            ]
        }

        # Handle logo file
        logo = request.FILES.get("restaurant_logo")
        if logo:
            request.session["has_logo"] = True
            request.session["restaurant_logo_name"] = logo.name
            encoded_logo = base64.b64encode(logo.read()).decode('utf-8')  # convert bytes → base64 → string
            request.session["restaurant_logo_content"] = encoded_logo
        else:
            request.session["has_logo"] = False

        # Create Razorpay order
        try:

            # client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            # order = client.order.create({"amount": amount, "currency": "INR", "payment_capture": 1})

            # # Save payment
            # Payment.objects.create(user=user, order_id=order["id"], amount=amount, status='created')
            order = create_razorpay_order(user, amount)
            return render(request, "qr/payment_gateway.html", {
                "user": user,
                "membership_name": membership_type,
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "order_id": order["id"],
                "amount": amount
            })
        except (NetworkError, ServerError, BadRequestError) as e:
            print("Razorpay error:", e)
            return render(request, "qr/network_error.html", {
                "error": "Internet connection problem or payment gateway unavailable. Please try again later."
            })
    return render(request, "qr/add_restaurant.html", {
        'membership_choices': UserMembership.MEMBERSHIP,
        'restaurant_type': Restaurant.TYPE_CHOICES,
        'restaurant_category': Restaurant.CATEGORY_CHOICES,
        
    })
logger = logging.getLogger(__name__)
@csrf_exempt
def membership_payment_success(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "User not authenticated"}, status=403)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        user = request.user

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({"status": "error", "message": "Missing payment details"}, status=400)
        # razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            # razorpay_client.utility.verify_payment_signature({
            #     'razorpay_order_id': razorpay_order_id,
            #     'razorpay_payment_id': razorpay_payment_id,
            #     'razorpay_signature': razorpay_signature
            # })
            verify_and_update_payment(
            user=request.user,
            razorpay_order_id= razorpay_order_id,
            razorpay_payment_id= razorpay_payment_id,
            razorpay_signature= razorpay_signature
            )

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "error", "message": "Invalid payment signature"}, status=400)

        try:
            payment = Payment.objects.get(order_id=razorpay_order_id, user=user)
            payment.payment_id = razorpay_payment_id
            payment.signature = razorpay_signature
            payment.status = "paid"
            payment.save()
        except Payment.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Payment not found"}, status=404)


        form_data = request.session.pop("restaurant_form", {})
        membership_type = form_data.get("membership_type")

        plan = MEMBERSHIP_PRICING.get(membership_type)
        if not plan:
            return JsonResponse({"status": "error", "message": "Invalid membership plan"}, status=400)

        # Decode and restore logo if present
        logo = None
        if request.session.pop("has_logo", False):
            logo_name = request.session.pop("restaurant_logo_name")
            encoded_logo = request.session.pop("restaurant_logo_content")
            logo = ContentFile(base64.b64decode(encoded_logo), name=logo_name)

        try:
            logger.error(f"Creating Restaurant with data: {form_data}")
            
            restaurant = Restaurant.objects.create(
                user=request.user,
                restaurant_name=form_data.get("restaurant_name"),
                address=form_data.get("address"),
                description=form_data.get('description'),
                restaurant_type=form_data.get("restaurant_type"),
                mobile=form_data.get("mobile"),
                wifi=form_data.get("wifi"),
                category=form_data.get("category"),
                fassai=form_data.get("fassai"),
                logo=logo
            )

            logger.error(f"Restaurant created with ID: {restaurant.id}")

            UserMembership.objects.create(
                restaurant=restaurant,
                membership_type=membership_type,
                start_date=timezone.now().date(),
                duration=plan["duration"]
            )

            logger.error("UserMembership created")
        except Exception as e:
            logger.exception("Error in creating Restaurant or UserMembership")
            return JsonResponse({"status": "error", "message": f"Failed to create records: {str(e)}"}, status=500)

    
def renewMembership(request):
    if request.method == "POST":
        user=request.user
        membership_type = request.POST.get("membership_type")
        if not request.user.is_authenticated:
            return JsonResponse({"status":"error","message":"Login to continue."}, status=403)
        if membership_type not in dict(UserMembership.MEMBERSHIP):
            return render(request, "qr/add_restaurant.html", {
                "error": "Invalid membership type",
                'membership_choices': UserMembership.MEMBERSHIP,
                'restaurant_type': Restaurant.TYPE_CHOICES,
                'restaurant_category': Restaurant.CATEGORY_CHOICES
            })

        plan = MEMBERSHIP_PRICING[membership_type]
        amount = plan["amount"]

        try :
            order = create_razorpay_order(user, amount)
            return render(request, "qr/renewMembershipGateway.html", {
                "user": user,
                "membership_name": membership_type,
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "order_id": order["id"],
                "amount": amount
            })
        except (ServerError, BadRequestError) as e:
            print("Razorpay error:", e)
            return render(request, "qr/network_error.html", {
                "error": "Internet connection problem or payment gateway unavailable. Please try again later."
            })
    restaurant = Restaurant.objects.get(user=request.user)
    membership = UserMembership.objects.get(restaurant=restaurant)
    return render(request,'qr/renewMembership.html',{'restaurant':restaurant,'membership_choices': UserMembership.MEMBERSHIP,'membership':membership})

def membershipRenewSuccess(request):
    if request.method == 'POST':
        if not request.user.is_authenticated :
            return JsonResponse({"status":"error","message":"User not authenticated"},status=403)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        user = request.user

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({"status": "error", "message": "Missing payment details"}, status=400)
        try:
            verify_and_update_payment(
            user=request.user,
            razorpay_order_id= razorpay_order_id,
            razorpay_payment_id= razorpay_payment_id,
            razorpay_signature= razorpay_signature
            )

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "error", "message": "Invalid payment signature"}, status=400)

        try:
            restaurant = Restaurant.objects.get(user=user)
            membership = UserMembership.objects.get(restaurant=restaurant)
            membership.renew()
            messages.success(request,"Your membership renewed successfully.")
        except (Restaurant.DoesNotExist, UserMembership.DoesNotExist):
            return JsonResponse({"status": "error", "message": "error occured"}, status=404)


@login_required
def paymentHistory(request):
    user=request.user
    context = get_restaurant_details(user=user)
    # payment = Payment.objects.filter(user=user)
    return render(request,'qr/partials/paymentHistory.html',{'payments':context['payments'],'membership':context['membership'],'restaurant':context['restaurant']})

def generate_qr_codes(request):
    if request.method == "POST":
        user = request.user
        restaurant = Restaurant.objects.get(user=user)
        restaurant_name = restaurant.restaurant_name
        total_tables = int(request.POST.get('total_table'))

        qr_codes = []

        for table_num in range(1, total_tables + 1):
            table_url = request.build_absolute_uri(
                # f"/{restaurant_name.lower().replace(' ', '-')}/table/{table_num}/"
                f"/{restaurant.restaurant_id}/table/{table_num}/"
            )
            img_str = generate_qr_image_with_logo(
                table_url, restaurant_name, table_num,
                logo_path=restaurant.logo.path if restaurant.logo else None,
                return_base64=True
            )

            qr_codes.append({
                "table_number": table_num,
                "image": img_str,
            })

        return render(request, "qr/generated_qr_codes.html", {
            "qr_codes": qr_codes,
            "total_tables": total_tables
        })

    return render(request, "qr/generate_qr.html")

def download_qr_pdf(request):
    if request.method == "POST":
        user = request.user
        restaurant = Restaurant.objects.get(user=user)
        restaurant_name = restaurant.restaurant_name
        total_tables = int(request.POST.get("total_table"))

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        for table_num in range(1, total_tables + 1):
            table_url = request.build_absolute_uri(
                # f"/{restaurant_name.lower().replace(' ', '-')}/table/{table_num}/"
                f"/{restaurant.restaurant_id}/table/{table_num}/"
            )

            img_buffer = generate_qr_image_with_logo(
                table_url, restaurant_name, table_num,
                logo_path=restaurant.logo.path if restaurant.logo else None,
                return_base64=False
            )

            img_reader = ImageReader(img_buffer)
            p.drawImage(img_reader, x=150, y=height / 2 - 150, width=300, height=360)
            p.showPage()

        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf', headers={
            'Content-Disposition': f'attachment; filename="{restaurant_name}-qr_codes.pdf"'
        })

    return HttpResponse("Invalid request")

@login_required
def createQr(request):
    user=request.user
    restaurant = Restaurant.objects.get(user=user)
    membership = UserMembership.objects.select_related('restaurant').get(restaurant=restaurant)
    return render(request,'qr/createQr.html',{'restaurant':restaurant,'membership':membership})


def qr_pdf(request):
    if request.method == "POST":
        user = request.user
        restaurant = Restaurant.objects.get(user=user)
        restaurant_name = restaurant.restaurant_name

        table_number = request.POST.get("table_number")
        total_tables = request.POST.get("total_table")

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Single QR code
        if table_number:
            table_num = table_number
            table_url = request.build_absolute_uri(
                f"/{restaurant.restaurant_id}/table/{table_num}/"
            )
            img_buffer = generate_qr_image_with_logo(
                table_url, restaurant_name, table_num,
                logo_path=restaurant.logo.path if restaurant.logo else None,
                return_base64=False
            )
            img_reader = ImageReader(img_buffer)
            p.drawImage(img_reader, x=150, y=height / 2 - 150, width=300, height=360)
            p.showPage()
            filename = f"{restaurant_name}-table-{table_num}-qr.pdf"

        # Multiple QR codes
        elif total_tables:
            if not total_tables.isdigit():
                messages.error(request, "Table number must be a valid number.")
                return redirect('createQr')
            
            # Grid layout settings
            qr_width = 150
            qr_height = 180
            margin_x = 40
            margin_y = 40
            padding_x = 30
            padding_y = 30
            cols = int((width - 2 * margin_x + padding_x) // (qr_width + padding_x))
            x_start = margin_x
            y_start = height - margin_y - qr_height

            x = x_start
            y = y_start
            col = 0
            total_tables = int(total_tables)
            
            for table_num in range(1, total_tables + 1):
                table_url = request.build_absolute_uri(
                    f"/{restaurant.restaurant_id}/table/{table_num}/"
                )
                img_buffer = generate_qr_image_with_logo(
                    table_url, restaurant_name, table_num,
                    logo_path=restaurant.logo.path if restaurant.logo else None,
                    return_base64=False
                )
                img_reader = ImageReader(img_buffer)
                p.drawImage(img_reader, x, y, width=qr_width, height=qr_height)          
                # Optional: add label below QR
                p.setFont("Helvetica", 10)
                p.drawCentredString(x + qr_width / 2, y - 12, f"Table {table_num}")

                col += 1
                if col >= cols:
                    col = 0
                    x = x_start
                    y -= qr_height + padding_y + 20  # adjust for label
                    if y < margin_y:
                        p.showPage()
                        y = y_start
                else:
                    x += qr_width + padding_x
            filename = f"{restaurant_name}-qr-codes.pdf"

        else:
            return HttpResponse("No table number or total table count provided", status=400)

        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf', headers={
            'Content-Disposition': f'inline; filename="{filename}"'
        })

    return HttpResponse("Invalid request method", status=405)





















@login_required
def menuItems_dashboard (request):
    user = request.user
    context = get_restaurant_details(user)
    # restaurant = get_object_or_404(Restaurant,user=user)
    # menus = MenuItem.objects.filter(restaurant=restaurant)
    # membership = UserMembership.objects.get(restaurant=restaurant)
    return render(request,'qr/partials/menus.html',{'restaurant':context['restaurant'],'menus':context['menuItems'], 'user':request.user.username,'membership':context['membership']})

@login_required
def menus_dashboard (request):
    user = request.user
    restaurant =  get_object_or_404(Restaurant,user=user)
    menus = Menu.objects.filter(restaurant=restaurant)
    return render(request,'qr/partials/menu_categories.html',{'restaurant':restaurant,'menus':menus,'user':user})

def updateCategory(request, id):
    if request.method == 'POST':
        category = get_object_or_404(Menu, id=id)
        category.menu_name = request.POST.get('categoryName')
        category.save()
        return redirect('category')  # or your page name

@login_required
def dashboard(request):

    if request.user.is_authenticated:
        # user_instance = get_object_or_404(User,username=user)
        user_instance = request.user

        if Restaurant.objects.filter(user=user_instance).exists():
            restaurant = get_object_or_404(Restaurant,user=user_instance)
            menus = restaurant.menus.select_related('restaurant').prefetch_related('items')
            membership = UserMembership.objects.get(restaurant=restaurant)
            return render(request,'qr/dashboardBase.html',{'restaurant':restaurant,'menus':menus, 'user':request.user.username,'membership':membership})
        else :
            return render(request, 'qr/add_restaurant.html', {
                'membership_choices': UserMembership.MEMBERSHIP,
                'restaurant_type' : Restaurant.TYPE_CHOICES,
                'restaurant_category' : Restaurant.CATEGORY_CHOICES,
                'membership_pricing':MEMBERSHIP_PRICING,
                })
    return render(request,'qr/home.html')

@login_required
def add_menu_item(request):
    if request.user.is_authenticated :


        if request.method == 'POST':
            if request.FILES.get('image'):
                image=request.FILES['image']
            else:
                image="default/default.png"
            name=request.POST['name']
            description=request.POST['description']
            price=request.POST['price']
            category=request.POST['category']
            is_available=request.POST.get('is_available')
            menu_id = request.POST['menu']
            user_instance=request.user
            restaurant = get_object_or_404(Restaurant,user=user_instance)
            menu = get_object_or_404(Menu,id=menu_id)
            menu_item = MenuItem(image=image,name=name,description=description,price=price,category=category,is_available=is_available,menu=menu,restaurant=restaurant)



            menu_item.save()
            messages.success(request,"Menu Item added successfully.")
            return redirect('dashboard')
        else:
            user_instance=request.user
            restaurant= get_object_or_404(Restaurant,user=user_instance)
            menu = Menu.objects.filter(restaurant=restaurant)
            return render(request,'qr/partials/addMenuItem.html',{'restaurant':restaurant,'menu':menu})

    return redirect('login')

@login_required
def profile(request):

    if request.user.is_authenticated :
        user_instance = request.user
        context = get_restaurant_details(user_instance)
        # restaurant = get_object_or_404(Restaurant,user=user_instance)
        # membership_choices = UserMembership.objects.get(restaurant=restaurant)
        restaurant = context['restaurant']
        if request.method == "POST" :
            restaurant.restaurant_id=request.POST.get('restaurant_id')
            restaurant.restaurant_name=request.POST['restaurant_name']
            restaurant.address=request.POST['address']
            if request.FILES.get('image'):
                restaurant.logo=request.FILES['image']
            restaurant.mobile=request.POST['mobile']
            restaurant.wifi=request.POST['wifi']
            restaurant.category=request.POST['category']
            restaurant.membership_type=request.POST.get('membership_type')

            restaurant.save()
            messages.success(request,"Profile updated successfully.")
            return redirect('dashboard')
        else:

            return render(request,'qr/partials/newProfile.html',{'restaurant':context['restaurant'],'membership':context['membership']})
    else:
        return redirect('login')

@login_required
def category(request):

    if request.user.is_authenticated:
        if request.method=="POST":
            user_instance=request.user
            restaurant = get_object_or_404(Restaurant,user=user_instance)
            category_name=request.POST["categoryName"]
            menu=Menu(restaurant=restaurant,menu_name=category_name)
            menu.save()
            messages.success(request,"Menu category added successfully.")
            return redirect('category')
        else:
            user=request.user
            restaurant = get_object_or_404(Restaurant,user=user)
            menuCategory=Menu.objects.filter(restaurant=restaurant)
            membership = UserMembership.objects.get(restaurant=restaurant)
            return render(request,'qr/partials/menu_categories.html',{'user':user,'membership':membership,'menus':menuCategory,'restaurant':restaurant})
    else:
        return redirect('login')

@login_required
def update_menu_item(request,id):


    menu_item = get_object_or_404(MenuItem,id=id)
    user_instance=request.user
    restaurant=get_object_or_404(Restaurant,user=user_instance)

    if request.method == 'POST':

        if request.FILES.get('image'):
            menu_item.image = request.FILES['image']
        menu_item.name = request.POST['name']
        menu_item.description = request.POST['description']
        menu_item.price = request.POST['price']
        menu_item.category = request.POST['category']
        menu_item.is_available = request.POST.get('is_available') == 'on'
        menu_item.save()
        messages.success(request,"Menu Item updated successfully.")
        return redirect('dashboard')
    else:

        context = {'item':menu_item, 'restaurant':restaurant}

    return render(request,'qr/partials/load_update_menu_item.html',context)

@login_required
def delete_menu_item(request,id):
    try :

        menu_item = get_object_or_404(MenuItem,id=id)
        menu_item.delete()
        messages.success(request,"Menu Item deleted successfully.")
    except Exception as e:
        messages.error("Something went wrong.")
        return redirect('dashboard')

    return redirect('dashboard')

@login_required
def deleteCategory(request,id):

    try :
        menu=get_object_or_404(Menu,id=id)
        menu.delete()
        messages.success(request,"Menu deleted successfully.")
    except Exception :
        messages.error("Something went wrong.")
        return redirect('dashboard')

    return redirect('dashboard')
 
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

def submit_rating(request, id, table):
    # slug = restaurant
    # restaurant_name = slug.replace('-', ' ')
    restaurant_obj = get_object_or_404(
        Restaurant.objects.prefetch_related(
            Prefetch('ratings', queryset=Rating.objects.order_by('-created_at'))
        ),
        restaurant_id=id  # or restaurant_name__iexact if you're not using slug field
    )

    ratings = restaurant_obj.ratings.all()

    # Find the restaurant
    # restaurant = get_object_or_404(Restaurant, restaurant_name__iexact=restaurant_name)
    if request.method == "POST":
        stars = int(request.POST.get("stars"))
        review = request.POST.get("review", "")
        name = request.POST.get('name')
        # user = request.user if request.user.is_authenticated else None

        Rating.objects.create(
            restaurant=restaurant_obj,
            name=name,
            stars=stars,
            review=review
        )
        messages.success(request,"rating submitted successfully.")
        return redirect('qr_home',restaurant=restaurant_obj,table=table) 
    else :

        context = {
            # 'slug':slug,
            'restaurant':restaurant_obj,
            'table':table,
            'ratings':ratings
        }

        
        return render(request,'qr/ratings.html',context)

@login_required
def offers(request):
    restaurant = Restaurant.objects.get(user=request.user)
    membership = UserMembership.objects.get(restaurant=restaurant)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        discount_percentage =request.POST.get('discount_percentage')
        discount_amount = request.POST.get('discount_amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active')=='on'

        Offer.objects.create(
            restaurant= restaurant,
            title = title,
            description = description,
            discount_percentage = discount_percentage,
            discount_amount = discount_amount,
            start_date = start_date,
            end_date = end_date,
            is_active = is_active
        )
        messages.success(request,"Offer saved successfully...")
        return redirect('dashboard')
    
    return render(request,"qr/partials/offers.html",{
        'now': now(),
        'membership':membership,
    })

@login_required
def allOffers(request):
    restaurant = Restaurant.objects.get(user=request.user)
    offers = Offer.objects.filter(restaurant=restaurant)
    membership = UserMembership.objects.get(restaurant=restaurant)
    return render(request,'qr/partials/allOffers.html', {'offers':offers,'restaurant':restaurant,'membership':membership})

@login_required
def deleteOffer(request,id):
    offer=Offer.objects.filter(id=id)
    offer.delete()
    messages.success(request,"Offer deleted successfully.")
    return redirect('allOffers')


def enquiry(request):
    if request.method == 'POST':
        name= request.POST.get('name','').strip()
        email = request.POST.get('email','').strip()
        number = request.POST.get('mobile','').strip()
        message = request.POST.get('message','').strip()

        if not (name and email and number and message):
            messages.error(request, "All fields are required.")
            return redirect('homepage')

        try :
            Enquiry.objects.create(
            name=name,
            email=email,
            number=number,
            message=message
            )
            messages.success(request,"Form submitted successfully. We will come back to you soon.")
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")

        return redirect('homepage')

    return redirect('homepage')



@login_required
def renew_membership(request, plan_type):
    user = request.user

    if plan_type not in dict(UserMembership.MEMBERSHIP):
            return HttpResponseBadRequest("Invalid membership type.")

        # Get plan details
    plan = MEMBERSHIP_PRICING.get(plan_type)
    if not plan:
        return HttpResponseBadRequest("Plan not found.")

    amount = plan['amount']

        # Create Razorpay Order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': 1})

        # Save payment entry
    Payment.objects.create(
        user=user,
        order_id=order['id'],
        amount=amount
    )

        # Store the membership_type in session temporarily
    request.session['selected_membership_type'] = plan_type

    return render(request, 'qr/payment_gateway.html', {
        'user': user,
        'plan': plan_type,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'amount': amount,
        'is_upgrade': True  # optional flag to show UI differences
    })

@csrf_exempt
@login_required
def upgrade_payment_success(request):
    if request.method == "POST":
        user = request.user
        data = request.POST

        try:
            payment = Payment.objects.get(order_id=data.get('razorpay_order_id'))
        except Payment.DoesNotExist:
            return HttpResponse("Payment not found", status=404)

        # Verify signature (optional but best practice)
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                'razorpay_order_id': data.get('razorpay_order_id'),
                'razorpay_payment_id': data.get('razorpay_payment_id'),
                'razorpay_signature': data.get('razorpay_signature'),
            })
        except:
            return HttpResponse("Signature mismatch", status=400)

        # Update payment
        payment.payment_id = data.get('razorpay_payment_id')
        payment.signature = data.get('razorpay_signature')
        payment.is_paid = True
        payment.save()

        # Update membership
        plan_type = request.session.get("selected_membership_type")
        restaurant = get_object_or_404(Restaurant, user=user)

        UserMembership.objects.update_or_create(
            restaurant=restaurant,
            defaults={"membership_type": plan_type}
        )

        # Clear session
        request.session.pop("selected_membership_type", None)

        messages.success(request, "Membership upgraded successfully!")
        return redirect('dashboard')

    return HttpResponseBadRequest("Invalid request")

# Set up a logger
logger = logging.getLogger(__name__)

@csrf_exempt
def translate_texts(request):
    if request.method == 'POST':
        texts = request.POST.getlist('texts[]')
        target_lang = request.POST.get('language', 'mr')

        if not texts:
            return JsonResponse({'error': 'No texts provided'}, status=400)

        body = [{'Text': text} for text in texts]
        endpoint = settings.AZURE_TRANSLATOR_ENDPOINT.rstrip('/')
        url = f"{endpoint}/translate?api-version=3.0&to={target_lang}"
        headers = {
            'Ocp-Apim-Subscription-Key': settings.AZURE_TRANSLATOR_KEY,
            'Ocp-Apim-Subscription-Region': settings.AZURE_TRANSLATOR_REGION,
            'Content-type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            result = response.json()
            translated = [item['translations'][0]['text'] for item in result]
            return JsonResponse({'translated': translated,'language':target_lang})

        except requests.exceptions.RequestException as e:
            logger.error(f"Translation API failed: {e}")
            # Fallback to original texts (no translation)
            return JsonResponse({'translated': texts})

    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def transliterate_texts(request):
    if request.method == 'POST':
        texts = request.POST.getlist('texts[]')
        language = request.POST.get('language', 'mr')

        if not texts:
            return JsonResponse({'error': 'No texts provided'}, status=400)

        lang_map = {
            'mr': ('hi', 'Deva'),
            'hi': ('hi', 'Deva')
        }

        if language not in lang_map:
            return JsonResponse({'error': 'Unsupported language for transliteration'}, status=400)

        lang_code, script = lang_map[language]
        endpoint = settings.AZURE_TRANSLATOR_ENDPOINT.rstrip('/')
        url = f"{endpoint}/transliterate?api-version=3.0&language={lang_code}&fromScript=Latn&toScript={script}"
        headers = {
            'Ocp-Apim-Subscription-Key': settings.AZURE_TRANSLATOR_KEY,
            'Ocp-Apim-Subscription-Region': settings.AZURE_TRANSLATOR_REGION,
            'Content-type': 'application/json'
        }

        body = [{'Text': text} for text in texts]
        
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            result = response.json()
            transliterated = [item['text'] for item in result]
            return JsonResponse({'transliterated': transliterated,'language':language})

        except requests.exceptions.RequestException as e:
            logger.error(f"Transliteration API failed: {e}")
            # Fallback to original texts (no transliteration)
            return JsonResponse({'transliterated': texts})

    return JsonResponse({'error': 'Invalid method'}, status=405)