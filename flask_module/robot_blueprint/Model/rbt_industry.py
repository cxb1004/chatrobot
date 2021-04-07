class Industry:
    def __init__(self):
        self.id = None
        self.industry_name = None
        self.has_model = None
        self.robot_id = None
        self.create_at = None
        self.update_at = None

    def getIndustryByName(self, industry_name):
        p