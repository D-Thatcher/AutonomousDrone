
reverse_map = {'takeoff':'land','up':'down','left':'right','Command':'Command','streamon':'streamoff','cw':'ccw'}
reverse_map_reversed = {reverse_map[i]:i for i in reverse_map}
reverse_map.update(reverse_map_reversed)

def swap(cmd):
    """
    :param cmd: One of the drone commands
    :return: The opposite drone command
    e.g. 'up' will return 'down'
    """
    if ' ' in cmd:
        s = cmd.split(' ')
        s = [i for i in s if len(i.strip())>0]
        return swap(s[0]) + ' ' + s[-1]
    if cmd not in reverse_map:
        raise KeyError("cmd "+cmd+" is not in the reverse map")
    return reverse_map[cmd]