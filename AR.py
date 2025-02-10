import cv2

def detect(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Initiate ORB detector
    orb = cv2.ORB_create()

    # find the keypoints with ORB
    kp = orb.detect(img, None)

    # compute the descriptors with ORB
    kp, des = orb.compute(img, kp)

    # draw only keypoints location,not size and orientation
    img2 = cv2.drawKeypoints(img, kp, img, color=(0,255,0), flags=0)
    cv2.imshow('keypoints',img2)
    cv2.waitKey(0)
