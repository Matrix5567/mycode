from bs4 import BeautifulSoup
import requests
from PIL import Image
import io
import urllib.request
import shutil
import django
import sys
import os
import json


project_dir_path = os.path.abspath(os.getcwd())
sys.path.append(project_dir_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerceweb.settings')
django.setup()



from eweb.models import Product
import django
import sys
import os
import json
import io
from django.core.files.images import ImageFile
#Product.objects.all().delete()
items = ['mobiles','televisions']
urls = ['tyy,4io&otracker=categorytree','ckf,czl&otracker=categorytree']
for item in items:
    if item == 'mobiles':
        url = 'tyy,4io&otracker=categorytree'
    else:
        url = 'ckf,czl&otracker=categorytree'
    for i in range(1, 6):
        url = f"https://www.flipkart.com/{item}/pr?sid={url}&page={i}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")                         #mobile and television
        product_div_links = soup.find_all("div", class_='_13oc-S')
        for objects in product_div_links:
            image_tag = objects.findChildren("img")
            product_name = objects.find("div",class_='_4rR01T').text
            product_description = objects.find("div",class_='fMghEO').text
            product_actualamount = objects.find("div", class_='_3I9_wc _27UcVY').text if objects.find("div",
                                                                                                      class_='_3I9_wc _27UcVY') else " "
            product_discountamount = objects.find("div", class_='_30jeq3 _1_WHN1').text if objects.find("div",
                                                                                                        class_='_30jeq3 _1_WHN1') else " "

            product_percentage = objects.find("div", class_='_3Ay6Sb').text if objects.find("div",
                                                                                            class_='_3Ay6Sb') else " "


            product_discountamount = product_discountamount.replace('₹','')
            product_discountamount = product_discountamount.replace(',','')
            prdct_dict = {
                'image': image_tag[0]["src"],
                'name': product_name,
                'description': product_description,
                'discountamount': int(product_discountamount),
                'actualamount': product_actualamount,
                'off': product_percentage
            }
            #print(prdct_dict)
            os.chdir('/home/user/PycharmProjects/pythonProject4/ecommerceweb/static/scrapedimages')
            baseDir = os.getcwd()
            image_content = requests.get(image_tag[0]["src"])
            file_name = f"{product_name}_image.jpg"
            file_path = os.path.join(baseDir, file_name)
            os.chdir('/home/user/PycharmProjects/pythonProject4/ecommerceweb')
            import urllib.request

            with urllib.request.urlopen(image_tag[0]["src"]) as response:
                resp_read = response.read()

            with open(file_path, 'wb') as f:                   #extracting image content from url
                f.write(resp_read)
            image = ImageFile(io.BytesIO(resp_read), name=f"{product_name}.jpg")
            prdct_obj = Product.objects.create(image = image,name = product_name,description= product_description,discountamount = int(product_discountamount),actualamount=product_actualamount,off=product_percentage)
            print("success")

