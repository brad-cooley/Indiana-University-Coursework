import numpy as np
import sys

def get_map(m=7 , n=8, p_dot = 0.7):
    map = list(np.random.choice(['.', 'X'], size=(m,n), replace=True, p = [p_dot,1-p_dot]))
    rnd_p = np.random.randint(0, len(map)-1, size=2)
    rnd_me = np.random.randint(0, len(map[0])-1, size=2)
    map[rnd_p[0]][rnd_p[1]] = 'p' 
    map[rnd_me[0]][rnd_me[1]] = '@' 
    map = [list(r) for r in map]
    return map

# Main Function
if __name__ == "__main__":
    file_name = sys.argv[1]
    f = open(file_name, "w")

    new_map = get_map(int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]))
    f.write("12\n")
    f.write("True\n")
    f.write("4\n")
    for line in new_map:
        for char in line:
            f.write(str(char))
        f.write("\n")
    f.close()