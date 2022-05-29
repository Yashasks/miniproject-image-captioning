from flask import Flask, render_template, request
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.applications.xception import Xception
from keras.models import load_model
from pickle import load
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import argparse


app=Flask(__name__)
max_length = 32
tokenizer = load(open("tokenizer.p","rb"))
model = load_model('model_9.h5')
xception_model = Xception(include_top=False, pooling="avg")

# ap = argparse.ArgumentParser()
# ap.add_argument('-i', '--image', required=True, help="Image Path")
# args = vars(ap.parse_args())
# img_path = args['image']

def extract_features(filename, model):
        try:
            image = Image.open(filename)

        except:
            print("ERROR: Couldn't open image! Make sure the image path and extension is correct")
        image = image.resize((299,299))
        image = np.array(image)
        # for images that has 4 channels, we convert them into 3 channels
        if image.shape[2] == 4: 
            image = image[..., :3]
        image = np.expand_dims(image, axis=0)
        image = image/127.5
        image = image - 1.0
        feature = model.predict(image)
        return feature

def word_for_id(integer, tokenizer):
    for word, index in tokenizer.word_index.items():
        if index == integer:
            return word
    return None


def generate_desc(model, tokenizer, photo, max_length):
    in_text = 'start'
    for i in range(max_length):
        sequence = tokenizer.texts_to_sequences([in_text])[0]
        sequence = pad_sequences([sequence], maxlen=max_length)
        pred = model.predict([photo,sequence], verbose=0)
        pred = np.argmax(pred)
        word = word_for_id(pred, tokenizer)
        if word is None:
            break
        in_text += ' ' + word
        if word == 'end':
            break
    return in_text


#path = 'Flicker8k_Dataset/111537222_07e56d5a30.jpg'


@app.route('/', methods=['GET'])
def about():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def predict():
    if request.method=='POST':
        imagefile=request.files["imagefile"]
        imagepath="./static/images/"+imagefile.filename
        imagefile.save(imagepath)


        photo = extract_features(imagepath, xception_model)
        img = Image.open(imagepath)

        description = generate_desc(model, tokenizer, photo, max_length)
        caption = ""

        caption = description[5:len(description)-3]

        caption_generated='%s' % (caption)

        return render_template('index.html', prediction=caption_generated, selected_image=imagepath)
    return None

if __name__ == '__main__':
    app.run(port=1234, debug=True)


    
# print("\n\n")
# print(description)
# plt.imshow(img)