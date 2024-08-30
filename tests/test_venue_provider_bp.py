import json
from bson import ObjectId
from unittest.mock import patch
from routes.venue_provider_bp.models import VenueProvider

def test_get_venue_providers_success(client, init_database):
    # Mock the VenueProvider.find_all method
    with patch('routes.venue_provider_bp.models.VenueProvider.find_all') as mock_find_all:
        mock_find_all.return_value = [
            {"_id": str(ObjectId()), "name_of_venue": "Venue 1"},
            {"_id": str(ObjectId()), "name_of_venue": "Venue 2"}
        ]
        response = client.get('/venueProvider/get/makeups', headers={'Authorization': 'Bearer fake-token'})
        assert response.status_code == 200
        assert len(response.json) == 2

def test_get_venue_providers_failure(client, init_database):
    # Simulate an exception in VenueProvider.find_all method
    with patch('routes.venue_provider_bp.models.VenueProvider.find_all') as mock_find_all:
        mock_find_all.side_effect = Exception("Database error")
        response = client.get('/venueProvider/get/makeups', headers={'Authorization': 'Bearer fake-token'})
        assert response.status_code == 500
        assert response.json['message'] == "Error in Fetching Venues"

def test_create_venue_provider_success(client, init_database):
    # Mock the ImageUploadingService.upload_image method
    with patch('services.image_upload_service.ImageUploadingService.upload_image') as mock_upload_image:
        mock_upload_image.return_value = "http://fake-url.com/image.jpg"

        # Mock the save method of the VenueProvider model
        with patch('routes.venue_provider_bp.models.VenueProvider.save') as mock_save:
            mock_save.return_value = True

            data = {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "phone": "1234567890",
                "nameOfVenue": "My Venue",
                "capacity": 100,
                "size": 1000,
                "typeOfProperty": "Banquet Hall"
            }
            response = client.post('/venueProvider/postdata', data=data, headers={'Authorization': 'Bearer fake-token'})

            assert response.status_code == 201
            assert response.json['message'] == "Successfully Created"

def test_create_venue_provider_failure(client, init_database):
    with patch('routes.venue_provider_bp.models.VenueProvider.save') as mock_save:
        mock_save.return_value = Exception("Save error")

        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "nameOfVenue": "My Venue",
            "capacity": 100,
            "size": 1000,
            "typeOfProperty": "Banquet Hall"
        }
        response = client.post('/venueProvider/postdata', data=data, headers={'Authorization': 'Bearer fake-token'})

        assert response.status_code == 500
        assert response.json['message'] == "Error in Creating Venue"

def test_delete_venue_provider_success(client, init_database):
    venue_id = str(ObjectId())
    with patch('routes.venue_provider_bp.models.mongo.db.VenueProvider.delete_one') as mock_delete:
        mock_delete.return_value.deleted_count = 1

        response = client.delete(f'/venueProvider/{venue_id}', headers={'Authorization': 'Bearer fake-token'})

        assert response.status_code == 200
        assert response.json['message'] == "Venue deleted successfully"

def test_delete_venue_provider_not_found(client, init_database):
    venue_id = str(ObjectId())
    with patch('routes.venue_provider_bp.models.mongo.db.VenueProvider.delete_one') as mock_delete:
        mock_delete.return_value.deleted_count = 0

        response = client.delete(f'/venueProvider/{venue_id}', headers={'Authorization': 'Bearer fake-token'})

        assert response.status_code == 404
        assert response.json['message'] == "Venue not found"
