from django import forms
from .models import Ville, Client
from datetime import date

class SearchTripForm(forms.Form):
    ville_depart = forms.ModelChoiceField(queryset=Ville.objects.filter(statut='active'), label="Ville de départ")
    ville_arrivee = forms.ModelChoiceField(queryset=Ville.objects.filter(statut='active'), label="Ville d'arrivée")
    date_voyage = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}), label="Date de voyage")

class ReservationForm(forms.Form):
    voyage_id = forms.IntegerField(widget=forms.HiddenInput())
    nombre_places = forms.IntegerField(min_value=1, label="Nombre de places")
    noms_passagers = forms.CharField(widget=forms.Textarea, label="Noms des passagers (un par ligne)", required=False)
    type_place = forms.ChoiceField(choices=[('standard', 'Standard'), ('vip', 'VIP')], label="Type de place")

class ClientRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'email', 'telephone', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Client.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if Client.objects.filter(telephone=telephone).exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return telephone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

class ClientLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")