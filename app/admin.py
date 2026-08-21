from django.contrib import admin

# Register your models here.
from .models import User, Plan, Feature, Subscription, Usage,Transaction

admin.site.register(User)
admin.site.register(Plan)
admin.site.register(Feature)
admin.site.register(Subscription)
admin.site.register(Usage)
admin.site.register(Transaction)