from pydantic import BaseModel as parse_json
from typing import List, Optional


class Application(parse_json):
    dorm_name: str
    applicant_name: str
    application_date: str
    application_status: str


class ResponseData(parse_json):
    status: str
    message: Optional[str] = None
    data: Optional[List[Application]] = None

    def display_rooms(self):
        
        if not self.data:
            return self.message or "No applications to display"
            
        result = ""
        for applications in self.data:
            result += "Dorm Name: " + applications.dorm_name + "\n"
            result += "Applicant Name: " + applications.applicant_name + "\n"
            result += "Application Date: " + applications.application_date + "\n"
            result += "Application Status: " + applications.application_status + "\n"
            result += "----------------------------------------\n"

        return result

