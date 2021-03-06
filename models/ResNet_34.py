import tensorflow.keras
from tensorflow.keras.layers import Dense, Conv2D
from tensorflow.keras.layers import BatchNormalization, Activation
from tensorflow.keras.layers import GlobalAveragePooling2D, Input, Flatten, MaxPool2D
from tensorflow.keras.models import Model


def resnet_layer(inputs,
                 num_filters=16,
                 kernel_size=3,
                 strides=1,
                 activation='relu',
                 batch_normalization=True):
    """
    # Arguments
        inputs (tensor): input tensor from input image or previous layer
        num_filters (int): Conv2D number of filters
        kernel_size (int): Conv2D square kernel dimensions
        strides (int): Conv2D square stride dimensions
        activation (string): activation name
        batch_normalization (bool): whether to include batch normalization
    # Returns
        x (tensor): tensor as input to the next layer
    """
    conv = Conv2D(num_filters,
                  kernel_size=kernel_size,
                  strides=strides,
                  padding='same')

    x = inputs

    x = conv(x)
    if batch_normalization:
        x = BatchNormalization()(x)
    if activation is not None:
        x = Activation(activation)(x)

    return x


def resnet34(input_shape, num_classes):
    """ResNet 34
    # Arguments
        input_shape (tensor): shape of input image tensor
        num_classes (int): number of classes

    # Returns
        model (Model): Keras model instance
    """

    num_filters = 64
    inputs = Input(shape=input_shape)

    x = resnet_layer(inputs=inputs,
                     num_filters=num_filters,
                     kernel_size=(7, 7))

    x = MaxPool2D(pool_size=(3, 3),
                  strides=2,
                  padding="same")(x)
    num_res_blocks = [3, 4, 6, 3]
    for stack in range(4):
        for res_block in range(num_res_blocks[stack]):
            strides = 1
            if stack > 0 and res_block == 0:  # first layer but not first stack
                strides = 2  # downsample
            y = resnet_layer(inputs=x,
                             kernel_size=(3, 3),
                             num_filters=num_filters,
                             strides=strides)
            y = resnet_layer(inputs=y,
                             kernel_size=(3, 3),
                             num_filters=num_filters,
                             activation=None)
            if stack > 0 and res_block == 0:
                x = resnet_layer(inputs=x,
                                 num_filters=num_filters,
                                 kernel_size=(1, 1),
                                 strides=strides,
                                 activation=None,
                                 batch_normalization=True)
            x = tensorflow.keras.layers.add([x, y])
            x = Activation('relu')(x)
        num_filters *= 2

    x = GlobalAveragePooling2D()(x)
    x = Flatten()(x)
    outputs = Dense(num_classes,
                    activation='softmax')(x)

    model = Model(inputs=inputs, outputs=outputs)
    return model
