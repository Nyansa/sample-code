import requests


# run this script once after changing  something in viewer.js


def start():
    try:
        url = 'https://javascript-minifier.com/raw'
        data = {'input': open('templates/viewer.js', 'rb').read()}
        response = requests.post(url, data=data)
        with open("templates/viewer.min.js", "w") as outfile:
            print(response.text, file=outfile)
    except Exception as e: 
        print(e)


start()