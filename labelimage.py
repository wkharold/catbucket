def label_image(filepath, apikey):
    with open(filepath, 'rb') as image:
        content = { 'content': base64.b64encode(image.read()).decode('UTF-8') }

    features = []
    features.append({
        'type': 'LABEL_DETECTION',
        'maxResults': 3,
    })

    rqs= []
    rqs.append({
        'features': features,
        'image': content,
    })

    response = requests.post(url='https://vision.googleapis.com/v1/images:annotate?key=' + apikey, 
            data=json.dumps({ 'requests': rqs }),
            headers={'Content-Type': 'application/json'})

    print(response.text)

    resp = json.loads(response.text)
    for r in resp['responses']:
        for l in r['labelAnnotations']:
            if l['description'] == 'cat':
                print('upload ' + filepath)
