import numpy as np
import cv2
from skimage.measure import compare_ssim
from PIL import Image
import hunter


UNKNOWN = 0
OCCUPIED = 1
AVAILABLE = 2


def _check_area_with_color(img, area, red_r, green_r, blue_r, debug = False):
    """
    :param img: PIL Image
    :param area: (start x, start y, end x, end y)
    :param red_r: (red rgb range start, red rgb range end)
    :param green_r:
    :param blue_r:
    :return: Bool
    """
    np_arr = np.array(img)
    np_arr = np_arr[area[1]:area[3], area[0]:area[2], :]
    if debug:
        print(np_arr)

    for i, c in enumerate(np.nditer(np.array(np_arr))):
        if i % 3 is 0:  # red
            if red_r[1] < c or c < red_r[0]:
                if debug:
                    print("Red Fail %d %d~%d" % (c, red_r[0], red_r[1]), area)
                return False
        elif (i + 2) % 3 is 0:  # green
            if green_r[1] < c or c < green_r[0]:
                if debug:
                    print("Green Fail %d %d~%d" % (c, green_r[0], green_r[1]), area)
                return False
        elif (i + 3) % 3 is 0:  # blue this is bug, it should be i+1
            if blue_r[1] < c or c < blue_r[0]:
                if debug:
                    print("Blue Fail %d %d~%d" % (c, blue_r[0], blue_r[1]), area)
                return False

    if debug:
        print("Return TRUE")
    return True


def is_search_popup(img, debug = False):
    return _check_area_with_color(img, (4, 578, 151, 579),
                                  (23 ,23), (26,26), (31, 31), debug)


def is_area_popup(img):
    black_header = _check_area_with_color(img, (20, 181, 200, 182),
                                          (20, 25), (20, 25), (20, 25))
    blue_button = _check_area_with_color(img, (427, 219, 500, 220),
                                         (104, 106), (141, 143), (183, 185))
    return black_header and blue_button


def is_checked_mine(img, player):
    occupied_mines = player.get_occupied_mine()
    xpos, ypos = fetch_pos_area_as_gray(img)

    for o in occupied_mines:
        (xscore, xdiff) = compare_ssim(xpos, o[1], full=True)
        (yscore, ydiff) = compare_ssim(ypos, o[2], full=True)
        # print("XSCORE", xscore)
        # print("YSCORE", yscore)
        if xscore > 0.8 and yscore > 0.8:
            return True

    return False


def is_occupied_mine(img, count = 0):
    icon_areas = [(389, 571, 393, 576 + 1), (394, 560, 395, 561 + 1),  # 5th
                  (335, 618, 340, 623 + 1), (360, 617, 362, 619 + 1),  # 4th
                  (267, 634, 273, 638 + 1),                            # 3rd
                  (182, 607, 201, 611 + 1),                            # 2nd
                  (137, 556, 140, 569 + 1)]                            # 1th
    result = OCCUPIED
    for area in icon_areas:
        if not _check_area_with_color(img, area,
                                      (200, 255), (200, 255), (200, 255)):
            # if count is 0:
            #    print("UNKNOWN1")
            result = UNKNOWN
            break

    if result is OCCUPIED:
        # print("OCCUPIED")
        return OCCUPIED

    icon_areas = [(335, 620, 346, 623 + 1), # error (360, 617, 362, 619 + 1),  # 3rd
                  (268, 634, 273, 638 + 1),                            # 2nd
                  (191, 602, 194, 614 + 1)]                            # 1nd

    black_areas = [(184, 594, 198 + 1, 594 + 1),
                   (263, 614, 276 + 1, 614 + 1),
                   (341, 594, 352 + 1, 594 + 1)]

    result = AVAILABLE
    for area in icon_areas:
        if not _check_area_with_color(img, area,
                                      (200, 255), (200, 255), (200, 255)):
            # if count is 0:
            #     print("UNKNOWN2")
            result = UNKNOWN
            break

    for area in black_areas:
        if not _check_area_with_color(img, area,
                                      (15, 35), (15, 35), (15, 35)):    # BUG: Whiter Color: 27, 29, 32
            result = UNKNOWN
            # if count is 0:
            #     print("UNKNOWN3")
            break

    if result is AVAILABLE:
        # print("AVAILABLE")
        return AVAILABLE

    result = OCCUPIED
    icon_areas = [(306, 627, 313, 630 + 1), (228, 615, 233, 623 + 1)]
    black_areas = [(224, 607, 237 + 1, 607 + 1), (303, 607, 315 + 1, 607 + 1)]
    for area in icon_areas:
        if not _check_area_with_color(img, area,
                                      (200, 255), (200, 255), (200, 255)):
            # if count is 0:
            #     print("ALLY UNKNOWN")
            result = UNKNOWN
            break

    for area in black_areas:
        if not _check_area_with_color(img, area,
                                      (15, 35), (15, 35), (15, 35)):
            result = UNKNOWN
            # if count is 0:
            #     print("ALLY UNKNOWN")
            break

    if result is OCCUPIED:
        # print("ALLY OCCUPIED")
        return OCCUPIED

    return UNKNOWN


def dispatch_army_popup(img):
    blue_area = _check_area_with_color(img, (132, 918, 213, 918 + 1),
                                       (125, 140), (160, 185), (195, 210))
    yellow_area = _check_area_with_color(img, (342, 918, 396, 918 + 1),
                                         (195, 210), (170, 190), (115, 135))

    return blue_area and yellow_area


def is_other_going(img):
    blue_area = _check_area_with_color(img, (110, 612, 167, 612 + 1),
                                       (125, 140), (160, 185), (195, 210))
    yellow_area = _check_area_with_color(img, (344, 612, 409, 612 + 1),
                                         (195, 210), (170, 190), (115, 135))

    return blue_area and yellow_area


def is_high_number(img):
    # 311, 393, 316, 401
    np_arr = np.array(img)
    np_arr = np_arr[393:401+1, 304:309+1, :]

    count = 0
    for i in range(402-393):
        for j in range(317-311):
            if np_arr[i][j][0] > 17 and np_arr[i][j][1] > 17 and np_arr[i][j][2] > 17:
                count += 1

    print("NUMBER COUNT:%d" % count)
    if count >= 17:
        return True

    return False


def is_castle_summary(img):
    dark_box = _check_area_with_color(img, (445, 174, 455 + 1, 180 + 1),
                                (40, 55), (55, 70), (55, 75))
    x_symbol_lt = _check_area_with_color(img, (465, 183, 468 + 1, 184 + 1),
                                (250, 255), (240, 255), (200, 210))
    x_symbol_rb = _check_area_with_color(img, (478, 199, 481 + 1, 199 + 1),
                                         (150, 155), (138, 142), (105, 107))
    left_top = _check_area_with_color(img, (46, 177, 50 + 1, 179 + 1),
                                         (29, 33), (37, 40), (42, 45))
    return dark_box and x_symbol_lt and x_symbol_rb and left_top


def is_weather(img):
    r1 = _check_area_with_color(img, (470, 259, 478+1, 266+1),
                                       (150, 250), (60, 90), (40, 50))
    r2 = _check_area_with_color(img, (458, 247, 464 + 1, 250 + 1),
                                (210, 230), (90, 105), (50, 65))
    r3 = _check_area_with_color(img, (484, 250, 488 + 1, 252 + 1),
                                (195, 230), (90, 105), (50, 65))
    r4 = _check_area_with_color(img, (482, 271, 484 + 1, 273 + 1),
                                (130, 150), (45, 60), (25, 35))

    return r1 and r2 and r3 and r4


def army_exists(img, index):
    y = 230 + 110 * index
    height = 11
    x = 187
    width = 2
    np_arr = np.array(img)
    np_arr = np_arr[y:y+height, x:x+width, :]
    for i in range(height):
        for j in range(width):
            if np_arr[i][j][0] > 200 and np_arr[i][j][1] > 200 and np_arr[i][j][2] > 200:
                print("ARMY EXIST")
                return True
    print("NO ARMY")
    return False


def is_reward(img):
    red = _check_area_with_color(img, (74, 633, 85 + 1, 649 + 1),
                                (200, 210), (60, 65), (50, 55))
    orange = _check_area_with_color(img, (71, 660, 81 + 1, 667 + 1),
                                 (200, 230), (145, 150), (60, 70))
    orange2 = _check_area_with_color(img, (236, 655, 248 + 1, 666 + 1),
                                    (200, 230), (145, 150), (60, 70))
    return red and orange and orange2


def fetch_pos_area_as_gray(img):
    np_arr = np.array(img)
    x_np_arr = np_arr[823:837+1, 225:239+1, :]
    y_np_arr = np_arr[823:837 + 1, 296:330 + 1, :]
    x_gray = cv2.cvtColor(x_np_arr, cv2.COLOR_BGR2GRAY)
    y_gray = cv2.cvtColor(y_np_arr, cv2.COLOR_BGR2GRAY)
    return x_gray, y_gray


def is_mine_found(img):
    gap = (182 - 64)

    current_arr = np.array(img)
    current_arr = current_arr[648:704, 64:524, :]
    current_arr = cv2.cvtColor(current_arr, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(current_arr, hunter.Hunter.mine,
                            cv2.TM_CCORR_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val > 0.98 and max_loc[0] == gap:
        return True

    return False


def is_target_found(img):
    gap = (182 - 64)

    current_arr = np.array(img)
    current_arr = current_arr[648:704, 64:524, :]
    current_arr = cv2.cvtColor(current_arr, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(current_arr, hunter.Hunter.target,
                            cv2.TM_CCORR_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    print(max_val, max_loc)
    if max_val > 0.98 and max_loc[0] == (gap * 3):
        return True

    return False


def is_target_screen(img):
    underbar = _check_area_with_color(img, (185, 636, 374 + 1, 636 + 1),
                                 (70, 120), (70, 120), (40, 88))
    blackrect = _check_area_with_color(img, (233, 460, 301 + 1, 472 + 1),
                                      (15, 30), (15, 30), (15, 30))
    return underbar and blackrect


def is_no_more_target(img):
    current_arr = np.array(img)
    current_arr = current_arr[408:424, 132:408, :]

    current_arr = cv2.cvtColor(current_arr, cv2.COLOR_BGR2GRAY)
    (score, _) = compare_ssim(current_arr, hunter.Hunter.no_more, full=True)
    # gprint("NO MORE TARGET", score)
    return score > 0.8


def get_target_type(img):
    # infantry = 0, knight = 1, archer = 2, tank = 3, unknown -1
    new_c = img.crop((254, 302, 283, 331))
    current_arr = cv2.cvtColor(np.array(new_c), cv2.COLOR_BGR2GRAY)
    for i in range(len(hunter.Hunter.types)):
        (score, diff) = compare_ssim(current_arr, hunter.Hunter.types[i], full=True)
        if score > 0.9:
            return i
    return -1


def is_defeat_popup(img):
    arrow = _check_area_with_color(img, (138, 824, 158 + 1, 829 + 1),
                                    (85, 150), (150, 210), (70, 85))
    arrow_right = _check_area_with_color(img, (498, 817, 501 + 1, 826 + 1),
                                   (190, 210), (180, 200), (150, 170))
    name_below = _check_area_with_color(img, (48, 846, 60 + 1, 856 + 1),
                                         (0, 15), (0, 15), (0, 15))
    if arrow and name_below:  # and arrow_right:
        print("DEFEAT POPUP**********")
        return True
    else:
        """
        fails = []
        if not arrow:
            fails.append("ARROW")
        if not arrow_right:
            fails.append("ARROW_RIGHT")
        if not name_below:
            fails.append("NAME_BELOW")
        print("DEFEAT FAILS ", fails)
        """
    return False


def capture_primary_army(img):
    # 172 - 243, y: 230 - 241
    np_arr = np.array(img)
    arr = np_arr[230:241+1, 172:243+1, :]
    arr = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    return arr


def army_is_back(origin, now):
    np_arr = np.array(now)
    arr = np_arr[230:241 + 1, 172:243 + 1, :]
    arr = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    score, _ = compare_ssim(arr, origin, full=True)
    print("ARMY IS BACK", score)
    if score > 0.8:
        return True
    """
    else:
        Image.fromarray(arr).save('now.png')
        Image.fromarray(origin).save('origin.png')
    """
    return False


def is_no_ticket(img):
    s = img.crop((137, 409, 367, 424))
    arr = cv2.cvtColor(np.array(s), cv2.COLOR_BGR2GRAY)
    score, _ = compare_ssim(arr, hunter.Hunter.no_ticket, full=True)
    if score > 0.8:
        print("NO TICKET***********")
        return True

    return False


def is_time_reward(img):
    gold = _check_area_with_color(img, (319, 317, 322 + 1, 319 + 1),
                                 (161, 255), (113, 180), (40, 55))
    return gold