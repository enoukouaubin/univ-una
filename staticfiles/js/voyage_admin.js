(function($) {
    $(document).ready(function() {
        console.log('Script voyage_admin.js chargé et exécuté'); // Journal de confirmation
        alert('JavaScript est chargé !'); // Alerte temporaire pour tester
        // Récupérer les éléments du formulaire
        var carSelect = $('#id_id_car');
        var ligneSelect = $('#id_id_ligne');
        var heureDepartInput = $('#id_heure_depart');
        var heureArriveeInput = $('#id_heure_arrivee_prevue');
        var placesDisponiblesInput = $('#id_places_disponibles');

        // Mettre à jour le nombre de places disponibles quand le car change
        carSelect.on('change', function() {
            var carId = $(this).val();
            if (carId) {
                $.ajax({
                    url: '/admin/reservations/voyage/get_car_details/' + carId + '/',
                    method: 'GET',
                    success: function(data) {
                        if (data.nombre_places !== undefined) {
                            placesDisponiblesInput.val(data.nombre_places);
                        } else {
                            placesDisponiblesInput.val('');
                        }
                    },
                    error: function() {
                        placesDisponiblesInput.val('');
                        alert('Erreur lors de la récupération des détails du car.');
                    }
                });
            } else {
                placesDisponiblesInput.val('');
            }
        });

        // Mettre à jour l'heure d'arrivée quand l'heure de départ ou la ligne change
        function updateHeureArrivee() {
            var ligneId = ligneSelect.val();
            var heureDepart = heureDepartInput.val();

            if (ligneId && heureDepart) {
                $.ajax({
                    url: '/admin/reservations/voyage/get_ligne_details/' + ligneId + '/',
                    method: 'GET',
                    success: function(data) {
                        if (data.duree_minutes !== undefined) {
                            // Convertir l'heure de départ (HH:MM) en objet Date
                            var [hours, minutes] = heureDepart.split(':').map(Number);
                            var depart = new Date();
                            depart.setHours(hours, minutes, 0, 0);

                            // Ajouter la durée (en minutes)
                            var arrivee = new Date(depart.getTime() + data.duree_minutes * 60000);

                            // Formater l'heure d'arrivée pour le champ (HH:MM)
                            var arriveeFormatted = arrivee.getHours().toString().padStart(2, '0') + ':' +
                                                  arrivee.getMinutes().toString().padStart(2, '0');
                            heureArriveeInput.val(arriveeFormatted);
                        } else {
                            heureArriveeInput.val('');
                        }
                    },
                    error: function() {
                        heureArriveeInput.val('');
                        alert('Erreur lors de la récupération des détails de la ligne.');
                    }
                });
            } else {
                heureArriveeInput.val('');
            }
        }

        // Écouter les changements sur l'heure de départ et la ligne
        heureDepartInput.on('change', updateHeureArrivee);
        ligneSelect.on('change', updateHeureArrivee);
    });
})(django.jQuery);