class VictimProfile:
    def __init__(self):
        self.victim_image = None
        self.victim_name = None
        self.father_name = None
        self.ssn = None
        self.age = None
        self.division = None
        self.district = None
        self.upazila = None
        self.email = None
        self.mobile = None

    def set_profile(self, victim_image, victim_name, father_name, ssn, age, division, district, upazila, email, mobile):
        self.victim_image = victim_image
        self.victim_name = victim_name
        self.father_name = father_name
        self.ssn = ssn
        self.age = age
        self.division = division
        self.district = district
        self.upazila = upazila
        self.email = email
        self.mobile = mobile

    def get_profile(self):
        return {
            'victim_image': self.victim_image,
            'victim_name': self.victim_name,
            'father_name': self.father_name,
            'ssn': self.ssn,
            'age': self.age,
            'division': self.division,
            'district': self.district,
            'upazila': self.upazila,
            'email': self.email,
            'mobile': self.mobile,
        }