import base64

WHITE_PLAYER = 0
BLACK_PLAYER = 1


def pad(s):
    l = len(s)
    result = '0' * (8-l) + s
    return result

def decode_gnuid(gnuid):
    """
    This decodes both position and match ids.
    """
    gnuid += '=='
    decoded = base64.b64decode(gnuid)
    le_bits = ''
    for byte in decoded:
        to_append = pad(str(bin(byte)).replace('0b', ''))
        le_bits += to_append
    bits = ''
    for start in range(len(le_bits) // 8):
        start *= 8
        byte = ''.join(list(reversed(le_bits[start:start+8])))
        bits += byte
    return bits

def encode_bits(bits):
    to_encode = [ ]
    for start in range(len(bits) // 8):
        start *= 8
        byte = ''.join(list(reversed(bits[start:start+8])))
        to_encode.append(int(byte, 2))
    result = base64.b64encode(bytearray(to_encode)).decode('utf8')
    return result
            

class Position:
    def __init__(self):
        self.cheq_distr = [0] * 50

    @staticmethod
    def from_position_id(pid):
        result = Position()
        bits = decode_gnuid(pid)
        current_index = 0
        for bit in bits:
            if bit == '0':
                current_index += 1
            else:
                result.cheq_distr[current_index] += 1
        return result

CENTERED_CUBE = 0b11


def decb2(s):
    return int(s, 2)
                    
class Match:

    def __init__(self):
        self.cube = 1
        self.cube_owner = CENTERED_CUBE

    @staticmethod
    def from_match_id(mid):
        result = Match()
        bits = decode_gnuid(mid)
        result.cube = decb2(bits[0:4])
        print(bits)
        print(result.cube)
        

def whose_turn(mid):
    bits = decode_gnuid(mid)
    result = bits[11]
    return int(result)

def is_cube_being_offered(mid):
    bits = decode_gnuid(mid)
    result = bits[12]
    return result == '1'

def position_id_to_points(position_id):
    points = [0] * 50
    bits = decode_gnuid(position_id)

    pointi = 0
    checkers = 0
    for bit in bits:
        if bit == '0':
            points[pointi] = checkers
            pointi += 1
            if pointi == 50:
                break
            checkers = 0
        else:
            checkers += 1

    return points

def points25_to_pips(points25):
    s = 0
    for pointi, point in enumerate(points25, 1):
        s += pointi * point
    return s
        
def position_id_to_pips(position_id):
    """
    Returns [opp_pips, player_pips].
    """
    points = position_id_to_points(position_id)
    a = points[:25]
    b = points[25:]
    return [points25_to_pips(a), points25_to_pips(b)]

def position_id_to_max_pips(position_id):
    return max(position_id_to_pips(position_id))


def set_dice_to_zero(mid):
# When it exports to text, GNU Backgammon will evaluate cube decision of the
# type "double or roll" and print it to the file, but the matchid that precedes
# the analysis will still have the dice the player rolled, if he did not
# double. This function fixes this, and it should be called only on those
# cases.
    bits = decode_gnuid(mid)
    bits = bits[:15] + ('0' * 6) + bits[21:]
    return encode_bits(bits)

def position_id_to_checker_list(pid):
    result = [0]
    index = 0
    bits = decode_gnuid(pid)
    for bit in bits:
        if len(result) == 50:
            break
        if bit == '0':
            result.append(0)
        elif bit == '1':
            result[-1] += 1
        else:
            raise Exception
    return result


if __name__ == '__main__':
    if 1:
        print(position_id_to_points('6jbBASRwt4kHAA:8AmyAAAAIAAE')[:25])
        print(position_id_to_points('6jbBASRwt4kHAA:8AmyAAAAIAAE')[25:])
        print(position_id_to_pips('6jbBASRwt4kHAA:8AmyAAAAIAAE'))
    if 0:
        print(position_id_to_points('4HPwATDgc/ABMA'))
        print(points25_to_pips(position_id_to_points('4HPwATDgc/ABMA')[:25]))
        print(position_id_to_max_pips('4HPwATDgc/ABMA'))
    if 0:
        print(len(position_id_to_checker_list('4HPwATDgc/ABMA')))
        print((position_id_to_checker_list('4HPwATDgc/ABMA')))
