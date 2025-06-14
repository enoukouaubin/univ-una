from django.contrib import admin
from reservations.models import Reservation, Client, Ville, Gare, Car, Chauffeur, Ligne, Voyage, Ticket, Administrateur
from django import forms
from datetime import datetime, timedelta, time
from django.urls import path
from django.http import JsonResponse

# Formulaire pour Voyage
class VoyageAdminForm(forms.ModelForm):
    class Meta:
        model = Voyage
        fields = '__all__'
        widgets = {
            'heure_arrivee_prevue': forms.DateTimeInput(
                attrs={
                    'readonly': 'readonly',
                    'style': 'background-color: #f0f0f0;',
                    'title': 'Calculé automatiquement selon la ligne et l\'heure de départ'
                }
            ),
            'places_disponibles': forms.NumberInput(
                attrs={
                    'readonly': 'readonly',
                    'style': 'background-color: #f0f0f0;',
                    'title': 'Défini automatiquement selon le car sélectionné'
                }
            )
        }

    class Media:
        js = ('js/voyage_admin.js',)

class VoyageAdmin(admin.ModelAdmin):
    form = VoyageAdminForm
    list_display = ('id_voyage', 'id_car', 'id_ligne', 'heure_depart', 'heure_arrivee_prevue', 'places_disponibles', 'statut')
    list_filter = ('date_voyage', 'id_car', 'id_ligne', 'statut')
    search_fields = ('id_car__numero_immatriculation', 'id_ligne__ville_depart__nom_ville', 'id_ligne__ville_arrivee__nom_ville')
    
    fieldsets = (
        ('Informations du voyage', {
            'fields': ('id_ligne', 'id_car', 'id_chauffeur', 'date_voyage')
        }),
        ('Horaires', {
            'fields': ('heure_depart', 'heure_arrivee_prevue'),
            'description': 'L\'heure d\'arrivée se calcule automatiquement selon la durée de la ligne.'
        }),
        ('Capacité et statut', {
            'fields': ('places_disponibles', 'statut'),
            'description': 'Les places disponibles correspondent au nombre de places du car sélectionné.'
        }),
    )

    # Ajouter des URLs pour les requêtes AJAX
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get_car_details/<int:car_id>/', self.admin_site.admin_view(self.get_car_details), name='get_car_details'),
            path('get_ligne_details/<int:ligne_id>/', self.admin_site.admin_view(self.get_ligne_details), name='get_ligne_details'),
        ]
        return custom_urls + urls

    # Endpoint pour récupérer les détails du car (nombre de places)
    def get_car_details(self, request, car_id):
        try:
            car = Car.objects.get(id_car=car_id)
            return JsonResponse({'nombre_places': car.nombre_places})
        except Car.DoesNotExist:
            return JsonResponse({'error': 'Car not found'}, status=404)

    # Endpoint pour récupérer les détails de la ligne (durée)
    def get_ligne_details(self, request, ligne_id):
        try:
            ligne = Ligne.objects.get(id_ligne=ligne_id)
            if ligne.duree_trajet:
                # Convertir TimeField (duree_trajet) en minutes pour le calcul
                duree_minutes = ligne.duree_trajet.hour * 60 + ligne.duree_trajet.minute
                return JsonResponse({'duree_minutes': duree_minutes})
            else:
                return JsonResponse({'error': 'Durée de trajet non définie pour cette ligne'}, status=400)
        except Ligne.DoesNotExist:
            return JsonResponse({'error': 'Ligne not found'}, status=404)

    def save_model(self, request, obj, form, change):
        # Auto-calculer les places disponibles si un car est sélectionné
        if obj.id_car and (not change or not obj.places_disponibles):
            obj.places_disponibles = obj.id_car.nombre_places
        
        # Auto-calculer l'heure d'arrivée prévue
        if obj.id_ligne and obj.date_voyage and obj.heure_depart and obj.id_ligne.duree_trajet:
            # Combiner date et heure de départ
            depart_datetime = datetime.combine(obj.date_voyage, obj.heure_depart)
            
            # Calculer la durée en minutes
            duree_trajet = obj.id_ligne.duree_trajet
            duree_minutes = duree_trajet.hour * 60 + duree_trajet.minute
            
            # Calculer l'heure d'arrivée prévue
            obj.heure_arrivee_prevue = depart_datetime + timedelta(minutes=duree_minutes)
        
        super().save_model(request, obj, form, change)

# Formulaire pour les filtres de réservation (inchangé)
class ReservationFilterForm(forms.Form):
    date = forms.DateField(
        label="Filtrer par jour",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.now().date
    )
    week_start = forms.DateField(
        label="Filtrer par semaine",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.now().date() - timedelta(days=datetime.now().weekday())
    )

class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'numero_reservation',
        'id_client',
        'id_voyage',
        'nombre_places',
        'prix_total',
        'statut',
        'date_reservation',
    )
    list_filter = ('statut', 'date_reservation')
    search_fields = ('numero_reservation', 'id_client__email', 'id_client__nom')
    ordering = ('-date_reservation',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if 'date' in request.GET:
            try:
                selected_date = datetime.strptime(request.GET['date'], '%Y-%m-%d').date()
                queryset = Reservation.filter_by_day(selected_date)
            except ValueError:
                pass
        elif 'week_start' in request.GET:
            try:
                selected_date = datetime.strptime(request.GET['week_start'], '%Y-%m-%d').date()
                queryset = Reservation.filter_by_week(selected_date)
            except ValueError:
                pass
        return queryset

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['filter_form'] = ReservationFilterForm(request.GET or None)
        return super().changelist_view(request, extra_context=extra_context)

# Enregistrer les modèles
admin.site.register(Client)
admin.site.register(Ville)
admin.site.register(Gare)
admin.site.register(Car)
admin.site.register(Chauffeur)
admin.site.register(Ligne)
admin.site.register(Voyage, VoyageAdmin)  # Utiliser VoyageAdmin
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Ticket)
admin.site.register(Administrateur)