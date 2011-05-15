from tools import color_from_string
import configparser

__dict = {} #store (config option, value)

def load_config():
    """ read configs from config file, and simulate a static config class """
    config_filepath = "config.ini"
    config = configparser.ConfigParser()
    config.read(config_filepath)
    for section in config.sections():
        options = config.options(section)
        for option in options:
            try:
                __dict[option] = config.get(section, option)
                if __dict[option] == -1:
                    print("[ERROR]: skipped option: %s" % option)
            except:
                print("[ERROR]: exception on option %s" % option)
                __dict[option] = None 
    return

# main config
def config_get_fps():
    return int(__dict['fps'])

def config_get_screencaption():
    return __dict['screencaption']


# board config    
def config_get_map():
    return __dict['mapname']

def config_get_screenwidth():
    return int(__dict['screenwidth'])

def config_get_screenheight():
    return int(__dict['screenheight'])


# cell graphics
def config_get_walkablecolor():
    return (color_from_string(__dict['walkablecolor']))

def config_get_nonwalkablecolor():
    return (color_from_string(__dict['nonwalkablecolor']))

def config_get_entrancecolor():
    return (color_from_string(__dict['entrancecolor']))

def config_get_laircolor():
    return (color_from_string(__dict['laircolor']))

def config_get_nonwalkableoverlay():
    return (color_from_string(__dict['nonwalkableoverlay']))

def config_get_walkableoverlay():
    return (color_from_string(__dict['walkableoverlay']))


# creep 
def config_get_creep_hp():
    return int(__dict['creep_hp'])

def config_get_creep_atk():
    return int(__dict['creep_atk'])

def config_get_creep_atk_range():
    return int(__dict['creep_atk_range'])

def config_get_creep_atk_cooldown():
    return int(__dict['creep_atk_cooldown'])
 
def config_get_creep_atk_anim_duration():
    return int(__dict['creep_atk_anim_duration'])
 
def config_get_creep_mvt_range():
    return int(__dict['creep_mvt_range'])

def config_get_creep_mvt_cooldown():
    return int(__dict['creep_mvt_cooldown'])

def config_get_creep_sprite():
    return __dict['creep_sprite']

def config_get_creep_sprite_scale():
    return float(__dict['creep_sprite_scale'])

def config_get_creep_atk_color():
    return (color_from_string(__dict['creep_atk_color']))


