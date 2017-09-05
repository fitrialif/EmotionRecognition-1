
from __future__ import print_function
import keras
import pandas as pd
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import numpy as np
from scipy import delete
from scipy.misc import imresize
import cv2
import gc
gc.collect()

batch_size = 8
num_classes = 7
epochs = 100
data_augmentation = True

img_rows = 20
img_cols = 20

def image_resize(images,newHeight,newWidth):
	images_resized = np.zeros([0, newHeight, newWidth], dtype=np.uint8)
	for image in range(images.shape[0]):
    		temp = imresize(images[image], [newHeight, newWidth], 'bilinear')
    		images_resized = np.append(images_resized, np.expand_dims(temp, axis=0), axis=0)
		
	return images_resized

def create_dataset(csv_file,mode):
	x=[]
	for i in csv_file:
		img=cv2.imread('data/'+mode+'/'+str(int(i[0])+1)+'.jpg')
		img=imresize(img,[img_rows,img_cols],'bilinear')
		x.append(img)
	return x

train = pd.read_csv("train.csv").values
test  = pd.read_csv("test.csv").values



Xtrain_mat=create_dataset(train,'Training')
X_train = np.array(Xtrain_mat)
Y_train = train[:, 1] 

Xtest_mat = create_dataset(test,'PublicTest')
X_test = np.asarray(Xtest_mat)
Y_test = test[:, 1 ]
print(Y_train)
X_train = X_train.astype('float32')
X_test = X_test.astype('float32')


print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices.
Y_train = keras.utils.to_categorical(Y_train, num_classes)
Y_test = keras.utils.to_categorical(Y_test, num_classes)
print(X_train.shape)
model = Sequential()

model.add(Conv2D(64, (5, 5), padding='same',
                 input_shape=X_train.shape[1:]))
model.add(Activation('relu'))
model.add(Conv2D(64, (5, 5)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(3, 3)))

model.add(Conv2D(64, (3, 3), padding='same'))
model.add(Activation('relu'))
model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.3))
model.add(Dense(num_classes))
model.add(Activation('softmax'))

# initiate RMSprop optimizer
opt = keras.optimizers.SGD(lr=0.01, momentum=0.0, decay=0.0, nesterov=False)

# Let's train the mode SGD
model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255

if not data_augmentation:
    print('Not using data augmentation.')
    model.fit(X_train, Y_train,
              batch_size=batch_size,
              epochs=epochs,
              validation_data=(X_test, Y_test),
              shuffle=True)
else:
    print('Using real-time data augmentation.')
    # This will do preprocessing and realtime data augmentation:
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # Compute quantities required for feature-wise normalization
    # (std, mean, and principal components if ZCA whitening is applied).
    datagen.fit(X_train)

    # Fit the model on the batches generated by datagen.flow().
    model.fit_generator(datagen.flow(X_train, Y_train,
                                     batch_size=batch_size),
                        steps_per_epoch=X_train.shape[0] // batch_size,
                        epochs=epochs,
                        validation_data=(X_test, Y_test))
model.save('cnn3.h5')
gc.collect()
