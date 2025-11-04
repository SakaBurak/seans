from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Psychologist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField("Telefon", max_length=15, blank=True)
    hourly_rate = models.DecimalField("Saatlik Ücret", max_digits=10, decimal_places=2, default=0)
    commission_rate = models.DecimalField("Kesinti Oranı (%)", max_digits=5, decimal_places=2, default=50.00)
    extra_commission_rate = models.DecimalField("Ek Kesinti Oranı (%)", max_digits=5, decimal_places=2, default=0.00, help_text="Admin tarafından ayarlanabilir ek kesinti oranı")
    is_active = models.BooleanField("Aktif", default=True)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    class Meta:
        verbose_name = "Psikolog"
        verbose_name_plural = "Psikologlar"

class Assistant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField("Telefon", max_length=15, blank=True)
    is_active = models.BooleanField("Aktif", default=True)
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    class Meta:
        verbose_name = "Asistan"
        verbose_name_plural = "Asistanlar"

class SessionTypeCommission(models.Model):
    session_type = models.CharField("Seans Türü", max_length=20, unique=True)
    rate = models.DecimalField("Ek Kesinti Oranı (%)", max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.get_session_type_display()} - %{self.rate}"
    
    class Meta:
        verbose_name = "Seans Türü Ek Kesinti"
        verbose_name_plural = "Seans Türü Ek Kesintiler"

class PaymentMethodCommission(models.Model):
    payment_method = models.CharField("Ödeme Yöntemi", max_length=20, unique=True)
    rate = models.DecimalField("Ek Kesinti Oranı (%)", max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.get_payment_method_display()} - %{self.rate}"
    
    class Meta:
        verbose_name = "Ödeme Yöntemi Ek Kesinti"
        verbose_name_plural = "Ödeme Yöntemi Ek Kesintiler"

class Session(models.Model):
    SESSION_TYPE_CHOICES = [
        ('online', 'Online Seans'),
        ('face_to_face', 'Yüz Yüze Seans'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Nakit'),
        ('credit_card', 'Kredi Kartı'),
        ('debit_card', 'Banka Kartı'),
        ('bank_transfer', 'Banka Transferi'),
    ]
    
    expert = models.ForeignKey(Psychologist, on_delete=models.CASCADE, verbose_name="Psikolog")
    client_name = models.CharField("Danışan Adı", max_length=100)
    date = models.DateTimeField("Tarih ve Saat")
    duration = models.IntegerField("Süre (Dakika)", default=60)
    price = models.DecimalField("Seans Ücreti", max_digits=10, decimal_places=2, default=0)
    session_type = models.CharField("Seans Türü", max_length=20, choices=SESSION_TYPE_CHOICES, default='face_to_face')
    payment_method = models.CharField("Ödeme Yöntemi", max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    extra_commission_rate = models.DecimalField("Ek Kesinti Oranı (%)", max_digits=5, decimal_places=2, default=0.00, help_text="Bu seans için özel ek kesinti oranı")
    notes = models.TextField("Notlar", blank=True)

    STATUS_CHOICES = [
        ('planned', 'Planlandı'),
        ('done', 'Yapıldı'),
        ('canceled', 'İptal'),
    ]
    status = models.CharField("Durum", max_length=10, choices=STATUS_CHOICES, default='planned')
    
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme Tarihi", auto_now=True)

    def __str__(self):
        return f"{self.client_name} - {self.date.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def commission_amount(self):
        """Kesinti miktarını hesapla"""
        if self.status == 'done' and self.price > 0:
            # Psikolog bazında kesinti
            psychologist_commission = (self.price * self.expert.commission_rate) / 100
            
            # Seans bazında ek kesinti oranı (admin tarafından ayarlanabilir)
            session_extra_commission = (self.price * self.extra_commission_rate) / 100
            
            # Seans türüne göre ek kesinti (dinamik)
            session_commission = 0
            try:
                stc = SessionTypeCommission.objects.get(session_type=self.session_type)
                session_commission = (self.price * stc.rate) / 100
            except SessionTypeCommission.DoesNotExist:
                pass
            
            # Ödeme yöntemine göre ek kesinti (dinamik)
            payment_commission = 0
            try:
                pmc = PaymentMethodCommission.objects.get(payment_method=self.payment_method)
                payment_commission = (self.price * pmc.rate) / 100
            except PaymentMethodCommission.DoesNotExist:
                pass
            
            return psychologist_commission + session_extra_commission + session_commission + payment_commission
        return 0
    
    @property
    def net_amount(self):
        """Net kazanç hesapla"""
        if self.status == 'done':
            return self.price - self.commission_amount
        return 0
    
    @property
    def commission_breakdown(self):
        """Kesinti detaylarını döndür"""
        if self.status == 'done' and self.price > 0:
            breakdown = []
            
            # Psikolog bazında kesinti
            psychologist_commission = (self.price * self.expert.commission_rate) / 100
            breakdown.append(f"Psikolog Kesintisi (%{self.expert.commission_rate}): ₺{psychologist_commission:.2f}")
            
            # Seans bazında ek kesinti oranı
            if self.extra_commission_rate > 0:
                session_extra_commission = (self.price * self.extra_commission_rate) / 100
                breakdown.append(f"Seans Ek Kesintisi (%{self.extra_commission_rate}): ₺{session_extra_commission:.2f}")
            
            # Seans türüne göre ek kesinti
            try:
                stc = SessionTypeCommission.objects.get(session_type=self.session_type)
                session_commission = (self.price * stc.rate) / 100
                if session_commission > 0:
                    breakdown.append(f"Seans Türü Kesintisi (%{stc.rate}): ₺{session_commission:.2f}")
            except SessionTypeCommission.DoesNotExist:
                pass
            
            # Ödeme yöntemine göre ek kesinti
            try:
                pmc = PaymentMethodCommission.objects.get(payment_method=self.payment_method)
                payment_commission = (self.price * pmc.rate) / 100
                if payment_commission > 0:
                    breakdown.append(f"Ödeme Yöntemi Kesintisi (%{pmc.rate}): ₺{payment_commission:.2f}")
            except PaymentMethodCommission.DoesNotExist:
                pass
            
            return breakdown
        return []
    
    @property
    def total_commission_rate(self):
        """Toplam kesinti oranını hesapla (%)"""
        total_rate = self.expert.commission_rate
        
        # Seans bazında ek kesinti oranı
        total_rate += self.extra_commission_rate
        
        # Seans türüne göre ek kesinti
        try:
            stc = SessionTypeCommission.objects.get(session_type=self.session_type)
            total_rate += stc.rate
        except SessionTypeCommission.DoesNotExist:
            pass
        
        # Ödeme yöntemine göre ek kesinti
        try:
            pmc = PaymentMethodCommission.objects.get(payment_method=self.payment_method)
            total_rate += pmc.rate
        except PaymentMethodCommission.DoesNotExist:
            pass
        
        return total_rate
    
    class Meta:
        verbose_name = "Seans"
        verbose_name_plural = "Seanslar"
        ordering = ['-date']
