import random
import time
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque

# Ansluter till SQLite-databasen och sätter upp logg-tabellen
conn = sqlite3.connect("SIMSIMDATABASE.db")
conn.execute("DROP TABLE IF EXISTS simulationLog;")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS SimulationLog (
    step INTEGER PRIMARY KEY,
    workers INTEGER,
    food INTEGER,
    products INTEGER
)
""")
conn.commit()
conn.close()

# Klass: Worker - Representerar en arbetare
class Worker:
    # Konstruktor: Initierar en arbetare med id, vitality och plats
    def __init__(self, id, vitality=100):
        self.id = id
        self.vitality = vitality
        self.location = "Barrack"

    # Funktion: hurt - Minskar arbetarens vitality
    def hurt(self, amount):
        self.vitality -= amount
        if self.vitality < 0:
            self.vitality = 0

    # Funktion: heal - Ökar arbetarens vitality
    def heal(self, amount):
        self.vitality += amount
        if self.vitality > 100:
            self.vitality = 100

    # Funktion: return_life - Returnerar arbetarens vitality
    def return_life(self):
        return self.vitality

# Klass: Food - Representerar mat
class Food:
    # Konstruktor: Initierar mat med id och kvalitet
    def __init__(self, id, quality=1):
        self.id = id
        self.quality = quality

    # Funktion: return_quality - Returnerar matens kvalitet
    def return_quality(self):
        return self.quality

# Klass: Product - Representerar en produkt
class Product:
    # Konstruktor: Initierar en produkt med id och kvalitet
    def __init__(self, id, quality=1):
        self.id = id
        self.quality = quality

    # Funktion: return_quality - Returnerar produktens kvalitet
    def return_quality(self):
        return self.quality

# Klass: Barrack - Hanterar en kö av arbetare
class Barrack:
    # Konstruktor: Initierar en barrack med en deque för arbetare
    def __init__(self):
        self.queue = deque()

    # Funktion: in_worker - Lägger till en arbetare i barracken
    def in_worker(self, worker):
        worker.location = "Barrack"
        self.queue.append(worker)

    # Funktion: out_worker - Tar ut en arbetare från barracken
    def out_worker(self):
        if self.queue:
            return self.queue.popleft()

    # Funktion: exist_worker - Kontrollerar om det finns arbetare i barracken
    def exist_worker(self):
        return len(self.queue) > 0

# Klass: Storage - Hanterar lagring av produkter
class Storage:
    # Konstruktor: Initierar ett förråd med en deque för produkter
    def __init__(self):
        self.storage = deque()

    # Funktion: in_product - Lägger till en produkt i förrådet
    def in_product(self, product):
        self.storage.append(product)

    # Funktion: out_product - Tar ut en produkt från förrådet
    def out_product(self):
        if self.storage:
            return self.storage.popleft()

    # Funktion: exist_product - Kontrollerar om det finns produkter i förrådet
    def exist_product(self):
        return len(self.storage) > 0

# Klass: Shed - Hanterar lagring av mat
class Shed:
    # Konstruktor: Initierar en lada med en deque för mat
    def __init__(self):
        self.queue = deque()

    # Funktion: in_food - Lägger till en matvara i ladan
    def in_food(self, food):
        self.queue.append(food)

    # Funktion: out_food - Tar ut en matvara från ladan
    def out_food(self):
        if self.queue:
            return self.queue.popleft()

    # Funktion: exist_food - Kontrollerar om det finns mat i ladan
    def exist_food(self):
        return len(self.queue) > 0

# Klass: Factory - Representerar en fabrik för att producera produkter
class Factory:
    # Konstruktor: Initierar en fabrik med input/output barrack och förråd
    def __init__(self, barrack_in, barrack_out, storage, set_active=True):
        self.barrack_in = barrack_in
        self.barrack_out = barrack_out
        self.storage = storage
        self.set_active = set_active
        self.name = "Factory"

    # Funktion: produce - Producerar en produkt med hjälp av en arbetare
    def produce(self):
        if self.set_active:
            worker = self.barrack_in.out_worker()
            if worker:
                worker.location = "Factory"
                worker.hurt(random.randint(1, 3))
                if worker.return_life() > 0:
                    self.storage.in_product(Product(id=0))
                    self.barrack_out.in_worker(worker)
                else:
                    print("Worker died in the factory")
        else:
            return None

# Klass: Home - Representerar ett hem som kan öka befolkningen
class Home:
    # Konstruktor: Initierar ett hem med input/output barrack, förråd och referens till simulationen
    def __init__(self, barrack_in, barrack_out, storage, simulation, set_active=True):
        self.barrack_in = barrack_in
        self.barrack_out = barrack_out
        self.storage = storage
        self.simulation = simulation
        self.set_active = set_active
        self.name = "Home"

    # Funktion: produce - Producerar genom att använda en arbetare och en produkt för att skapa en ny arbetare
    def produce(self):
        if self.set_active:
            worker1 = self.barrack_in.out_worker()
            if worker1:
                worker1.location = "Home"
                product = self.storage.out_product()
                if product:
                    worker1.heal(random.randint(10, 20))
                    worker2 = self.barrack_in.out_worker()
                    if worker2:
                        new_worker_id = self.simulation.count_total_workers()
                        self.barrack_out.in_worker(Worker(id=new_worker_id + 1))
                        self.barrack_out.in_worker(worker1)
                        self.barrack_out.in_worker(worker2)
                    else:
                        self.barrack_out.in_worker(worker1)
                else:
                    print("No product available in Home.produce")
            else:
                print("No worker available in Home.produce")
        else:
            return None

# Klass: Farm - Representerar en gård för att producera mat
class Farm:
    # Konstruktor: Initierar en gård med input/output barrack och lada
    def __init__(self, barrack_in, barrack_out, shed, set_active=True):
        self.barrack_in = barrack_in
        self.barrack_out = barrack_out
        self.shed = shed
        self.set_active = set_active
        self.name = "Farm"

    # Funktion: produce - Producerar mat med hjälp av en arbetare
    def produce(self):
        if self.set_active:
            worker = self.barrack_in.out_worker()
            if worker:
                worker.location = "Field"
                self.shed.in_food(Food(id=0))
                self.barrack_out.in_worker(worker)
            else:
                print("No worker available in Farm.produce")
        else:
            return None

# Klass: Foodcourt - Representerar en matplats där mat bearbetas
class Foodcourt:
    # Konstruktor: Initierar en matplats med input/output barrack och lada
    def __init__(self, barrack_in, barrack_out, shed, set_active=True):
        self.barrack_in = barrack_in
        self.barrack_out = barrack_out
        self.shed = shed
        self.set_active = set_active
        self.name = "Foodcourt"

    # Funktion: produce - Producerar genom att bearbeta mat med en arbetare
    def produce(self):
        if self.set_active:
            worker = self.barrack_in.out_worker()
            food = self.shed.out_food()
            if worker and food:
                worker.location = "Foodcourt"
                if food.return_quality() == 1:
                    worker.heal(food.return_quality() * random.randint(1, 10))
                else:
                    worker.hurt(random.randint(1, 5))
                self.barrack_out.in_worker(worker)
            elif worker:
                self.barrack_out.in_worker(worker)
            else:
                print("No worker available in Foodcourt.produce")
        else:
            return None

# Klass: main - Huvudklassen för att köra simulationen
class main():
    # Konstruktor: Initierar alla byggnader, resurser och databasanslutning
    def __init__(self):
        self.barracks = [Barrack(), Barrack()]  # Två barracker
        self.storages = [Storage()]             # Ett förråd
        self.sheds = [Shed(), Shed()]            # Två lador
        self.factories = [
            Factory(self.barracks[0], self.barracks[1], self.storages[0]),
            Factory(self.barracks[0], self.barracks[1], self.storages[0])
        ]
        self.homes = [
            Home(self.barracks[1], self.barracks[0], self.storages[0], self),
            Home(self.barracks[0], self.barracks[1], self.storages[0], self),
            Home(self.barracks[0], self.barracks[0], self.storages[0], self),
            Home(self.barracks[1], self.barracks[1], self.storages[0], self)
        ]
        self.farms = [
            Farm(self.barracks[0], self.barracks[0], self.sheds[0]),
            Farm(self.barracks[1], self.barracks[1], self.sheds[0])
        ]
        self.foodcourts = [
            Foodcourt(self.barracks[0], self.barracks[0], self.sheds[0]),
            Foodcourt(self.barracks[0], self.barracks[1], self.sheds[0]),
            Foodcourt(self.barracks[1], self.barracks[0], self.sheds[0])
        ]
        self.transitions = self.factories + self.homes + self.farms + self.foodcourts
        self.resources = []

        worker_id = 0
        product_id = 0
        food_id = 0

        # Funktion: Lägg till arbetare i varje barrack
        for barrack_instance in self.barracks:
            for _ in range(100):
                worker = Worker(id=worker_id)
                barrack_instance.in_worker(worker)
                worker_id += 1
            self.resources.append(barrack_instance)
        # Funktion: Lägg till produkter i varje förråd
        for storage_instance in self.storages:
            for _ in range(200):
                product = Product(id=product_id)
                storage_instance.in_product(product)
                product_id += 1
            self.resources.append(storage_instance)
        # Funktion: Lägg till mat i varje lada
        for shed_instance in self.sheds:
            for _ in range(100):
                food = Food(id=food_id)
                shed_instance.in_food(food)
                food_id += 1
            self.resources.append(shed_instance)

        self.connection = sqlite3.connect("SIMSIMDATABASE.db")
        self.curr = self.connection.cursor()

    # Funktion: evaluate_resource_balance - Utvärderar resursbalansen och bestämmer prioriterade byggnader
    def evaluate_resource_balance(self):
        total_workers = self.count_total_workers()
        total_food = self.count_total_food()
        total_products = self.count_total_products()

        resources = {
            'workers': total_workers,
            'food': total_food,
            'products': total_products
        }
        lowest_resource = min(resources.items(), key=lambda x: x[1])

        # Använd en snäv marginal (0.8 istället för 0.75) för att fånga obalanser tidigare
        if all(lowest_resource[1] < 0.8 * count for res, count in resources.items() if res != lowest_resource[0]):
            if lowest_resource[0] == 'workers':
                return self.homes
            elif lowest_resource[0] == 'food':
                return self.farms
            elif lowest_resource[0] == 'products':
                return self.factories

        return []

    # Funktion: count_total_products - Räknar totala antalet produkter
    def count_total_products(self):
        return sum(len(storage.storage) for storage in self.storages)

    # Funktion: count_total_food - Räknar totala antalet matvaror
    def count_total_food(self):
        return sum(len(shed.queue) for shed in self.sheds)

    # Funktion: count_total_workers - Räknar totala antalet arbetare
    def count_total_workers(self):
        return sum(len(barrack.queue) for barrack in self.barracks)

    # Funktion: print_simulation_status - Skriver ut simulationens status efter ett steg
    def print_simulation_status(self, step):
        print(f"\nStatus after step {step}:")
        print(f"Workers in barrack in: {len(self.barracks[0].queue)}")
        print(f"Workers in barrack out: {len(self.barracks[1].queue)}")
        print(f"Food in shed: {len(self.sheds[0].queue)}")
        print(f"Products in storage: {len(self.storages[0].storage)}")

    # Funktion: plot_simulation_data - Plottar simulationens data från databasen
    def plot_simulation_data(self, db_path):
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM SimulationLog", conn)
        conn.close()
        plt.figure(figsize=(10, 6))
        plt.plot(df['step'], df['workers'], label='Workers', color='blue')
        plt.plot(df['step'], df['food'], label='Food', color='green')
        plt.plot(df['step'], df['products'], label='Products', color='red')
        plt.xlabel('Simulation Step')
        plt.ylabel('Quantity')
        plt.title('Simulation Data Over Time')
        plt.legend()
        plt.grid(True)
        plt.show()

    # Funktion: export_table_to_excel - Exporterar simulationens data till en Excel-fil
    def export_table_to_excel(self, db_path, excel_path):
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM SimulationLog", conn)
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='SimulationLog', index=False)
        conn.close()

    # Funktion: log_simulation_status - Loggar simulationens status i databasen
    def log_simulation_status(self, step):
        workers_count = len(self.barracks[0].queue) + len(self.barracks[1].queue)
        food_count = sum(len(shed.queue) for shed in self.sheds)
        products_count = len(self.storages[0].storage)

        self.curr.execute("SELECT COUNT(*) FROM SimulationLog WHERE step = ?", (step,))
        count = self.curr.fetchone()[0]

        if count == 0:
            self.curr.execute("""
            INSERT INTO SimulationLog (step, workers, food, products)
            VALUES (?, ?, ?, ?)
            """, (step, workers_count, food_count, products_count))
        else:
            self.curr.execute("""
            UPDATE SimulationLog
            SET workers = ?, food = ?, products = ?
            WHERE step = ?
            """, (workers_count, food_count, products_count, step))

        self.connection.commit()
        print(f"Step {step}: Workers={workers_count}, Food={food_count}, Products={products_count}")

    # Funktion: _add_random_resources - Intervention: Lägger till slumpmässiga resurser för att bryta stagnation
    def _add_random_resources(self):
        print("Intervention: Adding random resources")
        new_workers = random.randint(10, 30)
        for _ in range(new_workers):
            worker_id = self.count_total_workers() + 1
            worker = Worker(id=worker_id, vitality=random.randint(50, 100))
            random.choice(self.barracks).in_worker(worker)
        new_food = random.randint(20, 40)
        for _ in range(new_food):
            food_id = random.randint(1, 1000)
            food = Food(id=food_id, quality=random.randint(1, 2))
            random.choice(self.sheds).in_food(food)
        new_products = random.randint(15, 35)
        for _ in range(new_products):
            product_id = random.randint(1, 1000)
            product = Product(id=product_id, quality=random.randint(1, 3))
            self.storages[0].in_product(product)
        print(f"Added {new_workers} workers, {new_food} food, and {new_products} products")

    # Funktion: _shift_resource_balance - Intervention: Tar bort en procentandel av den mest överflödiga resursen
    def _shift_resource_balance(self):
        print("Intervention: Shifting resource balance")
        workers = self.count_total_workers()
        food = self.count_total_food()
        products = self.count_total_products()
        resources = {"workers": workers, "food": food, "products": products}
        most_abundant = max(resources.items(), key=lambda x: x[1])[0]

        if most_abundant == "workers":
            remove_count = int(workers * 0.3)
            removed = 0
            for barrack in self.barracks:
                while barrack.queue and removed < remove_count:
                    barrack.queue.pop()
                    removed += 1
            print(f"Removed {removed} workers")
        elif most_abundant == "food":
            remove_count = int(food * 0.2)
            removed = 0
            for shed in self.sheds:
                while shed.queue and removed < remove_count:
                    shed.queue.pop()
                    removed += 1
            print(f"Removed {removed} food items")
        elif most_abundant == "products":
            remove_count = int(products * 0.2)
            removed = 0
            while self.storages[0].storage and removed < remove_count:
                self.storages[0].storage.pop()
                removed += 1
            print(f"Removed {removed} products")

    # Funktion: run_simulation - Kör simulationen och hanterar interveneringar
    def run_simulation(self):
        step = 0
        previous_counts = []
        stagnation_counter = 0
        stagnation_threshold = 15

        while step < 900:
            try:
                print(f"\nSimulation step {step}:")
                if not any(barrack.exist_worker() for barrack in self.barracks):
                    print("All workers have died, simulation ending...")
                    break

                current_counts = {
                    'workers': self.count_total_workers(),
                    'food': self.count_total_food(),
                    'products': self.count_total_products()
                }

                if len(previous_counts) > stagnation_threshold:
                    is_stagnant = True
                    for prev_count in previous_counts[-stagnation_threshold:]:
                        if any(abs(current_counts[res] - prev_count[res]) > 5 for res in current_counts):
                            is_stagnant = False
                            break
                    if is_stagnant:
                        stagnation_counter += 1
                        print(f"Stagnation detected! Counter: {stagnation_counter}")
                        if stagnation_counter % 2 == 0:
                            self._add_random_resources()
                        else:
                            self._shift_resource_balance()
                    else:
                        stagnation_counter = 0

                previous_counts.append(current_counts)
                if len(previous_counts) > stagnation_threshold + 5:
                    previous_counts.pop(0)

                # Återställ alla byggnader till inaktiva
                for building in self.transitions:
                    building.set_active = False

                # NY: Slumpmässigt välj en byggnad som ska producera varje steg
                t = random.choice(self.transitions)
                t.set_active = True
                try:
                    t.produce()
                except Exception as e:
                    print(f"Error in {t.name}.produce() in step {step}: {e}")

                self.print_simulation_status(step)
                self.log_simulation_status(step)

                if not any(storage.exist_product() for storage in self.storages):
                    print("No products left in storage, simulation ending...")
                    break

                time.sleep(0.01)
                step += 1
            except Exception as e:
                print(f"Unexpected error in simulation loop: {e}")

        self.export_table_to_excel("SIMSIMDATABASE.db", "simulation_data.xlsx")
        self.plot_simulation_data("SIMSIMDATABASE.db")
        self.connection.close()

# Huvudprogram: Startar simulationen
if __name__ == "__main__":
    simulation = main()
    simulation.run_simulation()