import pandas as pd
import mysql.connector

# MySQL connection details
mysql_config = {
    'user': 'test',
    'password': 'Password123!',
    'host': 'localhost',
    'database': 'allergen_blocker'
}

# CSV file path
csv_file = 'FoodData.csv'

def import_data():
    # Read CSV file
    df = pd.read_csv(csv_file)

    # Establish MySQL connection
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor()

    try:
        # Iterate through rows and insert into allergens table
        for index, row in df.iterrows():
            allergen_name = row['Food']
            cursor.execute("INSERT INTO allergens (allergen_name) VALUES (%s);", (allergen_name,))

        # Commit changes
        connection.commit()
        print("Data imported successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close connections
        cursor.close()
        connection.close()

if __name__ == "__main__":
    import_data()

