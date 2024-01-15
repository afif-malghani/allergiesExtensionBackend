import mysql.connector
import requests
from bs4 import BeautifulSoup

def connectDB():
    cnx = mysql.connector.connect(user='test', password='Test123!',
                                host='localhost',
                                database='allergen_blocker')
    return cnx

def getAllergens(user_id):
    cnx = connectDB()
    cursor = cnx.cursor()
    
    query = ("SELECT * FROM allergens")
    cursor.execute(query)
    result = cursor.fetchall()
    
    cnx.commit()
    cnx.close()
    
    allergens = {}
    if len(result) == 0:
        return allergens
    
    for row in result:
        allergens[row[0]] = row[1]
    
    cnx = connectDB()
    cursor = cnx.cursor()
    
    query = ("SELECT * FROM user_allergens where user_id = %s")
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    
    cnx.commit()
    cnx.close()
    
    if len(result) == 0:
        return allergens
    
    for row in result:
        allergens[row[1]] = allergens[row[1]] + " (selected)"
    
    return allergens

def getUserAllergensIDs(user_id):
    cnx = connectDB()
    cursor = cnx.cursor()
    
    query = ("SELECT * FROM user_allergens WHERE user_id = %s")
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    
    cnx.commit()
    cnx.close()
    
    allergen_ids = []
    
    if len(result) == 0:
        return allergen_ids
    
    for row in result:
        allergen_ids.append(row[1])
    
    return allergen_ids

def getAllergensNames(allergen_ids):
    allergen_names = []
    cnx = connectDB()
    cursor = cnx.cursor()
    
    for allergen_id in allergen_ids:
        cnx = connectDB()
        cursor = cnx.cursor()
        query = ("SELECT allergen_name FROM allergens WHERE allergen_id = %s")
        cursor.execute(query, (allergen_id,))
        result = cursor.fetchall()
        cnx.commit()
        cnx.close()
        if len(result) > 0:
            allergen_names.append(result[0][0])
        else:
            pass
    
    
    return allergen_names

def getIngredientsCarrefore(url):
    
    ingredientsList = []
    
    page = requests.get(url)
                
    # print(page.text)
    
    soup = BeautifulSoup(page.text, 'html.parser')

    # find the t
    ingredient_tag = soup.find(text='Ingredients')
    
    
    
    print("Ingredients Tag: ", ingredient_tag)
    
    
    
    if ingredient_tag:
        
        parentHtml = ingredient_tag.find_parent()
        
        if not parentHtml:
            return ingredientsList
        
        parentDiv = parentHtml.find_parent()
        
        if not parentDiv:
            return ingredientsList
        
        
        # find the child div and get its contents
        child_div = parentDiv.find('div')
        
        
        if child_div:
            # replace all span elements with a comma
            for span in child_div.find_all('span'):
                span.replace_with(', ')
            
            ingredientsList = child_div.get_text(strip=True).split(',')
    
    return ingredientsList

def getIngredientsAmazon(url):
    
    print("getting ingredients from amazon")
    
    # get page form the url
    page = requests.get(url)
    
    # parse the page
    soup = BeautifulSoup(page.text, 'html.parser')
    
    print("soup: ", soup)
    
    # find div with id 'important-information'
    important_info_div = soup.find(id='important-information')
    
    print("important info div: ", important_info_div)
    
    # if the div is found look for the 'Ingredients' tag
    if important_info_div:
        # find the 'Ingredients' tag
        ingredient_tag = important_info_div.find(text='Ingredients')
        
        # if the tag is found, find the parent div
        if ingredient_tag:
            parent_div = ingredient_tag.find_parent()
            
            # if the parent div is found, find the child div
            if parent_div:
                child_div = parent_div.find('div')
                
                # if the child div is found, get its text
                if child_div:
                    ingredients = child_div.get_text(strip=True)
                    
                    # if the text is not empty, split it by comma and return
                    if ingredients:
                        return ingredients.split(',')
    else:
        return []

def getIngredientsWalmart(url):
    pass


def addUserAllergens(user_id, allergens):
    for allergen in allergens:
        # add allergen to user
        cnx = connectDB()
        cursor = cnx.cursor()
        
        query = ("INSERT INTO user_allergens (user_id, allergen_id) VALUES (%s, %s)")
        cursor.execute(query, (user_id, allergen))
        
        cnx.commit()
        cnx.close()
        
        print('allergen added')
    return True

def removeUserAllergens(user_id, allergens):
    for allergen in allergens:
        # remove allergen from user
        
        print(allergen)
        cnx = connectDB()
        cursor = cnx.cursor()
        
        query = ("DELETE FROM user_allergens WHERE user_id = %s AND allergen_id = %s")
        cursor.execute(query, (user_id, allergen))
        
        cnx.commit()
        cnx.close()
        
        print('allergen removed')
    return True

def getUserRole(user_id):
    cnx = connectDB()
    cursor = cnx.cursor()
    
    query = ("SELECT role FROM user_roles WHERE user_id = %s")
    cursor.execute(query, (user_id,))
    result = cursor.fetchall()
    
    cnx.commit()
    cnx.close()
    
    if len(result) == 0:
        return None
    
    return result[0][0]

def addUser(user_id):
    cnx = connectDB()
    cursor = cnx.cursor()
    
    print("adding user", user_id)
    
    # add user to users table with name set to default
    query = ("INSERT INTO users (user_id) VALUES (%s)")
    cursor.execute(query, (user_id,))
    
    cnx.commit()
    cnx.close()
    
    print("user added")
    
    # add user to user_roles table with role set to user
    cnx = connectDB()
    cursor = cnx.cursor()
    
    query = ("INSERT INTO user_roles (user_id, role) VALUES (%s, %s)")
    cursor.execute(query, (user_id, 'user'))
    
    cnx.commit()
    cnx.close()
    
    # return the role assigned
    return 'user'

def addAllergensFn(allergens):
    for allergen in allergens:
        # add allergen to user
        cnx = connectDB()
        cursor = cnx.cursor()
        
        query = ("INSERT INTO allergens (allergen_name) VALUES (%s)")
        cursor.execute(query, (allergen,))
        
        cnx.commit()
        cnx.close()
        
        print('allergen added')
    return True

def searchAllergensFn(allergen_name):
    cnx = connectDB()
    cursor = cnx.cursor()
    
    # search with like query with % on either side
    query = ("SELECT * FROM allergens WHERE allergen_name LIKE %s")
    cursor.execute(query, ('%'+allergen_name+'%',))
    result = cursor.fetchall()
    
    cnx.commit()
    cnx.close()
    
    if len(result) == 0:
        return False
    
    # make a dict of allergens
    allergens = {}
    for row in result:
        allergens[row[0]] = row[1]
        
        
    return allergens

def removeAllergensFn(allergen_ids):
    print(allergen_ids)
    for allergen_id in allergen_ids:
        # remove allergen from user
        cnx = connectDB()
        cursor = cnx.cursor()
        
        query = ("DELETE FROM allergens WHERE allergen_id = %s")
        cursor.execute(query, (allergen_id,))
        
        cnx.commit()
        cnx.close()
        
        print('allergen removed')
    return True
