from models import mongo
from bson import ObjectId

class Staff:
    def __init__(self, **kwargs):
        # Initialize with all fields, defaulting to None if not provided
        id = ObjectId(kwargs.get('user_id'))
        self.user_id = id #foreign key for user id , whos staff details are entered
        self.phoneNumber = kwargs.get('phoneNumber', '')
        self.dateOfBirth = kwargs.get('dateOfBirth', '')
        self.gender = kwargs.get('gender', '')
        self.city = kwargs.get('city', '')
        self.state = kwargs.get('state', '')
        self.idCardNumber = kwargs.get('idCardNumber', '')
        self.experienceYears = kwargs.get('experienceYears', '')
        self.previousEmployers = kwargs.get('previousEmployers', '')
        self.relevantSkills = kwargs.get('relevantSkills', '')
        self.daysAvailable = kwargs.get('daysAvailable', [])
        self.preferredShifts = kwargs.get('preferredShifts', [])
        self.noticePeriod = kwargs.get('noticePeriod', '')
        self.currentAddress = kwargs.get('currentAddress', '')
        self.preferredWorkLocations = kwargs.get('preferredWorkLocations', '')
        self.foodCertifications = kwargs.get('foodCertifications', '')
        self.tipsCertification = kwargs.get('tipsCertification', '')
        self.firstAidTraining = kwargs.get('firstAidTraining', '')
        self.eventTypes = kwargs.get('eventTypes', '')
        self.rolesPerformed = kwargs.get('rolesPerformed', '')
        self.profilePhoto = kwargs.get('profilePhoto', None)
        self.resume = kwargs.get('resume', None)
        self.references = kwargs.get('references', '')
        self.hourlyRate = kwargs.get('hourlyRate', '')
        self.specialSkills = kwargs.get('specialSkills', '')
        self.specialRequirements = kwargs.get('specialRequirements', '')
        self.additionalComments = kwargs.get('additionalComments', '')
        self.agreement = kwargs.get('agreement', False)
        self.privacyConsent = kwargs.get('privacyConsent', False)

    def to_dict(self):
        return self.__dict__

    def save(self):
        """Save new staff data to the database."""
        return mongo.db['Staff'].insert_one(self.to_dict())

    @staticmethod
    def find_all():
        try:
            staffs = mongo.db['Staff'].find()
            return [{**staff, '_id': str(staff['_id'])} for staff in staffs]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def update_by_id(staff_id, update_data):
        """Update staff data by ID."""
        return mongo.db['Staff'].update_one(
            {"_id": ObjectId(staff_id)},
            {"$set": update_data}
        )

    @staticmethod
    def delete_by_id(staff_id):
        """Delete a staff member by ID."""
        return mongo.db['Staff'].delete_one({"_id": ObjectId(staff_id)})