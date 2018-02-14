from repository.ImageAnalyst import ImageAnalyst

ground_path = 'C:/Users/dsinger/PycharmProjects/masterthesis/files/images/'
input_image = ground_path + 'mistborn.jpg'

image = ImageAnalyst(input_path=input_image)

image.just_save(image.input_image, ground_path + 'juhuuu')
