document.addEventListener('DOMContentLoaded', function() {
    // Récupérer les champs du formulaire
    const carSelect = document.querySelector('#id_id_car');
    const ligneSelect = document.querySelector('#id_id_ligne');
    const heureDepartInput = document.querySelector('#id_heure_depart');
    const heureArriveeInput = document.querySelector('#id_heure_arrivee_prevue');
    const placesDisponiblesInput = document.querySelector('#id_places_disponibles');

    // Vérifier que les sélecteurs existent
    if (!carSelect || !ligneSelect || !heureDepartInput || !heureArriveeInput || !placesDisponiblesInput) {
        console.error('Un ou plusieurs sélecteurs de champ sont introuvables :', {
            carSelect: !!carSelect,
            ligneSelect: !!ligneSelect,
            heureDepartInput: !!heureDepartInput,
            heureArriveeInput: !!heureArriveeInput,
            placesDisponiblesInput: !!placesDisponiblesInput
        });
        return;
    }

    // Fonction pour récupérer les détails du car
    function fetchCarDetails(carId) {
        if (carId) {
            console.log(`Récupération des détails du car ${carId}`);
            fetch(`/admin/reservations/voyage/get_car_details/${carId}/`)
                .then(response => {
                    if (!response.ok) throw new Error(`Erreur HTTP ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log('Réponse car:', data);
                    if (data.nombre_places) {
                        placesDisponiblesInput.value = data.nombre_places;
                        console.log(`Places disponibles mises à jour : ${data.nombre_places}`);
                    } else {
                        placesDisponiblesInput.value = '';
                        console.error('Erreur car:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de la récupération des détails du car:', error);
                    placesDisponiblesInput.value = '';
                });
        } else {
            placesDisponiblesInput.value = '';
            console.log('Aucun car sélectionné');
        }
    }

    // Fonction pour récupérer les détails de la ligne et calculer l'heure d'arrivée
    function fetchLigneDetailsAndCalculateArrival(ligneId, heureDepart) {
        if (ligneId && heureDepart) {
            console.log(`Calcul de l'heure d'arrivée pour ligne ${ligneId}, heure de départ ${heureDepart}`);
            fetch(`/admin/reservations/voyage/get_ligne_details/${ligneId}/`)
                .then(response => {
                    if (!response.ok) throw new Error(`Erreur HTTP ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log('Réponse ligne:', data);
                    if (data.duree_minutes) {
                        // Parser heure_depart (format HH:MM)
                        const [hours, minutes] = heureDepart.split(':').map(Number);
                        if (isNaN(hours) || isNaN(minutes)) {
                            console.error('Format de heure_depart invalide:', heureDepart);
                            heureArriveeInput.value = '';
                            return;
                        }
                        const departMinutes = hours * 60 + minutes;
                        const totalMinutes = departMinutes + data.duree_minutes;
                        const arriveeHours = Math.floor(totalMinutes / 60) % 24;
                        const arriveeMinutes = totalMinutes % 60;
                        // Formater en HH:MM
                        const formattedTime = `${String(arriveeHours).padStart(2, '0')}:${String(arriveeMinutes).padStart(2, '0')}`;
                        heureArriveeInput.value = formattedTime;
                        console.log(`Heure d'arrivée calculée : ${formattedTime} (durée: ${data.duree_minutes} minutes)`);
                    } else {
                        heureArriveeInput.value = '';
                        console.error('Erreur ligne:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de la récupération des détails de la ligne:', error);
                    heureArriveeInput.value = '';
                });
        } else {
            heureArriveeInput.value = '';
            console.log(`Données manquantes - ligneId: ${ligneId}, heureDepart: ${heureDepart}`);
        }
    }

    // Écouter les changements sur le champ du car
    carSelect.addEventListener('change', function() {
        const carId = this.value;
        fetchCarDetails(carId);
    });

    // Écouter les changements sur le champ de la ligne
    ligneSelect.addEventListener('change', function() {
        const ligneId = this.value;
        const heureDepart = heureDepartInput.value;
        fetchLigneDetailsAndCalculateArrival(ligneId, heureDepart);
    });

    // Écouter les changements sur le champ heure de départ
    heureDepartInput.addEventListener('input', function() {
        const ligneId = ligneSelect.value;
        const heureDepart = this.value;
        fetchLigneDetailsAndCalculateArrival(ligneId, heureDepart);
    });

    // Initialiser les champs si des valeurs sont déjà sélectionnées
    if (carSelect.value) {
        fetchCarDetails(carSelect.value);
    }
    if (ligneSelect.value && heureDepartInput.value) {
        fetchLigneDetailsAndCalculateArrival(ligneSelect.value, heureDepartInput.value);
    }
});