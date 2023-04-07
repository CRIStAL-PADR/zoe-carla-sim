import carla
import random
import time
import argparse

def main(args):
    actor_list = []
    
    # Connect to client
    client = carla.Client('192.168.0.25', 2000)
    client.set_timeout(20.0)
    
    # Load the world for the simulation and spawun point of the ego vehicle and its initial pose
    world = client.load_world(args.world)
    print(args.world + " loaded")

    #Retrieve the world and the settings to activate synchronous mode
    settings = world.get_settings()
    settings.asynchronous_mode = True
    world.apply_settings(settings)
    if settings.asynchronous_mode:
        print('Activating asynchronous mode')
    
    # Get the spectator information to set its 3D pose in order to obseerve the ego car behaviour
    spectator = world.get_spectator()

    try:
        mymap = world.get_map()
        # Get the world scenario and all the objects bluesprints in a list
        blueprint_library = world.get_blueprint_library()

        # Destroy all the vehicles present before starting the simulation
        actors = world.get_actors().filter('vehicle.*.*')
        for actor in actors:
            actor.destroy()
        
        world.tick()
        world.wait_for_tick()

        # Creating the ego vehicle and positioning it
        # Find Tesla model in vehicle blueprints
        ego_blueprint = blueprint_library.find('vehicle.tesla.model3')
        ego_blueprint.set_attribute('color', '255,0,0')

        transform = carla.Transform(carla.Location(x=70, y=-4, z=0.3),
                                    carla.Rotation(yaw=-60))
        
        ego_vehicle = world.spawn_actor(ego_blueprint, transform)
        world.tick()
        world.wait_for_tick()
        # Set the spectator
        transform.location += carla.Location(z=30)
        transform.rotation.pitch = -60
        spectator.set_transform(transform)
        world.tick()
        world.wait_for_tick()
        print(ego_vehicle.get_location())
        print("%s %s %s created and positioned" % (ego_blueprint.tags[0], ego_blueprint.tags[1], ego_blueprint.tags[2]))
        actor_list.append(ego_vehicle)

        # Boucle principale de simulation

        while True:
            #Send command to the vehicle
            control= carla.VehicleControl(throttle=random.uniform(0.5,0.8),
                                          steer=random.uniform(-0.5, 0.5),
                                          brake=0.0)
            ego_vehicle.apply_control(control)
            world.tick()
            world.wait_for_tick()
            time.sleep(0.1)

    except KeyboardInterrupt:
        print('\n Exit by user')
    
    finally:
        # Code de nettoyage
        if settings.synchronous_mode:
            print('Disabling synchronous mode')
            settings.synchronous_mode = False
            world.apply_settings(settings)
        
        print("destroying actors")
        for actor in actor_list:
            actor.destroy()
        print('Done.')

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-w', '--world',
        metavar='WORLD_NAME',
        default='Town01',
        help='Name of the world to simulate (default: Town07)')
    args = argparser.parse_args()

    #connect to the client and print available maps
    client = carla.Client('192.168.0.25', 2000)
    client.set_timeout(20.0)
    print(client.get_available_maps())

    try:
        main(args)
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye')
