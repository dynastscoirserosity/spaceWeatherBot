import os
import requests
import tweepy
import pytz
import shutil
import PyPDF2
import pypdfium2
#import config # uncmment to use variables on Gitlab
from datetime import datetime
from bs4 import BeautifulSoup

# twitter api v2 authentication
v2_api = tweepy.Client(
    consumer_key = 'D8rn4Fl7TixzZoL3N443hWxlp',
    consumer_secret = 'kVqLj0HlcxTJZOX6NX706jluDaFoRfzyR9iiHG6C3Qu0M2ACKR',
    access_token = '1654139942505963521-Jyc252vnXF3XUb6AL6YVdVdUIJGLcD',
    access_token_secret = '4ts9Yq4eV7zUp789MRqOfgqp9f3wHRo2yzE78cp6Kcd4q'
)

# twitter api v1.1 authentication
v1_auth = tweepy.OAuth1UserHandler(
   'D8rn4Fl7TixzZoL3N443hWxlp', 'kVqLj0HlcxTJZOX6NX706jluDaFoRfzyR9iiHG6C3Qu0M2ACKR',
   '1654139942505963521-Jyc252vnXF3XUb6AL6YVdVdUIJGLcD', '4ts9Yq4eV7zUp789MRqOfgqp9f3wHRo2yzE78cp6Kcd4q'
)

v1_api = tweepy.API(v1_auth)

header = str('\U0001F4C5 Updated ' + datetime.now(pytz.timezone('US/Eastern')).strftime('%d %b %Y (%Y/%m/%d) %H:%M %Z') + '\n')

# download the target page
space_force_site = requests.get('https://www.patrick.spaceforce.mil/About-Us/Weather/')

# parse the HTML content of the page and identify the correct element
soup = BeautifulSoup(space_force_site.content, "html.parser")
find_launch_support = soup.find("div", {"id": "dnn_ctr5680_HtmlModule_lblContent"})
find_a = find_launch_support.find_all('a')

find_section = []

for link in find_a:
    link = link['href']
    #print(link)
    if link not in find_section:
        find_section.append(link)

if 'LaunchFAQ.pdf' in find_section[len(find_section) - 1]:
    find_section.pop(len(find_section) - 1)

if find_section == []:
    tweet_text = header + '\nThere are no weather forecasts listed at the moment.'
    print(tweet_text)
else:
    list_of_links = []
    list_of_names = []

    for each in find_section:
        name_start = each.find('/Weather/') + 9
        name_end = each.find('Forecast') - 2
        char = name_start
        file_name = str('')
        while char <= name_end:
            file_name = file_name + each[char]
            char = char + 1
        list_of_names.append(str(file_name))
        formatted_link = each.replace(' ', '%20')
        full_link = 'https://www.patrick.spaceforce.mil' + formatted_link
        list_of_links.append(full_link)

    print(list_of_links)
    print(list_of_names)

    max_links = len(list_of_links)

    index = 0
    while index < max_links:
        download_file = requests.get(list_of_links[index]) # gets PDF document
        with open(str(list_of_names[index]) + '.pdf', 'wb') as file:
            file.write(download_file.content) # writes contents of downloaded PDF file to local file with corresponding names

        current_file_name = list_of_names[index]

        pdf = pypdfium2.PdfDocument(current_file_name + '.pdf')
        page = pdf[0]
        bitmap = page.render(scale = 1, rotation = 0)
        pil_image = bitmap.to_pil()
        pil_image.save(current_file_name + '.jpg')
        page.close()
        pdf.close()

        pdffileobj = open(current_file_name + '.pdf', 'rb')
        pdfreader = PyPDF2.PdfReader(pdffileobj)
        x = len(pdfreader.pages)
        pageobj = pdfreader.pages[0]
        text = pageobj.extract_text()
        with open(current_file_name + '.txt', 'w', encoding = 'utf-8') as file:
            file.writelines(text)
        pdffileobj.close()
        os.remove(current_file_name + '.pdf')

        with open(current_file_name + '.txt', 'r') as file:
            percentages = 0
            list_of_percentages = []
            for line in file.readlines():
                if line.strip().startswith('Issued'):
                    issued_date = line.replace('Issued : ', '').rstrip()
                    issued_date = issued_date.replace('  / ', ' / ')
                    issued_date = issued_date.replace(' L', 'L')
                    issued_date = issued_date.replace(' Z', 'Z')
                    print(issued_date)
                elif line.startswith('Valid'):
                    valid_date = line.replace('Valid : ', '').rstrip()
                    valid_date = valid_date.replace('  / ', ' / ')
                    valid_date = valid_date.replace('  â€“ ', '-')
                    valid_date = valid_date.replace(' -', '-')
                    valid_date = valid_date.replace(' L', 'L')
                    valid_date = valid_date.replace(' )', ')')
                    valid_date = valid_date.replace(' Z', 'Z')
                    print(valid_date)
                elif line.__contains__('%  Primary') or line.__contains__('% Primary'):
                    percentages += 1
                    if percentages < 3:
                        list_of_percentages.append(line)
                        #print(list_of_percentages)
                    if percentages == 2:
                        # print(list_of_percentages)
                        # first launch opportunity
                        first_op_text = list_of_percentages[0]
                        max_char = list_of_percentages[0].find('%  Primary')
                        if max_char == -1:
                            max_char = list_of_percentages[0].find('% Primary')
                        curr_char = 0
                        first_launch_op = ''
                        while curr_char < max_char:
                            first_launch_op = first_launch_op + first_op_text[curr_char]
                            curr_char += 1
                        first_launch_op = first_launch_op.replace('â†’', '→')
                        print(first_launch_op)

                        # first launch opportunity
                        second_op_text = list_of_percentages[1]
                        max_char = list_of_percentages[1].find('%  Primary')
                        if max_char == -1:
                            max_char = list_of_percentages[1].find('% Primary')
                        curr_char = 0
                        second_launch_op = ''
                        while curr_char < max_char:
                            second_launch_op = second_launch_op + second_op_text[curr_char]
                            curr_char += 1
                        second_launch_op = second_launch_op.replace('â†’', '→')
                        print(second_launch_op)

            tweet_text = header + '\n== ' + str(list_of_names[index].upper()) + ' ==\nIssued:\n' + str(issued_date) + '\n\nValid:\n' + str(valid_date) + '\n\nViolation Probability:\n' + first_launch_op + '%\n\nViolation Probability (24h Delay):\n' + second_launch_op + '%'
            print(tweet_text)

            #print(len(tweet_text))
            #upload = v1_api.media_upload(str(list_of_names[index]) + '.jpg')
            #v2_api.create_tweet(text = tweet_text, media_ids = [str(upload.media_id)])

        #os.remove(current_file_name + '.txt')
        os.remove(current_file_name + '.jpg')

        index += 1