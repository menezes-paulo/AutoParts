# import mysql.connector


# banco = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="autoparts"
# )


# veiculos = []


# for versao in ["EX", "EXL", "LX"]:
#     veiculos.append(("HR-V", 2022, versao, "1.5"))


# for ano in range(2023, 2027):
#     for versao in ["ADV", "EX", "EXL", "TOUR"]:
#         veiculos.append(("HR-V", ano, versao, "1.5"))


# for ano in range(2022, 2024):
#     for versao in ["EXL", "EX", "TOUR"]:
#         veiculos.append(("CITY SEDAN", ano, versao, "1.5"))


# for ano in range(2024, 2027):
#     for versao in ["EXL", "EX", "LX", "TOUR"]:
#         veiculos.append(("CITY SEDAN", ano, versao, "1.5"))


# for ano in range(2022, 2024):
#     for versao in ["EXL", "TOUR"]:
#         veiculos.append(("CITY HATCHBACK", ano, versao, "1.5"))


# for ano in range(2024, 2027):
#     for versao in ["EX", "EXL", "LX", "TOUR"]:
#         veiculos.append(("CITY HATCHBACK", ano, versao, "1.5"))


# for ano in range(2015, 2022):
#     for versao in ["DX", "EX", "EXL", "LX"]:
#         veiculos.append(("FIT", ano, versao, "1.5"))


# for ano in range(2017, 2022):
#     for versao in ["EX", "EXL"]:
#         veiculos.append(("CIVIC", ano, versao, "2.0"))


# for ano in range(2017, 2022):
#     for versao in ["TOUR"]:
#         veiculos.append(("CIVIC", ano, versao, "1.5"))


# cursor = banco.cursor()


# sql = """
#     INSERT INTO veiculos (modelo, ano, versao, motorizacao)
#     VALUES (%s, %s, %s, %s)
# """


# cursor.executemany(sql, veiculos)

# banco.commit()


# print(f"{cursor.rowcount} veículos cadastrados com sucesso!")


# cursor.close()
# banco.close()