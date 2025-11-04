# sari_seans/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from .models import Session, Psychologist, SessionTypeCommission, PaymentMethodCommission, Assistant
from django.contrib.auth.models import User

def is_assistant(user):
    return hasattr(user, 'assistant')

def is_psychologist(user):
    return hasattr(user, 'psychologist')

def is_admin(user):
    return user.is_superuser

@login_required
def dashboard(request):
    """Ana dashboard - kullanıcı tipine göre yönlendirme"""
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif is_psychologist(request.user):
        return redirect('psychologist_dashboard')
    elif is_assistant(request.user):
        return redirect('assistant_dashboard')
    else:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('login')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard - tüm psikologların özeti"""
    psychologists = Psychologist.objects.filter(is_active=True)
    assistants = Assistant.objects.filter(is_active=True)
    
    # Ay filtreleme
    selected_month = int(request.GET.get('month', timezone.now().month))
    selected_year = int(request.GET.get('year', timezone.now().year))
    
    # Toplam istatistikler (tüm seanslar)
    total_sessions = Session.objects.count()
    total_revenue = Session.objects.filter(status='done').aggregate(Sum('price'))['price__sum'] or 0
    
    # Toplam kesinti hesaplama
    total_commission = 0
    for session in Session.objects.filter(status='done'):
        total_commission += session.commission_amount
    
    # Seçilen ay için istatistikler (tüm seanslar - durumdan bağımsız)
    monthly_sessions_all = Session.objects.filter(
        date__month=selected_month,
        date__year=selected_year
    )
    monthly_sessions_count = monthly_sessions_all.count()
    
    # Sadece 'done' durumundaki seanslar için gelir ve kesinti hesaplama
    monthly_sessions_done = monthly_sessions_all.filter(status='done')
    monthly_revenue = monthly_sessions_done.aggregate(Sum('price'))['price__sum'] or 0
    
    # Aylık kesinti hesaplama
    monthly_commission = 0
    for session in monthly_sessions_done:
        monthly_commission += session.commission_amount
    
    monthly_net = monthly_revenue - monthly_commission
    
    # Psikolog bazında istatistikler
    psychologist_stats = []
    for psychologist in psychologists:
        # Tüm seanslar
        all_sessions = Session.objects.filter(expert=psychologist)
        total_sessions_count = all_sessions.count()
        total_earnings = all_sessions.filter(status='done').aggregate(Sum('price'))['price__sum'] or 0
        
        # Aylık seanslar (tüm seanslar - durumdan bağımsız)
        monthly_psychologist_sessions_all = all_sessions.filter(
            date__month=selected_month,
            date__year=selected_year
        )
        monthly_psychologist_sessions_count = monthly_psychologist_sessions_all.count()
        
        # Sadece 'done' durumundaki seanslar için gelir ve kesinti hesaplama
        monthly_psychologist_sessions_done = monthly_psychologist_sessions_all.filter(status='done')
        monthly_earnings = monthly_psychologist_sessions_done.aggregate(Sum('price'))['price__sum'] or 0
        
        # Kesinti hesaplama
        commission_amount = 0
        for session in all_sessions.filter(status='done'):
            commission_amount += session.commission_amount
            
        monthly_commission_amount = 0
        for session in monthly_psychologist_sessions_done:
            monthly_commission_amount += session.commission_amount
            
        net_earnings = total_earnings - commission_amount
        monthly_net_earnings = monthly_earnings - monthly_commission_amount
        
        psychologist_stats.append({
            'psychologist': psychologist,
            'total_sessions': total_sessions_count,
            'total_earnings': total_earnings,
            'commission_amount': commission_amount,
            'net_earnings': net_earnings,
            'monthly_sessions': monthly_psychologist_sessions_count,
            'monthly_earnings': monthly_earnings,
            'monthly_commission': monthly_commission_amount,
            'monthly_net': monthly_net_earnings,
        })
    
    # Ay seçenekleri
    months = [
        (1, 'Ocak'), (2, 'Şubat'), (3, 'Mart'), (4, 'Nisan'),
        (5, 'Mayıs'), (6, 'Haziran'), (7, 'Temmuz'), (8, 'Ağustos'),
        (9, 'Eylül'), (10, 'Ekim'), (11, 'Kasım'), (12, 'Aralık')
    ]
    
    # Son 5 yıl
    current_year = timezone.now().year
    years = range(current_year - 2, current_year + 1)
    
    context = {
        'psychologists': psychologists,
        'assistants': assistants,
        'psychologist_stats': psychologist_stats,
        'total_sessions': total_sessions,
        'total_revenue': total_revenue,
        'total_commission': total_commission,
        'monthly_sessions_count': monthly_sessions_count,
        'monthly_revenue': monthly_revenue,
        'monthly_commission': monthly_commission,
        'monthly_net': monthly_net,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': months,
        'years': years,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(is_psychologist)
def psychologist_dashboard(request):
    """Psikolog dashboard - kendi seansları ve kazancı"""
    psychologist = request.user.psychologist
    
    # Ay filtreleme
    selected_month = int(request.GET.get('month', timezone.now().month))
    selected_year = int(request.GET.get('year', timezone.now().year))
    
    # Seanslar
    sessions = Session.objects.filter(expert=psychologist).order_by('-date')
    
    # Toplam istatistikler (tüm seanslar)
    total_sessions = sessions.count()
    total_earnings = sessions.filter(status='done').aggregate(Sum('price'))['price__sum'] or 0
    
    # Kesinti hesaplama - psikolog bazında
    commission_amount = 0
    for session in sessions.filter(status='done'):
        commission_amount += session.commission_amount
    
    net_earnings = total_earnings - commission_amount
    
    # Seçilen ay için istatistikler
    monthly_sessions = sessions.filter(
        date__month=selected_month,
        date__year=selected_year
    )
    monthly_sessions_count = monthly_sessions.count()
    monthly_earnings = monthly_sessions.filter(status='done').aggregate(Sum('price'))['price__sum'] or 0
    
    # Aylık kesinti hesaplama
    monthly_commission = 0
    for session in monthly_sessions.filter(status='done'):
        monthly_commission += session.commission_amount
    
    monthly_net = monthly_earnings - monthly_commission
    
    # Ay seçenekleri
    months = [
        (1, 'Ocak'), (2, 'Şubat'), (3, 'Mart'), (4, 'Nisan'),
        (5, 'Mayıs'), (6, 'Haziran'), (7, 'Temmuz'), (8, 'Ağustos'),
        (9, 'Eylül'), (10, 'Ekim'), (11, 'Kasım'), (12, 'Aralık')
    ]
    
    # Son 5 yıl
    current_year = timezone.now().year
    years = range(current_year - 2, current_year + 1)
    
    context = {
        'sessions': sessions[:10],  # Son 10 seans
        'total_sessions': total_sessions,
        'total_earnings': total_earnings,
        'commission_amount': commission_amount,
        'net_earnings': net_earnings,
        'monthly_sessions_count': monthly_sessions_count,
        'monthly_earnings': monthly_earnings,
        'monthly_commission': monthly_commission,
        'monthly_net': monthly_net,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': months,
        'years': years,
    }
    return render(request, 'psychologist_dashboard.html', context)

@login_required
@user_passes_test(is_assistant)
def assistant_dashboard(request):
    """Asistan dashboard - seans yönetimi odaklı"""
    # Ay filtreleme
    selected_month = int(request.GET.get('month', timezone.now().month))
    selected_year = int(request.GET.get('year', timezone.now().year))
    
    # Tüm seanslar (kesinti bilgileri olmadan)
    sessions = Session.objects.all().order_by('-date')
    
    # Toplam istatistikler
    total_sessions = sessions.count()
    
    # Seçilen ay için istatistikler
    monthly_sessions = sessions.filter(
        date__month=selected_month,
        date__year=selected_year
    )
    monthly_sessions_count = monthly_sessions.count()
    
    # Psikolog bazında istatistikler (sadece seans sayısı)
    psychologists = Psychologist.objects.filter(is_active=True)
    psychologist_stats = []
    
    for psychologist in psychologists:
        all_sessions = Session.objects.filter(expert=psychologist)
        total_sessions_count = all_sessions.count()
        
        monthly_psychologist_sessions = all_sessions.filter(
            date__month=selected_month,
            date__year=selected_year
        )
        monthly_sessions_count = monthly_psychologist_sessions.count()
        
        psychologist_stats.append({
            'psychologist': psychologist,
            'total_sessions': total_sessions_count,
            'monthly_sessions': monthly_sessions_count,
        })
    
    # Ay seçenekleri
    months = [
        (1, 'Ocak'), (2, 'Şubat'), (3, 'Mart'), (4, 'Nisan'),
        (5, 'Mayıs'), (6, 'Haziran'), (7, 'Temmuz'), (8, 'Ağustos'),
        (9, 'Eylül'), (10, 'Ekim'), (11, 'Kasım'), (12, 'Aralık')
    ]
    
    # Son 5 yıl
    current_year = timezone.now().year
    years = range(current_year - 2, current_year + 1)
    
    context = {
        'psychologists': psychologists,
        'psychologist_stats': psychologist_stats,
        'total_sessions': total_sessions,
        'monthly_sessions_count': monthly_sessions_count,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'months': months,
        'years': years,
    }
    return render(request, 'assistant_dashboard.html', context)

@login_required
@user_passes_test(is_assistant)
def assistant_manage_sessions(request):
    """Asistan seans yönetimi - kesinti bilgileri olmadan"""
    sessions = Session.objects.all().order_by('-date')
    
    # Filtreleme
    status_filter = request.GET.get('status')
    psychologist_filter = request.GET.get('psychologist')
    month_filter = request.GET.get('month')
    year_filter = request.GET.get('year')
    
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    
    if psychologist_filter:
        sessions = sessions.filter(expert_id=psychologist_filter)
    
    if month_filter:
        sessions = sessions.filter(date__month=int(month_filter))
    if year_filter:
        sessions = sessions.filter(date__year=int(year_filter))
    
    psychologists = Psychologist.objects.filter(is_active=True)
    
    # Ay seçenekleri
    months = [
        (1, 'Ocak'), (2, 'Şubat'), (3, 'Mart'), (4, 'Nisan'),
        (5, 'Mayıs'), (6, 'Haziran'), (7, 'Temmuz'), (8, 'Ağustos'),
        (9, 'Eylül'), (10, 'Ekim'), (11, 'Kasım'), (12, 'Aralık')
    ]
    current_year = timezone.now().year
    years = range(current_year - 2, current_year + 1)
    
    context = {
        'sessions': sessions,
        'psychologists': psychologists,
        'months': months,
        'years': years,
    }
    return render(request, 'assistant_manage_sessions.html', context)

@login_required
@user_passes_test(is_assistant)
def assistant_add_session(request):
    """Asistan seans ekleme - kesinti alanları olmadan"""
    if request.method == 'POST':
        # Seans ekleme formu işleme
        client_name = request.POST.get('client_name')
        expert_id = request.POST.get('expert')
        date = request.POST.get('date')
        duration = request.POST.get('duration')
        price = request.POST.get('price')
        session_type = request.POST.get('session_type')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        
        # Validasyon
        try:
            expert = Psychologist.objects.get(id=expert_id)
            
            # Süre kontrolü
            if duration:
                try:
                    duration = int(duration)
                except ValueError:
                    messages.error(request, 'Geçersiz süre formatı!')
                    psychologists = Psychologist.objects.filter(is_active=True)
                    return render(request, 'assistant_add_session.html', {'psychologists': psychologists})
            
            # Ücret kontrolü
            if price:
                try:
                    price = Decimal(str(price))
                    if price < 0:
                        messages.error(request, 'Ücret negatif olamaz!')
                        psychologists = Psychologist.objects.filter(is_active=True)
                        return render(request, 'assistant_add_session.html', {'psychologists': psychologists})
                except (ValueError, InvalidOperation):
                    messages.error(request, 'Geçersiz ücret formatı!')
                    psychologists = Psychologist.objects.filter(is_active=True)
                    return render(request, 'assistant_add_session.html', {'psychologists': psychologists})
            
            session = Session.objects.create(
                client_name=client_name,
                expert=expert,
                date=date,
                duration=duration,
                price=price,
                session_type=session_type,
                payment_method=payment_method,
                status=status,
                notes=notes,
                extra_commission_rate=Decimal('0')  # Asistan kesinti belirleyemez
            )
            messages.success(request, f'{client_name} için seans başarıyla eklendi.')
            return redirect('assistant_manage_sessions')
        except Exception as e:
            messages.error(request, f'Seans eklenirken hata oluştu: {str(e)}')
    
    psychologists = Psychologist.objects.filter(is_active=True)
    context = {
        'psychologists': psychologists,
    }
    return render(request, 'assistant_add_session.html', context)

@login_required
@user_passes_test(is_assistant)
def assistant_edit_session(request, session_id):
    """Asistan seans düzenleme - kesinti alanları olmadan"""
    session = get_object_or_404(Session, id=session_id)
    
    if request.method == 'POST':
        # Seans düzenleme formu işleme (kesinti alanları hariç)
        session.client_name = request.POST.get('client_name')
        session.expert_id = request.POST.get('expert')
        session.date = request.POST.get('date')
        
        # Süre kontrolü
        duration = request.POST.get('duration')
        if duration:
            try:
                session.duration = int(duration)
            except ValueError:
                messages.error(request, 'Geçersiz süre formatı!')
                return redirect('assistant_edit_session', session_id=session_id)
        
        # Ücret güvenlik kontrolü
        new_price = request.POST.get('price')
        if new_price:
            try:
                session.price = Decimal(str(new_price))
                if session.price < 0:
                    messages.error(request, 'Ücret negatif olamaz!')
                    return redirect('assistant_edit_session', session_id=session_id)
            except (ValueError, InvalidOperation):
                messages.error(request, 'Geçersiz ücret formatı!')
                return redirect('assistant_edit_session', session_id=session_id)
        
        session.session_type = request.POST.get('session_type')
        session.payment_method = request.POST.get('payment_method')
        session.status = request.POST.get('status')
        session.notes = request.POST.get('notes')
        # extra_commission_rate değiştirilmez
        session.save()
        
        messages.success(request, f'{session.client_name} için seans başarıyla güncellendi.')
        return redirect('assistant_manage_sessions')
    
    psychologists = Psychologist.objects.filter(is_active=True)
    # Decimal değerini string'e çevir
    session_price_str = str(session.price) if session.price else "0"
    context = {
        'session': session,
        'session_price_str': session_price_str,
        'psychologists': psychologists,
    }
    return render(request, 'assistant_edit_session.html', context)

@login_required
@user_passes_test(is_assistant)
def assistant_delete_session(request, session_id):
    """Asistan seans silme"""
    session = get_object_or_404(Session, id=session_id)
    client_name = session.client_name
    
    if request.method == 'POST':
        session.delete()
        messages.success(request, f'{client_name} için seans başarıyla silindi.')
        return redirect('assistant_manage_sessions')
    
    context = {
        'session': session,
    }
    return render(request, 'assistant_delete_session.html', context)

@login_required
@user_passes_test(is_admin)
def manage_psychologists(request):
    """Psikolog yönetimi"""
    # Admin'i psikolog listesinden çıkar
    psychologists = Psychologist.objects.all().order_by('-created_at')
    
    # İstatistikler için ayrı queryset'ler
    total_psychologists = psychologists.count()
    active_psychologists = psychologists.filter(is_active=True).count()
    passive_psychologists = psychologists.filter(is_active=False).count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        psychologist_id = request.POST.get('psychologist_id')
        
        if action == 'delete' and psychologist_id:
            psychologist = get_object_or_404(Psychologist, id=psychologist_id)
            psychologist.is_active = False
            psychologist.save()
            messages.success(request, f'{psychologist} pasif hale getirildi.')
            return redirect('manage_psychologists')
        elif action == 'activate' and psychologist_id:
            psychologist = get_object_or_404(Psychologist, id=psychologist_id)
            psychologist.is_active = True
            psychologist.save()
            messages.success(request, f'{psychologist} aktif hale getirildi.')
            return redirect('manage_psychologists')
        elif action == 'update_extra_commission' and psychologist_id:
            rate = request.POST.get('extra_commission_rate')
            psychologist = get_object_or_404(Psychologist, id=psychologist_id)
            try:
                psychologist.extra_commission_rate = rate
                psychologist.save()
                messages.success(request, f'{psychologist} için ek kesinti oranı %{rate} olarak güncellendi.')
            except Exception as e:
                messages.error(request, f'Ek kesinti oranı güncellenirken hata oluştu: {str(e)}')
            return redirect('manage_psychologists')
    
    context = {
        'psychologists': psychologists,
        'total_psychologists': total_psychologists,
        'active_psychologists': active_psychologists,
        'passive_psychologists': passive_psychologists,
    }
    return render(request, 'manage_psychologists.html', context)

@login_required
@user_passes_test(is_admin)
def manage_extra_commission(request):
    """Ek kesinti oranları yönetimi"""
    session_type_commissions = SessionTypeCommission.objects.all().order_by('session_type')
    payment_method_commissions = PaymentMethodCommission.objects.all().order_by('payment_method')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'session_type':
            session_type = request.POST.get('session_type')
            rate = request.POST.get('rate')
            if session_type and rate:
                SessionTypeCommission.objects.update_or_create(
                    session_type=session_type,
                    defaults={'rate': rate}
                )
                messages.success(request, f'{session_type} seans türü için %{rate} kesinti oranı ayarlandı.')
                
        elif action == 'payment_method':
            payment_method = request.POST.get('payment_method')
            rate = request.POST.get('rate')
            if payment_method and rate:
                PaymentMethodCommission.objects.update_or_create(
                    payment_method=payment_method,
                    defaults={'rate': rate}
                )
                messages.success(request, f'{payment_method} ödeme yöntemi için %{rate} kesinti oranı ayarlandı.')
                
        elif action == 'delete_session_type':
            commission_id = request.POST.get('commission_id')
            if commission_id:
                commission = get_object_or_404(SessionTypeCommission, id=commission_id)
                commission.delete()
                messages.success(request, f'{commission.session_type} seans türü kesinti oranı silindi.')
                
        elif action == 'delete_payment_method':
            commission_id = request.POST.get('commission_id')
            if commission_id:
                commission = get_object_or_404(PaymentMethodCommission, id=commission_id)
                commission.delete()
                messages.success(request, f'{commission.payment_method} ödeme yöntemi kesinti oranı silindi.')
        
        return redirect('manage_extra_commission')
    
    context = {
        'session_type_commissions': session_type_commissions,
        'payment_method_commissions': payment_method_commissions,
    }
    return render(request, 'manage_extra_commission.html', context)

@login_required
@user_passes_test(is_psychologist)
def my_sessions(request):
    """Psikolog kendi seanslarını görüntüleme"""
    psychologist = request.user.psychologist
    sessions = Session.objects.filter(expert=psychologist).order_by('-date')
    
    # Filtreleme
    status_filter = request.GET.get('status')
    month_filter = request.GET.get('month')
    year_filter = request.GET.get('year')
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    if month_filter:
        sessions = sessions.filter(date__month=int(month_filter))
    if year_filter:
        sessions = sessions.filter(date__year=int(year_filter))
    
    # Ay seçenekleri
    months = [
        (1, 'Ocak'), (2, 'Şubat'), (3, 'Mart'), (4, 'Nisan'),
        (5, 'Mayıs'), (6, 'Haziran'), (7, 'Temmuz'), (8, 'Ağustos'),
        (9, 'Eylül'), (10, 'Ekim'), (11, 'Kasım'), (12, 'Aralık')
    ]
    current_year = timezone.now().year
    years = range(current_year - 2, current_year + 1)
    
    context = {
        'sessions': sessions,
        'months': months,
        'years': years,
    }
    return render(request, 'my_sessions.html', context)

@login_required
@user_passes_test(is_psychologist)
def change_password(request):
    """Psikolog şifre değiştirme"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Şifreniz başarıyla değiştirildi.')
            return redirect('psychologist_dashboard')
        else:
            messages.error(request, 'Şifre değiştirme sırasında hata oluştu.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'change_password.html', context)

@login_required
@user_passes_test(is_admin)
def manage_sessions(request):
    """Admin seans yönetimi"""
    sessions = Session.objects.all().order_by('-date')
    
    # Filtreleme
    status_filter = request.GET.get('status')
    psychologist_filter = request.GET.get('psychologist')
    month_filter = request.GET.get('month')
    year_filter = request.GET.get('year')
    
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    
    if psychologist_filter:
        sessions = sessions.filter(expert_id=psychologist_filter)
    
    if month_filter:
        sessions = sessions.filter(date__month=int(month_filter))
    if year_filter:
        sessions = sessions.filter(date__year=int(year_filter))
    
    psychologists = Psychologist.objects.filter(is_active=True)
    
    # Ay seçenekleri
    months = [
        (1, 'Ocak'), (2, 'Şubat'), (3, 'Mart'), (4, 'Nisan'),
        (5, 'Mayıs'), (6, 'Haziran'), (7, 'Temmuz'), (8, 'Ağustos'),
        (9, 'Eylül'), (10, 'Ekim'), (11, 'Kasım'), (12, 'Aralık')
    ]
    current_year = timezone.now().year
    years = range(current_year - 2, current_year + 1)
    
    context = {
        'sessions': sessions,
        'psychologists': psychologists,
        'months': months,
        'years': years,
    }
    return render(request, 'manage_sessions.html', context)

@login_required
@user_passes_test(is_admin)
def add_session(request):
    """Admin seans ekleme"""
    if request.method == 'POST':
        # Seans ekleme formu işleme
        client_name = request.POST.get('client_name')
        expert_id = request.POST.get('expert')
        date = request.POST.get('date')
        duration = request.POST.get('duration')
        price = request.POST.get('price')
        extra_commission_rate = request.POST.get('extra_commission_rate', '0')
        session_type = request.POST.get('session_type')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        
        # Validasyon
        try:
            expert = Psychologist.objects.get(id=expert_id)
            
            # Süre kontrolü
            if duration:
                try:
                    duration = int(duration)
                except ValueError:
                    messages.error(request, 'Geçersiz süre formatı!')
                    psychologists = Psychologist.objects.filter(is_active=True)
                    return render(request, 'add_session.html', {'psychologists': psychologists})
            
            # Ücret kontrolü
            if price:
                try:
                    price = Decimal(str(price))
                    if price < 0:
                        messages.error(request, 'Ücret negatif olamaz!')
                        psychologists = Psychologist.objects.filter(is_active=True)
                        return render(request, 'add_session.html', {'psychologists': psychologists})
                except (ValueError, InvalidOperation):
                    messages.error(request, 'Geçersiz ücret formatı!')
                    psychologists = Psychologist.objects.filter(is_active=True)
                    return render(request, 'add_session.html', {'psychologists': psychologists})
            
            # Ek kesinti oranı kontrolü
            if extra_commission_rate == '' or extra_commission_rate is None:
                extra_commission_rate = '0'
            try:
                extra_commission_rate = Decimal(str(extra_commission_rate))
            except (ValueError, InvalidOperation):
                extra_commission_rate = Decimal('0')
            
            session = Session.objects.create(
                client_name=client_name,
                expert=expert,
                date=date,
                duration=duration,
                price=price,
                extra_commission_rate=extra_commission_rate,
                session_type=session_type,
                payment_method=payment_method,
                status=status,
                notes=notes
            )
            messages.success(request, f'{client_name} için seans başarıyla eklendi.')
            return redirect('manage_sessions')
        except Exception as e:
            messages.error(request, f'Seans eklenirken hata oluştu: {str(e)}')
    
    psychologists = Psychologist.objects.filter(is_active=True)
    context = {
        'psychologists': psychologists,
    }
    return render(request, 'add_session.html', context)

@login_required
@user_passes_test(is_admin)
def edit_session(request, session_id):
    """Admin seans düzenleme"""
    session = get_object_or_404(Session, id=session_id)
    
    if request.method == 'POST':
        # Seans düzenleme formu işleme
        session.client_name = request.POST.get('client_name')
        session.expert_id = request.POST.get('expert')
        session.date = request.POST.get('date')
        
        # Süre kontrolü
        duration = request.POST.get('duration')
        if duration:
            try:
                session.duration = int(duration)
            except ValueError:
                messages.error(request, 'Geçersiz süre formatı!')
                return redirect('edit_session', session_id=session_id)
        
        # Ücret güvenlik kontrolü
        new_price = request.POST.get('price')
        if new_price:
            try:
                session.price = Decimal(str(new_price))
                if session.price < 0:
                    messages.error(request, 'Ücret negatif olamaz!')
                    return redirect('edit_session', session_id=session_id)
            except (ValueError, InvalidOperation):
                messages.error(request, 'Geçersiz ücret formatı!')
                return redirect('edit_session', session_id=session_id)
        
        # Ek kesinti oranı kontrolü (boş string olabilir)
        extra_commission_rate = request.POST.get('extra_commission_rate', '0')
        if extra_commission_rate == '' or extra_commission_rate is None:
            extra_commission_rate = '0'
        try:
            session.extra_commission_rate = Decimal(str(extra_commission_rate))
        except (ValueError, InvalidOperation):
            session.extra_commission_rate = Decimal('0')
        session.session_type = request.POST.get('session_type')
        session.payment_method = request.POST.get('payment_method')
        session.status = request.POST.get('status')
        session.notes = request.POST.get('notes')
        session.save()
        
        messages.success(request, f'{session.client_name} için seans başarıyla güncellendi.')
        return redirect('manage_sessions')
    
    psychologists = Psychologist.objects.filter(is_active=True)
    # Decimal değerini string'e çevir
    session_price_str = str(session.price) if session.price else "0"
    context = {
        'session': session,
        'session_price_str': session_price_str,
        'psychologists': psychologists,
    }
    return render(request, 'edit_session.html', context)

@login_required
@user_passes_test(is_admin)
def delete_session(request, session_id):
    """Admin seans silme"""
    session = get_object_or_404(Session, id=session_id)
    client_name = session.client_name
    
    if request.method == 'POST':
        session.delete()
        messages.success(request, f'{client_name} için seans başarıyla silindi.')
        return redirect('manage_sessions')
    
    context = {
        'session': session,
    }
    return render(request, 'delete_session.html', context)

@login_required
@user_passes_test(is_admin)
def add_psychologist(request):
    """Admin psikolog ekleme"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone', '')
        hourly_rate = request.POST.get('hourly_rate', 0)
        commission_rate = request.POST.get('commission_rate', 50.00)
        extra_commission_rate = request.POST.get('extra_commission_rate', 0.00)
        
        # Validasyon
        if password1 != password2:
            messages.error(request, 'Şifreler eşleşmiyor.')
            return redirect('manage_psychologists')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu kullanıcı adı zaten kullanılıyor.')
            return redirect('manage_psychologists')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Bu e-posta adresi zaten kullanılıyor.')
            return redirect('manage_psychologists')
        
        try:
            # User oluştur
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password1
            )
            
            # Psychologist oluştur
            Psychologist.objects.create(
                user=user,
                phone=phone,
                hourly_rate=hourly_rate,
                commission_rate=commission_rate,
                extra_commission_rate=extra_commission_rate,
                is_active=True
            )
            
            messages.success(request, f'{first_name} {last_name} başarıyla psikolog olarak eklendi.')
            return redirect('manage_psychologists')
            
        except Exception as e:
            messages.error(request, f'Psikolog eklenirken hata oluştu: {str(e)}')
            return redirect('manage_psychologists')
    
    return redirect('manage_psychologists')

@login_required
@user_passes_test(is_admin)
def edit_psychologist(request, psychologist_id):
    """Admin psikolog düzenleme"""
    psychologist = get_object_or_404(Psychologist, id=psychologist_id)
    user = psychologist.user
    
    if request.method == 'POST':
        # User bilgilerini güncelle
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        # Psikolog bilgilerini güncelle
        psychologist.phone = request.POST.get('phone', psychologist.phone)
        psychologist.hourly_rate = request.POST.get('hourly_rate', psychologist.hourly_rate)
        psychologist.commission_rate = request.POST.get('commission_rate', psychologist.commission_rate)
        psychologist.extra_commission_rate = request.POST.get('extra_commission_rate', psychologist.extra_commission_rate)
        psychologist.is_active = request.POST.get('is_active') == 'on'
        
        # Şifre değiştirme (opsiyonel)
        new_password = request.POST.get('password1')
        if new_password:
            password2 = request.POST.get('password2')
            if new_password == password2:
                user.set_password(new_password)
                messages.success(request, 'Şifre güncellendi.')
            else:
                messages.error(request, 'Şifreler eşleşmiyor.')
                return redirect('edit_psychologist', psychologist_id=psychologist_id)
        
        try:
            user.save()
            psychologist.save()
            messages.success(request, f'{user.get_full_name()} başarıyla güncellendi.')
            return redirect('manage_psychologists')
        except Exception as e:
            messages.error(request, f'Güncelleme sırasında hata oluştu: {str(e)}')
            return redirect('edit_psychologist', psychologist_id=psychologist_id)
    
    context = {
        'psychologist': psychologist,
        'user': user,
    }
    return render(request, 'edit_psychologist.html', context)

@login_required
@user_passes_test(is_admin)
def add_assistant(request):
    """Admin asistan ekleme"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone', '')
        
        # Validasyon
        if password1 != password2:
            messages.error(request, 'Şifreler eşleşmiyor.')
            return redirect('admin_dashboard')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu kullanıcı adı zaten kullanılıyor.')
            return redirect('admin_dashboard')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Bu e-posta adresi zaten kullanılıyor.')
            return redirect('admin_dashboard')
        
        try:
            # User oluştur
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password1
            )
            
            # Assistant oluştur
            Assistant.objects.create(
                user=user,
                phone=phone,
                is_active=True
            )
            
            messages.success(request, f'{first_name} {last_name} başarıyla asistan olarak eklendi.')
            return redirect('admin_dashboard')
            
        except Exception as e:
            messages.error(request, f'Asistan eklenirken hata oluştu: {str(e)}')
            return redirect('admin_dashboard')
    
    return redirect('admin_dashboard')
