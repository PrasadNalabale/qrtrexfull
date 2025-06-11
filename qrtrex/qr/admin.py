from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Restaurant, UserMembership, Menu, MenuItem,Payment,Rating,Offer,Liquor,LiquorTypes,Enquiry
from django.contrib.admin import AdminSite
from django.urls import path
from django.utils.translation import gettext_lazy as _

admin.site.site_header = "QRtrex Admin"
admin.site.site_title = "QRtrex Admin Portal"
admin.site.index_title = "Welcome to QRtrex Admin"

    



class CustomUserAdmin(UserAdmin):
    # Display fields in the admin panel
    model = User
    list_display = ('username', 'first_name','last_name', 'email','restaurant_name' ,'is_staff', 'is_superuser')
    list_filter = ('is_superuser', 'is_staff')
    search_fields = ('username', 'first_name', 'email')
    ordering = ('username',)
    
    # Required fields for creating users
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name','last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    def restaurant_name(self, obj):
        restaurant = obj.restaurant_set.first()  # if reverse FK
        return restaurant.restaurant_name if restaurant else "—"


    restaurant_name.short_description = 'Restaurant Name'
    
    
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)



@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('restaurant_id', 'restaurant_name', 'user', 'mobile', 'email', 'category', 'created_at')
    search_fields = ('restaurant_name', 'restaurant_id', 'email')
    list_filter = ('category',)
    ordering = ('-created_at',)

@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    readonly_fields = ('end_date', 'duration')  # calculated automatically
    list_display = ('get_restaurant_id','get_restaurant_name', 'membership_type', 'start_date', 'end_date', 'is_active_display')
    search_fields = ('get_restaurant_id','get_restaurant_name','membership_type')

    def get_restaurant_id(self, obj):
        return obj.restaurant.restaurant_id
    get_restaurant_id.admin_order_field = 'restaurant__restaurant_id'
    get_restaurant_id.short_description = 'Restaurant ID'

    def get_restaurant_name(self, obj):
        return obj.restaurant.restaurant_name
    get_restaurant_name.admin_order_field = 'restaurant__restaurant_name'
    get_restaurant_name.short_description = 'Restaurant Name'

    def is_active_display(self, obj):
        return obj.is_active()
    is_active_display.boolean = True
    is_active_display.short_description = "Active"
    

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'menu_name')
    search_fields = ('menu_name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'menu', 'price', 'category', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')

# custom_admin_site.register(Restaurant,RestaurantAdmin)
# custom_admin_site.register(UserMembership,UserMembershipAdmin)
# custom_admin_site.register(Menu,MenuAdmin)
# custom_admin_site.register(MenuItem,MenuItemAdmin)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_id', 'payment_id', 'amount_display', 'status', 'created_at','signature')
    search_fields = ('user__username', 'order_id', 'payment_id')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)

    def amount_display(self, obj):
        return f"₹{obj.amount / 100:.2f}"
    amount_display.short_description = 'Amount'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('restaurant','name','stars', 'created_at')
    list_filter = ('stars', 'created_at','name')
    search_fields = ('review', 'reply','name')
    readonly_fields = ('restaurant', 'stars', 'review', 'created_at')

    # Allow reply
    fields = ('restaurant', 'stars', 'review', 'reply','name', 'created_at')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('-start_date',)

@admin.register(Liquor)
class LiquorAdmin(admin.ModelAdmin):
    list_display = ('restaurant','liquorTypes','name','price')
    list_filter = ('restaurant','name')
    search_fields = ('restaurant','name')

@admin.register(LiquorTypes)
class LiquorTypesAdmin(admin.ModelAdmin):
    list_display = ('restaurant','name')
    list_filter = ('name','restaurant')
    search_fields = ('restaurant','name')

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name','email','number','status','created_at')
    list_filter = ('name','status','email','created_at')
    search_fields = ('email','name','number','status')