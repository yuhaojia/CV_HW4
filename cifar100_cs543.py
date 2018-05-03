"""
This file has been adapted from the easy-to-use tutorial released by PyTorch:
http://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html

Training an image classifier
----------------------------

We will do the following steps in order:

1. Load the CIFAR100_CS543 training, validation and test datasets using
   torchvision. Use torchvision.transforms to apply transforms on the
   dataset.
2. Define a Convolution Neural Network - BaseNet
3. Define a loss function and optimizer
4. Train the network on training data and check performance on val set.
   Plot train loss and validation accuracies.
5. Try the network on test data and create .csv file for submission to kaggle
"""

import csv
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os.path
import sys
import torch
import torch.utils.data
import torchvision
import torchvision.transforms as transforms
import torchvision.models as models

from cs543_dataset import CIFAR100_CS543

np.random.seed(111)
torch.cuda.manual_seed_all(111)
torch.manual_seed(111)

# <<TODO#5>> Based on the val set performance, decide how many
# epochs are apt for your model.
# ---------
EPOCHS = 15
# ---------
#EPOCHS = 1

IS_GPU = True
TEST_BS = 256
TOTAL_CLASSES = 100
TRAIN_BS = 32
PATH_TO_CIFAR100_CS543 = "/projects/training/baps/CS543/"


def calculate_val_accuracy(valloader, is_gpu):
    """ Util function to calculate val set accuracy,
    both overall and per class accuracy
    Args:
        valloader (torch.utils.data.DataLoader): val set
        is_gpu (bool): whether to run on GPU
    Returns:
        tuple: (overall accuracy, class level accuracy)
    """
    correct = 0.
    total = 0.
    predictions = []

    class_correct = list(0. for i in range(TOTAL_CLASSES))
    class_total = list(0. for i in range(TOTAL_CLASSES))

    for data in valloader:
        images, labels = data
        if is_gpu:
            images = images.cuda()
            labels = labels.cuda()
        outputs = net(Variable(images))
        _, predicted = torch.max(outputs.data, 1)
        predictions.extend(list(predicted.cpu().numpy()))
        total += labels.size(0)
        correct += (predicted == labels).sum()

        c = (predicted == labels).squeeze()
        for i in range(len(labels)):
            label = labels[i]
            class_correct[label] += c[i]
            class_total[label] += 1

    class_accuracy = 100 * np.divide(class_correct, class_total)
    return 100 * correct / total, class_accuracy


"""
1. Loading CIFAR100_CS543
^^^^^^^^^^^^^^^^^^^^^^^^^

We modify the dataset to create CIFAR100_CS543 dataset which consist of 45000
training images (450 of each class), 5000 validation images (50 of each class)
and 10000 test images (100 of each class). The train and val datasets have
labels while all the labels in the test set are set to 0.
"""

# The output of torchvision datasets are PILImage images of range [0, 1].
# Using transforms.ToTensor(), transform them to Tensors of normalized range
# [-1, 1].


# <<TODO#1>> Use transforms.Normalize() with the right parameters to
# make the data well conditioned (zero mean, std dev=1) for improved training.
# <<TODO#2>> Try using transforms.RandomCrop() and/or transforms.RandomHorizontalFlip()
# to augment training data.
# After your edits, make sure that test_transform should have the same data
# normalization parameters as train_transform
# You shouldn't have any data augmentation in test_transform (val or test data is never augmented).
# ---------------------

train_transform = transforms.Compose(
    [
    transforms.RandomRotation(degrees=10),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize([0.50787758,0.48716971,0.44120977], [0.26711263,0.25646897,0.27624937])
    ])
test_transform = transforms.Compose(
    [transforms.ToTensor(),
    transforms.Normalize([0.50384122,0.48397544,0.43883288], [0.26844666,0.25662768,0.27560104])
    ])
#,transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))

# ---------------------

trainset = CIFAR100_CS543(root=PATH_TO_CIFAR100_CS543, fold="train",
                          download=True, transform=train_transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=TRAIN_BS,
                                          shuffle=True, num_workers=2)
print("Train set size: " + str(len(trainset)))
print(trainset.train_data.shape)
print(np.mean(trainset.train_data, axis=(0,1,2))/255)
print(np.std(trainset.train_data, axis=(0,1,2))/255)

valset = CIFAR100_CS543(root=PATH_TO_CIFAR100_CS543, fold="val",
                        download=True, transform=test_transform)
valloader = torch.utils.data.DataLoader(valset, batch_size=TEST_BS,
                                        shuffle=False, num_workers=2)
print("Val set size: " + str(len(valset)))
print(valset.train_data.shape)
print(np.mean(valset.train_data, axis=(0,1,2))/255)
print(np.std(valset.train_data, axis=(0,1,2))/255)

testset = CIFAR100_CS543(root=PATH_TO_CIFAR100_CS543, fold="test",
                         download=True, transform=test_transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=TEST_BS,
                                         shuffle=False, num_workers=2)
print("Test set size: " + str(len(testset)))
print(testset.test_data.shape)
print(np.mean(testset.test_data, axis=(0,1,2))/255)
print(np.std(testset.test_data, axis=(0,1,2))/255)



# The 100 classes for CIFAR100
classes = ['apple', 'aquarium_fish', 'baby', 'bear', 'beaver', 'bed', 'bee', 'beetle', 'bicycle', 'bottle', 'bowl',
           'boy', 'bridge', 'bus', 'butterfly', 'camel', 'can', 'castle', 'caterpillar', 'cattle', 'chair',
           'chimpanzee', 'clock', 'cloud', 'cockroach', 'couch', 'crab', 'crocodile', 'cup', 'dinosaur', 'dolphin',
           'elephant', 'flatfish', 'forest', 'fox', 'girl', 'hamster', 'house', 'kangaroo', 'keyboard', 'lamp',
           'lawn_mower', 'leopard', 'lion', 'lizard', 'lobster', 'man', 'maple_tree', 'motorcycle', 'mountain', 'mouse',
           'mushroom', 'oak_tree', 'orange', 'orchid', 'otter', 'palm_tree', 'pear', 'pickup_truck', 'pine_tree',
           'plain', 'plate', 'poppy', 'porcupine', 'possum', 'rabbit', 'raccoon', 'ray', 'road', 'rocket', 'rose',
           'sea', 'seal', 'shark', 'shrew', 'skunk', 'skyscraper', 'snail', 'snake', 'spider', 'squirrel', 'streetcar',
           'sunflower', 'sweet_pepper', 'table', 'tank', 'telephone', 'television', 'tiger', 'tractor', 'train',
           'trout', 'tulip', 'turtle', 'wardrobe', 'whale', 'willow_tree', 'wolf', 'woman', 'worm']

########################################################################
# 2. Define a Convolution Neural Network
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# We provide a basic network that you should understand, run and
# eventually improve
# <<TODO>> Add more conv layers
# <<TODO>> Add more fully connected (fc) layers
# <<TODO>> Add regularization layers like Batchnorm.
#          nn.BatchNorm2d after conv layers:
#          http://pytorch.org/docs/master/nn.html#batchnorm2d
#          nn.BatchNorm1d after fc layers:
#          http://pytorch.org/docs/master/nn.html#batchnorm1d
# This is a good resource for developing a CNN for classification:
# http://cs231n.github.io/convolutional-networks/#layers

from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F


class BaseNet(nn.Module):
    def __init__(self):
        super(BaseNet, self).__init__()

        # <<TODO#3>> Add more conv layers with increasing
        # output channels
        # <<TODO#4>> Add normalization layers after conv
        # layers (nn.BatchNorm2d)

        # Also experiment with kernel size in conv2d layers (say 3
        # inspired from VGGNet)
        # To keep it simple, keep the same kernel size
        # (right now set to 5) in all conv layers.
        # Do not have a maxpool layer after every conv layer in your
        # deeper network as it leads to too much loss of information.

        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)


        # <<TODO#3>> Add more linear (fc) layers
        # <<TODO#4>> Add normalization layers after linear and
        # experiment inserting them before or after ReLU (nn.BatchNorm1d)
        # More on nn.sequential:
        # http://pytorch.org/docs/master/nn.html#torch.nn.Sequential

        self.fc_net = nn.Sequential(
            nn.Linear(16 * 5 * 5, TOTAL_CLASSES // 2),
            nn.ReLU(inplace=True),
            nn.Linear(TOTAL_CLASSES // 2, TOTAL_CLASSES),
        )

    def forward(self, x):
        # <<TODO#3&#4>> Based on the above edits, you'll have
        # to edit the forward pass description here.

        x = self.pool(F.relu(self.conv1(x)))
        # Output size = 28//2 x 28//2 = 14 x 14

        x = self.pool(F.relu(self.conv2(x)))
        # Output size = 10//2 x 10//2 = 5 x 5

        # See the CS231 link to understand why this is 16*5*5!
        # This will help you design your own deeper network
        x = x.view(-1, 16 * 5 * 5)
        x = self.fc_net(x)

        # No softmax is needed as the loss function in step 3
        # takes care of that

        return x


class BaseNet1(nn.Module):
    def __init__(self):
        super(BaseNet1, self).__init__()

        # <<TODO#3>> Add more conv layers with increasing
        # output channels
        # <<TODO#4>> Add normalization layers after conv
        # layers (nn.BatchNorm2d)

        # Also experiment with kernel size in conv2d layers (say 3
        # inspired from VGGNet)
        # To keep it simple, keep the same kernel size
        # (right now set to 5) in all conv layers.
        # Do not have a maxpool layer after every conv layer in your
        # deeper network as it leads to too much loss of information.

        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.bn1 = nn.BatchNorm2d(6)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.conv1_drop = nn.Dropout2d(p=0.2)

        # <<TODO#3>> Add more linear (fc) layers
        # <<TODO#4>> Add normalization layers after linear and
        # experiment inserting them before or after ReLU (nn.BatchNorm1d)
        # More on nn.sequential:
        # http://pytorch.org/docs/master/nn.html#torch.nn.Sequential

        self.fc_net = nn.Sequential(
            nn.Linear(16 * 5 * 5, TOTAL_CLASSES // 2),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(TOTAL_CLASSES // 2, TOTAL_CLASSES),
        )

    def forward(self, x):
        # <<TODO#3&#4>> Based on the above edits, you'll have
        # to edit the forward pass description here.

        #x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.bn1(self.conv1_drop(self.conv1(x)))))
        # Output size = 28//2 x 28//2 = 14 x 14

        x = self.pool(F.relu(self.conv2(x)))
        # Output size = 10//2 x 10//2 = 5 x 5

        # See the CS231 link to understand why this is 16*5*5!
        # This will help you design your own deeper network
        x = x.view(-1, 16 * 5 * 5)
        x = self.fc_net(x)
        #x = F.dropout(x, training=self.training)

        # No softmax is needed as the loss function in step 3
        # takes care of that

        return x



class BaseNetMoreLayer(nn.Module):
    def __init__(self):
        super(BaseNetMoreLayer, self).__init__()

        # <<TODO#3>> Add more conv layers with increasing
        # output channels
        # <<TODO#4>> Add normalization layers after conv
        # layers (nn.BatchNorm2d)

        # Also experiment with kernel size in conv2d layers (say 3
        # inspired from VGGNet)
        # To keep it simple, keep the same kernel size
        # (right now set to 5) in all conv layers.
        # Do not have a maxpool layer after every conv layer in your
        # deeper network as it leads to too much loss of information.

        ################################################

       
        self.conv1 = nn.Conv2d(3, 90, 3)
        self.conv2 = nn.Conv2d(90, 260, 3)
        self.conv3 = nn.Conv2d(260, 300, 3)
        #self.conv4 = nn.Conv2d(300, 300, 3)
        self.conv5 = nn.Conv2d(300, 260, 3)
        self.conv6 = nn.Conv2d(260, 90, 3)
        #self.pool3 = nn.MaxPool2d(2,2)
        #self.pool4 = nn.MaxPool2d(2,2)
        #self.conv5 = nn.Conv2d(80, 160, 3)

        self.pool1 = nn.MaxPool2d(2,2)
        self.pool2 = nn.MaxPool2d(2,2)
        self.pool3 = nn.MaxPool2d(2,2)

        #################################################

        # <<TODO#3>> Add more linear (fc) layers
        # <<TODO#4>> Add normalization layers after linear and
        # experiment inserting them before or after ReLU (nn.BatchNorm1d)
        # More on nn.sequential:
        # http://pytorch.org/docs/master/nn.html#torch.nn.Sequential

        #self.fc_net = nn.Sequential(
        #    nn.Linear(16 * 5 * 5, TOTAL_CLASSES // 2),
        #    nn.ReLU(inplace=True),
        #    nn.Linear(TOTAL_CLASSES // 2, TOTAL_CLASSES),
        #)


        ######################################################
        self.fc1 = nn.Linear(90*3*3, 1024)
        self.fc2 = nn.Linear(1024,512)
        self.fc3 = nn.Linear(512, TOTAL_CLASSES)
        

        self.bn1 = nn.BatchNorm2d(90)
        self.bn2 = nn.BatchNorm2d(260)
        self.bn3 = nn.BatchNorm2d(300)
        #self.bn4 = nn.BatchNorm2d(300)
        self.bn5 = nn.BatchNorm2d(260)
        self.bn6 = nn.BatchNorm2d(90)
        #self.bn5 = nn.BatchNorm2d(160)

        self.bn01 = nn.BatchNorm1d(1024)
        self.bn02 = nn.BatchNorm1d(512)

        #self.conv1_drop = nn.Dropout2d(p=0.2)
        #self.conv2_drop = nn.Dropout2d(p=0.2)
        self.conv3_drop = nn.Dropout2d(p=0.2)
        #self.conv4_drop = nn.Dropout2d(p=0.2)
        #self.conv5_drop = nn.Dropout2d(p=0.2)
        #self.conv6_drop = nn.Dropout2d(p=0.2)

        
    def forward(self, x):
        # <<TODO#3&#4>> Based on the above edits, you'll have
        # to edit the forward pass description here.

        ###x = self.pool(F.relu(self.conv1(x)))
        # Output size = 28//2 x 28//2 = 14 x 14

        ###x = self.pool(F.relu(self.conv2(x)))
        # Output size = 10//2 x 10//2 = 5 x 5

        # See the CS231 link to understand why this is 16*5*5!
        # This will help you design your own deeper network
        ###x = x.view(-1, 16 * 5 * 5)
        ###x = self.fc_net(x)

        # No softmax is needed as the loss function in step 3
        # takes care of that

        #####################################################
        x = F.relu(self.bn1(self.conv1(x)))
        #x = self.conv1_drop(x)
        x = self.pool1(F.relu(self.bn2(self.conv2(x))))
        #x = self.conv2_drop(x)
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.conv3_drop(x)
        #x = self.pool2(F.relu(self.bn4(self.conv4(x))))
        x = self.pool3(F.relu(self.bn5(self.conv5(x))))
        #x = self.conv5_drop(x)
        x = (F.relu(self.bn6(self.conv6(x))))
        #x = self.conv6_drop(x)
        x = x.view(-1, 90 * 3 * 3)

        x = F.relu(self.bn01(self.fc1(x)))
        x = F.relu(self.bn02(self.fc2(x)))
        x = self.fc3(x)

        return x

class AlexNet(nn.Module):

    def __init__(self, num_classes=100):
        super(AlexNet, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(64, 192, kernel_size=3, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(192, 384, kernel_size=3),
            nn.ReLU(inplace=True),
            nn.Conv2d(384, 256, kernel_size=3),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(),
            nn.Linear(256 * 1 * 1, 1024),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(1024, 512),
            nn.ReLU(inplace=True),
            nn.Linear(512, TOTAL_CLASSES),
        )

    def forward(self, x):
        x = self.features(x)
        #print(x.shape())
        x = x.view(x.size(0), 256 * 1 * 1)
        #print(x.shape())
        x = self.classifier(x)
        return x


class My_Net1(nn.Module):
    def __init__(self):
        super(My_Net1, self).__init__()
        self.conv1 = nn.Conv2d(3, 128, 3, stride=1, padding=1)
        self.conv1_bn = nn.BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=False)
        self.conv2 = nn.Conv2d(128, 128, 3, stride=1, padding=1)
        self.conv2_bn = nn.BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=False)
        self.pool1 = nn.MaxPool2d(2, stride=2, dilation=1)
        self.conv3 = nn.Conv2d(128, 256, 3, stride=1, padding=1)
        self.conv3_bn = nn.BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=False)
        self.conv4 = nn.Conv2d(256, 256, 3, stride=1, padding=1)
        self.conv4_bn = nn.BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=False)
        self.pool2 = nn.MaxPool2d(2, stride=2, dilation=1)
        self.conv5 = nn.Conv2d(256, 512, 3, stride=1, padding=1)
        self.conv5_bn = nn.BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=False)
        self.conv6 = nn.Conv2d(512, 512, 3, stride=1, padding=1)
        self.conv6_bn = nn.BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=False)
        self.pool3 = nn.MaxPool2d(2, stride=2, dilation=1)
        self.conv7 = nn.Conv2d(512, 1024, 3, stride=1, padding=1)
        self.conv7_bn = nn.BatchNorm2d(1024, eps=1e-05, momentum=0.1, affine=False)
        self.pool4 = nn.MaxPool2d(2, stride=2, dilation=1)
        self.fc_net = nn.Sequential(
            nn.Linear(1024 * 4, TOTAL_CLASSES),
        )

    def forward(self, x):
        x = F.relu(self.conv1_bn(self.conv1(x)))
        x = self.pool1(F.relu(self.conv2_bn(self.conv2(x))))
        x = F.relu(self.conv3_bn(self.conv3(x)))
        x = self.pool2(F.relu(self.conv4_bn(self.conv4(x))))
        x = F.relu(self.conv5_bn(self.conv5(x)))
        x = self.pool3(F.relu(self.conv6_bn(self.conv6(x))))
        x = self.pool4(F.relu(self.conv7_bn(self.conv7(x))))
        x = x.view(-1, 1024 * 4)
        x = self.fc_net(x)
        return x


class My_Net2(nn.Module):
    def __init__(self):
        super(My_Net2, self).__init__()
        self.conv1 = nn.Conv2d(3, 3, 3, stride=1, padding=1)
        self.conv1_bn = nn.BatchNorm2d(3, eps=1e-05, momentum=0.1, affine=False)
        self.conv2 = nn.Conv2d(3, 3, 3, stride=1, padding=1)
        self.conv2_bn = nn.BatchNorm2d(3, eps=1e-05, momentum=0.1, affine=False)
        self.pool1 = nn.MaxPool2d(2, stride=2, dilation=1)
        self.conv3 = nn.Conv2d(3, 6, 3, stride=1, padding=1)
        self.conv3_bn = nn.BatchNorm2d(6, eps=1e-05, momentum=0.1, affine=False)
        self.conv4 = nn.Conv2d(6, 6, 3, stride=1, padding=1)
        self.conv4_bn = nn.BatchNorm2d(6, eps=1e-05, momentum=0.1, affine=False)
        self.pool2 = nn.MaxPool2d(2, stride=2, dilation=1)
        self.conv5 = nn.Conv2d(6, 12, 3, stride=1, padding=1)
        self.conv5_bn = nn.BatchNorm2d(12, eps=1e-05, momentum=0.1, affine=False)
        self.conv6 = nn.Conv2d(12, 12, 3, stride=1, padding=1)
        self.conv6_bn = nn.BatchNorm2d(12, eps=1e-05, momentum=0.1, affine=False)
        self.pool3 = nn.MaxPool2d(2, stride=2, dilation=1)
        self.conv7 = nn.Conv2d(12, 24, 3, stride=1, padding=1)
        self.conv7_bn = nn.BatchNorm2d(24, eps=1e-05, momentum=0.1, affine=False)
        self.pool4 = nn.MaxPool2d(2, stride=2, dilation=1)
        self.fc_net = nn.Sequential(
            nn.Linear(24 * 2 * 2, TOTAL_CLASSES),
        )

    def forward(self, x):
        x = F.relu(self.conv1_bn(self.conv1(x)))
        x = self.pool1(F.relu(self.conv2_bn(self.conv2(x))))
        x = F.relu(self.conv3_bn(self.conv3(x)))
        x = self.pool2(F.relu(self.conv4_bn(self.conv4(x))))
        x = F.relu(self.conv5_bn(self.conv5(x)))
        x = self.pool3(F.relu(self.conv6_bn(self.conv6(x))))
        x = self.pool4(F.relu(self.conv7_bn(self.conv7(x))))
        #print('1..x.size() = {}'.format(str(x.size())))
        x = x.view(-1, 24 * 2 * 2)
        #print('2..x.size() = {}'.format(str(x.size())))
        x = self.fc_net(x)
        #print('3..x.size() = {}'.format(str(x.size())))
        return x

class Vgg16(nn.Module):
    def __init__(self):
        super(Vgg16, self).__init__()
        original_model = models.vgg16()
        self.features = nn.Sequential(*list(original_model.children())[:-1])
        self.classifier = (nn.Linear(512, TOTAL_CLASSES))

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

# Create an instance of the nn.module class defined above:
#net = BaseNet()
#net = BaseNet1()
#net = BaseNetMoreLayer()
#net = AlexNet()
#net = MyNetComplicate()
#net = My_Net1()
#net = My_Net2()
net = Vgg16()


# For training on GPU, we need to transfer net and data onto the GPU
# http://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html#training-on-gpu
if IS_GPU:
    net = net.cuda()

########################################################################
# 3. Define a Loss function and optimizer
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Here we use Cross-Entropy loss and SGD with momentum.
# The CrossEntropyLoss criterion already includes softmax within its
# implementation. That's why we don't use a softmax in our model
# definition.

import torch.optim as optim

criterion = nn.CrossEntropyLoss()

# Tune the learning rate.
# See whether the momentum is useful or not
optimizer = optim.SGD(net.parameters(), lr=0.005, momentum=0.9)

plt.ioff()
fig = plt.figure()
train_loss_over_epochs = []
val_accuracy_over_epochs = []
########################################################################
# 4. Train the network
# ^^^^^^^^^^^^^^^^^^^^
#
# We simply have to loop over our data iterator, and feed the inputs to the
# network and optimize. We evaluate the validation accuracy at each
# epoch and plot these values over the number of epochs
# Nothing to change here
# -----------------------------
for epoch in range(EPOCHS):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        # get the inputs
        inputs, labels = data

        if IS_GPU:
            inputs = inputs.cuda()
            labels = labels.cuda()

        # wrap them in Variable
        inputs, labels = Variable(inputs), Variable(labels)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.data[0]

    # Normalizing the loss by the total number of train batches
    running_loss /= len(trainloader)
    print('[%d] loss: %.3f' %
          (epoch + 1, running_loss))

    # Scale of 0.0 to 100.0
    # Calculate validation set accuracy of the existing model
    val_accuracy, val_classwise_accuracy = \
        calculate_val_accuracy(valloader, IS_GPU)
    print('Accuracy of the network on the val images: %d %%' % (val_accuracy))

    # # Optionally print classwise accuracies
    # for c_i in range(TOTAL_CLASSES):
    #     print('Accuracy of %5s : %2d %%' % (
    #         classes[c_i], 100 * val_classwise_accuracy[c_i]))

    train_loss_over_epochs.append(running_loss)
    val_accuracy_over_epochs.append(val_accuracy)
# -----------------------------


# Plot train loss over epochs and val set accuracy over epochs
# Nothing to change here
# -------------
plt.subplot(2, 1, 1)
plt.ylabel('Train loss')
plt.plot(np.arange(EPOCHS), train_loss_over_epochs, 'k-')
plt.title('(hyu59) train loss and val accuracy')
plt.xticks(np.arange(EPOCHS, dtype=int))
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(np.arange(EPOCHS), val_accuracy_over_epochs, 'b-')
plt.ylabel('Val accuracy')
plt.xlabel('Epochs')
plt.xticks(np.arange(EPOCHS, dtype=int))
plt.grid(True)
plt.savefig("plot.png")
plt.close(fig)
print('Finished Training')
# -------------

########################################################################
# 5. Try the network on test data, and create .csv file
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
########################################################################

# Check out why .eval() is important!
# https://discuss.pytorch.org/t/model-train-and-model-eval-vs-model-and-model-eval/5744/2
net.eval()

total = 0
predictions = []
for data in testloader:
    images, labels = data

    # For training on GPU, we need to transfer net and data onto the GPU
    # http://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html#training-on-gpu
    if IS_GPU:
        images = images.cuda()
        labels = labels.cuda()

    outputs = net(Variable(images))
    _, predicted = torch.max(outputs.data, 1)
    predictions.extend(list(predicted.cpu().numpy()))
    total += labels.size(0)

with open('submission_netid.csv', 'w') as csvfile:
    wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    wr.writerow(["Id", "Prediction1"])
    for l_i, label in enumerate(predictions):
        wr.writerow([str(l_i), str(label)])