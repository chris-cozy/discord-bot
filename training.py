import random
import json
import pickle
import numpy as np
# Natural language toolkit
import nltk
# Reduces the word to its stem so its not wasting time looking for the exact word
# For example works work working all seen as the same
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
import os
from dotenv import load_dotenv

load_dotenv()

# Calls constructor of the lemmatizer
lemmatizer = WordNetLemmatizer()
intentsPath = os.getenv('INTENTS')

intents = json.loads(open(intentsPath).read())

words = []
classes = []
# this holds the pairing of words to their classes
documents = []
characterBlacklist = ['?', '!', '.', ',']

for intent in intents['intents']:
    for pattern in intent['patterns']:
        # this splits up the phrase into a collection of individual words
        wordList = nltk.word_tokenize(pattern)
        # takes the word and appends it to the list
        words.extend(wordList)
        documents.append((wordList, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# lemmatizes the words
words = [lemmatizer.lemmatize(word)
         for word in words if word not in characterBlacklist]
# set removes duplicates, sorted sorts the words
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# Getting into the Machine Learning part
# We now have the words needed but they are not numerical values. Nueral networks cannot be feed words, it must be numerical values
# Going to use 'bag of words'. Set the individual word values to either 0 or 1 depending on if it's occuring in that particular pattern.
# Doing the same for the classes

training = []
# template of 0s, as many as there are classes
outputEmpty = [0] * len(classes)

for document in documents:
    bag = []
    wordPatterns = document[0]
    wordPatterns = [lemmatizer.lemmatize(
        word.lower()) for word in wordPatterns]
    # for each word if word intents we want to know if it occurs in the pattern. If so signify a 1
    for word in words:
        bag.append(1) if word in wordPatterns else bag.append(0)

    # this is what we do to copy the list. not type casting but copying
    outputRow = list(outputEmpty)
    # setting this index in the output row to 1
    outputRow[classes.index(document[1])] = 1
    training.append([bag, outputRow])

# shuffle training data
random.shuffle(training)
# turn it into a np array
training = np.array(training)
# converting into x and y values
trainX = list(training[:, 0])
trainY = list(training[:, 1])

# Onto the MACHINE LEARNING portion
# building the nueral network model, a simple sequential model
model = Sequential()
# adding a couple layers
# input layer, 128 nuerons, input shape that is dependent on training data size
# activation function is a rectified linear unit, or 'relu'
model.add(Dense(128, input_shape=(len(trainX[0]),), activation='relu'))
# All the details of the layers not explained, seperate research: Nueral Network Theory
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
# Want to have as many nuerons as there are classes, activation function a soft max function, which is the function that will allow us to add up the results
# Scales the results in the output layer so that they all add up to 1
model.add(Dense(len(trainY[0]), activation='softmax'))
# lr is the learning rate
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
# compiles them all
model.compile(loss='categorical_crossentropy',
              optimizer=sgd, metrics=['accuracy'])

# epochs is how many times you are feeding the data into the nueral network
hist = model.fit(np.array(trainX), np.array(trainY),
                 epochs=200, batch_size=5, verbose=1)
model.save('chatbotmodel.h5', hist)
print("Trained.")

# After this the nueral network is trained. The next step is creating the chatbot application that uses the trained model
# The more training data, patterns, and intents added, the better and more fluid the recognition will be.
