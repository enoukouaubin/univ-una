from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime, timedelta, time
import json
import random
import string
import uuid

class CustomClientManager(BaseUserManager):
    def create_user(self, email, nom, prenom, telephone, password=None):
        if not email:
            raise ValueError("L'email est requis.")
        if not telephone:
            raise ValueError("Le téléphone est requis.")
        
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, telephone=telephone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, prenom, telephone, password=None):
        user = self.create_user(email, nom, prenom, telephone, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.statut = 'actif'
        user.save(using=self._db)
        return user

class Client(AbstractBaseUser, PermissionsMixin):
    id_client = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, null=False)
    prenom = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, unique=True, null=False)
    telephone = models.CharField(max_length=15, unique=True, null=False)
    date_inscription = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[('actif', 'Actif'), ('inactif', 'Inactif'), ('bloqué', 'Bloqué')], default='actif')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = CustomClientManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom', 'telephone']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='client_users',
        blank=True,
        help_text='The groups this client belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='client_user_permissions',
        blank=True,
        help_text='Specific permissions for this client.',
        verbose_name='user permissions'
    )

    class Meta:
        db_table = 'client'

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class CustomAdminManager(BaseUserManager):
    def create_user(self, email, nom, prenom, nom_utilisateur, password=None):
        if not email:
            raise ValueError("L'email est requis.")
        if not nom_utilisateur:
            raise ValueError("Le nom d'utilisateur est requis.")
        
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, nom_utilisateur=nom_utilisateur)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, prenom, nom_utilisateur, password=None):
        user = self.create_user(email, nom, prenom, nom_utilisateur, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.statut = 'actif'
        user.role = 'super_admin'
        user.save(using=self._db)
        return user

class Administrateur(AbstractBaseUser, PermissionsMixin):
    id_admin = models.AutoField(primary_key=True)
    nom_utilisateur = models.CharField(max_length=50, unique=True, null=False)
    nom = models.CharField(max_length=100, null=False)
    prenom = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, unique=True, null=False)
    role = models.CharField(max_length=20, choices=[('super_admin', 'Super Admin'), ('admin', 'Admin'), ('operateur', 'Opérateur')], default='operateur')
    dernier_acces = models.DateTimeField(null=True)
    statut = models.CharField(max_length=20, choices=[('active', 'Actif'), ('inactive', 'Inactif')], default='active')
    date_creation = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=True)

    objects = CustomAdminManager()

    USERNAME_FIELD = 'nom_utilisateur'
    REQUIRED_FIELDS = ['email', 'nom', 'prenom']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='admin_users',
        blank=True,
        help_text='The groups this admin belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='admin_user_permissions',
        blank=True,
        help_text='Specific permissions for this admin.',
        verbose_name='user permissions'
    )

    class Meta:
        db_table = 'administrateur'

    def __str__(self):
        return self.nom_utilisateur

class Ville(models.Model):
    id_ville = models.AutoField(primary_key=True)
    nom_ville = models.CharField(max_length=100, unique=True, null=False)
    statut = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    class Meta:
        db_table = 'ville'

    def __str__(self):
        return self.nom_ville

class Gare(models.Model):
    id_gare = models.AutoField(primary_key=True)
    nom_gare = models.CharField(max_length=100, null=False)
    adresse = models.TextField(null=False)
    telephone = models.CharField(max_length=20, null=True)
    id_ville = models.ForeignKey(Ville, on_delete=models.CASCADE, db_column='id_ville')
    statut = models.CharField(max_length=20, choices=[('active', 'Actif'), ('inactive', 'Inactif')], default='active')

    class Meta:
        db_table = 'gare'

    def __str__(self):
        return self.nom_gare

class Car(models.Model):
    id_car = models.AutoField(primary_key=True)
    numero_immatriculation = models.CharField(max_length=20, unique=True, null=False)
    nombre_places = models.IntegerField(null=False, validators=[MinValueValidator(1)])
    type_car = models.CharField(max_length=20, choices=[('VIP', 'VIP'), ('Ordinaire', 'Ordinaire'), ('Climatisé', 'Climatisé')], default='Ordinaire')
    statut = models.CharField(max_length=20, choices=[('actif', 'Actif'), ('maintenance', 'Maintenance'), ('hors_service', 'Hors Service')], default='actif')

    class Meta:
        db_table = 'car'

    def __str__(self):
        return self.numero_immatriculation

class Chauffeur(models.Model):
    id_chauffeur = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, null=False)
    prenom = models.CharField(max_length=100, null=False)
    telephone = models.CharField(max_length=20, unique=True, null=False)
    statut = models.CharField(max_length=20, choices=[('actif', 'Actif'), ('congé', 'Congé'), ('suspendu', 'Suspendu')], default='actif')
    date_embauche = models.DateField(null=True)

    class Meta:
        db_table = 'chauffeur'

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Ligne(models.Model):
    id_ligne = models.AutoField(primary_key=True)
    ville_depart = models.ForeignKey(Ville, related_name='lignes_depart', on_delete=models.CASCADE, db_column='ville_depart')
    ville_arrivee = models.ForeignKey(Ville, related_name='lignes_arrivee', on_delete=models.CASCADE, db_column='ville_arrivee')
    gare_depart = models.ForeignKey(Gare, related_name='lignes_depart', on_delete=models.CASCADE, db_column='gare_depart')
    gare_arrivee = models.ForeignKey(Gare, related_name='lignes_arrivee', on_delete=models.CASCADE, db_column='gare_arrivee')
    distance_km = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    duree_trajet = models.TimeField(null=True)
    prix_standard = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    prix_vip = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    statut = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('suspendue', 'Suspendue')], default='active')

    class Meta:
        db_table = 'ligne'

    def __str__(self):
        return f"{self.ville_depart.nom_ville} -> {self.ville_arrivee.nom_ville}"

class Voyage(models.Model):
    id_voyage = models.AutoField(primary_key=True)
    id_ligne = models.ForeignKey(Ligne, on_delete=models.CASCADE, db_column='id_ligne')
    id_car = models.ForeignKey(Car, on_delete=models.CASCADE, db_column='id_car')
    id_chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE, db_column='id_chauffeur')
    date_voyage = models.DateField(null=False)
    heure_depart = models.TimeField(null=False)
    heure_arrivee_prevue = models.TimeField(null=False)
    places_disponibles = models.IntegerField(null=False, validators=[MinValueValidator(0)])
    statut = models.CharField(max_length=20, choices=[('programmé', 'Programmé'), ('en_cours', 'En Cours'), ('terminé', 'Terminé'), ('annulé', 'Annulé'), ('reporté', 'Reporté')], default='programmé')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'voyage'

    def __str__(self):
        return f"Voyage {self.id_voyage} - {self.id_ligne}"

    def save(self, *args, **kwargs):
        # Set places_disponibles to car's nombre_places if not set
        if not self.places_disponibles and self.id_car:
            self.places_disponibles = self.id_car.nombre_places
        super().save(*args, **kwargs)

class Reservation(models.Model):
    id_reservation = models.AutoField(primary_key=True)
    numero_reservation = models.CharField(max_length=15, unique=True, null=False, blank=False)
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='id_client')
    id_voyage = models.ForeignKey(Voyage, on_delete=models.CASCADE, db_column='id_voyage')
    nombre_places = models.IntegerField(null=False, default=1, validators=[MinValueValidator(1)])
    noms_passagers = models.TextField(null=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    date_reservation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[('en_attente', 'En Attente'), ('confirmée', 'Confirmée'), ('payée', 'Payée'), ('annulée', 'Annulée'), ('utilisée', 'Utilisée')], default='en_attente')
    date_expiration = models.DateTimeField(null=True)

    class Meta:
        db_table = 'reservation'

    def get_noms_passagers(self):
        if self.noms_passagers:
            return json.loads(self.noms_passagers)
        return []

    def set_noms_passagers(self, noms_list):
        self.noms_passagers = json.dumps(noms_list) if noms_list else None

    def __str__(self):
        return self.numero_reservation

    def save(self, *args, **kwargs):
        if not self.numero_reservation:
            def generate_reservation_number():
                return 'RES' + ''.join(random.choices(string.digits, k=8))
            self.numero_reservation = generate_reservation_number()
            while Reservation.objects.filter(numero_reservation=self.numero_reservation).exists():
                self.numero_reservation = generate_reservation_number()
        super().save(*args, **kwargs)

    def cancel(self):
        """Annuler la réservation et restaurer les places disponibles."""
        with transaction.atomic():
            if self.statut not in ['annulée', 'utilisée']:
                voyage_date = datetime.combine(self.id_voyage.date_voyage, self.id_voyage.heure_depart)
                voyage_date_time = timezone.make_aware(voyage_date, timezone.get_current_timezone())
                if timezone.now() > voyage_date_time - timedelta(hours=5):
                    raise ValueError("Vous ne pouvez pas annuler votre réservation moins de 5 heures avant le départ.")
                self.statut = 'annulée'
                self.id_voyage.places_disponibles += self.nombre_places
                self.id_voyage.save()
                self.save()
                Ticket.objects.filter(id_reservation=self).update(statut='annulé')
            else:
                raise ValueError("La réservation est déjà annulée ou utilisée.")

    @classmethod
    def filter_by_day(cls, date):
        """Filter reservations sur une date spécifique."""
        start_of_day = datetime.combine(date, time(hour=0, minute=0, second=0))
        end_of_day = datetime.combine(date, time(hour=23, minute=59, second=59))
        return cls.objects.filter(date_reservation__range=(start_of_day, end_of_day))

    @classmethod
    def filter_by_week(cls, start_date):
        """Filter reservations sur une semaine spécifique."""
        start_of_week_date = start_date - timedelta(days=start_date.weekday())
        end_of_week_date = start_of_week_date + timedelta(days=6)
        start_of_week = datetime.combine(start_of_week_date, time(hour=0, minute=0, second=0))
        end_of_week = datetime.combine(end_of_week_date, time(hour=23, minute=59, second=59))
        return cls.objects.filter(date_reservation__range=(start_of_week, end_of_week))

class Ticket(models.Model):
    id_ticket = models.AutoField(primary_key=True)
    numero_ticket = models.CharField(max_length=20, unique=True, null=False, blank=True)
    id_reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, db_column='id_reservation')
    nom_passager = models.CharField(max_length=150, null=False)
    numero_place = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    type_place = models.CharField(max_length=20, choices=[('standard', 'Standard'), ('vip', 'VIP')], default='standard')
    date_emission = models.DateTimeField(auto_now_add=True)
    date_utilisation = models.DateTimeField(null=True)
    statut = models.CharField(max_length=20, choices=[('émis', 'Émis'), ('validé', 'Validé'), ('utilisé', 'Utilisé'), ('annulé', 'Annulé')], default='émis')

    class Meta:
        db_table = 'ticket'

    def __str__(self):
        return self.numero_ticket

    def save(self, *args, **kwargs):
        if not self.numero_ticket:
            def generate_ticket_number():
                return 'TCK' + ''.join(random.choices(string.digits, k=10))
            self.numero_ticket = generate_ticket_number()
            while Ticket.objects.filter(numero_ticket=self.numero_ticket).exists():
                self.numero_ticket = generate_ticket_number()
        super().save(*args, **kwargs)

    @classmethod
    def filter_by_day(cls, date):
        """Filter tickets émis sur une date spécifique."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        return cls.objects.filter(date_emission__range=(start_of_day, end_of_day))

    @classmethod
    def filter_by_week(cls, start_date):
        """Filter tickets émis sur une semaine spécifique."""
        start_of_week = start_date - timedelta(days=start_date.weekday())
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
        return cls.objects.filter(date_emission__range=(start_of_week, end_of_week))