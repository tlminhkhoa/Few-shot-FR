


# Few Shot Facial Recognition ![](https://i.imgur.com/JrYsVv4.png)

<p align="center">
    <img  src="https://i.imgur.com/mcHtn5R.png">
</p>
    
<!-- ![downloads](https://img.shields.io/github/downloads/atom/atom/total.svg)
![build](https://img.shields.io/appveyor/ci/:user/:repo.svg)
![chat](https://img.shields.io/discord/:serverId.svg) -->

<!-- ## Table of Contents -->

<!-- [TOC] -->

## What is this ?
Utilizing FaceNet pre-train model, we try to solve the facialrecogintion
problem with only 5 images for each person.

The need for capable facial recognition systems is
increasing every day, as new applications for the technology
are found - from security and surveillance to self-driving cars.

One unique requirement for facial recognition that sets it apart from other AI problems is the relatively small datasets it is
expected to work with; anyone who needs a facial recognition
system to recognize them would not be willing to provide
more than a few images. With this, the computer is expected to
learn how to accurately identify that person under a wide
range of lighting conditions, facial expressions, hairstyles, etc.
That type of machine learning - where a model uses a small
number of examples to cover a wide range of inputs - is
referred to as few-shot learning, and was the focus of this
project.

In short, a dataset of labeled face images was used, with
only a few training images per label. Then, image
augmentation was used to effectively create more training
data. Then, different models were created and trained on the
training data. The models were then used to make predictions
for the test data, and various performance metrics were
recorded. The models were then refined and experimented
with to achieve the best results. This process is elaborated on
further below.


Dataset
---

To achieve this, the publicly available CelebA dataset is used.

![](https://i.imgur.com/chd93DI.jpg)



Over 253 different people was used.

For each person, 5 images were picked at random for the training dataset, and 3 were picked for the test dataset.

Executable Files: `prepData.js`
 

> The dataset as downloaded from source has too many images per person and does not have a structure suitable for our use.
> 
> This file is a Node.js script that picks out a few train/test images per person, and arranges them in a folder hierarchy that makes the dataset easier to use.
> 
> Note that after running this code, the dataset still contains images for 10,000 people. For practical reasons, we manually reduced this down to 253 people by deleting the folders for all the others. The first 253 folders in numerical order (by name) were retained. This does not have any code associated with it as it was done manually.
> 
> All the follwing Python code assumed the dataset has been run through this script.



Aside from the train and test dataset, an ‘other’ dataset was also prepared. This contained images of people that did not exist in the training dataset, and so could never be identified by any trained model. The purpose of this dataset was to ensure that the models could correctly predict when an image had an unknown face in it, rather than reporting a false positive for any existing label. This is important since
identifying strangers is a critical feature for any security
system that uses facial recognition. During training, this
‘other’set was to be appended to the eval set and used to tune
the models.
Finally, the images in all datasets needed to be turned into
a standardized numerical format that the models could work
with. 


The original train dataset was then split into train and
evaluation (‘eval’) sets, at a 70/30 ratio. The eval set was
meant to be used to evaluate model performance during
training. At this point, the dataset was ready to be used. It had the
train, test, and eval (+ ‘other’) subsets with 7023, 900, and
3724 images respectively, and consisted of face embeddings
for the faces in the original images.



Image Augmentation
---
Image augmentation was performed on the training dataset,
where 9 new images were derived from each original image. 

This involved manipulating the existing images in
various ways such as rotating, flipping, resizing, adjusting the
brightness, and adding noise. This helped increase the amount
of training data and also helped the models to better recognize
faces under various different conditions

![](https://i.imgur.com/BmixROM.png)

Executable Files: `augmentation.py` This file contains code for image augmentation.

Multi-Task Cascaded Convolutional Networks (MTCNN)
---

First, the MTCNN facial extraction model was used to
identify the region of each image that contained a face.
MTCNN (Multi-Task Cascaded Convolutional Networks) is a
highly accurate face detection model that was developed in
2016 and is freely available. It uses three stages of
convolutional neural networks to perform its task. With it, the
face in each image could be cropped and then resized to 160
by 160 pixels.

<p align="center">
    <img  src="https://i.imgur.com/mcHtn5R.png">
</p>


FaceNet
---
FaceNet is a Google-developed ML system from 2015 that
“directly learns a mapping from face images to a compact
Euclidean space where distances directly correspond to a
measure of face similarity.” Put simply, the FaceNet model
was used to extract numerical feature mappings, called face
embeddings, from each image. A face embedding is a
128-element numerical array that captures information about
the unique or interesting features of the face. These can be
directly compared with each other or can be used to train
models and make predictions.

RESULTS 
---

Exploratory Data Analysis
---

After augmentation, within 12,630 total examples, MTCNN
was able to detect 10,75 faces, around 85%; the remaining
face images were not used. Most of the face-detection errors
were from the results of image augmentation. This shows that
the image augmentation process used could be improved in the
future. The following is the error distribution.

![](https://i.imgur.com/oAQZ2Cw.png)

To understand more about face embeddings, we decided to
find the centroid of each label. This was achieved by
averaging all the vectors of a person to find their spatial
center. This provides the opportunity to study which faces are
most similar, which are the most different by measuring the
distances from one to another.

![](https://i.imgur.com/A0ttsI1.png)

According to the FaceNet model, these were the 2 most
similar people in our data set, with a distance of 5.22884 from
each other. The resemblance is notable by eye.

![](https://i.imgur.com/xSb21od.png)

These were the 2 most different people, with a distance of
around 15. We might expect that these people would have
opposite genders and/or different skin colours, but these two
have the same gender and skin colour. This gives us an insight
that the model only focuses on facial features, not other visual
factors.
A dimensional reduction technique called tsne was employed
to visualize a sample of 100 labels from the training set:

![](https://i.imgur.com/tC3Cq5N.png)

It is clear that some clusters have formed, indicating that
different boundaries can be drawn for classification.

Interestingly some outliers are gathered in the middle; this
noise is possibly caused by the image augmentation.


Brute Force Euclidean Distance
---

This first system was the simplest possible approach. It
does not involve training. For prediction, the new ‘test’ face
embedding is simply compared to every single face
embedding from the training dataset by measuring the
Euclidean distances between them. The training image with
the shortest Euclidean distance from the test image is found,
and the person/label from that training image is identified as
the predicted identity for the test face. If the shortest distance
is still above a certain threshold, then the identity of the new
test face is declared to be unknown. This threshold is the only
parameter of this system; it was experimented with using the
eval set to find the optimal value.


Naturally, the brute-force method of comparing every
training sample to the test sample means this system is very
slow. The next approach is an optimized version of this
Euclidean distance comparison and is much faster.

After repeated trial and error, the threshold value of 10 was
found to be optimal. With this threshold, the system had an
accuracy of about 84.77% on the eval dataset, and the time
taken to make all the predictions was over 530 seconds.
On the test dataset, an accuracy of about 71.11% was achieved
in 122.44 seconds.
It should be noted that an analysis of the training dataset
showed that the two labels that were closest to each other (the
two different people in the dataset who looked the most alike)
had a Euclidean distance from each other of only 5.13 on
average. It is likely that errors made by the system involved
these individuals or others that looked like. This is also true
for the next K-D tree model.
We consider the Brute Force model as a baseline. It achieved
good accuracy with zero training time, but a terribly high
classification time. Inspired by KNN, we decided to employ a
K-D tree to optimize this process.

K-D Tree With Euclidean Distance
---

A K-D tree is a data structure that is used to organize
points in a k-dimensional space. This makes it ideal to store
face embeddings, as they are 128-dimensional vectors. While
building a K-D tree takes time, that initial investment pays off
later as the structure can be navigated very efficiently. The
samples in the training dataset can be arranged in a K-D tree
according to their Euclidean distances relative to each other.
Then instead of comparing the Euclidean distance of the new
test sample with every single training sample (as in the
previous section), the K-D tree can be used to efficiently
search through the training set and drastically reduce the
number of comparisons needed. It can be thought of as
searching through a sorted binary tree, except in k-dimensions
instead of 2. Similar to the previous approach, the only
parameter to change is the threshold at which the prediction is
“unknown”.
As will be explored further below, the results from the
previous approach are identical to those from this method, but
the latter is several times faster.

Since this optimized approach is very fast, predictions were
made for the eval dataset using every threshold value between
1 and 20. As with the previous approach, the optimal threshold
was found to be 10, and the highest accuracy achieved on the
eval dataset was 84.77%. The time taken was only about 6.87
seconds.
On the test dataset, an accuracy of about 71.11% was achieved
in 2.32 seconds.
The graph of accuracy on the eval dataset for each threshold
between 1 and 20 is below

![](https://i.imgur.com/i7lydWK.png)

Stacked SVM
---

Support Vector Machines are famous for their ability to fit
high dimensional data with limited examples, therefore an
SVM was a natural choice for this project. The previous
methods used a threshold value to decide when a sample was
from the ‘other’ dataset, meaning they did not exist in the
training set and were, therefore, unknown. To play a similar
role in this method, a second SVM was introduced to process
the output probability distribution of the first SVM. The
overall system structure is shown below:


![](https://i.imgur.com/clY2pnn.png)

The first model, SVM A, was trained to classify examples.
The second model, SVM B, was trained to study the
softmax-like probability distribution output of SVM A to
determine if the data point is from the ‘other’ dataset or not. If
its answer is yes, the example is concluded to be unknown; if
not, it will be pushed back to model A for class determination.


![](https://i.imgur.com/9qPi9QN.png)


The above graph shows that the hypothesis is true. For the
unseen labels, there is a high density of around 5.3, whereas
the remaining samples are spread out in the lower unit.

###### tags: `Templates` `Documentation`




Below is a brief explanation of each file.

## `prepData.js`
The dataset as downloaded from source has too many images per person and does not have a structure suitable for our use.

This file is a Node.js script that picks out a few train/test images per person, and arranges them in a folder hierarchy that makes the dataset easier to use.

Note that after running this code, the dataset still contains images for 10,000 people. For practical reasons, we manually reduced this down to 253 people by deleting the folders for all the others. The first 253 folders in numerical order (by name) were retained. This does not have any code associated with it as it was done manually.

All the follwing Python code assumed the dataset has been run through this script.






Interestingly some outliers are gathered in the middle; this
noise is possibly caused by the image augmentation.

## `few_shot_face_recogntion.py`
This file contains functions to load the data, split it into train/test/eval, extract face embeddings, and perform other steps (excluding image augmentation) as described in the report. It also contains functions to run the first two methods described in the report that involve Euclidean distances.

Finally, the code at the end of the file uses the aforementioned functions to run experiments and show results for the first 2 methods.

## `svm_fewshot.py`
This file contains (aside from some helper functions identical to those in the previous file) all the code related to the third "Stacked SVM" method from our report. Running this file will perform the training, testing, and will generate results.

## `analysis.py`
This file contains code that analyses the dataset in various ways as discussed in the report. This includes generating plots to visualize data samples, probability distributions, etc.

## Other Notes
The original dataset (and associated .txt files) can be downloaded from: http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html

The specific implementation of FaceNet we used (the `facenet_keras.h5` file) can be found here: https://drive.google.com/file/d/1PZ_6Zsy1Vb0s0JmjEmVd8FS99zoMCiN1/view?usp=sharing
