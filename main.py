#Student ID: 010988814

#Importing csv and datetime libraries
import csv
from datetime import datetime, timedelta

#Setting speed, the day, and the overall start time
speed = 18/60
day = datetime.now()
start_time = datetime(day.year, day.month, day.day, 8, 0, 0, 0)

#Class for individual package objects
class Package(object):
    def __init__(self, ID = None, truck = None, status = "HUB", time_loaded = None, time_delivered = None, address = "", city = None, state = None, zip = None, deadline = None):
        self.ID  = ID
        self.truck = truck
        self.status = status
        self.time_loaded = time_loaded
        self.time_delivered = time_delivered
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.deadline = deadline
        return

    #Prints all the package data
    def packagePrint(self):
        print("Package ID: ", self.ID)
        print("Package Delivered By Truck: ", self.truck)
        print("Package Status: ", self.status)
        print("Package Loaded onto truck at: ",self.time_loaded)
        print("Packaged Delivery Time :", self.time_delivered)
        print("Address: ", self.address)
        print("City: ", self.city)
        print("State: ", self.state)
        print("Zip Code: ", self.zip)
        return

#Hash table class to hold all packages
class hashT(object):
    def __init__(self, size = 20):
        self.size = size
        self.hash = []
        for i in range(self.size):
            self.hash.append([])
        return
    
    #Tested
    #Inserts packages into the hash table by key and inserts by the [ID, Package] pair.
    def insert(self, ID, package):
        key = hash(ID) % self.size
        if [ID, package] not in self.hash[key]:
            self.hash[key].append([ID, package])
        return
    
    #Tested
    #Updates the package associated with an ID in the hash table
    def update(self, ID, new_package):
        key = hash(ID) % self.size
        for pair in self.hash[key]:
            if pair[0] == ID:
                pair[1] = new_package
        return
    
    #Tested
    #Searches for a package in the hash table based on the package Id. Returns the package if it is found and None if it is not found.
    def search(self, ID):
        key = hash(ID) % self.size
        for pair in self.hash[key]:
            if pair[0] == ID:
                return pair[1]
        return None
    
    #Tested
    #prints the entire hash table
    def print_hash(self):
        print(self.hash)
        return
    
#Truck class for the three truck objects required
class Truck(object):
    
    def __init__(self, packages = None, location = "", time_now = None, time_left_hub = None):
        self.packages = packages
        self.location = location
        self.time_now = time_now
        self.time_left_hub = time_left_hub
        return
        
    #Tested
    #Takes a list of package ID numbers as input, searches the hash table for the assoicated packages, and puts those packages in the "packages_loaded" list which holds the packages that a truck is responsible for delivering.
    def load_packages(self, package_id_list, hash_table):
        packages_loaded = []
        for package in package_id_list:
            hash_table.search(package).status = "EN ROUTE"
            packages_loaded.append(hash_table.search(package))
        self.packages = packages_loaded

#Tested
#Uploads package data from the packageCSV.csv file into the package hash table.
def upload_package_data(file, hash_table):
    with open(file) as csv_package_file:
        csv_reader = csv.reader(csv_package_file, delimiter = ",")
        for row in csv_reader:
            package = Package()
            package.ID = int(str.strip(row[0]))
            package.address = str.strip(row[1])
            package.city = str.strip(row[2])
            package.state = str.strip(row[3])
            package.zip = str.strip(row[4])
            package.deadline = str.strip(row[5])
            hash_table.insert(package.ID, package)
    return hash_table

#Tested
#Uploads all the distance data from the "distanceCSV.csv" into a triangular symmetric matrix
def upload_distance_data(file):
    distance_matrix = []
    with open(file) as csv_file:
        count = 0
        csv_reader = csv.reader(csv_file, delimiter = ",")
        for row in csv_reader:
            dsitList = [float(x) for x in row[0 : count + 1]]
            distance_matrix.append(dsitList)
            count += 1
    return distance_matrix

#Tested
#Uploads all the address data from the "addressCSV.csv" file into a list called "addresses".
def upload_address_data(file):
    addresses = []
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ",")
        for row in csv_reader:
            addresses.append(str.strip(row[2]))
    return addresses

#Tested
#Determines the distance from one address to another based the address itself and the distance matrix.
def distance_to(address_from, address_to, addresses, distance_matrix):
    if (address_from not in addresses) or (address_to not in addresses):
        print("Not on truck")
        return
    else:
        i = addresses.index(address_from)
        j = addresses.index(address_to)
        if j <= i:
            return distance_matrix[i][j]
        else:
            return distance_matrix[j][i]

#Tested
#Delivers packages that are in the provided truck
def deliver_packages(truck, addresses, distance_matrix, package_hash):
    truck_populated = True
    total_distance = 0
    while truck_populated:
        current_package = next_closest_package(truck, addresses, distance_matrix, package_hash)
        if current_package == None:
            to_hub = distance_to(truck.location, addresses[0], addresses, distance_matrix)
            total_distance += to_hub
            truck.time_now += timedelta(minutes = float(to_hub/speed))
            truck.location = addresses[0]
            truck_populated = False
        else:
            #changes the delivery address of package 9 to the correct address at 10:20am when it is availabe to WGUPS.
            if truck == truck3 and truck.time_now >= datetime(day.year, day.month, day.day, 10, 20, 0, 0):
                package_hash.search(9).address = "410 S State St"
            #Makes sure package 9 isn't considered for delivery until 10:20am
            if current_package.ID == 9 and truck.time_now < datetime(day.year, day.month, day.day, 10, 20, 0, 0):
                deliverable_packages = addresses
                deliverable_packages.remove(9)
                print("deliverable packages: ", deliverable_packages)
                current_package = next_closest_package(truck, deliverable_packages, distance_matrix, package_hash)
            #Delivers all packages with the same address are delivered at the same time
            for package in truck.packages:
                if current_package.address == package.address:
                    package.status = "DELIVERED"
                    distance = distance_to(truck.location, package.address, addresses, distance_matrix)
                    truck.time_now = truck.time_now + timedelta(minutes = float(distance/speed))
                    package.time_delivered = truck.time_now
                    total_distance += distance
                    truck.location = package.address
    return total_distance

#Tested
#Determines the next closes package to the trucks current address
def next_closest_package(truck, addresses, distance_matrix, hash_table):
    package_distance_dict = dict()
    for package in truck.packages:
        if (package.address != truck.location) and (package.status != "DELIVERED"):
            package_distance_dict[package.ID] = distance_to(truck.location, package.address, addresses, distance_matrix)
    if len(package_distance_dict) > 0:
        # return hash_table.search(int(min(package_distance_dict, key = package_distance_dict.get)))
        return hash_table.search(int(min(package_distance_dict.items(), key = lambda x : x[1])[0]))
    else:
        return None

#Tested
#Sets up a truck based 
def set_truck(truck,truck_ID_list, truck_number, time):
    truck.time_now = time
    truck.time_left_hub = time
    truck.load_packages(truck_ID_list, package_hash)
    
    for ID in truck_ID_list:
        current_package = package_hash.search(ID)
        current_package.time_loaded = truck.time_left_hub
        current_package.truck = truck_number
    truck.location = addresses[0]

#Tested
#Creates the command line interface
def interface():
    print("Hello, this is the intuitive interface.")
    print("Input a time and the status of all packages will be printed at the provided time. If the package is at the HUB or EN ROUTE, the time displayed for that package will be the time you provided. If the package is delivered, the time displayed will be the time delivered for that package.")
    time = input("I would like to see the status of all packages at (24 hour clock - syntax - HH:MM): ")
    get_status_at_time(time)

#Tested
#Prints the status of all of the packages at a given time
def get_status_at_time(time):
    for i in range(1, 41):
        current_package = package_hash.search(i)
        package_delivery_time = current_package.time_delivered.strftime("%H:%M")
        package_ID = str(i)
        if  current_package.ID == 9 and time < datetime(day.year, day.month, day.day, 10, 20, 0, 0).strftime("%H:%M"):
            current_package.address = "300 State St"
        if  current_package.ID == 9 and time >= datetime(day.year, day.month, day.day, 10, 20, 0, 0).strftime("%H:%M"):
            current_package.address = "410 S State St"
        if current_package.ID in truck1_ID_list and time < truck1.time_left_hub.strftime("%H:%M"):
            print("Package " + package_ID)
            print("   Current Status: HUB " + time)
            print("   Delivery Address: " + current_package.address)
            print("   Deadline: " + current_package.deadline)
        elif current_package.ID in truck2_ID_list and time < truck2.time_left_hub.strftime("%H:%M"):
            print("Package " + package_ID)
            print("   Current Status: HUB " + time)
            print("   Delivery Address: " + current_package.address)
            print("   Deadline: " + current_package.deadline)
        elif current_package.ID in truck3_ID_list and time < truck3.time_left_hub.strftime("%H:%M"):
            print("Package " + package_ID)
            print("   Current Status: HUB " + time)
            print("   Delivery Address: " + current_package.address)
            print("   Deadline: " + current_package.deadline)
        elif package_delivery_time > time:
            print("Package " + package_ID)
            print("   Current Status: EN ROUTE " + time)
            print("   Delivery Address: " + current_package.address)
            print("   Deadline: " + current_package.deadline)
        elif package_delivery_time < time:
            print("Package " + package_ID)
            print("   Current Status: DELIVERED " + package_delivery_time)
            print("   Delivery Address: " + current_package.address)
            print("   Deadline: " + current_package.deadline)

#Load in address, distance, and package data
addresses = upload_address_data("addressCSV.csv")
distance_matrix = upload_distance_data("distanceCSV.csv")
package_hash = hashT()
upload_package_data("packageCSV.csv", package_hash)

#Set up truck one
truck1_ID_list = [15, 1, 13, 14, 16, 20, 29, 30, 31, 34, 37, 40, 39, 35]
truck1 = Truck()
set_truck(truck1, truck1_ID_list, "Truck One", start_time)

#Set up truck two
truck2_ID_list = [3, 18, 36, 38, 6, 25, 28, 32, 33, 27]
truck2 = Truck()
truck2_start_time = datetime(day.year, day.month, day.day, 9, 5, 0, 0)

set_truck(truck2, truck2_ID_list, "Truck Two", truck2_start_time)

#Set up truck three
truck3_ID_list = [2, 4, 5, 7, 8, 9, 10, 11, 12, 17, 19, 21, 22, 23, 24, 26]
truck3 = Truck()
truck3_start_time = min(truck1.time_now, truck2.time_now)
set_truck(truck3, truck3_ID_list, "Truck Three", truck3_start_time)

truck_one_total_distance = deliver_packages(truck1, addresses, distance_matrix, package_hash)
truck_two_total_distance = deliver_packages(truck2, addresses, distance_matrix, package_hash)
truck_three_total_distance = deliver_packages(truck3, addresses, distance_matrix, package_hash)

print("Total Distance Traveled: ", (truck_one_total_distance + truck_two_total_distance + truck_three_total_distance))
interface()
