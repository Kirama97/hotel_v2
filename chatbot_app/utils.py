from hotels.models import Hotel

def get_hotel_context():
    hotels = Hotel.objects.all()
    if not hotels:
        return "Aucun hôtel n'est actuellement disponible dans notre catalogue."

    context = "Voici la liste des hôtels disponibles chez Red Product :\n\n"
    for hotel in hotels:
        context += f"- Nom : {hotel.nom}\n"
        context += f"  Adresse : {hotel.adresse}\n"
        context += f"  Prix : {hotel.prix_par_nuit} {hotel.devise}\n"
        context += f"  Contact : {hotel.email_contact} / {hotel.telephone}\n\n"

    return context
