from flight_simulator import FlightSimulator
from command_handler import CommandHandler

def run_simulation():
    my_sim = FlightSimulator()
    my_commander = CommandHandler(command_poster_fn=my_sim.post_command)
    my_sim.set_commander(my_commander)

    my_commander.initialize_sdk()
    my_commander.take_off()
    my_commander.right(20)
    my_commander.rotate_clockwise(15)
    my_commander.land()
    my_commander.take_off()
    my_commander.rotate_clockwise(15)

    print('\n\n\ntracing route back...\n\n\n')
    my_commander.track_back()
    print('flight logs saved to logs')


if __name__ == '__main__':
    run_simulation()
