from flask import Flask, request, make_response, render_template
from flask_restful import Api, Resource
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
# from utils import getUserAllergensIDs, getAllergensNames, getProductIngredients, getAllergens, addUserAllergens, removeUserAllergens, getUserRole, addUser, addAllergensFn, searchAllergensFn
from utils import *


class HelloWorld(Resource):
    def get(self):
        # render index.html 
        return make_response(render_template('index.html'))
    
    def post(self):
        request.json['user_id']
        role = getUserRole(request.json['user_id'])
        if role == None:
            role = addUser(request.json['user_id'])
        
        return {'message': 'success', 'role': role}

class CheckAllergies(Resource):
    def post(self):
        try:
            user_id = request.json['user_id']
            product_link = request.json['product_link']
        except:
            print(request.json)
            return {'status': 'error'}
        
        
        print(request.json)
        user_allergies = getUserAllergensIDs(user_id)
        
        if len(user_allergies) > 0:
            
            # if product_link is a list, check all of them
            if isinstance(product_link, list):
                # print("got list")
                allergic_to_products = []
                # print(user_allergies)
                for link in product_link:
                    allergen_names = getAllergensNames(user_allergies)
                    
                    if len(allergen_names) > 0:
                        
                        # get the product page html
                        # url = "https://www.carrefouruae.com/mafuae/en/"+ link
                        
                        
                        ingredientsList = getIngredientsCarrefore(link)
                        
                        # print(ingredientsList)
                        
                        for ingredient in ingredientsList:
                            for allergen in allergen_names:
                                # print("checking for {} in {}".format(allergen, ingredient))
                                if allergen.lower() in ingredient.lower():
                                    allergic_to_products.append(link)
                                    # print(allergic_to_products)
                                    print('allergen found') 
                                else:
                                    pass
                                               
                    else:
                        return {'status': 'no allergies'}
                print("returning response: ", allergic_to_products)
                return {'status': 'allergies', 'allergies': allergic_to_products}
            elif isinstance(product_link, str):
                allergen_names = getAllergensNames(user_allergies)
                
                allergens_present = []
                if len(allergen_names) > 0:
                    
                    # get the product page html
                    url = "https://www.carrefouruae.com/mafuae/en/"+ product_link
                    
                    
                    ingredientsList = getIngredientsCarrefore(url)
                    
                    for ingredient in ingredientsList:
                        for allergen in allergen_names:
                            print("checking for {} in {}".format(allergen, ingredient))
                            if allergen.lower() in ingredient.lower():
                                allergens_present.append(allergen)
                                print(allergens_present)
                                print('allergen found') 
                                return {'status': 'allergies', 'allergies': allergens_present}
                            else:
                                pass
                    return {'status': 'no allergies'}
                                           
                else:
                    return {'status': 'no allergies'}
        else:
            return {'status': 'no allergies'}
        

class saveAllergies(Resource):
    def post(self):
        # get user id and allergies
        try:
            user_id = request.json['user_id']
            allergies = request.json['allergies']
        except:
            print(request.json)
            return {'status': 'error'}
        
        # get user allergies
        
        print(allergies)
        
        print(user_id)
        
        user_allergies = getUserAllergensIDs(user_id)
        
        print(user_allergies)
        
        allergies = [int(x) for x in allergies]
        
        toAdd = []
        toRemove = []
        
        # if an item is in allergeis but not in user_allergies, add it
        # if an item is in user_allergies but not in allergies, remove it
        for allergy in allergies:
            if allergy not in user_allergies:
                toAdd.append(allergy)
        for user_allergy in user_allergies:
            if user_allergy not in allergies:
                toRemove.append(user_allergy)
        
        # add new allergies
        addUserAllergens(user_id, toAdd)
        
        # remove old allergies
        removeUserAllergens(user_id, toRemove)
        
        
        
        return {'status': 'success'}
    

class getList(Resource):
    
    # recieve post reuqeust with user id
    def post(self):
        user_id = request.json['user_id']
        
        allergens = getAllergens(user_id)
        
        # return list of allergen names
        return {'allergens': allergens}
    

class addAllergens(Resource):
    def post(self):
        allergensList = request.json['allergens']
        addAllergensFn(allergensList)
        return {'message': 'success'}


class searchAllergens(Resource):
    def post(self):
        allergen = request.json['allergen']
        allergens = searchAllergensFn(allergen)
        return {'message':"success",  'allergens': allergens}
        
        
class removeAllergens(Resource):
    def post(self):
        allergenIDs = request.json['allergens']
        removeAllergensFn(allergenIDs)
        return {'message': 'success'}


# test routes to be removed in production
class testAmazonScrapper(Resource):
    def post(self):
        # get URL from request
        url = request.json['url']
        print("got url: ", url)
        return {'ingredients': getIngredientsAmazon(url)}

# test routes to be removed in production
class testWalmartScrapper(Resource):
    def post(self):
        url = request.json['url']
        return {'ingredients': getIngredientsWalmart(url)}


app = Flask(__name__)
api = Api(app)

CORS(app, resources={r"/*": {"origins": "*"}})


api.add_resource(HelloWorld, '/')
api.add_resource(CheckAllergies, '/allergies')
api.add_resource(saveAllergies, '/settings')
api.add_resource(getList, '/allergens-all')
api.add_resource(addAllergens, '/add-allergens')
api.add_resource(searchAllergens, '/search-allergens')
api.add_resource(removeAllergens, '/remove-allergens')


# test routes to be removed in production
api.add_resource(testAmazonScrapper, '/test-amazon')
api.add_resource(testWalmartScrapper, '/test-walmart')




if __name__ == '__main__':
    app.run(debug=True)
