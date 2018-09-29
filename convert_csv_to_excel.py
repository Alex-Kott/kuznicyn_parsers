import pandas as pd


if __name__ == "__main__":
    df = pd.read_csv("data.csv", sep=';')
    first_100_rows = df.head(100)

    excel_writer = pd.ExcelWriter("data.xlsx")
    first_100_rows.to_excel(excel_writer, 'Sheet 1', index=False)
    excel_writer.save()
