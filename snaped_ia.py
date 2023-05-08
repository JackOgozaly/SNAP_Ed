from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd
import requests


#______________________Step 1: List to Every State Directory___________________
#If you want to learn more, go to this link: https://pythonprogramminglanguage.com/get-links-from-webpage/

#This chunk here is going to get all the text off the site
req = Request("https://snaped.fns.usda.gov/state-snap-ed-programs")
html_page = urlopen(req)
soup = BeautifulSoup(html_page, "lxml")

#Select only the links we want on this site
links = [] #Create an empty list for our new links to go into
for link in soup.findAll('a'):
    links.append(link.get('href'))
    
    
    
clean_links = ['https://snaped.fns.usda.gov' + word for word in links if word.startswith('/state-snap-ed-programs/')]


ia_info = []

for link in clean_links:
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    results = soup.find(class_="state-program__implementing-agencies-wrapper")
    
    ia_elems = results.find_all('div', class_="state-program__implementing-agencies-item")
    
    
    
    for ia in ia_elems:
        
        
        address_city = ia.find('div', class_="state-program__address-city").text.strip()
        address_state = ia.find('div', class_="state-program__address-state").text.strip()
        address_zip = ia.find('div', class_="state-program__address-zipcode").text.strip()
        ia_name = ia.find('div', class_="paragraph paragraph--type-agency-contact-information paragraph--view-mode-default").text.strip().partition('\n')[0]
    
    
        
        ia_info.append((ia_name, address_city, address_state, address_zip))
    

df = pd.DataFrame(ia_info)
df.columns = ['Name', 'City', 'State', 'Zip Code',]


df.to_csv(r'/Users/jackogozaly/Desktop/Python_Directory/snaped_locations.csv', index=False)


