if __name__ == "__main__":
    with open("data.csv") as file:
        lines = [line.strip('\n') for line in file.readlines()]

    with open("data.json", "w") as file:
        text = ',\n'.join(lines)
        file.write(f"[{text}]")

    # with open("failed_products.txt") as file:
    #     lines = [line.strip('\n') for line in file.readlines() if line.strip(' \n') != '']
    #
    # with open("failed_products.txt", "w") as file:
    #     for line in lines:
    #         file.write(f"{line}\n")