"""
Regional Animal Shelter Management System (RASMS)

Features:
- Multi-shelter inventory
- Move animals between shelters (with movement record)
- Update animal health/adoption status
- Search animals by name, breed, or health status
- Summary report (totals, available, treatment)
- Adoption fees + shelter revenue tracking
- JSON load/save (rasms_data.json)

PEP 8 notes:
- Snake_case names
- Constants in UPPER_CASE
- Line lengths wrapped to ~79 characters
- Clear separation of concerns
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

DATA_FILE = "rasms_data.json"

VALID_TYPES = {"Dog", "Cat", "Rabbit", "Bird", "Reptile", "Other"}
VALID_HEALTH = {"Healthy", "Needs Vaccination", "Injured", "In Treatment"}
VALID_ADOPTION = {"Available", "Adopted", "In Treatment", "Hold"}


def calc_adoption_fee(animal_type: str, age_years: float) -> int:
    """Return adoption fee based on animal type and age."""
    animal_type = animal_type.strip().title()
    under_five = age_years < 5

    if animal_type == "Dog":
        return 300 if under_five else 200
    if animal_type == "Cat":
        return 250 if under_five else 150
    if animal_type in {"Rabbit", "Bird", "Reptile", "Other"}:
        return 150 if under_five else 100

    return 120 if under_five else 80


def safe_input(prompt: str) -> str:
    """Input wrapper to keep prompts consistent."""
    return input(prompt).strip()


@dataclass
class Animal:
    """A single animal record in the system."""

    animal_id: str
    animal_type: str
    name: str
    age: float
    breed: str
    health_status: str
    adoption_status: str
    shelter_address: str

    def normalized_id(self) -> str:
        """Return uppercased ID for indexing."""
        return self.animal_id.strip().upper()

    def display_line(self) -> str:
        """Return a formatted inventory line."""
        return (
            f"{self.animal_id:6} | {self.name:12} | {self.animal_type:8} | "
            f"{self.breed:18} | {self.age:4} | {self.health_status:16} | "
            f"{self.adoption_status}"
        )


@dataclass
class Shelter:
    """A shelter that holds animals and tracks revenue."""

    name: str
    suburb: str
    address: str
    animals: List[Animal]
    adoption_fees_collected: int = 0
    adopted_count: int = 0

    def add_animal(self, animal: Animal) -> None:
        """Add an animal and update its shelter address."""
        animal.shelter_address = self.address
        self.animals.append(animal)

    def remove_animal_by_id(self, animal_id: str) -> Optional[Animal]:
        """Remove an animal by ID and return it if found."""
        target = animal_id.strip().upper()
        for idx, animal in enumerate(self.animals):
            if animal.normalized_id() == target:
                return self.animals.pop(idx)
        return None

    def find_animal(self, animal_id: str) -> Optional[Animal]:
        """Find and return an animal by ID."""
        target = animal_id.strip().upper()
        for animal in self.animals:
            if animal.normalized_id() == target:
                return animal
        return None


class RASMS:
    """Regional Animal Shelter Management System controller."""

    def __init__(self) -> None:
        self.shelters: Dict[str, Shelter] = {}
        self.animal_index: Dict[str, str] = {}
        self.load_or_seed()

    # -------------------------
    # Persistence
    # -------------------------
    def load_or_seed(self) -> None:
        """Load from JSON if present; otherwise seed and save."""
        if os.path.exists(DATA_FILE):
            try:
                self.load(DATA_FILE)
                self.rebuild_index()
                return
            except (OSError, json.JSONDecodeError) as exc:
                print(
                    "⚠️ Could not load data file; seeding new data. "
                    f"Reason: {exc}"
                )

        self.seed_data()
        self.rebuild_index()
        self.save(DATA_FILE)

    def save(self, filename: str) -> None:
        """Save shelters and animals into JSON."""
        data = {"shelters": []}

        for shelter in self.shelters.values():
            shelter_dict = {
                "name": shelter.name,
                "suburb": shelter.suburb,
                "address": shelter.address,
                "adoption_fees_collected": shelter.adoption_fees_collected,
                "adopted_count": shelter.adopted_count,
                "animals": [asdict(animal) for animal in shelter.animals],
            }
            data["shelters"].append(shelter_dict)

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def load(self, filename: str) -> None:
        """Load shelters and animals from JSON."""
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.shelters.clear()

        for shelter_data in data.get("shelters", []):
            animals = [Animal(**a) for a in shelter_data.get("animals", [])]
            shelter = Shelter(
                name=shelter_data["name"],
                suburb=shelter_data["suburb"],
                address=shelter_data["address"],
                animals=animals,
                adoption_fees_collected=shelter_data.get(
                    "adoption_fees_collected", 0
                ),
                adopted_count=shelter_data.get("adopted_count", 0),
            )
            self.shelters[shelter.name] = shelter

    def rebuild_index(self) -> None:
        """Rebuild fast lookup map: animal_id -> shelter_name."""
        self.animal_index.clear()
        for shelter_name, shelter in self.shelters.items():
            for animal in shelter.animals:
                self.animal_index[animal.normalized_id()] = shelter_name

    # -------------------------
    # Seed data (10 SA shelters)
    # -------------------------
    def seed_data(self) -> None:
        """Create default shelters and sample animals."""
        shelter_list = [
            Shelter(
                "Glenelg Animal Rescue",
                "Glenelg",
                "12 Paws Street, Glenelg SA 5045",
                [],
            ),
            Shelter(
                "Mawson Lakes Pet Haven",
                "Mawson Lakes",
                "8 Shelter Lane, Mawson Lakes SA 5095",
                [],
            ),
            Shelter(
                "Norwood Animal Care",
                "Norwood",
                "21 Parade Road, Norwood SA 5067",
                [],
            ),
            Shelter(
                "Elizabeth Regional Shelter",
                "Elizabeth",
                "5 Rescue Avenue, Elizabeth SA 5112",
                [],
            ),
            Shelter(
                "Mount Barker Animal Shelter",
                "Mount Barker",
                "33 Wattle Drive, Mount Barker SA 5251",
                [],
            ),
            Shelter(
                "Port Adelaide Safe Paws",
                "Port Adelaide",
                "14 Wharf Road, Port Adelaide SA 5015",
                [],
            ),
            Shelter(
                "Victor Harbor Animal Aid",
                "Victor Harbor",
                "9 Ocean View Rd, Victor Harbor SA 5211",
                [],
            ),
            Shelter(
                "Whyalla Animal Welfare",
                "Whyalla",
                "2 Steel Street, Whyalla SA 5600",
                [],
            ),
            Shelter(
                "Murray Bridge Pet Refuge",
                "Murray Bridge",
                "10 River Road, Murray Bridge SA 5253",
                [],
            ),
            Shelter(
                "Kadina Country Animal Care",
                "Kadina",
                "6 Copper Coast Hwy, Kadina SA 5554",
                [],
            ),
        ]

        self.shelters = {shelter.name: shelter for shelter in shelter_list}

        animals = [
            Animal(
                "D102",
                "Dog",
                "Buddy",
                3,
                "Kelpie",
                "Healthy",
                "Available",
                shelter_list[0].address,
            ),
            Animal(
                "C214",
                "Cat",
                "Luna",
                6,
                "Domestic Short Hair",
                "Needs Vaccination",
                "Available",
                shelter_list[0].address,
            ),
            Animal(
                "R301",
                "Rabbit",
                "Snowy",
                2,
                "Mini Lop",
                "Healthy",
                "Available",
                shelter_list[1].address,
            ),
            Animal(
                "D155",
                "Dog",
                "Rocky",
                7,
                "Staffy Mix",
                "In Treatment",
                "In Treatment",
                shelter_list[1].address,
            ),
            Animal(
                "B410",
                "Bird",
                "Kiwi",
                4,
                "Budgerigar",
                "Healthy",
                "Available",
                shelter_list[2].address,
            ),
            Animal(
                "C230",
                "Cat",
                "Milo",
                1,
                "Ragdoll",
                "Healthy",
                "Available",
                shelter_list[2].address,
            ),
            Animal(
                "D199",
                "Dog",
                "Zara",
                5,
                "German Shepherd",
                "Injured",
                "In Treatment",
                shelter_list[3].address,
            ),
            Animal(
                "O520",
                "Other",
                "Nibbles",
                8,
                "Guinea Pig",
                "Healthy",
                "Available",
                shelter_list[3].address,
            ),
            Animal(
                "R388",
                "Reptile",
                "Spike",
                2,
                "Bearded Dragon",
                "Healthy",
                "Available",
                shelter_list[4].address,
            ),
            Animal(
                "C299",
                "Cat",
                "Shadow",
                9,
                "Domestic Long Hair",
                "Needs Vaccination",
                "Available",
                shelter_list[4].address,
            ),
            Animal(
                "D210",
                "Dog",
                "Coco",
                4,
                "Cavoodle",
                "Healthy",
                "Available",
                shelter_list[5].address,
            ),
            Animal(
                "B499",
                "Bird",
                "Sunny",
                7,
                "Cockatiel",
                "Healthy",
                "Available",
                shelter_list[6].address,
            ),
        ]

        self.shelters[shelter_list[0].name].add_animal(animals[0])
        self.shelters[shelter_list[0].name].add_animal(animals[1])
        self.shelters[shelter_list[1].name].add_animal(animals[2])
        self.shelters[shelter_list[1].name].add_animal(animals[3])
        self.shelters[shelter_list[2].name].add_animal(animals[4])
        self.shelters[shelter_list[2].name].add_animal(animals[5])
        self.shelters[shelter_list[3].name].add_animal(animals[6])
        self.shelters[shelter_list[3].name].add_animal(animals[7])
        self.shelters[shelter_list[4].name].add_animal(animals[8])
        self.shelters[shelter_list[4].name].add_animal(animals[9])
        self.shelters[shelter_list[5].name].add_animal(animals[10])
        self.shelters[shelter_list[6].name].add_animal(animals[11])

    # -------------------------
    # Core actions
    # -------------------------
    def view_inventory(self) -> None:
        """Display all shelters and current animals."""
        print("\n================= SHELTER INVENTORY =================")

        for shelter in self.shelters.values():
            print(f"\n🏠 {shelter.name} ({shelter.suburb})")
            print(f"   Address: {shelter.address}")

            if not shelter.animals:
                print("   (No animals currently housed here.)")
                continue

            header = (
                "   ID     | Name         | Type     | Breed              | "
                "Age  | Health Status     | Adoption Status"
            )
            print(header)
            print("   " + "-" * 95)

            for animal in shelter.animals:
                print("   " + animal.display_line())

    def move_animal(self, animal_id: str, new_shelter_name: str) -> None:
        """Relocate an animal from one shelter to another."""
        animal_key = animal_id.strip().upper()
        new_shelter_name = new_shelter_name.strip()

        if animal_key not in self.animal_index:
            print("❌ Animal ID not found.")
            return

        if new_shelter_name not in self.shelters:
            print("❌ New shelter not found.")
            return

        old_shelter_name = self.animal_index[animal_key]
        if old_shelter_name == new_shelter_name:
            print("⚠️ Animal is already in that shelter.")
            return

        old_shelter = self.shelters[old_shelter_name]
        new_shelter = self.shelters[new_shelter_name]

        animal = old_shelter.remove_animal_by_id(animal_key)
        if animal is None:
            print("❌ Data mismatch; rebuilding index.")
            self.rebuild_index()
            return

        old_address = old_shelter.address
        new_address = new_shelter.address
        new_shelter.add_animal(animal)

        self.animal_index[animal_key] = new_shelter_name

        print("\n✅ MOVEMENT RECORD")
        print(f"Animal: {animal.animal_id} - {animal.name}")
        print(f"From:   {old_shelter_name} | {old_address}")
        print(f"To:     {new_shelter_name} | {new_address}")

    def update_status(
        self,
        animal_id: str,
        new_health: Optional[str] = None,
        new_adoption: Optional[str] = None,
    ) -> None:
        """Update animal health and/or adoption status.

        If adoption status becomes 'Adopted', record fee and remove from
        shelter inventory.
        """
        animal_key = animal_id.strip().upper()
        if animal_key not in self.animal_index:
            print("❌ Animal ID not found.")
            return

        shelter_name = self.animal_index[animal_key]
        shelter = self.shelters[shelter_name]
        animal = shelter.find_animal(animal_key)

        if animal is None:
            print("❌ Data mismatch; rebuilding index.")
            self.rebuild_index()
            return

        old_health = animal.health_status
        old_adoption = animal.adoption_status

        if new_health is not None:
            new_health = new_health.strip()
            if new_health not in VALID_HEALTH:
                valid = ", ".join(sorted(VALID_HEALTH))
                print(f"❌ Invalid health status. Choose from: {valid}")
                return
            animal.health_status = new_health

        if new_adoption is not None:
            new_adoption = new_adoption.strip()
            if new_adoption not in VALID_ADOPTION:
                valid = ", ".join(sorted(VALID_ADOPTION))
                print(f"❌ Invalid adoption status. Choose from: {valid}")
                return

            if old_adoption != "Adopted" and new_adoption == "Adopted":
                fee = calc_adoption_fee(animal.animal_type, animal.age)
                shelter.adoption_fees_collected += fee
                shelter.adopted_count += 1

                removed = shelter.remove_animal_by_id(animal_key)
                if removed is not None:
                    del self.animal_index[animal_key]

                print("\n✅ ADOPTION RECORDED")
                print(
                    f"Animal: {animal.animal_id} - {animal.name} "
                    f"({animal.animal_type}, {animal.age} years)"
                )
                print(f"Shelter: {shelter.name}")
                print(f"Adoption Fee Charged: ${fee}")
                print(
                    "Note: Adopted animals are removed from current inventory."
                )
                return

            animal.adoption_status = new_adoption

        print("\n✅ STATUS UPDATED")
        print(f"Animal: {animal.animal_id} - {animal.name}")

        if new_health is not None:
            print(f"Health:  {old_health}  →  {animal.health_status}")

        if new_adoption is not None:
            print(f"Adopt:   {old_adoption}  →  {animal.adoption_status}")

    # -------------------------
    # Advanced features
    # -------------------------
    def search_animals(self, query: str, mode: str) -> None:
        """Search current inventory by name, breed, or health status."""
        query_text = query.strip().lower()
        if not query_text:
            print("❌ Empty search query.")
            return

        results: List[Tuple[str, Animal]] = []

        for shelter_name, shelter in self.shelters.items():
            for animal in shelter.animals:
                if mode == "name":
                    haystack = animal.name.lower()
                elif mode == "breed":
                    haystack = animal.breed.lower()
                elif mode == "health":
                    haystack = animal.health_status.lower()
                else:
                    print("❌ Invalid search mode.")
                    return

                if query_text in haystack:
                    results.append((shelter_name, animal))

        print("\n================= SEARCH RESULTS =================")
        print(f"Mode: {mode} | Query: '{query}'")

        if not results:
            print("No matches found.")
            return

        header = (
            "Shelter                         | ID     | Name         | "
            "Type     | Breed              | Age  | Health Status     | "
            "Adoption Status"
        )
        print(header)
        print("-" * 125)

        for shelter_name, animal in results:
            print(f"{shelter_name:30} | {animal.display_line()}")

    def summary_report(self) -> None:
        """Print totals per shelter + regional totals."""
        print("\n================= SUMMARY REPORT =================")

        regional_total = 0
        regional_available = 0
        regional_treatment = 0

        for shelter in self.shelters.values():
            total = len(shelter.animals)
            available = sum(
                1 for animal in shelter.animals
                if animal.adoption_status == "Available"
            )
            treatment = sum(
                1 for animal in shelter.animals
                if animal.adoption_status == "In Treatment"
                or animal.health_status in {"In Treatment", "Injured"}
            )

            regional_total += total
            regional_available += available
            regional_treatment += treatment

            print(f"\n🏠 {shelter.name} ({shelter.suburb})")
            print(f"  Total animals: {total}")
            print(f"  Available for adoption: {available}")
            print(f"  In treatment (approx): {treatment}")

        print("\n🌏 REGIONAL TOTALS")
        print(f"  Total animals in shelters: {regional_total}")
        print(f"  Available for adoption: {regional_available}")
        print(f"  In treatment (approx): {regional_treatment}")

    def revenue_report(self) -> None:
        """Display adoption counts and fees by shelter + regional total."""
        print("\n================= SHELTER REVENUE REPORT =================")

        regional_adopted = 0
        regional_fees = 0

        print("Shelter                         | Adopted | Fees Collected")
        print("-" * 65)

        for shelter in self.shelters.values():
            regional_adopted += shelter.adopted_count
            regional_fees += shelter.adoption_fees_collected
            print(
                f"{shelter.name:30} | {shelter.adopted_count:7} | "
                f"${shelter.adoption_fees_collected}"
            )

        print("-" * 65)
        print(f"{'REGIONAL TOTAL':30} | {regional_adopted:7} | ${regional_fees}")

    # -------------------------
    # Menu helpers
    # -------------------------
    def list_shelters(self) -> None:
        """Print numbered shelters."""
        print("\nAvailable Shelters:")
        for idx, shelter in enumerate(self.shelters.values(), start=1):
            print(f"  {idx}. {shelter.name} ({shelter.suburb})")

    def shelter_name_by_number(self, number: int) -> Optional[str]:
        """Get shelter name by 1-based index."""
        names = list(self.shelters.keys())
        if 1 <= number <= len(names):
            return names[number - 1]
        return None

    def menu_view_inventory(self) -> None:
        self.view_inventory()

    def menu_move_animal(self) -> None:
        animal_id = safe_input("Enter Animal ID to move (e.g., D102): ").upper()
        self.list_shelters()

        try:
            dest = int(safe_input("Enter destination shelter number: "))
        except ValueError:
            print("❌ Please enter a valid number.")
            return

        new_shelter = self.shelter_name_by_number(dest)
        if not new_shelter:
            print("❌ Invalid shelter selection.")
            return

        self.move_animal(animal_id, new_shelter)

    def menu_update_status(self) -> None:
        animal_id = safe_input("Enter Animal ID to update (e.g., C214): ").upper()

        print("\nUpdate what?")
        print("1) Health status")
        print("2) Adoption status")
        print("3) Both")
        sub_choice = safe_input("Choose (1-3): ")

        new_health = None
        new_adoption = None

        if sub_choice in {"1", "3"}:
            valid = ", ".join(sorted(VALID_HEALTH))
            print(f"Valid health statuses: {valid}")
            new_health = safe_input("Enter new health status: ")

        if sub_choice in {"2", "3"}:
            valid = ", ".join(sorted(VALID_ADOPTION))
            print(f"Valid adoption statuses: {valid}")
            new_adoption = safe_input("Enter new adoption status: ")

        self.update_status(animal_id, new_health, new_adoption)

    def menu_search(self) -> None:
        print("\nSearch by:")
        print("1) Name")
        print("2) Breed")
        print("3) Health status")
        mode_choice = safe_input("Choose (1-3): ")

        mode_map = {"1": "name", "2": "breed", "3": "health"}
        if mode_choice not in mode_map:
            print("❌ Invalid choice.")
            return

        query = safe_input("Enter search text: ")
        self.search_animals(query, mode_map[mode_choice])

    def run(self) -> None:
        """Run the menu loop."""
        actions = {
            "1": self.menu_view_inventory,
            "2": self.menu_move_animal,
            "3": self.menu_update_status,
            "4": self.menu_search,
            "5": self.summary_report,
            "6": self.revenue_report,
        }

        while True:
            print("\n================= RASMS MAIN MENU =================")
            print("1) View Shelter Inventory")
            print("2) Move an Animal Between Shelters")
            print("3) Update an Animal’s Status (Health/Adoption)")
            print("4) Search Animals (Name/Breed/Health)")
            print("5) Summary Report (Totals / Available / Treatment)")
            print("6) View Shelter Revenue Report (Adoptions + Fees)")
            print("7) Save and Exit")

            choice = safe_input("Select an option (1-7): ")

            if choice in actions:
                actions[choice]()
                continue

            if choice == "7":
                self.save(DATA_FILE)
                print("\n✅ Thank you for using RASMS.")
                print(f"Data saved to '{DATA_FILE}'. Goodbye! 🐾")
                break

            print("❌ Invalid option. Please choose 1-7.")


def main() -> None:
    """Program entry point."""
    system = RASMS()
    system.run()


if __name__ == "__main__":
    main()
