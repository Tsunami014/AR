import cv2
import numpy as np

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
    cv2.destroyWindow('keypoints')

def match(img, rectangle=True, matches=True):

    cap = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Init
    MIN_MATCHES = 10
    model = cv2.imread('testImgs/model2.png', 0)
    # create ORB keypoint detector
    orb = cv2.ORB_create()
    # create BFMatcher object based on hamming distance  
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)  
    # Compute model keypoints and its descriptors
    kp_model, des_model = orb.detectAndCompute(model, None)

    # Main
    # find and draw the keypoints of the frame
    kp_frame, des_frame = orb.detectAndCompute(cap, None)
    # match frame descriptors with model descriptors
    matches = bf.match(des_model, des_frame)
    # sort them in the order of their distance
    # the lower the distance, the better the match
    matches = sorted(matches, key=lambda x: x.distance)

    if len(matches) > MIN_MATCHES:
        # differenciate between source points and destination points
            src_pts = np.float32([kp_model[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
            # compute Homography
            homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if rectangle:
                # Draw a rectangle that marks the found model in the frame
                h, w = model.shape
                pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                # project corners into frame
                dst = cv2.perspectiveTransform(pts, homography)
                # connect them with lines  
                cap = cv2.polylines(cap, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)  
            # if a valid homography matrix was found render cube on model plane
            # if homography is not None:
            #     try:
            #         # obtain 3D projection matrix from homography matrix and camera parameters
            #         projection = projection_matrix(camera_parameters, homography)  
            #         # project cube or model
            #         cap = render(cap, obj, projection, model, False)
            #         #cap = render(cap, model, projection)
            #     except:
            #         pass
            # draw first 10 matches.
            if matches:
                cap = cv2.drawMatches(model, kp_model, cap, kp_frame, matches[:10], 0, flags=2)
            # show result
            cv2.imshow('frame', cap)
            cv2.waitKey(0)
            try:
                cv2.destroyWindow('frame')
            except:
                pass
    else:
        print("Not enough matches have been found - %d/%d" % (len(matches), MIN_MATCHES))
