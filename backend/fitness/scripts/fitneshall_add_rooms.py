from msilib.schema import Font
from fitness.models import *

hall_1_data = {
    "name": "Small Hall ",
    "capacity": 30,
}
hall_2_data = {
    "name": "Big Hall ",
    "capacity": 60,
}

if __name__ == "__main__":
    FitnessHall.objects.get_or_create(**hall_1_data)
    FitnessHall.objects.get_or_create(**hall_2_data)
