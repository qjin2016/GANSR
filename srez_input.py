import tensorflow as tf

FLAGS = tf.app.flags.FLAGS

def setup_inputs(sess, filenames, image_size=None, capacity_factor=3):

    if image_size is None:
        image_size = FLAGS.sample_size
    
    # Read each JPEG file
    reader = tf.WholeFileReader()
    filename_queue = tf.train.string_input_producer(filenames)
    key, value = reader.read(filename_queue)
    channels = 3
    image = tf.image.decode_jpeg(value, channels=channels, name="dataset_image")
    image.set_shape([None, None, channels])

    # Crop and other random augmentations
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_saturation(image, .95, 1.05)
    image = tf.image.random_brightness(image, .05)
    image = tf.image.random_contrast(image, .95, 1.05)

    wiggle = 8
    off_x, off_y = 25-wiggle, 60-wiggle
    crop_size = 128
    crop_size_plus = crop_size + 2*wiggle
    image = tf.image.crop_to_bounding_box(image, off_y, off_x, crop_size_plus, crop_size_plus)
    image = tf.random_crop(image, [crop_size, crop_size, 3])

    image = tf.reshape(image, [1, crop_size, crop_size, 3])
    image = tf.cast(image, tf.float32)/255.0 # from 0~1

    if crop_size != image_size:
        image = tf.image.resize_area(image, [image_size, image_size])
 
    # The feature is simply a Kx downscaled version
    K = 4
    downsampled = tf.image.resize_area(image, [image_size//K, image_size//K])

    feature = tf.reshape(downsampled, [image_size//K, image_size//K, 3])
    label   = tf.reshape(image,       [image_size,   image_size,     3])

    # Using asynchronous queues
    features, labels = tf.train.batch([feature, label],
                                      batch_size=FLAGS.batch_size,
                                      num_threads=4,
                                      capacity = capacity_factor*FLAGS.batch_size,
                                      name='labels_and_features')

    tf.train.start_queue_runners(sess=sess)
      
    return features, labels

def setup_inputs_two_sources(sess, filenames_input, filenames_output, image_size=None, capacity_factor=3):

    if image_size is None:
        image_size = FLAGS.sample_size
    
    # Read each JPEG file
    reader_input = tf.WholeFileReader()
    filename_queue_input = tf.train.string_input_producer(filenames_input)
    key, value_input = reader_input.read(filename_queue_input)
    channels = 3
    image_input = tf.image.decode_jpeg(value_input, channels=channels, name="input_image")
    image_input.set_shape([None, None, channels])

    # read output
    reader_output = tf.WholeFileReader()
    filename_queue_output = tf.train.string_input_producer(filenames_output)
    key, value_output = reader_output.read(filename_queue_output)
    channels = 3
    image_output = tf.image.decode_jpeg(value_output, channels=channels, name="output_image")
    image_output.set_shape([None, None, channels])

    # cast
    image_input = tf.cast(image_input, tf.float32)/255.0
    image_output = tf.cast(image_output, tf.float32)/255.0

    # do undersampling here

    # take channel0 real part, channel1 imag part    
    image_input = image_input[:,:,:2]
    image_output = image_output[:,:,0]

    # The feature is simply a Kx downscaled version
    feature = tf.reshape(image_input, [image_size, image_size, 2])
    label   = tf.reshape(image_output, [image_size,   image_size,     1])

    # Using asynchronous queues
    features, labels = tf.train.batch([feature, label],
                                      batch_size=FLAGS.batch_size,
                                      num_threads=4,
                                      capacity = capacity_factor*FLAGS.batch_size,
                                      name='labels_and_features')

    tf.train.start_queue_runners(sess=sess)
      
    return features, labels

def setup_inputs_one_sources(sess, filenames_input, filenames_output, image_size=None, capacity_factor=3):

    if image_size is None:
        image_size = FLAGS.sample_size
    
    # Read each JPEG file
    reader_input = tf.WholeFileReader()
    filename_queue_input = tf.train.string_input_producer(filenames_input)
    key, value_input = reader_input.read(filename_queue_input)
    channels = 3
    image_input = tf.image.decode_jpeg(value_input, channels=channels, name="input_image")
    image_input.set_shape([None, None, channels])

    # cast
    image_input = tf.cast(image_input, tf.float32)/255.0

    # take channel0 real part, channel1 imag part    
    image_input = image_input[:,:,:2]
    image_output = image_input[:,:,-1]

    # The feature is simply a Kx downscaled version
    feature = tf.reshape(image_input, [image_size, image_size, 2])
    label   = tf.reshape(image_output, [image_size,   image_size,     1])

    # Using asynchronous queues
    features, labels = tf.train.batch([feature, label],
                                      batch_size=FLAGS.batch_size,
                                      num_threads=4,
                                      capacity = capacity_factor*FLAGS.batch_size,
                                      name='labels_and_features')

    tf.train.start_queue_runners(sess=sess)
      
    return features, labels    
