import numpy as np
import cv2
import glob

images = []
for jpgfile in glob.glob('images/*.jpg'):
    images.append(cv2.imread(jpgfile))

def seal_find(img):
    width = img.shape[1] # интересует только второй элемент возвращаемого кортежа (ширина изображения)
        
    denoised = cv2.blur(img, (3,3)) # размытие для удаления мелких шумов    
    imggray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY) # конвертация изображения в серый диапазон для изготовления маски

    # Наложение маски с учетом освещенности скана:
    threshold = -1
    adaptiveThreshold = threshold if threshold >= 0 else cv2.mean(img)[0] # адаптивный порог насыщенности
    color = cv2.cvtColor(denoised, cv2.COLOR_BGR2HLS) # конвертация изображения в цветовую модель HLS
    mask = cv2.inRange(color, (0, int(adaptiveThreshold / 6), 60), (180, adaptiveThreshold, 255)) # выделение синего диапазона
    dst = cv2.bitwise_and(imggray, imggray, mask=mask) # применение маски в побитовом суммировании
    
    # Поиск контуров печатей:
    kernel = np.ones((5, 5), 'uint8') # подбор матрицы свертки
    dst = cv2.dilate(dst, kernel, iterations=3) # "размазывание" изображения для предотвращения слишком мелки контуров    
    contours = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0] # интересует только первый элемент возвращаемого кортежа (найденные контуры)

    imgdraw = img.copy() # создание копии входящих изображений для нанесения на них рамки выделения

    sides = {'LSide': "Нет", 'RSide': "Нет"} 
    coordsL = coordsR = None
    size = 100 # вручную выбранный размер искомого (наибольшего) контура печати
    # Обработка из всех полученных наибольшего контура:
    for i in range(len(contours)):        
        x, y, w, h = cv2.boundingRect(contours[i])
        if w > size and h > size:
            cv2.rectangle(imgdraw, (x, y), (x+w, y+h),(0, 255, 0), 2) # нанесение выделяющего прямоугольника 
            if x+w//2 < width//2:
                sides['LSide'] = "Да"
                coordsL = [x+w//2, y+h//2]        
            if x+w//2 > width//2:
                sides['RSide'] = "Да"
                coordsR = [x+w//2, y+h//2]        
            else:
                pass

    print('Изображение-{}: Левая сторона - {}, Правая сторона - {}'. format(img_num, sides['LSide'], sides['RSide']))    
    if coordsL != None:
        print('Координаты левой печати: ' , coordsL)         
    if coordsR != None:       
        print('Координаты правой печати: ', coordsR)
       
    output_filename = f'Output_Image_{img_num}.jpg'
    # cv2.imwrite(output_filename, imgdraw) # сохранение обработанного изображения в корневую директорию
    cv2.imshow(output_filename, imgdraw) # показ обоработанного изображения на экране
    cv2.waitKey(0)
 

img_num = 0
for img in images:
    seal_find(img)
    img_num += 1
