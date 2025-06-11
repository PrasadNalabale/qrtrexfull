"""
URL configuration for qrtrex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from qr import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name="homepage"),
    path('login/', views.login_view , name="login"),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('dashboard/update_menu_item/<int:id>/',views.update_menu_item,name="update_menu_item"),
    path('dashboard/delete_menu_item/<int:id>/',views.delete_menu_item, name="delete_menu_item"),
    path('profile/', views.profile,name="profile"),
    path('dashboard/add_menu_item/',views.add_menu_item,name="new_menu"),
    path('category/', views.category, name="category"),
    path('deleteCategory/<int:id>/', views.deleteCategory, name="deleteCategory"),
    path('logout/',views.user_logout, name="logout"),
    path('register/',views.register, name="register"),
    path('add-restaurant/',views.add_restaurant,name='add_restaurant'),
    # path("restaurant/add/", views.add_restaurant, name="add_restaurant"),
    path("restaurant/payment-success/", views.membership_payment_success, name="membership_payment_success"),
    path("generate_qr/", views.generate_qr_codes, name="generate_qr"),
    path("download-qr-pdf/", views.download_qr_pdf, name="download_qr_pdf"),
    path('<int:id>/table/<int:table>/', views.qr_home, name='qr_home'),
    path('<int:id>/table/<int:table>/menu', views.qr_menu, name='qr_menu'),
    path('<int:id>/table/<int:table>/liquor', views.qr_liquor, name='liquor'),
    path('menuItems/',views.menuItems_dashboard, name='menuItems'),
    path('menus/',views.menus_dashboard, name='menus'),
    path('paymentHistory/',views.paymentHistory,name='paymentHistory'),
    path('ratings/<int:id>/table/<int:table>/',views.submit_rating, name='ratings'),
    path('membership/upgrade/<str:plan_type>/', views.renew_membership, name='renew_membership'),
    path('membership/payment/success/', views.upgrade_payment_success, name='upgrade_payment_success'),
    path('api/translate/', views.translate_texts, name='translate_texts'),
    path('api/transliterate/', views.transliterate_texts, name='transliterate_texts'),
    path('demo/', views.demo, name='demo'),
    path('cart/<int:id>/', views.cart, name='cart'),
    path('offers/', views.offers,name="offers"),
    path('allOffers/', views.allOffers, name="allOffers"),
    path('deleteOffer/<int:id>/', views.deleteOffer, name="deleteOffer"),
    path('',include('pwa.urls')),
    path('renewMembership/',views.renewMembership,name="renewMembership"),
    path('qr-pdf/',views.qr_pdf, name="qr-pdf"),
    path('createQr/',views.createQr,name='createQr'),
    path('enquiry/',views.enquiry,name='enquiry'),
    path('update-category/<int:id>/', views.updateCategory, name='updateCategory'),
    path('renewMembershipPayment/',views.membershipRenewSuccess, name="renewMembershipPayment")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)