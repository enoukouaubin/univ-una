from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import json

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
    telephone = models.CharField(max_length=20, unique=True, null=False)
    date_inscription = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=[('actif', 'Actif'), ('inactif', 'Inactif'), ('bloqué', 'Bloqué')],
        default='actif'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = CustomClientManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom', 'telephone']

    class Meta:
        db_table = 'client'

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Ville(models.Model):
    id_ville = models.AutoField(primary_key=True)
    nom_ville = models.CharField(max_length=100, unique=True, null=False)
    statut = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        default='active'
    )

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
    statut = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        default='active'
    )

    class Meta:
        db_table = 'gare'

    def __str__(self):
        return self.nom_gare

class Car(models.Model):
    id_car = models.AutoField(primary_key=True)
    numero_immatriculation = models.CharField(max_length=20, unique=True, null=False)
    nombre_places = models.IntegerField(null=False)
    type_car = models.CharField(
        max_length=20,
        choices=[('VIP', 'VIP'), ('Ordinaire', 'Ordinaire'), ('Climatisé', 'Climatisé')],
        default='Ordinaire'
    )
    statut = models.CharField(
        max_length=20,
        choices=[('actif', 'Actif'), ('maintenance', 'Maintenance'), ('hors_service', 'Hors Service')],
        default='actif'
    )

    class Meta:
        db_table = 'car'

    def __str__(self):
        return self.numero_immatriculation

class Chauffeur(models.Model):
    id_chauffeur = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, null=False)
    prenom = models.CharField(max_length=100, null=False)
    telephone = models.CharField(max_length=20, unique=True, null=False)
    statut = models.CharField(
        max_length=20,
        choices=[('actif', 'Actif'), ('congé', 'Congé'), ('suspendu', 'Suspendu')],
        default='actif'
    )
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
    statut = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('inactive', 'Inactive'), ('suspendue', 'Suspendue')],
        default='active'
    )

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
    prix_voyage = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    places_disponibles = models.IntegerField(null=False)
    statut = models.CharField(
        max_length=20,
        choices=[('programmé', 'Programmé'), ('en_cours', 'En Cours'), ('terminé', 'Terminé'), ('annulé', 'Annulé'), ('reporté', 'Reporté')],
        default='programmé'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'voyage'

    def __str__(self):
        return f"Voyage {self.id_voyage} - {self.id_ligne}"

class Reservation(models.Model):
    id_reservation = models.AutoField(primary_key=True)
    numero_reservation = models.CharField(max_length=15, unique=True, null=False)
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='id_client')
    id_voyage = models.ForeignKey(Voyage, on_delete=models.CASCADE, db_column='id_voyage')
    nombre_places = models.IntegerField(null=False, default=1)
    noms_passagers = models.TextField(null=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    date_reservation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=[('en_attente', 'En Attente'), ('confirmée', 'Confirmée'), ('payée', 'Payée'), ('annulée', 'Annulée'), ('utilisée', 'Utilisée')],
        default='en_attente'
    )
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

class Ticket(models.Model):
    id_ticket = models.AutoField(primary_key=True)
    numero_ticket = models.CharField(max_length=20, unique=True, null=False)
    id_reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, db_column='id_reservation')
    nom_passager = models.CharField(max_length=150, null=False)
    numero_place = models.IntegerField(null=True)
    type_place = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('vip', 'VIP')],
        default='standard'
    )
    date_emission = models.DateTimeField(auto_now_add=True)
    date_utilisation = models.DateTimeField(null=True)
    statut = models.CharField(
        max_length=20,
        choices=[('émis', 'Émis'), ('validé', 'Validé'), ('utilisé', 'Utilisé'), ('annulé', 'Annulé')],
        default='émis'
    )

    class Meta:
        db_table = 'ticket'

    def __str__(self):
        return self.numero_ticket

class Administrateur(models.Model):
    id_admin = models.AutoField(primary_key=True)
    nom_utilisateur = models.CharField(max_length=50, unique=True, null=False)
    nom = models.CharField(max_length=100, null=False)
    prenom = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, unique=True, null=False)
    mot_de_passe = models.CharField(max_length=255, null=False)
    role = models.CharField(
        max_length=20,
        choices=[('super_admin', 'Super Admin'), ('admin', 'Admin'), ('operateur', 'Opérateur')],
        default='operateur'
    )
    dernier_acces = models.DateTimeField(null=True)
    statut = models.CharField(
        max_length=20,
        choices=[('actif', 'Actif'), ('inactif', 'Inactif')],
        default='actif'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'administrateur'

    def __str__(self):
        return self.nom_utilisateur