from django.contrib import admin
from .models import Reservation

# Register your models here.
# admin.site.register(Reservation)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'region', 'suggestion', 'created_at')