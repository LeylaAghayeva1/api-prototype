"""
Mock data: kept in memory, so it RESETS every time the server restarts.
 
  user-a owns: form_101, form_102
  user-b owns: form_103, form_104, form_105
  form_999 does NOT exist, use it to demo 404 Not Found.
""" 
from itertools import count
FORMS: dict[str, dict] = {
    "form_101": {
        "id": "form_101",
        "title": "Beach Cleanup Volunteers",
        "description": "Help us clean Bilgah beach before winter.",
        "location": "Baku",
        "eventDate": "2026-12-05",
        "capacity": 40,
        "status": "published",
        "questions": [
            {"label": "Full name", "type": "text", "required": True},
            {"label": "Phone number", "type": "text", "required": True},
            {"label": "Do you have a car?", "type": "yes_no", "required": False},
        ],
        "ownerId": "user-a",
        "createdAt": "2026-11-01T10:00:00Z",
        "updatedAt": "2026-11-01T10:00:00Z",
    },
    "form_102": {
        "id": "form_102",
        "title": "Tree Planting Day",
        "description": "Plant 500 trees in Sumgait park.",
        "location": "Sumgait",
        "eventDate": "2027-03-21",
        "capacity": 100,
        "status": "draft",
        "questions": [
            {"label": "Full name", "type": "text", "required": True},
            {"label": "T-shirt size", "type": "text", "required": False},
        ],
        "ownerId": "user-a",
        "createdAt": "2026-11-03T09:30:00Z",
        "updatedAt": "2026-11-03T09:30:00Z",
    },
    "form_103": {
        "id": "form_103",
        "title": "Food Bank Helpers",
        "description": "Pack and deliver food boxes to families.",
        "location": "Ganja",
        "eventDate": "2026-12-12",
        "capacity": 25,
        "status": "published",
        "questions": [
            {"label": "Full name", "type": "text", "required": True},
            {"label": "Available on weekends?", "type": "yes_no", "required": True},
        ],
        "ownerId": "user-b",
        "createdAt": "2026-11-05T14:00:00Z",
        "updatedAt": "2026-11-05T14:00:00Z",
    },
    "form_104": {
        "id": "form_104",
        "title": "Animal Shelter Weekend",
        "description": "Walk dogs and clean the shelter.",
        "location": "Ganja",
        "eventDate": "2026-12-19",
        "capacity": 15,
        "status": "published",
        "questions": [
            {"label": "Full name", "type": "text", "required": True},
            {"label": "Any allergies to animals?", "type": "yes_no", "required": True},
        ],
        "ownerId": "user-b",
        "createdAt": "2026-11-06T11:15:00Z",
        "updatedAt": "2026-11-06T11:15:00Z",
    },
    "form_105": {
        "id": "form_105",
        "title": "Marathon Water Station",
        "description": "Hand out water at the city marathon.",
        "location": "Ganja",
        "eventDate": "2026-10-10",
        "capacity": 30,
        "status": "closed",
        "questions": [
            {"label": "Full name", "type": "text", "required": True},
        ],
        "ownerId": "user-b",
        "createdAt": "2026-09-20T08:00:00Z",
        "updatedAt": "2026-10-11T18:00:00Z",
    },
}
 
_id_counter = count(106) 
def next_form_id() -> str:
    return f"form_{next(_id_counter)}"
 