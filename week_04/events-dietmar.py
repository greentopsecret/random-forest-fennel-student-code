import re

url = 'https://www.eventbrite.de/d/germany--berlin/music--events/'
response = requests.get(url)
event_soup = BeautifulSoup(response.text)
class_name = 'eds-event-card__formatted-name--is-clamped eds-event-card__formatted-name--is-clamped-three eds-text-weight--heavy'

event_titles = re.findall(r'\>(.*?)\<', str(event_soup.find_all(class_= class_name)))
event_titles = list(dict.fromkeys(event_titles))
event_titles.pop(1)
event_titles

for i in range(2,15,1):
    url = 'https://www.eventbrite.de/d/germany--berlin/music--events/?page={}'.format(i)
    response = requests.get(url)
    event_soup = BeautifulSoup(response.text)
    event_titles_temp = re.findall(r'\>(.*?)\<', str(event_soup.find_all(class_= class_name)))
    event_titles_temp = list(dict.fromkeys(event_titles_temp))
    event_titles_temp.pop(1)
    event_titles.append(event_titles_temp)
    
event_titles
