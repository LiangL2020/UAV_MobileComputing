import socket
import time

# create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)


def receive_response():
    try:
        response, _ = sock.recvfrom(1024)
        print(f"Response: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Error receiving response: {e}")


if __name__ == "__main__":
    # SDK mode
    print('command')
    sock.sendto('command'.encode(), tello_address)
    time.sleep(1)
    receive_response()

    # takeoff
    print('takeoff')
    sock.sendto('takeoff'.encode(), tello_address)
    time.sleep(5)
    receive_response()

    # up
    print('up')
    sock.sendto('up 40'.encode(), tello_address)
    time.sleep(3)
    receive_response()

    # down
    print('down')
    sock.sendto('down 40'.encode(), tello_address)
    time.sleep(3)
    receive_response()

    # left
    print('left')
    sock.sendto('left 20'.encode(), tello_address)
    time.sleep(3)
    receive_response()

    # right
    print('right')
    sock.sendto('right 20'.encode(), tello_address)
    time.sleep(3)
    receive_response()

    # # forward
    # print('forward')
    # sock.sendto('forward 20'.encode(), tello_address)
    # time.sleep(3)
    # receive_response()
    #
    # # back
    # print('back')
    # sock.sendto('back 20'.encode(), tello_address)
    # time.sleep(3)
    # receive_response()

    # rotate clockwise
    print('rotate clockwise')
    sock.sendto('cw 30'.encode(), tello_address)
    time.sleep(3)
    receive_response()

    # rotate counterclockwise
    print('rotate counterclockwise')
    sock.sendto('ccw 30'.encode(), tello_address)
    time.sleep(3)
    receive_response()

    # # flip left
    # sock.sendto('flip l'.encode(), tello_address)
    # time.sleep(3)
    # receive_response()
    #
    # # flip right
    # sock.sendto('flip r'.encode(), tello_address)
    # time.sleep(3)
    # receive_response()
    #
    # # flip forward
    # sock.sendto('flip f'.encode(), tello_address)
    # time.sleep(3)
    # receive_response()
    #
    # # flip backward
    # sock.sendto('flip b'.encode(), tello_address)
    # time.sleep(3)
    # receive_response()

    # land
    print('land')
    sock.sendto('land'.encode(), tello_address)
    time.sleep(3)
    receive_response()

    sock.close()
