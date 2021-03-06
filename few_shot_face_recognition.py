# -*- coding: utf-8 -*-
"""Few-Shot Face Recognition.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PNbAMdXjh_wZG7re9oN9imAp84xn-esz

# Prep
> Prepare dependencies, mount storage, etc.
"""

# pip install mtcnn

from google.colab import drive
drive.mount('/content/drive')

from keras.models import load_model
import mtcnn
from PIL import Image 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mtcnn.mtcnn import MTCNN
from sklearn.pipeline import Pipeline
import pandas as pd
import os
from numpy import savetxt,loadtxt
from keras.models import load_model
from sklearn.neighbors import KDTree
import time

"""# Functions
> Define the functions used to load data, create embeddings, train models, etc.
"""

# Load an image
def load_image_to_pixel(imdirect):
    im = Image.open(imdirect)
    im = im.convert("RGB")
    impixel = np.asarray(im)
    return impixel

# Crop out everything but one face from an image
def extract_face(impixel,boxReturn):
    facedetector = MTCNN()
    detectedFaces = facedetector.detect_faces(impixel)
    if len(detectedFaces) == 0:
        return None
    box = detectedFaces[0].get('box')
    if (boxReturn is True):
        return box
    x1,y1,x2,y2 = box[0] , box[1] , box[0] + box[2], box[1] + box[3]
    return Image.fromarray(impixel[y1:y2, x1:x2])

# Take an image path as input and return a face embedding for one face in the image (or return None)
def imageToEmbedding(imagePath):
    face = extract_face(load_image_to_pixel(imagePath),False)
    if face is None:
        print("WARNING: Could not detect face in ", imagePath)
        return None
    face = face.resize((160, 160))
    face_pixels = np.asarray(face)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    face_pixels = np.expand_dims(face_pixels, axis=0)
    model = load_model("/content/drive/MyDrive/CPS803/facenet_keras.h5", compile=False)
    return model.predict(face_pixels)[0]

# Generate embeddings for all images in a directory and save the data into CSV files so they can be re-used later (this takes a long time)
def datasetToEmbeddingCSVs(directory, outputDirectory):
    if not os.path.isdir(outputDirectory):
        os.mkdir(outputDirectory)
    for dirname in os.listdir(directory):
        idDirPath = os.path.join(directory, dirname)
        if os.path.isdir(idDirPath):
            data = [["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100", "101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "111", "112", "113", "114", "115", "116", "117", "118", "119", "120", "121", "122", "123", "124", "125", "126", "127", "label", "file"]]
            for filename in os.listdir(idDirPath):
                if filename.endswith((".jpg", ".jpeg", ".png")):
                    sudoface = imageToEmbedding(os.path.join(idDirPath, filename))
                    if sudoface is not None:
                        sudoface = sudoface.tolist()
                        sudoface.append(dirname)
                        sudoface.append(filename)
                        data.append(sudoface)
            data = np.array(data)
            savetxt(os.path.join(outputDirectory, dirname + ".csv"), data, delimiter=',', fmt='%s')

# Load dataset embeddings from all the CSV files in the given directory (the CSV should have been generated by the datasetToEmbeddingCSVs function above)
def load_train_embeddings_from_per_identity_CSV_directory(directory):
    df = pd.DataFrame()
    labels = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            lines = loadtxt(os.path.join(directory,filename), delimiter=',', skiprows=1, usecols=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127)).reshape(-1,128)
            for row in lines:
                row = row.reshape(1,128)
                if(df.empty):
                    df = pd.DataFrame(row)
                else:
                    df = pd.concat([df,pd.DataFrame(row)])
                labels.append(filename.replace(".csv",""))
    df["labels"] = labels
    return df

# Draw the given image with a rectangle using the given coordinates
def drawAbox(im,corr):
    fig,ax = plt.subplots(1)
    ax.imshow(im)
    rect = patches.Rectangle((corr[0],corr[1]),corr[2],corr[3],linewidth=1,edgecolor='r',facecolor='none')
    ax.add_patch(rect)
    plt.show()

# Changing pandas DataFrame table to numpy arrays for easier processing (expects last column to be labels, rest to be features)
def datasetDataFramesToNumpyArrays(dataFrame, splitIntoXY = True):
    temp = dataFrame.to_numpy()
    if splitIntoXY is True:
        return (temp[:, :-1], temp[:, -1])
    else:
        return temp

# Given a numpy array of face embeddings X and corresponding labels Y, get rid of all samples which are all-zero, and their corresponding labels, and return the result
def dropZeroRows(datasetX, datasetY):
    resultX = []
    resultY = []
    for i, row in enumerate(datasetX):
        if np.sum(row) != 0:
            resultX.append(row)
            resultY.append(datasetY[i])
    return (np.array(resultX), np.array(resultY))

# Loads the train + test datasets from the specified embedding CSVs, then splits the test set into eval and test sets based on the specified percentage (for test set)
# Returns the X,y arrays for all 3 (trainX, trainY, evalX, evalY, testX, testY)
# If an "other" set is specified, it is added to the eval dataset
# All zero-rows in the data (empty face embeddings) are silently removed
def loadAndSplitDatasets(trainEmbeddingsCSVPath, testEmbeddingsCSVPath, percentEval, otherEmbeddingsCSVPath = ""):
    if percentEval > 1:
        percentEval = percentEval/100 # Interpret any number > 1 as being /100
    if percentEval == 1:
        raise Exception("You can't split the train set into train/eval with a ratio of 100%!")
    trainAndEvalXY = datasetDataFramesToNumpyArrays(load_train_embeddings_from_per_identity_CSV_directory(trainEmbeddingsCSVPath), False)
    (testX, testY) = datasetDataFramesToNumpyArrays(load_train_embeddings_from_per_identity_CSV_directory(testEmbeddingsCSVPath))
    
    (rows, cols) = trainAndEvalXY.shape
    trainAndEvalXYListByLabel = [trainAndEvalXY[trainAndEvalXY[:, cols-1] == k] for k in np.unique(trainAndEvalXY[:, cols-1])]
    trainXY = []
    evalXY = []
    for array in trainAndEvalXYListByLabel:
        size = len(array[:, -1])
        trainEndIndex = int(round((size * (1 - percentEval)) - 1))
        (trainXYthis, evalXYthis) = (array[:trainEndIndex,:], array[trainEndIndex+1:,:])
        trainXY.append(trainXYthis)
        evalXY.append(evalXYthis)
    trainXY = np.vstack(trainXY)
    evalXY = np.vstack(evalXY)
    (trainX, trainY) = (trainXY[:, :-1], trainXY[:, -1])
    (evalX, evalY) = (evalXY[:, :-1], evalXY[:, -1])
    if (len(otherEmbeddingsCSVPath) > 0):
        (otherX, otherY) = datasetDataFramesToNumpyArrays(load_train_embeddings_from_per_identity_CSV_directory(otherEmbeddingsCSVPath))
        evalX = np.concatenate((evalX, otherX), axis=0)
        evalY = np.concatenate((evalY, otherY))
    else:
        otherY = []
    print("Loaded data.       Sizes: " + str(len(trainY)) + " train, " + str(len(evalY)) + " eval (of which 'other' is " + str(len(otherY)) + "), " + str(len(testY)) + " test")
    (trainX, trainY) = dropZeroRows(trainX, trainY)
    (testX, testY) = dropZeroRows(testX, testY)
    (evalX, evalY) = dropZeroRows(evalX, evalY)
    print("Dropped zero rows. Sizes: " + str(len(trainY)) + " train, " + str(len(evalY)) + " eval, " + str(len(testY)) + " test")
    return (trainX, trainY, testX, testY, evalX, evalY)

# Generate a K-D tree (which uses Euclidian distance as the metric) from a 2D array of face embeddings
# This is a separate function from the query function since the tree should only be generated once and can then be reused for all queries
def generateKDTreeFromTrainEmbeddings(trainX):
    return KDTree(trainX, metric="euclidean")

# Use a previously generated K-D tree of training data, along with associated labels array, to predict the label for a new face embedding
# If even the top candidate label has a distance above the given threshold, the result is null (unknown)
def predictFaceUsingKDTree(trainXTree, trainY, newFaceEmbedding, threshold, verbose=False):
    newFaceEmbedding = newFaceEmbedding.reshape(1, -1)
    dist, ind = trainXTree.query(newFaceEmbedding, k=1)
    if verbose:
        print("Distance:", dist[0])
    if dist[0] > threshold:
        return None
    else:
        return trainY[ind[0]][0]

# Manually measure the Euclidian distance between the given new face embedding and every sample in the training set to find the new face's label
# If even the top candidate label has a distance above the given threshold, the result is null (unknown)
def predictFaceUsingBruteForceEuclidianDistance(trainX, trainY, newFaceEmbedding, threshold, verbose=False):
    resultIndex = -1
    resultDist = -1
    for i, trainEmbedding in enumerate(trainX):
        dist = np.linalg.norm(newFaceEmbedding - trainEmbedding)
        if dist < resultDist or resultDist < 0:
            resultDist = dist
            resultIndex = i
    if verbose:
        print("Distance:", resultDist)
    if resultDist > threshold or resultIndex < 0:
        return None
    else:
        return trainY[resultIndex]

# Uses the provided training and test sets, along with the threshold, to make predictions using a euclidian distance model (based on either the K-D tree or brute force approach)
def runEuclidianDistanceModel(trainX, trainY, testX, testY, threshold, useBruteForceApproach):
    # Prepare timers to check performance
    timeTaken = 0
    # Generate the K-D tree (add the time that takes to the total time taken with K-D approach)
    tic = time.perf_counter()
    trainXTree = generateKDTreeFromTrainEmbeddings(trainX)
    # print(trainXTree.get_arrays())
    timeTaken = timeTaken + (time.perf_counter() - tic)
    # print("Build Tree time",timeTaken)
    # Prepare result counters
    correctPredictions = 0
    incorrectPredictions = 0
    for i, testEmbedding in enumerate(testX):
        # Make a prediction using the K-D tree approach (also time it and increment the appropriate counters)
        tic = time.perf_counter()
        if useBruteForceApproach:
            prediction = predictFaceUsingBruteForceEuclidianDistance(trainX, trainY, testEmbedding, threshold)
        else:
            prediction = predictFaceUsingKDTree(trainXTree, trainY, testEmbedding, threshold)
        timeTaken = timeTaken + (time.perf_counter() - tic)
        if prediction == testY[i] or (prediction is None and testY[i] not in trainY):
            correctPredictions = correctPredictions + 1
        else:
            incorrectPredictions = incorrectPredictions + 1
    return (correctPredictions, incorrectPredictions, timeTaken)

"""# Create Embeddings
> Create face embeddings for the train and test datasets.
>
> **ONLY RUN ONCE** - Whenever the dataset changes.
"""

# Creating training set embeddings CSV
datasetToEmbeddingCSVs("/content/drive/MyDrive/CPS803/img_celeba/subset train/", "/content/drive/MyDrive/CPS803/img_celeba/train embedding/")

# Creating test set embeddings CSV
datasetToEmbeddingCSVs("/content/drive/MyDrive/CPS803/img_celeba/subset test", "/content/drive/MyDrive/CPS803/img_celeba/test embedding/")

# Creating "other" set embeddings CSV
datasetToEmbeddingCSVs("/content/drive/MyDrive/CPS803/img_celeba/Other", "/content/drive/MyDrive/CPS803/img_celeba/Other embedding/")

"""# Tests
> Use the functions defined above to actually train/test models, run experiments, etc.
"""

# Testing Euclidian distance using K-D tree and brute force approaches
# --------------------------------------------------------------------
print("EUCLIDIAN DISTANCE MODELS...")
# Set threshold - if this is set to less than 0, then the best value between 1 and 20 will be searched for and used
threshold = -1
runBF=True # Run the brute-force method too (much slower)?
# Load data
(trainX, trainY, testX, testY, evalX, evalY) = loadAndSplitDatasets("/content/drive/MyDrive/CPS803/img_celeba/train embedding", "/content/drive/MyDrive/CPS803/img_celeba/test embedding", 0.3, "/content/drive/MyDrive/CPS803/img_celeba/Other embedding")
# If threshold < 0, find the best one between 1-20 and run the K-D tree model with that, else just run the model with the specified threshold - on the eval set
if threshold < 0:
    print("Finding best threshold between 1 and 20...")
    accuracy = 0
    (kdCorrect, kdIncorrect, kdTime) = (0, 0, 0)
    for i in range(0,21):
        (kdCorrectI, kdIncorrectI, kdTimeI) = runEuclidianDistanceModel(trainX, trainY, evalX, evalY, i, False)
        accuracyI = kdCorrectI/(kdCorrectI + kdIncorrectI)
        print("(threshold, accuracy): " + str(i) + ", " + str(accuracyI))
        if accuracyI >= accuracy:
            accuracy = accuracyI
            threshold = i
            (kdCorrect, kdIncorrect, kdTime) = (kdCorrectI, kdIncorrectI, kdTimeI)
else:
    (kdCorrect, kdIncorrect, kdTime) = runEuclidianDistanceModel(trainX, trainY, evalX, evalY, threshold, False)
    accuracy = kdCorrect/(kdCorrect + kdIncorrect)
print("Threshold used                                                                  :", str(threshold))
print("K-D Tree Results - eval - (correctCount, incorrectCount, timeTaken, accuracy)   :", str(kdCorrect) + ", " + str(kdIncorrect) + ", " + str(kdTime), "seconds, " + str((kdCorrect/(kdCorrect + kdIncorrect))*100) + "%")
if runBF is True:
    (bfCorrect, bfIncorrect, bfTime) = runEuclidianDistanceModel(trainX, trainY, evalX, evalY, threshold, True)
    print("Brute Force Results - eval - (correctCount, incorrectCount, timeTaken, accuracy):", str(bfCorrect) + ", " + str(bfIncorrect) + ", " + str(bfTime), "seconds, " + str((bfCorrect/(bfCorrect + bfIncorrect))*100) + "%")
# Repeat experiments on the test set
(kdCorrect, kdIncorrect, kdTime) = runEuclidianDistanceModel(trainX, trainY, testX, testY, threshold, False)
print("K-D Tree Results - test - (correctCount, incorrectCount, timeTaken, accuracy)   :", str(kdCorrect) + ", " + str(kdIncorrect) + ", " + str(kdTime), "seconds, " + str((kdCorrect/(kdCorrect + kdIncorrect))*100) + "%")
if runBF is True:
    (bfCorrect, bfIncorrect, bfTime) = runEuclidianDistanceModel(trainX, trainY, testX, testY, threshold, True)
    print("Brute Force Results - test - (correctCount, incorrectCount, timeTaken, accuracy):", str(bfCorrect) + ", " + str(bfIncorrect) + ", " + str(bfTime), "seconds, " + str((bfCorrect/(bfCorrect + bfIncorrect))*100) + "%")

