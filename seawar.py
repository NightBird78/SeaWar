import random
import numpy

# ⬜ white large square
# ⬛ black large square


symbol_number = dict(zip(list('abcdefghij'), list('0123456789')))


random_shot = ['У вашого корабля пробоїна на _!', "В точці _ проведено вогонь по нам!", "Бомбардування корабля на _",
               "Палуба під номером _ заповнюється водою!", "Палуба _ горить!","Ваш корабель _ підстрелено!",
               "Аварія на _ палубі!", "Корабель на _ пошкоджений!", "Ворог атакував корабель на _!"]

random_die = ["Союзний корабель затонув", "Стався вибух корабля!", "Наші друзі тонуть з почестями",
              "Наш корабель було знищено", "Корабель наблизився до дна моря!", "Корабель переможно відступає на дно!",
              "Один із наших кораблів став підводним човном!", "Від нашого корабля залишилося лише мокре місце!"]


random_miss = ["Наведи приціл ліпше!"]

empty_filler = '·'  # '.'
ship_filler = '■'

shot = '×'  # xX
kill = '#'
miss = '≈'


def Ship(lent):
    s = numpy.array([ship_filler for _ in range(lent)])
    if lent != 1:
        return {0: s, 1: s, 2: s, 3: s}
    return {0: s, 1: s.T, 2: s, 3: s.T}


# -----------------
# x y Len Rotation
# -----------------

def check_die(x, y, arr: numpy.ndarray):
    # print(arr[x - 1:x + 2, y - 1:y + 2])
    x1, x2, y1, y2 = 0, 0, 0, 0
    #print(arr.item(x, y))

    for _ in range(5):
        #print(y2)
        # if y + 2 + y2 > 9:
        #     y2 -= 1
        # if y + 2 + y2 > 9:
        #     y2 -= 1
        # if x + (2 + x2) > 9:
        #     x2 -= 1
        # if x + (2 + x2) > 9:
        #     x2 -= 1
        # if x - (1 + x1) < 0:
        #     x1 += 1
        # if y - (1 + y1) < 0:
        #     y1 += 1
    # print(arr.item(x, y))
    #try:
        if str(arr.item(x - (1 + x1), y)) in f'{ship_filler}{shot}':  # верх
            if x - (1 + x1) > 0:
                x1 += 1
    #except:
    #    x1 -= 1
    #try:
        elif str(arr.item(x + (1 + x2), y) if x + (1 + x2) < 9 else x) in f'{ship_filler}{shot}':  # низ
            if x + (1 + x2) < 9:
                x2 += 1
    #except:
    #    x2 -= 1
    #try:
        elif str(arr.item(x, y - (1 + y1))) in f'{ship_filler}{shot}':  # ліво
            if y - (1 + y1) > 0:
                y1 += 1
    #except:
    #    y1 -= 1
    #try:
        elif str(arr.item(x, y + (1 + y2) if y + (1 + y2) < 9 else y)) in f'{ship_filler}{shot}':  # право
            if y + (1 + y2) < 9:
                y2 += 1
    #except:
    #    y2 -= 1
        else:
            break
    x1, x2, y1, y2 = x - x1 - 1, x + x2 + 2, y - y1 - 1, y + y2 + 2

    if x1 < 0:
        x1 = 0
    if x2 > 10:
        x2 = 10
    if y1<0:
        y1=0
    if y2>10:
        y2=10

    if ship_filler not in arr[x1:x2, y1:y2]:
        for a in range(x1,x2):
            for b in range(y1,y2):
                if arr[a, b] == shot:
                    arr.itemset((a, b), kill)
                elif arr[a, b] == empty_filler:
                    arr.itemset((a, b), miss)

        return arr, "kill"
    return arr, None

    # if shot in arr[x - x1 - 1:x + x2 + 2, y - y1 - 1:y + y2 + 2] or \
    #         ship_filler in arr[x - x1 - 1:x + x2 + 2, y - y1 - 1:y + y2 + 2]:
    #
    #     if shot in arr.item(x - (1 + x1), y) or ship_filler in arr.item(x - (1 + x1), y):
    #        x1 += 1
    #        print('x1')
    #     elif shot in arr.item(x + x2 + 1, y) or ship_filler in arr.item(x + x2 + 1, y):
    #         x2 += 1
    #         print('x2')
    #     elif shot in arr.item(x, y - (1 + y1)) or ship_filler in arr.item(x, y - (1 + y1)):
    #         y1 += 1
    #         print('y1')
    #     elif shot in arr.item(x, y + y2 + 1) or ship_filler in arr.item(x, y + y2 + 1):
    #         y2 += 1
    #         print('y2')
    #     else:
    #         pass
    #         #break


def set_ship(x, x1, y, y1, arr):
    for a in range(y, y1 + 1):
        for b in range(x, x1 + 1):
            arr.itemset((b, a), ship_filler)
    return arr


def funk(x, y, Len, arr):
    sh = Ship(Len)
    for rotation in range(4):
        x1, y1 = 0, 0
        if rotation == 1:
            x1 += x
            y1 += y + Len - 1
        elif rotation == 2:
            x1 += x + Len - 1
            y1 += y
        elif rotation == 3:
            x1 += x
            y1 += y - Len + 1
        elif rotation == 0:
            x1 += x - Len + 1
            y1 += y
        else:
            raise ValueError

        if not -1 < y1 < 10 or not -1 < x1 < 10:
            continue

        if rotation in [1, 2]:
            if ship_filler in arr[x if x < 1 else x - 1:
            x1 + 1 if x1 + 1 > 9 else x1 + 1 + 2,
                              y if y < 1 else y - 1:
                              y1 + 1 if y1 + 1 > 9 else y1 + 1 + 2]:
                continue

            else:
                set_ship(x, x1, y, y1, arr)
            return 1

        else:
            if ship_filler in arr[x1 if x1 < 1 else x1 - 1:
                                  x + 1 if x + 1 > 9 else x + 1 + 2,
                                  y1 if y1 < 1 else y1 - 1:
                                  y + 1 if y + 1 > 9 else y + 1 + 2]:
                continue
            else:
                set_ship(x1, x, y1, y, arr)
            #
            #
            return 1

    else:
        return -1


def check_endgame(arr: numpy.ndarray):
    return ship_filler not in arr


def repeat(Len, arr):
    x = random.randint(0, 9)
    y = random.randint(0, 9)
    if funk(x, y, Len, arr) == -1:
        repeat(Len, arr)


# a = [[',' for _ in range(10)] for _ in range(10)]
# arr = numpy.array(a)

def creat():
    for _ in range(3):
        a = [[empty_filler for _ in range(10)] for _ in range(10)]
        arr = numpy.array(a)
        lis = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        random.shuffle(lis)
        for a in lis:
            x = random.randint(0, 9)
            y = random.randint(0, 9)

            if funk(x, y, a, arr) == -1:
                try:
                    repeat(a, arr)
                except:
                    break
        else:
            return arr
    return creat()


def fire(symbol: str, number: int, array: numpy.ndarray):
    '''
    :param symbol: y кордината
    :param number: x кордината
    :param array: карта з корабликами
    :return: array або -1 при 'таке вже було'
    '''
    number1 = int(symbol_number[symbol])
    number = int(number)

    item = array[number][number1]
    if item in '#×≈':
        return None, None
    elif item == ship_filler:
        array.itemset((number, number1), shot)
        array, doing = check_die(number, number1, array)
        return array, "shot" if doing is None else doing

    elif item == empty_filler:
        array.itemset((number, number1), miss)
        return array, "miss"



# print(creat())
# print(arr)


# print(arr[2-1:2+2,2-1:4+2])
# x = 2, y = 4, x1 = 2, y1 = 2, rotation = 2
