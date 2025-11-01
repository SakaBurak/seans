from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import Psychologist, Session, SessionTypeCommission, PaymentMethodCommission, Assistant

class PsychologistInline(admin.StackedInline):
    model = Psychologist
    can_delete = False
    verbose_name_plural = 'Psikolog Bilgileri'

class AssistantInline(admin.StackedInline):
    model = Assistant
    can_delete = False
    verbose_name_plural = 'Asistan Bilgileri'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (PsychologistInline, AssistantInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')

class PsychologistCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Kullanıcı Adı')
    email = forms.EmailField(label='E-posta')
    first_name = forms.CharField(max_length=30, label='Ad')
    last_name = forms.CharField(max_length=30, label='Soyad')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Şifre')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Şifre (Tekrar)')
    
    class Meta:
        model = Psychologist
        fields = ('phone', 'hourly_rate', 'commission_rate', 'extra_commission_rate', 'is_active')
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Şifreler eşleşmiyor.")
        return password2
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu kullanıcı adı zaten kullanılıyor.")
        return username

class AssistantCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Kullanıcı Adı')
    email = forms.EmailField(label='E-posta')
    first_name = forms.CharField(max_length=30, label='Ad')
    last_name = forms.CharField(max_length=30, label='Soyad')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Şifre')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Şifre (Tekrar)')
    
    class Meta:
        model = Assistant
        fields = ('phone', 'is_active')
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Şifreler eşleşmiyor.")
        return password2

class PsychologistAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'hourly_rate', 'commission_rate', 'extra_commission_rate', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone')
    list_editable = ('hourly_rate', 'commission_rate', 'extra_commission_rate', 'is_active')
    readonly_fields = ('created_at',)
    
    form = PsychologistCreationForm
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yeni kayıt oluşturuluyor
            # User oluştur
            user_data = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
            }
            user = User.objects.create_user(**user_data)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Psychologist'ı user'a bağla
            obj.user = user
        
        super().save_model(request, obj, form, change)
    
    def get_fieldsets(self, request, obj=None):
        if obj is None:  # Yeni kayıt ekleme
            return (
                ('Kullanıcı Bilgileri', {
                    'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
                }),
                ('Psikolog Bilgileri', {
                    'fields': ('phone', 'hourly_rate', 'commission_rate', 'extra_commission_rate', 'is_active')
                }),
            )
        else:  # Kayıt düzenleme
            return (
                ('Psikolog Bilgileri', {
                    'fields': ('user', 'phone', 'hourly_rate', 'commission_rate', 'extra_commission_rate', 'is_active', 'created_at')
                }),
            )

class AssistantAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone')
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    
    form = AssistantCreationForm
    
    def save_model(self, request, obj, form, change):
        if not change:  # Yeni kayıt oluşturuluyor
            user_data = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
            }
            user = User.objects.create_user(**user_data)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Assistant'ı user'a bağla
            obj.user = user
        
        super().save_model(request, obj, form, change)
    
    def get_fieldsets(self, request, obj=None):
        if obj is None:  # Yeni kayıt ekleme
            return (
                ('Kullanıcı Bilgileri', {
                    'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
                }),
                ('Asistan Bilgileri', {
                    'fields': ('phone', 'is_active')
                }),
            )
        else:  # Kayıt düzenleme
            return (
                ('Asistan Bilgileri', {
                    'fields': ('user', 'phone', 'is_active', 'created_at')
                }),
            )

class SessionAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'expert', 'date', 'duration', 'price', 'session_type', 'payment_method', 'status', 'extra_commission_rate', 'commission_breakdown_display')
    list_filter = ('status', 'session_type', 'payment_method', 'expert', 'date')
    search_fields = ('client_name', 'expert__user__username', 'expert__user__first_name', 'expert__user__last_name')
    list_editable = ('status', 'session_type', 'payment_method', 'extra_commission_rate')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Seans Bilgileri', {
            'fields': ('client_name', 'expert', 'date', 'duration', 'price', 'status')
        }),
        ('Seans Detayları', {
            'fields': ('session_type', 'payment_method', 'extra_commission_rate', 'notes')
        }),
        ('Sistem Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def commission_breakdown_display(self, obj):
        """Kesinti detaylarını admin listesinde göster"""
        if obj.status == 'done':
            breakdown = obj.commission_breakdown
            if breakdown:
                return '<br>'.join(breakdown)
        return '-'
    commission_breakdown_display.short_description = 'Kesinti Detayları'
    commission_breakdown_display.allow_tags = True
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Psikologlar sadece kendi seanslarını görebilir
        try:
            psychologist = request.user.psychologist
            return qs.filter(expert=psychologist)
        except Psychologist.DoesNotExist:
            return qs.none()

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Psychologist, PsychologistAdmin)
admin.site.register(Assistant, AssistantAdmin)
admin.site.register(SessionTypeCommission)
admin.site.register(PaymentMethodCommission)
admin.site.register(Session, SessionAdmin)
