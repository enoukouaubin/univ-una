# Generated by Django 5.2.1 on 2025-06-09 10:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Administrateur',
            fields=[
                ('id_admin', models.AutoField(primary_key=True, serialize=False)),
                ('nom_utilisateur', models.CharField(max_length=50, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('mot_de_passe', models.CharField(max_length=255)),
                ('role', models.CharField(choices=[('super_admin', 'Super Admin'), ('admin', 'Admin'), ('operateur', 'Opérateur')], default='operateur', max_length=20)),
                ('dernier_acces', models.DateTimeField(null=True)),
                ('statut', models.CharField(choices=[('actif', 'Actif'), ('inactif', 'Inactif')], default='actif', max_length=20)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'administrateur',
            },
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id_car', models.AutoField(primary_key=True, serialize=False)),
                ('numero_immatriculation', models.CharField(max_length=20, unique=True)),
                ('nombre_places', models.IntegerField()),
                ('type_car', models.CharField(choices=[('VIP', 'VIP'), ('Ordinaire', 'Ordinaire'), ('Climatisé', 'Climatisé')], default='Ordinaire', max_length=20)),
                ('statut', models.CharField(choices=[('actif', 'Actif'), ('maintenance', 'Maintenance'), ('hors_service', 'Hors Service')], default='actif', max_length=20)),
            ],
            options={
                'db_table': 'car',
            },
        ),
        migrations.CreateModel(
            name='Chauffeur',
            fields=[
                ('id_chauffeur', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('telephone', models.CharField(max_length=20, unique=True)),
                ('statut', models.CharField(choices=[('actif', 'Actif'), ('congé', 'Congé'), ('suspendu', 'Suspendu')], default='actif', max_length=20)),
                ('date_embauche', models.DateField(null=True)),
            ],
            options={
                'db_table': 'chauffeur',
            },
        ),
        migrations.CreateModel(
            name='Gare',
            fields=[
                ('id_gare', models.AutoField(primary_key=True, serialize=False)),
                ('nom_gare', models.CharField(max_length=100)),
                ('adresse', models.TextField()),
                ('telephone', models.CharField(max_length=20, null=True)),
                ('statut', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
            ],
            options={
                'db_table': 'gare',
            },
        ),
        migrations.CreateModel(
            name='Ville',
            fields=[
                ('id_ville', models.AutoField(primary_key=True, serialize=False)),
                ('nom_ville', models.CharField(max_length=100, unique=True)),
                ('statut', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
            ],
            options={
                'db_table': 'ville',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id_client', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('telephone', models.CharField(max_length=20, unique=True)),
                ('date_inscription', models.DateTimeField(auto_now_add=True)),
                ('statut', models.CharField(choices=[('actif', 'Actif'), ('inactif', 'Inactif'), ('bloqué', 'Bloqué')], default='actif', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'client',
            },
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id_reservation', models.AutoField(primary_key=True, serialize=False)),
                ('numero_reservation', models.CharField(max_length=15, unique=True)),
                ('nombre_places', models.IntegerField(default=1)),
                ('noms_passagers', models.TextField(null=True)),
                ('prix_unitaire', models.DecimalField(decimal_places=2, max_digits=10)),
                ('prix_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_reservation', models.DateTimeField(auto_now_add=True)),
                ('statut', models.CharField(choices=[('en_attente', 'En Attente'), ('confirmée', 'Confirmée'), ('payée', 'Payée'), ('annulée', 'Annulée'), ('utilisée', 'Utilisée')], default='en_attente', max_length=20)),
                ('date_expiration', models.DateTimeField(null=True)),
                ('id_client', models.ForeignKey(db_column='id_client', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'reservation',
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id_ticket', models.AutoField(primary_key=True, serialize=False)),
                ('numero_ticket', models.CharField(max_length=20, unique=True)),
                ('nom_passager', models.CharField(max_length=150)),
                ('numero_place', models.IntegerField(null=True)),
                ('type_place', models.CharField(choices=[('standard', 'Standard'), ('vip', 'VIP')], default='standard', max_length=20)),
                ('date_emission', models.DateTimeField(auto_now_add=True)),
                ('date_utilisation', models.DateTimeField(null=True)),
                ('statut', models.CharField(choices=[('émis', 'Émis'), ('validé', 'Validé'), ('utilisé', 'Utilisé'), ('annulé', 'Annulé')], default='émis', max_length=20)),
                ('id_reservation', models.ForeignKey(db_column='id_reservation', on_delete=django.db.models.deletion.CASCADE, to='reservations.reservation')),
            ],
            options={
                'db_table': 'ticket',
            },
        ),
        migrations.CreateModel(
            name='Ligne',
            fields=[
                ('id_ligne', models.AutoField(primary_key=True, serialize=False)),
                ('distance_km', models.DecimalField(decimal_places=2, max_digits=7, null=True)),
                ('duree_trajet', models.TimeField(null=True)),
                ('prix_standard', models.DecimalField(decimal_places=2, max_digits=10)),
                ('prix_vip', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('statut', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('suspendue', 'Suspendue')], default='active', max_length=20)),
                ('gare_arrivee', models.ForeignKey(db_column='gare_arrivee', on_delete=django.db.models.deletion.CASCADE, related_name='lignes_arrivee', to='reservations.gare')),
                ('gare_depart', models.ForeignKey(db_column='gare_depart', on_delete=django.db.models.deletion.CASCADE, related_name='lignes_depart', to='reservations.gare')),
                ('ville_arrivee', models.ForeignKey(db_column='ville_arrivee', on_delete=django.db.models.deletion.CASCADE, related_name='lignes_arrivee', to='reservations.ville')),
                ('ville_depart', models.ForeignKey(db_column='ville_depart', on_delete=django.db.models.deletion.CASCADE, related_name='lignes_depart', to='reservations.ville')),
            ],
            options={
                'db_table': 'ligne',
            },
        ),
        migrations.AddField(
            model_name='gare',
            name='id_ville',
            field=models.ForeignKey(db_column='id_ville', on_delete=django.db.models.deletion.CASCADE, to='reservations.ville'),
        ),
        migrations.CreateModel(
            name='Voyage',
            fields=[
                ('id_voyage', models.AutoField(primary_key=True, serialize=False)),
                ('date_voyage', models.DateField()),
                ('heure_depart', models.TimeField()),
                ('heure_arrivee_prevue', models.TimeField()),
                ('prix_voyage', models.DecimalField(decimal_places=2, max_digits=10)),
                ('places_disponibles', models.IntegerField()),
                ('statut', models.CharField(choices=[('programmé', 'Programmé'), ('en_cours', 'En Cours'), ('terminé', 'Terminé'), ('annulé', 'Annulé'), ('reporté', 'Reporté')], default='programmé', max_length=20)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('id_car', models.ForeignKey(db_column='id_car', on_delete=django.db.models.deletion.CASCADE, to='reservations.car')),
                ('id_chauffeur', models.ForeignKey(db_column='id_chauffeur', on_delete=django.db.models.deletion.CASCADE, to='reservations.chauffeur')),
                ('id_ligne', models.ForeignKey(db_column='id_ligne', on_delete=django.db.models.deletion.CASCADE, to='reservations.ligne')),
            ],
            options={
                'db_table': 'voyage',
            },
        ),
        migrations.AddField(
            model_name='reservation',
            name='id_voyage',
            field=models.ForeignKey(db_column='id_voyage', on_delete=django.db.models.deletion.CASCADE, to='reservations.voyage'),
        ),
    ]
