from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Voyage, Ligne, Reservation, Ticket, Client
from .forms import SearchTripForm, ReservationForm, ClientRegistrationForm, ClientLoginForm
from .utils import generate_reservation_number, generate_ticket_number
from .decorators import admin_required
from datetime import datetime, timedelta
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import qrcode
import io

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def home(request):
    reservations = []
    if request.user.is_authenticated:
        reservations = Reservation.objects.filter(id_client=request.user)
    return render(request, 'reservations/home.html', {'reservations': reservations})

def search_trips(request):
    form = SearchTripForm(request.GET or None)
    voyages = []
    if form.is_valid():
        ville_depart = form.cleaned_data['ville_depart']
        ville_arrivee = form.cleaned_data['ville_arrivee']
        date_voyage = form.cleaned_data['date_voyage']
        voyages = Voyage.objects.filter(
            id_ligne__ville_depart=ville_depart,
            id_ligne__ville_arrivee=ville_arrivee,
            date_voyage=date_voyage,
            statut='programmé',
            places_disponibles__gt=0
        )
        if voyages.exists():
            messages.success(request, "Voyages trouvés ! Voici les résultats.")
        else:
            messages.warning(request, "Aucun trajet trouvé pour ces critères.")
    return render(request, 'reservations/search_trips.html', {'form': form, 'voyages': voyages})

@login_required
def make_reservation(request, voyage_id):
    try:
        voyage = Voyage.objects.get(id_voyage=voyage_id)
    except Voyage.DoesNotExist:
        messages.error(request, "Le voyage spécifié n'existe pas.")
        return redirect('reservations:home')
    
    form = ReservationForm(request.POST or None, initial={'voyage_id': voyage_id})
    if form.is_valid():
        nombre_places = form.cleaned_data['nombre_places']
        noms_passagers = form.cleaned_data['noms_passagers'].splitlines()
        type_place = form.cleaned_data['type_place']
        
        if nombre_places > voyage.places_disponibles:
            messages.error(request, "Pas assez de places disponibles.")
            return render(request, 'reservations/reservation_form.html', {'form': form, 'voyage': voyage})
        
        # Validate number of passenger names
        if len(noms_passagers) != nombre_places:
            messages.error(request, f"Vous devez fournir exactement {nombre_places} nom(s) de passager(s).")
            return render(request, 'reservations/reservation_form.html', {'form': form, 'voyage': voyage})
        
        prix_unitaire = voyage.id_ligne.prix_vip if type_place == 'vip' and voyage.id_ligne.prix_vip else voyage.id_ligne.prix_standard
        prix_total = prix_unitaire * nombre_places
        
        reservation = Reservation.objects.create(
            id_client=request.user,
            numero_reservation=generate_reservation_number(),  
            id_voyage=voyage,
            nombre_places=nombre_places,
            prix_unitaire=prix_unitaire,
            prix_total=prix_total,
            date_expiration=datetime.now() + timedelta(minutes=30),
            statut='en_attente'
        )
        reservation.set_noms_passagers(noms_passagers if noms_passagers else None)
        reservation.save()
        
        for i, nom_passager in enumerate(noms_passagers, start=1):
            Ticket.objects.create(
                id_reservation=reservation,
                nom_passager=nom_passager or f"Passager {i}",
                numero_place=None,
                type_place=type_place
            )
        
        voyage.places_disponibles -= nombre_places
        voyage.save()
        
        messages.success(request, "Réservation effectuée avec succès.")
        return redirect('reservations:home')
    
    return render(request, 'reservations/reservation_form.html', {'form': form, 'voyage': voyage})

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(id_client=request.user, statut__in=['en_attente', 'confirmée', 'payée']).order_by('-date_reservation')
    return render(request, 'reservations/my_reservations.html', {'reservations': reservations})

@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id_reservation=reservation_id, id_client=request.user)
    if request.method == 'POST':
        try:
            reservation.cancel()
            messages.success(request, f"Réservation {reservation.numero_reservation} annulée avec succès.")
            return redirect('reservations:my_reservations')
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'reservations/confirm_cancel.html', {'reservation': reservation})
    return render(request, 'reservations/confirm_cancel.html', {'reservation': reservation})

def client_register(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = Client.objects.create_user(
                email=form.cleaned_data['email'],
                nom=form.cleaned_data['nom'],
                prenom=form.cleaned_data['prenom'],
                telephone=form.cleaned_data['telephone'],
                password=form.cleaned_data['password']
            )
            user.save()
            messages.success(request, "Inscription réussie. Veuillez vous connecter.")
            return redirect('reservations:login')
    else:
        form = ClientRegistrationForm()
    return render(request, 'reservations/login.html', {'form': form, 'form_type': 'register'})

def client_login(request):
    if request.method == 'POST':
        form = ClientLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue, {user.prenom} {user.nom} !")
                return redirect('reservations:home')
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = ClientLoginForm()
    return render(request, 'reservations/login.html', {'form': form, 'form_type': 'login'})
    
def client_logout(request):
    logout(request)
    messages.success(request, "Vous êtes déconnecté.")
    return redirect('reservations:home')

@login_required
def view_ticket(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id_ticket=ticket_id, id_reservation__id_client=request.user)
        reservation = ticket.id_reservation
        voyage = reservation.id_voyage
        return render(request, 'reservations/view_ticket.html', {
            'ticket': ticket,
            'reservation': reservation,
            'voyage': voyage,
        })
    except Ticket.DoesNotExist:
        messages.error(request, "Ticket non trouvé ou vous n'êtes pas autorisé à y accéder.")
        return redirect('reservations:home')

@login_required
def download_ticket_receipt(request, ticket_id):
    logger.debug(f"Attempting to download ticket receipt for ticket_id: {ticket_id}")
    try:
        ticket = Ticket.objects.get(id_ticket=ticket_id, id_reservation__id_client=request.user)
        reservation = ticket.id_reservation
        voyage = reservation.id_voyage
        client = reservation.id_client
        logger.debug(f"Ticket found: {ticket.numero_ticket}, Reservation: {reservation.numero_reservation}")

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.numero_ticket}.pdf"'

        # Initialize PDF document
        doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name='Title',
            fontSize=24,
            leading=28,
            alignment=1,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#003087')  # Bleu foncé
        )
        ticket_number_style = ParagraphStyle(
            name='TicketNumber',
            fontSize=18,
            leading=22,
            alignment=1,
            spaceAfter=5,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#007bff')
        )
        subtitle_style = ParagraphStyle(
            name='Subtitle',
            fontSize=14,
            leading=18,
            alignment=0,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#343a40')
        )
        normal_style = ParagraphStyle(
            name='Normal',
            fontSize=10,
            leading=12,
            alignment=0,
            spaceAfter=5,
            fontName='Helvetica',
            textColor=colors.HexColor('#343a40')
        )

        # QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(f"https://kea.trans.com/verify-ticket/{ticket.numero_ticket}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        # Header
        elements.append(Paragraph("Trans - Reçu de Ticket", title_style))
        elements.append(Paragraph(f"Ticket N° {ticket.numero_ticket}", ticket_number_style))
        elements.append(Paragraph(f"Émis le : {datetime.now().strftime('%d/%m/%Y')}", normal_style))
        elements.append(Table([['']], colWidths=[A4[0] - 4*cm], style=[
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#007bff'))
        ]))
        elements.append(Spacer(1, 0.75*cm))

        # Two-column layout
        left_column = []
        right_column = []

        # Left Column: Reservation + Client Details
        left_column.append(Paragraph("Informations Client & Réservation", subtitle_style))
        reservation_data = [
            ['Numéro de Réservation', reservation.numero_reservation],
            ['Client', f"{client.prenom} {client.nom}"],
            ['Email', client.email],
            ['Téléphone', client.telephone]
        ]
        reservation_table = Table(reservation_data, colWidths=[5.5*cm, 10*cm])
        reservation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#343a40')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#007bff')),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        left_column.append(reservation_table)

        # Right Column: Voyage + Passagers
        right_column.append(Paragraph("Détails du Voyage", subtitle_style))
        voyage_data = [
            ['Ville de Départ', voyage.id_ligne.ville_depart.nom_ville],
            ['Ville d\'Arrivée', voyage.id_ligne.ville_arrivee.nom_ville],
            ['Date du Voyage', voyage.date_voyage.strftime('%d/%m/%Y')],
            ['Heure de Départ', voyage.heure_depart.strftime('%H:%M')],
            ['Heure d\'Arrivée', voyage.heure_arrivee_prevue.strftime('%H:%M')],
            ['Type de Place', ticket.type_place.title()]
        ]
        voyage_table = Table(voyage_data, colWidths=[5.5*cm, 10*cm])
        voyage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#343a40')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#007bff')),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        right_column.append(voyage_table)
        right_column.append(Spacer(1, 0.5*cm))

        right_column.append(Paragraph("Passagers", subtitle_style))
        passenger_list = reservation.get_noms_passagers()
        passenger_data = [['#', 'Nom']] + [[str(i+1), name] for i, name in enumerate(passenger_list)]
        passenger_table = Table(passenger_data, colWidths=[2.5*cm, 13*cm])
        passenger_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003087')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#343a40')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#007bff')),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        right_column.append(passenger_table)

        # Combine columns
        columns_table = Table([
            [left_column, right_column]
        ], colWidths=[(A4[0] - 1*cm)/2, (A4[0] - 8*cm)/2], style=[
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ])
        elements.append(columns_table)
        elements.append(Spacer(1, 0.75*cm))

        # Financial and Status
        elements.append(Paragraph("Détails Financiers & Statut", subtitle_style))
        financial_status_data = [
            ['Prix Unitaire', f"{reservation.prix_unitaire:.2f} F CFA", 'Statut du Ticket', ticket.statut.title()],
            ['Prix Total', f"{reservation.prix_total:.2f} F CFA", 'Date d\'Émission', ticket.date_emission.strftime('%d/%m/%Y %H:%M')]
        ]
        financial_status_table = Table(financial_status_data, colWidths=[5.5*cm, 5*cm, 5.5*cm, 5*cm])
        financial_status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, -1), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (2, 0), (3, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#343a40')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#007bff')),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(financial_status_table)
        elements.append(Spacer(1, 0.75*cm))

        # QR Code
        elements.append(Paragraph("Vérification du Ticket", subtitle_style))
        qr_table = Table([[Paragraph("Scannez pour vérifier", normal_style), Image(qr_buffer, 2*cm, 2*cm)]], colWidths=[13*cm, 2.5*cm])
        qr_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(qr_table)
        elements.append(Spacer(1, 1*cm))

        # Footer
        elements.append(Table([['']], colWidths=[A4[0] - 4*cm], style=[
            ('LINEABOVE', (0, 0), (-1, -1), 2, colors.HexColor('#007bff'))
        ]))
        elements.append(Paragraph("Merci d'avoir choisi Trans pour votre voyage !", normal_style))
        elements.append(Paragraph("Trans, 123 Avenue du Voyage, Daoukro, Côte d'Ivoire | support@trans.com | kea.trans.com", normal_style))

        # Build PDF
        doc.build(elements)
        logger.debug(f"PDF generated for ticket: {ticket.numero_ticket}")
        return response

    except Ticket.DoesNotExist:
        logger.error(f"Ticket with id {ticket_id} not found or not authorized")
        messages.error(request, "Ticket non trouvé ou vous n'êtes pas autorisé à y accéder.")
        return redirect('reservations:home')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        messages.error(request, f"Une erreur s'est produite : {str(e)}")
        return redirect('reservations:home')

@admin_required
@login_required
def admin_reservations_by_day(request):
    try:
        selected_date = datetime.now().date()
        if request.GET.get('date'):
            try:
                selected_date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Format de date invalide. Utilisez AAAA-MM-JJ.")
        
        reservations = Reservation.filter_by_day(selected_date)
        context = {
            'reservations': reservations,
            'selected_date': selected_date,
            'title': f"Réservations du {selected_date.strftime('%d/%m/%Y')}"
        }
        return render(request, 'reservations/admin_reservations_by_day.html', context)
    except Exception as e:
        logger.error(f"Error in admin_reservations_by_day: {str(e)}")
        messages.error(request, "Une erreur s'est produite lors du chargement des réservations.")
        return redirect('reservations:home')

@admin_required
@login_required
def admin_reservations_by_week(request):
    try:
        selected_date = datetime.now().date()
        if request.GET.get('week_start'):
            try:
                selected_date = datetime.strptime(request.GET.get('week_start'), '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Format de date invalide pour le début de la semaine. Utilisez AAAA-MM-JJ.")

        start_of_week = selected_date - timedelta(days=selected_date.weekday())
        reservations = Reservation.filter_by_week(start_of_week)
        context = {
            'reservations': reservations,
            'selected_date': selected_date,
            'start_of_week': start_of_week,
            'end_of_week': start_of_week + timedelta(days=6),
            'title': f"Réservations de la semaine du {start_of_week.strftime('%d/%m/%Y')} au {(start_of_week + timedelta(days=6)).strftime('%d/%m/%Y')}"
        }
        return render(request, 'reservations/admin_reservations_by_week.html', context)
    except Exception as e:
        logger.error(f"Error in admin_reservations_by_week: {str(e)}")
        messages.error(request, "Une erreur s'est produite lors du chargement des réservations.")
        return redirect('reservations:home')