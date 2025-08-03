import pandas as pd

# Create the data
data = [
    ("Amiens Stephen", "Psychology of Money"),
    ("Annointing Omamuzo", "How to win friends and influence people"),
    ("Adejare Isaac", ""),
    ("Robert Monday Ndikponke", "The winning ticket; The power of choice"),
    ("Favour Ojieriakhi", "how to talk to anyone"),
    ("Godswill Stephen", "Atomic habits"),
    ("Success", "Secrets of the millionaire mind"),
    ("Hannah Favour Oviawele", "How to win friends and influence people"),
    ("Moses Felix", "The power of your mind"),
    ("Obiekwe Chioma", "Rich Dad, poor Dad"),
    ("Favour Iyare", "The pursuit of God; Good morning, Holy Spirit"),
    ("Anna Osasogie", "The 360° leader; The quick and easy way to effective speaking"),
    ("Gift Aladejare", "How to win friends and influence people"),
    ("Ibude Precious", "The practice of Entrepreneurship in Nigeria"),
    ("Sharon Efevberha", "How to win friends and influence people"),
    ("Onyemesim Anita", "The psychology of money")
]

# Create DataFrame
df = pd.DataFrame(data, columns=["Name", "Book(s)"])

# Save as CSV
file_path = "Book_List.csv"
df.to_csv(file_path, index=False)

print(f'Done. Ssved to {file_path}')