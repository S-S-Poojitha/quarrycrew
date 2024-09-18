import sys
import datetime

class EVCostCalculator:
    def __init__(self):
        self.ev_data = {
            "model_a": {
                "cost": 30000,
                "description": "Basic model with standard features.",
                "suitable_for": ["surface_mining", "strip_mining"],
                "efficiency_rating": 6
            },
            "model_b": {
                "cost": 45000,
                "description": "Advanced model with extended range and premium features.",
                "suitable_for": ["surface_mining", "underground_mining", "mountain_top_removal"],
                "efficiency_rating": 9
            },
            "model_c": {
                "cost": 35000,
                "description": "Mid-range model with balanced features and performance.",
                "suitable_for": ["underground_mining", "platinum_mining"],
                "efficiency_rating": 7
            },
            "model_d": {
                "cost": 40000,
                "description": "Heavy-duty model for large-scale operations.",
                "suitable_for": ["strip_mining", "mountain_top_removal"],
                "efficiency_rating": 8
            },
            "model_e": {
                "cost": 50000,
                "description": "High-performance model with specialized features.",
                "suitable_for": ["underground_mining", "platinum_mining", "open_pit_mining"],
                "efficiency_rating": 10
            }
        }
        self.log_file = 'ev_cost_calculator_log.txt'
        self.mining_types = {
            "surface_mining": "Surface mining involves the removal of overburden to extract minerals.",
            "strip_mining": "Strip mining involves stripping away overburden to access the ore.",
            "underground_mining": "Underground mining involves the extraction of minerals from beneath the surface.",
            "mountain_top_removal": "Mountain top removal involves blasting the top off a mountain to access minerals.",
            "platinum_mining": "Platinum mining involves extracting platinum from ore bodies, often in deep underground mines.",
            "open_pit_mining": "Open pit mining involves creating a large pit to extract minerals from the surface."
        }

    def get_ev_data(self, model):
        model = model.lower()
        return self.ev_data.get(model, {})

    def display_available_models(self):
        print("Available EV models:")
        for model in self.ev_data:
            print(f"- {model.replace('_', ' ').title()}")

    def log_query(self, model, data):
        with open(self.log_file, 'a') as file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if data:
                cost = data.get("cost")
                description = data.get("description")
                suitable_for = ", ".join(data.get("suitable_for", []))
                efficiency = data.get("efficiency_rating")
                file.write(f"{timestamp} - Model: {model.replace('_', ' ').title()}, Cost: ${cost}, Description: {description}, Suitable for: {suitable_for}, Efficiency Rating: {efficiency}\n")
            else:
                file.write(f"{timestamp} - Model: {model.replace('_', ' ').title()}, Result: Not Found\n")

    def handle_single_query(self):
        model = input("Enter the EV model (e.g., model_a): ").strip().lower()
        data = self.get_ev_data(model)
        if data:
            cost = data.get("cost")
            description = data.get("description")
            suitable_for = data.get("suitable_for")
            efficiency = data.get("efficiency_rating")
            self.display_cost(model, cost, description, suitable_for, efficiency)
            self.log_query(model, data)
        else:
            self.display_cost(model, None, "Not Available", None, None)
            self.log_query(model, None)

    def handle_multiple_queries(self):
        models = input("Enter multiple EV models separated by commas (e.g., model_a, model_b): ").strip().lower()
        models = [model.strip() for model in models.split(',')]
        for model in models:
            data = self.get_ev_data(model)
            if data:
                cost = data.get("cost")
                description = data.get("description")
                suitable_for = data.get("suitable_for")
                efficiency = data.get("efficiency_rating")
                self.display_cost(model, cost, description, suitable_for, efficiency)
                self.log_query(model, data)
            else:
                self.display_cost(model, None, "Not Available", None, None)
                self.log_query(model, None)

    def display_cost(self, model, cost, description, suitable_for, efficiency):
        if cost is not None:
            print(f"\nThe cost of {model.replace('_', ' ').title()} is ${cost}.")
            print(f"Description: {description}")
            print(f"Suitable for: {', '.join([t.replace('_', ' ').title() for t in suitable_for])}")
            print(f"Efficiency Rating: {efficiency} / 10")
        else:
            print("\nModel not found. Please enter a valid model.")
            print("Description: Not Available")
            print("Suitable for: Not Available")
            print("Efficiency Rating: Not Available")

    def display_mining_types(self):
        print("\nMining Types:")
        for key, value in self.mining_types.items():
            print(f"- {key.replace('_', ' ').title()}: {value}")

    def display_menu(self):
        print("\nEV Vehicle Cost Calculator Menu")
        print("1. Query a single EV model")
        print("2. Query multiple EV models")
        print("3. Display available models")
        print("4. Display mining types and descriptions")
        print("5. Exit")

    def prompt_user_choice(self):
        self.display_menu()
        choice = input("Enter your choice (1-5): ").strip()
        return choice

    def run(self):
        while True:
            choice = self.prompt_user_choice()
            if choice == '1':
                self.handle_single_query()
            elif choice == '2':
                self.handle_multiple_queries()
            elif choice == '3':
                self.display_available_models()
            elif choice == '4':
                self.display_mining_types()
            elif choice == '5':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    calculator = EVCostCalculator()
    try:
        calculator.run()
    except KeyboardInterrupt:
        sys.exit("\nOperation cancelled by the user.")
    except Exception as e:
        sys.exit(f"An unexpected error occurred: {e}")
