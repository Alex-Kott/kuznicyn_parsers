import json
import csv

if __name__ == "__main__":
    with open("data.json") as file:
        parsed_products = json.loads(file.read())

    # for i in parsed_products:
    #     for k, v in i.items():
    #         print(k, v)
    #     exit()

    with open("data.csv", "w") as file:
        csv_writer = csv.writer(file, delimiter=';')
        csv_writer.writerow(["Product URL", "Category", "Title", "Product ID", "Manufacturer", "Description", "Availability", "Price", "Image(s)"])

        for item in parsed_products:
            csv_writer.writerow([v for k, v in item.items()])
